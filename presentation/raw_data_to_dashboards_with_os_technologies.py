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
                "Is it possible to go from raw data to dashboards with open source tools?",
                "How would you even do it?",
                "Is it a good idea?",
                "How do OS tools compare to a managed data platform?",
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

    def chart_step(n, label, code, gold, *, total=4):
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
        width. Diagrams that tell a story build in steps - reveal.js
        fragments inside the SVG - one per click of the presenter's clicker."""
        return mo.Html(
            f'<div style="width:{width}; margin:0 auto;">{assets.svg(name).text}</div>'
        )

    #: Line icons for icon_cards(), drawn on a 48x48 grid in currentColor.
    ICONS = {
        "wheel": '<circle cx="24" cy="24" r="18"/><circle cx="24" cy="24" r="5"/><path d="M24 19V6M19.7 26.5 8.4 33M28.3 26.5 39.6 33"/>',
        "toolbox": '<rect x="6" y="18" width="36" height="22" rx="3"/><path d="M17 18v-6h14v6M6 27h36M21 27v5h6v-5"/>',
        "code": '<path d="M17 13 7 24l10 11M31 13l10 11-10 11M27 9l-6 30"/>',
        "server": '<rect x="9" y="7" width="30" height="9" rx="2"/><rect x="9" y="20" width="30" height="9" rx="2"/><rect x="9" y="33" width="30" height="9" rx="2"/><path d="M15 11.5h1M15 24.5h1M15 37.5h1"/>',
        "growth": '<path d="M8 40h34M8 40V8M14 34V26M22 34V20M30 34V14"/><path d="M28 9h9v9M37 9 25 21"/>',
        "cap": '<path d="M4 18 24 9l20 9-20 9z"/><path d="M12 22v10c4 4 20 4 24 0V22M44 18v12"/>',
    }

    def icon_cards(items, *, columns=3):
        """Cards with a line icon, a title, a short text and an example line:
        items are (icon, title, text, example, accent)."""
        _tone = theme.TONES["navy"]
        _cells = "".join(
            f'<div style="background:#0a1440; border:1px solid {_tone.rule}; border-top:4px solid {_accent}; '
            f'border-radius:{theme.SPACE["radius"]}; padding:{theme.SPACE["gap_sm"]} {theme.SPACE["gap"]} {theme.SPACE["gap"]};">'
            f'<svg viewBox="0 0 48 48" style="width:3.4cqw; height:3.4cqw; color:{_accent}; display:block; margin:0.4cqw 0 0.8cqw;" '
            f'fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">{ICONS[_icon]}</svg>'
            f'<div style="font-size:{theme.SIZE["body"]}; font-weight:700; line-height:1.25; margin-bottom:0.6cqw;">{_title}</div>'
            f'<div style="font-size:{theme.SIZE["small"]}; line-height:1.4; color:{_tone.fg};">{_text}</div>'
            f'<div style="font-size:{theme.SIZE["caption"]}; line-height:1.4; color:{_tone.muted}; margin-top:0.8cqw;">{_example}</div></div>'
            for _icon, _title, _text, _example, _accent in items
        )
        return mo.Html(
            f'<div style="display:grid; grid-template-columns:repeat({columns}, 1fr); gap:{theme.SPACE["gap"]}; '
            f'align-items:stretch;">{_cells}</div>'
        )

    return (
        AREA_CODE,
        chart_from,
        chart_step,
        diagram,
        full_bleed_slide,
        icon_cards,
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
    # Ingesting, fragment: the data model behind the tabs, as a star schema
    # - fact tables (readings, settlement, and the daily per-plant table the
    # dashboard is built on) around the sensor and plant dimensions. The slide
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
        .merge(sensors[["sensor_id", "plant_id"]], on="sensor_id")
        .assign(date=lambda d: d["timestamp"].dt.normalize()) # Add a timestamp column
        .groupby(["plant_id", "date"], as_index=False)
        .agg(energy_generated_kwh=("ac_power_kw_clean", "sum"))
        .merge(settlement, on=["plant_id", "date"])
        .merge(plants[["plant_id", "name", "capacity_mw"]], on="plant_id")
        # Compute net produced energy
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
        nf.body(f"The slider is at **{slider.value}**"),
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
    # Filters, step 3: marimo has no date-range slider, so this one is a
    # custom widget - an anywidget: a Python class with a JavaScript
    # front end (template/timeline.py, abridged here) and synced state.
    _define = '''
    class DateRangeTimeline(anywidget.AnyWidget):
        # the browser side: plain JavaScript
        _esm = """
        function render({ model, el }) {
          // draw the strip, the range and two handles...
          // ...and when a drag ends, tell Python:
          model.set("start", toIso(start));
          model.set("end", toIso(end));
          model.save_changes();
        }
        export default { render };
        """
        # state synced between Python and the browser
        start = traitlets.Unicode().tag(sync=True)
        end = traitlets.Unicode().tag(sync=True)
        values = traitlets.List(traitlets.Float()).tag(sync=True)
    '''
    _use = '''
    period_filter = mo.ui.anywidget(
        DateRangeTimeline(
            start=first_day,
            end=last_day,
            # the strip behind the handles
            values=daily_energy,
        )
    )
    period_filter

    # cells reading this re-run on drag
    period_filter.value["start"]
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
        nf.two_col(
            mo.vstack([nf.caption("Define it: a Python class + JavaScript"), nf.code(_define, size=8, fit=(nf.CONTENT_CQW - 2.5) * 0.58)], gap=0.3),
            mo.vstack([nf.caption("Use it like any marimo element"), nf.code(_use, size=8, fit=(nf.CONTENT_CQW - 2.5) * 0.42)], gap=0.3),
            ratio=(58, 42),
            gap="2.5cqw",
        ),
        mo.Html(_widget),
        nf.body(
            f"Selected: **{period_filter.value['start']}** to **{period_filter.value['end']}**"
        ),
        title="Adding filters with marimo ui elements",
        kicker="Step 3: a date range - a custom anywidget",
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
def _():
    return


@app.cell
def _(mo, nf, theme):
    # The open-source platform as a simple map: the data path (ingestion ->
    # storage -> transformation -> serving) with orchestration above it and
    # deployment under it. Shown whole with question marks on the "can we"
    # slide, then again before each part of the talk with that part lit up.
    _tone = theme.TONES["navy"]
    _STAGES = [  # key, label, sub-label, accent
        ("ingestion", "Ingestion", "get the raw data in", theme.LAVENDER),
        ("storage", "Storage", "files, tables, databases", theme.BLUE),
        ("transformation", "Transformation", "clean, join, aggregate", theme.PURPLE),
        ("serving", "Serving", "dashboards and BI", theme.MINT),
    ]
    _BARS = [  # key, label, sub-label, y, accent
        ("orchestration", "Orchestration", "runs every step on schedule", 8, theme.PURPLE),
        ("deployment", "Deployment", "where and how it all runs", 244, theme.BLUE),
    ]

    def _qmark(x, y, color):
        return (
            f'<g transform="translate({x},{y}) rotate(12)"><circle r="17" fill="{theme.NAVY}" stroke="{color}" stroke-width="2"/>'
            f'<text y="7" text-anchor="middle" font-size="21" font-weight="700" fill="{color}">?</text></g>'
        )

    def platform_map(highlight=None, *, width="100%"):
        """The platform map; `highlight` lights up one part and dims the rest."""
        _parts = []

        def _look(key):
            _on = highlight is None or highlight == key
            return ("1" if _on else "0.25"), (theme.MINT if highlight == key else None)

        for _key, _label, _sub, _y, _accent in _BARS:
            _op, _ring = _look(_key)
            _parts.append(
                f'<g opacity="{_op}"><rect x="40" y="{_y}" width="920" height="48" rx="10" fill="#0a1440" '
                f'stroke="{_ring or _accent}" stroke-width="{3 if _ring else 1.5}" stroke-dasharray="{"none" if _ring else "6 5"}"/>'
                f'<text x="66" y="{_y + 31}" font-size="19" font-weight="700" fill="{_tone.fg}">{_label}'
                f'<tspan dx="12" font-size="15" font-weight="400" fill="{_tone.muted}">{_sub}</tspan></text>'
                f"{_qmark(948, _y + 4, _ring or _accent)}</g>"
            )
        for _i, (_key, _label, _sub, _accent) in enumerate(_STAGES):
            _x = 40 + _i * 242
            _op, _ring = _look(_key)
            _parts.append(
                f'<g opacity="{_op}"><rect x="{_x}" y="84" width="194" height="128" rx="14" fill="#0a1440" '
                f'stroke="{_ring or _tone.rule}" stroke-width="{3 if _ring else 1.5}"/>'
                f'<rect x="{_x + 16}" y="84" width="162" height="5" rx="2.5" fill="{_accent}"/>'
                f'<text x="{_x + 97}" y="146" text-anchor="middle" font-size="22" font-weight="700" fill="{_tone.fg}">{_label}</text>'
                f'<text x="{_x + 97}" y="172" text-anchor="middle" font-size="14" fill="{_tone.muted}">{_sub}</text>'
                f"{_qmark(_x + 186, 88, _ring or _accent)}</g>"
            )
            if _i < len(_STAGES) - 1:
                _ax = _x + 194
                _parts.append(
                    f'<g opacity="{"1" if highlight is None else "0.35"}"><line x1="{_ax + 6}" y1="148" x2="{_ax + 38}" y2="148" '
                    f'stroke="{_tone.muted}" stroke-width="2"/><path d="M{_ax + 36},142 L{_ax + 44},148 L{_ax + 36},154 z" fill="{_tone.muted}"/></g>'
                )
        return mo.Html(
            f'<div style="width:{width}; margin:0 auto;"><svg viewBox="0 0 1000 304" width="100%" '
            f'xmlns="http://www.w3.org/2000/svg" style="display:block; font-family:inherit; overflow:visible;">'
            + "".join(_parts)
            + "</svg></div>"
        )

    def platform_step(key, title, coming_up):
        """A section opener: the map with one part lit, and what comes next."""
        return nf.slide(
            platform_map(key, width="92%"),
            nf.body(f"**Coming up:** {coming_up}"),
            title=title,
            kicker="An open-source platform, piece by piece",
            pad_top="5cqw",
            gap="2.5cqw",
        )

    return platform_map, platform_step


@app.cell
def _(nf, platform_map, theme):
    nf.slide(
        platform_map(width="86%"),
        nf.cards(
            [
                ("Is it possible?",
                 "Can open-source tools give us what a managed data platform does: storage, pipelines, governance, dashboards?"),
                ("What tools should I use?",
                 "To replace services provided by data platforms?"),
                ("Is it a good idea?",
                 "What are the benefits and the drawbacks in economical/technical terms?"),
            ],
            columns=3,
        ),
        title="Can we have an open source data platform?",
        pad_top="4.5cqw",
        gap="2cqw",
    )
    return


@app.cell
def _(platform_step):
    platform_step("ingestion", "Ingestion: getting the raw data in", "Airbyte")
    return


@app.cell
def _(assets, mo, nf, theme):
    # Ingestion: Airbyte, the open-source connector platform. Screenshots of
    # its UI in a click-through carousel (a CSS radio carousel: no script, so
    # it survives the slide's HTML composition and leaves the arrow keys to
    # reveal). Drop more in as assets/images/airbyte-*.png.
    _tone = theme.TONES["navy"]
    _shots = [
        ("images/airbyte-connections.png", "Connections: every source-to-destination pipeline and its last sync"),
        ("images/airbyte-source.png", "Adding a source: pick a connector, fill in its settings"),
        ("images/airbyte-streams.png", "Choosing streams: which tables and columns to sync, full or incremental"),
        ("images/airbyte-sync.png", "A sync's history and logs"),
    ]
    _shots = [_s for _s in _shots if assets.exists(_s[0])]
    if _shots:
        _css = "".join(
            f"#ab-shot-{_i}:checked ~ .ab-frames .ab-{_i} {{ opacity:1; }} "
            f"#ab-shot-{_i}:checked ~ .ab-dots label[for=ab-shot-{_i}] {{ background:{theme.MINT}; }} "
            for _i in range(len(_shots))
        )
        _carousel = (
            f"<style>.ab-frames > div {{ opacity:0; transition:opacity .4s; }} .ab-dots label {{ cursor:pointer; }} {_css}</style>"
            '<div style="position:relative;">'
            + "".join(
                f'<input type="radio" name="ab-shot" id="ab-shot-{_i}" {"checked" if _i == 0 else ""} style="display:none;">'
                for _i in range(len(_shots))
            )
            + '<div class="ab-frames" style="display:grid;">'
            + "".join(
                f'<div class="ab-{_i}" style="grid-area:1 / 1;">'
                + assets.img(_f, alt=_alt, style={"aspect-ratio": "4 / 3", "object-fit": "cover", "object-position": "left top"}).text
                + f'<div style="font-size:{theme.SIZE["caption"]}; color:{_tone.muted}; margin-top:0.5cqw;">{_alt}</div></div>'
                for _i, (_f, _alt) in enumerate(_shots)
            )
            + '</div><div class="ab-dots" style="display:flex; gap:0.8cqw; justify-content:center; margin-top:0.8cqw;">'
            + "".join(
                f'<label for="ab-shot-{_i}" style="width:1cqw; height:1cqw; border-radius:50%; border:1px solid {theme.MINT};"></label>'
                for _i in range(len(_shots))
            )
            + "</div></div>"
        )
    else:
        _carousel = (
            f'<div style="aspect-ratio:4 / 3; border:1px dashed {_tone.rule}; border-radius:{theme.SPACE["radius"]}; '
            f'display:grid; place-items:center; color:{_tone.muted}; font-size:{theme.SIZE["small"]};">'
            "Airbyte screenshots go here: assets/images/airbyte-*.png</div>"
        )
    nf.slide(
        nf.two_col(
            mo.vstack(
                [
                    nf.tool("Airbyte", "logos/airbyte.svg", note="open-source data movement", layout="row", height=theme.pt(28)),
                    nf.bullets(
                        [
                            "**600+ connectors:** databases, SaaS APIs and files in; warehouses, lakes and databases out",
                            "**Point and click:** source → destination → schedule, then it copies the data on every sync",
                            "**Incremental syncs and CDC:** only what changed since the last run",
                            "**No connector for your API?** Build one in the Connector Builder, or in Python",
                            "**Self-host it** on Docker or Kubernetes, or let Airbyte Cloud run it",
                        ],
                        size=theme.SIZE["small"],
                    ),
                ],
                gap=1.2,
            ),
            mo.Html(_carousel),
            ratio=(1, 1.25),
            gap="3cqw",
        ),
        title="Airbyte: getting the data in",
        kicker="Ingestion",
        pad_top="5cqw",
    )
    return


@app.cell
def _(platform_step):
    platform_step(
        "storage", "Storage: where the data lives",
        "file and table formats (Parquet, Delta Lake, Iceberg), then the databases (PostgreSQL, DuckDB, ClickHouse)",
    )
    return


@app.cell
def _(mo, nf, theme):
    # Parquet, intro: what it is, where it came from and what it's for -
    # before the three diagrams that show how it works.
    nf.slide(
        nf.tool("Apache Parquet", "logos/parquet.svg", note="an open-source columnar file format for tables",
                layout="row", height=theme.pt(28)),
        nf.two_col(
            mo.vstack(
                [
                    nf.eyebrow("What it is"),
                    nf.bullets(
                        [
                            "A compressed file format for storing tabular data, with several optimizations for speed and size",
                            "Created in **2013 by Twitter and Cloudera**, inspired by Google's Dremel paper (2010)",
                            "An Apache top-level project since 2015 - the default file format of data lakes",
                            "Being one of the most common file formats for storing large datasets, it's supported by many tools and software",
                        ],
                        size=theme.SIZE["small"],
                    ),
                ],
                gap=1,
            ),
            mo.vstack(
                [
                    nf.eyebrow("Pros"),
                    nf.bullets(
                        [
                            "Analytical workloads, fast reads, aggregations, and filtering",
                            "Cheaply storing large datasets (e.g. archives)",
                            "Size-efficient data format with enforced data types",
                        ],
                        size=theme.SIZE["small"],
                    ),
                    nf.eyebrow("Cons"),
                    nf.bullets(
                        [
                            "Updating a row requires rewriting the whole file",
                            "Not suited for transactional workloads"
                        ],
                        size=theme.SIZE["small"],
                        marker="×",
                    ),
                ],
                gap=1,
            ),
            gap="3cqw",
        ),
        title="Parquet: a compressed columnar file format",
        kicker="Data formats",
        pad_top="5cqw",
        gap="2cqw",
    )
    return


@app.cell
def _(assets, nf):
    # Parquet, 1 of 3: the same rows stored row by row vs column by column.
    # The diagram builds in four steps, one per click (reveal fragments).
    nf.slide(
        assets.svg("diagrams/parquet_columnar.svg"),
        title="Parquet writes columns in contiguous memory space",
        kicker="Data formats",
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
            ]
        ),
        title="Compressing column data",
        kicker="Parquet - why the files are small",
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
def _(mo, nf, theme):
    # Table formats, Delta intro: where it came from, the one idea behind it,
    # and where you will meet it - before the four-step walk through the log.
    nf.slide(
        nf.tool("Delta Lake", "logos/delta-lake.svg", note="an open table format: Parquet files plus a transaction log",
                layout="row", height=theme.pt(28)),
        nf.two_col(
            mo.vstack(
                [
                    nf.eyebrow("Where it came from"),
                    nf.bullets(
                        [
                            "Built at **Databricks**, by the team behind Spark; open-sourced in **2019** and now hosted by the Linux Foundation",
                            "The problem: a data lake is just a folder of files - a failed job leaves half-written data, "
                            "readers see changes mid-way, and you can't update or delete a row",
                        ],
                        size=theme.SIZE["small"],
                    ),
                    nf.eyebrow("The main idea"),
                    nf.bullets(
                        [
                            "Keep the data in plain **Parquet** files, and add a **log**: one small JSON file per change, saying which files were added or removed",
                            "The table is whatever the log says - so every change is **all or nothing**, and old versions can be read back",
                        ],
                        size=theme.SIZE["small"],
                    ),
                ],
                gap=1,
            ),
            mo.vstack(
                [
                    nf.eyebrow("Where you will meet it"),
                    nf.tool("Databricks", "logos/databricks.svg", note="the default format of every table",
                            layout="row", height=theme.pt(24)),
                    nf.tool("Microsoft Fabric", "logos/fabric.svg", note="OneLake stores every table as Delta Parquet",
                            layout="row", height=theme.pt(24)),
                    nf.bullets(
                        [
                            "Also read and written by Spark, DuckDB, Trino and, from plain Python, pandas and Polars (via delta-rs)",
                            "Open specification: the data stays yours, in files any engine can read",
                        ],
                        size=theme.SIZE["small"],
                    ),
                ],
                gap=1,
            ),
            gap="3cqw",
        ),
        title="Delta Lake: a reliable table made of plain files",
        kicker="Data formats - table formats",
        pad_top="5cqw",
        gap="2cqw",
    )
    return


@app.cell
def _(mo, nf, theme):
    # Delta, the log in four steps. Top: the SQL and the commit it writes to
    # _delta_log/. Bottom: the files on disk and the table a reader sees, with
    # what this commit changed marked. Both code panels are sized for the
    # longest snippet of all four steps, so the text doesn't jump between them.
    _tone = theme.TONES["navy"]
    _MONO = "var(--marimo-monospace-font, ui-monospace, SFMono-Regular, Menlo, monospace)"

    def _chip(name, state):
        # state: "new" (this commit), "removed" (left the table, still on
        # disk) or "live"
        _color = {"new": theme.MINT, "removed": _tone.muted, "live": _tone.fg}[state]
        _border = theme.MINT if state == "new" else _tone.rule
        _strike = "text-decoration:line-through;" if state == "removed" else ""
        return (
            f'<span style="display:inline-block; font-family:{_MONO}; font-size:{theme.pt(7)}; '
            f"color:{_color}; {_strike} border:1px solid {_border}; border-radius:0.5cqw; "
            f'padding:0.1cqw 0.5cqw; margin:0 0.4cqw 0.4cqw 0;">{name}</span>'
        )

    def _files(n, data_files, aside, legend):
        _row = lambda label, chips: (
            f'<div style="display:flex; align-items:baseline; gap:0.8cqw;">'
            f'<span style="flex:none; width:6.5cqw; font-size:{theme.SIZE["caption"]}; color:{_tone.muted};">{label}</span>'
            f'<div>{"".join(chips)}</div></div>'
        )
        _logs = [_chip(f"{_v:05d}.json", "new" if _v == n - 1 else "live") for _v in range(n)]
        _data = [_chip(f"{_f}.parquet", _s) for _f, _s in data_files] or [
            f'<span style="font-size:{theme.SIZE["caption"]}; color:{_tone.muted};">none yet</span>'
        ]
        _html = _row("_delta_log/", _logs) + _row("data files", _data)
        if legend and any(_s == "removed" for _, _s in data_files):
            _html += nf.caption("Struck through: out of the table, still on disk until VACUUM.").text
        if aside:
            _html += (
                f'<div style="margin-top:0.8cqw; padding:0.6cqw 1cqw; border-left:3px solid {theme.PURPLE}; '
                f'background:#0a1440; font-size:{theme.SIZE["caption"]}; line-height:1.45;">{mo.md(aside).text}</div>'
            )
        return mo.Html(_html)

    def _table(rows, live):
        # rows: (ts, sensor_id, ac_power_kw, mark) - mark is None, "new",
        # "deleted", or the old value of an updated ac_power_kw
        _cell = f"padding:0.3cqw 0.8cqw; border-bottom:1px solid {_tone.rule}; text-align:left; white-space:nowrap;"
        _head = "".join(
            f'<th style="{_cell} color:{_tone.muted}; font-weight:500; text-transform:uppercase; letter-spacing:0.06em;">{_c}</th>'
            for _c in ("", "ts", "sensor_id", "ac_power_kw")
        )
        _body = ""
        for _ts, _sensor, _kw, _mark in rows:
            _sign, _style, _kw_html = "", f"color:{_tone.fg};", f"{_kw}"
            if _mark == "new":
                _sign = f'<span style="color:{theme.MINT};">+</span>'
            elif _mark == "deleted":
                _sign = f'<span style="color:{theme.PURPLE};">−</span>'
                _style = f"color:{_tone.muted}; text-decoration:line-through;"
            elif _mark is not None:
                _sign = f'<span style="color:{theme.MINT};">~</span>'
                _kw_html = (
                    f'<span style="color:{_tone.muted}; text-decoration:line-through;">{_mark}</span> '
                    f'<span style="color:{theme.MINT}; font-weight:700;">{_kw}</span>'
                )
            _body += (
                f'<tr style="{_style}"><td style="{_cell} width:1.5cqw;">{_sign}</td><td style="{_cell}">{_ts}</td>'
                f'<td style="{_cell}">{_sensor}</td><td style="{_cell}">{_kw_html}</td></tr>'
            )
        _count = sum(1 for *_, _m in rows if _m != "deleted")
        _caption = f"{_count} rows · read from {', '.join(live)}" if live else "0 rows · nothing to read yet"
        return mo.Html(
            f'<table style="border-collapse:collapse; width:100%; font-family:{_MONO}; font-size:{theme.SIZE["small"]};">'
            f"<thead><tr>{_head}</tr></thead><tbody>{_body}</tbody></table>"
            + nf.caption(_caption).text
        )

    def delta_step(n, label, sql, log_json, rows, data_files, note, *, aside=None, legend=True, total=4):
        _panel = lambda eyebrow, body: f'<div style="min-width:0;">{mo.vstack([nf.eyebrow(eyebrow), body], gap=1.4).text}</div>'
        _live = [_f for _f, _s in data_files if _s != "removed"]
        _grid = mo.Html(
            '<div style="display:grid; grid-template-columns:1fr 1fr; column-gap:2.5cqw; row-gap:1.4cqw; align-items:start;">'
            + _panel("1 · SQL", nf.code(sql, language="sql", size=10, fit=39.7))
            + _panel(f"2 · _delta_log/{n - 1:05d}.json - trimmed", nf.code(log_json, language="json", size=10, fit=39.7))
            + _panel("3 · Files on disk", _files(n, data_files, aside, legend))
            + _panel("4 · Table snapshot", _table(rows, _live))
            + "</div>"
        )
        return nf.slide(
            _grid,
            nf.body(note),
            title="How the Delta log tracks a table",
            kicker=f"Step {n} of {total}: {label}",
            pad_top="4cqw",
            gap="1.4cqw",
        )

    return (delta_step,)


@app.cell
def _(delta_step):
    delta_step(
        1, "create the table",
        """
        CREATE TABLE readings (
          ts          TIMESTAMP,
          sensor_id   STRING,
          ac_power_kw DOUBLE
        ) USING DELTA;
        """,
        """
        {"commitInfo": {
          "operation": "CREATE TABLE"}}
        {"protocol": {"minReaderVersion": 1,
                      "minWriterVersion": 2}}
        {"metaData": {"schema": [
          "ts timestamp", "sensor_id string",
          "ac_power_kw double"]}}
        """,
        [],
        [],
        "Creating a table writes no data - only the first JSON log file, with the schema and the protocol version.",
    )
    return


@app.cell
def _(delta_step):
    delta_step(
        2, "add rows",
        """
        INSERT INTO readings VALUES
          ('2026-06-01 12:00', 'S1', 4.2),
          ('2026-06-01 12:00', 'S2', 3.8),
          ('2026-06-01 12:15', 'S1', 0.0),
          ('2026-06-01 12:15', 'S2', 3.9);
        """,
        """
        {"commitInfo": {"operation": "WRITE"}}
        {"add": {"path": "part-0001.parquet",
                 "stats": {"numRecords": 4}}}
        """,
        [("2026-06-01 12:00", "S1", 4.2, "new"), ("2026-06-01 12:00", "S2", 3.8, "new"),
         ("2026-06-01 12:15", "S1", 0.0, "new"), ("2026-06-01 12:15", "S2", 3.9, "new")],
        [("part-0001", "new")],
        "The Parquet file is written first, then the commit lists it. The rows only exist for readers once the JSON file is there.",
    )
    return


@app.cell
def _(delta_step):
    delta_step(
        3, "delete rows",
        """
        -- S1 dropped out at 12:15
        DELETE FROM readings
        WHERE ac_power_kw = 0;
        """,
        """
        {"commitInfo": {"operation": "DELETE"}}
        {"remove": {"path": "part-0001.parquet"}}
        {"add": {"path": "part-0002.parquet",
                 "stats": {"numRecords": 3}}}
        """,
        [("2026-06-01 12:00", "S1", 4.2, None), ("2026-06-01 12:00", "S2", 3.8, None),
         ("2026-06-01 12:15", "S1", 0.0, "deleted"), ("2026-06-01 12:15", "S2", 3.9, None)],
        [("part-0001", "removed"), ("part-0002", "new")],
        "**Files are never edited.** The file holding the deleted row is rewritten without it: remove one file, add another. "
        "The old file stays on disk, so version 1 can still be read back.",
        aside="**Deletion vectors:** Databricks and Fabric can skip the rewrite. The commit keeps the same Parquet file "
        "and attaches a small bitmap of the deleted rows; readers filter them out until the next OPTIMIZE.",
    )
    return


@app.cell
def _(delta_step):
    delta_step(
        4, "update rows",
        """
        -- S2 was reading 0.5 kW low
        UPDATE readings
        SET ac_power_kw = ac_power_kw + 0.5
        WHERE sensor_id = 'S2';
        """,
        """
        {"commitInfo": {"operation": "UPDATE"}}
        {"remove": {"path": "part-0002.parquet"}}
        {"add": {"path": "part-0003.parquet",
                 "stats": {"numRecords": 3}}}
        """,
        [("2026-06-01 12:00", "S1", 4.2, None), ("2026-06-01 12:00", "S2", 4.3, 3.8),
         ("2026-06-01 12:15", "S2", 4.4, 3.9)],
        [("part-0001", "removed"), ("part-0002", "removed"), ("part-0003", "new")],
        "**An update is a rewrite too:** the same remove + add, with the new values in a new file. "
        "*VERSION AS OF 2* still reads the table before the fix.",
        legend=False,
        aside="**Checkpoints:** every 10 commits (by default) the whole table state is also saved as one Parquet "
        "checkpoint in _delta_log/, so readers start there instead of replaying every JSON file.",
    )
    return


@app.cell
def _(mo, nf, theme):
    # Delta, a real commit: the whole of 00000000000000000003.json as delta-rs
    # wrote it for the step-4 UPDATE - one panel per action, in file order,
    # each with what it is for. Captured once, not written live: the
    # timestamps and file names would change on every run.
    def _action(name, what, source, extra=None):
        return mo.vstack(
            [
                nf.eyebrow(name),
                mo.Html(f'<div style="font-size:{theme.SIZE["small"]}; line-height:1.35;">{mo.md(what).text}</div>'),
                nf.code(source, language="json", size=9, fit=26.7),
                *([extra] if extra is not None else []),
            ],
            gap=0.6,
        )

    _cols = [
        _action(
            "commitInfo",
            "**Who, when and what:** the operation, its predicate, the version it started from and some metrics. "
            "Audit only - readers skip it.",
            """
            {"commitInfo": {
              "timestamp": 1792427178690,
              "operation": "UPDATE",
              "operationParameters": {
                "predicate": "sensor_id = 'S2'"},
              "readVersion": 2,
              "engineInfo": "delta-rs:py-1.6.6",
              "clientVersion": "delta-rs.py-1.6.6",
              "operationMetrics": {
                "num_added_files": 1,
                "num_removed_files": 1,
                "num_updated_rows": 2,
                "num_copied_rows": 1,
                "execution_time_ms": 4,
                "scan_time_ms": 2}}}
            """,
        ),
        _action(
            "add",
            "**A file joins the table**, with its size and per-column min / max / null counts - "
            "so a reader can skip it without opening it.",
            """
            {"add": {
              "path": "part-00000-0bbd….parquet",
              "partitionValues": {},
              "size": 1112,
              "modificationTime": 1792427178690,
              "dataChange": true,
              "stats": {
                "numRecords": 3,
                "minValues": {"sensor_id": "S1",
                  "ac_power_kw": 4.2,
                  "ts": "2026-06-01 12:00:00"},
                "maxValues": {"sensor_id": "S2",
                  "ac_power_kw": 4.4,
                  "ts": "2026-06-01 12:15:00"},
                "nullCount": {"sensor_id": 0,
                  "ac_power_kw": 0, "ts": 0}},
              "tags": null,
              "baseRowId": null,
              "defaultRowCommitVersion": null,
              "clusteringProvider": null}}
            """,
        ),
        _action(
            "remove",
            "**A file leaves the table.** Just a tombstone: the file stays on disk for time travel "
            "until VACUUM deletes it.",
            """
            {"remove": {
              "path": "part-00000-fc90….parquet",
              "dataChange": true,
              "deletionTimestamp": 1792427178690,
              "extendedFileMetadata": true,
              "partitionValues": {},
              "size": 1157}}
            """,
            mo.vstack(
                [
                    nf.eyebrow("protocol · metaData"),
                    mo.Html(
                        f'<div style="font-size:{theme.SIZE["small"]}; line-height:1.35;">'
                        + mo.md(
                            "**Only in 00000.json**, or when they change. *protocol*: the reader and writer "
                            "features an engine must support. *metaData*: table id, schema, partition columns "
                            "and settings."
                        ).text
                        + "</div>"
                    ),
                ],
                gap=0.6,
            ),
        ),
    ]
    nf.slide(
        mo.Html(
            '<div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:1.5cqw; align-items:start;">'
            + "".join(f'<div style="min-width:0;">{mo.as_html(_c).text}</div>' for _c in _cols)
            + "</div>"
        ),
        nf.caption(
            "_delta_log/00000000000000000003.json, written by delta-rs for the step-4 UPDATE, every field kept. On disk "
            "each action is a single line, stats is a JSON string and file names carry a full UUID (shortened here)."
        ),
        title="Inside a real log file",
        kicker="Delta Lake - one commit, action by action",
        pad_top="4.5cqw",
        gap="1.4cqw",
    )
    return


@app.cell
def _(mo, nf, theme):
    # Table formats, Iceberg: the same guarantees as Delta, kept in a tree of
    # metadata files behind a catalog instead of a log - then the main
    # differences between the two, side by side.
    _tone = theme.TONES["navy"]
    _levels = [
        ("Catalog", "points at the current metadata file"),
        ("Metadata file", "schema, partitions, every snapshot"),
        ("Manifest list", "one per snapshot: its manifests"),
        ("Manifests", "data files, with column min / max"),
        ("Data files", "Parquet, as in Delta"),
    ]
    _tree = "".join(
        (f'<div style="text-align:center; color:{_tone.muted}; font-size:{theme.SIZE["small"]}; line-height:1;">↓</div>' if _i else "")
        + f'<div style="background:#0a1440; border:1px solid {theme.MINT if _i == 0 else _tone.rule}; border-radius:{theme.SPACE["radius"]}; '
        f'padding:0.45cqw 1.2cqw; display:flex; justify-content:space-between; align-items:baseline; gap:1cqw; white-space:nowrap;">'
        f'<span style="font-size:{theme.SIZE["small"]}; font-weight:700;">{_name}</span>'
        f'<span style="font-size:{theme.SIZE["caption"]}; color:{_tone.muted};">{_what}</span></div>'
        for _i, (_name, _what) in enumerate(_levels)
    )
    _rows = [
        ("Born at", "Netflix, 2017", "Databricks, 2019"),
        ("Table state", "a tree of metadata files", "a log of JSON commits"),
        ("A commit is", "one atomic pointer swap in the catalog", "writing the next numbered JSON file"),
        ("Catalog", "needed, to find the current version", "optional: the folder is the table"),
        ("Partitioning", "hidden, and can change later", "partition columns, or liquid clustering"),
        ("At home in", "Snowflake, AWS, Trino, Flink", "Databricks, Microsoft Fabric"),
    ]
    _cell = f"padding:0.55cqw 0.8cqw; border-bottom:1px solid {_tone.rule}; text-align:left; vertical-align:top;"
    _table = (
        f'<table style="border-collapse:collapse; width:100%; font-size:{theme.SIZE["small"]}; line-height:1.35;">'
        f'<thead><tr><th style="{_cell}"></th>'
        f'<th style="{_cell} color:{theme.MINT};">Iceberg</th><th style="{_cell} color:{_tone.muted};">Delta Lake</th></tr></thead><tbody>'
        + "".join(
            f'<tr><td style="{_cell} color:{_tone.muted}; white-space:nowrap;">{_k}</td><td style="{_cell}">{_ice}</td>'
            f'<td style="{_cell} color:{_tone.muted};">{_delta}</td></tr>'
            for _k, _ice, _delta in _rows
        )
        + "</tbody></table>"
    )
    nf.slide(
        nf.two_col(
            mo.vstack(
                [
                    nf.tool("Apache Iceberg", "logos/iceberg.svg", note="Parquet files plus a tree of metadata",
                            layout="row", height=theme.pt(24)),
                    mo.Html(_tree),
                ],
                gap=0.8,
            ),
            mo.vstack([nf.eyebrow("Main differences with Delta Lake"), mo.Html(_table)], gap=1.4),
            ratio=(1, 1.15),
            gap="3cqw",
        ),
        nf.body(
            "**The same idea:** ACID transactions, time travel, schema evolution and MERGE on plain Parquet files - "
            "and converging (Delta *UniForm* also writes Iceberg metadata)."
        ),
        title="Apache Iceberg: the same guarantees, a different shape",
        kicker="Data formats - table formats",
        pad_top="4.5cqw",
        gap="1.6cqw",
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
    return


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
def _(platform_step):
    platform_step("transformation", "Transformation: from raw to ready", "Spark and dbt")
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
def _(platform_step):
    platform_step(
        "serving", "Serving: dashboards and BI",
        "the open-source dataviz ecosystem, Superset and Metabase, D3, and dashboards in the browser with WebAssembly",
    )
    return


@app.cell
def _(mo, nf, theme):
    # Dataviz, overview: the ecosystem as a spectrum, from clicking to
    # coding. Logos come from assets/logos/; a missing one falls back to an
    # initials chip.
    _layers = [
        ("BI apps (low/no code)", [
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
        ("Run in the browser with WASM/GPU", [
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
def _(dashboard, mo, pd):
    from perspective.widget import PerspectiveWidget

    # The Perspective slide's widget: the fleet's P&L, one row per plant,
    # day and line - revenue (+, from the grid settlement, with the energy
    # behind it) and every cost line (-, from the finance system). Summed,
    # the bars are the margin. binding_mode="client-server": Python ships the
    # table to the browser once, as Arrow, and Perspective's WASM engine does
    # every pivot, filter and chart from there - no server calls.
    _cols = ["date", "plant", "country", "line", "kind", "amount_eur", "energy_kwh"]
    _names = {"name": "plant", "country_code": "country"}  # readable in Perspective's column list
    _revenue = dashboard.defs["gold"].rename(columns=_names).assign(
        line="Revenue", kind="revenue", amount_eur=lambda d: d["revenue_eur"], energy_kwh=lambda d: d["energy_exported_kwh"]
    )[_cols]
    _costs = dashboard.defs["costs"].rename(columns={"cost_date": "date", "category": "line", "cost_type": "kind", **_names}).assign(
        amount_eur=lambda d: -d["amount_eur"], energy_kwh=0.0
    )[_cols]
    _pnl = pd.concat([_revenue, _costs], ignore_index=True)
    perspective_view = mo.ui.anywidget(
        PerspectiveWidget(
            _pnl,
            binding_mode="client-server",
            plugin="Y Bar",
            expressions={"month": "bucket(\"date\", 'M')"},
            group_by=["month"],
            split_by=["line"],
            columns=["amount_eur"],
            theme="Pro Dark",
            settings=False,  # the presenter opens the panel live
        )
    )
    return (perspective_view,)


@app.cell
def _(mo, nf, perspective_view):
    # Dataviz, Perspective live: the fleet's P&L, pivoted and charted in the
    # browser. Open the settings and drag fields.
    nf.slide(
        # fixed-pixel widget: Perspective draws itself 520px tall, so give it a
        # 1150x520 canvas and zoom that to the slide's width
        mo.Html(
            f'<div style="container-type:inline-size; width:100%;">'
            f'<div style="width:1150px; height:520px; overflow:hidden; zoom:calc(100cqw / 1150px);">'
            f"{mo.as_html(perspective_view).text}</div></div>"
        ),
        nf.caption(
            "The fleet's P&L by month: revenue up, every cost line down - the net is the margin. Open the settings (top left): "
            "split by plant or country, switch to a datagrid, filter a year - nothing goes back to Python."
        ),
        title="Perspective: a pivot engine in WebAssembly",
        kicker="Data visualization - WASM, live",
        pad_top="4.5cqw",
        gap="1.2cqw",
    )
    return


@app.cell
def _(platform_step):
    platform_step("orchestration", "Orchestration: running it all on schedule", "Airflow and Prefect")
    return


@app.cell
def _(assets, mo, nf, theme):
    # Orchestration, 2 of 3: Airflow - a DAG's overview, alternating slowly
    # between its graph and its runs (a CSS cross-fade), and the same
    # pipeline as a DAG file.
    _shot = lambda _f, _alt: assets.img(_f, alt=_alt, style={"aspect-ratio": "2 / 1", "object-fit": "cover", "object-position": "left top"}).text
    _swap = (
        "<style>@keyframes nf-airflow-swap { 0%, 42% { opacity: 0; } 50%, 92% { opacity: 1; } 100% { opacity: 0; } }</style>"
        '<div style="position:relative;">'
        f'{_shot("images/airflow-dag-graph.png", "Airflow 3: the graph view of a Dag")}'
        '<div style="position:absolute; inset:0; opacity:0; animation:nf-airflow-swap 16s ease-in-out infinite;">'
        f'{_shot("images/airflow-dag-runs.png", "Airflow 3: the runs of a Dag")}</div></div>'
    )
    nf.slide(
        nf.two_col(
            mo.vstack(
                [
                    mo.Html(_swap),
                    nf.caption("A Dag's overview in the Airflow 3 UI: the task graph, then every run and its state. From the Airflow docs."),
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
def _(platform_step):
    platform_step("deployment", "Deployment: running the platform", "Docker and Kubernetes")
    return


@app.cell
def _(diagram, nf):
    # Deployment, 1: Docker for everyone - the value is that the same box
    # runs anywhere. Builds in two steps, one per click.
    nf.slide(
        diagram("diagrams/docker.svg"),
        title="Docker: pack it once, run it anywhere",
        kicker="Deploying the platform",
        pad_top="5cqw",
    )
    return


@app.cell
def _(mo, nf, theme):
    # Deployment, 1b: the dashboard from this talk as an image - for the
    # technical part of the audience; skippable.
    nf.slide(
        nf.two_col(
            mo.vstack(
                [
                    nf.code(
                        '''
                        # Dockerfile: the solar dashboard, as an image
                        FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim
                        WORKDIR /app
                        COPY pyproject.toml uv.lock ./
                        RUN uv sync --frozen --no-dev --no-install-project
                        COPY presentation/ presentation/
                        EXPOSE 2718
                        CMD ["uv", "run", "marimo", "run",
                             "presentation/solar_dashboard.py", "--host", "0.0.0.0"]
                        ''',
                        language="docker",
                        size=8,
                        fit=(nf.CONTENT_CQW - 3) * 0.55,
                    ),
                    nf.code(
                        '''
                        docker build -t solar-dashboard:1.4 .
                        docker run -p 2718:2718 solar-dashboard:1.4

                        # every tool in this talk ships an official image
                        docker run -p 5432:5432 postgres
                        docker run -p 3000:3000 metabase/metabase
                        ''',
                        language="bash",
                        size=8,
                        fit=(nf.CONTENT_CQW - 3) * 0.55,
                    ),
                ],
                gap=0.8,
            ),
            nf.bullets(
                [
                    "**What you tested is what runs:** the same image on a laptop, in CI and in production",
                    "**Versions are tags:** a new release is a new image; rolling back is running the previous one",
                    "**Official images for everything:** Postgres, Airflow, Superset, Metabase, ClickHouse...",
                    "**docker compose:** the whole platform on one machine, from one file - often all a small team needs",
                ],
                size=theme.SIZE["small"],
            ),
            ratio=(11, 9),
            gap="3cqw",
        ),
        title="The dashboard as a Docker image",
        kicker="Deploying the platform",
        pad_top="4.5cqw",
    )
    return


@app.cell
def _(diagram, nf):
    # Deployment, 2: Kubernetes runs the platform's containers across a few
    # machines - placement, self-healing, scaling, rolling updates. Four
    # steps, one per click.
    nf.slide(
        diagram("diagrams/kubernetes.svg", width="94%"),
        title="Kubernetes: many containers, one platform",
        kicker="Deploying the platform",
        pad_top="4.5cqw",
    )
    return


@app.cell
def _(mo, nf, theme):
    # Deployment, 2b: what you actually write for Kubernetes - a declaration
    # for our own app, ready-made Helm charts for the big tools.
    nf.slide(
        nf.two_col(
            nf.code(
                '''
                # "two copies of the dashboard, always"
                apiVersion: apps/v1
                kind: Deployment
                metadata:
                  name: solar-dashboard
                spec:
                  replicas: 2
                  selector:
                    matchLabels: {app: solar-dashboard}
                  template:
                    metadata:
                      labels: {app: solar-dashboard}
                    spec:
                      containers:
                        - name: dashboard
                          image: registry.example.com/solar-dashboard:1.5
                          ports: [{containerPort: 2718}]
                ''',
                language="yaml",
                size=8,
                fit=(nf.CONTENT_CQW - 3) / 2,
            ),
            mo.vstack(
                [
                    nf.code(
                        '''
                        # the big tools come as ready-made charts
                        helm repo add apache-airflow https://airflow.apache.org
                        helm install airflow apache-airflow/airflow

                        helm repo add superset https://apache.github.io/superset
                        helm install superset superset/superset
                        ''',
                        language="bash",
                        size=8,
                        fit=(nf.CONTENT_CQW - 3) / 2,
                    ),
                    nf.bullets(
                        [
                            "**Everywhere:** managed on every cloud (EKS, AKS, GKE), or on your own servers (k3s, OpenShift)",
                            "**Declared, not scripted:** you say what should run; Kubernetes keeps it true",
                            "**But** it is a skill of its own: a small team may be better off with docker compose on one VM",
                        ],
                        size=theme.SIZE["small"],
                    ),
                ],
                gap=1.2,
            ),
            gap="3cqw",
        ),
        title="What you write for Kubernetes",
        kicker="Deploying the platform",
        pad_top="4.5cqw",
    )
    return


@app.cell
def _(assets, mo, nf):
    # OSS vs managed, intro: the question of the last part, in one picture.
    nf.slide(
        nf.two_col(
            mo.vstack(
                [
                    nf.lead("We've seen that you can build it. Should you?"),
                    nf.bullets(
                        [
                            "What does each option really cost?",
                            "How much work is it to build - and to run?",
                            "What do you get in return?",
                            "Who usually goes for open source?",
                        ],
                    ),
                ],
                gap=2,
            ),
            mo.Html(
                '<div style="background:#ffffff; border-radius:1.25cqw; padding:1cqw; width:88%; margin:0 auto;">'
                + assets.img("images/hmmm.png", alt="Open source or managed platform?", rounded=False).text
                + "</div>"
            ),
            ratio=(3, 2),
            gap="3cqw",
            align="center",
        ),
        title="Open source or a managed platform?",
        kicker="Open source or managed",
        pad_top="4.5cqw",
    )
    return


@app.cell
def _(assets, mo, nf, theme):
    # OSS vs managed, 1b: the trade-off at a glance - pros and cons of
    # assembling the platform from open-source tools vs adopting a managed one.
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
        kicker="Open source or managed",
        pad_top="4.5cqw",
        gap="1.4cqw",
    )
    return


@app.cell
def _(mo, nf, theme):
    # OSS vs managed, costs: what drives the bill on each side, row by row.
    # Prices: Microsoft list prices, US pay-as-you-go (Power BI Pro since
    # April 2025; Fabric F64 = 64 CU x $0.18/h x 730 h).
    _OSS, _MAN = theme.MINT, theme.BLUE
    _rows = [
        ("Licences", "none - the software is free", "€0",
         "per user or capacity: Power BI Pro $14 / user / month, Fabric F64 ~$8,400 / month", "grows with users"),
        ("Compute", "servers you size: your own hardware, or cloud VMs", "you size it",
         "consumption: credits, DBUs, capacity units - every query costs", "grows with use"),
        ("Storage & network", "disks or object storage, wherever you choose", "cheap",
         "cloud storage, plus egress fees to get data out", "grows with data"),
        ("People", "engineers to build, upgrade and run it", "the biggest line",
         "fewer platform engineers, plus FinOps to watch the bill", "smaller team"),
        ("Support", "community - or paid support, managed editions", "optional",
         "included, with SLAs", "included"),
        ("Leaving later", "open formats and code: cheap to move", "low",
         "proprietary formats and code: costly to migrate", "high"),
    ]
    _tone = theme.TONES["navy"]
    _cell = f"padding:0.6cqw {theme.SPACE['gap_sm']}; border-bottom:1px solid {_tone.rule}; vertical-align:middle;"

    def _tag(_t, _c):
        return (f'<span style="display:inline-block; white-space:nowrap; margin-left:0.5em; padding:0.05em 0.6em; '
                f'border-radius:999px; border:1px solid {_c}; color:{_c}; font-size:{theme.SIZE["caption"]}; font-weight:700;">{_t}</span>')

    _head = (f'<tr><th style="{_cell}"></th>'
             f'<th style="{_cell} text-align:left; color:{_OSS}; font-size:{theme.SIZE["body"]};">Open source</th>'
             f'<th style="{_cell} text-align:left; color:{_MAN}; font-size:{theme.SIZE["body"]};">Managed platform</th></tr>')
    _body = "".join(
        f"<tr><td style='{_cell} font-weight:700; white-space:nowrap; color:{_tone.muted};'>{_k}</td>"
        f"<td style='{_cell}'>{_o}{_tag(_ot, _OSS)}</td><td style='{_cell}'>{_m}{_tag(_mt, _MAN)}</td></tr>"
        for _k, _o, _ot, _m, _mt in _rows
    )
    nf.slide(
        mo.Html(
            f'<table style="width:100%; border-collapse:collapse; font-size:{theme.SIZE["small"]}; line-height:1.35;">'
            f"<thead>{_head}</thead><tbody>{_body}</tbody></table>"
        ),
        nf.body("**Open source moves the bill from licences to people.** Managed platforms move it from people to usage."),
        title="What drives the cost",
        kicker="Open source or managed",
        pad_top="4.5cqw",
        gap="1.4cqw",
    )
    return


@app.cell
def _(diagram, nf):
    # OSS vs managed, effort: everything below the waterline - what it takes
    # to build and run a platform from open-source tools. Two steps.
    nf.slide(
        diagram("diagrams/oss_effort.svg"),
        title="The work behind an open-source platform",
        kicker="Open source or managed",
        pad_top="4.5cqw",
    )
    return


@app.cell
def _(icon_cards, nf, theme):
    # OSS vs managed, control: what the extra effort buys you.
    nf.slide(
        nf.lead("The flip side of doing the work yourself: you are in control."),
        icon_cards(
            [
                ("wheel", "You decide what runs",
                 "Versions, upgrades and the roadmap are yours: no forced migrations, no retired features, no surprise price rises.",
                 "e.g. upgrade Airflow when it suits you, not the vendor", theme.MINT),
                ("toolbox", "The right tool for each job",
                 "Pick the best tool for every layer instead of one vendor's bundle - and swap it later, the data stays in open formats.",
                 "e.g. DuckDB in the notebook, ClickHouse for real time, Postgres for the app", theme.BLUE),
                ("code", "Build any feature",
                 "Custom visuals, analytics inside your product, your own permissions - without waiting on a third party's backlog.",
                 "e.g. the D3 race, the Perspective pivot, plant-level access", theme.PURPLE),
            ]
        ),
        title="More effort - but more control",
        kicker="Open source or managed",
        pad_top="4.5cqw",
        gap="2cqw",
    )
    return


@app.cell
def _(icon_cards, nf, theme):
    # OSS vs managed, who: the organisations that usually choose open source.
    nf.slide(
        icon_cards(
            [
                ("server", "Organisations with their own infrastructure",
                 "Data centres or a private cloud, run by their own ops team - and often data that may not leave it (sovereignty, regulation).",
                 "e.g. public sector, healthcare, banks, manufacturing", theme.MINT),
                ("growth", "Data as a core competence",
                 "Strong engineering teams for whom data is the product, or the competitive edge: they want control and build on it.",
                 "e.g. Airbnb gave us Airflow and Superset, Netflix Iceberg, Facebook Presto - now Trino", theme.BLUE),
                ("cap", "Academia and research",
                 "Open code and open formats make results easy to share and reproduce; budgets are tight; many run their own clusters.",
                 "e.g. Postgres and Spark came out of UC Berkeley, DuckDB out of CWI Amsterdam", theme.PURPLE),
            ]
        ),
        nf.body("**The common thread:** they already have the infrastructure or the skills - so the effort is "
                "smaller for them, and the control is worth more."),
        title="Who usually goes for open source",
        kicker="Open source or managed",
        pad_top="4.5cqw",
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
