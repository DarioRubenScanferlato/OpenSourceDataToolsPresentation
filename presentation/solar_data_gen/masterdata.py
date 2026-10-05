"""Plant and sensor masterdata generation."""

from __future__ import annotations

import numpy as np
import pandas as pd
from faker import Faker

from solar_data_gen.config import GenerationConfig

_PANEL_MANUFACTURERS = [
    "JinkoSolar",
    "LONGi",
    "Trina Solar",
    "Canadian Solar",
    "JA Solar",
    "First Solar",
]
_INVERTER_MANUFACTURERS = ["SMA", "Huawei", "SolarEdge", "Sungrow", "Fronius"]
_BATTERY_MANUFACTURERS = ["Tesla", "BYD", "LG Energy Solution", "Fluence"]
_WEATHER_STATION_MANUFACTURERS = ["Vaisala", "Campbell Scientific", "Davis Instruments"]


def _random_land_location(fake: Faker) -> tuple[float, float, str, str, str]:
    """A random (latitude, longitude, place, country_code, timezone) on land.

    Falls back to a plausible mid-latitude location if the installed Faker
    version lacks the geo provider's `location_on_land`.
    """
    try:
        lat, lon, place, country_code, timezone = fake.location_on_land()
        return float(lat), float(lon), str(place), str(country_code), str(timezone)
    except AttributeError:
        return (
            float(fake.latitude()),
            float(fake.longitude()),
            fake.city(),
            fake.country_code(),
            "UTC",
        )


def build_plants(cfg: GenerationConfig) -> pd.DataFrame:
    fake = Faker()
    fake.seed_instance(cfg.seed)
    rng = np.random.default_rng(cfg.seed)
    start = pd.Timestamp(cfg.start_date)

    rows = []
    for i in range(cfg.n_plants):
        lat, lon, place, country_code, timezone = _random_land_location(fake)
        rows.append(
            {
                "plant_id": f"PLANT-{i + 1:03d}",
                "name": f"{place} Solar Farm",
                "country_code": country_code,
                "timezone": timezone,
                "latitude": round(lat, 5),
                "longitude": round(lon, 5),
                "altitude_m": round(float(rng.uniform(0, 500)), 1),
                "capacity_mw": round(float(rng.uniform(5.0, 80.0)), 1),
                # relative to the generated period, not to "today", so a
                # given seed always produces the same plants
                "commissioning_date": fake.date_between(
                    start_date=(start - pd.DateOffset(years=12)).date(),
                    end_date=(start - pd.Timedelta(days=30)).date(),
                ),
                "decommissioning_date": None,
                "grid_connection_id": f"GRID-{fake.bothify('??-#####').upper()}",
                "status": "operational",
            }
        )
    plants = pd.DataFrame(rows)
    _apply_lifecycle(plants, cfg)
    return plants


def _apply_lifecycle(plants: pd.DataFrame, cfg: GenerationConfig) -> None:
    """Open the last `n_new_plants` part-way through the period and close
    `n_decommissioned_plants` of the rest, in place.

    Uses its own RNG stream so the plants themselves (names, locations,
    capacities) come out the same whatever the lifecycle settings.
    """
    rng = np.random.default_rng(cfg.seed + 11)
    start, end = pd.Timestamp(cfg.start_date), pd.Timestamp(cfg.end_date)
    span_days = (end - start).days
    n = len(plants)
    n_new = min(cfg.n_new_plants, n)
    for i in range(n - n_new, n):
        # somewhere in the middle 80% of the period, so there's some data after
        offset = int(rng.uniform(0.1, 0.9) * span_days)
        plants.loc[i, "commissioning_date"] = (start + pd.Timedelta(days=offset)).date()

    existing = list(range(n - n_new))
    n_closed = min(cfg.n_decommissioned_plants, len(existing))
    for i in rng.choice(existing, size=n_closed, replace=False):
        # in the second half of the period
        offset = int(rng.uniform(0.5, 0.9) * span_days)
        plants.loc[i, "decommissioning_date"] = (start + pd.Timedelta(days=offset)).date()
        plants.loc[i, "status"] = "decommissioned"


def operating_mask(plant: pd.Series, times: pd.DatetimeIndex) -> np.ndarray:
    """True for the timestamps at which `plant` was operating."""
    mask = times >= pd.Timestamp(plant["commissioning_date"], tz=times.tz)
    if plant.get("decommissioning_date") is not None and not pd.isna(plant["decommissioning_date"]):
        mask &= times < pd.Timestamp(plant["decommissioning_date"], tz=times.tz)
    return np.asarray(mask)


def _sensor_row(
    *,
    sensor_id: str,
    plant_id: str,
    sensor_type: str,
    parent_sensor_id: str | None,
    manufacturer: str,
    model: str,
    install_date: pd.Timestamp,
    nameplate_capacity: float | None,
    nameplate_unit: str | None,
    tilt_deg: float | None = None,
    azimuth_deg: float | None = None,
    rated_voltage_v: float | None = None,
) -> dict:
    return {
        "sensor_id": sensor_id,
        "plant_id": plant_id,
        "sensor_type": sensor_type,
        "parent_sensor_id": parent_sensor_id,
        "manufacturer": manufacturer,
        "model": model,
        "install_date": install_date.date() if hasattr(install_date, "date") else install_date,
        "status": "active",
        "nameplate_capacity": nameplate_capacity,
        "nameplate_unit": nameplate_unit,
        "tilt_deg": tilt_deg,
        "azimuth_deg": azimuth_deg,
        "rated_voltage_v": rated_voltage_v,
    }


def build_sensors(cfg: GenerationConfig, plants: pd.DataFrame) -> pd.DataFrame:
    fake = Faker()
    fake.seed_instance(cfg.seed + 1)
    rng = np.random.default_rng(cfg.seed + 1)

    rows = []
    for _, plant in plants.iterrows():
        plant_id = plant["plant_id"]
        commissioning = pd.Timestamp(plant["commissioning_date"])
        total_ac_kw = plant["capacity_mw"] * 1000.0
        # Plants are typically built with more DC (panel) capacity than AC
        # (inverter) capacity, since panels rarely all peak simultaneously.
        total_dc_w = total_ac_kw * 1000.0 * 1.15

        inverter_ids = []
        for j in range(cfg.inverters_per_plant):
            sensor_id = f"INV-{plant_id}-{j + 1:02d}"
            inverter_ids.append(sensor_id)
            capacity_kw = (total_ac_kw / cfg.inverters_per_plant) * rng.uniform(0.9, 1.1)
            rows.append(
                _sensor_row(
                    sensor_id=sensor_id,
                    plant_id=plant_id,
                    sensor_type="inverter",
                    parent_sensor_id=None,
                    manufacturer=str(rng.choice(_INVERTER_MANUFACTURERS)),
                    model=fake.bothify("??-####").upper(),
                    install_date=commissioning,
                    nameplate_capacity=round(float(capacity_kw), 0),
                    nameplate_unit="kW",
                )
            )

        for j in range(cfg.panels_per_plant):
            sensor_id = f"PNL-{plant_id}-{j + 1:02d}"
            parent = inverter_ids[j % len(inverter_ids)]
            rated_power_w = (total_dc_w / cfg.panels_per_plant) * rng.uniform(0.85, 1.15)
            rows.append(
                _sensor_row(
                    sensor_id=sensor_id,
                    plant_id=plant_id,
                    sensor_type="panel_string",
                    parent_sensor_id=parent,
                    manufacturer=str(rng.choice(_PANEL_MANUFACTURERS)),
                    model=fake.bothify("PV-###W").upper(),
                    install_date=commissioning,
                    nameplate_capacity=round(float(rated_power_w), 0),
                    nameplate_unit="W",
                    tilt_deg=round(float(rng.uniform(10, 35)), 1),
                    azimuth_deg=round(float(rng.uniform(150, 210)), 1),  # roughly equator-facing
                    rated_voltage_v=round(float(rng.uniform(600, 1000)), 0),
                )
            )

        for j in range(cfg.batteries_per_plant):
            sensor_id = f"BAT-{plant_id}-{j + 1:02d}"
            # Sized as roughly 20-60 minutes of full-plant storage, a typical
            # co-located grid-scale ratio.
            capacity_kwh = total_ac_kw * rng.uniform(0.3, 1.0)
            rows.append(
                _sensor_row(
                    sensor_id=sensor_id,
                    plant_id=plant_id,
                    sensor_type="battery",
                    parent_sensor_id=None,
                    manufacturer=str(rng.choice(_BATTERY_MANUFACTURERS)),
                    model=fake.bothify("ESS-###").upper(),
                    install_date=commissioning,
                    nameplate_capacity=round(float(capacity_kwh), 0),
                    nameplate_unit="kWh",
                )
            )

        rows.append(
            _sensor_row(
                sensor_id=f"WX-{plant_id}-01",
                plant_id=plant_id,
                sensor_type="weather_station",
                parent_sensor_id=None,
                manufacturer=str(rng.choice(_WEATHER_STATION_MANUFACTURERS)),
                model=fake.bothify("WX-###").upper(),
                install_date=commissioning,
                nameplate_capacity=None,
                nameplate_unit=None,
            )
        )

    return pd.DataFrame(rows)
