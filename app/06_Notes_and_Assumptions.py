from __future__ import annotations

import streamlit as st
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

st.set_page_config(page_title="Notes & Assumptions", layout="wide")
st.title("Notes & Assumptions")

st.subheader("Data Dictionary")
st.markdown(
    """
    - date: daily date (UTC naive)
    - channel: marketing channel (facebook|google|tiktok)
    - tactic: e.g., prospecting, retargeting (string)
    - state: region/state if available
    - campaign: campaign name
    - impressions, clicks, spend: delivery metrics
    - attributed_revenue: platform-attributed revenue
    - orders, new_orders, new_customers, total_revenue, gross_profit, cogs: business KPIs
    """
)

st.subheader("Metric Definitions")
st.markdown(
    """
    - CTR = clicks / impressions
    - CPC = spend / clicks
    - CPM = spend * 1000 / impressions
    - ROAS = attributed_revenue / spend
    - Blended ROAS = sum(attributed_revenue) / sum(spend)
    - AOV = total_revenue / orders
    - Gross Margin % = gross_profit / total_revenue
    - COGS % = COGS / total_revenue
    - New Customer Rate = new_customers / orders
    """
)

st.subheader("Quality Flags & Validation")
st.markdown(
    """
    - Rows flagged when impressions == 0 and clicks > 0
    - Negative impressions or spend dropped
    - Date continuity checked (gaps reported)
    - Gross Profit reconciled to Total Revenue - COGS within tolerance
    """
)

st.subheader("Caveats")
st.markdown(
    """
    - Platform attributed_revenue may differ from total_revenue. Use for directional insights and ROAS, not GAAP.
    - Cohort/retention views are proxies due to limited customer-level data.
    - Upload .zip with the required CSVs or place them in the `data/` folder.
    """
)
