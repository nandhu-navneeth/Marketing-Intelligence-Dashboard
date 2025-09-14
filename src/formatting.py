from __future__ import annotations

def _compact(num: float) -> tuple[float, str]:
    n = float(num or 0.0)
    for unit, div in [("T", 1e12), ("B", 1e9), ("M", 1e6), ("K", 1e3)]:
        if abs(n) >= div:
            return n / div, unit
    return n, ""


def fmt_currency_compact(value: float, decimals: int = 1) -> str:
    n, unit = _compact(value)
    if unit:
        return f"${n:.{decimals}f}{unit}"
    return f"${n:,.0f}"


def fmt_int_compact(value: float, decimals: int = 0) -> str:
    n, unit = _compact(value)
    if unit:
        return f"{n:.{decimals}f}{unit}"
    return f"{int(round(n)):,}"


def fmt_ratio(value: float, decimals: int = 2) -> str:
    return f"{float(value or 0.0):.{decimals}f}x"

