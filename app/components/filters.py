from __future__ import annotations

import streamlit as st
import pandas as pd


def init_filters(df_ads: pd.DataFrame):
    if "filters" not in st.session_state:
        st.session_state["filters"] = {
            "date_range": (df_ads["date"].min(), df_ads["date"].max()) if not df_ads.empty else (None, None),
            "channel": sorted([c for c in df_ads["channel"].dropna().unique()]) if "channel" in df_ads else [],
            "tactic": sorted([c for c in df_ads["tactic"].dropna().unique()]) if "tactic" in df_ads else [],
            "state": sorted([c for c in df_ads["state"].dropna().unique()]) if "state" in df_ads else [],
            "campaign": sorted([c for c in df_ads["campaign"].dropna().unique()]) if "campaign" in df_ads else [],
            "blended": True,
            "include_quality_flags": True,
        }


def sidebar_filters(df_ads: pd.DataFrame):
    init_filters(df_ads)
    f = st.session_state["filters"]
    st.sidebar.header("Filters")

    if not df_ads.empty:
        dr = st.sidebar.date_input(
            "Date Range",
            value=(f["date_range"][0].date(), f["date_range"][1].date()),
            min_value=df_ads["date"].min().date(),
            max_value=df_ads["date"].max().date(),
        )
        f["date_range"] = (pd.to_datetime(dr[0]), pd.to_datetime(dr[1]))

        f["blended"] = st.sidebar.toggle("Show blended view", value=f.get("blended", True))
        f["include_quality_flags"] = st.sidebar.toggle("Include quality-flagged rows", value=f.get("include_quality_flags", True))

        f["channel"] = st.sidebar.multiselect("Channel", options=sorted(df_ads["channel"].dropna().unique()), default=f.get("channel", []))
        f["tactic"] = st.sidebar.multiselect("Tactic", options=sorted(df_ads["tactic"].dropna().unique()), default=f.get("tactic", []))
        f["state"] = st.sidebar.multiselect("State", options=sorted(df_ads["state"].dropna().unique()), default=f.get("state", []))
        f["campaign"] = st.sidebar.multiselect("Campaign", options=sorted(df_ads["campaign"].dropna().unique()), default=f.get("campaign", []))

    st.session_state["filters"] = f
    return f


def apply_filters(df: pd.DataFrame, f: dict) -> pd.DataFrame:
    if df.empty:
        return df
    m = pd.Series(True, index=df.index)
    if f.get("date_range") and df["date"].notna().any():
        start, end = f["date_range"]
        m &= (df["date"] >= start) & (df["date"] <= end)
    for col in ["channel", "tactic", "state", "campaign"]:
        vals = f.get(col) or []
        if len(vals) > 0 and col in df.columns:
            m &= df[col].isin(vals)
    if not f.get("include_quality_flags", True) and "quality_flag" in df.columns:
        m &= ~df["quality_flag"].astype(bool)
    return df[m].copy()

