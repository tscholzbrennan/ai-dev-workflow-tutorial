import plotly.express as px
import streamlit as st

from calculations import (
    compute_total_orders,
    compute_total_sales,
    load_data,
    sales_by_category,
    sales_by_month,
    sales_by_region,
)

st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")
st.title("ShopSmart Sales Dashboard")

DATA_PATH = "data/sales-data.csv"

cached_load_data = st.cache_data(load_data)

try:
    sales_df = cached_load_data(DATA_PATH)
except ValueError as e:
    st.error(f"Could not load sales data: {e}")
    st.stop()

total_sales = compute_total_sales(sales_df)
total_orders = compute_total_orders(sales_df)

col1, col2 = st.columns(2)
col1.metric("Total Sales", f"${total_sales:,.0f}")
col2.metric("Total Orders", f"{total_orders:,}")

AXIS_LABELS = {"month": "Month", "category": "Category", "region": "Region", "total_amount": "Total Sales ($)"}

monthly_df = sales_by_month(sales_df)
fig_trend = px.line(
    monthly_df, x="month", y="total_amount",
    title="Sales Trend by Month", markers=True, labels=AXIS_LABELS,
)
st.plotly_chart(fig_trend, use_container_width=True)

category_df = sales_by_category(sales_df)
region_df = sales_by_region(sales_df)

col3, col4 = st.columns(2)
fig_category = px.bar(
    category_df, x="category", y="total_amount",
    title="Sales by Category", labels=AXIS_LABELS,
)
col3.plotly_chart(fig_category, use_container_width=True)

fig_region = px.bar(
    region_df, x="region", y="total_amount",
    title="Sales by Region", labels=AXIS_LABELS,
)
col4.plotly_chart(fig_region, use_container_width=True)
