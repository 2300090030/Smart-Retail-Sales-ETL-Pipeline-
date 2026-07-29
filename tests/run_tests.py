"""
Automated Test Runner using Standard Unittest Framework
Executes unit & integration tests for Data Ingestion, ETL, Quality, and DB loading.
"""

import os
import sys
import unittest

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.generate_sample_data import generate_sample_data
from ingestion.csv_ingestor import CSVIngestor
from ingestion.api_ingestor import APIIngestor
from etl.python_etl import PythonETL
from data_quality.quality_checker import QualityChecker
from database.db_loader import DBLoader

class TestSmartRetailPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_dir = os.path.join(PROJECT_ROOT, "data", "test_env")
        generate_sample_data(base_dir=cls.test_dir)

    def test_1_ingestion(self):
        raw_dir = os.path.join(self.test_dir, "data", "raw")
        ingestor = CSVIngestor(raw_dir)
        dims = ingestor.load_dimension_tables()
        self.assertIn("dim_products", dims)
        self.assertIn("dim_stores", dims)

        mock_file = os.path.join(self.test_dir, "data", "mock_api", "recent_api_sales.json")
        api = APIIngestor(mock_file_path=mock_file)
        df_api = api.fetch_api_sales()
        self.assertFalse(df_api.empty)

    def test_2_etl_processing(self):
        raw_dir = os.path.join(self.test_dir, "data", "raw")
        mock_api_dir = os.path.join(self.test_dir, "data", "mock_api")
        output_dir = os.path.join(self.test_dir, "data", "processed")

        etl = PythonETL(raw_dir=raw_dir, mock_api_dir=mock_api_dir, output_dir=output_dir)
        df_fact, df_daily, dims = etl.run_pipeline()

        self.assertFalse(df_fact.empty)
        self.assertIn("gross_profit", df_fact.columns)
        self.assertTrue(os.path.exists(os.path.join(output_dir, "fact_sales.csv")))

    def test_3_data_quality(self):
        output_dir = os.path.join(self.test_dir, "data", "processed")
        checker = QualityChecker(processed_dir=output_dir)
        res = checker.run_all_checks()
        self.assertTrue(res["passed"])

    def test_4_database_load(self):
        output_dir = os.path.join(self.test_dir, "data", "processed")
        loader = DBLoader()
        loader.sqlite_path = os.path.join(self.test_dir, "data", "database", "test_retail_dw.db")
        loader.load_processed_data(processed_dir=output_dir)

        import sqlite3
        conn = sqlite3.connect(loader.sqlite_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM fact_sales;")
        count = cursor.fetchone()[0]
        conn.close()
        self.assertGreater(count, 0)

if __name__ == "__main__":
    unittest.main()
