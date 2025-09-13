from __future__ import annotations

from typing import Optional


def safe_div(numerator: float, denominator: float) -> float:
    """Return numerator/denominator with zero-division guard.

    If denominator is 0 or None, returns 0.0.
    """
    try:
        if denominator in (0, None):
            return 0.0
        return float(numerator) / float(denominator)
    except Exception:
        return 0.0


def ctr(clicks: Optional[float], impressions: Optional[float]) -> float:
    """Click-through rate = clicks / impressions.

    Returns 0.0 if impressions is 0/None.
    """
    return safe_div(clicks or 0.0, impressions or 0.0)


def cpc(spend: Optional[float], clicks: Optional[float]) -> float:
    """Cost per click = spend / clicks.

    Returns 0.0 if clicks is 0/None.
    """
    return safe_div(spend or 0.0, clicks or 0.0)


def cpm(spend: Optional[float], impressions: Optional[float]) -> float:
    """Cost per mille = spend * 1000 / impressions.

    Returns 0.0 if impressions is 0/None.
    """
    return safe_div((spend or 0.0) * 1000.0, impressions or 0.0)


def roas(attributed_revenue: Optional[float], spend: Optional[float]) -> float:
    """Return on ad spend = attributed_revenue / spend.

    Returns 0.0 if spend is 0/None.
    """
    return safe_div(attributed_revenue or 0.0, spend or 0.0)


def blended_roas(total_attrib_revenue: float, total_spend: float) -> float:
    """Blended ROAS across channels for a period.

    Parameters
    ----------
    total_attrib_revenue: float
        Sum of attributed revenue across selected scope.
    total_spend: float
        Sum of spend across selected scope.
    """
    return roas(total_attrib_revenue, total_spend)


def aov(total_revenue: Optional[float], orders: Optional[float]) -> float:
    """Average order value = total_revenue / orders.

    Returns 0.0 if orders is 0/None.
    """
    return safe_div(total_revenue or 0.0, orders or 0.0)


def gross_margin_pct(gross_profit: Optional[float], total_revenue: Optional[float]) -> float:
    """Gross margin % = gross_profit / total_revenue.

    Returns 0.0 if total_revenue is 0/None.
    """
    return safe_div(gross_profit or 0.0, total_revenue or 0.0)


def cogs_pct(cogs: Optional[float], total_revenue: Optional[float]) -> float:
    """COGS % = COGS / total_revenue.

    Returns 0.0 if total_revenue is 0/None.
    """
    return safe_div(cogs or 0.0, total_revenue or 0.0)


def new_customer_rate(new_customers: Optional[float], orders: Optional[float]) -> float:
    """New customer rate = new_customers / orders.

    Returns 0.0 if orders is 0/None.
    """
    return safe_div(new_customers or 0.0, orders or 0.0)


def share(part: Optional[float], total: Optional[float]) -> float:
    """Generic share metric = part / total with guard.
    Returns 0.0 if total is 0/None.
    """
    return safe_div(part or 0.0, total or 0.0)


def pareto_cumulative_shares(values_sorted_desc: list[float]) -> list[float]:
    """Return cumulative share sequence for Pareto chart (descending values).

    Parameters
    ----------
    values_sorted_desc: list[float]
        Values sorted in descending order.

    Returns
    -------
    list[float]
        Cumulative shares in [0, 1]. Returns empty list if no positive total.
    """
    total = float(sum(v for v in values_sorted_desc if v is not None))
    if total <= 0.0:
        return []
    cum = 0.0
    out: list[float] = []
    for v in values_sorted_desc:
        cum += float(v or 0.0)
        out.append(min(1.0, max(0.0, cum / total)))
    return out

