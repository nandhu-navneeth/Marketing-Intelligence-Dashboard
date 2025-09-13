from __future__ import annotations

from typing import Final

CHANNELS: Final = ["facebook", "google", "tiktok"]

# Expected file names in data dir or zip (case-insensitive match)
EXPECTED_FILES: Final = {
    "facebook": "facebook.csv",
    "google": "google.csv",
    "tiktok": "tiktok.csv",
    "business": "business.csv",
}

# Standard column names
AD_COLS: Final = [
    "date",
    "tactic",
    "state",
    "campaign",
    "impressions",
    "clicks",
    "spend",
    "attributed_revenue",
]

BUSINESS_COLS: Final = [
    "date",
    "orders",
    "new_orders",
    "new_customers",
    "total_revenue",
    "gross_profit",
    "cogs",
]

RENAMES_GENERIC: Final = {
    # common variants to standardize
    "impression": "impressions",
    "impr": "impressions",
    "click": "clicks",
    "spend_usd": "spend",
    "rev": "attributed_revenue",
    "revenue": "attributed_revenue",
    "cogs_amount": "cogs",
}

DTYPE_ADS: Final = {
    "date": "datetime64[ns]",
    "tactic": "string",
    "state": "string",
    "campaign": "string",
    "impressions": "Int64",
    "clicks": "Int64",
    "spend": "float64",
    "attributed_revenue": "float64",
}

DTYPE_BUSINESS: Final = {
    "date": "datetime64[ns]",
    "orders": "Int64",
    "new_orders": "Int64",
    "new_customers": "Int64",
    "total_revenue": "float64",
    "gross_profit": "float64",
    "cogs": "float64",
}

QUALITY_FLAGS_COL: Final = "quality_flag"
