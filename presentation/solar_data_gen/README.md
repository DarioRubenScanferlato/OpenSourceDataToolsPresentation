# solar_data_gen

Simulator for the synthetic solar fleet behind `solar_dashboard.py` and the
"From raw data to dashboards" deck: plant masterdata, physics-based
(pvlib) telemetry, weather, alarms, maintenance, billing and costs, with
real-world sensor faults (stuck values, dropouts) injected. Ported from the
standalone `SolarDataPlatform/generator` project so this repo is
self-contained.

`bronze.py` runs it for the deck's fleet (8 plants, 2 years, hourly, seed 7)
and writes one raw file per source system to `data/solar/bronze/`
(git-ignored). It is deterministic: the same seed gives identical files.

The dashboard and the deck offer to run it the first time they are opened
and the files are missing. To do it by hand, from `presentation/`:

```bash
uv run python -m solar_data_gen
```
