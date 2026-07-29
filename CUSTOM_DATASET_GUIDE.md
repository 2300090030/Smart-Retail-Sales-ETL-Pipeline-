# 📥 How to Add Your Own Dataset to the Smart Retail Pipeline

You can easily integrate your own custom retail sales CSV or Excel files into the pipeline using either **Method 1 (Drag & Drop UI)** or **Method 2 (Folder Drop)**.

---

## 🎯 Method 1: Upload via Interactive Web Dashboard (Easiest)

1. Open the live dashboard at **`http://localhost:8501`** (or launch via `python -m streamlit run dashboards/app.py`).
2. Look at the left sidebar under **📤 Add Your Own Dataset**.
3. Drag & drop your CSV or Excel (`.csv`, `.xlsx`, `.xls`) file.
4. Click the **⚡ Ingest & Process Dataset** button.
5. The pipeline will automatically format your columns, run ETL transformations, update the Data Warehouse database, and refresh all visual metrics on the dashboard instantly!

---

## 📁 Method 2: File Drop in `data/custom_uploads/`

1. Copy your custom CSV or Excel file into the directory:
   ```
   data/custom_uploads/
   ```
2. Run the pipeline CLI command:
   ```bash
   python etl/python_etl.py && python database/db_loader.py
   ```
3. The custom loader will automatically map your column headers and merge your sales records into `fact_sales` and the database.

---

## 📋 Supported Column Names & Auto-Mapping

The custom ingestor automatically detects and maps column name variations:

| Pipeline Standard Field | Accepted Column Headers in Your Dataset | Description |
| :--- | :--- | :--- |
| `transaction_id` | `transaction_id`, `txn_id`, `order_id`, `id`, `sales_id` | Unique order ID |
| `transaction_timestamp` | `transaction_timestamp`, `timestamp`, `order_date`, `date`, `created_at` | Date/time of sale |
| `store_id` | `store_id`, `store`, `branch_id`, `location_id` | Store branch ID (e.g. STR-101) |
| `customer_id` | `customer_id`, `client_id`, `user_id`, `cust_id` | Customer ID (e.g. CUST-5001) |
| `product_id` | `product_id`, `item_id`, `sku`, `prod_id` | Product SKU/ID (e.g. PRD-1001) |
| `quantity` | `quantity`, `qty`, `count`, `units`, `items_sold` | Number of items purchased |
| `unit_price` | `unit_price`, `price`, `item_price`, `rate` | Price per unit |
| `discount_pct` *(Optional)* | `discount_pct`, `discount` | Discount percentage (default: 0.0) |
| `payment_method` *(Optional)* | `payment_method`, `payment_type` | Credit Card, Cash, UPI, Debit Card |
| `sales_channel` *(Optional)* | `sales_channel`, `channel` | In-Store, Online, Mobile App |

---

## 🧪 Sample Custom CSV Format

Here is a quick sample format you can paste into `data/custom_uploads/my_custom_sales.csv`:

```csv
order_id,date,store,cust_id,sku,qty,price,sales_channel
MY-TXN-001,2026-07-29 10:00:00,STR-101,CUST-5001,PRD-1001,3,150.00,Online
MY-TXN-002,2026-07-29 11:30:00,STR-102,CUST-5002,PRD-1002,1,299.99,In-Store
```
