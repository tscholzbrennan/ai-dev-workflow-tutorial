import streamlit as st

from calculations import compute_total_orders, compute_total_sales, load_data

st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")
st.title("ShopSmart Sales Dashboard")

DATA_PATH = "data/sales-data.csv"

try:
    sales_df = load_data(DATA_PATH)
except ValueError as e:
    st.error(f"Could not load sales data: {e}")
    st.stop()

total_sales = compute_total_sales(sales_df)
total_orders = compute_total_orders(sales_df)

col1, col2 = st.columns(2)
col1.metric("Total Sales", f"${total_sales:,.0f}")
col2.metric("Total Orders", f"{total_orders:,}")
