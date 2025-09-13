from __future__ import annotations

import streamlit as st
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
import pandas as pd
from app.Home import _load_default_data, _transform
from app.components.filters import sidebar_filters, apply_filters
from src.viz import treemap, scatter_bubble


st.set_page_config(page_title="Channel Drilldown", layout="wide")
st.title("Channel Drilldown")

dfs = _load_default_data()
td = _transform(dfs)
f = sidebar_filters(td.df_ads)

df_daily = apply_filters(td.df_daily_by_channel, f)
df_all = apply_filters(td.df_ads, f)

st.subheader("Spend and Revenue by Tactic")
if not df_all.empty:
    by_tactic = df_all.groupby(["channel", "tactic"]).agg(spend=("spend", "sum"), attr=("attributed_revenue", "sum")).reset_index()
    fig = treemap(by_tactic, path=["channel", "tactic"], values="spend", color="attr", title="Spend Treemap (color=Attributed Revenue)")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Campaign League Table")
if not df_all.empty:
    league = df_all.groupby(["channel", "tactic", "campaign"]).agg(
        impressions=("impressions", "sum"),
        clicks=("clicks", "sum"),
        spend=("spend", "sum"),
        attributed_revenue=("attributed_revenue", "sum"),
    ).reset_index()
    league["ctr"] = (league["clicks"]/league["impressions"]).fillna(0.0)
    league["cpc"] = (league["spend"]/league["clicks"]).fillna(0.0)
    league["cpm"] = (league["spend"]*1000/league["impressions"]).fillna(0.0)
    league["roas"] = (league["attributed_revenue"]/league["spend"]).fillna(0.0)
    st.dataframe(league.sort_values(["roas"], ascending=False), use_container_width=True)
    st.download_button("Download League Table (CSV)", league.to_csv(index=False).encode(), file_name="campaign_league.csv", mime="text/csv")

st.subheader("Spend vs ROAS")
if not df_all.empty:
    camp = df_all.groupby(["channel", "tactic", "campaign"]).agg(spend=("spend", "sum"), attr=("attributed_revenue", "sum")).reset_index()
    camp["roas"] = (camp["attr"]/camp["spend"]).replace([pd.NA, pd.NaT], 0).fillna(0.0)
    fig2 = scatter_bubble(camp, x="spend", y="roas", size="attr", color="channel", hover_name="campaign", title="Spend vs ROAS (bubble = Attrib Rev)")
    st.plotly_chart(fig2, use_container_width=True)
