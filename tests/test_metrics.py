from __future__ import annotations

from src.metrics import safe_div, ctr, cpc, cpm, roas, blended_roas, aov, gross_margin_pct, cogs_pct, new_customer_rate, share, pareto_cumulative_shares


def test_safe_div_zero():
    assert safe_div(10, 0) == 0.0
    assert safe_div(0, 10) == 0.0


def test_ctr():
    assert ctr(50, 1000) == 0.05
    assert ctr(0, 0) == 0.0


def test_cpc():
    assert cpc(100, 10) == 10.0
    assert cpc(100, 0) == 0.0


def test_cpm():
    assert cpm(100, 10000) == 10.0
    assert cpm(100, 0) == 0.0


def test_roas_and_blended():
    assert roas(200, 100) == 2.0
    assert blended_roas(0, 0) == 0.0


def test_aov_and_margin():
    assert aov(1000, 10) == 100.0
    assert gross_margin_pct(400, 800) == 0.5
    assert cogs_pct(400, 800) == 0.5


def test_new_customer_rate_and_share():
    assert new_customer_rate(20, 100) == 0.2
    assert share(2, 10) == 0.2


def test_pareto():
    vals = [50, 30, 20]
    cum = pareto_cumulative_shares(vals)
    assert cum[-1] == 1.0
    assert cum[0] == 0.5
