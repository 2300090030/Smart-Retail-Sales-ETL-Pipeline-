"""
CSV Ingestion Module for Smart Retail Data Pipeline
Ingests multi-file sales batches and dimension CSV files into unified DataFrames.
"""

import os
import glob
import pandas as pd
from typing import Dict, List, Tuple

class CSVIngestor:
    def __init__(self, raw_data_dir: str):
        self.raw_data_dir = raw_data_dir

    def load_dimension_tables(self) -> Dict[str, pd.DataFrame]:
        """Loads store, product, and customer dimension CSVs."""
        dimensions = {}
        for dim_name in ["dim_products", "dim_stores", "dim_customers"]:
            file_path = os.path.join(self.raw_data_dir, f"{dim_name}.csv")
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                dimensions[dim_name] = df
                print(f"📥 [CSV Ingestor] Loaded {dim_name}: {len(df)} records")
            else:
                raise FileNotFoundError(f"Required dimension file missing: {file_path}")
        return dimensions

    def load_sales_batches(self) -> pd.DataFrame:
        """Finds and combines all sales CSV files matching pattern."""
        pattern = os.path.join(self.raw_data_dir, "sales_batch_*.csv")
        batch_files = glob.glob(pattern)
        
        if not batch_files:
            print(f"⚠️ Warning: No sales batch CSV files found in {self.raw_data_dir}")
            return pd.DataFrame()

        dfs = []
        for file_path in batch_files:
            df = pd.read_csv(file_path)
            print(f"📥 [CSV Ingestor] Ingested file {os.path.basename(file_path)}: {len(df)} rows")
            dfs.append(df)

        combined_sales = pd.concat(dfs, ignore_index=True)
        # Standardize column types and drop exact duplicates
        combined_sales.drop_duplicates(subset=["transaction_id"], inplace=True)
        combined_sales["transaction_timestamp"] = pd.to_datetime(combined_sales["transaction_timestamp"])
        
        print(f"✅ [CSV Ingestor] Total deduplicated sales records: {len(combined_sales)}")
        return combined_sales
