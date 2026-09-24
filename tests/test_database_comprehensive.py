"""Integrity and relational constraint checks for analytical PostgreSQL tables."""

import pytest
from sqlalchemy import text

from src.ingestion.db import get_engine


# 1. Dimension Tables Integrity Checks (6 cases)
@pytest.mark.parametrize("dim_table,pk_col", [
    ("analytics.dim_customer", "customer_key"),
    ("analytics.dim_product", "product_key"),
    ("analytics.dim_country", "country_key"),
    ("analytics.dim_date", "date_key"),
    ("analytics.customer_behavior_features", "customer_id"),
    ("analytics.customer_segment", "customer_id"),
])
def test_database_table_pk_uniqueness(dim_table, pk_col):
    engine = get_engine()
    with engine.connect() as conn:
        res = conn.execute(text(f"""
            SELECT COUNT(*) - COUNT(DISTINCT {pk_col}) FROM {dim_table};
        """)).scalar()
        assert res == 0, f"Duplicate primary key {pk_col} found in {dim_table}!"


# 2. Fact Tables Integrity & Foreign Key Non-Orphan Tests (5 cases)
@pytest.mark.parametrize("fact_table,fk_col,ref_table,ref_pk", [
    ("analytics.fact_order", "customer_key", "analytics.dim_customer", "customer_key"),
    ("analytics.fact_order", "country_key", "analytics.dim_country", "country_key"),
    ("analytics.fact_order", "date_key", "analytics.dim_date", "date_key"),
    ("analytics.customer_segment", "customer_id", "analytics.customer_behavior_features", "customer_id"),
    ("analytics.customer_decision_signal", "customer_id", "analytics.customer_behavior_features", "customer_id"),
])
def test_database_foreign_key_integrity(fact_table, fk_col, ref_table, ref_pk):
    engine = get_engine()
    with engine.connect() as conn:
        orphans = conn.execute(text(f"""
            SELECT COUNT(*) FROM {fact_table} f
            LEFT JOIN {ref_table} r ON f.{fk_col} = r.{ref_pk}
            WHERE f.{fk_col} IS NOT NULL AND r.{ref_pk} IS NULL;
        """)).scalar()
        assert orphans == 0, f"Orphan foreign keys found in {fact_table}.{fk_col} pointing to {ref_table}.{ref_pk}!"


# 3. Decision Strategy Catalog Completeness (6 cases)
@pytest.mark.parametrize("strat_id,expected_signal", [
    ("STRAT-01", "HIGH_VALUE_SOFTENING"),
    ("STRAT-02", "HIGH_FREQUENCY_LOW_VALUE"),
    ("STRAT-03", "EMERGING_BROADENING"),
    ("STRAT-04", "HISTORICAL_VALUE_DORMANT"),
    ("STRAT-05", "BROAD_ENGAGEMENT_SOFTENING"),
    ("STRAT-06", "POSITIVE_MOMENTUM"),
])
def test_database_strategy_catalog(strat_id, expected_signal):
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(text(f"""
            SELECT target_signal, status FROM analytics.decision_strategy WHERE strategy_id = '{strat_id}';
        """)).fetchone()
        assert row is not None, f"Strategy {strat_id} missing from analytics.decision_strategy!"
        assert row[0] == expected_signal


# 4. Check Non-Negative Quantities in Valid Purchases (4 cases)
@pytest.mark.parametrize("check_query,expected_max_violation", [
    ("SELECT COUNT(*) FROM analytics.fact_order WHERE order_value <= 0", 0),
    ("SELECT COUNT(*) FROM analytics.fact_order WHERE total_quantity <= 0", 0),
    ("SELECT COUNT(*) FROM analytics.customer_behavior_features WHERE total_value <= 0", 0),
    ("SELECT COUNT(*) FROM analytics.customer_behavior_features WHERE transaction_count <= 0", 0),
])
def test_database_positive_measures(check_query, expected_max_violation):
    engine = get_engine()
    with engine.connect() as conn:
        val = conn.execute(text(check_query)).scalar()
        assert val <= expected_max_violation
