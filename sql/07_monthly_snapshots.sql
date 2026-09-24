-- ============================================================================
-- 07_monthly_snapshots.sql: Monthly Customer Behavioral Snapshots
-- ============================================================================

DROP TABLE IF EXISTS analytics.customer_monthly_snapshot CASCADE;

CREATE TABLE analytics.customer_monthly_snapshot (
    snapshot_id BIGSERIAL PRIMARY KEY,
    customer_id VARCHAR(64) NOT NULL,
    year_month VARCHAR(7) NOT NULL, -- YYYY-MM
    month_start_date DATE NOT NULL,
    month_end_date DATE NOT NULL,
    transaction_count INTEGER NOT NULL,
    value NUMERIC(14, 4) NOT NULL,
    items INTEGER NOT NULL,
    product_count INTEGER NOT NULL,
    recency_at_month_end INTEGER NOT NULL,
    active_flag BOOLEAN NOT NULL,
    rolling_90d_transactions INTEGER NOT NULL,
    rolling_90d_value NUMERIC(14, 4) NOT NULL,
    rolling_90d_products INTEGER NOT NULL,
    behavioral_state VARCHAR(32) NOT NULL,
    CONSTRAINT uq_customer_month UNIQUE (customer_id, year_month)
);

CREATE INDEX idx_cms_customer ON analytics.customer_monthly_snapshot(customer_id);
CREATE INDEX idx_cms_month ON analytics.customer_monthly_snapshot(year_month);
CREATE INDEX idx_cms_state ON analytics.customer_monthly_snapshot(behavioral_state);
