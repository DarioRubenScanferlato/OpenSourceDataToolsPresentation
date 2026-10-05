"""Maintenance work order generation: scheduled preventive work plus repairs
triggered by critical alarms."""

from __future__ import annotations

import numpy as np
import pandas as pd
from faker import Faker

_EVENT_TYPES_PREVENTIVE = ["panel_cleaning", "routine_inspection", "vegetation_control"]

_COLUMNS = [
    "event_id",
    "plant_id",
    "asset_id",
    "event_type",
    "status",
    "technician_name",
    "scheduled_date",
    "completed_date",
    "downtime_hours",
    "cost_eur",
    "related_alarm_id",
]


def build_maintenance_events(
    plants: pd.DataFrame,
    alarms: pd.DataFrame,
    start: pd.Timestamp,
    end: pd.Timestamp,
    seed: int,
) -> pd.DataFrame:
    fake = Faker()
    fake.seed_instance(seed + 2)
    rng = np.random.default_rng(seed + 2)

    rows = []
    event_seq = 1

    for _, plant in plants.iterrows():
        # preventive work only while the plant is operating
        plant_start = max(start, pd.Timestamp(plant["commissioning_date"], tz=start.tz))
        plant_end = end
        if plant.get("decommissioning_date") is not None and not pd.isna(plant["decommissioning_date"]):
            plant_end = min(end, pd.Timestamp(plant["decommissioning_date"], tz=end.tz))
        current = plant_start + pd.Timedelta(days=int(rng.integers(1, 30)))
        while current <= plant_end:
            event_type = _EVENT_TYPES_PREVENTIVE[int(rng.integers(0, len(_EVENT_TYPES_PREVENTIVE)))]
            duration_hours = round(float(rng.uniform(2, 8)), 1)
            rows.append(
                {
                    "event_id": f"WO-{event_seq:06d}",
                    "plant_id": plant["plant_id"],
                    "asset_id": None,
                    "event_type": event_type,
                    "status": "completed",
                    "technician_name": fake.name(),
                    "scheduled_date": current.date(),
                    "completed_date": (current + pd.Timedelta(hours=duration_hours)).date(),
                    "downtime_hours": 0.0,
                    "cost_eur": round(float(rng.uniform(400, 3500)), 2),
                    "related_alarm_id": None,
                }
            )
            event_seq += 1
            current += pd.Timedelta(days=int(rng.integers(45, 75)))

    critical = alarms[alarms["severity"] == "critical"]
    for _, alarm in critical.iterrows():
        triggered = pd.Timestamp(alarm["triggered_at"])
        cleared = pd.Timestamp(alarm["cleared_at"])
        downtime_hours = round((cleared - triggered).total_seconds() / 3600.0, 2)
        rows.append(
            {
                "event_id": f"WO-{event_seq:06d}",
                "plant_id": alarm["plant_id"],
                "asset_id": alarm["sensor_id"],
                "event_type": "corrective_repair",
                "status": "completed",
                "technician_name": fake.name(),
                "scheduled_date": triggered.date(),
                "completed_date": cleared.date(),
                "downtime_hours": downtime_hours,
                "cost_eur": round(float(rng.uniform(200, 6000)), 2),
                "related_alarm_id": alarm["alarm_id"],
            }
        )
        event_seq += 1

    return pd.DataFrame(rows, columns=_COLUMNS).sort_values("scheduled_date").reset_index(drop=True)
