"""Solar irradiance, thermal, and electrical models built on pvlib.

pvlib supplies the well-tested solar-position and clear-sky irradiance
physics. The pieces pvlib does not model — cloud cover, sensor noise, and
faults — are layered on top in this module and in `streams.py` so the
generated telemetry looks like real field data rather than a noiseless
clear-sky simulation.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pvlib

NOCT_C = 45.0
TEMP_DERATING_PER_C = 0.004  # fractional DC power loss per °C above 25°C (STC)
VOLTAGE_TEMP_COEFF_PER_C = -0.0032


def solar_geometry(
    latitude: float, longitude: float, times: pd.DatetimeIndex, altitude: float = 0.0
) -> pd.DataFrame:
    """Solar position and clear-sky irradiance for a location over `times`."""
    location = pvlib.location.Location(latitude, longitude, altitude=altitude, tz="UTC")
    solpos = location.get_solarposition(times)
    clearsky = location.get_clearsky(times, model="ineichen", solar_position=solpos)
    return pd.DataFrame(
        {
            "zenith": solpos["apparent_zenith"].to_numpy(),
            "azimuth": solpos["azimuth"].to_numpy(),
            "ghi_clear": clearsky["ghi"].to_numpy(),
            "dni_extra": pvlib.irradiance.get_extra_radiation(times).to_numpy(),
        },
        index=times,
    )


def cloud_cover_series(
    times: pd.DatetimeIndex, rng: np.random.Generator, *, persistence: float = 0.85
) -> pd.Series:
    """Autocorrelated cloud cover fraction in [0, 1] (0 = clear sky).

    Modeled as a day-scale AR(1) process so "weather systems" persist for
    hours or days, with gaussian intraday jitter layered on top for texture.
    """
    days = pd.date_range(times[0].normalize(), times[-1].normalize(), freq="D")
    daily = np.empty(len(days))
    daily[0] = rng.beta(1.5, 3.0)
    for i in range(1, len(daily)):
        shock = rng.beta(1.5, 3.0)
        daily[i] = np.clip(persistence * daily[i - 1] + (1 - persistence) * shock, 0.0, 1.0)
    base = pd.Series(daily, index=days).reindex(times.normalize()).to_numpy()
    jitter = rng.normal(0.0, 0.05, size=len(times))
    return pd.Series(np.clip(base + jitter, 0.0, 1.0), index=times)


def cloudy_irradiance(geometry: pd.DataFrame, cloud_cover: pd.Series) -> pd.DataFrame:
    """Attenuate clear-sky GHI by cloud cover and split into DNI/DHI (Erbs model)."""
    transmittance = 1.0 - 0.75 * cloud_cover.to_numpy() ** 1.5
    ghi = np.clip(geometry["ghi_clear"].to_numpy() * np.clip(transmittance, 0.05, 1.0), 0.0, None)
    erbs = pvlib.irradiance.erbs(ghi, geometry["zenith"].to_numpy(), geometry.index)
    return pd.DataFrame(
        {"ghi": ghi, "dni": erbs["dni"].to_numpy(), "dhi": erbs["dhi"].to_numpy()},
        index=geometry.index,
    )


def poa_irradiance(
    geometry: pd.DataFrame, irradiance: pd.DataFrame, *, tilt_deg: float, azimuth_deg: float
) -> pd.Series:
    """Plane-of-array irradiance (W/m^2) for a panel with the given tilt/azimuth."""
    total = pvlib.irradiance.get_total_irradiance(
        surface_tilt=tilt_deg,
        surface_azimuth=azimuth_deg,
        solar_zenith=geometry["zenith"],
        solar_azimuth=geometry["azimuth"],
        dni=irradiance["dni"],
        ghi=irradiance["ghi"],
        dhi=irradiance["dhi"],
        dni_extra=geometry["dni_extra"],
        model="isotropic",
    )
    return total["poa_global"].clip(lower=0.0)


def cell_temperature(poa_wm2: pd.Series, ambient_temp_c: pd.Series) -> pd.Series:
    """NOCT (Nominal Operating Cell Temperature) thermal model."""
    return ambient_temp_c + (NOCT_C - 20.0) / 800.0 * poa_wm2


def panel_dc_output(
    poa_wm2: pd.Series,
    cell_temp_c: pd.Series,
    *,
    rated_power_w: float,
    rated_voltage_v: float,
) -> pd.DataFrame:
    """DC voltage/current/power for a panel string, STC-normalized and temperature-derated."""
    derating = 1.0 - TEMP_DERATING_PER_C * (cell_temp_c - 25.0)
    power_w = (rated_power_w * (poa_wm2 / 1000.0) * derating).clip(lower=0.0)
    voltage_v = np.where(
        poa_wm2 > 1.0,
        rated_voltage_v * (1.0 + VOLTAGE_TEMP_COEFF_PER_C * (cell_temp_c - 25.0)),
        0.0,
    )
    current_a = np.where(voltage_v > 0, power_w / voltage_v, 0.0)
    return pd.DataFrame(
        {
            "poa_irradiance_wm2": poa_wm2,
            "cell_temperature_c": cell_temp_c,
            "dc_voltage_v": voltage_v,
            "dc_current_a": current_a,
            "dc_power_w": power_w,
        }
    )
