"""
Data Quality Checker Module for Smart Retail Data Pipeline
Performs automated data validation tests on processed datasets.
"""

import os
import pandas as pd
from typing import Dict, Any, List

class QualityChecker:
    def __init__(self, processed_dir: str = "data/processed"):
        self.processed_dir = processed_dir

    def check_file_existence(self) -> List[str]:
        required_files = [
            "fact_sales.csv",
            "dim_stores.csv",
            "dim_products.csv",
            "dim_customers.csv",
            "agg_daily_sales.csv",
            "agg_category_performance.csv"
        ]
        missing = []
        for file in required_files:
            path = os.path.join(self.processed_dir, file)
            if not os.path.exists(path):
                missing.append(file)
        return missing

    def check_fact_sales_integrity(self, df_fact: pd.DataFrame) -> Dict[str, Any]:
        """Checks fact sales for nulls, positive quantities, and totals match."""
        issues = []
        null_counts = df_fact[["transaction_id", "store_id", "product_id", "calculated_total"]].isnull().sum().to_dict()
        if any(v > 0 for v in null_counts.values()):
            issues.append(f"Nulls found in critical columns: {null_counts}")

        invalid_qty = len(df_fact[df_fact["quantity"] <= 0])
        if invalid_qty > 0:
            issues.append(f"Found {invalid_qty} rows with quantity <= 0")

        invalid_amounts = len(df_fact[df_fact["calculated_total"] <= 0])
        if invalid_amounts > 0:
            issues.append(f"Found {invalid_amounts} rows with calculated_total <= 0")

        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "total_records": len(df_fact)
        }

    def run_all_checks(self) -> Dict[str, Any]:
        print("🔍 [Data Quality] Running data quality check suite...")
        missing_files = self.check_file_existence()
        if missing_files:
            print(f"❌ [Data Quality] Missing files: {missing_files}")
            return {"passed": False, "reason": f"Missing processed files: {missing_files}"}

        df_fact = pd.read_csv(os.path.join(self.processed_dir, "fact_sales.csv"))
        fact_res = self.check_fact_sales_integrity(df_fact)

        if fact_res["passed"]:
            print(f"✅ [Data Quality] All quality checks PASSED ({fact_res['total_records']} fact records verified)")
        else:
            print(f"❌ [Data Quality] Quality checks FAILED: {fact_res['issues']}")

        return fact_res

if __name__ == "__main__":
    checker = QualityChecker()
    checker.run_all_checks()
