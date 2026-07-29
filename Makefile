.PHONY: help generate-data etl etl-spark load-db quality-check run-dashboard test docker-up docker-down pipeline

help:
	@echo "Smart Retail Data Engineering Pipeline CLI Commands:"
	@echo "  make generate-data  : Synthesize retail sales CSVs & API data"
	@echo "  make etl            : Run Python (Pandas) ETL pipeline"
	@echo "  make etl-spark      : Run PySpark ETL pipeline"
	@echo "  make load-db        : Load processed datasets into SQL Data Warehouse"
	@echo "  make quality-check  : Run automated data quality verification suite"
	@echo "  make run-dashboard  : Launch interactive Streamlit Web Dashboard"
	@echo "  make test           : Run pytest test suite"
	@echo "  make pipeline       : Run complete pipeline end-to-end"
	@echo "  make docker-up      : Start Postgres & Web Dashboard in Docker"

generate-data:
	python scripts/generate_sample_data.py

etl:
	python etl/python_etl.py

etl-spark:
	python etl/spark_etl.py

load-db:
	python database/db_loader.py

quality-check:
	python data_quality/quality_checker.py

run-dashboard:
	streamlit run dashboards/app.py

test:
	pytest tests/

pipeline: generate-data etl quality-check load-db
	@echo "✅ Complete pipeline executed successfully!"

docker-up:
	docker-compose -f docker/docker-compose.yml up --build -d

docker-down:
	docker-compose -f docker/docker-compose.yml down
