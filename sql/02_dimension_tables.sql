-- ============================================================================
-- 02_dimension_tables.sql: Dimension Model
-- ============================================================================

DROP TABLE IF EXISTS analytics.dim_customer CASCADE;
DROP TABLE IF EXISTS analytics.dim_product CASCADE;
DROP TABLE IF EXISTS analytics.dim_date CASCADE;
DROP TABLE IF EXISTS analytics.dim_country CASCADE;

-- Dim Customer
CREATE TABLE analytics.dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id VARCHAR(64) UNIQUE NOT NULL,
    first_purchase_date TIMESTAMP WITHOUT TIME ZONE,
    last_purchase_date TIMESTAMP WITHOUT TIME ZONE,
    primary_country VARCHAR(128),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);

CREATE INDEX idx_dim_customer_id ON analytics.dim_customer(customer_id);

-- Dim Product
CREATE TABLE analytics.dim_product (
    product_key SERIAL PRIMARY KEY,
    stock_code VARCHAR(64) UNIQUE NOT NULL,
    primary_description TEXT,
    is_manual_or_fee BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);

CREATE INDEX idx_dim_product_stock_code ON analytics.dim_product(stock_code);

-- Dim Country
CREATE TABLE analytics.dim_country (
    country_key SERIAL PRIMARY KEY,
    country_name VARCHAR(128) UNIQUE NOT NULL,
    region VARCHAR(64) DEFAULT 'International'
);

-- Dim Date
CREATE TABLE analytics.dim_date (
    date_key INTEGER PRIMARY KEY, -- YYYYMMDD
    full_date DATE UNIQUE NOT NULL,
    year_num INTEGER NOT NULL,
    quarter_num INTEGER NOT NULL,
    month_num INTEGER NOT NULL,
    month_name VARCHAR(16) NOT NULL,
    year_month VARCHAR(7) NOT NULL, -- YYYY-MM
    day_num INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(16) NOT NULL,
    is_weekend BOOLEAN NOT NULL
);
