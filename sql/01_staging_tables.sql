-- ============================================================================
-- 01_staging_tables.sql: Raw Ingest and Classified Transactions
-- ============================================================================

DROP TABLE IF EXISTS staging.raw_retail_transactions CASCADE;

CREATE TABLE staging.raw_retail_transactions (
    staging_id BIGSERIAL PRIMARY KEY,
    invoice_no VARCHAR(64) NOT NULL,
    stock_code VARCHAR(64) NOT NULL,
    description TEXT,
    quantity INTEGER NOT NULL,
    invoice_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    unit_price NUMERIC(12, 4) NOT NULL,
    line_value NUMERIC(14, 4) NOT NULL,
    customer_id VARCHAR(64),
    country VARCHAR(128) NOT NULL,
    source_sheet VARCHAR(64) NOT NULL,
    event_class VARCHAR(32) NOT NULL,
    loaded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);

CREATE INDEX idx_staging_invoice ON staging.raw_retail_transactions(invoice_no);
CREATE INDEX idx_staging_customer ON staging.raw_retail_transactions(customer_id);
CREATE INDEX idx_staging_date ON staging.raw_retail_transactions(invoice_date);
CREATE INDEX idx_staging_event_class ON staging.raw_retail_transactions(event_class);
