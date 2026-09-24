"""End-to-end database validation script running all 7 checks from sql/11_validation_queries.sql."""

import sys

from sqlalchemy import text

from src.ingestion.db import get_engine
from src.logging_config import logger


def run_all_validations() -> bool:
    """Executes systematic validation checks against live PostgreSQL tables.
    
    Returns True if all checks pass, False if any critical integrity check fails.
    """
    logger.info("Running database integrity and constraint checks...")
    engine = get_engine()

    checks = [
        ("Check 1: Duplicate customer keys in dim_customer", """
            SELECT COUNT(*) - COUNT(DISTINCT customer_id) AS violations
            FROM analytics.dim_customer;
        """),
        ("Check 2: Duplicate invoice numbers in fact_order", """
            SELECT COUNT(*) - COUNT(DISTINCT invoice_no) AS violations
            FROM analytics.fact_order;
        """),
        ("Check 3: Orphan foreign keys in fact_order", """
            SELECT COUNT(*) AS violations
            FROM analytics.fact_order fo
            LEFT JOIN analytics.dim_customer dc ON fo.customer_key = dc.customer_key
            WHERE fo.customer_key IS NOT NULL AND dc.customer_key IS NULL;
        """),
        ("Check 4: Null primary keys in customer_behavior_features", """
            SELECT COUNT(*) AS violations
            FROM analytics.customer_behavior_features
            WHERE customer_id IS NULL;
        """),
        ("Check 5: Non-positive line_value in valid purchase staging", """
            SELECT COUNT(*) AS violations
            FROM staging.raw_retail_transactions
            WHERE event_class = 'VALID_PURCHASE' AND line_value <= 0;
        """),
        ("Check 6: Duplicate customer-month in customer_monthly_snapshot", """
            SELECT COUNT(*) - COUNT(DISTINCT (customer_id || '_' || year_month)) AS violations
            FROM analytics.customer_monthly_snapshot;
        """),
        ("Check 7: Segment assignment completeness for eligible customers", """
            SELECT COUNT(*) AS violations
            FROM analytics.customer_behavior_features cbf
            LEFT JOIN analytics.customer_segment cs ON cbf.customer_id = cs.customer_id
            WHERE cbf.insufficient_history = FALSE AND cs.customer_id IS NULL;
        """)
    ]

    all_passed = True
    with engine.connect() as conn:
        for name, query in checks:
            val = conn.execute(text(query)).scalar()
            if val == 0:
                logger.info(f"  [PASS] {name}: 0 violations")
            else:
                logger.error(f"  [FAIL] {name}: {val} violations detected!")
                all_passed = False

    return all_passed

if __name__ == "__main__":
    success = run_all_validations()
    sys.exit(0 if success else 1)
