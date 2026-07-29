-- =========================================================================
-- Smart Retail Data Engineering Pipeline - Data Warehouse Star Schema DDL
-- Compatible with PostgreSQL, MySQL, and SQLite
-- =========================================================================

-- 1. Dimension Tables

CREATE TABLE IF NOT EXISTS dim_stores (
    store_id VARCHAR(50) PRIMARY KEY,
    store_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    square_feet INT,
    opened_date DATE
);

CREATE TABLE IF NOT EXISTS dim_products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    cost_price DECIMAL(10, 2) NOT NULL,
    supplier VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS dim_customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    gender VARCHAR(20),
    loyalty_tier VARCHAR(30),
    join_date DATE
);

-- 2. Fact Table

CREATE TABLE IF NOT EXISTS fact_sales (
    transaction_id VARCHAR(50) PRIMARY KEY,
    transaction_timestamp TIMESTAMP NOT NULL,
    sale_date DATE NOT NULL,
    store_id VARCHAR(50) NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    discount_pct DECIMAL(5, 2) DEFAULT 0.00,
    net_unit_price DECIMAL(10, 2) NOT NULL,
    calculated_total DECIMAL(12, 2) NOT NULL,
    total_cost DECIMAL(12, 2) NOT NULL,
    gross_profit DECIMAL(12, 2) NOT NULL,
    payment_method VARCHAR(50),
    sales_channel VARCHAR(50),
    FOREIGN KEY (store_id) REFERENCES dim_stores(store_id),
    FOREIGN KEY (product_id) REFERENCES dim_products(product_id),
    FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id)
);

-- 3. Aggregated Summary Tables

CREATE TABLE IF NOT EXISTS agg_daily_sales (
    sale_date DATE NOT NULL,
    store_id VARCHAR(50) NOT NULL,
    sales_channel VARCHAR(50) NOT NULL,
    total_transactions INT NOT NULL,
    total_units_sold INT NOT NULL,
    total_revenue DECIMAL(14, 2) NOT NULL,
    total_gross_profit DECIMAL(14, 2) NOT NULL,
    avg_order_value DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (sale_date, store_id, sales_channel)
);

CREATE TABLE IF NOT EXISTS agg_category_performance (
    category VARCHAR(50) NOT NULL,
    year INT NOT NULL,
    month INT NOT NULL,
    transactions_count INT NOT NULL,
    category_revenue DECIMAL(14, 2) NOT NULL,
    category_profit DECIMAL(14, 2) NOT NULL,
    PRIMARY KEY (category, year, month)
);
