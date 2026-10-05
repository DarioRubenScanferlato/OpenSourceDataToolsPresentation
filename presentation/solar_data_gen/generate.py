"""End-to-end synthetic dataset generation pipeline."""

from __future__ import annotations

import numpy as np
import pandas as pd

from solar_data_gen import alarms as alarms_mod
from solar_data_gen import billing as billing_mod
from solar_data_gen import costs as costs_mod
from solar_data_gen import maintenance as maintenance_mod
from solar_data_gen import masterdata, streams
from solar_data_gen import weather as weather_mod
from solar_data_gen.config import GenerationConfig


def _time_index(cfg: GenerationConfig) -> pd.DatetimeIndex:
    start = pd.Timestamp(cfg.start_date, tz="UTC")
    end = pd.Timestamp(cfg.end_date, tz="UTC") + pd.Timedelta(days=1)
    return pd.date_range(start=start, end=end, freq=f"{cfg.interval_minutes}min", inclusive="left")


def run(cfg: GenerationConfig) -> dict[str, pd.DataFrame]:
    plants = masterdata.build_plants(cfg)
    sensors = masterdata.build_sensors(cfg, plants)
    times = _time_index(cfg)

    weather_frames, panel_frames, inverter_frames, battery_frames = [], [], [], []

    for plant_seq, (_, plant) in enumerate(plants.iterrows()):
        plant_rng = np.random.default_rng(cfg.seed + 100 + plant_seq)
        # A plant only has sensors (and so telemetry and weather readings)
        # while it's operating: from commissioning until decommissioning.
        plant_times = times[masterdata.operating_mask(plant, times)]
        if len(plant_times) == 0:
            continue
        observations, geometry, irradiance, ambient_temp = weather_mod.build_weather(
            plant["plant_id"], plant["latitude"], plant["longitude"], plant_times, plant_rng
        )
        weather_frames.append(observations)

        plant_sensors = sensors[sensors["plant_id"] == plant["plant_id"]]
        panel_sensors = plant_sensors[plant_sensors["sensor_type"] == "panel_string"]

        panel_telemetry_parts = []
        for _, panel in panel_sensors.iterrows():
            telemetry = streams.generate_panel_telemetry(
                panel, plant_times, geometry, irradiance, ambient_temp, plant_rng
            )
            panel_frames.append(telemetry)
            panel_telemetry_parts.append(telemetry)
        plant_panel_telemetry = pd.concat(panel_telemetry_parts, ignore_index=True)

        inverter_sensors = plant_sensors[plant_sensors["sensor_type"] == "inverter"]
        for _, inverter in inverter_sensors.iterrows():
            assigned_ids = panel_sensors.loc[
                panel_sensors["parent_sensor_id"] == inverter["sensor_id"], "sensor_id"
            ]
            assigned = plant_panel_telemetry[plant_panel_telemetry["sensor_id"].isin(assigned_ids)]
            inverter_frames.append(
                streams.generate_inverter_telemetry(inverter, assigned, plant_times, plant_rng)
            )

        total_dc_power = plant_panel_telemetry.groupby("timestamp")["dc_power_w"].sum()
        battery_sensors = plant_sensors[plant_sensors["sensor_type"] == "battery"]
        for _, battery in battery_sensors.iterrows():
            battery_frames.append(
                streams.generate_battery_telemetry(
                    battery,
                    total_dc_power,
                    plant_times,
                    plant_rng,
                    interval_minutes=cfg.interval_minutes,
                )
            )

    panel_telemetry = pd.concat(panel_frames, ignore_index=True)
    inverter_telemetry = pd.concat(inverter_frames, ignore_index=True)
    battery_telemetry = pd.concat(battery_frames, ignore_index=True)
    weather_observations = pd.concat(weather_frames, ignore_index=True)

    alarm_rng = np.random.default_rng(cfg.seed + 500)
    alarms = alarms_mod.build_alarms(panel_telemetry, inverter_telemetry, sensors, alarm_rng)

    maintenance = maintenance_mod.build_maintenance_events(
        plants,
        alarms,
        start=pd.Timestamp(cfg.start_date, tz="UTC"),
        end=pd.Timestamp(cfg.end_date, tz="UTC"),
        seed=cfg.seed,
    )

    billing = billing_mod.build_energy_billing(
        inverter_telemetry, plants, cfg.interval_minutes, cfg.seed
    )
    # Billing is settled from the (accurate) grid meter, i.e. the true power
    # above - only now do the SCADA readings pick up measurement faults
    # (stuck values, dropouts), the way a raw telemetry feed would.
    inverter_telemetry = streams.inject_reading_faults(
        inverter_telemetry, "ac_power_kw", np.random.default_rng(cfg.seed + 13)
    )
    plant_costs = costs_mod.build_plant_costs(plants, billing, cfg.seed)

    return {
        "dim_plants": plants,
        "dim_sensors": sensors,
        "fact_panel_telemetry": panel_telemetry,
        "fact_inverter_telemetry": inverter_telemetry,
        "fact_battery_telemetry": battery_telemetry,
        "fact_weather_observations": weather_observations,
        "fact_alarm_events": alarms,
        "fact_maintenance_events": maintenance,
        "fact_energy_billing": billing,
        "fact_plant_costs": plant_costs,
    }
