"""Daily plant cost accruals: operating costs, depreciation and interest.

Costs are accrued per plant per billing day, so they can be filtered and
summed over any date range alongside the billing (revenue) data. Rates are
drawn once per plant from typical utility-scale solar ranges; fixed costs
scale with AC capacity, grid fees with exported energy. Corrective repairs
are not included here - they already live in the maintenance work orders.
Income tax is left to consumers, since it depends on the profit over
whatever period they report on.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

#: (category, cost_type, EUR per kW of AC capacity per year) - accrued evenly
_FIXED_COSTS = [
    ("O&M contract", "opex", (11.0, 15.0)),
    ("Land lease", "opex", (4.0, 8.0)),
    ("Insurance", "opex", (2.0, 4.0)),
    ("Asset management", "opex", (2.0, 3.5)),
]
_GRID_FEE_EUR_PER_MWH = (3.0, 6.0)  # network / balancing fees on exported energy
_CAPEX_EUR_PER_KW = (550.0, 750.0)
_LIFETIME_YEARS = 25  # straight-line depreciation
_DEBT_SHARE = 0.7  # share of capex financed with debt
_INTEREST_RATE = (0.04, 0.06)

_COLUMNS = ["cost_date", "plant_id", "category", "cost_type", "amount_eur"]


def build_plant_costs(plants: pd.DataFrame, billing: pd.DataFrame, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 7)
    frames = []

    for _, plant in plants.iterrows():
        capacity_kw = plant["capacity_mw"] * 1000.0
        days = billing.loc[billing["plant_id"] == plant["plant_id"]].sort_values("billing_date")
        n = len(days)
        if n == 0:
            continue

        def daily(annual_eur: float, *, jitter: float = 0.03) -> np.ndarray:
            # small day-to-day variation so the accruals don't look flat
            return annual_eur / 365.0 * rng.uniform(1 - jitter, 1 + jitter, size=n)

        capex = capacity_kw * rng.uniform(*_CAPEX_EUR_PER_KW)
        amounts = {
            (category, cost_type): daily(capacity_kw * rng.uniform(*rate))
            for category, cost_type, rate in _FIXED_COSTS
        }
        amounts[("Grid fees", "opex")] = (
            days["energy_exported_kwh"].to_numpy() / 1000.0 * rng.uniform(*_GRID_FEE_EUR_PER_MWH)
        )
        amounts[("Depreciation", "depreciation")] = daily(capex / _LIFETIME_YEARS, jitter=0.0)
        amounts[("Interest", "financing")] = daily(
            capex * _DEBT_SHARE * rng.uniform(*_INTEREST_RATE), jitter=0.0
        )

        for (category, cost_type), values in amounts.items():
            frames.append(
                pd.DataFrame(
                    {
                        "cost_date": days["billing_date"].to_numpy(),
                        "plant_id": plant["plant_id"],
                        "category": category,
                        "cost_type": cost_type,
                        "amount_eur": np.round(values, 2),
                    }
                )
            )

    if not frames:
        return pd.DataFrame(columns=_COLUMNS)
    return pd.concat(frames, ignore_index=True)[_COLUMNS]
