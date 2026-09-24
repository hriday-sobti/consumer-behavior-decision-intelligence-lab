-- ============================================================================
-- 04_customer_features.sql: Customer Behavioral Features Table
-- ============================================================================

DROP TABLE IF EXISTS analytics.customer_behavior_features CASCADE;

CREATE TABLE analytics.customer_behavior_features (
    customer_id VARCHAR(64) PRIMARY KEY,
    customer_key INTEGER REFERENCES analytics.dim_customer(customer_key),
    first_purchase_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    last_purchase_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    customer_lifetime_days INTEGER NOT NULL,
    recency_days INTEGER NOT NULL,
    transaction_count INTEGER NOT NULL, -- order/invoice count
    active_month_count INTEGER NOT NULL,
    frequency_per_active_month NUMERIC(10, 4) NOT NULL,
    total_value NUMERIC(14, 4) NOT NULL,
    average_order_value NUMERIC(14, 4) NOT NULL,
    median_order_value NUMERIC(14, 4) NOT NULL,
    average_items_per_order NUMERIC(12, 4) NOT NULL,
    median_items_per_order NUMERIC(12, 4) NOT NULL,
    product_count INTEGER NOT NULL, -- distinct stock codes purchased
    purchase_day_count INTEGER NOT NULL,
    mean_interpurchase_days NUMERIC(10, 2),
    median_interpurchase_days NUMERIC(10, 2),
    interpurchase_gap_std NUMERIC(10, 2),
    interpurchase_gap_cv NUMERIC(10, 4),
    recent_90d_value NUMERIC(14, 4) NOT NULL,
    prior_90d_value NUMERIC(14, 4) NOT NULL,
    recent_90d_transactions INTEGER NOT NULL,
    prior_90d_transactions INTEGER NOT NULL,
    recent_90d_items INTEGER NOT NULL,
    prior_90d_items INTEGER NOT NULL,
    value_change_pct NUMERIC(10, 4),
    frequency_change_pct NUMERIC(10, 4),
    product_breadth_change_pct NUMERIC(10, 4),
    reversal_line_count INTEGER NOT NULL DEFAULT 0,
    reversal_value NUMERIC(14, 4) NOT NULL DEFAULT 0.0000,
    reversal_rate NUMERIC(10, 4) NOT NULL DEFAULT 0.0000,
    country VARCHAR(128) NOT NULL,
    insufficient_history BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);

CREATE INDEX idx_cbf_recency ON analytics.customer_behavior_features(recency_days);
CREATE INDEX idx_cbf_value ON analytics.customer_behavior_features(total_value);
CREATE INDEX idx_cbf_frequency ON analytics.customer_behavior_features(transaction_count);
CREATE INDEX idx_cbf_eligibility ON analytics.customer_behavior_features(insufficient_history);
