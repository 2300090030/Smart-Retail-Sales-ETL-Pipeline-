"""
Sample Data Generator for Smart Retail Data Pipeline
Generates synthetic sales transactions, stores, products, and customer review API payload formatted in Indian Rupees (₹).
"""

import os
import json
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def generate_sample_data(base_dir: str = "."):
    raw_dir = os.path.join(base_dir, "data", "raw")
    mock_api_dir = os.path.join(base_dir, "data", "mock_api")
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(mock_api_dir, exist_ok=True)

    print("🚀 Generating synthetic retail datasets (in Indian Rupees ₹)...")
    random.seed(42)
    np.random.seed(42)

    # 1. Product Dimension Data (Rupees pricing)
    categories = ["Electronics", "Clothing", "Home & Kitchen", "Beauty & Care", "Sports & Outdoors"]
    products = []
    product_ids = [f"PRD-{1000 + i}" for i in range(50)]
    for p_id in product_ids:
        cat = random.choice(categories)
        unit_price = round(random.uniform(499.0, 25000.0), 2)
        cost_price = round(unit_price * random.uniform(0.55, 0.78), 2)
        products.append({
            "product_id": p_id,
            "product_name": f"{cat} Item {p_id.split('-')[1]}",
            "category": cat,
            "unit_price": unit_price,
            "cost_price": cost_price,
            "supplier": f"Supplier {random.randint(1, 10)}"
        })
    df_products = pd.DataFrame(products)
    df_products.to_csv(os.path.join(raw_dir, "dim_products.csv"), index=False)
    print(f"  └─ Created dim_products.csv ({len(df_products)} rows)")

    # 2. Store Dimension Data (Indian Cities & Regions)
    cities = ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai", "Kolkata", "Pune", "Ahmedabad"]
    regions = {"Mumbai": "West", "Pune": "West", "Ahmedabad": "West", "Delhi": "North", "Bengaluru": "South", "Hyderabad": "South", "Chennai": "South", "Kolkata": "East"}
    stores = []
    store_ids = [f"STR-{100 + i}" for i in range(15)]
    for s_id in store_ids:
        city = random.choice(cities)
        stores.append({
            "store_id": s_id,
            "store_name": f"Smart Retail {city} Hub",
            "city": city,
            "region": regions[city],
            "square_feet": random.randint(15000, 85000),
            "opened_date": (datetime(2018, 1, 1) + timedelta(days=random.randint(0, 1500))).strftime("%Y-%m-%d")
        })
    df_stores = pd.DataFrame(stores)
    df_stores.to_csv(os.path.join(raw_dir, "dim_stores.csv"), index=False)
    print(f"  └─ Created dim_stores.csv ({len(df_stores)} rows)")

    # 3. Customer Dimension Data
    customers = []
    customer_ids = [f"CUST-{5000 + i}" for i in range(200)]
    tiers = ["Bronze", "Silver", "Gold", "Platinum"]
    for c_id in customer_ids:
        customers.append({
            "customer_id": c_id,
            "customer_name": f"Customer {c_id.split('-')[1]}",
            "gender": random.choice(["M", "F", "Other"]),
            "loyalty_tier": random.choice(tiers),
            "join_date": (datetime(2020, 1, 1) + timedelta(days=random.randint(0, 1000))).strftime("%Y-%m-%d")
        })
    df_customers = pd.DataFrame(customers)
    df_customers.to_csv(os.path.join(raw_dir, "dim_customers.csv"), index=False)
    print(f"  └─ Created dim_customers.csv ({len(df_customers)} rows)")

    # 4. Transaction Sales Data (Multi-file CSV batch simulate)
    start_date = datetime(2026, 1, 1)
    payment_methods = ["UPI", "Credit Card", "Debit Card", "Net Banking", "Cash"]
    channels = ["In-Store", "Online", "Mobile App"]

    batch_sales_1 = []
    batch_sales_2 = []

    for transaction_idx in range(2500):
        t_id = f"TXN-{100000 + transaction_idx}"
        p_info = random.choice(products)
        qty = random.randint(1, 5)
        unit_p = p_info["unit_price"]
        disc_pct = round(random.choice([0.0, 0.05, 0.10, 0.15, 0.20]), 2)
        total_amt = round(qty * unit_p * (1 - disc_pct), 2)
        tx_date = start_date + timedelta(days=random.randint(0, 180), hours=random.randint(8, 21), minutes=random.randint(0, 59))
        
        row = {
            "transaction_id": t_id,
            "transaction_timestamp": tx_date.strftime("%Y-%m-%d %H:%M:%S"),
            "store_id": random.choice(store_ids),
            "customer_id": random.choice(customer_ids),
            "product_id": p_info["product_id"],
            "quantity": qty,
            "unit_price": unit_p,
            "discount_pct": disc_pct,
            "total_amount": total_amt,
            "payment_method": random.choice(payment_methods),
            "sales_channel": random.choice(channels)
        }

        if transaction_idx < 1250:
            batch_sales_1.append(row)
        else:
            batch_sales_2.append(row)

    df_b1 = pd.DataFrame(batch_sales_1)
    df_b2 = pd.DataFrame(batch_sales_2)
    df_b1.to_csv(os.path.join(raw_dir, "sales_batch_2026_q1.csv"), index=False)
    df_b2.to_csv(os.path.join(raw_dir, "sales_batch_2026_q2.csv"), index=False)
    print(f"  └─ Created sales_batch_2026_q1.csv ({len(df_b1)} rows)")
    print(f"  └─ Created sales_batch_2026_q2.csv ({len(df_b2)} rows)")

    # 5. Mock API Feedback / Online Sales stream JSON payload
    api_events = []
    for idx in range(150):
        t_id = f"API-TXN-{200000 + idx}"
        p_info = random.choice(products)
        qty = random.randint(1, 4)
        unit_p = p_info["unit_price"]
        total_amt = round(qty * unit_p, 2)
        tx_date = start_date + timedelta(days=random.randint(150, 200), hours=random.randint(9, 22))

        api_events.append({
            "transaction_id": t_id,
            "transaction_timestamp": tx_date.strftime("%Y-%m-%d %H:%M:%S"),
            "store_id": random.choice(store_ids),
            "customer_id": random.choice(customer_ids),
            "product_id": p_info["product_id"],
            "quantity": qty,
            "unit_price": unit_p,
            "discount_pct": 0.0,
            "total_amount": total_amt,
            "payment_method": random.choice(["UPI", "Credit Card"]),
            "sales_channel": "Online",
            "api_ingestion_flag": True
        })

    with open(os.path.join(mock_api_dir, "recent_api_sales.json"), "w") as f:
        json.dump({"status": "success", "count": len(api_events), "data": api_events}, f, indent=2)
    print(f"  └─ Created mock API JSON payload ({len(api_events)} items)")

    print("✅ Sample data generation completed successfully!")

if __name__ == "__main__":
    generate_sample_data()
