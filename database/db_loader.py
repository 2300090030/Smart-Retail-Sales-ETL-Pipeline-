"""
Database Loader Module for Smart Retail Data Pipeline
Loads transformed data into SQLite, MySQL, or PostgreSQL using SQLAlchemy or standard sqlite3 fallback.
"""

import os
import sqlite3
import pandas as pd

try:
    from sqlalchemy import create_engine, text
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

class DBLoader:
    def __init__(self, db_type: str = "sqlite", connection_string: str = None):
        self.db_type = db_type
        self.connection_string = connection_string
        db_dir = os.path.join("data", "database")
        os.makedirs(db_dir, exist_ok=True)
        self.sqlite_path = os.path.join(db_dir, "retail_dw.db")

        if SQLALCHEMY_AVAILABLE and connection_string:
            self.engine = create_engine(connection_string)
        elif SQLALCHEMY_AVAILABLE:
            self.engine = create_engine(f"sqlite:///{self.sqlite_path}")
        else:
            self.engine = None

    def execute_sql_file(self, sql_file_path: str):
        """Executes DDL/view SQL files on the database."""
        if not os.path.exists(sql_file_path):
            print(f"⚠️ SQL file not found: {sql_file_path}")
            return
        
        with open(sql_file_path, "r", encoding="utf-8") as f:
            sql_script = f.read()

        statements = [s.strip() for s in sql_script.split(";") if s.strip()]

        if self.engine:
            with self.engine.begin() as conn:
                for stmt in statements:
                    conn.execute(text(stmt))
        else:
            os.makedirs(os.path.dirname(os.path.abspath(self.sqlite_path)), exist_ok=True)
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()
            for stmt in statements:
                try:
                    cursor.execute(stmt)
                except Exception as e:
                    print(f"  └─ Statement warning: {e}")
            conn.commit()
            conn.close()

        print(f"⚡ [DB Loader] Executed SQL file: {os.path.basename(sql_file_path)}")

    def load_processed_data(self, processed_dir: str = "data/processed"):
        """Reads transformed CSV files from processed directory and loads into database."""
        print("💾 [DB Loader] Loading processed datasets into Database Warehouse...")

        schema_path = os.path.join("database", "schema.sql")
        views_path = os.path.join("database", "views.sql")
        self.execute_sql_file(schema_path)

        tables_to_load = [
            ("dim_products", "dim_products.csv", "replace"),
            ("dim_stores", "dim_stores.csv", "replace"),
            ("dim_customers", "dim_customers.csv", "replace"),
            ("fact_sales", "fact_sales.csv", "replace"),
            ("agg_daily_sales", "agg_daily_sales.csv", "replace"),
            ("agg_category_performance", "agg_category_performance.csv", "replace"),
        ]

        if self.engine:
            with self.engine.begin() as conn:
                for table_name, csv_name, mode in tables_to_load:
                    file_path = os.path.join(processed_dir, csv_name)
                    if os.path.exists(file_path):
                        df = pd.read_csv(file_path)
                        df.to_sql(table_name, conn, if_exists=mode, index=False)
                        print(f"  └─ Table `{table_name}` updated: {len(df)} records inserted.")
                    else:
                        print(f"  └─ File missing: {file_path}")
        else:
            conn = sqlite3.connect(self.sqlite_path)
            for table_name, csv_name, mode in tables_to_load:
                file_path = os.path.join(processed_dir, csv_name)
                if os.path.exists(file_path):
                    df = pd.read_csv(file_path)
                    df.to_sql(table_name, conn, if_exists=mode, index=False)
                    print(f"  └─ Table `{table_name}` updated: {len(df)} records inserted.")
                else:
                    print(f"  └─ File missing: {file_path}")
            conn.close()

        self.execute_sql_file(views_path)
        print("✅ [DB Loader] Database warehouse load complete!")

if __name__ == "__main__":
    loader = DBLoader()
    loader.load_processed_data()
