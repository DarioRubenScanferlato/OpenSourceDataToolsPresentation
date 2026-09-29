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
    import marimo as mo

    from template import assets, nf, theme

    return assets, mo, nf, theme


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
            - Data sources -> Transform -> Data Store -> Visualization
    - Data platforms and their services (comparison of services: Fabric, Databricks, Snowflake) 2:00
    - OS technologies 20:00
        - postgres 3:00 - https://db-engines.com/en/ranking
        - duckdb 3:00
        - clickhouse 2:00
        - airflow/prefect 1:00
        - data formats (parquet/delta/iceberg) 5:00
        - Data governance
    - Data visualization 7:30
        - pros and cons of power bi - features - values in one filter depend on previous filter
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
    DATA_DIR = Path("data/solar")

    dim_plants = pd.read_csv(DATA_DIR / "dim_plants.csv")
    fact_billing = pd.read_csv(DATA_DIR / "fact_energy_billing.csv")
    fact_maintenance = pd.read_csv(DATA_DIR / "fact_maintenance_events.csv")
    '''
    nf.slide(
        nf.code(_code),
        # A tab per dataframe rather than all three side by side - three
        # wide tables at once didn't fit the slide; one at a time does.
        mo.ui.tabs(
            {
                "dim_plants": nf.dataframe(dashboard.defs["dim_plants"], max_rows=5),
                "fact_billing": nf.dataframe(dashboard.defs["fact_billing"], max_rows=5),
                "fact_maintenance": nf.dataframe(dashboard.defs["fact_maintenance"], max_rows=5),
            }
        ),
        title="Ingesting the raw data",
        kicker="From CSV to dataframe",
        # This slide is denser than most (code + tabs + a table): the
        # template's usual top margin and inter-block rhythm, sized for a
        # sparse title+bullets slide, left this one taller than the frame -
        # buy the room back here instead of shrinking the table further.
        pad_top="5cqw",
        gap="1.2cqw",
    )
    return


@app.cell
def _(dashboard, nf):
    _code = '''
    # join plant names into every fact table once, so charts and filters
    # can work with "location" (plant name) directly
    billing = fact_billing.merge(
        dim_plants[["plant_id", "name", "country_code"]], on="plant_id"
    )
    '''
    nf.slide(
        nf.code(_code),
        nf.dataframe(dashboard.defs["billing"], max_rows=5),
        title="Preparing it for visualization",
        kicker="One join, not a repeated lookup",
    )
    return


@app.cell
def _(dashboard, nf):
    _code = '''
    # one row per (plant, day): that day's total energy, summed across
    # whichever sensors belong to the plant
    daily = billing.groupby(["name", "billing_date"], as_index=False)[
        "energy_generated_kwh"
    ].sum()

    alt.Chart(daily).mark_area(line={"strokeWidth": 1.5}).encode(
        x="billing_date:T",                              # date, on the x-axis
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
    _billing = dashboard.defs["fact_billing"]
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
    date_from = mo.ui.date(value=_billing["billing_date"].min().date())
    date_to = mo.ui.date(value=_billing["billing_date"].max().date())
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
    plant_sel = alt.selection_point(
        fields=["name"], on="click", clear="dblclick", empty="all"
    )

    # added to all four charts, then combined into one Vega-Lite spec
    chart.add_params(plant_sel).encode(
        opacity=alt.condition(plant_sel, alt.value(1.0), alt.value(0.2))
    )
    '''
    nf.slide(
        nf.code(_code),
        nf.bullets(
            [
                "One selection object, reused across the map, the line chart, the sankey and the bar chart",
                "Each chart dims everything except the selected plant via the same opacity condition",
                "Vega-Lite recognizes the shared param and keeps every chart's click state in sync - no callbacks, no server round-trip",
            ]
        ),
        title="Crossfiltering, for free",
        kicker="One selection, four charts",
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
