-- =========================================================================
-- Analytical Views for Power BI & Business Reporting
-- =========================================================================

-- View 1: Detailed Sales Performance with Dimension Metadata
CREATE VIEW IF NOT EXISTS v_sales_detailed AS
SELECT 
    f.transaction_id,
    f.transaction_timestamp,
    f.sale_date,
    f.payment_method,
    f.sales_channel,
    f.quantity,
    f.unit_price,
    f.discount_pct,
    f.calculated_total AS revenue,
    f.total_cost,
    f.gross_profit,
    s.store_id,
    s.store_name,
    s.city AS store_city,
    s.region AS store_region,
    p.product_id,
    p.product_name,
    p.category AS product_category,
    c.customer_id,
    c.customer_name,
    c.loyalty_tier
FROM fact_sales f
LEFT JOIN dim_stores s ON f.store_id = s.store_id
LEFT JOIN dim_products p ON f.product_id = p.product_id
LEFT JOIN dim_customers c ON f.customer_id = c.customer_id;

-- View 2: Regional Performance Summary
CREATE VIEW IF NOT EXISTS v_regional_sales_summary AS
SELECT 
    s.region,
    s.city,
    COUNT(DISTINCT f.transaction_id) AS total_orders,
    SUM(f.quantity) AS total_items_sold,
    SUM(f.calculated_total) AS total_revenue,
    SUM(f.gross_profit) AS total_profit,
    AVG(f.calculated_total) AS avg_order_value
FROM fact_sales f
JOIN dim_stores s ON f.store_id = s.store_id
GROUP BY s.region, s.city;
