from __future__ import annotations

import streamlit as st
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
from app.Home import _load_default_data, _transform
from app.components.filters import sidebar_filters, apply_filters
from src.viz import pareto_chart


st.set_page_config(page_title="Campaigns", layout="wide")
st.title("Campaigns")

dfs = _load_default_data()
td = _transform(dfs)
f = sidebar_filters(td.df_ads)

df_camp = apply_filters(td.df_campaigns, f)

st.subheader("Pareto of Attributed Revenue by Campaign")
if not df_camp.empty:
    d = df_camp.copy().sort_values("attributed_revenue", ascending=False)
    d["label"] = d["channel"].str.capitalize() + " · " + d["campaign"].astype(str)
    fig = pareto_chart(d, value_col="attributed_revenue", label_col="label", title="80/20 Contribution")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Campaign Detail Table")
st.dataframe(df_camp.sort_values(["attributed_revenue"], ascending=False), use_container_width=True)
if not df_camp.empty:
    st.download_button("Download Campaigns (CSV)", df_camp.to_csv(index=False).encode(), file_name="campaigns.csv", mime="text/csv")
