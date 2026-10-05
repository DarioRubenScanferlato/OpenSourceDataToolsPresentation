"""Alarm/fault event log derived from telemetry fault flags."""

from __future__ import annotations

import numpy as np
import pandas as pd

_ALARM_CODES = {
    "panel_string": ("STRING_OUTAGE", "critical"),
    "inverter": ("INVERTER_FAULT", "critical"),
}

_RANDOM_ALARM_CODES = [
    ("COMMS_TIMEOUT", "warning"),
    ("SENSOR_DRIFT", "info"),
    ("OVER_TEMPERATURE", "warning"),
]


def _episodes_from_mask(telemetry: pd.DataFrame) -> pd.DataFrame:
    """Collapse a per-timestamp `is_fault` boolean column into start/end episodes."""
    episodes = []
    for sensor_id, group in telemetry.groupby("sensor_id"):
        group = group.sort_values("timestamp")
        is_fault = group["is_fault"].to_numpy()
        timestamps = group["timestamp"].to_numpy()
        plant_id = group["plant_id"].iloc[0]
        start = None
        for i, flag in enumerate(is_fault):
            if flag and start is None:
                start = i
            elif not flag and start is not None:
                episodes.append((sensor_id, plant_id, timestamps[start], timestamps[i - 1]))
                start = None
        if start is not None:
            episodes.append((sensor_id, plant_id, timestamps[start], timestamps[-1]))
    return pd.DataFrame(episodes, columns=["sensor_id", "plant_id", "triggered_at", "cleared_at"])


def build_alarms(
    panel_telemetry: pd.DataFrame,
    inverter_telemetry: pd.DataFrame,
    sensors: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    rows = []
    alarm_seq = 1

    for sensor_type, telemetry in (
        ("panel_string", panel_telemetry),
        ("inverter", inverter_telemetry),
    ):
        code, severity = _ALARM_CODES[sensor_type]
        for _, ep in _episodes_from_mask(telemetry).iterrows():
            rows.append(
                {
                    "alarm_id": f"ALM-{alarm_seq:06d}",
                    "plant_id": ep["plant_id"],
                    "sensor_id": ep["sensor_id"],
                    "alarm_code": code,
                    "severity": severity,
                    "triggered_at": ep["triggered_at"],
                    "cleared_at": ep["cleared_at"],
                    "description": f"{code.replace('_', ' ').title()} on {ep['sensor_id']}",
                }
            )
            alarm_seq += 1

    # Sprinkle a handful of independent, lower-severity alarms for variety.
    n_random = max(5, len(sensors) // 4)
    sample_sensors = sensors.sample(
        n=min(n_random, len(sensors)), random_state=int(rng.integers(0, 2**32 - 1))
    )
    all_times = (
        pd.concat([panel_telemetry["timestamp"], inverter_telemetry["timestamp"]])
        .drop_duplicates()
        .sort_values()
        .reset_index(drop=True)
    )
    for _, sensor in sample_sensors.iterrows():
        code, severity = _RANDOM_ALARM_CODES[int(rng.integers(0, len(_RANDOM_ALARM_CODES)))]
        triggered = all_times.sample(n=1, random_state=int(rng.integers(0, 2**32 - 1))).iloc[0]
        cleared = triggered + pd.Timedelta(minutes=int(rng.integers(15, 240)))
        rows.append(
            {
                "alarm_id": f"ALM-{alarm_seq:06d}",
                "plant_id": sensor["plant_id"],
                "sensor_id": sensor["sensor_id"],
                "alarm_code": code,
                "severity": severity,
                "triggered_at": triggered,
                "cleared_at": cleared,
                "description": f"{code.replace('_', ' ').title()} on {sensor['sensor_id']}",
            }
        )
        alarm_seq += 1

    return pd.DataFrame(rows).sort_values("triggered_at").reset_index(drop=True)
