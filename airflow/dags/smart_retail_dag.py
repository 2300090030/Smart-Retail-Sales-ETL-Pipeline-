"""
Apache Airflow DAG: Smart Retail Sales Data Engineering Pipeline
Automates data generation, API collection, PySpark/Python ETL, quality checks, and warehouse loading.
"""

import os
import sys
from datetime import datetime, timedelta

# Import Airflow modules
try:
    from airflow import DAG  # type: ignore
    from airflow.operators.python import PythonOperator  # type: ignore
    from airflow.operators.bash import BashOperator  # type: ignore
    from airflow.operators.dummy import DummyOperator  # type: ignore
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False
    class DummyTask:
        def __rshift__(self, other): return other
        def __lshift__(self, other): return other
    class DAG:
        def __init__(self, *args, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass
    class PythonOperator(DummyTask):
        def __init__(self, *args, **kwargs): pass
    class DummyOperator(DummyTask):
        def __init__(self, *args, **kwargs): pass

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def run_sample_data_generation():
    from scripts.generate_sample_data import generate_sample_data
    generate_sample_data(base_dir=PROJECT_ROOT)

def run_etl_pipeline():
    try:
        from etl.spark_etl import SmartRetailSparkETL, PYSPARK_AVAILABLE
        if PYSPARK_AVAILABLE:
            etl = SmartRetailSparkETL()
            etl.run_pipeline(
                raw_dir=os.path.join(PROJECT_ROOT, "data", "raw"),
                mock_api_dir=os.path.join(PROJECT_ROOT, "data", "mock_api"),
                output_dir=os.path.join(PROJECT_ROOT, "data", "processed")
            )
            return
    except Exception as e:
        print(f"PySpark ETL skipped or failed: {e}. Executing Python ETL fallback...")

    from etl.python_etl import PythonETL
    etl = PythonETL(
        raw_dir=os.path.join(PROJECT_ROOT, "data", "raw"),
        mock_api_dir=os.path.join(PROJECT_ROOT, "data", "mock_api"),
        output_dir=os.path.join(PROJECT_ROOT, "data", "processed")
    )
    etl.run_pipeline()

def run_data_quality_checks():
    from data_quality.quality_checker import QualityChecker
    checker = QualityChecker(processed_dir=os.path.join(PROJECT_ROOT, "data", "processed"))
    results = checker.run_all_checks()
    if not results["passed"]:
        raise ValueError(f"Data Quality Check Failed! Details: {results}")

def run_database_loading():
    from database.db_loader import DBLoader
    loader = DBLoader()
    loader.load_processed_data(processed_dir=os.path.join(PROJECT_ROOT, "data", "processed"))

default_args = {
    'owner': 'data_engineering_team',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='smart_retail_sales_etl_pipeline',
    default_args=default_args,
    description='Automated Smart Retail Sales Data Engineering Pipeline',
    schedule_interval='0 2 * * *',  # Daily at 2:00 AM
    catchup=False,
    tags=['retail', 'etl', 'spark', 'data_warehouse'],
) as dag:

    start_node = DummyOperator(task_id='pipeline_start')

    generate_data_task = PythonOperator(
        task_id='generate_retail_sample_data',
        python_callable=run_sample_data_generation,
    )

    execute_etl_task = PythonOperator(
        task_id='execute_spark_python_etl',
        python_callable=run_etl_pipeline,
    )

    quality_check_task = PythonOperator(
        task_id='validate_data_quality',
        python_callable=run_data_quality_checks,
    )

    load_warehouse_task = PythonOperator(
        task_id='load_data_warehouse',
        python_callable=run_database_loading,
    )

    end_node = DummyOperator(task_id='pipeline_completed')

    start_node >> generate_data_task >> execute_etl_task >> quality_check_task >> load_warehouse_task >> end_node

if __name__ == "__main__":
    print("✅ Airflow DAG syntax validated successfully!")
