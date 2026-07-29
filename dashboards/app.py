"""
Smart Retail Analytics Interactive Web Dashboard
Built with Streamlit and Plotly for high-impact executive visual insights.
Formated in Indian Rupees (₹) with dynamic dataset filtering and dataset ingestion.
"""

import os
import sys
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as io
import streamlit as st

# Add project root path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from etl.python_etl import PythonETL
from database.db_loader import DBLoader
from data_quality.quality_checker import QualityChecker

st.set_page_config(
    page_title="Smart Retail Sales Analytics (INR)",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for rich aesthetics and dark glassmorphism
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #e0e6ed;
    }
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.8));
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(8px);
        text-align: center;
    }
    .metric-value {
        font-size: 2.1rem;
        font-weight: 700;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-label {
        font-size: 0.95rem;
        color: #94a3b8;
        margin-top: 5px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .filter-header {
        color: #38bdf8;
        font-weight: 700;
        font-size: 1.1rem;
        margin-top: 10px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_dashboard_data():
    processed_dir = os.path.join(PROJECT_ROOT, "data", "processed")
    fact_path = os.path.join(processed_dir, "fact_sales.csv")
    stores_path = os.path.join(processed_dir, "dim_stores.csv")
    products_path = os.path.join(processed_dir, "dim_products.csv")

    if not os.path.exists(fact_path):
        return None, None, None

    df_fact = pd.read_csv(fact_path)
    df_stores = pd.read_csv(stores_path)
    df_products = pd.read_csv(products_path)

    df_fact["sale_date"] = pd.to_datetime(df_fact["sale_date"]).dt.date
    return df_fact, df_stores, df_products

def process_uploaded_custom_file(uploaded_file):
    custom_dir = os.path.join(PROJECT_ROOT, "data", "custom_uploads")
    os.makedirs(custom_dir, exist_ok=True)
    save_path = os.path.join(custom_dir, uploaded_file.name)

    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.sidebar.info(f"💾 Saved file `{uploaded_file.name}`. Executing ETL pipeline...")

    # Run ETL Pipeline
    raw_dir = os.path.join(PROJECT_ROOT, "data", "raw")
    mock_api_dir = os.path.join(PROJECT_ROOT, "data", "mock_api")
    output_dir = os.path.join(PROJECT_ROOT, "data", "processed")

    etl = PythonETL(raw_dir=raw_dir, mock_api_dir=mock_api_dir, output_dir=output_dir, custom_dir=custom_dir)
    etl.run_pipeline()

    # Load Database
    loader = DBLoader()
    loader.load_processed_data(processed_dir=output_dir)

    st.cache_data.clear()
    st.sidebar.success(f"🎉 Custom dataset `{uploaded_file.name}` successfully integrated!")

def main():
    st.title("🛍️ Smart Retail Sales Analytics Dashboard")
    st.markdown("Real-time pipeline analytics formatted in **Indian Rupees (₹)**.")

    # --- Sidebar: Custom Dataset Uploader ---
    st.sidebar.markdown("### 📤 Add Your Own Dataset")
    uploaded_file = st.sidebar.file_uploader(
        "Upload Custom Sales CSV or Excel:",
        type=["csv", "xlsx", "xls"],
        help="Upload sales transactions with columns like transaction_id, store_id, product_id, quantity, unit_price, date."
    )

    if uploaded_file is not None:
        if st.sidebar.button("⚡ Ingest & Process Dataset"):
            process_uploaded_custom_file(uploaded_file)

    st.sidebar.markdown("---")

    df_fact, df_stores, df_products = load_dashboard_data()

    if df_fact is None or df_fact.empty:
        st.error("⚠️ Processed datasets not found! Please run the ETL pipeline first:")
        st.code("python etl/python_etl.py", language="bash")
        return

    # Merge store & product metadata safely
    df_merged = df_fact.merge(df_stores[["store_id", "store_name", "region", "city"]], on="store_id", how="left")
    df_merged["region"] = df_merged["region"].fillna("Other / Custom")
    df_merged["store_name"] = df_merged["store_name"].fillna(df_merged["store_id"])
    df_merged["category"] = df_merged["category"].fillna("General Retail")
    df_merged["sales_channel"] = df_merged["sales_channel"].fillna("Direct")

    # --- Sidebar: Dynamic Dataset Analytics Filters ---
    st.sidebar.markdown('<div class="filter-header">🔍 Filter Analytics by Dataset</div>', unsafe_allow_html=True)
    
    # 1. Date Range Filter
    min_date = df_merged["sale_date"].min()
    max_date = df_merged["sale_date"].max()

    start_date, end_date = st.sidebar.date_input(
        "Select Date Range:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # 2. Sales Channel / Dataset Source Filter
    available_channels = sorted(list(df_merged["sales_channel"].unique()))
    selected_channels = st.sidebar.multiselect(
        "Sales Channel / Data Source:",
        options=available_channels,
        default=available_channels
    )

    # 3. Region Filter
    available_regions = sorted(list(df_merged["region"].unique()))
    selected_regions = st.sidebar.multiselect(
        "Select Region:",
        options=available_regions,
        default=available_regions
    )

    # 4. Store Branch Filter
    available_stores = sorted(list(df_merged["store_name"].unique()))
    selected_stores = st.sidebar.multiselect(
        "Select Store Branch:",
        options=available_stores,
        default=available_stores
    )

    # 5. Product Category Filter
    available_categories = sorted(list(df_merged["category"].unique()))
    selected_categories = st.sidebar.multiselect(
        "Product Category:",
        options=available_categories,
        default=available_categories
    )

    # Apply Dynamic Filtering to Active Dataset
    df_filtered = df_merged[
        (df_merged["sale_date"] >= start_date) &
        (df_merged["sale_date"] <= end_date) &
        (df_merged["sales_channel"].isin(selected_channels)) &
        (df_merged["region"].isin(selected_regions)) &
        (df_merged["store_name"].isin(selected_stores)) &
        (df_merged["category"].isin(selected_categories))
    ]

    st.sidebar.markdown(f"**Filtered Records:** `{len(df_filtered):,}` / `{len(df_merged):,}`")

    if df_filtered.empty:
        st.warning("⚠️ No data matches the selected filter criteria. Please broaden your sidebar filters!")
        return

    # --- KPI Row ---
    total_revenue = df_filtered["calculated_total"].sum()
    total_profit = df_filtered["gross_profit"].sum()
    profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    total_orders = len(df_filtered)
    avg_order_val = total_revenue / total_orders if total_orders > 0 else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">₹{total_revenue:,.2f}</div><div class="metric-label">Total Revenue</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">₹{total_profit:,.2f}</div><div class="metric-label">Gross Profit</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{profit_margin:.1f}%</div><div class="metric-label">Profit Margin</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{total_orders:,}</div><div class="metric-label">Total Orders</div></div>', unsafe_allow_html=True)
    with col5:
        st.markdown(f'<div class="metric-card"><div class="metric-value">₹{avg_order_val:,.2f}</div><div class="metric-label">Avg Order Value</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Charts Row 1 ---
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("📈 Daily Sales & Revenue Trend (₹)")
        df_trend = df_filtered.groupby("sale_date")["calculated_total"].sum().reset_index()
        fig_trend = px.line(
            df_trend, 
            x="sale_date", 
            y="calculated_total", 
            template="plotly_dark",
            color_discrete_sequence=["#38bdf8"]
        )
        fig_trend.update_layout(xaxis_title="Date", yaxis_title="Revenue (₹)", margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_trend, use_container_width=True)

    with c2:
        st.subheader("🍕 Revenue by Product Category")
        df_cat = df_filtered.groupby("category")["calculated_total"].sum().reset_index()
        fig_cat = px.pie(
            df_cat, 
            names="category", 
            values="calculated_total", 
            hole=0.4,
            template="plotly_dark",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_cat.update_layout(margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_cat, use_container_width=True)

    # --- Charts Row 2 ---
    c3, c4 = st.columns(2)

    with c3:
        st.subheader("🏢 Regional & Store Performance (₹)")
        df_region = df_filtered.groupby(["region", "store_name"])["calculated_total"].sum().reset_index()
        fig_region = px.bar(
            df_region, 
            x="store_name", 
            y="calculated_total", 
            color="region", 
            barmode="group",
            template="plotly_dark"
        )
        fig_region.update_layout(xaxis_title="Store Branch", yaxis_title="Revenue (₹)", margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_region, use_container_width=True)

    with c4:
        st.subheader("💳 Sales Channel & Payment Method Matrix")
        df_channel = df_filtered.groupby(["sales_channel", "payment_method"])["calculated_total"].sum().reset_index()
        fig_channel = px.sunburst(
            df_channel, 
            path=["sales_channel", "payment_method"], 
            values="calculated_total",
            template="plotly_dark",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_channel.update_layout(margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_channel, use_container_width=True)

    # --- Raw Data Table ---
    with st.expander("📄 View Active Filtered Fact Dataset"):
        st.dataframe(df_filtered, use_container_width=True)

if __name__ == "__main__":
    main()
