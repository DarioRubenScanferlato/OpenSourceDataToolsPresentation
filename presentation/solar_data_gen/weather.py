"""Plant-level weather observations."""

from __future__ import annotations

import numpy as np
import pandas as pd

from solar_data_gen import physics


def seasonal_ambient_temp_c(
    times: pd.DatetimeIndex, latitude: float, rng: np.random.Generator
) -> pd.Series:
    """Ambient temperature combining a yearly seasonal cycle, a diurnal cycle, and noise."""
    doy = times.dayofyear.to_numpy()
    sign = 1.0 if latitude >= 0 else -1.0
    seasonal = 10.0 * np.cos(2 * np.pi * (doy - 200) / 365.0 * sign)
    diurnal = 5.0 * np.cos(2 * np.pi * (times.hour.to_numpy() - 15) / 24.0)
    noise = rng.normal(0.0, 1.5, size=len(times))
    return pd.Series(15.0 + seasonal + diurnal + noise, index=times)


def build_weather(
    plant_id: str,
    latitude: float,
    longitude: float,
    times: pd.DatetimeIndex,
    rng: np.random.Generator,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series]:
    """Build one plant's weather observations.

    Returns (observations, geometry, irradiance, ambient_temp_c) — geometry
    and irradiance are handed back so panel telemetry generation can reuse
    them instead of recomputing solar position per sensor.
    """
    geometry = physics.solar_geometry(latitude, longitude, times)
    cloud_cover = physics.cloud_cover_series(times, rng)
    irradiance = physics.cloudy_irradiance(geometry, cloud_cover)
    ambient_temp = seasonal_ambient_temp_c(times, latitude, rng)

    wind_speed = np.clip(rng.weibull(2.0, size=len(times)) * 4.0, 0.0, None)
    is_rainy = (cloud_cover.to_numpy() > 0.7) & (rng.random(len(times)) < 0.3)
    precipitation = np.where(is_rainy, rng.exponential(2.0, size=len(times)), 0.0)

    observations = pd.DataFrame(
        {
            "plant_id": plant_id,
            "timestamp": times,
            "ghi_wm2": np.round(irradiance["ghi"].to_numpy(), 2),
            "dni_wm2": np.round(irradiance["dni"].to_numpy(), 2),
            "dhi_wm2": np.round(irradiance["dhi"].to_numpy(), 2),
            "ambient_temp_c": np.round(ambient_temp.to_numpy(), 2),
            "wind_speed_ms": np.round(wind_speed, 2),
            "cloud_cover_pct": np.round(cloud_cover.to_numpy() * 100, 1),
            "precipitation_mm": np.round(precipitation, 2),
        }
    )
    return observations, geometry, irradiance, ambient_temp
