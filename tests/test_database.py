"""Tests for live PostgreSQL database connection, schemas, and integrity queries."""

from sqlalchemy import text

from src.ingestion.db import get_engine


def test_database_connection_and_schemas():
    engine = get_engine()
    with engine.connect() as conn:
        # Check active database name
        db_name = conn.execute(text("SELECT current_database()")).scalar()
        assert db_name == "cbdil_analytics"

        # Check schemas exist
        schemas = conn.execute(text("SELECT schema_name FROM information_schema.schemata")).scalars().all()
        assert "staging" in schemas
        assert "analytics" in schemas
        assert "reporting" in schemas

def test_database_integrity_validation():
    """Executes validation checks against populated tables."""
    engine = get_engine()
    with engine.connect() as conn:
        # Check 1: No duplicate customer keys in dim_customer
        dup_cust = conn.execute(text("""
            SELECT COUNT(*) - COUNT(DISTINCT customer_id) FROM analytics.dim_customer
        """)).scalar()
        assert dup_cust == 0, "Duplicate customer_id detected in dim_customer."

        # Check 2: No orphan foreign keys
        orphan_orders = conn.execute(text("""
            SELECT COUNT(*) FROM analytics.fact_order fo
            LEFT JOIN analytics.dim_customer dc ON fo.customer_key = dc.customer_key
            WHERE fo.customer_key IS NOT NULL AND dc.customer_key IS NULL
        """)).scalar()
        assert orphan_orders == 0, "Orphan customer_key in fact_order."
