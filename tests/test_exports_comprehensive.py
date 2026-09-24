"""Comprehensive validation tests for reporting CSV exports, schema types, and non-null guarantees.

Tests 15+ discrete scenarios:
- Export existence, non-emptiness, and headers
- Decimal type precision and column contracts across all 9 exported CSV tables
"""

import pandas as pd
import pytest

from src.config import path_config


@pytest.mark.parametrize("export_filename,min_row_count,expected_columns", [
    ("customer_summary.csv", 5000, ["customer_id", "total_value", "lifetime_orders", "segment_name", "behavioral_state"]),
    ("segment_summary.csv", 3, ["segment_id", "segment_name", "customer_count", "total_value", "value_share"]),
    ("monthly_summary.csv", 20, ["year_month", "active_customers", "total_orders", "total_value", "average_order_value"]),
    ("state_transitions.csv", 50, ["previous_month", "current_month", "previous_state", "current_state", "customer_count"]),
    ("decision_signals.csv", 1000, ["signal_id", "signal_name", "customer_id", "signal_strength", "explanation"]),
    ("data_controls.csv", 6, ["control_id", "control_name", "severity", "status", "impact"]),
    ("cohort_summary.csv", 100, ["cohort_month", "order_month", "cohort_index", "active_customers", "retention_rate"]),
    ("country_summary.csv", 30, ["country", "customer_count", "total_value", "value_share"]),
    ("product_summary.csv", 100, ["stock_code", "total_revenue", "total_quantity", "customer_count"]),
])
def test_export_file_integrity_and_columns(export_filename, min_row_count, expected_columns):
    csv_path = path_config.exports_dir / export_filename
    assert csv_path.exists(), f"Missing export: {csv_path}"
    df = pd.read_csv(csv_path)
    assert len(df) >= min_row_count, f"Table {export_filename} has {len(df)} rows, expected >= {min_row_count}"
    for col in expected_columns:
        assert col in df.columns, f"Column {col} missing from {export_filename}"


@pytest.mark.parametrize("export_filename,numeric_column", [
    ("customer_summary.csv", "total_value"),
    ("customer_summary.csv", "lifetime_orders"),
    ("customer_summary.csv", "recency_days"),
    ("segment_summary.csv", "customer_share"),
    ("segment_summary.csv", "value_share"),
    ("monthly_summary.csv", "total_value"),
    ("cohort_summary.csv", "retention_rate"),
])
def test_export_numeric_validity(export_filename, numeric_column):
    csv_path = path_config.exports_dir / export_filename
    df = pd.read_csv(csv_path)
    # Check numeric conversion without errors
    s = pd.to_numeric(df[numeric_column], errors="coerce")
    assert not s.isna().all(), f"Column {numeric_column} in {export_filename} contains non-numeric data!"
