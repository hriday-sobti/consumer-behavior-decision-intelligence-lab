-- ============================================================================
-- 06_behavioral_segments.sql: Behavioral Segments & Cluster Profiles
-- ============================================================================

DROP TABLE IF EXISTS analytics.customer_segment CASCADE;
DROP TABLE IF EXISTS analytics.segment_profile CASCADE;

CREATE TABLE analytics.customer_segment (
    customer_id VARCHAR(64) PRIMARY KEY REFERENCES analytics.customer_behavior_features(customer_id),
    segment_id INTEGER NOT NULL,
    segment_name VARCHAR(128) NOT NULL,
    log_total_value NUMERIC(10, 4) NOT NULL,
    log_transaction_count NUMERIC(10, 4) NOT NULL,
    recency_days INTEGER NOT NULL,
    log_product_count NUMERIC(10, 4) NOT NULL,
    mean_interpurchase_days NUMERIC(10, 2) NOT NULL,
    value_momentum_pct NUMERIC(10, 4) NOT NULL,
    frequency_momentum_pct NUMERIC(10, 4) NOT NULL,
    distance_to_center NUMERIC(10, 4),
    assigned_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);

CREATE INDEX idx_cs_segment_id ON analytics.customer_segment(segment_id);
CREATE INDEX idx_cs_segment_name ON analytics.customer_segment(segment_name);

CREATE TABLE analytics.segment_profile (
    segment_id INTEGER PRIMARY KEY,
    segment_name VARCHAR(128) NOT NULL,
    customer_count INTEGER NOT NULL,
    customer_share NUMERIC(6, 4) NOT NULL,
    total_value NUMERIC(14, 4) NOT NULL,
    value_share NUMERIC(6, 4) NOT NULL,
    median_value NUMERIC(14, 4) NOT NULL,
    median_recency INTEGER NOT NULL,
    median_frequency INTEGER NOT NULL,
    median_product_breadth INTEGER NOT NULL,
    median_interpurchase_gap NUMERIC(10, 2) NOT NULL,
    median_value_momentum NUMERIC(10, 4) NOT NULL,
    median_frequency_momentum NUMERIC(10, 4) NOT NULL,
    median_stability NUMERIC(10, 4) NOT NULL,
    reversal_rate NUMERIC(6, 4) NOT NULL,
    primary_behavior TEXT NOT NULL,
    secondary_behavior TEXT NOT NULL,
    interpretation TEXT NOT NULL,
    possible_business_question TEXT NOT NULL
);
