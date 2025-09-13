from __future__ import annotations

import streamlit as st
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
import pandas as pd
from app.Home import _load_default_data, _transform
from app.components.filters import sidebar_filters, apply_filters
from src.viz import line_simple
from src.metrics import new_customer_rate, aov


st.set_page_config(page_title="Cohorts & Customers", layout="wide")
st.title("Cohorts & Customers")

dfs = _load_default_data()
td = _transform(dfs)
f = sidebar_filters(td.df_ads)

df = apply_filters(td.df_daily_blended, f)

st.subheader("New Customers & New Customer Rate")
if not df.empty:
    d = df.sort_values("date").copy()
    d["new_customer_rate"] = d.apply(lambda r: new_customer_rate(r["new_customers"], r["orders"]), axis=1)
    st.plotly_chart(line_simple(d, x="date", y="new_customers", title="New Customers"), use_container_width=True)
    st.plotly_chart(line_simple(d, x="date", y="new_customer_rate", title="New Customer Rate"), use_container_width=True)

st.subheader("AOV Trend (proxy)")
if not df.empty:
    d = df.sort_values("date").copy()
    d["aov"] = d.apply(lambda r: aov(r["total_revenue"], r["orders"]), axis=1)
    st.plotly_chart(line_simple(d, x="date", y="aov", title="Average Order Value"), use_container_width=True)

st.info("Retention proxy: using new vs repeat mix approximation from daily orders due to limited customer-level data.")
