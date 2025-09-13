from __future__ import annotations

import pandas as pd
from src.validate import validate_frames


def test_validate_basic():
    ads = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "tactic": ["p", "p"],
            "state": ["CA", "CA"],
            "campaign": ["A", "A"],
            "impressions": [1000, 1200],
            "clicks": [50, 60],
            "spend": [100.0, 120.0],
            "attributed_revenue": [150.0, 160.0],
        }
    )
    biz = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "orders": [10, 12],
            "new_orders": [6, 7],
            "new_customers": [5, 6],
            "total_revenue": [800.0, 900.0],
            "gross_profit": [400.0, 450.0],
            "cogs": [400.0, 450.0],
        }
    )
    warns = validate_frames({"facebook": ads, "business": biz})
    assert isinstance(warns, list)

