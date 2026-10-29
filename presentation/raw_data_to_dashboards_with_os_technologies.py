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
    html_head_file="template/head.html",
)


@app.cell
def imports():
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
def notes_research(mo):
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
def slide_title(nf):
    nf.title_slide(
        "From raw data to dashboard with open source software",
        event="Ticino Data Conference - 2026",
        author="Dario Ruben Scanferlato, Nearform",
    )
    return


@app.cell
def slide_speaker(assets, nf):
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
def slide_agenda(nf):
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
def slide_disclaimers(nf):
    # Disclaimers, before the talk starts: what the code and diagrams are,
    # and how far my own experience goes.
    nf.slide(
        nf.bullets(
            [
                "This presentation contains some demonstrative code",
                "Most of the diagrams and code have been AI-generated",
                "I will present many open source technologies for the sake of comprehensiveness: "
                "I am not an expert in all of those, and I haven't tested them all in production settings",
            ]
        ),
        title="Disclaimers",
        page=4,
    )
    return


@app.cell
def slide_big_question(nf):
    nf.slide(
        title="Is it possible to create great dashboards from raw data using open source technologies?", align='center', page=5
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
def import_dashboard_app():
    from solar_dashboard import app as solar_app

    return (solar_app,)


@app.cell(hide_code=True)
async def embed_dashboard(solar_app):
    # `embed()` can't be called in the cell that imports the app - marimo
    # runs the embedded notebook in its own nested kernel, so every `mo.ui`
    # element (the filters, the click cross-filter) stays fully interactive
    # here, not just a static screenshot. `dashboard.defs` exposes every
    # top-level name the notebook defines (dataframes, charts, UI elements),
    # which the next few slides reuse directly instead of recomputing.
    dashboard = await solar_app.embed()
    return (dashboard,)


@app.cell(hide_code=True)
def slide_helpers(alt, assets, mo, nf, textwrap, theme):
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


    def chart_from(code, *, gold_dataset, var="chart", width=None, height=None):
        """Run a snippet shown on a slide and hand back the chart it builds,
        so the code on the slide is *exactly* the code that drew the chart.
        A stacked (vconcat) chart gets `width` x `height` per part."""
        scope = {"alt": alt, "gold_dataset": gold_dataset}
        exec(textwrap.dedent(code), scope)
        chart = scope[var]
        if hasattr(chart, "vconcat"):
            for _part in chart.vconcat:  # in place: copying would detach the shared selection
                _part.width, _part.height = width, height
        return chart

    def chart_step(n, label, code, gold_dataset, *, total=4):
        """One sub-slide of the "Plotting a chart" build-up.

        Sized for reading from the back of the room, with the chart as wide
        as possible: side margins of 4.5cqw instead of the template's 9%,
        the code font up to 9pt (fewer for a long snippet: 200/lines pt, so
        it fits without scrolling), and the code column only as wide as its
        longest line - the chart takes the rest. The chart is drawn 420px
        wide, no taller than the ~36cqw the slide has left, and zoomed to its
        column, with its text set larger than Vega's 10-11px defaults and
        any legend below it."""
        _lines = textwrap.dedent(code).strip().splitlines()
        _size = min(9, 200 / len(_lines))
        _pad_x = 4.5
        # monospace glyphs are ~0.61em wide, plus the block's side padding
        _code_cqw = max(map(len, _lines)) * 0.61 * _size * theme.PT / theme.DECK_W * 100 + 5.2
        _chart_cqw = 100 - 2 * _pad_x - 2.5 - _code_cqw
        _chart = chart_from(code, gold_dataset=gold_dataset)
        if "legend" not in _chart.encoding.color.to_dict():
            # every plant's name ends in "Solar Farm": drop it, so that the
            # legend fits in two columns under the plot
            _chart.encoding.color = _chart.encoding.color.legend(
                labelExpr="replace(datum.label, ' Solar Farm', '')"
            )
        _chart = (
            _chart.configure_axis(labelFontSize=16, titleFontSize=17)
            # under the plot, not beside it: the plant names would take half its width
            .configure_legend(labelFontSize=16, titleFontSize=17, orient="bottom", columns=2)
            .configure_title(fontSize=20)
        )
        return nf.slide(
            nf.two_col(
                nf.code(code, size=_size, fit=_code_cqw),
                scaled_chart(_chart, width=420, height=round(min(420, 420 * 36 / _chart_cqw))),
                ratio=(round(_code_cqw, 2), round(_chart_cqw, 2)),
                gap="2.5cqw",
            ),
            title="Plotting a chart",
            kicker=f"Step {n} of {total}: {label}",
            pad_top="5cqw",
            pad_x=f"{_pad_x}cqw",
        )

    #: The cross-filtering slides' first chart; the second slide builds on it.
    AREA_CODE = textwrap.dedent('''
        plant_sel = alt.selection_point(fields=["name"], on="click", clear="dblclick")

        area = (
            alt.Chart(gold_dataset)
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
def slide_live_dashboard(dashboard, full_bleed_slide):
    # Scale by the dashboard's own chart width, not the helper's default:
    # the embedded notebook renders without its grid layout, so
    # nf-dashboard.css's zoom rules (keyed on `.react-grid-item`) don't
    # apply here and the Vega chart sits at its fixed `DASHBOARD_WIDTH` -
    # a wider wrapper leaves that difference as an empty strip on the right.
    full_bleed_slide(dashboard.output, natural_width=dashboard.defs["DASHBOARD_WIDTH"])
    return


@app.cell
def slide_dashboard_pipeline(assets, nf):
    # How the dashboard on the previous slide works, as one picture: marimo
    # runs the Python, and reading, transforming and displaying the data all
    # happen inside it; the dashboard and this deck are output modes of the
    # same kind of notebook. A hand-drawn SVG in assets/diagrams/, inlined so
    # it animates and uses the deck's fonts.
    nf.slide(
        assets.svg("diagrams/dashboard_pipeline.svg"),
        title="How does the dashboard work?",
        pad_top="5cqw",
    )
    return


@app.cell
def slide_ingesting_raw_data(dashboard, mo, nf):
    # One tab per dataset: what it is, the code that loads it, a few rows.
    # Switching tab switches all three.
    _datasets = {
        "readings": (
            "Contains time series of readings from solar AC power (kW) sensors.",
            '''
            readings = pd.read_csv(
                "data/solar/bronze/sensor_readings.csv.gz",
                parse_dates=["timestamp"],
            )
            ''',
            nf.dataframe(dashboard.defs["sensor_readings"], max_rows=3),
        ),
        "sensors": (
            "Master data for installed sensors, includes product information and where it is installed",
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
            "Indicates how much energy was transferred from plants to the grid",
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
            "Solar production plant master data",
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
        # This slide is denser than most (code + tabs + a table): the
        # template's usual top margin and inter-block rhythm, sized for a
        # sparse title+bullets slide, left this one taller than the frame -
        # buy the room back here instead of shrinking the table further.
        pad_top="5cqw",
        gap="1.2cqw",
    )
    return


@app.cell
def slide_data_model_overlay(assets, mo, theme):
    # Ingesting, fragment: the data model behind the tabs, as a star schema
    # - fact tables (readings, settlement, and the daily per-plant table the
    # dashboard is built on) around the sensor and plant dimensions. The slide
    # above is already full, so this is revealed (next click) as a panel
    # *over* the tabs, below the slide's title, rather than under them. The
    # diagram scales to the panel's height (a flex column, the svg at 100%), so
    # it never spills past the slide whatever size the slide renders at.
    _tone = theme.TONES["navy"]
    mo.Html(
        # marimo wraps each output in a `position:relative` box - here a
        # zero-height one under the slide. Making just that wrapper static
        # anchors the panel to the slide's own box instead.
        "<style>.output:has(> [data-nf-overlay]) { position: static !important; }"
        " [data-nf-overlay] svg { width: 100%; height: 100%; }</style>"
        f'<div data-nf-overlay style="position:absolute; left:0; right:0; top:15.6%; bottom:0; z-index:100; '
        # the slide sits 20px in from this box, then pads 8.96% of its own width
        f'background:{theme.NAVY}; padding:0 calc(16.4px + 8.96%) 2.5%; box-sizing:border-box; '
        f"display:flex; flex-direction:column; overflow:hidden; "
        f'container-type:inline-size; font-family:{theme.SANS}; color:{_tone.fg};">'
        f'<div style="color:{theme.MINT}; font-size:{theme.SIZE["small"]}; font-weight:600; '
        f'text-transform:uppercase; letter-spacing:0.12em; margin-bottom:1.2cqw;">The data model</div>'
        f'<div style="flex:1; min-height:0;">{assets.svg("diagrams/data_model.svg").text}</div>'
        "</div>"
    )
    return


@app.cell
def slide_bronze_to_gold(dashboard, nf):
    _code = '''
    gold_dataset = (
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
        nf.dataframe(dashboard.defs["gold_dataset"][_cols], max_rows=2),
        title="From bronze to gold",
        kicker="aggregate, join, derive",
        pad_top="5cqw",
        gap="1.2cqw",
    )
    return


@app.cell
def slide_chart_step1(chart_step, dashboard):
    chart_step(
        1,
        "the simplest chart",
        '''
        chart = alt.Chart(gold_dataset).mark_line().encode(
            x="date:T",  # T: temporal - a time axis
            y="energy_generated_kwh:Q",  # Q: quantitative
            color="name:N",  # N: nominal - one colour per plant
        )
        ''',
        dashboard.defs["gold_dataset"],
    )
    return


@app.cell
def slide_chart_step2(chart_step, dashboard):
    chart_step(
        2,
        "stack the plants into areas",
        '''
        # lines -> filled areas
        chart = alt.Chart(gold_dataset).mark_area().encode(
            x="date:T",
            y=alt.Y(
                "energy_generated_kwh:Q",
                stack="zero",  # plants stacked on top of each other
            ),
            color="name:N",
        )
        ''',
        dashboard.defs["gold_dataset"],
    )
    return


@app.cell
def slide_chart_step3(chart_step, dashboard):
    chart_step(
        3,
        "titles, outline and smooth curves",
        '''
        chart = (
            alt.Chart(gold_dataset)
            .mark_area(
                line={"strokeWidth": 1.5},  # outline each area
                interpolate="monotone",  # smooth curves
            )
            .encode(
                x=alt.X("date:T", title=None).axis(format="%b %Y"),
                y=alt.Y(
                    "energy_generated_kwh:Q",
                    title="Energy generated (kWh)",
                    stack="zero",
                    axis=alt.Axis(format="~s"),  # 2.2M, not 2200000
                ),
                color=alt.Color("name:N", legend=None),
                order=alt.Order("name:N"),  # fixed stacking order
            )
            .properties(title="Daily energy production by plant")
        )
        ''',
        dashboard.defs["gold_dataset"],
    )
    return


@app.cell
def slide_chart_step4(chart_step, dashboard):
    chart_step(
        4,
        "tooltips on hover",
        '''
        chart = (
            alt.Chart(gold_dataset)
            .mark_area(
                line={"strokeWidth": 1.5},
                interpolate="monotone",
            )
            .encode(
                x=alt.X("date:T", title=None).axis(format="%b %Y"),
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
                    alt.Tooltip("energy_generated_kwh:Q",
                                title="kWh", format=",.0f"),
                ],
            )
            .properties(title="Daily energy production by plant")
        )
        ''',
        dashboard.defs["gold_dataset"],
    )
    return


@app.cell
def filter_widgets(DateRangeTimeline, dashboard, mo, pd, theme):
    # Fresh widgets, not the *same* objects as the dashboard slide: a
    # marimo UI element is bound to exactly one live DOM mount, so
    # displaying `dashboard.defs["location_filter"]` a second time here
    # would leave an inert copy. These are independent of the dashboard's
    # own filters. (A UI element's `.value` can't be read in the cell that
    # creates it, hence the split from the slide cells below.)
    _plants = dashboard.defs["dim_plants"]
    _gold = dashboard.defs["gold_dataset"]

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
def slide_filter_slider(mo, nf, slider):
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
        kicker="Adding a simple slider",
        pad_top="5cqw",
        gap="1.2cqw",
    )
    return


@app.cell
def slide_filter_multiselect(dashboard, location_filter, mo, nf):
    _code = """
    plant_names = {
        name.removesuffix(" Solar Farm"): name  # short label -> full value
        for name in sorted(plants["name"])
    }

    location_filter = mo.ui.multiselect(
        options=plant_names,
        value=list(plant_names),  # everything selected to start
    )
    location_filter

    # in another cell: re-runs whenever the selection changes
    selected = plants[plants["name"].isin(location_filter.value)]
    selected[["name", "country_code", "capacity_mw", "status"]]
    """
    _plants = dashboard.defs["dim_plants"]
    _selected = _plants[_plants["name"].isin(location_filter.value)]
    # `wrap=True` is load-bearing: with all 8 plants selected the chip row
    # is wide, and unwrapped it pushed past the slide's right edge.
    nf.slide(
        nf.code(_code, size=9, fit=nf.CONTENT_CQW),
        mo.Html(f'<div class="dark" style="zoom:1.4;">{mo.as_html(mo.hstack([location_filter], justify="start", wrap=True)).text}</div>'),
        nf.dataframe(
            _selected[["name", "country_code", "capacity_mw", "status"]].sort_values("name"),
            max_rows=len(_plants),
            label=f"{len(_selected)} of {len(_plants)} plants",
        ),
        title="Adding filters with marimo ui elements",
        kicker="Adding a multiselect",
        pad_top="5cqw",
        gap="1.2cqw",
    )
    return


@app.cell
def slide_filter_date_range(mo, nf, period_filter):
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
def slide_crossfilter_step1(
    AREA_CODE,
    chart_from,
    dashboard,
    mo,
    nf,
    scaled_chart,
):
    _chart = chart_from(AREA_CODE, var="area", gold_dataset=dashboard.defs["gold_dataset"])
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
def slide_crossfilter_step2(
    AREA_CODE,
    chart_from,
    dashboard,
    mo,
    nf,
    scaled_chart,
):
    _new = '''
    # a second chart, reusing the same selection object
    bars = (
        alt.Chart(gold_dataset)
        .mark_bar()
        .encode(
            x=alt.X("sum(revenue_eur):Q", title="Revenue (EUR)", axis=alt.Axis(format="~s")),
            y=alt.Y("name:N", sort="-x", title=None),
            color=alt.Color("name:N", legend=None),
            opacity=alt.condition(plant_sel, alt.value(0.85), alt.value(0.15)),
        )
        .add_params(plant_sel)
    )

    chart = area & bars  # we create the final chart stacking the two previous objects
    '''
    _chart = chart_from(AREA_CODE + _new, gold_dataset=dashboard.defs["gold_dataset"], width=340, height=150)
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
def slide_what_if(mo, nf):
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

        title="Great, we have a dashboard, but what if..."
    )
    return


@app.cell
def slide_data_platform_diagram(assets, nf):
    # What a data platform is, as one picture rather than a list: the data
    # path left to right (ingest, store, transform, visualize), orchestration
    # over it, observability and governance across it, dev tooling and
    # infrastructure under it.
    nf.slide(
        assets.svg("diagrams/data_platform.svg"),
        title="Sounds like you need a data platform",
        pad_top="5cqw",
    )
    return


@app.cell
def slide_data_platforms_compared(assets, mo, nf, theme):
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
        """Tab labels run through mo.md, so an inline <img> renders in the tab strip.
        The `data-nf-platform-tab` marker lets nearform.css hide this strip's
        scrollbar (see template/theme.py)."""
        if not assets.exists(_logo):
            return f"<span data-nf-platform-tab>{_name}</span>"
        _mark = assets.img(
            _logo, width="auto", rounded=False, alt=_name,
            style={"height": "1.1em", "object-fit": "contain",
                   "display": "inline-block", "vertical-align": "middle"},
        ).text
        return f"<span data-nf-platform-tab>{_mark} {_name}</span>"


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
def platform_map_helpers(mo, nf, theme):
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

    def platform_step(key, title):
        """A section opener: the map with one part lit."""
        return nf.slide(
            platform_map(key, width="92%"),
            title=title,
            kicker="Sitching together an OS data platform",
            pad_top="5cqw",
            gap="2.5cqw",
        )

    return platform_map, platform_step


@app.cell
def slide_can_we_go_open_source(nf, platform_map):
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
def slide_opener_ingestion(platform_step):
    platform_step("ingestion", "Ingestion: getting the raw data in")
    return


@app.cell
def slide_airbyte(assets, mo, nf, theme):
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
                            "**600+ connectors:** databases, APIs, warehouses, lakes, SaaS.",
                            "**Point and click UI:** to configure source, destination, and schedule",
                            "**Incremental syncs and Change data capture:** to avoid full refreshes",
                            "**Custom connectors** can be implemented when missing",
                            "**Self-host it** on Docker or Kubernetes, or use the managed platform (Airbyte Cloud)",
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
def slide_opener_storage(platform_step):
    platform_step("storage", "Storing the data")
    return


@app.cell
def slide_parquet_intro(mo, nf, theme):
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
        title="Parquet: the file format used in data lakes",
        kicker="Data formats",
        pad_top="5cqw",
        gap="2cqw",
    )
    return


@app.cell
def slide_parquet_columnar(assets, nf):
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
def slide_parquet_compression(dashboard, diagram, nf):
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
        diagram("diagrams/parquet_encoding.svg", width="90%"),
        # the measured sizes come in last, after the diagram's three steps
        nf.fragment(nf.stats(
            [
                (f"{_size(_csv_bytes)} → {_size(_pq_bytes)}", "sensor readings: CSV vs Parquet",
                 f"{_csv_bytes / _pq_bytes:.0f}x smaller  ({len(_raw):,} rows)"),
                (f"{_size(_sensor_csv)} → {_size(_sensor_pq)}", "the sensor_id column alone",
                 f"{_sensor_csv / _sensor_pq:.0f}x smaller  ({len(_raw):,} rows)"),
            ]
        ), index=4),
        title="Compressing column data",
        kicker="Parquet - why the files are small",
        pad_top="4cqw",
    )
    return


@app.cell
def slide_parquet_skipping(diagram, nf):
    # Parquet, 2 of 3: row groups, column chunks and the footer's min/max
    # statistics - how a filter skips most of the file without reading it.
    nf.slide(
        diagram("diagrams/parquet_anatomy.svg", width="88%"),
        nf.body(
            "*Predicate pushdown* - it means filtering the data at the source, before it is retrieved"
        ),
        title="Optimizing reads with filters",
        kicker="Parquet - inside the file",
        pad_top="5cqw",
    )
    return


@app.cell
def slide_delta_intro(mo, nf, theme):
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
                            "Built at **Databricks**, by the team behind Spark",
                            "open-sourced in **2019** and now hosted by the Linux Foundation",
                            "The problem: due to its compressed nature, to update a Parquet file you rewrite it entirely"
                            "You can't just update or delete a row",
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
                    nf.eyebrow("Where it's used"),
                    nf.tool("Databricks", "logos/databricks.svg", note="the default format of every table",
                            layout="row", height=theme.pt(24)),
                    nf.tool("Microsoft Fabric", "logos/fabric.svg", note="OneLake stores every table as Delta Parquet",
                            layout="row", height=theme.pt(24)),
                    nf.bullets(
                        [
                            "Widely supported",
                            "Open specification",
                        ],
                        size=theme.SIZE["small"],
                    ),
                ],
                gap=1,
            ),
            gap="3cqw",
        ),
        title="Delta Lake: turning a bunch of files in an organized table",
        kicker="Data formats - table formats",
        pad_top="5cqw",
        gap="2cqw",
    )
    return


@app.cell
def delta_step_helper(mo, nf, theme):
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
def slide_delta_step1_create(delta_step):
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
def slide_delta_step2_insert(delta_step):
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
def slide_delta_step3_delete(delta_step):
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
        "",
        aside="We can avoid re-writing the new file in newer version of Delta Lake by leveraging **deletion vectors**, which are compressed bitmaps representing deleted rows",
    )
    return


@app.cell
def slide_delta_step4_update(delta_step):
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
def slide_delta_real_log(mo, nf, theme):
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
        title="Inside a real log file",
        kicker="Delta Lake - one commit, action by action",
        pad_top="4.5cqw",
        gap="1.4cqw",
    )
    return


@app.cell(hide_code=True)
def slide_delta_schema_evolution(mo, nf, theme):
    # Delta, schema evolution: adding a column is a metadata-only commit - no
    # Parquet file is rewritten; files written before it read the new column
    # as NULL. Then the rules around it: enforcement, merging on write, and
    # renames / drops through column mapping.
    _tone = theme.TONES["navy"]
    _MONO = "var(--marimo-monospace-font, ui-monospace, SFMono-Regular, Menlo, monospace)"
    _cell = f"padding:0.3cqw 0.8cqw; border-bottom:1px solid {_tone.rule}; text-align:left; white-space:nowrap;"
    _head = "".join(
        f'<th style="{_cell} color:{theme.MINT if _c == "temp_c" else _tone.muted}; font-weight:500; '
        f'text-transform:uppercase; letter-spacing:0.06em;">{_c}</th>'
        for _c in ("ts", "sensor_id", "ac_power_kw", "temp_c")
    )
    _body = "".join(
        f'<tr><td style="{_cell}">{_ts}</td><td style="{_cell}">{_s}</td><td style="{_cell}">{_kw}</td>'
        f'<td style="{_cell} color:{_tone.muted};">NULL</td></tr>'
        for _ts, _s, _kw in [("2026-06-01 12:00", "S1", 4.2), ("2026-06-01 12:00", "S2", 4.3), ("2026-06-01 12:15", "S2", 4.4)]
    )
    _table = (
        f'<table style="border-collapse:collapse; width:100%; font-family:{_MONO}; font-size:{theme.SIZE["small"]};">'
        f"<thead><tr>{_head}</tr></thead><tbody>{_body}</tbody></table>"
    )
    _panel = lambda eyebrow, body: mo.vstack([nf.eyebrow(eyebrow), body], gap=1.4)
    nf.slide(
        nf.two_col(
            mo.vstack(
                [
                    _panel("1 · SQL", nf.code(
                        """
                        -- the panels' temperature, from now on
                        ALTER TABLE readings
                        ADD COLUMNS (temp_c DOUBLE);
                        """,
                        language="sql", size=10, fit=39.7,
                    )),
                    _panel("2 · _delta_log/00004.json - trimmed", nf.code(
                        """
                        {"commitInfo": {"operation": "ADD COLUMNS"}}
                        {"metaData": {"schema": [
                          "ts timestamp", "sensor_id string",
                          "ac_power_kw double", "temp_c double"]}}
                        """,
                        language="json", size=10, fit=39.7,
                    )),
                ],
                gap=1.4,
            ),
            mo.vstack(
                [
                    _panel("3 · Table snapshot", mo.Html(
                        _table + nf.caption("Still read from part-0003: no data file was rewritten.").text
                    )),
                    nf.bullets(
                        [
                            "**Enforcement:** a write that doesn't match the schema fails, instead of leaving broken files",
                            "**Evolve on write:** *mergeSchema* in Spark, *schema_mode=\"merge\"* in delta-rs, adds new columns in the same commit",
                            "**Rename or drop:** turn on column mapping (*delta.columnMapping.mode = name*) - still no rewrite",
                        ],
                        size=theme.SIZE["small"],
                    ),
                ],
                gap=1.4,
            ),
            gap="2.5cqw",
        ),
        nf.body("**The schema lives in the log too.** Changing it is one more commit, so it is all-or-nothing and old versions keep their old schema."),
        title="Schema evolution: changing the columns",
        kicker="Delta Lake - schema evolution",
        pad_top="4cqw",
        gap="1.6cqw",
    )
    return


@app.cell
def slide_iceberg(mo, nf, theme):
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
def slide_engines_overview(diagram, nf):
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
def duckdb_editor(mo):
    # The DuckDB slide's editor. Created here, shown on the next slide: a UI
    # element's value can't be read in the cell that creates it.
    duckdb_sql = mo.ui.code_editor(
        value=(
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
def slide_duckdb_live(bronze, dashboard, duckdb_sql, mo, nf):
    import time

    import duckdb

    # Engines, 2 of 4: DuckDB, live. The query runs in this notebook's own
    # process on every edit - against the raw CSV, or `gold_dataset`, the
    # dashboard's DataFrame, registered as a table.
    _editor_w = 450
    _con = duckdb.connect()
    _con.execute(f"SET file_search_path = '{bronze.BRONZE_DIR.parents[2].as_posix()}'")
    _con.register("gold_dataset", dashboard.defs["gold_dataset"])
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
                    nf.caption("Edit me - it re-runs."),
                ],
                gap=0.4,
            ),
            _result,
            ratio=(1, 1),
            gap="2.5cqw",
        ),
        nf.cards(
            [
                ("In-process", "similar to SQLite but aimed at analytical workloads"),
                ("Reads everything", "Parquet, CSV, JSON, Iceberg, Delta; local or S3"),
                ("Fast on one machine", "columnar, vectorized, larger-than-memory"),
            ]
        ),
        title="DuckDB: an in-process analytical database",
        pad_top="4.5cqw",
        gap="1.4cqw",
    )
    return


@app.cell
def slide_postgres(assets, mo, nf, theme):
    # Engines, 3 of 4: Postgres. Survey numbers: Stack Overflow Developer
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
                            "Fully featured and reliable database with rich SQL",
                            "Extensions for optimized geo, vector or time-series data structures",
                            "Transactional database (but some plugins exist for columnar storage)",
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
def slide_clickhouse(assets, mo, nf, theme):
    # Engines, 4 of 4: ClickHouse - why it's fast on the left; MergeTree on
    # the right, hidden until the first click (it then steps through its own
    # four clicks).
    nf.slide(
        nf.two_col(
            nf.bullets(
                [
                    "**Real-time analytics:** fast queries over billions of rows, for many concurrent users",
                    "**Columnar, compressed, vectorized** - same concepts as Parquet, but inside a server",
                    "**MergeTree:** inserts land as small sorted parts, merged in the background",
                    "**Sparse primary index:** skips blocks of rows, like Parquet's row groups",
                    "**Materialized views** update as the data arrives",
                    "Apache 2.0 - can be self-hosted or used through ClickHouse Cloud",
                ],
                size=theme.SIZE["small"],
            ),
            mo.Html(
                '<div class="fragment" data-fragment-index="1">'
                + assets.svg("diagrams/clickhouse_mergetree.svg").text
                + "</div>"
            ),
            ratio=(1, 1),
            gap="2.5cqw",
            align="center",
        ),
        title="ClickHouse: an OLAP database for real time analytics",
        kicker="Storage and query engines",
        pad_top="4.5cqw",
    )
    return


@app.cell
def slide_opener_transformation(platform_step):
    platform_step("transformation", "Transformation: from raw to ready")
    return


@app.cell
def slide_transformation_styles(mo, nf, theme):
    # Transformation, two styles: SQL inside the database (dbt on top), or
    # dataframes in your own process or on a cluster. Not either/or: most
    # dataframe engines also take SQL.
    def _side(eyebrow, tools, points, snippet, language):
        return mo.vstack(
            [
                nf.eyebrow(eyebrow),
                mo.hstack(
                    [nf.tool(_name, _logo, layout="row", height=theme.pt(15)) for _name, _logo in tools],
                    justify="start", gap=1.0, wrap=True,
                ),
                nf.bullets(points, size=theme.SIZE["small"]),
                nf.code(snippet, language=language, size=9, fit=(nf.CONTENT_CQW - 2.5) / 2),
            ],
            gap=1.1,
        )


    nf.slide(
        nf.two_col(
            _side(
                "SQL inside the database",
                [("PostgreSQL", "logos/postgresql.svg"), ("ClickHouse", "logos/clickhouse.svg"),
                 ("DuckDB", "logos/duckdb.svg"), ("dbt", "logos/dbt.svg")],
                [
                    "The data stays where it is: the database does the work",
                    "Use dbt to manage SQL code, and deploy it to your database/data lake",
                ],
                """
                SELECT plant_id, date,
                       sum(energy_kwh) as energy_generated_kwh
                FROM SensorReadings
                GROUP BY plant_id, date
                """,
                "sql",
            ),
            _side(
                "Dataframes",
                [("pandas", "logos/pandas.svg"), ("Polars", "logos/polars.svg"), ("Spark", "logos/spark.svg")],
                [
                    "Interact with dataframes through some programming language",
                    "Popular tools are pandas (when working locally) and Spark (for distributed workloads)",
                    "I highly recommend the polars library, which now supports both local, and distributed workloads",
                ],
                """
                gold_dataset = (
                    polars.scan_parquet("sensors/readings/*.parquet")
                    .group_by("plant_id", "date")
                    .agg(pl.col("energy_kwh").sum()
                           .alias("energy_generated_kwh"))
                    .collect()
                )
                """,
                "python",
            ),
            gap="2.5cqw",
        ),
        nf.body(
            "Note that most dataframe engines also support SQL queries on their underlying data"
        ),
        title="Transformation: SQL or dataframes?",
        kicker="Transformation - two styles",
        pad_top="3.5cqw",
        gap="1.4cqw",
    )
    return


@app.cell(hide_code=True)
def bar_chart_helper(mo, theme):
    # Horizontal bar charts for the benchmark slides, in plain HTML: one
    # series, so one colour; values labelled at the bar end; the scale is
    # linear, or log when the values span orders of magnitude.
    import math as _math

    _tone = theme.TONES["navy"]


    def bar_chart(rows, *, fmt, log=False, missing="did not run"):
        """rows: (label, value or None). Bars sized against the largest value."""
        _top = max(_v for _, _v in rows if _v is not None)
        _size = (lambda v: _math.log10(v) / _math.log10(_top)) if log else (lambda v: v / _top)
        _html = ""
        for _label, _v in rows:
            if _v is None:
                _bar = f'<span style="color:{_tone.muted}; font-size:{theme.SIZE["small"]};">{missing}</span>'
            else:
                _w = max(_size(_v), 0.02) * 78
                _bar = (
                    f'<div style="display:flex; align-items:center; gap:0.8cqw;">'
                    f'<div style="width:{_w:.1f}%; height:2.1cqw; background:{theme.MINT}; border-radius:0 4px 4px 0;"></div>'
                    f'<span style="font-size:{theme.SIZE["small"]}; font-variant-numeric:tabular-nums;">{fmt(_v)}</span></div>'
                )
            _html += (
                f'<div style="display:grid; grid-template-columns:9cqw 1fr; align-items:center; gap:1cqw; margin-bottom:0.7cqw;">'
                f'<span style="font-size:{theme.SIZE["small"]}; text-align:right;">{_label}</span>{_bar}</div>'
            )
        return mo.Html(f'<div style="border-left:1px solid {_tone.rule}; padding-left:0;">{_html}</div>')

    return (bar_chart,)


@app.cell(hide_code=True)
def slide_benchmark_pdsh(bar_chart, mo, nf):
    # Transformation, performance 1: Polars' PDS-H benchmark - the 22
    # TPC-H-derived queries - on one AWS c7a.24xlarge (96 vCPU, 192 GB),
    # results of May 2025. Total seconds, lower is better. Polars with its
    # streaming engine; pandas could not run at SF-100.
    _panels = {
        "Scale factor 10 · ~10 GB": [("Polars", 3.89), ("DuckDB", 5.87), ("PySpark", 120.11), ("pandas", 365.71)],
        "Scale factor 100 · ~100 GB": [("DuckDB", 19.65), ("Polars", 23.94), ("PySpark", 312.43), ("pandas", None)],
    }
    nf.slide(
        nf.two_col(
            *[
                mo.vstack([nf.eyebrow(_name), bar_chart(_rows, fmt=lambda v: f"{v:,.1f} s", missing="out of memory")], gap=1.4)
                for _name, _rows in _panels.items()
            ],
            gap="4cqw",
        ),
        nf.caption(
            "Total time for 22 queries, lower is better. PDS-H, a TPC-H-derived benchmark run by Polars (pola.rs/posts/benchmarks), "
            "May 2025: Polars 1.30 (streaming engine), DuckDB 1.3, PySpark 4.0, pandas 2.2, on one AWS c7a.24xlarge (96 vCPU, 192 GB)."
        ),
        title="Benchmarking dataframe libraries",
        kicker="Transformation - performance",
        pad_top="5cqw",
        gap="3cqw",
    )
    return


@app.cell(hide_code=True)
def slide_benchmark_clickbench(bar_chart, mo, nf, theme):
    # Transformation, performance 2: ClickBench, the benchmark ClickHouse
    # publishes - what the dataset is, and hot-run results on its default
    # machine. Scores are "times slower than the fastest system", per query,
    # geometric mean; read off benchmark.clickhouse.com on 20 Oct 2026.
    _facts = [("~100 M", "rows"), ("105", "columns"), ("14.8 GB", "as Parquet"), ("43", "queries")]
    _tiles = "".join(
        f'<div style="background:#0a1440; border:1px solid {theme.TONES["navy"].rule}; border-radius:{theme.SPACE["radius"]}; padding:0.9cqw 1.2cqw;">'
        f'<div style="font-size:{theme.SIZE["subhead"]}; font-weight:700; color:{theme.MINT};">{_v}</div>'
        f'<div style="font-size:{theme.SIZE["small"]}; color:{theme.TONES["navy"].muted};">{_l}</div></div>'
        for _v, _l in _facts
    )
    nf.slide(
        nf.two_col(
            mo.vstack(
                [
                    nf.eyebrow("The dataset"),
                    mo.Html(f'<div style="display:grid; grid-template-columns:1fr 1fr; gap:1cqw;">{_tiles}</div>'),
                    nf.body("One wide table of real, anonymised web-analytics hits. Every system loads it, then runs "
                            "43 typical dashboard queries three times."),
                ],
                gap=1.4,
            ),
            mo.vstack(
                [
                    nf.eyebrow("Times slower than the fastest · log scale"),
                    bar_chart(
                        [("ClickHouse", 3.10), ("DuckDB", 6.04), ("Polars", 6.58), ("Spark", 153.14), ("PostgreSQL", 6587.69)],
                        fmt=lambda v: f"×{v:,.1f}" if v < 100 else f"×{v:,.0f}", log=True,
                    ),
                ],
                gap=1.4,
            ),
            ratio=(1, 1.3),
            gap="3cqw",
        ),
        nf.caption(
            "ClickBench (benchmark.clickhouse.com), hot runs, as of 20 Oct 2026, on its default machine: AWS c6a.4xlarge "
            "(16 vCPU, 32 GB). Lower is better. Polars as a DataFrame; PostgreSQL without indexes."
        ),
        title="ClickBench: the ClickHouse benchmark",
        kicker="Transformation - performance",
        pad_top="5cqw",
        gap="2.5cqw",
    )
    return


@app.cell
def slide_opener_serving(platform_step):
    platform_step("serving", "Serving: dashboards and BI")
    return


@app.cell
def slide_dataviz_ecosystem(mo, nf, theme):
    # Dataviz, overview: the ecosystem as a spectrum, from clicking to
    # coding. Logos come from assets/logos/; a missing one falls back to an
    # initials chip.
    _layers = [

  
        ("BI apps (low/no code)", [
            ("Apache Superset", "logos/superset.svg"), ("Metabase", "logos/metabase.svg"),
            ("Grafana", "logos/grafana.svg")
        ]),

        ("Dashboards as code", [
            ("Streamlit", "logos/streamlit.svg"), ("Dash", "logos/plotly.svg"),
            ("marimo", "logos/marimo.png")
        ]),
        ("Chart libraries", [
            ("Altair · Vega-Lite", "logos/altair.svg"), ("Plotly", "logos/plotly.svg"),
            ("D3", "logos/d3.svg"), ("ECharts", "logos/echarts.svg"),
            ("Bokeh", "logos/bokeh.svg"), ("Matplotlib", "logos/matplotlib.svg"),
        ]),
        ("Run in the browser with WASM/GPU", [
            ("Perspective", "logos/perspective.svg"), ("DuckDB-WASM", "logos/duckdb.svg"),
            ("deck.gl", "logos/deckgl.svg"),
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
def slide_dataviz_gallery(assets, mo, nf, theme):
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
def slide_open_source_vs_powerbi(assets, mo, nf, theme):
    # Dataviz vs Power BI: a scorecard, one row per decision driver; the side
    # with the edge is ticked and bright, the other muted. Prices:
    # Microsoft's list prices since April 2025.
    _PBI, _OSS = "#F2C811", theme.MINT
    _rows = [
        ("Self-service", "easy to install, drag and drop", "Superset and Metabase come close", "pbi"),
        ("Semantic model", "relationships, DAX measures, row-level security", "available, but as separate tools", "pbi"),
        ("Microsoft 365", "Teams, Excel, Entra ID built in", "authentication needs to be configured", "pbi"),
        ("Operations", "SaaS: Microsoft runs it", "you host, patch, secure (or buy managed)", "pbi"),
        ("Cost", "pay for subscription/capacity", "free", "oss"),
        ("Visual freedom", "fixed visuals, custom ones in TypeScript", "anything a browser can draw", "oss"),
        ("Version control", "PBIP / TMDL help, still awkward to review", "just use git", "oss"),
        ("Embedding", "Power BI Embedded needs paid capacity", "do whatever you want", "oss"),
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
        title="Open source or Power BI?",
        kicker="Data visualization",
        pad_top="4.5cqw",
        gap="1.4cqw",
    )
    return


@app.cell(hide_code=True)
def slide_dataviz_coding_agents(assets, mo, nf, theme):
    # Dataviz with coding agents: a dashboard Kurt Buhler built with Claude
    # Code, next to what he wrote about it (the cuts are his post's).
    import html as _html

    _paras = [
        "If you enjoy visualizing data [...] try it with coding agents. You'll fall in love with dataviz all over again [...] "
        "I haven't felt this inspired and interested in data design since I first used Tableau and Power BI years ago... [...]",
        "ask Claude Code to create it for you in vega, vega-lite, or d3.js [...] "
        "You'll never see the current UI-driven visualization tools the same, again.",
    ]
    _quote = mo.Html(
        f'<blockquote style="margin:0; font-family:{theme.SERIF}; font-size:{theme.SIZE["body"]}; '
        f'font-weight:{theme.WEIGHT["light"]}; line-height:1.4; color:{theme.TONES["navy"].fg};">'
        + "".join(f'<p style="margin:0 0 0.8cqw;">{"&ldquo;" if _i == 0 else ""}{_html.escape(_p)}{"&rdquo;" if _i == len(_paras) - 1 else ""}</p>'
                  for _i, _p in enumerate(_paras))
        + f'<div style="margin-top:{theme.SPACE["gap_sm"]}; font-family:inherit; font-size:{theme.SIZE["small"]}; '
        f'font-weight:400; color:{theme.MINT};">Kurt Buhler</div></blockquote>'
    )
    nf.slide(
        nf.two_col(
            mo.vstack(
                [
                    assets.img("images/kurt-buhler-data-visualization.png", alt="A fitness dashboard by Kurt Buhler, made with Claude Code"),
                    nf.caption("A dashboard by Kurt Buhler, made with Claude Code."),
                ],
                gap=0.4,
            ),
            _quote,
            ratio=(1.45, 1),
            gap="2.5cqw",
            align="center",
        ),
        title="Dataviz with coding agents",
        kicker="Data visualization",
        pad_top="4.5cqw",
    )
    return


@app.cell
def slide_superset_metabase(assets, mo, nf, theme):
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
                    "BI visualization tool with SQL workspace included",
                    "Full feature version can be self-hosted or managed version is provided by Preset (paid service)",
                    "Interesting technical features such as caching, RBAC, row-level security, caching, background jobs for scheduled reports",
                ],
                "git clone https://github.com/apache/superset && docker compose up",
            ),
            _side(
                "Metabase", "logos/metabase.svg", "AGPL · open core · screenshots © Metabase",
                "images/metabase-dashboard.png",
                [
                    "Easy to use, good for non-technical users",
                    "Easy set-up with Docker",
                    "Simple, but available features work well",
                    "Paid tier supports alerts, embedding, SSO",
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
def slide_d3_race(BarChartRace, dashboard, mo, pd, theme):
    # The D3 slide's widget: weekly energy per plant, as running totals.
    # Created here, shown on the next slide (a UI element is bound to one
    # live mount). Colours are the dashboard's own, so plants match.
    _gold = dashboard.defs["gold_dataset"]
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
def slide_wasm(diagram, nf, theme):
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
        title="Running compiled code in the browser with WebAssembly",
        kicker="Data visualization - WASM",
        pad_top="4.5cqw",
        gap="1.2cqw",
    )
    return


@app.cell
def perspective_widget(dashboard, mo, pd):
    from perspective.widget import PerspectiveWidget

    # The Perspective slide's widget: the fleet's P&L, one row per plant,
    # day and line - revenue (+, from the grid settlement) and every cost line
    # (-, from the finance system). Summed, the bars are the margin. Revenue
    # rows also carry the plant's energy figures, tariff and capacity, so the
    # settings panel has more than one metric to drag in; cost rows leave
    # them empty. binding_mode="client-server": Python ships the table to the
    # browser once, as Arrow, and Perspective's WASM engine does every pivot,
    # filter and chart from there - no server calls.
    _names = {"name": "plant", "country_code": "country"}  # readable in Perspective's column list
    _energy = ["energy_generated_kwh", "energy_exported_kwh", "self_consumption_kwh", "curtailment_kwh"]
    _cols = ["date", "plant", "country", "line", "kind", "amount_eur", "revenue_eur", "cost_eur",
             *_energy, "tariff_eur_per_kwh", "capacity_mw"]
    _revenue = dashboard.defs["gold_dataset"].rename(columns=_names).assign(
        line="Revenue", kind="revenue", amount_eur=lambda d: d["revenue_eur"], cost_eur=float("nan")
    )[_cols]
    _costs = (
        dashboard.defs["costs"]
        .rename(columns={"cost_date": "date", "category": "line", "cost_type": "kind", **_names})
        .assign(cost_eur=lambda d: d["amount_eur"], amount_eur=lambda d: -d["amount_eur"], revenue_eur=float("nan"),
                tariff_eur_per_kwh=float("nan"), **{_c: float("nan") for _c in _energy})[_cols]
    )
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
            # sums by default, except where a sum means nothing
            aggregates={"tariff_eur_per_kwh": "avg", "capacity_mw": "avg"},
            theme="Pro Dark",
            settings=False,  # the presenter opens the panel live
        )
    )
    return (perspective_view,)


@app.cell
def slide_perspective_live(mo, nf, perspective_view):
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
        title="Perspective: a pivot engine in WebAssembly",
        kicker="Data visualization with WASM",
        pad_top="4.5cqw",
        gap="1.2cqw",
    )
    return


@app.cell
def slide_opener_orchestration(platform_step):
    platform_step("orchestration", "Orchestration and scheduling")
    return


@app.cell
def slide_airflow(assets, mo, nf, theme):
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
                            def refresh_dashboard(gold_dataset): ...

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
                "A job orchestrator that allows you to write jobs with Python and manage them through a UI"
                "Born at Airbnb in 2014, now an Apache top-level project",
                "Possibly the most popular orchestration tool, ",
                "Airflow 3 (released in 2025) brought a new UI, asset-based scheduling for event-driven ingestion, scheduler-based backfills",
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
def slide_dagster(assets, bar_chart, mo, nf, theme):
    # Orchestration, 3 of 3: Dagster - its UI in a click-through carousel
    # (screenshots from the Dagster docs; same CSS radio carousel as Airbyte's),
    # and how fast it has been growing: PyPI downloads in September of each
    # year, from ClickPy (clickpy.clickhouse.com).
    _tone = theme.TONES["navy"]
    _shots = [
        ("images/dagster-asset-lineage.png", "The asset graph: every table, what it is built from, when it was last built"),
        ("images/dagster-dbt-assets.png", "Ingestion (Sling) and dbt models as assets in one graph"),
        ("images/dagster-run.png", "A run: its steps on a timeline, with the logs"),
        ("images/dagster-asset-details.png", "An asset's page: its upstream assets, and whether it is out of date"),
    ]
    _css = "".join(
        f"#dg-shot-{_i}:checked ~ .dg-frames .dg-{_i} {{ opacity:1; }} "
        f"#dg-shot-{_i}:checked ~ .dg-dots label[for=dg-shot-{_i}] {{ background:{theme.MINT}; }} "
        for _i in range(len(_shots))
    )
    _carousel = (
        f"<style>.dg-frames > div {{ opacity:0; transition:opacity .4s; }} .dg-dots label {{ cursor:pointer; }} {_css}</style>"
        '<div style="position:relative;">'
        + "".join(
            f'<input type="radio" name="dg-shot" id="dg-shot-{_i}" {"checked" if _i == 0 else ""} style="display:none;">'
            for _i in range(len(_shots))
        )
        + '<div class="dg-frames" style="display:grid;">'
        + "".join(
            f'<div class="dg-{_i}" style="grid-area:1 / 1;">'
            + assets.img(_f, alt=_alt, style={"aspect-ratio": "2 / 1", "object-fit": "cover", "object-position": "left top"}).text
            + f'<div style="font-size:{theme.SIZE["caption"]}; color:{_tone.muted}; margin-top:0.5cqw;">{_alt}</div></div>'
            for _i, (_f, _alt) in enumerate(_shots)
        )
        + '</div><div class="dg-dots" style="display:flex; gap:0.8cqw; justify-content:center; margin-top:0.5cqw;">'
        + "".join(
            f'<label for="dg-shot-{_i}" style="width:1cqw; height:1cqw; border-radius:50%; border:1px solid {theme.MINT};"></label>'
            for _i in range(len(_shots))
        )
        + "</div></div>"
    )
    nf.slide(
        nf.two_col(
            mo.Html(_carousel),
            mo.vstack(
                [
                    nf.eyebrow("PyPI downloads per month (September)"),
                    bar_chart(
                        [("2023", 0.61), ("2024", 1.35), ("2025", 3.05), ("2026", 8.17)],
                        fmt=lambda v: f"{v:.1f} M",
                    ),
                    nf.caption("x6 in two years. Source: ClickPy (PyPI data). Downloads include CI runs: read it as a trend, not as users. Screenshots from the Dagster docs."),
                ],
                gap=1.4,
            ),
            ratio=(1.3, 1),
            gap="2.5cqw",
        ),
        nf.bullets(
            [
                "Asset-based: declare the data you want, and the function that builds it",
                "Parameters are dependencies: free lineage, rebuild only what is stale",
                "Apache 2.0, self-hosted or Dagster+. Prefect is acquiring Dagster Labs (July 2026)",
            ],
            size=theme.SIZE["small"],
        ),
        title="Dagster",
        kicker="Orchestration",
        pad_top="4cqw",
        gap="1.4cqw",
    )
    return


@app.cell
def slide_opener_deployment(platform_step):
    platform_step("deployment", "Deployment: running the platform")
    return


@app.cell
def slide_docker(diagram, nf):
    # Deployment, 1: how Docker works - a Dockerfile (the recipe) is built
    # into an image of cached layers, pushed to a registry, and run as
    # containers on any machine. Three steps, one per click.
    nf.slide(
        diagram("diagrams/docker.svg"),
        title="Docker: how it works",
        kicker="Deploying the platform",
        pad_top="5cqw",
    )
    return


@app.cell
def slide_marimo_docker_image(mo, nf, theme):
    # Deployment, 1b: a marimo dashboard as an image - copy the app folder,
    # install what it needs, say how to start it. For the technical part of
    # the audience; skippable.
    nf.slide(
        nf.two_col(
            mo.vstack(
                [
                    nf.code(
                        """
                        # Dockerfile: a marimo dashboard, as an image
                        FROM python:3.14-slim
                        RUN pip install --no-cache-dir marimo pandas altair
                        COPY app/ /app
                        WORKDIR /app
                        EXPOSE 2718
                        CMD ["marimo", "run", "dashboard.py",
                             "--host", "0.0.0.0", "--port", "2718"]
                        """,
                        language="docker",
                        size=8,
                        fit=(nf.CONTENT_CQW - 3) * 0.55,
                    ),
                    nf.code(
                        """
                        docker build -t my-dashboard:1.0 .
                        docker run -p 2718:2718 my-dashboard:1.0
                        # open http://localhost:2718
                        """,
                        language="bash",
                        size=8,
                        fit=(nf.CONTENT_CQW - 3) * 0.55,
                    ),
                ],
                gap=0.8,
            ),
            nf.bullets(
                [
                    "A docker image is built layer by layer, from operating system, to dependencies, to the code that runs your app",
                    "Defining a container in such way makes it easily reproducible",
                    "You run your container on your infrastructure or on any cloud provider",
                    "Extra steps might be required to secure the app beyond a simple password",
                ],
                size=theme.SIZE["small"],
            ),
            ratio=(11, 9),
            gap="3cqw",
        ),
        title="A marimo dashboard as a Docker image",
        kicker="Deploying the platform",
        pad_top="4.5cqw",
    )
    return


@app.cell(hide_code=True)
def slide_more_services(diagram, nf):
    # Deployment, 2: more services - a database, Airflow, Superset. Each is
    # already an image; docker compose runs them together on one machine,
    # Kubernetes runs the same images across several. Two clicks.
    nf.slide(
        diagram("diagrams/services.svg"),
        title="More services = more containers",
        kicker="Deploying the platform",
        pad_top="5cqw",
    )
    return


@app.cell
def slide_kubernetes(diagram, nf):
    # Deployment, 3: what Kubernetes does with those containers across a few
    # machines - placement, self-healing, scaling, rolling updates. Four
    # steps, one per click.
    nf.slide(
        diagram("diagrams/kubernetes.svg", width="94%"),
        title="Scaling with Kubernetes",
        kicker="Deploying the platform",
        pad_top="4.5cqw",
    )
    return


@app.cell
def slide_oss_vs_managed_intro(assets, mo, nf):
    # OSS vs managed, intro: the question of the last part, in one picture.
    nf.slide(
        nf.two_col(
            mo.vstack(
                [
                    nf.lead("Should your organization use open source to manage its data?"),
                    nf.bullets(
                        [
                            "What does each option really cost?",
                            "How much work is it to build and maintain an open source solution?",
                            "What are the pros and cons of each option?"
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


@app.cell(hide_code=True)
def slide_oss_costs_sanges(assets, mo, nf):
    # OSS vs managed, costs intro: Adriano Sanges' cost comparison from his
    # PyCon Italia 2026 talk - the same workload on a Modern Data Stack and on a
    # Python-native one, at three sizes.
    nf.slide(
        mo.vstack(
            [
                mo.Html(
                    '<div style="width:64cqw; margin:0 auto;">'
                    + assets.img("logos/sanges-presentation.png", alt="Adriano Sanges presenting a cost comparison: same workload, wildly different price tags").text
                    + "</div>"
                ),
                nf.caption("From Adriano Sanges' presentation \u201cThe Modern Data Stack Is Overkill (Most of the Time)\u201d at PyCon Italia 2026"),
            ],
            gap=0.6,
            align="center",
        ),
        title="A cost comparison",
        kicker="Open source or managed",
        pad_top="4cqw",
    )
    return


@app.cell
def slide_oss_costs(mo, nf):
    # OSS vs managed, 1: costs - development effort on one side, licences and
    # usage on the other.
    def _side(_name, _points):
        return mo.vstack([nf.eyebrow(_name), nf.bullets(_points)], gap=1.4)


    nf.slide(
        nf.two_col(
            _side(
                "Open source",
                [
                    "No licence fees, but more development effort is needed, both to manage the infrastructure and the software",
                    "If your organization has core competencies in managing data with open-source tools, this can become a competitive advantage",
                ],
            ),
            _side(
                "Managed data platform",
                [
                    "You pay for licences and usage",
                    "You rely on the vendor's price offering, which can have an opaque cost structure",
                    "It can become more expensive over time",
                ],
            ),
            gap="4cqw",
        ),
        title="Costs",
        kicker="Open source or managed",
        pad_top="5cqw",
    )
    return


@app.cell
def slide_oss_infrastructure(nf):
    # OSS vs managed, 2: infrastructure - open source goes with on-prem the
    # way managed goes with cloud, and the managed versions in between.
    nf.slide(
        nf.bullets(
            [
                "The open source vs managed data platform choice goes hand in hand with on-prem vs cloud",
                "If you have your own infrastructure, it's usually easier to run open-source software on it",
                "Several providers offer managed versions of open-source software, e.g. ClickHouse Cloud, MotherDuck, "
                "Astronomer for Airflow, Preset for Superset",
                "Some companies open source their software to boost adoption, and then sell consulting, support or hosting",
            ]
        ),
        title="Infrastructure",
        kicker="Open source or managed",
        pad_top="5cqw",
    )
    return


@app.cell
def slide_oss_flexibility(nf):
    # OSS vs managed, 3: flexibility - runs anywhere, best tool per job, and
    # missing features you can build yourself.
    nf.slide(
        nf.bullets(
            [
                "Open-source software can run anywhere, which makes it easier to migrate to another cloud provider",
                "Assembling a data platform from different tools lets you pick the best suited tool for each job",
                "If a feature is missing you can implement it yourself, instead of waiting for it to show up on a vendor's roadmap",
            ]
        ),
        nf.quote(
            "Avoiding vendor lock-in has emerged as one of the leading drivers of open source adoption, "
            "cited by 55% of respondents",
            author="2026 State of Open Source Report",
        ),
        title="Flexibility",
        kicker="Open source or managed",
        pad_top="5cqw",
    )
    return


@app.cell(hide_code=True)
def slide_oss_integration(nf):
    # OSS vs managed, 4: integration - a managed platform is one product, an
    # open-source one is pieces you connect; and the Microsoft ecosystem.
    nf.slide(
        nf.bullets(
            [
                "A managed data platform is a one-stop shop: storage, pipelines, catalog and BI already work together",
                "It takes less time to go from the raw data to a shared dashboard",
                "With open source you integrate the tools yourself: login, permissions and metadata across every tool",
                "Many corporations already run on Microsoft 365: Fabric and Power BI plug into the company's accounts, "
                "Teams, Excel and SharePoint, which is a big plus",
            ]
        ),
        title="Integration",
        kicker="Open source or managed",
        pad_top="5cqw",
    )
    return


@app.cell
def slide_oss_governance_compliance(nf):
    # OSS vs managed, 5: governance and compliance - what managed platforms
    # give you out of the box, what it takes with open source, and the risks
    # that come with each.
    nf.slide(
        nf.bullets(
            [
                "Managed data platforms have built-in tools for security, encryption, data masking and authentication",
                #"They also come with certifications like ISO 27001 and SOC 2, which helps with audits",
                "Data governance tools like catalogs and lineage are built in too (Unity Catalog, Purview). "
                "Open-source alternatives exist, e.g. OpenMetadata or DataHub",
                #"With open source you can get the same things, e.g. Keycloak for authentication, but you have to set them up "
                #"and maintain them yourself",
                "Managed platforms come with support and SLAs. With open source your team handles upgrades, security patches "
                "and incidents",
                "Open source has its own risks: projects can change licence (e.g. Elasticsearch, Redis, Terraform) or lose "
                "their maintainers",
                "Some governments are pushing for the adoption of open source tools to increase control over their digital infrastructure"
            ],
        ),
        title="Governance and compliance",
        kicker="Open source or managed",
        pad_top="5cqw",
    )
    return


@app.cell
def slide_who_goes_open_source(icon_cards, nf, theme):
    # OSS vs managed, who: the organisations that usually choose open source.
    nf.slide(
        icon_cards(
            [
                ("server", "Organisations with their own infrastructure",
                 "Data centres or a private cloud, run by their own ops team - and often data that may not leave it (sovereignty, regulation).",
                 "e.g. public sector, healthcare, banks", theme.MINT),
                ("growth", "Data as a core competence",
                 "Strong engineering teams for whom skills in data and infrastructure management provide a competitive advantage",
                 "e.g. consulting businesses, open-source companies, large companies that want to drive adoption of their libraries", theme.BLUE),
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


@app.cell(hide_code=True)
def slide_repo_and_feedback(assets, mo, nf, theme):
    # Closing: QR codes for the talk's repo and for feedback, side by side.
    _MONO = "var(--marimo-monospace-font, ui-monospace, SFMono-Regular, Menlo, monospace)"
    _repo = "github.com/DarioRubenScanferlato/OpenSourceDataToolsPresentation"


    def _qr(_eyebrow, _img, _alt, _caption, _pad):
        return mo.vstack(
            [
                nf.eyebrow(_eyebrow),
                mo.Html(
                    f'<div style="background:#ffffff; border-radius:{theme.SPACE["radius"]}; padding:{_pad}; width:24cqw;">'
                    + assets.img(_img, alt=_alt, rounded=False).text
                    + "</div>"
                ),
                _caption,
            ],
            gap=1.2,
            align="center",
        )


    nf.slide(
        mo.hstack(
            [
                _qr(
                    "Presentation", "images/repo-qr.svg", "GitHub repo QR code",
                    mo.Html(
                        f'<a href="https://{_repo}" target="_blank" style="font-family:{_MONO}; font-size:{theme.SIZE["caption"]}; '
                        f'color:{theme.MINT}; text-decoration:none; text-align:center; display:block;">'
                        f'{_repo.rsplit("/", 1)[0]}/<br>{_repo.rsplit("/", 1)[1]}</a>'
                    ),
                    "2.6cqw",
                ),
                _qr("Feedback", "images/feedback-qr.png", "Feedback form QR code", nf.caption("Tell me what you think"), "0.6cqw"),
            ],
            justify="center",
            gap=8,
            align="start",
        ),
        title="Thank you!",
        kicker="Code and feedback",
        pad_top="5cqw",
    )
    return


@app.cell
def slide_resources(mo, nf, theme):
    # Closing: resources - books, articles and benchmarks, docs and specs
    # behind this talk.
    def _group(_name, _items):
        return mo.vstack([nf.eyebrow(_name), nf.bullets(_items, size=theme.SIZE["small"])], gap=1.4)


    nf.slide(
        mo.Html(
            '<div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:3cqw; align-items:start;">'
            + "".join(
                f'<div style="min-width:0;">{_g.text}</div>'
                for _g in [
                    _group(
                        "Books",
                        [
                            "*Fundamentals of Data Engineering*, Joe Reis and Matt Housley (O'Reilly)",
                            "*Designing Data-Intensive Applications*, Martin Kleppmann (O'Reilly)",
                        ],
                    ),
                    _group(
                        "Articles and benchmarks",
                        [
                            "*Big Data is Dead*, Jordan Tigani - motherduck.com/blog/big-data-is-dead",
                            "ClickBench - benchmark.clickhouse.com",
                            "PDS-H benchmark - pola.rs/posts/benchmarks",
                            "DB-Engines ranking - db-engines.com/en/ranking",
                        ],
                    ),
                    _group(
                        "Docs and specs",
                        [
                            "marimo - docs.marimo.io",
                            "Delta Lake protocol - github.com/delta-io/delta, PROTOCOL.md",
                        ],
                    ),
                ]
            )
            + "</div>"
        ),
        title="Resources",
        kicker="Further reading",
        pad_top="5cqw",
    )
    return


if __name__ == "__main__":
    app.run()
