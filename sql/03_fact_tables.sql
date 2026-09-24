-- ============================================================================
-- 03_fact_tables.sql: Transaction Fact and Order Fact
-- ============================================================================

DROP TABLE IF EXISTS analytics.fact_transaction CASCADE;
DROP TABLE IF EXISTS analytics.fact_order CASCADE;

-- Fact Order (Order Grain)
CREATE TABLE analytics.fact_order (
    order_key BIGSERIAL PRIMARY KEY,
    invoice_no VARCHAR(64) UNIQUE NOT NULL,
    customer_key INTEGER REFERENCES analytics.dim_customer(customer_key),
    customer_id VARCHAR(64),
    date_key INTEGER REFERENCES analytics.dim_date(date_key),
    order_timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    country_key INTEGER REFERENCES analytics.dim_country(country_key),
    line_item_count INTEGER NOT NULL,
    total_quantity INTEGER NOT NULL,
    order_value NUMERIC(14, 4) NOT NULL,
    is_cancellation BOOLEAN DEFAULT FALSE,
    is_reversal BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_fact_order_invoice ON analytics.fact_order(invoice_no);
CREATE INDEX idx_fact_order_customer_key ON analytics.fact_order(customer_key);
CREATE INDEX idx_fact_order_date_key ON analytics.fact_order(date_key);

-- Fact Transaction (Line Item Grain)
CREATE TABLE analytics.fact_transaction (
    transaction_key BIGSERIAL PRIMARY KEY,
    invoice_no VARCHAR(64) NOT NULL,
    order_key BIGINT REFERENCES analytics.fact_order(order_key),
    customer_key INTEGER REFERENCES analytics.dim_customer(customer_key),
    customer_id VARCHAR(64),
    product_key INTEGER REFERENCES analytics.dim_product(product_key),
    stock_code VARCHAR(64) NOT NULL,
    date_key INTEGER REFERENCES analytics.dim_date(date_key),
    transaction_timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    country_key INTEGER REFERENCES analytics.dim_country(country_key),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(12, 4) NOT NULL,
    line_value NUMERIC(14, 4) NOT NULL,
    event_class VARCHAR(32) NOT NULL
);

CREATE INDEX idx_fact_tx_invoice ON analytics.fact_transaction(invoice_no);
CREATE INDEX idx_fact_tx_customer_key ON analytics.fact_transaction(customer_key);
CREATE INDEX idx_fact_tx_product_key ON analytics.fact_transaction(product_key);
CREATE INDEX idx_fact_tx_date_key ON analytics.fact_transaction(date_key);
CREATE INDEX idx_fact_tx_event_class ON analytics.fact_transaction(event_class);
