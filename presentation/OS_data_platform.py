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
            "Currently developing a nature conservation planning app",
            "MSc in Engineering and Management at Politecnico di Torino",
            "Volunteer of the Python Torino user group",
            "Talk to me about recording music, chess, and open-source",
        ],
        page=2,
    )
    return


@app.cell
def _(nf):
    nf.slide(
        title="Is it possible to create great dashboards from raw data using open source technologies?", align='center'
    )
    return


@app.cell
def _():
    return


@app.cell
def _(nf):
    nf.slide(
        nf.lead(
            "Is it possible to build a data platform using open-source tools?"
        ),
        nf.bullets(
            [
                "What do we mean by data platform?",
                "Is it a good idea?",
                "How would you even do it?",
                "Why would it be better than using a proprietary alternative?",
            ]
        ),
        title="In this presentation",
        page=4,
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


@app.cell
def _(nf):
    nf.slide(
        nf.stats(
            [
                ("15m+", "Downloads", "every week"),
                ("1192k+", "Contributions", "every year"),
                ("166+", "Packages", "maintained by us"),
                ("10+", "Years", "of open source at Nearform"),
            ]
        ),
        title="Open source at Nearform",
        kicker="Why us",
        page=5,
    )
    return


@app.cell
def _(nf):
    nf.slide(
        nf.two_col(
            nf.body(
                "Node.js is an open source, cross-platform JavaScript runtime. "
                "Nearform has been instrumental to its development since the "
                "earliest releases."
            ),
            nf.metrics(
                [
                    ("57.3m", "Lines of code changed"),
                    ("25", "Employee contributors"),
                    ("7.1k", "Contributions"),
                    ("7th", "Most active contributor"),
                ]
            ),
            ratio=(3, 2),
        ),
        title="We love Node.js",
        kicker="Nearform OSS",
        page=6,
    )
    return


@app.cell
def _(nf):
    nf.section("What we are building", kicker="OS Data Platform")
    return


@app.cell
def _(nf):
    nf.slide(
        nf.quote(
            "At the heart of Nearform's mission is a profound commitment to the "
            "Node.js ecosystem and the OpenJS Foundation.",
            author="Robin Ginn",
            role="Executive Director, OpenJS Foundation",
        ),
        page=7,
    )
    return


@app.cell
def _(nf):
    nf.slide(
        nf.cards(
            [
                ("Iceberg", "Open table format. Catalog is the hard part."),
                ("DuckDB", "The engine that made local analytics fun again."),
                ("marimo", "This deck. Reactive notebook, reveal.js underneath."),
            ]
        ),
        title="The pieces",
        page=8,
    )
    return


@app.cell
def _(nf):
    nf.slide(
        nf.code(
            """
            import duckdb

            con = duckdb.connect()
            con.sql("INSTALL iceberg; LOAD iceberg;")
            con.sql("SELECT count(*) FROM iceberg_scan('s3://lake/events')")
            """
        ),
        nf.caption("Runs against the local MinIO stack - no cloud account needed."),
        title="Reading the lake",
        page=9,
    )
    return


@app.cell
def _(mo, nf):
    # Anything marimo can render drops straight into a slide.
    _demo = mo.ui.slider(1, 10, value=4, label="partitions")
    nf.slide(_demo, title="Live, on the slide", kicker="Demo", page=10)
    return


@app.cell
def _(nf):
    nf.slide(
        nf.bullets(
            [
                "Nearform Brand Hub - logos, fonts, the full deck template",
                "github.com/nearform - everything we maintain",
                "nearform.com/careers - we're hiring",
            ],
            tone="pale",
        ),
        title="Resources",
        tone="pale",
        page=11,
    )
    return


@app.cell
def _(nf):
    nf.closing("Questions", page=12)
    return


@app.cell
def _():
    # Rebuild layouts/example_deck.slides.json after adding or removing cells.
    # One entry per cell, in order - the first one is the import cell, hence SKIP.
    #
    #     from template import SKIP, Cell, write_slides_layout
    #     write_slides_layout(
    #         "presentation/example_deck.py",
    #         [SKIP, Cell(notes="30s - who I am"), ...],
    #     )
    return


if __name__ == "__main__":
    app.run()
