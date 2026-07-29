"""
PySpark ETL Pipeline for Smart Retail Sales Data Engineering
Processes large datasets using Apache Spark: data cleaning, Star Schema transformation, aggregations, and Parquet output.
"""

import os
import sys
from typing import Tuple

try:
    from pyspark.sql import SparkSession
    from pyspark.sql import functions as F
    from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, TimestampType, DateType
    PYSPARK_AVAILABLE = True
except ImportError:
    PYSPARK_AVAILABLE = False

class SmartRetailSparkETL:
    def __init__(self, app_name: str = "SmartRetailSparkETL", master: str = "local[*]"):
        self.app_name = app_name
        self.master = master
        self.spark = None

    def get_or_create_spark_session(self):
        if not PYSPARK_AVAILABLE:
            raise ImportError("PySpark is not installed in the environment.")
        if self.spark is None:
            self.spark = SparkSession.builder \
                .appName(self.app_name) \
                .master(self.master) \
                .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
                .config("spark.driver.memory", "2g") \
                .getOrCreate()
            self.spark.sparkContext.setLogLevel("WARN")
        return self.spark

    def run_pipeline(self, raw_dir: str, mock_api_dir: str, output_dir: str):
        print("⚡ [PySpark ETL] Starting Apache Spark ETL Execution...")
        spark = self.get_or_create_spark_session()

        # 1. Read Raw CSV & API Data
        sales_csv_path = os.path.join(raw_dir, "sales_batch_*.csv")
        stores_csv_path = os.path.join(raw_dir, "dim_stores.csv")
        products_csv_path = os.path.join(raw_dir, "dim_products.csv")
        customers_csv_path = os.path.join(raw_dir, "dim_customers.csv")
        api_json_path = os.path.join(mock_api_dir, "recent_api_sales.json")

        df_sales_raw = spark.read.option("header", "true").option("inferSchema", "true").csv(sales_csv_path)
        df_stores_raw = spark.read.option("header", "true").option("inferSchema", "true").csv(stores_csv_path)
        df_products_raw = spark.read.option("header", "true").option("inferSchema", "true").csv(products_csv_path)
        df_customers_raw = spark.read.option("header", "true").option("inferSchema", "true").csv(customers_csv_path)

        print(f"  ├─ Raw CSV Sales records loaded: {df_sales_raw.count()}")

        # Read JSON API payload if exists
        if os.path.exists(api_json_path):
            df_api_raw = spark.read.option("multiline", "true").json(api_json_path)
            if "data" in df_api_raw.columns:
                df_api_events = df_api_raw.select(F.explode("data").alias("event")).select("event.*")
                # Drop api_ingestion_flag if present for schema match
                if "api_ingestion_flag" in df_api_events.columns:
                    df_api_events = df_api_events.drop("api_ingestion_flag")
                df_sales_raw = df_sales_raw.unionByName(df_api_events, allowMissingColumns=True)
                print(f"  ├─ API Sales merged. Combined count: {df_sales_raw.count()}")

        # 2. Data Cleaning & Transformations
        df_sales_clean = df_sales_raw \
            .dropDuplicates(["transaction_id"]) \
            .filter(F.col("quantity") > 0) \
            .filter(F.col("total_amount") > 0) \
            .withColumn("transaction_timestamp", F.to_timestamp(F.col("transaction_timestamp"))) \
            .withColumn("sale_date", F.to_date(F.col("transaction_timestamp"))) \
            .withColumn("year", F.year(F.col("sale_date"))) \
            .withColumn("month", F.month(F.col("sale_date"))) \
            .withColumn("day_of_week", F.date_format(F.col("sale_date"), "E"))

        # Calculate Net Sales & Profit Margin Estimate
        df_sales_clean = df_sales_clean \
            .withColumn("net_unit_price", F.col("unit_price") * (1 - F.col("discount_pct"))) \
            .withColumn("calculated_total", F.round(F.col("quantity") * F.col("net_unit_price"), 2))

        # Join with Products to compute Profit
        df_fact_sales = df_sales_clean.join(
            df_products_raw.select("product_id", "cost_price", "category"),
            on="product_id",
            how="left"
        ).withColumn(
            "total_cost", F.round(F.col("quantity") * F.col("cost_price"), 2)
        ).withColumn(
            "gross_profit", F.round(F.col("calculated_total") - F.col("total_cost"), 2)
        )

        print(f"  ├─ Cleaned Fact Sales records count: {df_fact_sales.count()}")

        # 3. Aggregations (Daily Sales & Category Analytics)
        df_agg_daily = df_fact_sales.groupBy("sale_date", "store_id", "sales_channel") \
            .agg(
                F.count("transaction_id").alias("total_transactions"),
                F.sum("quantity").alias("total_units_sold"),
                F.round(F.sum("calculated_total"), 2).alias("total_revenue"),
                F.round(F.sum("gross_profit"), 2).alias("total_gross_profit"),
                F.round(F.avg("calculated_total"), 2).alias("avg_order_value")
            ).orderBy("sale_date", "store_id")

        df_agg_category = df_fact_sales.groupBy("category", "year", "month") \
            .agg(
                F.count("transaction_id").alias("transactions_count"),
                F.round(F.sum("calculated_total"), 2).alias("category_revenue"),
                F.round(F.sum("gross_profit"), 2).alias("category_profit")
            ).orderBy(F.col("category_revenue").desc())

        # 4. Write Processed Datasets to Output (Parquet & CSV)
        os.makedirs(output_dir, exist_ok=True)
        
        # Fact Sales (Partitioned by Year and Month)
        fact_output = os.path.join(output_dir, "fact_sales")
        df_fact_sales.write.mode("overwrite").partitionBy("year", "month").parquet(fact_output)
        print(f"  ├─ Saved fact_sales to Parquet at: {fact_output}")

        # Dimensions & Aggregations
        df_stores_raw.write.mode("overwrite").option("header", "true").csv(os.path.join(output_dir, "dim_stores"))
        df_products_raw.write.mode("overwrite").option("header", "true").csv(os.path.join(output_dir, "dim_products"))
        df_customers_raw.write.mode("overwrite").option("header", "true").csv(os.path.join(output_dir, "dim_customers"))
        df_agg_daily.write.mode("overwrite").option("header", "true").csv(os.path.join(output_dir, "agg_daily_sales"))
        df_agg_category.write.mode("overwrite").option("header", "true").csv(os.path.join(output_dir, "agg_category_performance"))

        print("✅ [PySpark ETL] Spark ETL completed successfully!")
        return df_fact_sales, df_agg_daily

if __name__ == "__main__":
    if PYSPARK_AVAILABLE:
        etl = SmartRetailSparkETL()
        etl.run_pipeline("data/raw", "data/mock_api", "data/processed")
    else:
        print("PySpark is not available. Use etl/python_etl.py instead.")
