from __future__ import annotations

import streamlit as st
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
from app.Home import _load_default_data, _transform
from app.components.filters import sidebar_filters, apply_filters
from src.viz import line_simple, line_dual_axis
from src.metrics import gross_margin_pct, cogs_pct


st.set_page_config(page_title="Profitability & COGS", layout="wide")
st.title("Profitability & COGS")

dfs = _load_default_data()
td = _transform(dfs)
f = sidebar_filters(td.df_ads)

df = apply_filters(td.df_daily_blended, f)

if not df.empty:
    d = df.sort_values("date").copy()
    d["gm_pct"] = d.apply(lambda r: gross_margin_pct(r["gross_profit"], r["total_revenue"]), axis=1)
    d["cogs_pct"] = d.apply(lambda r: cogs_pct(r["cogs"], r["total_revenue"]), axis=1)
    st.subheader("GM% and COGS%")
    st.plotly_chart(line_dual_axis(d, x="date", y_left="gm_pct", y_right="cogs_pct", title="Gross Margin% vs COGS%"), use_container_width=True)

st.subheader("Revenue vs Gross Profit")
if not df.empty:
    st.plotly_chart(line_dual_axis(df.sort_values("date"), x="date", y_left="total_revenue", y_right="gross_profit", title="Revenue vs Gross Profit"), use_container_width=True)
