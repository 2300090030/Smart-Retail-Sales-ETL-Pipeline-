import os
import sys
import sqlite3
import pytest
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.generate_sample_data import generate_sample_data
from etl.python_etl import PythonETL
from database.db_loader import DBLoader

@pytest.fixture(scope="module")
def db_test_env(tmp_path_factory):
    tmp_dir = str(tmp_path_factory.mktemp("db_test_env"))
    generate_sample_data(base_dir=tmp_dir)
    
    raw_dir = os.path.join(tmp_dir, "data", "raw")
    mock_api_dir = os.path.join(tmp_dir, "data", "mock_api")
    output_dir = os.path.join(tmp_dir, "data", "processed")

    etl = PythonETL(raw_dir=raw_dir, mock_api_dir=mock_api_dir, output_dir=output_dir)
    etl.run_pipeline()
    return tmp_dir, output_dir

def test_database_loading(db_test_env):
    tmp_dir, output_dir = db_test_env
    db_path = os.path.join(tmp_dir, "data", "database", "retail_dw.db")

    loader = DBLoader()
    loader.sqlite_path = db_path
    loader.load_processed_data(processed_dir=output_dir)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    assert "fact_sales" in tables
    assert "dim_stores" in tables
    assert "dim_products" in tables
    assert "dim_customers" in tables
    assert "agg_daily_sales" in tables
