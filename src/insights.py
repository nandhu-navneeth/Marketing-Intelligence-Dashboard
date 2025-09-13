from __future__ import annotations

from typing import List
import pandas as pd
from .metrics import blended_roas


def generate_overview_insights(df_daily_by_channel: pd.DataFrame) -> List[str]:
    """Return a few human-readable insight bullets for Overview page.

    Expects columns: date, channel, spend, attributed_revenue.
    """
    bullets: List[str] = []
    if df_daily_by_channel.empty:
        return ["No marketing data available for insights."]

    last_date = df_daily_by_channel["date"].max()
    recent = df_daily_by_channel[df_daily_by_channel["date"] == last_date]
    total_spend = float(recent["spend"].sum())
    total_attr = float(recent["attributed_revenue"].sum())
    b_roas = blended_roas(total_attr, total_spend)
    bullets.append(
        f"On {last_date.date()}, blended ROAS was {b_roas:.2f} across all channels."
    )

    ch = (
        recent.groupby("channel").agg(spend=("spend", "sum"), attr=("attributed_revenue", "sum"))
    )
    ch["share_spend"] = ch["spend"] / max(ch["spend"].sum(), 1e-9)
    ch = ch.sort_values("attr", ascending=False)
    if not ch.empty:
        top = ch.index[0]
        attr_share = ch.iloc[0]["attr"] / max(ch["attr"].sum(), 1e-9)
        bullets.append(
            f"{top.capitalize()} led attributed revenue with {attr_share:.0%} share on the most recent day."
        )

    # WoW change
    recent_week = df_daily_by_channel[df_daily_by_channel["date"] >= last_date - pd.Timedelta(days=6)]
    prev_week = df_daily_by_channel[
        (df_daily_by_channel["date"] >= last_date - pd.Timedelta(days=13))
        & (df_daily_by_channel["date"] <= last_date - pd.Timedelta(days=7))
    ]
    def _kpi(df: pd.DataFrame) -> float:
        return float(df["attributed_revenue"].sum())

    cur = _kpi(recent_week)
    prev = _kpi(prev_week)
    if prev > 0:
        delta = (cur - prev) / prev
        bullets.append(f"Attributed revenue changed {delta:+.0%} WoW.")

    return bullets


def campaign_leaders(df_campaigns: pd.DataFrame, top_n: int = 5) -> List[str]:
    if df_campaigns.empty:
        return ["No campaign performance data available."]
    top = df_campaigns.sort_values(["attributed_revenue"], ascending=False).head(top_n)
    out = [
        f"{r.channel.capitalize()} · {r.campaign}: ROAS {r.roas:.2f}, Spend ${r.spend:,.0f}, Attrib Rev ${r.attributed_revenue:,.0f}"
        for r in top.itertuples()
    ]
    return out

