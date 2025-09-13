from __future__ import annotations

from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
from pydantic import BaseModel, Field, validator

from .config import AD_COLS, BUSINESS_COLS


class AdRow(BaseModel):
    date: datetime
    tactic: Optional[str]
    state: Optional[str]
    campaign: str
    impressions: int = Field(ge=0)
    clicks: int = Field(ge=0)
    spend: float = Field(ge=0)
    attributed_revenue: float = Field(ge=0)

    @validator("tactic", "state", pre=True, always=True)
    def _trim(cls, v):  # type: ignore
        return v.strip() if isinstance(v, str) else v


class BusinessRow(BaseModel):
    date: datetime
    orders: int = Field(ge=0)
    new_orders: int = Field(ge=0)
    new_customers: int = Field(ge=0)
    total_revenue: float = Field(ge=0)
    gross_profit: float
    cogs: float = Field(ge=0)


def _check_continuous_dates(series: pd.Series) -> List[str]:
    warnings: List[str] = []
    s = pd.to_datetime(series.dropna()).sort_values().unique()
    if len(s) <= 1:
        return warnings
    expected = pd.date_range(start=s[0], end=s[-1], freq="D")
    missing = set(expected.date) - set(pd.to_datetime(s).date)
    if missing:
        warnings.append(f"Missing {len(missing)} daily dates in window {s[0].date()}..{s[-1].date()}.")
    return warnings


def validate_frames(dfs: Dict[str, pd.DataFrame]) -> List[str]:
    """Validate input frames with light checks.

    Returns a list of warning strings. Critical schema issues raise ValueError.
    """
    warnings: List[str] = []

    # Schema presence
    for key in [k for k in dfs.keys() if k != "business"]:
        df = dfs[key]
        missing = [c for c in AD_COLS if c not in df.columns]
        if missing:
            raise ValueError(f"{key}: missing columns {missing}")
        # Row-level checks via Pydantic for a small sample to avoid heavy cost
        for _, row in df.head(1000).iterrows():
            try:
                AdRow(**{c: row.get(c) for c in AD_COLS})
            except Exception as e:
                raise ValueError(f"{key}: row validation failed: {e}")

        # Quality flags
        bad_clicks = df[(df["impressions"] == 0) & (df["clicks"] > 0)]
        if not bad_clicks.empty:
            warnings.append(f"{key}: {len(bad_clicks)} rows have clicks>0 with impressions==0.")

        warnings.extend(_check_continuous_dates(df["date"]))

        if (df[["impressions", "spend"]] < 0).any().any():
            warnings.append(f"{key}: negative impressions or spend observed; rows will be dropped.")

    if "business" in dfs:
        b = dfs["business"]
        missing = [c for c in BUSINESS_COLS if c not in b.columns]
        if missing:
            raise ValueError(f"business: missing columns {missing}")
        for _, row in b.head(1000).iterrows():
            try:
                BusinessRow(**{c: row.get(c) for c in BUSINESS_COLS})
            except Exception as e:
                raise ValueError(f"business: row validation failed: {e}")
        warnings.extend(_check_continuous_dates(b["date"]))
        # Reconcile gross profit ~ total_revenue - cogs
        tol = 1e-6
        diff = (b["total_revenue"] - b["cogs"]) - b["gross_profit"]
        mismatches = diff[diff.abs() > tol]
        if not mismatches.empty:
            warnings.append(
                f"business: {len(mismatches)} rows where gross_profit != total_revenue - cogs (>|{tol}|)."
            )

    return warnings

