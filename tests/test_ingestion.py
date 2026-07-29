import os
import sys
import pytest
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.generate_sample_data import generate_sample_data
from ingestion.csv_ingestor import CSVIngestor
from ingestion.api_ingestor import APIIngestor

@pytest.fixture(scope="module")
def setup_sample_data(tmp_path_factory):
    tmp_dir = str(tmp_path_factory.mktemp("retail_test_data"))
    generate_sample_data(base_dir=tmp_dir)
    return tmp_dir

def test_csv_ingestion(setup_sample_data):
    raw_dir = os.path.join(setup_sample_data, "data", "raw")
    ingestor = CSVIngestor(raw_dir)
    
    dimensions = ingestor.load_dimension_tables()
    assert "dim_products" in dimensions
    assert "dim_stores" in dimensions
    assert "dim_customers" in dimensions
    assert len(dimensions["dim_products"]) > 0

    sales_df = ingestor.load_sales_batches()
    assert not sales_df.empty
    assert "transaction_id" in sales_df.columns

def test_api_ingestion(setup_sample_data):
    mock_file = os.path.join(setup_sample_data, "data", "mock_api", "recent_api_sales.json")
    api_ingestor = APIIngestor(mock_file_path=mock_file)
    df_api = api_ingestor.fetch_api_sales()
    assert not df_api.empty
    assert "transaction_id" in df_api.columns
