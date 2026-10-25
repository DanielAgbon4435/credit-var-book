import json
from pathlib import Path

from book import (
    asrf_capital,
    concentrated_ead,
    expected_loss,
    granular_ead,
    large_name_default_loss,
)
from simulate import credit_var, default_indicators, portfolio_loss


def report(ead, defaults):
    mc = credit_var(portfolio_loss(ead, defaults))
    return {
        "el_closed": expected_loss(ead),
        "asrf": asrf_capital(ead),
        "mc_el": mc["el"],
        "mc_var": mc["var"],
        "mc_ul": mc["ul"],
        "n_paths": mc["n_paths"],
    }


def main():
    defaults = default_indicators()
    stressed_rho = default_indicators(rho_scale=1.5)
    stressed_pd = default_indicators(pd_scale=2.0)

    ead_g = granular_ead()
    ead_c = concentrated_ead()
    granular = report(ead_g, defaults)
    concentrated = report(ead_c, defaults)
    rho_stress = credit_var(portfolio_loss(ead_c, stressed_rho))
    pd_stress = credit_var(portfolio_loss(ead_c, stressed_pd))

    payload = {
        "granular": granular,
        "concentrated": concentrated,
        "concentrated_rho_x1_5": {
            "mc_el": rho_stress["el"],
            "mc_var": rho_stress["var"],
        },
        "concentrated_pd_x2": {
            "mc_el": pd_stress["el"],
            "mc_var": pd_stress["var"],
        },
        "large_name_default": large_name_default_loss(),
    }

    print("names: 50   EAD: 100   LGD: 45%   horizon: 1 year")
    print(
        f"granular    EL {granular['el_closed']:.3f}  "
        f"ASRF {granular['asrf']:.2f}  "
        f"MC 99.9% {granular['mc_var']:.1f}"
    )
    print(
        f"concentrated EL {concentrated['el_closed']:.3f}  "
        f"ASRF {concentrated['asrf']:.2f}  "
        f"MC 99.9% {concentrated['mc_var']:.1f}"
    )
    print(f"large-name default: {payload['large_name_default']:.2f}")
    print(f"1.5x correlation, concentrated 99.9%: {rho_stress['var']:.1f}")
    print(
        f"2x PD, concentrated EL {pd_stress['el']:.2f}  "
        f"99.9% {pd_stress['var']:.1f}"
    )

    Path("results").mkdir(exist_ok=True)
    Path("results/results.json").write_text(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
