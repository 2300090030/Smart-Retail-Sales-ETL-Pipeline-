-- =========================================================================
-- SQL Direct Queries for Power BI Data Import / DirectQuery Connection
-- =========================================================================

-- Query 1: Power BI Fact Sales Table Query
SELECT 
    f.transaction_id,
    f.transaction_timestamp,
    f.sale_date,
    f.store_id,
    f.customer_id,
    f.product_id,
    f.quantity,
    f.unit_price,
    f.discount_pct,
    f.calculated_total AS revenue,
    f.total_cost,
    f.gross_profit,
    f.payment_method,
    f.sales_channel
FROM fact_sales f;

-- Query 2: Daily Revenue & Store KPI Aggregation Query
SELECT 
    a.sale_date,
    a.store_id,
    a.sales_channel,
    a.total_transactions,
    a.total_units_sold,
    a.total_revenue,
    a.total_gross_profit,
    a.avg_order_value
FROM agg_daily_sales a;
