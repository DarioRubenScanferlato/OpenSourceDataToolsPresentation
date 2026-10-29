# From raw data to dashboard with open source software

These are the slides for my talk at the Ticino Data Conference 2026. The talk asks a simple question: can you go from raw data to a good dashboard using only open source tools? And if you can, is it a good idea, compared to paying for a managed data platform?

To answer it, I go through the pieces of a data platform one at a time: ingestion, storage and query engines, transformation, dashboards, orchestration and deployment. Then I look at what it all costs.

The slides are a [marimo](https://marimo.io) notebook, so the demos are live. The dashboard in the talk is a real one that you can filter and click around in, and the SQL query on the DuckDB slide runs again whenever you edit it. The data behind it is made up: eight solar plants over two years, generated on your machine.

## Running it

You need [uv](https://docs.astral.sh/uv/getting-started/installation/). It installs the right Python version (3.14) and everything else for you.

```bash
git clone https://github.com/DarioRubenScanferlato/OpenSourceDataToolsPresentation.git
```

```bash
cd OpenSourceDataToolsPresentation
```

```bash
uv sync
```

Then start the presentation:

```bash
uv run marimo run presentation/raw_data_to_dashboards_with_os_technologies.py --include-code --no-show-tracebacks
```

It opens in your browser. Use the right arrow to go to the next section, and the down arrow for the slides and steps inside it.

The first time you run it, it generates the data, which takes about 20 seconds. Until then the dashboard slides stay empty. So if you're presenting, open it once beforehand.

To change the slides, open the notebook in the editor instead:

```bash
uv run marimo edit presentation/raw_data_to_dashboards_with_os_technologies.py
```

You can also open the dashboard on its own:

```bash
uv run marimo run presentation/solar_dashboard.py
```

## The data

The data isn't in the repo (`data/` is git-ignored). It's simulated by `presentation/solar_data_gen/`, using real solar physics (pvlib), plus weather, alarms, maintenance, billing and costs, with some realistic sensor faults thrown in. The seed is fixed, so everyone gets the same files. They end up in `data/solar/bronze/`.

The presentation creates them for you on the first run. To do it by hand:

```bash
cd presentation && uv run python -m solar_data_gen
```

## What's where

- `presentation/raw_data_to_dashboards_with_os_technologies.py`: the slides
- `presentation/layouts/`: the slide types and speaker notes, one entry per notebook cell, in the same order
- `presentation/solar_dashboard.py`: the dashboard shown in the talk
- `presentation/solar_data_gen/`: the data simulator
- `presentation/template/`: the slide template (colors, fonts, slide components)
- `presentation/assets/`: diagrams, logos and images
