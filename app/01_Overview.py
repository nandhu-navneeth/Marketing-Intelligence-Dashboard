from __future__ import annotations

import streamlit as st
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
from app.Home import _load_default_data, _transform
from app.components.filters import sidebar_filters, apply_filters
from src.viz import line_dual_axis, stacked_bar
from src.metrics import blended_roas


st.set_page_config(page_title="Overview", layout="wide")
st.title("Overview")

dfs = _load_default_data()
td = _transform(dfs)
f = sidebar_filters(td.df_ads)

df_blended = apply_filters(td.df_daily_blended, f)
df_by_channel = apply_filters(td.df_daily_by_channel, f)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Revenue", f"${df_blended['total_revenue'].sum():,.0f}")
with col2:
    st.metric("Spend", f"${df_blended['spend'].sum():,.0f}")
with col3:
    broas = blended_roas(float(df_blended['attributed_revenue'].sum() or 0.0), float(df_blended['spend'].sum() or 0.0))
    st.metric("Blended ROAS", f"{broas:.2f}x")

if not df_blended.empty:
    st.plotly_chart(line_dual_axis(df_blended.sort_values("date"), "date", "spend", "attributed_revenue", "Spend vs Attributed Revenue"), use_container_width=True)
    st.plotly_chart(line_dual_axis(df_blended.sort_values("date"), "date", "total_revenue", "orders", "Total Revenue vs Orders"), use_container_width=True)

if not df_by_channel.empty:
    st.plotly_chart(stacked_bar(df_by_channel.sort_values("date"), "date", "spend", "channel", "Spend by Channel"), use_container_width=True)
