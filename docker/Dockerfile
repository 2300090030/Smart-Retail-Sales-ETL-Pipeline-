FROM python:3.10-slim

WORKDIR /app

# Install system dependencies & OpenJDK for PySpark
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-jre-headless \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "dashboards/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
