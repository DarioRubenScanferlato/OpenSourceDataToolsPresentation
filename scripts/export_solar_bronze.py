"""Turn a `solar-data-gen` run into the raw ("bronze") files the solar
dashboard ingests.

The generator simulates every source system at once, with some ground
truth mixed in (e.g. true DC power next to the SCADA reading, generated
energy on the billing rows). A real platform would receive each source
separately and only with what that source actually knows, so this keeps
just that:

- plants.csv            - plant masterdata (the asset register)
- sensor_readings.csv.gz - hourly SCADA readings: inverter AC power, faults and all
- grid_settlement.csv   - daily settlement from the grid operator: metered
                          export, curtailment, tariff, revenue (no view of
                          what the plant *generated*)
- costs.csv             - daily cost accruals from the finance system
- alarms.csv            - alarm log from the monitoring system
- maintenance.csv       - work orders from the maintenance system

Usage:
    uv run python scripts/export_solar_bronze.py /path/to/solar-data-gen/output
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

BRONZE_DIR = Path(__file__).resolve().parent.parent / "data" / "solar" / "bronze"


def _read(out_dir: Path, dataset: str) -> pd.DataFrame:
    """The generator writes <dataset>/<dataset>_<run_id>.csv."""
    (path,) = sorted((out_dir / dataset).glob(f"{dataset}_*.csv"))[-1:]
    return pd.read_csv(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("generator_output", type=Path)
    args = parser.parse_args()
    src = args.generator_output
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)

    _read(src, "dim_plants").to_csv(BRONZE_DIR / "plants.csv", index=False)

    readings = _read(src, "fact_inverter_telemetry")[
        ["timestamp", "plant_id", "sensor_id", "ac_power_kw"]
    ]
    readings.to_csv(BRONZE_DIR / "sensor_readings.csv.gz", index=False, compression="gzip")

    settlement = _read(src, "fact_energy_billing").rename(columns={"billing_date": "settlement_date"})[
        [
            "settlement_date",
            "plant_id",
            "energy_exported_kwh",
            "curtailment_kwh",
            "tariff_eur_per_kwh",
            "revenue_eur",
        ]
    ]
    settlement.to_csv(BRONZE_DIR / "grid_settlement.csv", index=False)

    _read(src, "fact_plant_costs").to_csv(BRONZE_DIR / "costs.csv", index=False)
    _read(src, "fact_alarm_events").to_csv(BRONZE_DIR / "alarms.csv", index=False)
    _read(src, "fact_maintenance_events").to_csv(BRONZE_DIR / "maintenance.csv", index=False)

    for path in sorted(BRONZE_DIR.iterdir()):
        print(f"  {path.name:<24} {path.stat().st_size / 1e6:6.2f} MB")


if __name__ == "__main__":
    main()
