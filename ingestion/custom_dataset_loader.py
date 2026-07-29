"""
Custom Dataset Ingestion Module for Smart Retail Data Pipeline
Allows users to drop custom sales/dimension CSV or Excel files into `data/custom_uploads/`
and automatically maps schemas for ETL ingestion and database warehouse loading.
"""

import os
import glob
import pandas as pd
from typing import Dict, Tuple, Optional

REQUIRED_SALES_COLUMNS = [
    "transaction_id", "transaction_timestamp", "store_id", 
    "customer_id", "product_id", "quantity", "unit_price"
]

COLUMN_SYNONYMS = {
    "transaction_id": ["txn_id", "order_id", "id", "sales_id"],
    "transaction_timestamp": ["timestamp", "order_date", "date", "datetime", "created_at"],
    "store_id": ["store", "branch_id", "location_id"],
    "customer_id": ["client_id", "user_id", "cust_id"],
    "product_id": ["item_id", "sku", "prod_id"],
    "quantity": ["qty", "count", "units", "items_sold"],
    "unit_price": ["price", "item_price", "rate", "cost_per_unit"]
}

class CustomDatasetLoader:
    def __init__(self, upload_dir: str = "data/custom_uploads", processed_dir: str = "data/processed"):
        self.upload_dir = upload_dir
        self.processed_dir = processed_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    def standardize_df_schema(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardizes user column names to match fact_sales schema."""
        df_cols = {c.lower().strip(): c for c in df.columns}
        rename_map = {}

        for req_col, synonyms in COLUMN_SYNONYMS.items():
            if req_col not in df_cols:
                for syn in synonyms:
                    if syn in df_cols:
                        rename_map[df_cols[syn]] = req_col
                        break

        df_renamed = df.rename(columns=rename_map)

        # Fill missing optional columns with defaults if needed
        if "discount_pct" not in df_renamed.columns:
            df_renamed["discount_pct"] = 0.0
        if "payment_method" not in df_renamed.columns:
            df_renamed["payment_method"] = "Credit Card"
        if "sales_channel" not in df_renamed.columns:
            df_renamed["sales_channel"] = "Custom Upload"

        return df_renamed

    def load_and_merge_custom_files(self) -> Tuple[Optional[pd.DataFrame], int]:
        """Finds all CSV and Excel files in data/custom_uploads/ and merges them."""
        csv_files = glob.glob(os.path.join(self.upload_dir, "*.csv"))
        excel_files = glob.glob(os.path.join(self.upload_dir, "*.xlsx")) + glob.glob(os.path.join(self.upload_dir, "*.xls"))
        
        all_files = csv_files + excel_files
        if not all_files:
            print(f"ℹ️ No custom uploaded files found in `{self.upload_dir}`.")
            return None, 0

        dfs = []
        total_rows = 0

        for file_path in all_files:
            try:
                if file_path.endswith(".csv"):
                    df_raw = pd.read_csv(file_path)
                else:
                    df_raw = pd.read_excel(file_path)

                df_standard = self.standardize_df_schema(df_raw)

                # Check if required sales columns present
                missing_cols = [c for c in REQUIRED_SALES_COLUMNS if c not in df_standard.columns]
                if missing_cols:
                    print(f"⚠️ Skipping file {os.path.basename(file_path)}: missing required columns {missing_cols}")
                    continue

                print(f"📥 [Custom Loader] Standardized user dataset `{os.path.basename(file_path)}`: {len(df_standard)} rows")
                dfs.append(df_standard)
                total_rows += len(df_standard)

            except Exception as e:
                print(f"❌ Error parsing custom dataset {file_path}: {e}")

        if not dfs:
            return None, 0

        df_combined = pd.concat(dfs, ignore_index=True)
        return df_combined, total_rows

if __name__ == "__main__":
    loader = CustomDatasetLoader()
    df_custom, count = loader.load_and_merge_custom_files()
    if df_custom is not None:
        print(f"✅ Loaded {count} custom transaction rows!")
