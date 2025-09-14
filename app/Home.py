from __future__ import annotations

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Ensure repo root on path when running pages directly
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.io_load import load_sources
from src.validate import validate_frames
from src.transform import transform_inputs, TransformedData
from src.insights import generate_overview_insights
from app.components.filters import sidebar_filters, apply_filters
from app.components.kpi import kpi_card
from src.metrics import blended_roas, aov, gross_margin_pct
from src.formatting import fmt_currency_compact, fmt_int_compact, fmt_ratio
from src.viz import line_dual_axis, stacked_bar


@st.cache_data(show_spinner=False)
def _load_default_data() -> dict[str, pd.DataFrame]:
    data_dir = Path(__file__).resolve().parents[1] / "data"
    return load_sources(data_dir)


@st.cache_data(show_spinner=False)
def _transform(dfs: dict[str, pd.DataFrame]) -> TransformedData:
    return transform_inputs(dfs)


st.set_page_config(page_title="Marketing Intelligence Dashboard", layout="wide")
st.title("Marketing Intelligence Dashboard")

st.caption("Upload a .zip or use default sample data in `data/`.")

uploaded = st.file_uploader("Upload data .zip (optional)", type=["zip"])  # type: ignore
if uploaded is not None:
    dfs = load_sources(uploaded)
else:
    dfs = _load_default_data()

try:
    warnings = validate_frames(dfs)
except Exception as e:
    warnings = [f"Validation issue: {e}"]
td = _transform(dfs)

f = sidebar_filters(td.df_ads)

df_blended = apply_filters(td.df_daily_blended, f)
df_by_channel = apply_filters(td.df_daily_by_channel, f)

# Period-over-period deltas (same length previous period)
delta_map = {}
if not df_blended.empty and f.get("date_range"):
    start, end = f["date_range"]
    days = (end - start).days + 1
    prev_end = start - pd.Timedelta(days=1)
    prev_start = prev_end - pd.Timedelta(days=days - 1)
    cur = df_blended[(df_blended["date"] >= start) & (df_blended["date"] <= end)]
    prev = df_blended[(df_blended["date"] >= prev_start) & (df_blended["date"] <= prev_end)]
    def _delta(cur_v: float, prev_v: float) -> str:
        if prev_v == 0:
            return ""
        d = (cur_v - prev_v) / prev_v
        return f"{d:+.0%} vs prev"
    delta_map = {
        "total_revenue": _delta(float(cur["total_revenue"].sum()), float(prev["total_revenue"].sum() or 0.0)),
        "gross_profit": _delta(float(cur["gross_profit"].sum()), float(prev["gross_profit"].sum() or 0.0)),
        "orders": _delta(float(cur["orders"].sum()), float(prev["orders"].sum() or 0.0)),
        "new_customers": _delta(float(cur["new_customers"].sum()), float(prev["new_customers"].sum() or 0.0)),
        "spend": _delta(float(cur["spend"].sum()), float(prev["spend"].sum() or 0.0)),
        "broas": _delta(
            float(cur["attributed_revenue"].sum()) / max(float(cur["spend"].sum()), 1e-9),
            float(prev["attributed_revenue"].sum()) / max(float(prev["spend"].sum()), 1e-9) if len(prev) else 0.0,
        ),
    }

# KPI row
col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    kpi_card("Total Revenue", fmt_currency_compact(float(df_blended['total_revenue'].sum() or 0.0)), delta=delta_map.get("total_revenue"))
with col2:
    kpi_card("Gross Profit", fmt_currency_compact(float(df_blended['gross_profit'].sum() or 0.0)), delta=delta_map.get("gross_profit"))
with col3:
    kpi_card("Orders", fmt_int_compact(float(df_blended['orders'].sum() or 0.0)), delta=delta_map.get("orders"))
with col4:
    kpi_card("New Customers", fmt_int_compact(float(df_blended['new_customers'].sum() or 0.0)), delta=delta_map.get("new_customers"))
with col5:
    spend_total = float(df_blended['spend'].sum() or 0.0)
    kpi_card("Spend", fmt_currency_compact(spend_total), delta=delta_map.get("spend"))
with col6:
    broas = blended_roas(float(df_blended['attributed_revenue'].sum() or 0.0), spend_total)
    kpi_card("Blended ROAS", fmt_ratio(broas), delta=delta_map.get("broas"))

st.subheader("Time Series")
if not df_blended.empty:
    fig1 = line_dual_axis(df_blended.sort_values("date"), x="date", y_left="spend", y_right="attributed_revenue", title="Spend vs Attributed Revenue")
    st.plotly_chart(fig1, use_container_width=True)
    fig2 = line_dual_axis(df_blended.sort_values("date"), x="date", y_left="total_revenue", y_right="orders", title="Total Revenue vs Orders")
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Channel Mix Over Time")
if not df_by_channel.empty:
    fig3 = stacked_bar(df_by_channel.sort_values("date"), x="date", y="spend", color="channel", title="Spend by Channel")
    st.plotly_chart(fig3, use_container_width=True)

st.subheader("Insights")
insights = generate_overview_insights(df_by_channel)
for b in insights:
    st.write(f"• {b}")

with st.expander("Data Quality Warnings"):
    if warnings:
        for w in warnings:
            st.warning(w)
    else:
        st.success("No validation warnings.")
