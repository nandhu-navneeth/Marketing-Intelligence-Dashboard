from __future__ import annotations

import streamlit as st
import pandas as pd


def _to_str_options(series: pd.Series) -> list[str]:
    if series.empty:
        return []
    return sorted([str(x) for x in series.dropna().astype(str).unique()])


def init_filters(df_ads: pd.DataFrame):
    if "filters" not in st.session_state:
        channels = _to_str_options(df_ads.get("channel", pd.Series(dtype="string"))) if not df_ads.empty else []
        tactics = _to_str_options(df_ads.get("tactic", pd.Series(dtype="string"))) if not df_ads.empty else []
        states = _to_str_options(df_ads.get("state", pd.Series(dtype="string"))) if not df_ads.empty else []
        campaigns = _to_str_options(df_ads.get("campaign", pd.Series(dtype="string"))) if not df_ads.empty else []
        st.session_state["filters"] = {
            "date_range": (df_ads["date"].min(), df_ads["date"].max()) if not df_ads.empty else (None, None),
            "channel": channels,
            "tactic": tactics,
            "state": states,
            "campaign": campaigns,
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
            key="date_range_picker",
        )
        f["date_range"] = (pd.to_datetime(dr[0]), pd.to_datetime(dr[1]))

        f["blended"] = st.sidebar.toggle("Show blended view", value=f.get("blended", True), key="blended_toggle")
        f["include_quality_flags"] = st.sidebar.toggle("Include quality-flagged rows", value=f.get("include_quality_flags", True), key="quality_toggle")

        channels = _to_str_options(df_ads["channel"]) if "channel" in df_ads else []
        tactics = _to_str_options(df_ads["tactic"]) if "tactic" in df_ads else []
        states = _to_str_options(df_ads["state"]) if "state" in df_ads else []
        campaigns = _to_str_options(df_ads["campaign"]) if "campaign" in df_ads else []

        # Intersect current selections with available options to avoid resets
        sel_channels = [c for c in (f.get("channel") or []) if c in channels] or channels
        sel_tactics = [t for t in (f.get("tactic") or []) if t in tactics] or tactics
        sel_states = [s for s in (f.get("state") or []) if s in states] or states
        sel_campaigns = [c for c in (f.get("campaign") or []) if c in campaigns] or campaigns

        f["channel"] = st.sidebar.multiselect("Channel", options=channels, default=sel_channels, key="channel_ms")
        f["tactic"] = st.sidebar.multiselect("Tactic", options=tactics, default=sel_tactics, key="tactic_ms")
        f["state"] = st.sidebar.multiselect("State", options=states, default=sel_states, key="state_ms")
        f["campaign"] = st.sidebar.multiselect("Campaign", options=campaigns, default=sel_campaigns, key="campaign_ms")

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
            m &= df[col].astype(str).isin([str(v) for v in vals])
    if not f.get("include_quality_flags", True) and "quality_flag" in df.columns:
        m &= ~df["quality_flag"].astype(bool)
    return df[m].copy()
