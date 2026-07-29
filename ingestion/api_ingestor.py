"""
API Ingestion Module for Smart Retail Data Pipeline
Fetches API payloads or mock API JSON data streams.
"""

import os
import json
import pandas as pd
import requests
from typing import Dict, Any

class APIIngestor:
    def __init__(self, api_url: str = None, mock_file_path: str = None):
        self.api_url = api_url
        self.mock_file_path = mock_file_path

    def fetch_api_sales(self) -> pd.DataFrame:
        """Fetches sales events from API endpoint or mock JSON payload."""
        if self.api_url:
            try:
                response = requests.get(self.api_url, timeout=10)
                if response.status_code == 200:
                    payload = response.json()
                    events = payload.get("data", [])
                    print(f"📡 [API Ingestor] Successfully fetched {len(events)} events from live API")
                    df = pd.DataFrame(events)
                    if not df.empty:
                        df["transaction_timestamp"] = pd.to_datetime(df["transaction_timestamp"])
                    return df
            except Exception as e:
                print(f"⚠️ [API Ingestor] Live API request failed: {e}. Falling back to mock file...")

        if self.mock_file_path and os.path.exists(self.mock_file_path):
            with open(self.mock_file_path, "r") as f:
                payload = json.load(f)
            events = payload.get("data", [])
            print(f"📥 [API Ingestor] Loaded {len(events)} sales records from mock API payload: {os.path.basename(self.mock_file_path)}")
            df = pd.DataFrame(events)
            if not df.empty:
                df["transaction_timestamp"] = pd.to_datetime(df["transaction_timestamp"])
            return df

        print("⚠️ [API Ingestor] No API data fetched.")
        return pd.DataFrame()
