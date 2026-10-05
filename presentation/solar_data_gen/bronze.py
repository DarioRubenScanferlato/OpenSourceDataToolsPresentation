"""Generate the solar dashboard's raw ("bronze") data - one file per source system.

The generator simulates every source system at once, with some ground truth
mixed in (e.g. true DC power next to the SCADA reading, generated energy on
the billing rows). A real platform would receive each source separately and
only with what that source actually knows, so this keeps just that:

- plants.csv             - plant masterdata (the asset register)
- sensors.csv            - the sensor register: every sensor and the plant it
                           belongs to (the readings only carry a sensor_id)
- sensor_readings.csv.gz - hourly SCADA readings: timestamp, sensor, inverter AC
                           power - faults and all, and nothing *about* the
                           faults: spotting them is the cleaning step's job
- grid_settlement.csv    - daily settlement from the grid operator: metered
                           export, curtailment, tariff, revenue (no view of
                           what the plant *generated*)
- costs.csv              - daily cost accruals from the finance system
- alarms.csv             - alarm log from the monitoring system
- maintenance.csv        - work orders from the maintenance system

Usage (from the repository root):
    uv run python -m solar_data_gen            # from presentation/, or
    uv run python presentation/solar_data_gen/bronze.py

It is deterministic: the same seed always gives the same files.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

if __package__ in (None, ""):  # run as a plain script: make the package importable
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from solar_data_gen.config import GenerationConfig  # noqa: E402
from solar_data_gen.generate import run  # noqa: E402

BRONZE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "solar" / "bronze"
FILES = (
    "plants.csv",
    "sensors.csv",
    "sensor_readings.csv.gz",
    "grid_settlement.csv",
    "costs.csv",
    "alarms.csv",
    "maintenance.csv",
)

#: The fleet the deck and the dashboard are built around: 8 plants over two
#: years at hourly resolution, two of which open and one of which closes.
CONFIG = GenerationConfig(
    start_date=date(2024, 9, 21),
    end_date=date(2026, 9, 20),
    interval_minutes=60,
    n_plants=8,
    n_new_plants=2,
    n_decommissioned_plants=1,
    panels_per_plant=6,
    inverters_per_plant=2,
    batteries_per_plant=1,
    seed=7,
)


def is_ready(bronze_dir: Path = BRONZE_DIR) -> bool:
    """Whether every bronze file is already on disk."""
    return all((bronze_dir / name).is_file() for name in FILES)


def generate(bronze_dir: Path = BRONZE_DIR) -> list[Path]:
    """Simulate the fleet and write the bronze files. Takes a minute or two."""
    datasets = run(CONFIG)
    bronze_dir.mkdir(parents=True, exist_ok=True)

    datasets["dim_plants"].to_csv(bronze_dir / "plants.csv", index=False)
    datasets["dim_sensors"][
        [
            "sensor_id",
            "plant_id",
            "sensor_type",
            "parent_sensor_id",
            "manufacturer",
            "model",
            "install_date",
            "nameplate_capacity",
            "nameplate_unit",
        ]
    ].to_csv(bronze_dir / "sensors.csv", index=False)
    # Normalised like a real SCADA feed: a reading names its sensor, and the
    # sensor register says which plant that sensor is in.
    datasets["fact_inverter_telemetry"][
        ["timestamp", "sensor_id", "ac_power_kw"]
    ].to_csv(bronze_dir / "sensor_readings.csv.gz", index=False, compression="gzip")
    datasets["fact_energy_billing"].rename(columns={"billing_date": "settlement_date"})[
        [
            "settlement_date",
            "plant_id",
            "energy_exported_kwh",
            "curtailment_kwh",
            "tariff_eur_per_kwh",
            "revenue_eur",
        ]
    ].to_csv(bronze_dir / "grid_settlement.csv", index=False)
    datasets["fact_plant_costs"].to_csv(bronze_dir / "costs.csv", index=False)
    datasets["fact_alarm_events"].to_csv(bronze_dir / "alarms.csv", index=False)
    datasets["fact_maintenance_events"].to_csv(bronze_dir / "maintenance.csv", index=False)
    return [bronze_dir / name for name in FILES]


def main() -> None:
    print("Generating the solar bronze data (a minute or two)...")
    for path in generate():
        print(f"  {path.name:<24} {path.stat().st_size / 1e6:6.2f} MB")


if __name__ == "__main__":
    main()
