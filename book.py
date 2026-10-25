import numpy as np

from asrf import asrf_capital_rate

LGD = 0.45
TOTAL_EAD = 100.0
LARGE_EAD = 25.0

PDS = [0.0020] * 20 + [0.0100] * 20 + [0.0400] * 10


def granular_ead():
    n = len(PDS)
    return np.full(n, TOTAL_EAD / n)


def concentrated_ead():
    n = len(PDS)
    ead = np.full(n, (TOTAL_EAD - LARGE_EAD) / (n - 1))
    ead[-1] = LARGE_EAD
    return ead


def expected_loss(ead, lgd=LGD):
    return float(np.sum(np.array(PDS) * lgd * ead))


def asrf_capital(ead, lgd=LGD, quantile=0.999):
    total = 0.0
    for pd, exposure in zip(PDS, ead):
        total += asrf_capital_rate(pd, lgd, quantile) * float(exposure)
    return total


def large_name_default_loss(lgd=LGD):
    return LARGE_EAD * lgd
