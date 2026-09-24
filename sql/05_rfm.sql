-- ============================================================================
-- 05_rfm.sql: Supporting RFM Quintile Scoring Model
-- ============================================================================

DROP TABLE IF EXISTS analytics.customer_rfm CASCADE;

CREATE TABLE analytics.customer_rfm (
    customer_id VARCHAR(64) PRIMARY KEY REFERENCES analytics.customer_behavior_features(customer_id),
    recency_days INTEGER NOT NULL,
    transaction_count INTEGER NOT NULL,
    total_value NUMERIC(14, 4) NOT NULL,
    rfm_recency_score INTEGER NOT NULL CHECK (rfm_recency_score BETWEEN 1 AND 5),
    rfm_frequency_score INTEGER NOT NULL CHECK (rfm_frequency_score BETWEEN 1 AND 5),
    rfm_monetary_score INTEGER NOT NULL CHECK (rfm_monetary_score BETWEEN 1 AND 5),
    rfm_total_score INTEGER NOT NULL,
    rfm_composite_code VARCHAR(8) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);

CREATE INDEX idx_rfm_composite ON analytics.customer_rfm(rfm_composite_code);
CREATE INDEX idx_rfm_total ON analytics.customer_rfm(rfm_total_score);
