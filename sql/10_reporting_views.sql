-- ============================================================================
-- 10_reporting_views.sql: Reporting Summaries and Control Summary
-- ============================================================================

DROP TABLE IF EXISTS reporting.monthly_summary CASCADE;
DROP TABLE IF EXISTS reporting.segment_summary CASCADE;
DROP TABLE IF EXISTS reporting.customer_summary CASCADE;
DROP TABLE IF EXISTS reporting.decision_summary CASCADE;
DROP TABLE IF EXISTS reporting.data_control_summary CASCADE;

-- Monthly Summary
CREATE TABLE reporting.monthly_summary (
    year_month VARCHAR(7) PRIMARY KEY,
    active_customers INTEGER NOT NULL,
    total_orders INTEGER NOT NULL,
    total_quantity INTEGER NOT NULL,
    total_value NUMERIC(14, 4) NOT NULL,
    average_order_value NUMERIC(14, 4) NOT NULL,
    new_customers INTEGER NOT NULL,
    reactivated_customers INTEGER NOT NULL,
    dormant_customers INTEGER NOT NULL
);

-- Segment Summary
CREATE TABLE reporting.segment_summary (
    segment_id INTEGER PRIMARY KEY,
    segment_name VARCHAR(128) NOT NULL,
    customer_count INTEGER NOT NULL,
    customer_share NUMERIC(6, 4) NOT NULL,
    total_value NUMERIC(14, 4) NOT NULL,
    value_share NUMERIC(6, 4) NOT NULL,
    average_order_value NUMERIC(14, 4) NOT NULL,
    median_recency INTEGER NOT NULL,
    median_frequency INTEGER NOT NULL,
    median_interpurchase_gap NUMERIC(10, 2) NOT NULL,
    high_signal_count INTEGER NOT NULL
);

-- Customer Summary
CREATE TABLE reporting.customer_summary (
    customer_id VARCHAR(64) PRIMARY KEY,
    segment_name VARCHAR(128) NOT NULL,
    behavioral_state VARCHAR(32) NOT NULL,
    primary_country VARCHAR(128) NOT NULL,
    lifetime_orders INTEGER NOT NULL,
    total_value NUMERIC(14, 4) NOT NULL,
    recency_days INTEGER NOT NULL,
    average_order_value NUMERIC(14, 4) NOT NULL,
    recent_90d_value NUMERIC(14, 4) NOT NULL,
    prior_90d_value NUMERIC(14, 4) NOT NULL,
    value_momentum_pct NUMERIC(10, 4),
    frequency_momentum_pct NUMERIC(10, 4),
    primary_active_signal VARCHAR(64)
);

-- Decision Summary
CREATE TABLE reporting.decision_summary (
    signal_name VARCHAR(64) PRIMARY KEY,
    affected_customers INTEGER NOT NULL,
    affected_customer_share NUMERIC(6, 4) NOT NULL,
    total_historical_value NUMERIC(14, 4) NOT NULL,
    high_strength_count INTEGER NOT NULL,
    medium_strength_count INTEGER NOT NULL,
    low_strength_count INTEGER NOT NULL,
    associated_strategy_id VARCHAR(32)
);

-- Data Control Summary
CREATE TABLE reporting.data_control_summary (
    control_id VARCHAR(32) PRIMARY KEY,
    control_name VARCHAR(128) NOT NULL,
    population_affected INTEGER NOT NULL,
    affected_pct NUMERIC(6, 2) NOT NULL,
    severity VARCHAR(16) NOT NULL CHECK (severity IN ('PASS', 'WARNING', 'FAIL')),
    status VARCHAR(16) NOT NULL CHECK (status IN ('PASS', 'WARNING', 'FAIL')),
    impact TEXT NOT NULL,
    recommended_resolution TEXT NOT NULL,
    evaluated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);
