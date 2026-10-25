# Credit VaR for one corporate book

Expected loss, the one-factor ASRF unexpected-loss charge, and a Monte Carlo 99.9% credit VaR on the same 50 names.

The point of the repo is the gap between those last two numbers once one name is a quarter of the book. ASRF assumes an infinitely granular portfolio. The simulation does not.

PDs are assigned by rating. They are not estimated from defaults. LGD is 45%. The horizon is one year, so the IRB maturity adjustment is 1 and is left out. This is not a rating model and not an IFRS 9 calculator.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
python3 run.py
```

`pytest` checks the formulas. `run.py` writes `results/results.json`.

## The book

50 corporates, total EAD 100.

| Rating | Names | PD |
|---|---:|---:|
| BBB | 20 | 0.20% |
| BB | 20 | 1.00% |
| B | 10 | 4.00% |

The granular book gives every name EAD 2. The concentrated book gives the last B-rated name EAD 25 and splits the remaining 75 across the other 49.

Expected loss is the sum of PD × LGD × EAD.

## ASRF

The Basel IRB unexpected-loss rate on a name is

K = LGD × (Φ((Φ⁻¹(PD) + √ρ Φ⁻¹(0.999)) / √(1−ρ)) − PD)

with the corporate correlation

ρ(PD) = 0.12 w + 0.24 (1−w),   w = (1 − e^(−50 PD)) / (1 − e^(−50))

Capital on the book is the sum of K × EAD. That formula is the infinitely granular one-factor model. It does not see that one name is 25 of the 100.

## Monte Carlo

One systematic factor Y and an idiosyncratic shock per name. Name i defaults when

√ρᵢ Y + √(1−ρᵢ) εᵢ < Φ⁻¹(PDᵢ)

Loss on a path is the sum of LGD × EAD over the names that default. 200,000 paths, seed 7. Credit VaR is the 99.9% quantile of that loss. Unexpected loss is Credit VaR minus the sample mean.

| | EL | ASRF capital | MC 99.9% |
|---|---:|---:|---:|
| Equal EAD | 0.58 | 5.25 | 7.2 |
| One name at 25 | 0.86 | 6.30 | 14.7 |

Default of the large name alone is 11.25. That is already above the granular ASRF charge of 5.25. The ASRF number only moves from 5.25 to 6.30. The Monte Carlo 99.9% more than doubles, from 7.2 to 14.7.

Raising every asset correlation by half takes the concentrated 99.9% to 16.8. Doubling every PD, and leaving correlation at the unstressed IRB value, takes expected loss to 1.72 and the 99.9% to 17.4.

Fifty names is not an infinite book, so even the equal-weight Monte Carlo (7.2) sits above ASRF (5.25). The large gap is the concentrated book.

## Files

```
asrf.py               IRB correlation and the ASRF rate
book.py               names, EAD, expected loss
simulate.py           one-factor defaults and credit VaR
run.py                print the comparison
tests/test_engine.py
```
