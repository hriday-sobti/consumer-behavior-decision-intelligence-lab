-- ============================================================================
-- 11_validation_queries.sql: Automated Integrity Checks & Gate Queries
-- ============================================================================

-- Check 1: Duplicate customer keys in dimension
SELECT 'Duplicate customer_keys in dim_customer' AS check_name,
       COUNT(*) - COUNT(DISTINCT customer_key) AS violation_count
FROM analytics.dim_customer
HAVING COUNT(*) - COUNT(DISTINCT customer_key) > 0;

-- Check 2: Duplicate invoice numbers in fact_order
SELECT 'Duplicate invoice_no in fact_order' AS check_name,
       COUNT(*) - COUNT(DISTINCT invoice_no) AS violation_count
FROM analytics.fact_order
HAVING COUNT(*) - COUNT(DISTINCT invoice_no) > 0;

-- Check 3: Orphan foreign keys between fact_transaction and dim_customer
SELECT 'Orphan customer_key in fact_transaction' AS check_name,
       COUNT(*) AS violation_count
FROM analytics.fact_transaction ft
LEFT JOIN analytics.dim_customer dc ON ft.customer_key = dc.customer_key
WHERE ft.customer_key IS NOT NULL AND dc.customer_key IS NULL;

-- Check 4: Null primary keys in customer features
SELECT 'Null customer_id in customer_behavior_features' AS check_name,
       COUNT(*) AS violation_count
FROM analytics.customer_behavior_features
WHERE customer_id IS NULL;

-- Check 5: Unexpected negative line_values in valid purchase fact
SELECT 'Negative line_value in valid purchase fact' AS check_name,
       COUNT(*) AS violation_count
FROM analytics.fact_transaction
WHERE event_class = 'VALID_PURCHASE' AND line_value <= 0;

-- Check 6: Duplicate monthly snapshots per customer
SELECT 'Duplicate customer-month in customer_monthly_snapshot' AS check_name,
       COUNT(*) - COUNT(DISTINCT (customer_id || '_' || year_month)) AS violation_count
FROM analytics.customer_monthly_snapshot
HAVING COUNT(*) - COUNT(DISTINCT (customer_id || '_' || year_month)) > 0;

-- Check 7: Segment assignment completeness for eligible customers
SELECT 'Unsegmented eligible customers' AS check_name,
       COUNT(*) AS violation_count
FROM analytics.customer_behavior_features cbf
LEFT JOIN analytics.customer_segment cs ON cbf.customer_id = cs.customer_id
WHERE cbf.insufficient_history = FALSE AND cs.customer_id IS NULL;
