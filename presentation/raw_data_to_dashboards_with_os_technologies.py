"""From raw data to dashboard with open source software.

Ticino Data Conference, 2026. Speaker notes and slide order live in
``layouts/raw_data_to_dashboards_with_os_technologies.slides.json`` - regenerate it after adding or
removing cells with the script at the bottom of this file (see the last cell).

Run it:      uv run marimo edit presentation/raw_data_to_dashboards_with_os_technologies.py
Present it:  uv run marimo run presentation/raw_data_to_dashboards_with_os_technologies.py --include-code --no-show-tracebacks
"""

import marimo

__generated_with = "0.24.0"
app = marimo.App(
    width="medium",
    layout_file="layouts/raw_data_to_dashboards_with_os_technologies.slides.json",
    css_file="template/nearform.css",
)


@app.cell
def _():
    import altair as alt
    import textwrap

    import marimo as mo
    import pandas as pd

    from template import assets, nf, theme
    from template.race import BarChartRace
    from template.timeline import DateRangeTimeline

    return (
        BarChartRace,
        DateRangeTimeline,
        alt,
        assets,
        mo,
        nf,
        pd,
        textwrap,
        theme,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Index
    - Intro 3:00
        - Title :15
        - Speaker presentation :45
        - Nearform :45
        - Agenda :30
    - From raw data to dashboards 7:00
        - Data sources -> Transform -> Data Store -> Visualization -> cross-filters
    - What is a data platform 1:00
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
        - Coding your own dashboard, using javascript
        - perspective
    - Pros and cons of open source 7:30
        - Decision drivers when deciding between open source or managed data platform
        - Cost - infrastructure/memory/compute/storage, licenses, info from Adriano Sanges talk
            - 47% of developers work in companies <100 employees. Power BI developer probably work in bigger firms
        - Lock-in effects - proprietary software, programming languages
        - Technical skills
        - Flexibility
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
        page=3,
    )
    return


@app.cell
def _(nf):
    nf.slide(
        title="Is it possible to create great dashboards from raw data using open source technologies?", align='center', page=4
    )
    return


@app.cell(hide_code=True)
def data_gate(mo):
    # The raw data isn't committed (data/ is git-ignored): it is generated
    # by the synthetic-data simulator in solar_data_gen/, deterministically
    # (same seed, same files). On a fresh checkout, offer to do that first.
    from solar_data_gen import bronze

    generate_button = mo.ui.run_button(label="Generate the data")
    return bronze, generate_button


@app.cell(hide_code=True)
def ensure_data(bronze, generate_button, mo):
    if not bronze.is_ready():
        mo.stop(
            not generate_button.value,
            mo.callout(
                mo.vstack(
                    [
                        mo.md(
                            "**The solar data isn't generated yet.** It is simulated from "
                            "scratch - 8 plants over two years, hourly - and takes about "
                            "20 seconds. Nothing is downloaded."
                        ),
                        generate_button,
                    ]
                ),
                kind="warn",
            ),
        )
        with mo.status.spinner(title="Generating the solar data..."):
            bronze.generate()
    data_ready = True
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
def _(alt, assets, mo, nf, textwrap, theme):
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

    def scaled_chart(chart, *, width, height):
        """An Altair chart that scales with the slide instead of keeping a
        fixed pixel size (which, in a small window, is taller than the
        slide and scrolls). Drawn at `width` x `height` - axes and legend
        included (`autosize: fit`) - then zoomed to its column's width, the
        same trick as `full_bleed_slide` above."""
        _fit = alt.AutoSizeParams(type="fit", contains="padding")
        # a stacked (vconcat) chart is sized part by part, not as a whole
        fitted = (
            chart.properties(autosize=_fit)
            if hasattr(chart, "vconcat")
            else chart.properties(width=width, height=height, autosize=_fit)
        )
        # no "..." menu: vega-embed pads its wrapper for it, overflowing the column
        with alt.renderers.enable(alt.renderers.active, embed_options={"actions": False}):
            html = mo.as_html(mo.ui.altair_chart(fitted)).text
        return mo.Html(
            f'<div style="container-type:inline-size; width:100%;">'
            f'<div style="width:{width}px; zoom:calc(100cqw / {width}px);">{html}</div></div>'
        )


    def chart_from(code, *, gold, var="chart", width=None, height=None):
        """Run a snippet shown on a slide and hand back the chart it builds,
        so the code on the slide is *exactly* the code that drew the chart.
        A stacked (vconcat) chart gets `width` x `height` per part."""
        scope = {"alt": alt, "gold": gold}
        exec(textwrap.dedent(code), scope)
        chart = scope[var]
        if hasattr(chart, "vconcat"):
            for _part in chart.vconcat:  # in place: copying would detach the shared selection
                _part.width, _part.height = width, height
        return chart

    def chart_step(n, label, code, gold, *, total=5):
        """One sub-slide of the "Plotting a chart" build-up."""
        _lines = len(textwrap.dedent(code).strip().splitlines())
        return nf.slide(
            nf.two_col(
                nf.code(code, size=9 if _lines <= 20 else 8 if _lines <= 28 else 7, fit=47.7),
                scaled_chart(chart_from(code, gold=gold), width=560, height=400),
                ratio=(3, 2),
                gap="2.5cqw",
            ),
            title="Plotting a chart",
            kicker=f"Step {n} of {total}: {label}",
            pad_top="5cqw",
        )

    #: The cross-filtering slides' first chart; the second slide builds on it.
    AREA_CODE = textwrap.dedent('''
        plant_sel = alt.selection_point(fields=["name"], on="click", clear="dblclick")

        area = (
            alt.Chart(gold)
            .mark_area()
            .encode(
                x=alt.X("date:T", title=None),
                y=alt.Y("energy_generated_kwh:Q", title="Energy (kWh)", axis=alt.Axis(format="~s")),
                color=alt.Color("name:N", legend=None),
                # the selected plant stays bright, the rest fade
                opacity=alt.condition(plant_sel, alt.value(0.85), alt.value(0.15)),
            )
            .add_params(plant_sel)
        )
    ''').strip()

    def diagram(name, *, width="100%"):
        """An animated SVG from assets/diagrams/, centred at `width` of the
        column - for a diagram that would be taller than the slide at full
        width. Click one to replay its animation."""
        return mo.Html(
            f'<div style="width:{width}; margin:0 auto;">{assets.svg(name).text}</div>'
        )

    return (
        AREA_CODE,
        chart_from,
        chart_step,
        diagram,
        full_bleed_slide,
        scaled_chart,
    )


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
def _(assets, nf):
    # How the dashboard on the previous slide is built, as one picture - a
    # hand-drawn SVG in assets/diagrams/, inlined so it animates and uses the
    # deck's fonts.
    nf.slide(
        assets.svg("diagrams/dashboard_pipeline.svg"),
        title="How the dashboard is built",
        kicker="Four open-source tools, one notebook",
        pad_top="5cqw",
    )
    return


@app.cell
def _(dashboard, mo, nf):
    # One tab per dataset: what it is, the code that loads it, a few rows.
    # Switching tab switches all three.
    _datasets = {
        "readings": (
            "Contains readings from solar AC power (kW) sensors. "
            "Like real sensors, it has faults: values that get stuck, and dropouts.",
            '''
            readings = pd.read_csv(
                "data/solar/bronze/sensor_readings.csv.gz",
                parse_dates=["timestamp"],
            )
            ''',
            nf.dataframe(dashboard.defs["sensor_readings"], max_rows=3),
        ),
        "sensors": (
            "The sensor register: every sensor and the plant it is installed in. "
            "A reading only names its sensor - this is how it finds its plant.",
            '''
            sensors = pd.read_csv(
                "data/solar/bronze/sensors.csv",
                parse_dates=["install_date"],
            )
            ''',
            nf.dataframe(
                dashboard.defs["sensors"][["sensor_id", "plant_id", "sensor_type", "manufacturer", "model", "install_date"]],
                max_rows=3,
            ),
        ),
        "settlement": (
            "From the grid operator: per plant and day, the energy it metered "
            "and paid for, curtailment, the tariff and the revenue.",
            '''
            settlement = (
                pd.read_csv(
                    "data/solar/bronze/grid_settlement.csv",
                    parse_dates=["settlement_date"],
                )
                .rename(columns={"settlement_date": "date"})
            )
            ''',
            nf.dataframe(dashboard.defs["grid_settlement"], max_rows=3),
        ),
        "plants": (
            "The asset register: where each plant is, its capacity, and when "
            "it was commissioned or shut down.",
            '''
            plants = pd.read_csv(
                "data/solar/bronze/plants.csv",
                parse_dates=["commissioning_date", "decommissioning_date"],
            )
            ''',
            nf.dataframe(dashboard.defs["plants"], max_rows=3),
        ),
    }
    nf.slide(
        mo.ui.tabs(
            {
                _name: mo.vstack(
                    [nf.body(_about), nf.code(_code, size=9, fit=nf.CONTENT_CQW), _table],
                    gap=1,
                )
                for _name, (_about, _code, _table) in _datasets.items()
            }
        ),
        title="Ingesting the raw data",
        kicker="One file per source system, straight into pandas",
        # This slide is denser than most (code + tabs + a table): the
        # template's usual top margin and inter-block rhythm, sized for a
        # sparse title+bullets slide, left this one taller than the frame -
        # buy the room back here instead of shrinking the table further.
        pad_top="5cqw",
        gap="1.2cqw",
    )
    return


@app.cell
def _(assets, mo, theme):
    # Ingesting, fragment: the data model behind the tabs - how the files
    # relate, and the two tables the pipeline derives from them. The slide
    # above is already full, so this is revealed (next click) as a panel
    # *over* the tabs, below the slide's title, rather than under them.
    _tone = theme.TONES["navy"]
    mo.Html(
        # marimo wraps each output in a `position:relative` box - here a
        # zero-height one under the slide. Making just that wrapper static
        # anchors the panel to the slide's own box instead.
        "<style>.output:has(> [data-nf-overlay]) { position: static !important; }</style>"
        f'<div data-nf-overlay style="position:absolute; left:0; right:0; top:19%; bottom:0; z-index:100; '
        # the slide sits 20px in from this box, then pads 8.96% of its own width
        f'background:{theme.NAVY}; padding:0 calc(16.4px + 8.96%) 2.5%; box-sizing:border-box; '
        f'container-type:inline-size; font-family:{theme.SANS}; color:{_tone.fg};">'
        f'<div style="color:{theme.MINT}; font-size:{theme.SIZE["small"]}; font-weight:600; '
        f'text-transform:uppercase; letter-spacing:0.12em; margin-bottom:1.2cqw;">The data model</div>'
        f'{assets.svg("diagrams/data_model.svg").text}'
        "</div>"
    )
    return


@app.cell
def _(alt, dashboard, mo, nf, pd, scaled_chart, theme):
    _code = '''
    power = sensor["ac_power_kw"]  # one sensor, hourly
    hour = sensor["timestamp"].dt.hour

    # stuck: same value as an hour ago
    # (0 at night is normal, so ignore it)
    stuck = power.eq(power.shift(1)) & power.gt(0)
    bad = stuck | power.isna()

    # typical value for each hour of the day:
    # the median of that hour over 7 nearby days
    typical = power.mask(bad).groupby(hour).transform(
        lambda s: s.rolling(7, center=True, min_periods=1).median()
    )

    # keep the good readings, replace the bad ones
    clean = power.mask(bad, typical)
    '''
    # The longest stuck stretch in the data: a flat line that runs through
    # a whole night, with some normal hours around it.
    # each reading's issue, if any, from the cleaning step's own table
    _r = (
        dashboard.defs["readings"]
        .merge(dashboard.defs["reading_issues"], on=["sensor_id", "timestamp"], how="left")
        .fillna({"issue": "ok"})
        .sort_values(["sensor_id", "timestamp"])
    )
    _run = (_r["ac_power_kw"] != _r.groupby("sensor_id")["ac_power_kw"].shift()).cumsum()
    _longest = _run[_r["issue"] == "stuck"].value_counts().idxmax()
    _ep = _r[_run == _longest]
    _sensor = _ep["sensor_id"].iloc[0]
    _lo = _ep["timestamp"].min() - pd.Timedelta(hours=18)
    _hi = _ep["timestamp"].max() + pd.Timedelta(hours=18)
    _win = _r[(_r["sensor_id"] == _sensor) & _r["timestamp"].between(_lo, _hi)]
    _bad = _win[_win["issue"] != "ok"]
    _ymax = float(max(_win["ac_power_kw"].max(), _win["ac_power_kw_clean"].max())) * 1.05

    _lines = pd.concat(
        [
            _win.assign(series="Raw reading", kw=_win["ac_power_kw"]),
            # only the hours we replaced, with the value we put there
            _bad.assign(series="Imputed value", kw=_bad["ac_power_kw_clean"]),
        ]
    )
    # the bad hours themselves, as a shaded band behind the lines
    _bands = _bad.assign(
        series=_bad["issue"].map({"stuck": "Stuck hour", "missing": "Missing hour"}),
        end=_bad["timestamp"] + pd.Timedelta(hours=1),
        lo=0.0,
        hi=_ymax,
    )
    _series = ["Raw reading", "Imputed value", "Stuck hour", "Missing hour"]
    _color = alt.Color(
        "series:N",
        title=None,
        scale=alt.Scale(domain=_series, range=["#8F9AB8", theme.MINT, "#FF7A8A", theme.LAVENDER]),
        legend=alt.Legend(orient="top", direction="horizontal", symbolOpacity=1),
    )
    _x = alt.X("timestamp:T", title=None, axis=alt.Axis(format="%b %d %H:%M", labelAngle=0, tickCount=4))
    _y = alt.Y("kw:Q", title="AC power (kW)", scale=alt.Scale(domain=[0, _ymax], nice=False))
    _chart = (
        alt.Chart(_bands)
        .mark_rect(opacity=0.22)
        .encode(x=_x, x2="end:T", y=alt.Y("lo:Q", axis=None), y2="hi:Q", color=_color)
        + alt.Chart(_lines)
        .mark_line(strokeWidth=2, point=alt.OverlayMarkDef(size=18, filled=True))
        .encode(x=_x, y=_y, color=_color)
    ).properties(title=_sensor)
    nf.slide(
        nf.two_col(
            mo.vstack(
                [
                    nf.code(_code, size=9, fit=39.8),
                    nf.bullets(
                        [
                            "Missing: the sensor sent nothing (NaN)",
                            "Stuck: the same reading, hour after hour",
                            "Fix: use the typical value for that hour over the nearby days - nights stay 0, nothing is left empty",
                        ]
                    ),
                ],
                gap=1.5,
            ),
            scaled_chart(_chart, width=520, height=320),
            ratio=(1, 1),
            gap="2.5cqw",
        ),
        title="Cleaning data",
        kicker="Imputing values for broken sensors",
        pad_top="5cqw",
    )
    return


@app.cell
def _(dashboard, nf):
    _code = '''
    gold = (
        readings
        # 1. which plant is each sensor in? the sensor register knows
        .merge(sensors[["sensor_id", "plant_id"]], on="sensor_id")
        # 2. one energy number per plant per day (an hourly kW reading = kWh)
        .assign(date=lambda d: d["timestamp"].dt.normalize())
        .groupby(["plant_id", "date"], as_index=False)
        .agg(energy_generated_kwh=("ac_power_kw_clean", "sum"))
        # 3. attach what the grid operator measured and paid that day
        .merge(settlement, on=["plant_id", "date"])
        # 4. attach each plant's name and size
        .merge(plants[["plant_id", "name", "capacity_mw"]], on="plant_id")
        # 5. work out what was used on site: what we generated, minus what
        #    went to the grid, minus what the grid made us throw away
        .assign(
            self_consumption_kwh=lambda d: (
                d["energy_generated_kwh"] - d["energy_exported_kwh"] - d["curtailment_kwh"]
            ).clip(lower=0)
        )
    )
    '''
    _cols = [
        "date", "name", "energy_generated_kwh", "energy_exported_kwh",
        "curtailment_kwh", "self_consumption_kwh", "revenue_eur",
    ]
    nf.slide(
        nf.code(_code, size=8, fit=nf.CONTENT_CQW),
        nf.dataframe(dashboard.defs["gold"][_cols], max_rows=2),
        title="From bronze to gold",
        kicker="Step 2: aggregate, join, derive",
        pad_top="5cqw",
        gap="1.2cqw",
    )
    return


@app.cell
def _(chart_step, dashboard):
    chart_step(
        1,
        "the simplest chart",
        '''
        chart = alt.Chart(gold).mark_line().encode(
            x="date:T",  # T: temporal - a time axis
            y="energy_generated_kwh:Q",  # Q: quantitative
            color="name:N",  # N: nominal - one colour per plant
        )
        ''',
        dashboard.defs["gold"],
    )
    return


@app.cell
def _(chart_step, dashboard):
    chart_step(
        2,
        "stack the plants into areas",
        '''
        chart = alt.Chart(gold).mark_area().encode(  # lines -> filled areas
            x="date:T",
            y=alt.Y(
                "energy_generated_kwh:Q",
                stack="zero",  # plants stacked on top of each other
            ),
            color="name:N",
        )
        ''',
        dashboard.defs["gold"],
    )
    return


@app.cell
def _(chart_step, dashboard):
    chart_step(
        3,
        "titles, outline and smooth curves",
        '''
        chart = (
            alt.Chart(gold)
            .mark_area(
                line={"strokeWidth": 1.5},  # a line on top of each area
                interpolate="monotone",  # smooth curves
            )
            .encode(
                x=alt.X("date:T", title=None, axis=alt.Axis(format="%b %Y")),
                y=alt.Y(
                    "energy_generated_kwh:Q",
                    title="Energy generated (kWh)",
                    stack="zero",
                    axis=alt.Axis(format="~s"),  # 2.2M, not 2200000
                ),
                color=alt.Color("name:N", legend=None),
                order=alt.Order("name:N"),  # same stacking order always
            )
            .properties(title="Daily energy production by plant")
        )
        ''',
        dashboard.defs["gold"],
    )
    return


@app.cell
def _(chart_step, dashboard):
    chart_step(
        4,
        "tooltips on hover",
        '''
        chart = (
            alt.Chart(gold)
            .mark_area(line={"strokeWidth": 1.5}, interpolate="monotone")
            .encode(
                x=alt.X("date:T", title=None, axis=alt.Axis(format="%b %Y")),
                y=alt.Y(
                    "energy_generated_kwh:Q",
                    title="Energy generated (kWh)",
                    stack="zero",
                    axis=alt.Axis(format="~s"),
                ),
                color=alt.Color("name:N", legend=None),
                order=alt.Order("name:N"),
                tooltip=[  # what to show when hovering
                    alt.Tooltip("name:N", title="Plant"),
                    alt.Tooltip("date:T", title="Date"),
                    alt.Tooltip("energy_generated_kwh:Q", title="kWh", format=",.0f"),
                ],
            )
            .properties(title="Daily energy production by plant")
        )
        ''',
        dashboard.defs["gold"],
    )
    return


@app.cell
def _(chart_step, dashboard):
    chart_step(
        5,
        "grid, ticks and the finishing touches",
        '''
        chart = (
            alt.Chart(gold)
            .mark_area(line={"strokeWidth": 1.5}, interpolate="monotone")
            .encode(
                x=alt.X(
                    "date:T",
                    title=None,
                    axis=alt.Axis(
                        format="%b %Y",
                        tickCount={"interval": "month", "step": 3},  # quarterly
                        grid=True,  # vertical grid lines
                    ),
                ),
                y=alt.Y(
                    "energy_generated_kwh:Q",
                    title="Energy generated (kWh)",
                    stack="zero",
                    axis=alt.Axis(format="~s"),
                    impute=alt.ImputeParams(value=0),  # no row = 0 kWh
                ),
                color=alt.Color("name:N", legend=None),
                order=alt.Order("name:N"),
                opacity=alt.value(0.85),  # let the grid show through
                tooltip=[
                    alt.Tooltip("name:N", title="Plant"),
                    alt.Tooltip("date:T", title="Date"),
                    alt.Tooltip("energy_generated_kwh:Q", title="kWh", format=",.0f"),
                ],
            )
            .properties(title="Daily energy production by plant")
        )
        ''',
        dashboard.defs["gold"],
    )
    return


@app.cell
def _(DateRangeTimeline, dashboard, mo, pd, theme):
    # Fresh widgets, not the *same* objects as the dashboard slide: a
    # marimo UI element is bound to exactly one live DOM mount, so
    # displaying `dashboard.defs["location_filter"]` a second time here
    # would leave an inert copy. These are independent of the dashboard's
    # own filters. (A UI element's `.value` can't be read in the cell that
    # creates it, hence the split from the slide cells below.)
    _plants = dashboard.defs["dim_plants"]
    _gold = dashboard.defs["gold"]

    slider = mo.ui.slider(start=1, stop=10, value=5, show_value=True)

    _short = {n.removesuffix(" Solar Farm"): n for n in sorted(_plants["name"])}
    location_filter = mo.ui.multiselect(options=_short, value=list(_short))

    _first, _last = _gold["date"].min(), _gold["date"].max()
    _daily = (
        _gold.groupby("date")["energy_generated_kwh"].sum()
        .reindex(pd.date_range(_first, _last, freq="D"), fill_value=0)
    )
    _tone = theme.TONES["navy"]
    period_filter = mo.ui.anywidget(
        DateRangeTimeline(
            start=_first.date().isoformat(),
            end=_last.date().isoformat(),
            min_date=_first.date().isoformat(),
            max_date=_last.date().isoformat(),
            values=[float(v) for v in _daily],
            width=760,
            label="Period",
            colors={"accent": theme.MINT, "fg": _tone.fg, "muted": _tone.muted, "rule": _tone.rule, "bg": theme.NAVY},
        )
    )
    return location_filter, period_filter, slider


@app.cell
def _(mo, nf, slider):
    _code = '''
    import marimo as mo

    slider = mo.ui.slider(start=1, stop=10, value=5, show_value=True)
    slider  # shown as a widget

    # any cell that reads .value re-runs when you move it
    mo.md(f"The slider is at **{slider.value}**")
    '''
    # `.dark`: marimo's widgets pick their palette from a `.dark` ancestor,
    # and this notebook's own display theme is light - without it the
    # controls render light-on-light on the navy slide.
    nf.slide(
        nf.code(_code, size=10, fit=nf.CONTENT_CQW),
        mo.Html(f'<div class="dark" style="zoom:1.6; transform-origin:left;">{mo.as_html(slider).text}</div>'),
        nf.body(f"The slider is at **{slider.value}** - move it and this line updates."),
        title="Adding filters with marimo ui elements",
        kicker="Step 1: a slider",
        pad_top="5cqw",
        gap="1.2cqw",
    )
    return


@app.cell
def _(location_filter, mo, nf):
    _code = '''
    plant_names = {
        name.removesuffix(" Solar Farm"): name  # short label -> full value
        for name in sorted(plants["name"])
    }

    location_filter = mo.ui.multiselect(
        options=plant_names,
        value=list(plant_names),  # everything selected to start
    )
    location_filter

    location_filter.value  # the list of selected plants
    '''
    # `wrap=True` is load-bearing: with all 8 plants selected the chip row
    # is wide, and unwrapped it pushed past the slide's right edge.
    nf.slide(
        nf.code(_code, size=9, fit=nf.CONTENT_CQW),
        mo.Html(f'<div class="dark" style="zoom:1.4;">{mo.as_html(mo.hstack([location_filter], justify="start", wrap=True)).text}</div>'),
        nf.body(
            f"**{len(location_filter.value)} plants selected:** "
            + ", ".join(location_filter.value)
        ),
        title="Adding filters with marimo ui elements",
        kicker="Step 2: a multiselect",
        pad_top="5cqw",
        gap="1.2cqw",
    )
    return


@app.cell
def _(mo, nf, period_filter):
    _code = '''
    from template.timeline import DateRangeTimeline  # a small anywidget

    # the strip behind the handles: total energy per day
    daily_energy = gold.groupby("date")["energy_generated_kwh"].sum()

    period_filter = mo.ui.anywidget(
        DateRangeTimeline(
            start=first_day, end=last_day,  # the selected range
            min_date=first_day, max_date=last_day,  # the whole timeline
            values=daily_energy,
            label="Period",
        )
    )
    period_filter  # drag either handle, or the range between them

    period_filter.value  # {"start": "2024-09-21", "end": "2026-09-20", ...}
    '''
    # The widget has a fixed pixel width; scale it to the slide like the
    # charts (see scaled_chart above).
    _w = 760
    _widget = (
        f'<div class="dark" style="container-type:inline-size; width:100%;">'
        f'<div style="width:{_w}px; zoom:calc(100cqw / {_w}px);">'
        f"{mo.as_html(period_filter).text}</div></div>"
    )
    nf.slide(
        nf.code(_code, size=9, fit=nf.CONTENT_CQW),
        mo.Html(_widget),
        nf.body(
            f"Selected: **{period_filter.value['start']}** to **{period_filter.value['end']}**"
        ),
        title="Adding filters with marimo ui elements",
        kicker="Step 3: a date range - the one in the dashboard",
        pad_top="5cqw",
        gap="1.2cqw",
    )
    return


@app.cell
def _(AREA_CODE, chart_from, dashboard, mo, nf, scaled_chart):
    _chart = chart_from(AREA_CODE, var="area", gold=dashboard.defs["gold"])
    nf.slide(
        nf.two_col(
            mo.vstack(
                [
                    nf.code(AREA_CODE + "\narea  # click a band: the selected plant stays bright", size=9, fit=47.7),
                    nf.bullets(
                        [
                            "A selection object remembers which plant you clicked",
                            "Marks react through a condition: selected stays bright, the rest fade",
                        ]
                    ),
                ],
                gap=1.5,
            ),
            scaled_chart(_chart, width=560, height=330),
            ratio=(3, 2),
            gap="2.5cqw",
        ),
        title="Cross-filtering",
        kicker="Step 1: a selection on one chart",
        pad_top="5cqw",
    )
    return


@app.cell
def _(AREA_CODE, chart_from, dashboard, mo, nf, scaled_chart):
    _new = '''
    # a second chart, reusing the same selection object
    bars = (
        alt.Chart(gold)
        .mark_bar()
        .encode(
            x=alt.X("sum(revenue_eur):Q", title="Revenue (EUR)", axis=alt.Axis(format="~s")),
            y=alt.Y("name:N", sort="-x", title=None),
            color=alt.Color("name:N", legend=None),
            opacity=alt.condition(plant_sel, alt.value(0.85), alt.value(0.15)),
        )
        .add_params(plant_sel)
    )

    chart = area & bars  # stacked: one click updates both
    '''
    _chart = chart_from(AREA_CODE + _new, gold=dashboard.defs["gold"], width=340, height=150)
    nf.slide(
        nf.two_col(
            mo.vstack(
                [
                    nf.code(_new, size=9, fit=47.7),
                    nf.bullets(
                        [
                            "Same plant_sel, added to both charts: click a bar or an area and both react",
                            "Double-click to clear",
                        ]
                    ),
                ],
                gap=1.5,
            ),
            scaled_chart(_chart, width=520, height=340),
            ratio=(3, 2),
            gap="2.5cqw",
        ),
        title="Cross-filtering",
        kicker="Step 2: share it with a second chart",
        pad_top="5cqw",
    )
    return


@app.cell
def _(mo, nf):
    nf.slide(
        nf.two_col(
            left=nf.bullets(
                [
                    "I need to share this dashboard with my colleagues?",
                    "I need to secure the app with authentication and different permission levels?",
                    "I need to scale to TB of data?",
                    "I need to refresh the data daily?"
                ]
            ),
            right=mo.image(src='https://i.imgflip.com/b2gpbs.jpg', rounded=True)
        ),

        title="What if..."
    )
    return


@app.cell
def _(assets, nf):
    # What a data platform is, as one picture rather than a list: the data
    # path left to right (ingest, store, transform, visualize), orchestration
    # over it, observability and governance across it, dev tooling and
    # infrastructure under it.
    nf.slide(
        assets.svg("diagrams/data_platform.svg"),
        title="Data platform? What do you mean?",
        pad_top="5cqw",
    )
    return


@app.cell
def _(assets, mo, nf, theme):
    # Pick a platform to see how it fills in the components from the previous slide.
    # (name, logo, note) per component. Drop logo files into presentation/assets/logos/
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
                        (_component, [nf.tool(_svc[0], _svc[1] if assets.exists(_svc[1]) else _logo, *_svc[2:], height=theme.pt(22), layout="row") for _svc in _services])
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
    nf.slide(title="Can we build a data platform through open source technologies?")
    return


@app.cell
def _(assets, nf):
    # Parquet, 1 of 3: the same rows stored row by row vs column by column,
    # raced by one query. Click the diagram to replay it.
    nf.slide(
        assets.svg("diagrams/parquet_columnar.svg"),
        nf.body(
            "A query reads **only the columns it asks for** (*projection pushdown*) - "
            "on a wide table that is often 5% of the file, not 100%."
        ),
        title="Parquet: a compressed columnar file format",
        kicker="Data formats",
        pad_top="5cqw",
    )
    return


@app.cell
def _(diagram, nf):
    # Parquet, 2 of 3: row groups, column chunks and the footer's min/max
    # statistics - how a filter skips most of the file without reading it.
    nf.slide(
        diagram("diagrams/parquet_anatomy.svg", width="88%"),
        nf.body(
            "*Predicate pushdown* - and it works best when the data is sorted by what you filter on."
        ),
        title="Skipping what you don't need",
        kicker="Parquet - inside the file",
        pad_top="5cqw",
    )
    return


@app.cell
def _(assets, dashboard, nf):
    import io

    import pyarrow.parquet as pq

    # Parquet, 3 of 3: the encodings, then the same thing measured on the
    # sensor readings from the dashboard - written to Parquet in memory, so
    # nothing lands on disk.
    _raw = dashboard.defs["sensor_readings"]
    _csv_bytes = len(_raw.to_csv(index=False).encode())
    _buf = io.BytesIO()
    _raw.to_parquet(_buf, compression="zstd", index=False)
    _pq_bytes = _buf.tell()
    _meta = pq.ParquetFile(io.BytesIO(_buf.getvalue())).metadata
    _sensor_col = _raw.columns.get_loc("sensor_id")
    _sensor_pq = sum(
        _meta.row_group(_g).column(_sensor_col).total_compressed_size
        for _g in range(_meta.num_row_groups)
    )
    _sensor_csv = int(_raw["sensor_id"].str.len().sum()) + len(_raw)  # + one comma each


    def _size(n):
        for _unit in ("B", "KB", "MB", "GB"):
            if n < 1000:
                return f"{n:.3g} {_unit}"
            n /= 1000
        return f"{n:.3g} TB"


    nf.slide(
        assets.svg("diagrams/parquet_encoding.svg"),
        nf.stats(
            [
                (f"{_size(_csv_bytes)} → {_size(_pq_bytes)}", "sensor readings: CSV vs Parquet",
                 f"{_csv_bytes / _pq_bytes:.0f}x smaller, {len(_raw):,} rows"),
                (f"{_size(_sensor_csv)} → {_size(_sensor_pq)}", "the sensor_id column alone",
                 f"{_raw['sensor_id'].nunique()} distinct values, long runs"),
                ("typed", "schema in the file", "no more parsing dates from strings"),
            ]
        ),
        title="Encoding and compression",
        kicker="Parquet - why the files are small",
        pad_top="5cqw",
    )
    return


@app.cell
def _(diagram, nf):
    # Table formats, 1 of 3: Delta Lake's transaction log, as a five-scene
    # story - insert, insert, update, a crashed writer, time travel.
    nf.slide(
        diagram("diagrams/delta_log.svg"),
        title="Delta Lake: ACID transactions on a folder of Parquet files",
        kicker="Data formats - table formats",
        pad_top="4.5cqw",
        gap="1.6cqw",
    )
    return


@app.cell
def _(diagram, nf):
    # Table formats, 2 of 3: Iceberg's metadata tree - the same guarantees,
    # with a catalog pointer as the commit.
    nf.slide(
        diagram("diagrams/iceberg_snapshots.svg"),
        title="Iceberg: the table is a tree of snapshots",
        kicker="Data formats - table formats",
        pad_top="5cqw",
    )
    return


@app.cell
def _(mo, nf, theme):
    # Table formats, 3 of 3: what they share, where they differ, and what
    # time travel looks like in code.
    def _side(name, logo, note, points, snippet, language):
        return mo.vstack(
            [
                nf.tool(name, logo, note=note, layout="row", height=theme.pt(24)),
                nf.bullets(points, size=theme.SIZE["small"]),
                nf.code(snippet, language=language, size=9, fit=(nf.CONTENT_CQW - 2.5) / 2),
            ],
            gap=0.8,
        )

    nf.slide(
        nf.two_col(
            _side(
                "Delta Lake",
                "logos/delta-lake.svg",
                "Linux Foundation · born at Databricks",
                [
                    "A log of JSON commits, checkpointed to Parquet",
                    "The default in Databricks and Microsoft Fabric",
                    "deltalake (delta-rs): read and write it from plain Python",
                ],
                '''
                from deltalake import DeltaTable, write_deltalake

                t = "s3://lake/readings"
                write_deltalake(t, readings)                 # v0
                write_deltalake(t, fixed, mode="overwrite")  # v1

                DeltaTable(t, version=0).to_pandas()  # back to v0
                ''',
                "python",
            ),
            _side(
                "Apache Iceberg",
                "logos/iceberg.svg",
                "Apache Software Foundation · born at Netflix",
                [
                    "A metadata tree behind a catalog (REST spec)",
                    "Hidden partitioning, and partitions can change later",
                    "The widest engine support: Spark, Trino, Flink, DuckDB, Snowflake",
                ],
                '''
                -- Trino: time travel by snapshot id...
                SELECT * FROM lake.readings
                FOR VERSION AS OF 8744736658442914487;

                -- ...or by point in time
                SELECT * FROM lake.readings
                FOR TIMESTAMP AS OF
                    TIMESTAMP '2026-06-01 00:00:00 UTC';
                ''',
                "sql",
            ),
            gap="2.5cqw",
        ),
        nf.body(
            "**Both:** ACID transactions · time travel · schema evolution · MERGE / upserts · "
            "open specs on top of Parquet - and converging (Delta *UniForm* also writes Iceberg metadata)."
        ),
        title="Delta Lake or Iceberg?",
        kicker="Data formats - table formats",
        pad_top="4.5cqw",
        gap="1.4cqw",
    )
    return


@app.cell
def _(mo, nf, theme):
    # Back to the platforms slide: each one's storage layer is one of the
    # open table formats from the last few slides.
    _rows = [
        ("Databricks", "logos/databricks.svg", "Delta Lake", "logos/delta-lake.svg",
         "the default table format - Unity Catalog is built around it"),
        ("Snowflake", "logos/snowflake.svg", "Iceberg", "logos/iceberg.svg",
         "Iceberg Tables: the open format, on your own storage"),
        ("Microsoft Fabric", "logos/fabric.svg", "Delta Lake", "logos/delta-lake.svg",
         "OneLake stores every table as Delta Parquet, and reads Iceberg via shortcuts"),
    ]
    _tone = theme.TONES["navy"]
    _cells = "".join(
        mo.as_html(nf.tool(_platform, _plogo, layout="row", height=theme.pt(26))).text
        + f'<div style="color:{theme.MINT}; font-size:{theme.SIZE["heading"]}; text-align:center;">&rarr;</div>'
        + mo.as_html(nf.tool(_format, _flogo, layout="row", height=theme.pt(26))).text
        + f'<div style="color:{_tone.muted}; font-size:{theme.SIZE["small"]}; line-height:1.4;">{_note}</div>'
        for _platform, _plogo, _format, _flogo, _note in _rows
    )
    nf.slide(
        mo.Html(
            f'<div style="display:grid; grid-template-columns:auto auto auto 1fr; align-items:center; '
            f'gap:{theme.SPACE["gap"]} {theme.SPACE["gap"]}; padding-top:{theme.SPACE["gap_sm"]};">{_cells}</div>'
        ),
        nf.lead("Learn the open formats once: they are what the managed platforms store your data in, too."),
        title="Even the managed platforms run on this",
        kicker="Data formats",
        gap=theme.SPACE["gap_lg"],
    )
    return


@app.cell
def _(diagram, nf):
    # Ingestion: copy the data in (Airbyte) or query it where it is (Trino).
    nf.slide(
        diagram("diagrams/ingestion.svg"),
        title="Getting the data in",
        kicker="Ingestion - move it, or query it in place",
        pad_top="5cqw",
    )
    return


@app.cell
def _(diagram, nf):
    # Orchestration, 1 of 3: the dashboard's own pipeline as a DAG - the
    # answer to "I need to refresh the data daily". Click to replay the run.
    nf.slide(
        diagram("diagrams/orchestration.svg"),
        nf.body(
            "Schedules · dependencies · retries · backfills · alerts · logs - "
            "and one UI that shows every run."
        ),
        title="Orchestration: who runs the pipeline at 6 am?",
        kicker="Orchestration",
        pad_top="5cqw",
    )
    return


@app.cell
def _(assets, mo, nf, theme):
    # Orchestration, 2 of 3: Airflow - its Grid view (task x run, coloured by
    # state) and the same pipeline as a DAG file.
    nf.slide(
        nf.two_col(
            mo.vstack(
                [
                    assets.img(
                        "images/airflow-grid.png",
                        alt="Airflow 3 Grid view",
                        # the left half: task names x runs; the overview panel is noise here
                        style={"aspect-ratio": "1500 / 960", "object-fit": "cover", "object-position": "left top"},
                    ),
                    nf.caption("The Grid view: every task of every run, coloured by state. Airflow 3 UI, from the Airflow docs."),
                ],
                gap=0.4,
            ),
            mo.vstack(
                [
                    nf.code(
                        '''
                        from airflow.sdk import dag, task

                        @dag(schedule="@daily", catchup=False)
                        def solar_pipeline():
                            @task(retries=3)
                            def extract(source): ...

                            @task
                            def build_gold(paths): ...

                            @task
                            def refresh_dashboard(gold): ...

                            raw = extract.expand(
                                source=["readings", "settlement", "plants"]
                            )
                            refresh_dashboard(build_gold(raw))

                        solar_pipeline()
                        ''',
                        size=8,
                        fit=(nf.CONTENT_CQW - 2.5) / 2,
                    ),
                ]
            ),
            ratio=(1, 1),
            gap="2.5cqw",
        ),
        nf.bullets(
            [
                "The industry standard: born at Airbnb in 2014, now an Apache top-level project",
                "Integrations for every cloud and database; run for you by AWS, Google, Astronomer",
                "Airflow 3 (2025): a new UI, DAG versioning, data-aware scheduling",
            ],
            size=theme.SIZE["small"],
        ),
        title="Apache Airflow",
        kicker="Orchestration",
        pad_top="4.5cqw",
        gap="1.4cqw",
    )
    return


@app.cell
def _(assets, mo, nf, theme):
    # Orchestration, 3 of 3: Prefect - a flow run's timeline graph, and the
    # same pipeline as plain decorated Python.
    _shot = assets.img(
        "images/prefect-flow-run.png",
        alt="Prefect flow run page",
        # the screenshot's bottom half is the log list: show the run graph only
        style={"aspect-ratio": "2036 / 790", "object-fit": "cover", "object-position": "top"},
    )
    nf.slide(
        nf.two_col(
            mo.vstack(
                [_shot, nf.caption("A flow run: tasks on a timeline, with their dependencies. From the Prefect docs.")],
                gap=0.4,
            ),
            nf.code(
                '''
                from prefect import flow, task

                @task(retries=3, retry_delay_seconds=60)
                def extract(source): ...

                @task
                def build_gold(readings, settlement, plants): ...

                @flow(log_prints=True)
                def solar_pipeline():
                    raw = [extract(s) for s in SOURCES]
                    refresh_dashboard(build_gold(*raw))

                if __name__ == "__main__":
                    solar_pipeline.serve(cron="0 6 * * *")
                ''',
                size=9,
                fit=(nf.CONTENT_CQW - 2.5) / 2,
            ),
            ratio=(1, 1),
            gap="2.5cqw",
        ),
        nf.bullets(
            [
                "Just Python: decorate the functions you already have with @flow and @task",
                "Dynamic: branch and loop with plain if and for - no graph to declare up front",
                "Runs as a normal script on your laptop; self-host the server or use Prefect Cloud",
            ],
            size=theme.SIZE["small"],
        ),
        title="Prefect",
        kicker="Orchestration",
        pad_top="4.5cqw",
        gap="1.4cqw",
    )
    return


@app.cell
def _(diagram, nf):
    # Transformation: Spark when the data outgrows one machine, dbt for
    # SQL transformations managed like software.
    nf.slide(
        diagram("diagrams/transformation.svg"),
        title="Transformation",
        kicker="Spark for scale, dbt for SQL people",
        pad_top="5cqw",
    )
    return


@app.cell
def _(diagram, nf):
    # Engines, 1 of 4: the three shapes side by side; the sub-slides take one
    # engine each.
    nf.slide(
        diagram("diagrams/engines.svg"),
        title="Storing and querying the data",
        kicker="Storage and query engines",
        pad_top="5cqw",
    )
    return


@app.cell
def _(assets, mo, nf, theme):
    # Engines, 2 of 4: Postgres. Survey numbers: Stack Overflow Developer
    # Survey 2025 (survey.stackoverflow.co/2025/technology); DB-Engines'
    # DBMS of the Year (db-engines.com/en/blog_post/106).
    nf.slide(
        nf.two_col(
            assets.svg("diagrams/postgres_extensions.svg"),
            mo.vstack(
                [
                    nf.stats(
                        [("55.6%", "of developers use it", "#1 database, Stack Overflow survey 2025"),
                         ("4x", "DBMS of the Year", "DB-Engines: 2017, 2018, 2020, 2023")],
                        columns=2,
                    ),
                    nf.bullets(
                        [
                            "Transactions, constraints, rich SQL - boringly reliable",
                            "Extensions make it a geo, vector or time-series database",
                            "Permissive licence, no single vendor: the community owns it",
                            "**But** a row store: slow for big analytical scans - remember the Parquet race",
                        ],
                        size=theme.SIZE["small"],
                    ),
                ],
                gap=1.2,
            ),
            ratio=(1, 1),
            gap="2.5cqw",
            align="center",
        ),
        title="PostgreSQL: the default database",
        kicker="Storage and query engines",
        pad_top="4.5cqw",
    )
    return


@app.cell
def _(mo):
    # The DuckDB slide's editor. Created here, shown on the next slide: a UI
    # element's value can't be read in the cell that creates it.
    duckdb_sql = mo.ui.code_editor(
        value=(
            "-- two raw files, joined in place: no server\n"
            "SELECT s.plant_id,\n"
            "       count(*) AS readings,\n"
            "       round(sum(r.ac_power_kw) / 1e3) AS mwh\n"
            "FROM 'data/solar/bronze/sensor_readings.csv.gz' r\n"
            "JOIN 'data/solar/bronze/sensors.csv' s\n"
            "  USING (sensor_id)\n"
            "GROUP BY ALL\n"
            "ORDER BY mwh DESC"
        ),
        language="sql",
        theme="dark",
        min_height=170,
    )
    return (duckdb_sql,)


@app.cell
def _(bronze, dashboard, duckdb_sql, mo, nf):
    import time

    import duckdb

    # Engines, 3 of 4: DuckDB, live. The query runs in this notebook's own
    # process on every edit - against the raw CSV, or `gold`, the
    # dashboard's DataFrame, registered as a table.
    _editor_w = 450
    _con = duckdb.connect()
    _con.execute(f"SET file_search_path = '{bronze.BRONZE_DIR.parents[2].as_posix()}'")
    _con.register("gold", dashboard.defs["gold"])
    _t0 = time.perf_counter()
    try:
        _df = _con.sql(duckdb_sql.value).df()
        _ms = (time.perf_counter() - _t0) * 1000
        _result = nf.dataframe(
            _df, max_rows=8, label=f"{len(_df):,} rows in {_ms:,.0f} ms - inside this Python process"
        )
    except duckdb.Error as _e:
        _result = mo.callout(mo.md(f"`{type(_e).__name__}`: {_e}"), kind="danger")
    finally:
        _con.close()

    nf.slide(
        nf.two_col(
            mo.vstack(
                [
                    # fixed-pixel widget: scale it to the column, like the charts
                    mo.Html(
                        f'<div style="container-type:inline-size; width:100%;">'
                        f'<div style="width:{_editor_w}px; zoom:calc(100cqw / {_editor_w}px);">'
                        f"{mo.as_html(duckdb_sql).text}</div></div>"
                    ),
                    nf.caption("Edit me - it re-runs. Also try: SELECT * FROM gold"),
                ],
                gap=0.4,
            ),
            _result,
            ratio=(1, 1),
            gap="2.5cqw",
        ),
        nf.cards(
            [
                ("In-process", "pip install duckdb: no server - SQLite for analytics"),
                ("Reads everything", "Parquet, CSV, JSON, Iceberg, Delta; local or S3"),
                ("Fast on one machine", "columnar, vectorized, larger-than-memory"),
            ]
        ),
        title="DuckDB: an analytical database in your process",
        kicker="Storage and query engines - live",
        pad_top="4.5cqw",
        gap="1.4cqw",
    )
    return duckdb, time


@app.cell
def _(assets, nf, theme):
    # Engines, 4 of 4: ClickHouse - MergeTree on the left, why it's fast on
    # the right.
    nf.slide(
        nf.two_col(
            assets.svg("diagrams/clickhouse_mergetree.svg"),
            nf.bullets(
                [
                    "**Real-time analytics:** sub-second queries over billions of rows, for many users at once",
                    "**Columnar, compressed, vectorized** - the Parquet ideas, inside a server",
                    "**MergeTree:** inserts land as small sorted parts, merged in the background",
                    "**Sparse primary index:** skips blocks of rows, like Parquet's row groups",
                    "**Materialized views** update as the data arrives",
                    "Apache 2.0 - self-host it, or use ClickHouse Cloud",
                ],
                size=theme.SIZE["small"],
            ),
            ratio=(1, 1),
            gap="2.5cqw",
            align="center",
        ),
        title="ClickHouse: analytics at scale, in real time",
        kicker="Storage and query engines",
        pad_top="4.5cqw",
    )
    return


@app.cell
def _(mo, nf, theme):
    # Dataviz, overview: the ecosystem as a spectrum, from clicking to
    # coding. Logos come from assets/logos/; a missing one falls back to an
    # initials chip.
    _layers = [
        ("BI apps · click, don't code", [
            ("Apache Superset", "logos/superset.svg"), ("Metabase", "logos/metabase.svg"),
            ("Grafana", "logos/grafana.svg"), ("Lightdash", "logos/lightdash.svg"),
            ("Redash", "logos/redash.svg"),
        ]),
        ("Dashboards as code", [
            ("Streamlit", "logos/streamlit.svg"), ("Dash", "logos/plotly.svg"),
            ("marimo", "logos/marimo.png"), ("Evidence", "logos/evidence.svg"),
            ("Observable Framework", "logos/observable.svg"),
        ]),
        ("Chart libraries", [
            ("Altair · Vega-Lite", "logos/altair.svg"), ("Plotly", "logos/plotly.svg"),
            ("D3", "logos/d3.svg"), ("ECharts", "logos/echarts.svg"),
            ("Bokeh", "logos/bokeh.svg"), ("Matplotlib", "logos/matplotlib.svg"),
        ]),
        ("In the browser · WASM, GPU", [
            ("Perspective", "logos/perspective.svg"), ("DuckDB-WASM", "logos/duckdb.svg"),
            ("deck.gl", "logos/deckgl.svg"), ("Pyodide", "logos/pyodide.svg"),
        ]),
    ]
    _tone = theme.TONES["navy"]
    _spectrum = mo.Html(
        f'<svg viewBox="0 0 800 30" width="100%" style="display:block; font-family:inherit;">'
        f'<defs><linearGradient id="viz-spectrum" x1="0" x2="1"><stop offset="0" stop-color="{theme.LAVENDER}"/>'
        f'<stop offset="1" stop-color="{theme.MINT}"/></linearGradient></defs>'
        f'<rect x="0" y="12" width="790" height="5" rx="2.5" fill="url(#viz-spectrum)"/>'
        f'<path d="M786,6 L800,14.5 L786,23 z" fill="{theme.MINT}"/>'
        f'<text x="0" y="8" font-size="13" fill="{_tone.muted}">less code, faster start</text>'
        f'<text x="782" y="8" font-size="13" fill="{_tone.muted}" text-anchor="end">more code, full control</text></svg>'
    )
    nf.slide(
        _spectrum,
        nf.stack(
            [(_name, [nf.tool(_t, _logo, layout="row", height=theme.pt(18)) for _t, _logo in _tools])
             for _name, _tools in _layers],
            columns=4,
            gap=theme.SPACE["gap_sm"],
        ),
        nf.body(
            "All of these sit on top of the same open storage and engines - Postgres, DuckDB, "
            "Parquet - so picking one is not a lock-in decision."
        ),
        title="The open-source dataviz ecosystem",
        kicker="Data visualization",
        pad_top="5cqw",
    )
    return


@app.cell
def _(assets, mo, nf, theme):
    # Dataviz, gallery: one example from each project's own gallery (see
    # assets/images/gallery/README.md for sources and licences).
    _gallery = [
        ("gallery/d3", "D3", "anything you can draw with SVG or canvas"),
        ("gallery/echarts", "Apache ECharts", "rich, animated charts out of the box"),
        ("gallery/plotly", "Plotly", "interactive charts from Python, R or JS"),
        ("gallery/deckgl", "deck.gl", "millions of points on a map, on the GPU"),
        ("gallery/vega-lite", "Vega-Lite / Altair", "a grammar of interactive graphics"),
        ("gallery/observable-plot", "Observable Plot", "concise, exploratory charts"),
        ("gallery/kepler", "kepler.gl", "geospatial exploration, no code"),
        ("gallery/bokeh", "Bokeh", "interactive plots for Python, in the browser"),
    ]
    _tone = theme.TONES["navy"]

    def _tile(_file, _name, _what):
        _img = assets.img(
            f"images/{_file}", alt=_name,
            style={"aspect-ratio": "16 / 10", "object-fit": "cover", "background": "#ffffff"},
        )
        return mo.Html(
            f"<div>{mo.as_html(_img).text}"
            f'<div style="margin-top:{theme.SPACE["tight"]}; font-size:{theme.SIZE["small"]}; font-weight:700;">{_name}</div>'
            f'<div style="font-size:{theme.SIZE["caption"]}; color:{_tone.muted};">{_what}</div></div>'
        )

    nf.slide(
        mo.Html(
            f'<div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:{theme.SPACE["gap_sm"]} {theme.SPACE["gap_sm"]};">'
            + "".join(mo.as_html(_tile(*_g)).text for _g in _gallery)
            + "</div>"
        ),
        title="From the galleries",
        kicker="Data visualization",
        pad_top="4.5cqw",
        gap="1.2cqw",
    )
    return


@app.cell
def _(assets, mo, nf, theme):
    # Dataviz vs Power BI: a scorecard, one row per decision driver; the side
    # with the edge is ticked and bright, the other muted. Prices:
    # Microsoft's list prices since April 2025.
    _PBI, _OSS = "#F2C811", theme.MINT
    _rows = [
        ("Self-service", "drag-and-drop Desktop app (Windows-only)", "Superset and Metabase come close", "pbi"),
        ("Semantic model", "relationships, DAX measures, row-level security", "dbt metrics, Cube: a separate piece", "pbi"),
        ("Microsoft 365", "Teams, Excel, Entra ID built in", "you wire up SSO and sharing", "pbi"),
        ("Operations", "SaaS: Microsoft runs it", "you host, patch, secure (or buy managed)", "pbi"),
        ("Cost", "$14 / user / month; free viewers need F64", "free licence: pay for servers and people", "oss"),
        ("Visual freedom", "fixed visuals, custom ones in TypeScript", "anything a browser can draw", "oss"),
        ("Version control", "PBIP / TMDL help, still awkward to review", "it's code: git, review, CI", "oss"),
        ("Embedding", "Power BI Embedded needs paid capacity", "embed anywhere, any way", "oss"),
    ]
    _tone = theme.TONES["navy"]
    _cell = f"padding:0.55cqw {theme.SPACE['gap_sm']}; border-bottom:1px solid {_tone.rule}; vertical-align:middle;"

    def _side(_text, _wins, _color):
        if _wins:
            return f"<td style='{_cell} color:{_tone.fg}; font-weight:600;'><span style='color:{_color};'>&#10003;&nbsp;</span>{_text}</td>"
        return f"<td style='{_cell} color:{_tone.muted};'><span style='visibility:hidden;'>&#10003;&nbsp;</span>{_text}</td>"

    _pbi_logo = assets.img("logos/powerbi.svg", width="auto", rounded=False,
                           style={"height": "1.4em", "display": "inline-block", "vertical-align": "middle"}).text
    _head = (
        f'<tr><th style="{_cell}"></th>'
        f'<th style="{_cell} text-align:left; color:{_PBI}; font-size:{theme.SIZE["body"]};">{_pbi_logo}&nbsp; Power BI</th>'
        f'<th style="{_cell} text-align:left; color:{_OSS}; font-size:{theme.SIZE["body"]};">Open source</th></tr>'
    )
    _body = "".join(
        f"<tr><td style='{_cell} font-weight:700; white-space:nowrap; color:{_tone.muted};'>{_k}</td>"
        + _side(_p, _w == "pbi", _PBI) + _side(_o, _w == "oss", _OSS) + "</tr>"
        for _k, _p, _o, _w in _rows
    )
    nf.slide(
        mo.Html(
            f'<table style="width:100%; border-collapse:collapse; font-size:{theme.SIZE["small"]}; line-height:1.3;">'
            f"<thead>{_head}</thead><tbody>{_body}</tbody></table>"
        ),
        nf.body(
            "**Power BI** wins in a Microsoft shop where business users build their own reports. "
            "**Open source** wins when dashboards are code, are part of a product, or reach thousands of viewers."
        ),
        title="Open source or Power BI?",
        kicker="Data visualization",
        pad_top="4.5cqw",
        gap="1.4cqw",
    )
    return


@app.cell
def _(assets, mo, nf, theme):
    # Dataviz, the two big open-source BI apps side by side. Screenshots
    # from each project's own repo (sources in assets/logos/README.md).
    def _side(name, logo, tagline, shot, points, start):
        return mo.vstack(
            [
                nf.tool(name, logo, note=tagline, layout="row", height=theme.pt(24)),
                assets.img(shot, alt=f"{name} screenshot",
                           style={"aspect-ratio": "2.4 / 1", "object-fit": "cover", "object-position": "top left"}),
                nf.bullets(points, size=theme.SIZE["small"]),
                nf.code(start, language="bash", size=8, fit=(nf.CONTENT_CQW - 2.5) / 2),
            ],
            gap=0.5,
        )

    nf.slide(
        nf.two_col(
            _side(
                "Apache Superset", "logos/superset.svg", "Apache 2.0 · born at Airbnb",
                "images/superset-dashboard.jpg",
                [
                    "For data teams: SQL Lab, 40+ chart types, cross-filters",
                    "Any SQL database: Postgres, DuckDB, ClickHouse, Trino",
                    "Roles, row-level security, caching: scales to many users",
                ],
                "git clone https://github.com/apache/superset && docker compose up",
            ),
            _side(
                "Metabase", "logos/metabase.svg", "AGPL · open core · screenshots © Metabase",
                "images/metabase-dashboard.png",
                [
                    "For everyone else: the question builder needs no SQL",
                    "Running in five minutes; X-rays draft a first dashboard",
                    "Alerts and embedding; the paid tier adds SSO and more",
                ],
                "docker run -d -p 3000:3000 metabase/metabase",
            ),
            gap="2.5cqw",
        ),
        title="Superset and Metabase",
        kicker="Data visualization - open-source BI",
        pad_top="4.5cqw",
        gap="1.2cqw",
    )
    return


@app.cell
def _(BarChartRace, dashboard, mo, pd, theme):
    # The D3 slide's widget: weekly energy per plant, as running totals.
    # Created here, shown on the next slide (a UI element is bound to one
    # live mount). Colours are the dashboard's own, so plants match.
    _gold = dashboard.defs["gold"]
    _names = sorted(_gold["name"].unique())
    _plant_color = dict(zip(_names, dashboard.defs["PLANT_COLORS"]))
    _weekly = (
        _gold.groupby([pd.Grouper(key="date", freq="W"), "name"])["energy_generated_kwh"].sum()
        .unstack(fill_value=0)
        .reindex(columns=_names, fill_value=0)
        / 1e6  # kWh -> GWh
    )
    _cumulative = _weekly.cumsum()
    _tone = theme.TONES["navy"]
    race = mo.ui.anywidget(
        BarChartRace(
            title="Energy generated so far, by plant (GWh)",
            labels=[_n.removesuffix(" Solar Farm") for _n in _names],
            plant_colors=[_plant_color[_n] for _n in _names],
            dates=[_d.date().isoformat() for _d in _cumulative.index],
            values=_cumulative.round(4).values.tolist(),
            steps=_weekly.round(6).values.tolist(),
            unit="GWh",
            frame_ms=200,
            width=760,
            height=330,
            colors={"fg": _tone.fg, "muted": _tone.muted, "rule": _tone.rule, "bg": theme.NAVY,
                    "panel": "#0a1440", "accent": theme.MINT},
        )
    )
    return (race,)


@app.cell
def _(mo, nf, race, theme):
    # Dataviz, coding it yourself: a D3 bar chart race over the dashboard's
    # data - animation a BI tool can't do. Press play; hover; click a bar.
    _w = 760
    nf.slide(
        nf.two_col(
            mo.Html(
                f'<div style="container-type:inline-size; width:100%;">'
                f'<div style="width:{_w}px; zoom:calc(100cqw / {_w}px);">{mo.as_html(race).text}</div></div>'
            ),
            mo.vstack(
                [
                    nf.bullets(
                        [
                            "**Full control** of every pixel, transition and interaction",
                            "**Embed it anywhere:** your product, a site, a notebook like this one",
                            "**But** more code, and you own hosting, auth and state",
                        ],
                        size=theme.SIZE["small"],
                    ),
                    nf.cards([("What changed", "Coding assistants write the D3 boilerplate. This chart - "
                                               "about 150 lines - took minutes, not days.")], columns=1),
                ],
                gap=1.2,
            ),
            ratio=(2, 1),
            gap="2.5cqw",
            align="center",
        ),
        title="Coding dashboards in JavaScript",
        kicker="Data visualization - D3, live",
        pad_top="4.5cqw",
    )
    return


@app.cell
def _(nf):
    # Dataviz, the code behind the race: the actual draw() function from
    # template/race.py, cut out of the widget's source rather than retyped.
    from template import race as _race_module

    _src = _race_module._ESM
    _draw = _src[_src.index("  function draw(") : _src.index("  function setPlaying(")].rstrip()
    nf.slide(
        nf.code(_draw, language="javascript", size=8, fit=nf.CONTENT_CQW),
        nf.caption(
            "D3's data join: one <g> per plant, then a transition that moves, resizes and relabels "
            "every bar at once. Each frame of the race is one call to draw()."
        ),
        title="The code behind it",
        kicker="Data visualization - D3",
        pad_top="4.5cqw",
        gap="1.2cqw",
    )
    return


@app.cell
def _(diagram, nf, theme):
    # Dataviz, WebAssembly: the query engine moves into the browser tab.
    nf.slide(
        diagram("diagrams/wasm.svg", width="94%"),
        nf.stack(
            [
                ("Perspective", [nf.caption("C++ engine compiled to WASM; born at J.P. Morgan, now at FINOS")]),
                ("DuckDB-WASM", [nf.caption("the whole of DuckDB, SQL over Parquet, in a tab")]),
                ("marimo · Pyodide", [nf.caption("Python itself in the browser: marimo export html-wasm")]),
            ],
            columns=3,
            gap=theme.SPACE["gap_sm"],
        ),
        title="WebAssembly: the database moves into the browser",
        kicker="Data visualization - WASM",
        pad_top="4.5cqw",
        gap="1.2cqw",
    )
    return


@app.cell
def _(dashboard, mo):
    from perspective.widget import PerspectiveWidget

    # The Perspective slide's widget. binding_mode="client-server": Python
    # ships the table to the browser once, as Arrow, and Perspective's WASM
    # engine does every pivot, filter and chart from there - no server calls.
    _readings = dashboard.defs["sensor_readings"].merge(
        dashboard.defs["sensors"][["sensor_id", "plant_id"]], on="sensor_id"
    )
    _readings["timestamp"] = _readings["timestamp"].dt.tz_localize(None)
    perspective_view = mo.ui.anywidget(
        PerspectiveWidget(
            _readings.reset_index(drop=True),
            binding_mode="client-server",
            plugin="Y Area",
            expressions={"day": "bucket(\"timestamp\", 'D')"},
            group_by=["day"],
            split_by=["plant_id"],
            columns=["ac_power_kw"],
            theme="Pro Dark",
            settings=False,  # the presenter opens the panel live
        )
    )
    return (perspective_view,)


@app.cell
def _(mo, nf, perspective_view):
    # Dataviz, Perspective live: every sensor reading from the dashboard,
    # pivoted and charted in the browser. Open the settings and drag fields.
    nf.slide(
        # fixed-pixel widget: Perspective draws itself 520px tall, so give it a
        # 1150x520 canvas and zoom that to the slide's width
        mo.Html(
            f'<div style="container-type:inline-size; width:100%;">'
            f'<div style="width:1150px; height:520px; overflow:hidden; zoom:calc(100cqw / 1150px);">'
            f"{mo.as_html(perspective_view).text}</div></div>"
        ),
        nf.caption(
            "225k hourly readings, summed by day and plant in the browser. Open the settings (top left), "
            "change the chart, group by sensor, filter a plant - nothing goes back to Python."
        ),
        title="Perspective: a pivot engine in WebAssembly",
        kicker="Data visualization - WASM, live",
        pad_top="4.5cqw",
        gap="1.2cqw",
    )
    return


@app.cell
def _(assets, mo, nf, theme):
    # Wrap-up, 1 of 5: the trade-off itself - pros and cons of assembling
    # the platform from open-source tools vs adopting a managed one.
    _BAD = "#FF7A8A"
    _tone = theme.TONES["navy"]

    def _logos(_files):
        return "".join(
            assets.img(_f, width="auto", rounded=False,
                       style={"height": "1.2em", "display": "inline-block", "margin-left": "0.45em"}).text
            for _f in _files
        )

    def _column(_title, _files, _items, _accent):
        _rows = "".join(
            f'<li style="display:flex; gap:0.6em; align-items:baseline;">'
            f'<span style="color:{theme.MINT if _s == "+" else _BAD}; font-weight:900; flex:0 0 auto;">'
            f'{"&#10003;" if _s == "+" else "&#10007;"}</span>'
            f'<span style="color:{_tone.fg if _s == "+" else _tone.muted};">{_t}</span></li>'
            for _s, _t in _items
        )
        return mo.Html(
            f'<div style="background:#0a1440; border:1px solid {_tone.rule}; border-top:4px solid {_accent}; '
            f'border-radius:{theme.SPACE["radius"]}; padding:{theme.SPACE["gap_sm"]} {theme.SPACE["gap"]};">'
            f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:{theme.SPACE["gap_sm"]};">'
            f'<span style="font-size:{theme.SIZE["body"]}; font-weight:700;">{_title}</span>'
            f'<span style="white-space:nowrap;">{_logos(_files)}</span></div>'
            f'<ul style="list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:0.45em; '
            f'font-size:{theme.SIZE["small"]}; line-height:1.3;">{_rows}</ul></div>'
        )

    nf.slide(
        nf.two_col(
            _column(
                "Assemble it from open source",
                ["logos/duckdb.svg", "logos/airflow.svg", "logos/iceberg.svg", "logos/superset.svg"],
                [
                    ("+", "No licence fees: pay for servers and people"),
                    ("+", "No lock-in: open formats and APIs"),
                    ("+", "Best tool per layer, customised as you like"),
                    ("+", "Runs anywhere: laptop, on-prem, any cloud"),
                    ("+", "Transferable skills: SQL, Python, git"),
                    ("-", "You integrate: glue, upgrades, version clashes"),
                    ("-", "You run it: patches, backups, on-call, no SLA"),
                    ("-", "Catalog, lineage, access: pieces to assemble"),
                ],
                theme.MINT,
            ),
            _column(
                "Adopt a managed platform",
                ["logos/fabric.svg", "logos/databricks.svg", "logos/snowflake.svg"],
                [
                    ("+", "One-stop shop: ingestion to BI, integrated"),
                    ("+", "SLAs, support, compliance certifications"),
                    ("+", "Governance and security built in"),
                    ("+", "Elastic scale, fast start, low-code tools"),
                    ("-", "Consumption pricing: every query adds up"),
                    ("-", "Lock-in: proprietary compute, catalogs, skills"),
                    ("-", "The vendor's roadmap, outages, price rises"),
                    ("-", "Still needs skills: different ones, plus FinOps"),
                ],
                theme.BLUE,
            ),
            gap="2.5cqw",
        ),
        title="Open source or a managed platform?",
        kicker="Wrapping up",
        pad_top="4.5cqw",
        gap="1.4cqw",
    )
    return


@app.cell
def _(diagram, nf):
    # Wrap-up, 2 of 5: who usually goes for which. Company sizes: Stack
    # Overflow Developer Survey 2025, "Work" section (survey.stackoverflow.co/2025/work):
    # just me 3.9% + under 20 employees 17.2% + 20-99 20.8% = 41.9%.
    nf.slide(
        diagram("diagrams/who_goes_for_what.svg", width="96%"),
        nf.caption(
            "42% of developers work at companies with fewer than 100 people (Stack Overflow survey 2025) - "
            "the bottom of this map is bigger than it looks."
        ),
        title="Who usually goes for which",
        kicker="Wrapping up",
        pad_top="4.5cqw",
        gap="1cqw",
    )
    return


@app.cell
def _(bronze, diagram, duckdb, mo, nf, pd, theme, time):
    # Wrap-up, 3 of 5: costs (left, illustrative curve plus real list
    # prices) and performance (right, measured live on this machine).
    # Prices: Microsoft list prices, US pay-as-you-go - Fabric F64 is
    # 64 CU x $0.18/h x 730 h; Power BI Pro since April 2025. AWS m7i.4xlarge
    # on-demand, us-east-1: $0.8064/h x 730 h. Data sizes: Jordan Tigani,
    # "Big Data is Dead" (motherduck.com/blog/big-data-is-dead/), from BigQuery.
    _readings = pd.read_csv(bronze.BRONZE_DIR / "sensor_readings.csv.gz", usecols=["sensor_id", "ac_power_kw"])
    _readings["sensor_id"] = _readings["sensor_id"].astype("category")
    _times = 100
    _big = pd.concat([_readings] * _times, ignore_index=True)  # ~22.5M rows

    def _best_ms(_fn, _n=3):
        _out = []
        for _ in range(_n):
            _t0 = time.perf_counter()
            _fn()
            _out.append((time.perf_counter() - _t0) * 1000)
        return min(_out)

    _con = duckdb.connect()
    _con.register("big", _big)
    _con.execute("CREATE TABLE big_native AS SELECT * FROM big")
    _pandas_ms = _best_ms(lambda: _big.groupby("sensor_id", observed=True)["ac_power_kw"].agg(["sum", "mean"]))
    _duck_ms = _best_ms(lambda: _con.sql("SELECT sensor_id, sum(ac_power_kw), avg(ac_power_kw) FROM big_native GROUP BY ALL").fetchall())
    _con.close()
    _rows = len(_big)
    del _big

    _tone = theme.TONES["navy"]
    _max = max(_pandas_ms, _duck_ms)

    def _bar(_label, _ms, _color):
        return (
            f'<div style="display:grid; grid-template-columns:5.5em 1fr 4.5em; align-items:center; gap:0.6em; margin:0.35em 0;">'
            f'<span style="font-weight:700;">{_label}</span>'
            f'<span style="display:block; height:1em; border-radius:0.3em; background:{_color}; width:{_ms / _max * 100:.1f}%;"></span>'
            f'<span style="font-variant-numeric:tabular-nums; text-align:right;">{_ms:,.0f} ms</span></div>'
        )

    _perf = mo.Html(
        f'<div style="font-size:{theme.SIZE["small"]};">'
        f'<div style="color:{_tone.muted}; margin-bottom:0.3em;">Sum and average by sensor over {_rows / 1e6:.1f}M readings, '
        f"on this laptop, just now:</div>"
        + _bar("pandas", _pandas_ms, _tone.muted)
        + _bar("DuckDB", _duck_ms, theme.MINT)
        + f'<div style="color:{theme.MINT}; font-weight:700; margin-top:0.2em;">{_pandas_ms / _duck_ms:.0f}x faster - with no cluster at all</div></div>'
    )

    nf.slide(
        nf.two_col(
            mo.vstack(
                [
                    nf.eyebrow("Costs"),
                    diagram("diagrams/cost_curve.svg", width="92%"),
                    nf.bullets(
                        [
                            "Fabric F64 (free report viewers): ~$8,400 / month pay-as-you-go",
                            "Power BI Pro: $14 / user / month",
                            "A 16-core, 64 GB VM: ~$590 / month on demand (AWS m7i.4xlarge)",
                            "The hidden cost on both sides: people's time",
                        ],
                        size=theme.SIZE["caption"],
                    ),
                ],
                gap=0.6,
            ),
            mo.vstack(
                [
                    nf.eyebrow("Performance"),
                    _perf,
                    nf.stats(
                        [("90%", "of queries read under 100 MB", "BigQuery, per Jordan Tigani"),
                         ("<100 GB", "median data per customer", "\"Big Data is Dead\", 2023")],
                        columns=2,
                    ),
                    nf.bullets(
                        [
                            "One machine runs most workloads - DuckDB, ClickHouse, Postgres",
                            "Managed platforms win on elastic scale and many concurrent users",
                        ],
                        size=theme.SIZE["caption"],
                    ),
                ],
                gap=0.9,
            ),
            ratio=(1, 1),
            gap="3cqw",
        ),
        title="Costs and performance",
        kicker="Wrapping up",
        pad_top="4.5cqw",
        gap="1cqw",
    )
    return


@app.cell
def _(nf, theme):
    # Wrap-up, 4 of 5: the answers to the questions from the agenda slide.
    nf.slide(
        nf.cards(
            [
                ("Is it possible?", "Yes. We built the dashboard, and there is a mature open-source tool for every layer of a platform."),
                ("How would you do it?", "Open formats (Parquet, Iceberg) + an engine (DuckDB, Postgres, ClickHouse) + "
                                         "orchestration (Airflow, Prefect) + BI or code."),
                ("Is it a good idea?", "When you have engineers, care about cost, lock-in and flexibility - or your data is "
                                       "small enough for one machine. Which is most data."),
                ("Better than managed?", "Not always: a platform buys integration, SLAs and governance. Open formats make it "
                                         "not all-or-nothing - mix and match."),
            ],
            columns=2,
        ),
        title="So: open source, from raw data to dashboards?",
        kicker="Wrapping up",
        pad_top=theme.scale(70),
    )
    return


@app.cell
def _(nf):
    nf.closing("Questions")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
