from __future__ import annotations

import pandas as pd
from src.transform import transform_inputs


def test_transform_shapes():
    ads = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-01", "2024-01-02"]),
            "tactic": ["p", "p", "p"],
            "state": ["CA", "CA", "CA"],
            "campaign": ["A", "B", "A"],
            "impressions": [1000, 2000, 1500],
            "clicks": [50, 60, 55],
            "spend": [100.0, 120.0, 110.0],
            "attributed_revenue": [150.0, 140.0, 160.0],
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
    dfs = {"facebook": ads, "business": biz}
    td = transform_inputs(dfs)
    # daily_by_channel should have 2 rows
    assert set(td.df_daily_by_channel["date"]) == set(pd.to_datetime(["2024-01-01", "2024-01-02"]))
    # blended should include business columns
    for col in ["orders", "total_revenue", "gross_profit", "cogs"]:
        assert col in td.df_daily_blended.columns

