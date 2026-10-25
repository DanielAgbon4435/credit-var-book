import numpy as np
from scipy.stats import norm

from asrf import asset_correlation
from book import LGD, PDS


def default_indicators(n_paths=200_000, seed=7, rho_scale=1.0, pd_scale=1.0):
    base_pds = np.array(PDS)
    pds = np.minimum(base_pds * pd_scale, 0.99)
    rhos = np.array([asset_correlation(pd) for pd in base_pds])
    rhos = np.minimum(rhos * rho_scale, 0.99)

    rng = np.random.default_rng(seed)
    y = rng.standard_normal(n_paths)
    eps = rng.standard_normal((n_paths, len(PDS)))
    asset = np.sqrt(rhos) * y[:, None] + np.sqrt(1.0 - rhos) * eps
    return asset < norm.ppf(pds)


def portfolio_loss(ead, defaults, lgd=LGD):
    return (defaults * lgd * ead).sum(axis=1)


def credit_var(losses, quantile=0.999):
    losses = np.asarray(losses, dtype=float)
    if losses.ndim != 1 or losses.size < 100:
        raise ValueError("need a 1-d loss sample")
    var = float(np.quantile(losses, quantile, method="linear"))
    el = float(losses.mean())
    return {
        "el": el,
        "var": var,
        "ul": var - el,
        "quantile": quantile,
        "n_paths": int(losses.size),
    }
