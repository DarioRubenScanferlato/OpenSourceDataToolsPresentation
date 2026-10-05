"""Sensor telemetry stream generation: panel strings, inverters, batteries."""

from __future__ import annotations

import numpy as np
import pandas as pd

from solar_data_gen import physics


def _fault_mask(
    times: pd.DatetimeIndex,
    rng: np.random.Generator,
    *,
    n_episodes_per_month: float = 0.3,
    max_hours: int = 6,
) -> np.ndarray:
    """Boolean mask marking short fault episodes (string outage, comms drop, ...)."""
    mask = np.zeros(len(times), dtype=bool)
    if len(times) < 2:
        return mask
    n_days = max((times[-1] - times[0]).days, 1)
    n_episodes = rng.poisson(n_episodes_per_month * n_days / 30.0)
    if n_episodes == 0:
        return mask
    step_minutes = (times[1] - times[0]).total_seconds() / 60.0
    steps_per_hour = max(1, round(60.0 / step_minutes))
    for _ in range(n_episodes):
        start = int(rng.integers(0, len(times)))
        duration = int(rng.integers(1, max_hours + 1)) * steps_per_hour
        mask[start : start + duration] = True
    return mask


def inject_reading_faults(
    telemetry: pd.DataFrame,
    column: str,
    rng: np.random.Generator,
    *,
    stuck_episodes_per_month: float = 0.25,
    dropout_episodes_per_month: float = 0.4,
    max_stuck_hours: int = 36,
    max_dropout_hours: int = 12,
) -> pd.DataFrame:
    """Corrupt a telemetry reading column the way real sensors fail.

    Unlike `_fault_mask` (real outages: the equipment actually stops), these
    are *measurement* faults - the plant keeps producing, but the reading is
    wrong: a stuck sensor repeats the value it froze on (a flatline), and a
    dropout reports nothing at all (NaN). Stuck episodes start in daylight,
    so the frozen value isn't just a plausible night-time zero.
    """
    out = telemetry.copy()
    values = out[column].to_numpy(dtype=float).copy()
    for _, idx in out.groupby("sensor_id").indices.items():
        idx = np.sort(idx)
        times = pd.DatetimeIndex(out["timestamp"].to_numpy()[idx])
        if len(times) < 2:
            continue
        n_days = max((times[-1] - times[0]).days, 1)
        step_h = (times[1] - times[0]).total_seconds() / 3600.0
        daylight = np.flatnonzero(values[idx] > 0)
        for _ in range(rng.poisson(stuck_episodes_per_month * n_days / 30.0)):
            if len(daylight) == 0:
                break
            start = int(rng.choice(daylight))
            length = max(1, round(rng.integers(3, max_stuck_hours + 1) / step_h))
            values[idx[start : start + length]] = values[idx[start]]
        for _ in range(rng.poisson(dropout_episodes_per_month * n_days / 30.0)):
            start = int(rng.integers(0, len(idx)))
            length = max(1, round(rng.integers(1, max_dropout_hours + 1) / step_h))
            values[idx[start : start + length]] = np.nan
    out[column] = values
    return out


def generate_panel_telemetry(
    sensor: pd.Series,
    times: pd.DatetimeIndex,
    geometry: pd.DataFrame,
    irradiance: pd.DataFrame,
    ambient_temp_c: pd.Series,
    rng: np.random.Generator,
) -> pd.DataFrame:
    poa = physics.poa_irradiance(
        geometry, irradiance, tilt_deg=sensor["tilt_deg"], azimuth_deg=sensor["azimuth_deg"]
    )
    cell_temp = physics.cell_temperature(poa, ambient_temp_c)
    electrical = physics.panel_dc_output(
        poa,
        cell_temp,
        rated_power_w=sensor["nameplate_capacity"],
        rated_voltage_v=sensor["rated_voltage_v"],
    )

    # Small per-tick measurement noise so identical panels don't read identically.
    noise = rng.normal(1.0, 0.015, size=len(times))
    electrical["dc_power_w"] = (electrical["dc_power_w"] * noise).clip(lower=0.0)
    electrical["dc_current_a"] = (electrical["dc_current_a"] * noise).clip(lower=0.0)

    fault = _fault_mask(times, rng)
    electrical.loc[fault, ["dc_voltage_v", "dc_current_a", "dc_power_w"]] = 0.0

    electrical = electrical.round(
        {
            "poa_irradiance_wm2": 2,
            "cell_temperature_c": 2,
            "dc_voltage_v": 2,
            "dc_current_a": 3,
            "dc_power_w": 2,
        }
    )
    electrical.insert(0, "timestamp", times)
    electrical.insert(0, "plant_id", sensor["plant_id"])
    electrical.insert(0, "sensor_id", sensor["sensor_id"])
    electrical["is_fault"] = fault
    return electrical


def generate_inverter_telemetry(
    inverter: pd.Series,
    assigned_panel_telemetry: pd.DataFrame,
    times: pd.DatetimeIndex,
    rng: np.random.Generator,
    *,
    efficiency: float = 0.97,
) -> pd.DataFrame:
    dc_input_w = (
        assigned_panel_telemetry.groupby("timestamp")["dc_power_w"]
        .sum()
        .reindex(times, fill_value=0.0)
        .to_numpy()
    )
    noise = rng.normal(1.0, 0.01, size=len(times))
    capacity_w = inverter["nameplate_capacity"] * 1000.0
    ac_power_w = np.clip(dc_input_w * efficiency * noise, 0.0, capacity_w)
    # The meter reading itself is noisy too, even when the inverter is
    # clipping at its ceiling - so real output never repeats bit-for-bit
    # hour after hour (only a stuck sensor does, see inject_reading_faults).
    ac_power_w = ac_power_w * rng.normal(1.0, 0.002, size=len(times))

    fault = _fault_mask(times, rng, n_episodes_per_month=0.15, max_hours=3)
    ac_power_w = np.where(fault, 0.0, ac_power_w)
    status = np.where(fault, "fault", "online")
    temperature_c = (
        25.0 + 15.0 * (ac_power_w / max(capacity_w, 1.0)) + rng.normal(0.0, 1.0, size=len(times))
    )

    return pd.DataFrame(
        {
            "sensor_id": inverter["sensor_id"],
            "plant_id": inverter["plant_id"],
            "timestamp": times,
            "dc_input_kw": np.round(dc_input_w / 1000.0, 3),
            "ac_power_kw": np.round(ac_power_w / 1000.0, 3),
            "temperature_c": np.round(temperature_c, 2),
            "status": status,
            "is_fault": fault,
        }
    )


def generate_battery_telemetry(
    battery: pd.Series,
    plant_dc_power_w: pd.Series,
    times: pd.DatetimeIndex,
    rng: np.random.Generator,
    *,
    interval_minutes: float,
) -> pd.DataFrame:
    capacity_kwh = battery["nameplate_capacity"]
    charge_rate_pct = 100.0 * (interval_minutes / 60.0) * 0.15  # ~15% capacity/hour charge
    discharge_rate_pct = 100.0 * (interval_minutes / 60.0) * 0.08  # ~8% capacity/hour discharge

    generating = plant_dc_power_w.reindex(times, fill_value=0.0).to_numpy() > 0.0
    soc = np.empty(len(times))
    soc[0] = rng.uniform(40.0, 60.0)
    for i in range(1, len(times)):
        delta = charge_rate_pct if generating[i] else -discharge_rate_pct
        soc[i] = np.clip(soc[i - 1] + delta, 0.0, 100.0)

    charge_power_kw = np.where(generating, capacity_kwh * 0.15, 0.0)
    discharge_power_kw = np.where(~generating, capacity_kwh * 0.08, 0.0)

    return pd.DataFrame(
        {
            "sensor_id": battery["sensor_id"],
            "plant_id": battery["plant_id"],
            "timestamp": times,
            "state_of_charge_pct": np.round(soc, 2),
            "charge_power_kw": np.round(charge_power_kw, 2),
            "discharge_power_kw": np.round(discharge_power_kw, 2),
            "status": "online",
        }
    )
