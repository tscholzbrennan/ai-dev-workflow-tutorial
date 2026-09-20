import streamlit as st

from calculations import load_data

st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")
st.title("ShopSmart Sales Dashboard")

DATA_PATH = "data/sales-data.csv"

try:
    sales_df = load_data(DATA_PATH)
except ValueError as e:
    st.error(f"Could not load sales data: {e}")
    st.stop()
