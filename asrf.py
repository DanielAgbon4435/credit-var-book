import math

from scipy.stats import norm


def asset_correlation(pd):
    if not 0.0 < pd < 1.0:
        raise ValueError("PD must be between 0 and 1")
    weight = (1.0 - math.exp(-50.0 * pd)) / (1.0 - math.exp(-50.0))
    return 0.12 * weight + 0.24 * (1.0 - weight)


def asrf_capital_rate(pd, lgd, quantile=0.999):
    if not 0.0 < lgd <= 1.0:
        raise ValueError("LGD must be in (0, 1]")
    if not 0.5 < quantile < 1.0:
        raise ValueError("quantile must be in (0.5, 1)")
    rho = asset_correlation(pd)
    x = (norm.ppf(pd) + math.sqrt(rho) * norm.ppf(quantile)) / math.sqrt(1.0 - rho)
    return lgd * (float(norm.cdf(x)) - pd)
