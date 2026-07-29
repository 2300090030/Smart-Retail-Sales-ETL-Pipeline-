import os
import sys
import pytest
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.generate_sample_data import generate_sample_data
from etl.python_etl import PythonETL

@pytest.fixture(scope="module")
def sample_environment(tmp_path_factory):
    tmp_dir = str(tmp_path_factory.mktemp("etl_test_env"))
    generate_sample_data(base_dir=tmp_dir)
    return tmp_dir

def test_python_etl_execution(sample_environment):
    raw_dir = os.path.join(sample_environment, "data", "raw")
    mock_api_dir = os.path.join(sample_environment, "data", "mock_api")
    output_dir = os.path.join(sample_environment, "data", "processed")

    etl = PythonETL(raw_dir=raw_dir, mock_api_dir=mock_api_dir, output_dir=output_dir)
    df_fact, df_daily, dimensions = etl.run_pipeline()

    assert not df_fact.empty
    assert "gross_profit" in df_fact.columns
    assert "calculated_total" in df_fact.columns
    assert (df_fact["gross_profit"] == (df_fact["calculated_total"] - df_fact["total_cost"]).round(2)).all()
    assert os.path.exists(os.path.join(output_dir, "fact_sales.csv"))
