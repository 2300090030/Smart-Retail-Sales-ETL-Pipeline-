# Power BI Integration Guide - Smart Retail Data Engineering Pipeline

This guide explains how to connect Power BI Desktop to the Smart Retail Data Warehouse database or load the processed CSV outputs directly into Power BI.

---

## 🔌 Connection Method 1: Database Connection (MySQL / PostgreSQL / SQLite)

### Step 1: Open Power BI Desktop
Launch Power BI Desktop and select **Get Data** $\rightarrow$ **More...**

### Step 2: Select Data Source
- For PostgreSQL: Choose **PostgreSQL database** $\rightarrow$ Server: `localhost:5432` $\rightarrow$ Database: `smart_retail_dw`
- For MySQL: Choose **MySQL database** $\rightarrow$ Server: `localhost:3306` $\rightarrow$ Database: `smart_retail_dw`
- Select Data Connectivity Mode: **Import** or **DirectQuery**.

### Step 3: Import Star Schema Tables & Views
Import the following tables/views:
1. `fact_sales`
2. `dim_stores`
3. `dim_products`
4. `dim_customers`
5. `v_sales_detailed`
6. `agg_daily_sales`

---

## 📁 Connection Method 2: Direct CSV Import

If running standalone without a database server:
1. In Power BI Desktop, click **Get Data** $\rightarrow$ **Text/CSV**.
2. Navigate to `data/processed/` in this repository.
3. Import `fact_sales.csv`, `dim_stores.csv`, `dim_products.csv`, and `dim_customers.csv`.

---

## 📐 Data Model Setup (Star Schema Relationships)

Create the following relationships in Power BI **Model View**:

| From Table | From Column | To Table | To Column | Cardinality | Cross Filter |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `fact_sales` | `store_id` | `dim_stores` | `store_id` | Many to One (*:1) | Single |
| `fact_sales` | `product_id` | `dim_products` | `product_id` | Many to One (*:1) | Single |
| `fact_sales` | `customer_id` | `dim_customers` | `customer_id` | Many to One (*:1) | Single |

---

## 📊 Adding DAX Measures

1. In Power BI, right-click on `fact_sales` $\rightarrow$ Select **New Measure**.
2. Copy DAX formulas from `dashboards/dax_measures.dax` (e.g., `Total Revenue`, `Gross Profit Margin %`, `Average Order Value`, `YoY Revenue Growth %`).

---

## 🎨 Recommended Visual Dashboard Layout

1. **Top Bar**: Card Visuals for `Total Revenue`, `Gross Profit`, `Profit Margin %`, and `Total Orders`.
2. **Line Chart**: `Total Revenue` by `sale_date` (Trend Analysis).
3. **Donut Chart**: `Total Revenue` by `dim_products[category]`.
4. **Stacked Bar Chart**: `Total Revenue` by `dim_stores[store_name]` broken down by `dim_stores[region]`.
5. **Matrix / Slicer**: Interactive Filter by Region, Sales Channel, and Payment Method.
