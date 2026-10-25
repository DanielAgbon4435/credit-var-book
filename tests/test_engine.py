import math

import pytest
from scipy.stats import norm

from asrf import asrf_capital_rate, asset_correlation
from book import (
    LGD,
    PDS,
    asrf_capital,
    concentrated_ead,
    expected_loss,
    granular_ead,
    large_name_default_loss,
)
from simulate import credit_var, default_indicators, portfolio_loss


def test_irb_correlation_falls_as_pd_rises():
    low_pd_rho = asset_correlation(0.002)
    high_pd_rho = asset_correlation(0.04)
    assert low_pd_rho == pytest.approx(0.2286, abs=1e-4)
    assert high_pd_rho < low_pd_rho


def test_asrf_rate_matches_the_hand_formula():
    pd = 0.002
    lgd = 0.45
    rho = asset_correlation(pd)
    x = (norm.ppf(pd) + math.sqrt(rho) * norm.ppf(0.999)) / math.sqrt(1 - rho)
    assert asrf_capital_rate(pd, lgd) == pytest.approx(lgd * (float(norm.cdf(x)) - pd))


def test_expected_loss_is_sum_of_pd_lgd_ead():
    ead = granular_ead()
    closed = sum(pd * LGD * x for pd, x in zip(PDS, ead))
    assert expected_loss(ead) == pytest.approx(closed)
    assert expected_loss(ead) == pytest.approx(0.576)


def test_asrf_barely_moves_when_one_name_is_large():
    granular = asrf_capital(granular_ead())
    concentrated = asrf_capital(concentrated_ead())
    assert concentrated > granular
    assert concentrated - granular < 1.2


def test_monte_carlo_el_matches_the_closed_form():
    defaults = default_indicators(n_paths=80_000, seed=3)
    sample_el = portfolio_loss(granular_ead(), defaults).mean()
    assert sample_el == pytest.approx(expected_loss(granular_ead()), rel=0.05)


def test_concentration_lifts_monte_carlo_var():
    defaults = default_indicators(n_paths=80_000, seed=3)
    granular = credit_var(portfolio_loss(granular_ead(), defaults))
    concentrated = credit_var(portfolio_loss(concentrated_ead(), defaults))
    assert concentrated["var"] > granular["var"]
    assert concentrated["var"] > large_name_default_loss()


def test_large_name_default_is_lgd_times_twenty_five():
    assert large_name_default_loss() == pytest.approx(11.25)


def test_doubling_pd_nearly_doubles_expected_loss():
    base = default_indicators(n_paths=80_000, seed=3)
    stressed = default_indicators(n_paths=80_000, seed=3, pd_scale=2.0)
    ead = concentrated_ead()
    assert portfolio_loss(ead, stressed).mean() == pytest.approx(
        2.0 * portfolio_loss(ead, base).mean(), rel=0.08
    )
