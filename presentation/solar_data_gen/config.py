"""Configuration for a synthetic data generation run."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass
class GenerationConfig:
    start_date: date
    end_date: date
    interval_minutes: int = 15
    n_plants: int = 3
    panels_per_plant: int = 8
    inverters_per_plant: int = 2
    batteries_per_plant: int = 1
    seed: int = 42
    #: Plants (the last `n_new_plants` of `n_plants`) commissioned *during*
    #: the generated period rather than before it.
    n_new_plants: int = 0
    #: Plants (among those running from the start) decommissioned during the period.
    n_decommissioned_plants: int = 0
    output_dir: str = "data/output"
    output_format: str = "parquet"  # "parquet" or "csv"
