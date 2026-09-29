"""From raw data to dashboard with open source software.

Ticino Data Conference, 2026. Speaker notes and slide order live in
``layouts/OS_data_platform.slides.json`` - regenerate it after adding or
removing cells with the script at the bottom of this file (see the last cell).

Run it:      uv run marimo edit presentation/OS_data_platform.py
Present it:  uv run marimo run presentation/OS_data_platform.py --include-code --no-show-tracebacks
"""

import marimo

__generated_with = "0.24.0"
app = marimo.App(
    width="medium",
    layout_file="layouts/OS_data_platform.slides.json",
    css_file="template/nearform.css",
)


@app.cell
def _():
    import altair as alt
    import marimo as mo
    import pandas as pd

    from template import assets, nf, theme

    return alt, assets, mo, nf, pd, theme


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Index
    - Intro 5:00
        - Title :15
        - Speaker presentation :45
        - Nearform :45
        - Agenda :30
        - From raw data to dashboards 1:00
        - What is a data platform 1:00
            - Data sources -> Transform -> Data Store -> Visualization -> cross-filters
    - Data platforms and their services (comparison of services: Fabric, Databricks, Snowflake) 2:00
    - OS technologies 20:00
        - postgres 3:00 - https://db-engines.com/en/ranking
        - duckdb 3:00
        - clickhouse 2:00
        - airflow/prefect 1:00
        - data formats (parquet/delta/iceberg) 5:00
        - Data governance
    - Data visualization 7:30
        - pros and cons of power bi - features
        - superset/metabase
        - Coding your own dashboard
        - perspective
    - Pros and cons of open source 7:30
        - Decision drivers when deciding between open source or managed data platform
        - Cost - infrastructure/memory/compute/storage, licenses, info from Adriano Sanges talk
            - 47% of developers work in companies <100 employees. Power BI developer probably work in bigger firms
        - Lock-in effects - proprietary software, programming languages
        - Technical skills
        - Features - open source lets you implement whatever you want, managed data platforms already implement almost anything you would ever want
        - One-stop shop
        - Maintenance, SLAs
        - Performance
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # notes
    - The increases in main-memory sizes over the last decade have made pure in-memory database systems feasible, and in-memory systems offer unprecedented performance. However, DRAM is still relatively expensive, and the growth of main-memory sizes has slowed down. In contrast, the prices for SSDs have fallen substantially in the last years, and their read bandwidth has increased to gigabytes per second. This makes it attractive to combine a large in-memory buffer with fast SSDs as storage devices, combining the excellent performance for the in-memory working set with the scalability of a disk-based system.
    - SSAS vertipaq import mode can be considered in-memory
    - Many data platform are starting to focus on open source technology at its core, and they support open data formats.
        - Parquet, Delta, Iceberg formats
    - Postgres, DuckDB, Airflow/prefect, dbt, Clickhouse
    - Open source business models (community driven, foundations, backed by companies)
    - Open source good for academia or government
    - Proprietary platform and tools have lock-in effects
    - https://duckdblabs.github.io/db-benchmark/
    - Jordan Tigani - big data is dead
    """)
    return


@app.cell
def _(nf):
    nf.title_slide(
        "From raw data to dashboard with open source software",
        event="Ticino Data Conference - 2026",
        author="Dario Ruben Scanferlato, Nearform",
    )
    return


@app.cell
def _(assets, nf):
    nf.speaker(
        name="Dario Ruben Scanferlato",
        role="Senior Data Engineer @ Nearform",
        handle="dario.scanferlato@gmail.com",
        photo=assets.img("images/profilepic.jpg"),
        bio=[
            "Worked in the supply chain, healthcare, and energy sectors",
            "Currently developing a nature conservation planning agentic app",
            "MSc in Engineering and Management at Politecnico di Torino",
            "Organizer for the Python Torino user group",
            "Talk to me about recording music, chess, and open-source",
        ],
        page=2,
    )
    return


@app.cell
def _(nf):
    nf.slide(
        nf.bullets(
            [
                "Is it possible to go from raw data to dashboards with open source tools",
                "How would you even do it?",
                "Is it a good idea?",
                "Why would it be better than using a managed data platform?",
            ]
        ),
        title="In this presentation",
        page=4,
    )
    return


@app.cell
def _(nf):
    nf.slide(
        title="Is it possible to create great dashboards from raw data using open source technologies?", align='center', page=3
    )
    return


@app.cell(hide_code=True)
def _():
    from solar_dashboard import app as solar_app

    return (solar_app,)


@app.cell(hide_code=True)
async def _(solar_app):
    # `embed()` can't be called in the cell that imports the app - marimo
    # runs the embedded notebook in its own nested kernel, so every `mo.ui`
    # element (the filters, the click cross-filter) stays fully interactive
    # here, not just a static screenshot. `dashboard.defs` exposes every
    # top-level name the notebook defines (dataframes, charts, UI elements),
    # which the next few slides reuse directly instead of recomputing.
    dashboard = await solar_app.embed()
    return (dashboard,)


@app.cell(hide_code=True)
def _(mo, theme):
    def full_bleed_slide(content, *, natural_width=1650):
        """A slide with none of `nf.slide()`'s margins, for content - like an
        embedded notebook - that already brings its own layout and sizing.

        `nf.slide()`'s own content sizes itself with `cqw` units, which
        resolve against the slide's *actual* rendered width - whatever that
        turns out to be (there's no single "960px" to target: reveal scales
        the deck to the window, and the slide box itself sits inside some
        margin on top of that, so its real width is a moving target - a
        fixed guess like ``theme.DECK_W`` is what left this covering only
        part of the slide before).

        The embedded dashboard is a real, fixed-pixel-width page though, so
        it can't be reflowed with plain CSS - `container-type: inline-size`
        makes `cqw` resolve against *this wrapper's own* rendered width, and
        `calc(100cqw / {natural_width}px)` divides that by the dashboard's
        pixel width to get the scale factor, live, in pure CSS (modern
        browsers support dividing a length by a length in `calc()` down to
        a plain number). `zoom`, not `transform`, because `zoom` actually
        reflows layout at the zoomed size, so this wrapper's height ends up
        matching automatically - no separate height has to be guessed or
        measured. If the result is still taller than one slide, it scrolls,
        like any other dense slide in this deck (see `nf.slide()`'s
        `pad_top` note).
        """
        _inner = (
            f'<div style="width:{natural_width}px; '
            f"zoom:calc(100cqw / {natural_width}px);\">"
            f"{mo.as_html(content).text}</div>"
        )
        # No `min-height` here (unlike `nf.slide()`'s own frame): with one,
        # this box couldn't shrink below one full slide even once the
        # zoomed content was already shorter than that - which is exactly
        # what was leaving empty space at the bottom, whatever the zoom
        # factor. Height should come from the content alone.
        return mo.Html(
            f'<div data-nf-slide data-nf-tone="navy" style="box-sizing:border-box; '
            f'container-type:inline-size; width:100%; background:{theme.NAVY};">'
            f"{_inner}</div>"
        )

    return (full_bleed_slide,)


@app.cell
def _(dashboard, full_bleed_slide):
    # Scale by the dashboard's own chart width, not the helper's default:
    # the embedded notebook renders without its grid layout, so
    # nf-dashboard.css's zoom rules (keyed on `.react-grid-item`) don't
    # apply here and the Vega chart sits at its fixed `DASHBOARD_WIDTH` -
    # a wider wrapper leaves that difference as an empty strip on the right.
    full_bleed_slide(dashboard.output, natural_width=dashboard.defs["DASHBOARD_WIDTH"])
    return


@app.cell
def _(dashboard, mo, nf):
    _code = '''
    BRONZE = Path("data/solar/bronze")  # raw files, one per source system

    plants = pd.read_csv(BRONZE / "plants.csv")                     # asset register
    sensor_readings = pd.read_csv(BRONZE / "sensor_readings.csv.gz")  # SCADA, hourly
    grid_settlement = pd.read_csv(BRONZE / "grid_settlement.csv")     # grid operator, daily
    '''
    # Show the sensor readings around a stuck sensor, so the raw data's
    # problems are visible straight away (the next slide deals with them).
    _r = dashboard.defs["readings"].reset_index(drop=True)
    _at = int(_r.index[_r["issue"] == "stuck"][0])
    _raw_cols = ["timestamp", "plant_id", "sensor_id", "ac_power_kw"]
    nf.slide(
        nf.code(_code),
        # A tab per dataframe rather than all three side by side - three
        # wide tables at once didn't fit the slide; one at a time does.
        mo.ui.tabs(
            {
                "sensor_readings": nf.dataframe(_r.iloc[_at - 2 : _at + 3][_raw_cols], max_rows=5),
                "grid_settlement": nf.dataframe(dashboard.defs["grid_settlement"], max_rows=5),
                "plants": nf.dataframe(dashboard.defs["plants"], max_rows=5),
            }
        ),
        title="Ingesting the raw data",
        kicker="Bronze: one file per source",
        # This slide is denser than most (code + tabs + a table): the
        # template's usual top margin and inter-block rhythm, sized for a
        # sparse title+bullets slide, left this one taller than the frame -
        # buy the room back here instead of shrinking the table further.
        pad_top="5cqw",
        gap="1.2cqw",
    )
    return

@app.cell
def _(alt, dashboard, nf, pd, theme):
    _code = '''
    readings = sensor_readings.sort_values(["sensor_id", "timestamp"])
    power = readings["ac_power_kw"]

    # a stuck sensor repeats the value it froze on - real output never does
    run = (power != readings.groupby("sensor_id")["ac_power_kw"].shift()).cumsum()
    stuck = (readings.groupby(run)["ac_power_kw"].transform("size") >= 3) & (power > 0)

    # stuck + missing (NaN) readings: use the same hour the day before
    readings["ac_power_kw_clean"] = (
        power.mask(stuck)
        .groupby(readings["sensor_id"])
        .transform(lambda s: s.fillna(s.shift(24)))
    )
    '''
    # One real faulty stretch from the data: the first stuck episode with
    # a dropout (NaN) within a day and a half on the same sensor, shown
    # with both in view plus some normal days around them.
    _r = dashboard.defs["readings"]
    _pick, _near = None, None
    for _, _row in _r[_r["issue"] == "stuck"].iterrows():
        _cand = _r[
            (_r["sensor_id"] == _row["sensor_id"])
            & (_r["issue"] == "missing")
            & ((_r["timestamp"] - _row["timestamp"]).abs() <= pd.Timedelta(hours=36))
        ]
        if len(_cand):
            _pick, _near = _row, _cand["timestamp"].iloc[0]
            break
    if _pick is None:
        _pick = _r[_r["issue"] == "stuck"].iloc[0]
        _near = _pick["timestamp"]
    _lo = min(_pick["timestamp"], _near) - pd.Timedelta(hours=30)
    _hi = max(_pick["timestamp"], _near) + pd.Timedelta(hours=30)
    _win = _r[(_r["sensor_id"] == _pick["sensor_id"]) & _r["timestamp"].between(_lo, _hi)]
    _lines = pd.concat(
        [
            _win.assign(series="Raw reading", kw=_win["ac_power_kw"]),
            _win.assign(series="Cleaned", kw=_win["ac_power_kw_clean"]),
        ]
    )
    _series = ["Raw reading", "Cleaned", "Stuck", "Missing (NaN)"]
    _color = alt.Color(
        "series:N",
        title=None,
        scale=alt.Scale(domain=_series, range=[theme.MUTED, theme.MINT, "#FF7A8A", theme.LAVENDER]),
        legend=alt.Legend(orient="top", direction="horizontal"),
    )
    _x = alt.X("timestamp:T", title=None, axis=alt.Axis(format="%b %d %H:%M", labelAngle=0, tickCount=4))
    _chart = (
        alt.Chart(_lines)
        .mark_line(strokeWidth=2)
        .encode(
            x=_x,
            y=alt.Y("kw:Q", title="AC power (kW)"),
            color=_color,
            strokeDash=alt.StrokeDash("series:N", scale=alt.Scale(domain=["Raw reading", "Cleaned"], range=[[1, 0], [5, 3]]), legend=None),
        )
        + alt.Chart(_win[_win["issue"] == "stuck"].assign(series="Stuck"))
        .mark_circle(size=70, opacity=1)
        .encode(x=_x, y="ac_power_kw:Q", color=_color)
        + alt.Chart(_win[_win["issue"] == "missing"].assign(series="Missing (NaN)"))
        # no value to plot, so a tick along the bottom of the plot marks the hour
        .mark_tick(thickness=3, size=14, opacity=1)
        .encode(x=_x, y=alt.value(222), color=_color)
    # fills its column, whatever the window size
    ).properties(width="container", height=230, title=f"{_pick['sensor_id']}")
    nf.slide(
        nf.two_col(nf.code(_code), _chart, ratio=(1, 1)),
        title="Spotting broken sensors",
        kicker="Bronze to gold, step 1: clean",
        pad_top="5cqw",
    )
    return

@app.cell
def _(dashboard, nf):
    _code = '''
    # hourly kW -> daily kWh per plant (one reading = one hour)
    readings["date"] = readings["timestamp"].dt.tz_localize(None).dt.normalize()
    daily = readings.groupby(["plant_id", "date"], as_index=False).agg(
        energy_generated_kwh=("ac_power_kw_clean", "sum")
    )
    # join what the grid operator metered and paid, and the plant masterdata
    gold = daily.merge(grid_settlement.rename(columns={"settlement_date": "date"})).merge(
        plants[["plant_id", "name", "capacity_mw"]]
    )
    # derive what neither source has on its own
    gold["self_consumption_kwh"] = (
        gold["energy_generated_kwh"] - gold["energy_exported_kwh"] - gold["curtailment_kwh"]
    ).clip(lower=0)
    '''
    _cols = [
        "date", "name", "energy_generated_kwh", "energy_exported_kwh",
        "curtailment_kwh", "self_consumption_kwh", "revenue_eur",
    ]
    nf.slide(
        nf.code(_code),
        nf.dataframe(dashboard.defs["gold"][_cols], max_rows=3),
        title="From bronze to gold",
        kicker="Step 2: aggregate, join, derive",
        pad_top="5cqw",
        gap="1.2cqw",
    )
    return

@app.cell
def _(dashboard, nf):
    _code = '''
    # gold is already one row per (plant, day)
    alt.Chart(gold).mark_area(line={"strokeWidth": 1.5}).encode(
        x="date:T",                                       # date, on the x-axis
        y=alt.Y(
            "energy_generated_kwh:Q",
            stack="zero",                                 # stack plants instead of overlapping them
        ),
        color="name:N",                                   # one color per plant
    )
    '''
    nf.slide(
        # The dashboard's own copy is sized to fill a full-width panel - far
        # wider than half a slide - so shrink this one back to half-slide.
        nf.two_col(
            nf.code(_code),
            dashboard.defs["line_chart"].properties(width=510, height=320),
            ratio=(1, 1),
        ),
        title="Plotting a chart",
        kicker="Altair, stacked area",
        # The chart keeps the dashboard's own fixed pixel size (so it's the
        # *same* chart, not a redrawn one) - that's taller than this denser
        # slide's default top margin leaves room for, so buy the room back
        # the same way the ingestion slide does.
        pad_top="5cqw",
    )
    return


@app.cell
def _(dashboard, mo):
    _plants = dashboard.defs["dim_plants"]
    _gold = dashboard.defs["gold"]
    # Fresh widgets, not the *same* objects as the dashboard slide: a
    # marimo UI element is bound to exactly one live DOM mount, so
    # displaying `dashboard.defs["date_from"]` a second time here left a
    # second, inert copy that didn't respond to clicks - only the first
    # mount (on the dashboard slide) was actually wired up. These are
    # independent, so clicking them here works, at the cost of no longer
    # being in sync with the dashboard slide's own filters. (A UI element's
    # `.value` can't be read in the same cell that creates it, hence the
    # split from the slide-building cell below.)
    location_filter = mo.ui.multiselect(
        options=sorted(_plants["name"]), value=sorted(_plants["name"])
    )
    date_from = mo.ui.date(value=_gold["date"].min().date())
    date_to = mo.ui.date(value=_gold["date"].max().date())
    return date_from, date_to, location_filter


@app.cell
def _(date_from, date_to, location_filter, mo, nf):
    _code = '''
    location_filter = mo.ui.multiselect(
        options=sorted(dim_plants["name"]), value=sorted(dim_plants["name"])
    )
    date_from = mo.ui.date(value=min_date)
    date_to = mo.ui.date(value=max_date)

    mo.hstack([location_filter, date_from, date_to])

    # each widget's current value, live:
    f"{len(location_filter.value)} plants, {date_from.value} to {date_to.value}"
    '''
    # `wrap=True` is load-bearing, not cosmetic: with all 7 plants selected
    # by default, the multiselect's own chip row is already wide enough
    # that an unwrapped hstack pushed both date pickers past the slide's
    # right edge - clicking where they *should* be hit nothing, which is
    # exactly the "dates picker don't work at all" bug this fixes.
    _widgets = mo.as_html(
        mo.hstack(
            [location_filter, date_from, date_to], justify="start", gap=2, wrap=True
        )
    ).text
    # marimo's date widget is dark-mode-aware, but *this notebook's* own
    # display theme is "light" (marimo's default), so by itself it renders
    # with light colors - white text on a white control - regardless of
    # this slide's navy paint. Its shadow-DOM styles pick their palette via
    # `:host-context(.dark)`, which checks for a `.dark` class anywhere in
    # the *light-DOM* ancestor chain (crossing the shadow boundary is what
    # `:host-context` is for) - so just wrapping it in one here is enough,
    # no per-property overrides needed (and none would reach past the
    # shadow boundary anyway).
    nf.slide(
        nf.code(_code),
        mo.Html(f'<div class="dark">{_widgets}</div>'),
        nf.caption(
            f"Selected: **{len(location_filter.value)} plants**, "
            f"**{date_from.value}** to **{date_to.value}** - click a plant "
            "chip or a date above and this line updates."
        ),
        title="Filters, straight from marimo",
        kicker="mo.ui, not a custom form",
        # Wrapping the widget row (so the date pickers stay on-slide, see
        # above) added a second row's worth of height - buy that back too.
        pad_top="5cqw",
        gap="1.2cqw",
    )
    return


@app.cell
def _(nf):
    _code = '''
    plant_sel = alt.selection_point(fields=["name"], on="click", clear="dblclick")

    # table, line chart: dim the other plants
    chart.add_params(plant_sel).encode(
        opacity=alt.condition(plant_sel, alt.value(1.0), alt.value(0.2))
    )
    # monthly P&L: keep only the selected plant's rows
    alt.Chart(pnl_monthly).transform_filter(plant_sel)
    '''
    nf.slide(
        nf.code(_code),
        nf.bullets(
            [
                "One selection object, shared by the table, the line chart, the sankey and the monthly P&L",
                "Charts react in the browser: dimming the other plants, or switching to that plant's own numbers - no server round-trip",
                "The KPI cards follow too: marimo sends the selection back to Python, which recomputes them",
            ]
        ),
        title="Crossfiltering, for free",
        kicker="One selection, the whole dashboard",
    )
    return


@app.cell
def _(nf):
    nf.slide(
        nf.lead(
            "A data platform provides a centralized solution for managing and interacting with data. It may include services for:"
        ),
        nf.bullets(
            [
                "Ingestion - receive data from external sources",
                "Storage - data in buckets, databases, data warehouses, or lakehouses",
                "Transformation - manipulating, joining, aggregating data",
                "Observability",
                "Orchestration",
                "Development tooling - CI/CD, testing, versioning",
                "Visualization - gain insight from charts, dashboards",
                "Governance - data access policies, encryption policies, lineage, catalogue, compliance",
                "Infrastructure - for running all of the above"
            ]
        ),
        title="Data platform? What do you mean?",
    )
    return


@app.cell
def _(assets, mo, nf, theme):
    # Pick a platform to see how it fills in the components from the previous slide.
    # (name, logo, note) per component. Drop logo files into presentation/images/logos/
    # - anything missing falls back to an initials chip, so the slide always reads.
    _PLATFORMS = {
        "Microsoft Fabric": (
            "logos/fabric.png",
            {
                "Ingestion": [("Data Factory", "logos/fabric-data-factory.png", "pipelines, copy job")],
                "Storage": [("OneLake", "logos/onelake.png", "Delta Parquet")],
                "Transformation": [("Notebooks", "logos/fabric-notebooks.png", "Spark"),
                                   ("Dataflows Gen2", "logos/dataflows.png", None)],
                "Observability": [("Monitoring hub", "logos/fabric-monitor.png", None)],
                "Orchestration": [("Data Factory", "logos/fabric-data-factory.png", "scheduled pipelines")],
                "Dev tooling": [("Git integration", "logos/fabric-git.png", "deployment pipelines")],
                "Visualization": [("Power BI", "logos/powerbi.png", "Direct Lake")],
                "Governance": [("Purview", "logos/purview.png", None)],
                "Infrastructure": [("Fabric capacity", "logos/fabric.png", "SaaS, F SKUs")],
            },
        ),
        "Databricks": (
            "logos/databricks.png",
            {
                "Ingestion": [("Lakeflow Connect", "logos/lakeflow.png", "Auto Loader")],
                "Storage": [("Delta Lake", "logos/delta-lake.png", "on S3 / ADLS")],
                "Transformation": [("Apache Spark", "logos/spark.png", None),
                                   ("Declarative Pipelines", "logos/lakeflow.png", "ex-DLT")],
                "Observability": [("Lakehouse Monitoring", "logos/databricks.png", "system tables")],
                "Orchestration": [("Lakeflow Jobs", "logos/lakeflow.png", "ex-Workflows")],
                "Dev tooling": [("Asset Bundles", "logos/databricks.png", "Repos, CLI")],
                "Visualization": [("AI/BI Dashboards", "logos/aibi.png", "Genie")],
                "Governance": [("Unity Catalog", "logos/unity-catalog.png", None)],
                "Infrastructure": [("Your cloud account", "logos/databricks.png", "clusters, SQL warehouses")],
            },
        ),
        "Snowflake": (
            "logos/snowflake.png",
            {
                "Ingestion": [("Snowpipe", "logos/snowpipe.png", "+ Streaming")],
                "Storage": [("Snowflake tables", "logos/snowflake.png", None),
                            ("Iceberg tables", "logos/iceberg.png", "external volumes")],
                "Transformation": [("Dynamic Tables", "logos/dynamic-tables.png", None),
                                   ("Snowpark", "logos/snowpark.png", "Python")],
                "Observability": [("Snowflake Trail", "logos/snowflake.png", "account usage")],
                "Orchestration": [("Streams & Tasks", "logos/snowflake-tasks.png", None)],
                "Dev tooling": [("Snowflake CLI", "logos/snowflake-cli.png", "Git integration")],
                "Visualization": [("Snowsight", "logos/snowsight.png", "dashboards"),
                                  ("Streamlit", "logos/streamlit.png", "in Snowflake")],
                "Governance": [("Horizon Catalog", "logos/horizon.png", None)],
                "Infrastructure": [("Virtual warehouses", "logos/snowflake.png", "SaaS")],
            },
        ),
    }


    def _tab_label(_name, _logo):
        """Tab labels run through mo.md, so an inline <img> renders in the tab strip."""
        if not assets.exists(_logo):
            return _name
        _mark = assets.img(
            _logo, width="auto", rounded=False, alt=_name,
            style={"height": "1.1em", "object-fit": "contain",
                   "display": "inline-block", "vertical-align": "middle"},
        ).text
        return f"{_mark} {_name}"


    nf.slide(
        mo.ui.tabs(
            {
                _tab_label(_name, _logo): nf.stack(
                    [
                        (_component, [nf.tool(*_svc, height=theme.pt(22), layout="row") for _svc in _services])
                        for _component, _services in _layers.items()
                    ],
                    columns=3,
                    gap=theme.SPACE["tight"],
                )
                for _name, (_logo, _layers) in _PLATFORMS.items()
            }
        ),
        title="Data Platforms",
        pad_top=theme.scale(40),
    )
    return


@app.cell
def _(nf):
    nf.slide(
        nf.tool(
            "Parquet",
            "logos/parquet.svg",
            layout="row",
        ),
        nf.lead(
            "A columnar file format: values for one column sit together on disk, "
            "instead of row by row."
        ),
        nf.bullets(
            [
                "Column-by-column storage means better compression, and a query only reads the columns it actually needs",
                "Files are split into row groups, each carrying per-column stats (min/max) so engines can skip whole chunks that can't match a filter",
                "It's just a file format - no transactions, no built-in idea of which files make up 'the table' right now",
            ]
        ),
        title="Parquet: the file everything else builds on",
        kicker="Data formats",
    )
    return


@app.cell
def _(nf, theme):
    nf.slide(
        nf.two_col(
            nf.tool("Iceberg", "logos/iceberg.svg", layout="row", height=theme.pt(22)),
            nf.tool("Delta Lake", None, layout="row"),
        ),
        nf.lead(
            "A folder of Parquet files has no idea which files are 'current'. "
            "These formats fix that with a transaction log."
        ),
        nf.bullets(
            [
                "Every write appends an entry to a log of metadata files (Delta's _delta_log, Iceberg's manifests) - a reader picks a version and knows exactly which Parquet files belong to it",
                "That log is what buys you ACID transactions, safe concurrent writes, and time travel - query the table as it looked yesterday",
            ]
        ),
        title="Tables, not just files",
        kicker="Data formats",
    )
    return


@app.cell
def _(nf):
    nf.slide(
        nf.bullets(
            [
                "Databricks: Delta Lake is the default table format - Unity Catalog is built around it",
                "Snowflake: 'Iceberg Tables' read and write the open format directly on your own storage",
                "Microsoft Fabric: OneLake stores everything as Delta Parquet, and reads Iceberg via shortcuts",
                "The 'swap the pieces without lock-in' pitch already ships as a checkbox in the platforms you're paying for",
            ]
        ),
        title="Even the managed platforms run on this",
        kicker="Data formats",
    )
    return


@app.cell
def _(nf):
    nf.slide(
        nf.bullets(
            ["Trino", "Airbyte"]
        ),
        title="Data ingestion tools"
    )
    return


@app.cell
def _(nf):
    nf.slide(
        nf.bullets(
            ["Airflow", "Prefect"]
        ),
        title="Orchestration"
    )
    return


@app.cell
def _(nf):
    nf.slide(
        nf.bullets(
            ["spark", "dbt"]
        ),
        title="Transformation"
    )
    return


@app.cell
def _(nf):
    nf.slide(
        title="Data storage"
    )
    return


if __name__ == "__main__":
    app.run()
