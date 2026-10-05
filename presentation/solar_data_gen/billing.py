"""Daily energy billing / grid settlement dataset."""

from __future__ import annotations

import numpy as np
import pandas as pd


def build_energy_billing(
    inverter_telemetry: pd.DataFrame, plants: pd.DataFrame, interval_minutes: int, seed: int
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 3)
    interval_hours = interval_minutes / 60.0

    daily = (
        inverter_telemetry.assign(billing_date=inverter_telemetry["timestamp"].dt.date)
        .groupby(["plant_id", "billing_date"])["ac_power_kw"]
        .sum()
        .mul(interval_hours)
        .rename("energy_generated_kwh")
        .reset_index()
    )

    n = len(daily)
    self_consumption_pct = rng.uniform(0.03, 0.12, size=n)
    curtailment_pct = np.where(rng.random(n) < 0.05, rng.uniform(0.02, 0.15, size=n), 0.0)
    # Each plant sells into its own market at its own base price, which
    # swings with the season - dearer in the local winter, when demand is
    # higher and solar supply lower - plus day-to-day market noise.
    base_price = dict(zip(plants["plant_id"], rng.uniform(0.08, 0.12, size=len(plants))))
    southern = dict(zip(plants["plant_id"], plants["latitude"] < 0))
    doy = pd.to_datetime(daily["billing_date"]).dt.dayofyear.to_numpy()
    winter_peak = np.where(daily["plant_id"].map(southern).to_numpy(), 196, 15)  # mid-Jul / mid-Jan
    seasonal = 1.0 + 0.18 * np.cos(2 * np.pi * (doy - winter_peak) / 365.0)
    tariff = daily["plant_id"].map(base_price).to_numpy() * seasonal * rng.normal(1.0, 0.06, size=n)
    tariff = np.clip(tariff, 0.03, None)

    generated = daily["energy_generated_kwh"].to_numpy()
    self_consumption_kwh = generated * self_consumption_pct
    curtailment_kwh = generated * curtailment_pct
    exported_kwh = np.clip(generated - self_consumption_kwh - curtailment_kwh, 0.0, None)

    daily["energy_generated_kwh"] = np.round(generated, 2)
    daily["self_consumption_kwh"] = np.round(self_consumption_kwh, 2)
    daily["curtailment_kwh"] = np.round(curtailment_kwh, 2)
    daily["energy_exported_kwh"] = np.round(exported_kwh, 2)
    daily["tariff_eur_per_kwh"] = np.round(tariff, 4)
    daily["revenue_eur"] = np.round(exported_kwh * tariff, 2)
    return daily
