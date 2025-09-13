from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple
import pandas as pd
import numpy as np

from .config import (
    CHANNELS,
    AD_COLS,
    BUSINESS_COLS,
    DTYPE_ADS,
    DTYPE_BUSINESS,
    RENAMES_GENERIC,
    QUALITY_FLAGS_COL,
)
from .metrics import ctr, cpc, cpm, roas


def _standardize_ads(df: pd.DataFrame, channel: str) -> pd.DataFrame:
    df = df.rename(columns=RENAMES_GENERIC)
    # Downselect and reorder
    cols = [c for c in AD_COLS if c in df.columns]
    df = df[cols].copy()
    # Types
    for col, dt in DTYPE_ADS.items():
        if col not in df.columns:
            df[col] = pd.Series([pd.NA] * len(df))
        if dt.startswith("datetime"):
            df[col] = pd.to_datetime(df[col], errors="coerce")
        elif dt == "string":
            df[col] = df[col].astype("string").str.strip()
        elif dt in ("Int64", "Int32"):
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
        else:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Remove negatives and obvious anomalies
    df = df[(df["impressions"] >= 0) & (df["spend"] >= 0)].copy()

    # Fill tactic/state
    df["tactic"] = df["tactic"].fillna("unknown")
    df["state"] = df["state"].fillna("unknown")

    df["channel"] = channel
    df[QUALITY_FLAGS_COL] = (
        (df["impressions"] == 0) & (df["clicks"].fillna(0) > 0)
    )
    return df


def _standardize_business(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns=RENAMES_GENERIC)
    cols = [c for c in BUSINESS_COLS if c in df.columns]
    df = df[cols].copy()
    for col, dt in DTYPE_BUSINESS.items():
        if col not in df.columns:
            df[col] = pd.Series([pd.NA] * len(df))
        if dt.startswith("datetime"):
            df[col] = pd.to_datetime(df[col], errors="coerce")
        elif dt == "string":
            df[col] = df[col].astype("string").str.strip()
        elif dt in ("Int64", "Int32"):
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
        else:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


@dataclass
class TransformedData:
    df_ads: pd.DataFrame
    df_business: pd.DataFrame
    df_daily_by_channel: pd.DataFrame
    df_daily_blended: pd.DataFrame
    df_campaigns: pd.DataFrame


def transform_inputs(dfs: Dict[str, pd.DataFrame]) -> TransformedData:
    """Standardize, aggregate, and build joined daily datasets.

    Returns a TransformedData object with main views ready for analytics.
    """
    frames = []
    for ch in CHANNELS:
        if ch in dfs:
            frames.append(_standardize_ads(dfs[ch], ch))
    df_ads = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=AD_COLS + ["channel"])  # type: ignore

    df_business = _standardize_business(dfs.get("business", pd.DataFrame(columns=BUSINESS_COLS)))

    # Aggregate to daily channel/tactic/campaign
    if not df_ads.empty:
        grp_keys = ["date", "channel", "tactic", "state", "campaign"]
        agg = df_ads.groupby(grp_keys, dropna=False).agg(
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            spend=("spend", "sum"),
            attributed_revenue=("attributed_revenue", "sum"),
            quality_flag=(QUALITY_FLAGS_COL, "max"),
        )
        df_daily = agg.reset_index()
    else:
        df_daily = pd.DataFrame(columns=["date", "channel", "tactic", "state", "campaign", "impressions", "clicks", "spend", "attributed_revenue", "quality_flag"])  # type: ignore

    # Derived metrics on daily rows
    if not df_daily.empty:
        df_daily["ctr"] = df_daily.apply(lambda r: ctr(r["clicks"], r["impressions"]), axis=1)
        df_daily["cpc"] = df_daily.apply(lambda r: cpc(r["spend"], r["clicks"]), axis=1)
        df_daily["cpm"] = df_daily.apply(lambda r: cpm(r["spend"], r["impressions"]), axis=1)
        df_daily["roas"] = df_daily.apply(lambda r: roas(r["attributed_revenue"], r["spend"]), axis=1)

    # Daily by channel (sum across tactics/campaigns per channel)
    if not df_daily.empty:
        agg_ch = df_daily.groupby(["date", "channel"], dropna=False).agg(
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            spend=("spend", "sum"),
            attributed_revenue=("attributed_revenue", "sum"),
            quality_flag=("quality_flag", "max"),
        ).reset_index()
        df_daily_by_channel = agg_ch.copy()
        df_daily_by_channel["ctr"] = df_daily_by_channel.apply(lambda r: ctr(r["clicks"], r["impressions"]), axis=1)
        df_daily_by_channel["cpc"] = df_daily_by_channel.apply(lambda r: cpc(r["spend"], r["clicks"]), axis=1)
        df_daily_by_channel["cpm"] = df_daily_by_channel.apply(lambda r: cpm(r["spend"], r["impressions"]), axis=1)
        df_daily_by_channel["roas"] = df_daily_by_channel.apply(lambda r: roas(r["attributed_revenue"], r["spend"]), axis=1)
    else:
        df_daily_by_channel = pd.DataFrame(columns=["date", "channel", "impressions", "clicks", "spend", "attributed_revenue", "quality_flag", "ctr", "cpc", "cpm", "roas"])  # type: ignore

    # Blended marketing daily view (all channels combined)
    if not df_daily_by_channel.empty:
        blended = df_daily_by_channel.groupby(["date"]).agg(
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            spend=("spend", "sum"),
            attributed_revenue=("attributed_revenue", "sum"),
            quality_flag=("quality_flag", "max"),
        ).reset_index()
        # Derived
        blended["ctr"] = blended.apply(lambda r: ctr(r["clicks"], r["impressions"]), axis=1)
        blended["cpc"] = blended.apply(lambda r: cpc(r["spend"], r["clicks"]), axis=1)
        blended["cpm"] = blended.apply(lambda r: cpm(r["spend"], r["impressions"]), axis=1)
        blended["roas"] = blended.apply(lambda r: roas(r["attributed_revenue"], r["spend"]), axis=1)
        df_daily_blended = blended
    else:
        df_daily_blended = pd.DataFrame(columns=["date", "impressions", "clicks", "spend", "attributed_revenue", "quality_flag", "ctr", "cpc", "cpm", "roas"])  # type: ignore

    # Join to business by date
    df_business_daily = df_business.groupby("date", dropna=False).agg(
        orders=("orders", "sum"),
        new_orders=("new_orders", "sum"),
        new_customers=("new_customers", "sum"),
        total_revenue=("total_revenue", "sum"),
        gross_profit=("gross_profit", "sum"),
        cogs=("cogs", "sum"),
    ).reset_index()

    # Prepare campaign rollups
    if not df_daily.empty:
        df_campaigns = df_daily.groupby(["channel", "tactic", "state", "campaign"]).agg(
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            spend=("spend", "sum"),
            attributed_revenue=("attributed_revenue", "sum"),
        ).reset_index()
        df_campaigns["ctr"] = df_campaigns.apply(lambda r: ctr(r["clicks"], r["impressions"]), axis=1)
        df_campaigns["cpc"] = df_campaigns.apply(lambda r: cpc(r["spend"], r["clicks"]), axis=1)
        df_campaigns["cpm"] = df_campaigns.apply(lambda r: cpm(r["spend"], r["impressions"]), axis=1)
        df_campaigns["roas"] = df_campaigns.apply(lambda r: roas(r["attributed_revenue"], r["spend"]), axis=1)
    else:
        df_campaigns = pd.DataFrame(columns=["channel", "tactic", "state", "campaign", "impressions", "clicks", "spend", "attributed_revenue", "ctr", "cpc", "cpm", "roas"])  # type: ignore

    # Merge marketing with business for blended and by-channel views
    df_daily_blended = df_daily_blended.merge(df_business_daily, on="date", how="left")
    if not df_daily_by_channel.empty:
        df_daily_by_channel = df_daily_by_channel.merge(df_business_daily, on="date", how="left")

    return TransformedData(
        df_ads=df_ads,
        df_business=df_business_daily,
        df_daily_by_channel=df_daily_by_channel,
        df_daily_blended=df_daily_blended,
        df_campaigns=df_campaigns,
    )

