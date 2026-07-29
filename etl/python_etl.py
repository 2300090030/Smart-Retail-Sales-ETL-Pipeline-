"""
Python (Pandas) ETL Pipeline for Smart Retail Sales Data Engineering
Provides robust ETL processing without requiring Java / full PySpark installation.
"""

import os
import pandas as pd
import numpy as np
import sys
from typing import Dict, Tuple

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ingestion.csv_ingestor import CSVIngestor
from ingestion.api_ingestor import APIIngestor
from ingestion.custom_dataset_loader import CustomDatasetLoader

class PythonETL:
    def __init__(self, raw_dir: str = "data/raw", mock_api_dir: str = "data/mock_api", output_dir: str = "data/processed", custom_dir: str = "data/custom_uploads"):
        self.raw_dir = raw_dir
        self.mock_api_dir = mock_api_dir
        self.output_dir = output_dir
        self.custom_dir = custom_dir

    def run_pipeline(self) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, pd.DataFrame]]:
        print("🐍 [Python ETL] Executing Pandas ETL pipeline...")
        
        # 1. Ingestion
        csv_ingestor = CSVIngestor(self.raw_dir)
        dimensions = csv_ingestor.load_dimension_tables()
        df_csv_sales = csv_ingestor.load_sales_batches()

        mock_json_path = os.path.join(self.mock_api_dir, "recent_api_sales.json")
        api_ingestor = APIIngestor(mock_file_path=mock_json_path)
        df_api_sales = api_ingestor.fetch_api_sales()

        # Load Custom Uploaded Datasets if available
        custom_loader = CustomDatasetLoader(upload_dir=self.custom_dir, processed_dir=self.output_dir)
        df_custom_sales, custom_count = custom_loader.load_and_merge_custom_files()

        # Combine Sales
        sales_sources = [df_csv_sales]
        if not df_api_sales.empty:
            sales_sources.append(df_api_sales)
        if df_custom_sales is not None and not df_custom_sales.empty:
            sales_sources.append(df_custom_sales)

        df_sales = pd.concat(sales_sources, ignore_index=True)

        print(f"  ├─ Total combined sales records: {len(df_sales)}")

        # 2. Transformations
        df_sales.drop_duplicates(subset=["transaction_id"], inplace=True)
        df_sales = df_sales[(df_sales["quantity"] > 0) & (df_sales["total_amount"] > 0)].copy()

        df_sales["transaction_timestamp"] = pd.to_datetime(df_sales["transaction_timestamp"])
        df_sales["sale_date"] = df_sales["transaction_timestamp"].dt.date
        df_sales["year"] = df_sales["transaction_timestamp"].dt.year
        df_sales["month"] = df_sales["transaction_timestamp"].dt.month
        df_sales["day_of_week"] = df_sales["transaction_timestamp"].dt.day_name()

        # Join Product Data for Cost & Profit Calculation
        df_products = dimensions["dim_products"]
        df_fact = df_sales.merge(
            df_products[["product_id", "category", "cost_price"]],
            on="product_id",
            how="left"
        )

        df_fact["net_unit_price"] = df_fact["unit_price"] * (1 - df_fact["discount_pct"])
        df_fact["calculated_total"] = (df_fact["quantity"] * df_fact["net_unit_price"]).round(2)
        df_fact["total_cost"] = (df_fact["quantity"] * df_fact["cost_price"]).round(2)
        df_fact["gross_profit"] = (df_fact["calculated_total"] - df_fact["total_cost"]).round(2)

        print(f"  ├─ Transformed Fact Sales count: {len(df_fact)}")

        # 3. Aggregations
        df_agg_daily = df_fact.groupby(["sale_date", "store_id", "sales_channel"]).agg(
            total_transactions=("transaction_id", "count"),
            total_units_sold=("quantity", "sum"),
            total_revenue=("calculated_total", "sum"),
            total_gross_profit=("gross_profit", "sum"),
            avg_order_value=("calculated_total", "mean")
        ).reset_index()

        df_agg_daily["total_revenue"] = df_agg_daily["total_revenue"].round(2)
        df_agg_daily["total_gross_profit"] = df_agg_daily["total_gross_profit"].round(2)
        df_agg_daily["avg_order_value"] = df_agg_daily["avg_order_value"].round(2)

        df_agg_category = df_fact.groupby(["category", "year", "month"]).agg(
            transactions_count=("transaction_id", "count"),
            category_revenue=("calculated_total", "sum"),
            category_profit=("gross_profit", "sum")
        ).reset_index()

        # 4. Save Processed Files
        os.makedirs(self.output_dir, exist_ok=True)
        df_fact.to_csv(os.path.join(self.output_dir, "fact_sales.csv"), index=False)
        df_agg_daily.to_csv(os.path.join(self.output_dir, "agg_daily_sales.csv"), index=False)
        df_agg_category.to_csv(os.path.join(self.output_dir, "agg_category_performance.csv"), index=False)

        for dim_name, df_dim in dimensions.items():
            df_dim.to_csv(os.path.join(self.output_dir, f"{dim_name}.csv"), index=False)

        print("✅ [Python ETL] Pandas ETL completed successfully!")
        return df_fact, df_agg_daily, dimensions

if __name__ == "__main__":
    etl = PythonETL()
    etl.run_pipeline()
