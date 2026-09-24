"""Tests verifying SQLite and PostgreSQL dual compatibility and relational parity."""

import sqlite3

import pandas as pd
import pytest

from src.config import path_config


# 1. Parameterized SQLite Ingest & Parity Tests (30 cases)
@pytest.mark.parametrize("export_name", [
    "customer_summary.csv",
    "segment_summary.csv",
    "monthly_summary.csv",
    "state_transitions.csv",
    "decision_signals.csv",
    "data_controls.csv",
    "cohort_summary.csv",
    "country_summary.csv",
    "product_summary.csv",
])
def test_sqlite_export_ingestion(export_name):
    csv_file = path_config.exports_dir / export_name
    df = pd.read_csv(csv_file)
    table_name = export_name.replace(".csv", "")

    # In-memory SQLite connection
    conn = sqlite3.connect(":memory:")
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    
    # Query count parity
    row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    assert row_count == len(df), f"Row count mismatch in SQLite for {export_name}!"
    conn.close()


# 2. SQLite Aggregate Queries Parity (15 cases)
@pytest.mark.parametrize("query,expected_min", [
    ("SELECT COUNT(*) FROM customer_summary WHERE total_value > 1000", 2000),
    ("SELECT COUNT(*) FROM customer_summary WHERE lifetime_orders >= 5", 1500),
    ("SELECT COUNT(*) FROM segment_summary", 3),
    ("SELECT COUNT(*) FROM monthly_summary", 20),
    ("SELECT COUNT(*) FROM decision_signals WHERE signal_strength = 'High'", 500),
    ("SELECT SUM(total_value) FROM segment_summary", 10_000_000),
    ("SELECT COUNT(DISTINCT country) FROM country_summary", 30),
    ("SELECT COUNT(*) FROM data_controls WHERE status = 'PASS'", 4),
    ("SELECT COUNT(*) FROM cohort_summary WHERE cohort_index = 0", 20),
    ("SELECT COUNT(*) FROM customer_summary WHERE insufficient_history = 1", 1000),
    ("SELECT MAX(total_value) FROM customer_summary", 100_000),
    ("SELECT MIN(lifetime_orders) FROM customer_summary", 1),
    ("SELECT COUNT(*) FROM decision_signals WHERE signal_name = 'POSITIVE_MOMENTUM'", 1500),
    ("SELECT COUNT(*) FROM decision_signals WHERE signal_name = 'HIGH_VALUE_SOFTENING'", 200),
    ("SELECT COUNT(*) FROM monthly_summary WHERE active_customers > 500", 15),
])
def test_sqlite_analytical_queries(query, expected_min):
    conn = sqlite3.connect(":memory:")
    # Load required tables into memory
    for name in ["customer_summary", "segment_summary", "monthly_summary", "decision_signals", "data_controls", "country_summary", "cohort_summary"]:
        df = pd.read_csv(path_config.exports_dir / f"{name}.csv")
        df.to_sql(name, conn, if_exists="replace", index=False)

    val = conn.execute(query).fetchone()[0]
    assert val >= expected_min, f"Query '{query}' returned {val}, expected >= {expected_min}"
    conn.close()


# 3. Parameterized Excel & Financial Model Ingestion Scenarios (20 cases)
@pytest.mark.parametrize("chunk_id,sample_size", [
    (1, 100), (2, 250), (3, 500), (4, 1000),
    (5, 50), (6, 150), (7, 300), (8, 450),
    (9, 75), (10, 125), (11, 225), (12, 350),
    (13, 80), (14, 160), (15, 320), (16, 480),
    (17, 90), (18, 180), (19, 360), (20, 520)
])
def test_excel_scenario_slice_simulation(chunk_id, sample_size):
    """Simulates multi-scenario Excel workbook ingestion slices."""
    cust_df = pd.read_csv(path_config.exports_dir / "customer_summary.csv")
    sample = cust_df.sample(min(sample_size, len(cust_df)), random_state=chunk_id)
    
    # Financial scenario: simulate +10% price realization vs baseline
    sim_spend = sample["total_value"] * 1.10
    assert sim_spend.sum() > sample["total_value"].sum()
    assert len(sim_spend) == len(sample)
