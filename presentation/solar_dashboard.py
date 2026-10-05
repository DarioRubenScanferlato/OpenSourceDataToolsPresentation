import marimo

__generated_with = "0.24.0"
app = marimo.App(
    width="full",
    layout_file="layouts/solar_dashboard.grid.json",
    css_file="nf-dashboard.css",
)


@app.cell(hide_code=True)
def imports():
    import warnings
    from pathlib import Path

    import altair as alt
    import marimo as mo
    import pandas as pd

    from template import theme as nf
    from template.timeline import DateRangeTimeline

    return DateRangeTimeline, Path, alt, mo, nf, pd, warnings


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
    data_ready = bronze.is_ready()
    if not data_ready and generate_button.value:
        with mo.status.spinner(title="Generating the solar data..."):
            bronze.generate()
        data_ready = True
    # Shown (in the dashboard's top row, where the filters go) until the data
    # exists; empty afterwards. The cells below wait on `data_ready`.
    first_run_notice = (
        None
        if data_ready
        else mo.callout(
            mo.hstack(
                [
                    mo.Html(
                        "<span style='color:#1a1a1a'><b>The solar data isn't generated yet.</b> "
                        "Simulate it (about 20 s, nothing is downloaded):</span>"
                    ),
                    generate_button,
                ],
                justify="start",
                align="center",
                gap=1.5,
            ),
            kind="warn",
        )
    )
    first_run_notice
    return (data_ready,)


@app.cell(hide_code=True)
def branding(alt, nf):
    # Nearform brand tokens, imported from the shared presentation/template
    # package (presentation/template/theme.py) so this dashboard stays in
    # sync with the deck and the co2_gdp_dashboard.py reference notebook.
    _tone = nf.TONES["navy"]
    NF_BG = _tone.bg
    NF_FG = _tone.fg
    NF_MUTED = _tone.muted
    NF_RULE = _tone.rule
    #: One step lighter than the page, for the Power BI-style card behind
    #: each stat tile and chart - enough to read as a raised surface without
    #: competing with the brand accents drawn on top of it.
    NF_PANEL = "#0a1440"

    #: One color per plant (8), assigned alphabetically - never cycled, so
    #: no two plants share one. The brand accents plus brand-derived steps
    #: (a mint shade, a purple tint, a mint-blue teal) in place of theme.py's
    #: PALE_BLUE, which read as the same near-gray as PALE_MINT. Checked
    #: with the dataviz skill's palette validator on NF_PANEL: in this order
    #: every *adjacent* pair - neighbors in the stacked area - clears ΔE 31
    #: (normal vision) / 21 (color-blind). The weakest pair overall is BLUE
    #: vs PURPLE, never adjacent; the table and tooltips always name plants
    #: too. The bright brand accents sit above the validator's dark-mode
    #: lightness band by design.
    PLANT_COLORS = [
        "#B18CFF",  # purple, one step lighter
        nf.MINT,
        nf.BLUE,
        nf.LAVENDER,
        nf.PURPLE,
        "#00B383",  # mint, one step darker
        nf.PALE_MINT,
        "#0BA8D1",  # teal, between mint and blue
    ]

    #: Maintenance event types, in brand accents rather than a Vega scheme.
    EVENT_COLORS = {
        "Corrective repair": nf.MINT,
        "Routine inspection": nf.LAVENDER,
        "Vegetation control": nf.BLUE,
    }

    #: Better/worse markers on the KPI cards' week-over-week deltas - always
    #: paired with an arrow and the number, never color alone.
    STATUS_GOOD = nf.MINT
    STATUS_BAD = "#FF7A8A"

    #: Dim -> bright brand ramp for quantitative (sequential) scales on a dark
    #: ground: a near-invisible hairline tone rising through blue to mint.
    NF_SEQUENTIAL = [NF_RULE, nf.BLUE, nf.MINT]

    #: Text sizes, bumped for a projector: the whole dashboard is scaled down
    #: to fit a slide, so anything below ~12px ends up unreadable from the
    #: back of the room.
    FONT_SM = 13
    FONT_MD = 16


    def plant_scale(all_plant_names: list[str]) -> alt.Scale:
        """The per-plant color scale. Always pass *every* plant, not just the
        filtered ones: color follows the plant, so filtering some out must
        not repaint the rest."""
        names = sorted(all_plant_names)
        return alt.Scale(domain=names, range=PLANT_COLORS[: len(names)])


    @alt.theme.register("nearform-solar", enable=True)
    def nearform_theme() -> alt.theme.ThemeConfig:
        return {
            "config": {
                "background": NF_BG,
                "font": nf.SANS,
                "title": {"color": NF_FG, "fontSize": FONT_MD, "fontWeight": 600, "anchor": "middle"},
                "text": {"fontSize": FONT_SM},
                "axis": {
                    "labelColor": NF_MUTED,
                    "labelFontSize": FONT_SM,
                    "titleColor": NF_FG,
                    "titleFontSize": FONT_SM,
                    "gridColor": NF_RULE,
                    "domainColor": NF_RULE,
                    "tickColor": NF_RULE,
                },
                "legend": {
                    "labelColor": NF_FG,
                    "labelFontSize": FONT_SM,
                    "titleColor": NF_FG,
                    "titleFontSize": FONT_SM,
                },
                "view": {"stroke": "transparent"},
                "range": {
                    "category": PLANT_COLORS,
                    "ramp": NF_SEQUENTIAL,
                    "heatmap": NF_SEQUENTIAL,
                },
            }
        }

    return (
        EVENT_COLORS,
        FONT_MD,
        FONT_SM,
        NF_FG,
        NF_MUTED,
        NF_PANEL,
        NF_RULE,
        STATUS_BAD,
        STATUS_GOOD,
        plant_scale,
    )


@app.cell(hide_code=True)
def grid_layout(FONT_MD, NF_FG, NF_PANEL, NF_RULE, alt):
    #: Vega-Lite renders the linked-explorer chart at a *fixed* pixel size,
    #: which never grows or shrinks with the browser window, unlike the rest
    #: of this `width="full"` page. Both the chart and the stat cards above
    #: it are authored at this *design* width and scaled to the page's
    #: actual width with the same CSS trick the main deck uses to embed this
    #: dashboard full-bleed into a slide (`container-type: inline-size` +
    #: `zoom: calc(100cqw / Npx)`, declared in nf-dashboard.css - see that
    #: file for why it has to live there and not here; keep its number in
    #: sync with this one).
    DASHBOARD_WIDTH = 1518

    #: The explorer is a 2x2 grid of equal-sized Power BI-style panels. Each
    #: panel's card is drawn *inside* the Vega-Lite spec (see `panel()`), so
    #: it also defines that view's full bounds - every grid slot ends up
    #: exactly PANEL_W x PANEL_H whatever axes/legends each chart has, which
    #: is what keeps the four panels aligned without any spacing fudges.
    PANEL_GAP = 16
    PANEL_W = (DASHBOARD_WIDTH - PANEL_GAP) // 2 - 2  # -2: the card's stroke, 1px per side
    #: Sized so the whole dashboard fits one 16:9 slide in the deck without
    #: scrolling (filters + two rows of stat cards + two rows of panels) -
    #: check at a 16:9 window: a taller one leaves more room than a
    #: projector will.
    PANEL_H = 280
    PANEL_PAD = 24
    PANEL_TITLE_H = 30  # title strip across the top of each panel

    def plot_size(*, left: int = 0, right: int = 0, bottom: int = 0) -> tuple[int, int]:
        """The plot-area (width, height) that fills one panel, leaving
        `left`/`right`/`bottom` px for that chart's own axis/legend chrome
        (on top of the panel's padding and title strip)."""
        return (
            PANEL_W - 2 * PANEL_PAD - left - right,
            PANEL_H - 2 * PANEL_PAD - PANEL_TITLE_H - bottom,
        )

    def panel(chart, *, left: int = 0, right: int = 0, bottom: int = 0):
        """Wrap a chart sized with `plot_size(...)` (same chrome arguments)
        in a rounded card with its title centered along the top, Power BI
        style.

        The card and title are just two extra layers - a `mark_rect` and a
        `mark_text` positioned in pixels *around* the plot area, past its
        axes - rather than HTML around the chart: all four charts have to
        stay one compiled spec for the shared click selection to sync
        (see `explorer_layout`), so there's no per-chart DOM node to style.
        """
        w, h = chart.width, chart.height
        x0, y0 = -(PANEL_PAD + left), -(PANEL_PAD + PANEL_TITLE_H)
        x1 = w + PANEL_PAD + right
        one_row = alt.InlineData(values=[{}])
        card = alt.Chart(one_row).mark_rect(
            fill=NF_PANEL, stroke=NF_RULE, cornerRadius=10
        ).encode(
            x=alt.value(x0),
            x2=alt.value(x1),
            y=alt.value(y0),
            y2=alt.value(h + PANEL_PAD + bottom),
        )
        title = alt.Chart(one_row).mark_text(
            align="center", baseline="top", color=NF_FG, fontSize=FONT_MD, fontWeight=600
        ).encode(
            x=alt.value((x0 + x1) / 2),
            y=alt.value(y0 + PANEL_PAD - 2),
            text=alt.value(chart.title),
        )
        body = chart.copy()
        body.title = body.width = body.height = alt.Undefined
        return alt.layer(card, title, body).properties(width=w, height=h)

    return DASHBOARD_WIDTH, PANEL_GAP, PANEL_PAD, PANEL_TITLE_H, panel, plot_size


@app.cell(hide_code=True)
def load_data(Path, bronze, data_ready, mo, pd):
    mo.stop(not data_ready)
    # The raw ("bronze") data, one file per source system, as it would land
    # in a platform: simulated by solar_data_gen/ (8 synthetic plants over
    # two years) and split per source - see data/solar/README.md. `data_ready`
    # makes this wait for the first-run "Generate the data" step.
    BRONZE = bronze.BRONZE_DIR

    plants = pd.read_csv(BRONZE / "plants.csv", parse_dates=["commissioning_date", "decommissioning_date"])
    # which plant each sensor belongs to - the readings only name the sensor
    sensors = pd.read_csv(BRONZE / "sensors.csv", parse_dates=["install_date"])
    sensor_readings = pd.read_csv(BRONZE / "sensor_readings.csv.gz", parse_dates=["timestamp"])
    grid_settlement = pd.read_csv(BRONZE / "grid_settlement.csv", parse_dates=["settlement_date"])
    costs_raw = pd.read_csv(BRONZE / "costs.csv", parse_dates=["cost_date"])
    alarms_raw = pd.read_csv(BRONZE / "alarms.csv", parse_dates=["triggered_at", "cleared_at"])
    maintenance_raw = pd.read_csv(BRONZE / "maintenance.csv", parse_dates=["scheduled_date", "completed_date"])
    # the plant dimension everything else is keyed on
    dim_plants = plants
    return (
        alarms_raw,
        costs_raw,
        dim_plants,
        grid_settlement,
        maintenance_raw,
        plants,
        sensor_readings,
        sensors,
    )


@app.cell(hide_code=True)
def bronze_to_gold(
    alarms_raw,
    costs_raw,
    grid_settlement,
    maintenance_raw,
    pd,
    plants,
    sensor_readings,
    sensors,
):
    # Bronze -> gold in one step: the SCADA sensor readings and the grid
    # operator's settlement are separate sources that only meet here, in
    # `gold` - one row per plant per day, everything the dashboard needs.

    # 1. Find the bad sensor readings. A dropout arrives as NaN; a *stuck*
    #    sensor keeps repeating the value it froze on, which real output
    #    never does (there's always some noise) - so the same non-zero
    #    reading 3+ hours in a row is treated as missing too. What's found
    #    goes into its own table, `reading_issues` (one row per bad
    #    reading), rather than a column on the readings: the readings stay
    #    measurements, and the issues can be counted and joined on their own.
    readings = sensor_readings.sort_values(["sensor_id", "timestamp"]).reset_index(drop=True)
    _power = readings["ac_power_kw"]
    _run = (_power != readings.groupby("sensor_id")["ac_power_kw"].shift()).cumsum()
    _run_length = readings.groupby(_run)["ac_power_kw"].transform("size")
    _stuck = (_run_length >= 3) & (_power > 0)
    _missing = _power.isna()
    reading_issues = (
        pd.concat(
            [
                readings.loc[_stuck, ["sensor_id", "timestamp"]].assign(issue="stuck"),
                readings.loc[_missing, ["sensor_id", "timestamp"]].assign(issue="missing"),
            ]
        )
        .sort_values(["sensor_id", "timestamp"])
        .reset_index(drop=True)
    )
    _bad = _stuck | _missing
    readings["ac_power_kw_clean"] = _power.mask(_bad)

    # 2. Fill each bad hour with the typical value for that hour of the day
    #    around it: the median of the same hour over the surrounding week
    #    (7 days, centred). Solar output follows the sun, so this keeps the
    #    daily bell shape and leaves nights at 0 - and unlike "yesterday's
    #    value" it still has an answer when yesterday was broken too (a
    #    stuck run can last more than a day).
    _same_hour = readings.groupby(["sensor_id", readings["timestamp"].dt.hour])["ac_power_kw_clean"]
    readings["ac_power_kw_clean"] = readings["ac_power_kw_clean"].fillna(
        _same_hour.transform(lambda s: s.rolling(7, center=True, min_periods=1).median())
    )

    # 3. Hourly kW -> daily kWh per plant (one reading = one hour). The
    #    sensor register says which plant each sensor is in.
    daily = (
        readings.assign(
            date=readings["timestamp"].dt.tz_localize(None).dt.normalize(),
            measured=~_bad,
        )
        .merge(sensors[["sensor_id", "plant_id"]], on="sensor_id")
        .groupby(["plant_id", "date"], as_index=False)
        .agg(
            energy_generated_kwh=("ac_power_kw_clean", "sum"),
            # share of hours that were really measured, not filled in
            reading_coverage=("measured", "mean"),
        )
    )

    # 4. Join the settlement (what the grid operator metered and paid) and
    #    the plant masterdata, and derive what neither source has alone:
    #    energy used on site = generated - exported - curtailed.
    _plant_cols = plants[["plant_id", "name", "country_code", "capacity_mw"]]
    gold = (
        daily.merge(
            grid_settlement.rename(columns={"settlement_date": "date"}),
            on=["plant_id", "date"],
            how="inner",
        )
        .merge(_plant_cols, on="plant_id")
    )
    gold["self_consumption_kwh"] = (
        gold["energy_generated_kwh"] - gold["energy_exported_kwh"] - gold["curtailment_kwh"]
    ).clip(lower=0)

    # The other sources only need the plant name joined in.
    alarms = alarms_raw.merge(_plant_cols, on="plant_id")
    maintenance = maintenance_raw.merge(_plant_cols, on="plant_id")
    costs = costs_raw.merge(_plant_cols, on="plant_id")

    #: Business regions for the Region filter. With one plant per country a
    #: country filter would just duplicate the Plants one.
    REGIONS = {"GB": "EMEA", "NL": "EMEA", "DE": "EMEA", "RU": "EMEA", "CA": "Americas", "US": "Americas", "BR": "Americas", "MM": "APAC"}
    plant_region = dict(zip(plants["name"], plants["country_code"].map(REGIONS).fillna("Other")))
    return alarms, costs, gold, maintenance, plant_region, reading_issues, readings


@app.cell(hide_code=True)
def filters(
    DateRangeTimeline,
    FONT_SM,
    NF_FG,
    NF_MUTED,
    NF_RULE,
    PANEL_GAP,
    dim_plants,
    gold,
    mo,
    nf,
    pd,
    plant_region,
):
    _min_date, _max_date = gold["date"].min(), gold["date"].max()

    # Short labels ("Dorval"), full names as values: every plant name ends
    # in "Solar Farm", which only made the selected chips overflow.
    location_filter = mo.ui.multiselect(
        options={n.removesuffix(" Solar Farm"): n for n in sorted(dim_plants["name"])},
        value=[n.removesuffix(" Solar Farm") for n in sorted(dim_plants["name"])],
        full_width=True,
    )
    _regions = sorted(set(plant_region.values()))
    region_filter = mo.ui.multiselect(options=_regions, value=_regions, full_width=True)

    # Period: a timeline slider across the whole data range - the strip
    # shows daily fleet energy (so you can see where there's data), and its
    # two handles set the start and end independently (dragging between
    # them moves both). A small anywidget (template/timeline.py): marimo's
    # own range slider is numeric-only, and a Vega-Lite brush can't be
    # resized from either end. Starts on the full range of the data.
    _daily_energy = (
        gold.groupby("date")["energy_generated_kwh"].sum()
        .reindex(pd.date_range(_min_date, _max_date, freq="D"), fill_value=0)
    )
    period_filter = mo.ui.anywidget(
        DateRangeTimeline(
            start=_min_date.date().isoformat(),
            end=_max_date.date().isoformat(),
            min_date=_min_date.date().isoformat(),
            max_date=_max_date.date().isoformat(),
            values=[float(v) for v in _daily_energy],
            width=2 * 367 + PANEL_GAP,  # spans two card columns
            label="Period",
            colors={"accent": nf.MINT, "fg": NF_FG, "muted": NF_MUTED, "rule": NF_RULE, "bg": nf.NAVY},
        )
    )

    def _slot(label, widget, *, span=1):
        """One filter per stat-card column (or `span` of them): its label
        above (unless the widget draws its own), the control stretched to
        the column's full width."""
        head = (
            f'<div style="color:{NF_MUTED}; font-size:{FONT_SM}px; margin-bottom:4px;">{label}</div>'
            if label
            else ""
        )
        return f'<div style="min-width:0; grid-column:span {span};">{head}{mo.as_html(widget).text}</div>'


    # marimo's date widget colors its *background* via a token that reads
    # the computed `color-scheme` (this notebook's own page is `body.light.
    # light-theme`, so left alone it's white) - `color-scheme: dark` here
    # fixes that for the multiselects' popovers and inputs too, and `color`
    # covers the text they inherit (nf-dashboard.css deliberately leaves
    # marimo's own design tokens alone otherwise - see that file's docstring
    # for why).
    #
    # Same 4-column grid and gap as the stat cards below (`nf-filters` gets
    # the same fit-to-width scaling in nf-dashboard.css), so each filter
    # lines up with the card under it. Vertical padding = the panels' gap:
    # cells stack flush in the deck's embed, so this is the only space
    # between the slide's top edge, this row and the cards.
    mo.Html(
        f'<div class="dark nf-filters" style="color-scheme:dark; color:{NF_FG}; '
        f"display:grid; grid-template-columns:repeat(4, 1fr); gap:{PANEL_GAP}px; "
        f'padding:{PANEL_GAP}px 0;">'
        f'{_slot("Plants", location_filter)}'
        f'{_slot(None, period_filter, span=2)}'
        f'{_slot("Region", region_filter)}</div>'
    )
    return location_filter, period_filter, region_filter


@app.cell(hide_code=True)
def apply_filters(
    alarms,
    gold,
    costs,
    location_filter,
    maintenance,
    pd,
    period_filter,
    plant_region,
    region_filter,
):
    # The single filtered view every card and chart below reads from - a
    # plant/region/period scope, distinct from the click-based cross-filter
    # selection (`plant_sel`, defined further down) that only *highlights*
    # within it.
    _locations = [n for n in location_filter.value if plant_region[n] in region_filter.value]

    # The Period timeline's two handles, as ISO dates.
    period_start = pd.Timestamp(period_filter.value["start"])
    period_end = pd.Timestamp(period_filter.value["end"])
    _start, _end = period_start.date(), period_end.date()

    gold_f = gold[
        gold["name"].isin(_locations) & gold["date"].dt.date.between(_start, _end)
    ]
    alarms_f = alarms[
        alarms["name"].isin(_locations) & alarms["triggered_at"].dt.date.between(_start, _end)
    ]
    maintenance_f = maintenance[
        maintenance["name"].isin(_locations)
        & maintenance["scheduled_date"].dt.date.between(_start, _end)
    ]
    costs_f = costs[
        costs["name"].isin(_locations) & costs["cost_date"].dt.date.between(_start, _end)
    ]

    # P&L over the scope - per plant (the sankey) and per plant and month
    # (the revenue/cost/profit chart). Operating costs are the generated
    # accruals plus corrective repairs from the maintenance work orders;
    # tax is 25% of pre-tax profit (0 on a loss) per plant (and month).
    _TAX_RATE = 0.25
    _OPEX = ["O&M contract", "Land lease", "Insurance", "Asset management", "Grid fees"]
    _month = lambda dates: dates.dt.strftime("%Y-%m")
    _b = gold_f.assign(month=_month(gold_f["date"]))
    _c = costs_f.assign(month=_month(costs_f["cost_date"]))
    _m = maintenance_f.assign(month=_month(maintenance_f["scheduled_date"]))

    def _pnl_by(keys):
        out = _b.groupby(keys)[["revenue_eur"]].sum().rename(columns={"revenue_eur": "Revenue"})
        by_cat = _c.pivot_table(index=keys, columns="category", values="amount_eur", aggfunc="sum")
        for cat in _OPEX + ["Depreciation", "Interest"]:
            out[cat] = by_cat.get(cat, 0.0)
        out["Corrective maintenance"] = _m.groupby(keys)["cost_eur"].sum()
        out = out.fillna(0.0)
        out["Operating costs"] = out[_OPEX + ["Corrective maintenance"]].sum(axis=1)
        pre_tax = out["Revenue"] - out["Operating costs"] - out["Depreciation"] - out["Interest"]
        out["Tax"] = (pre_tax.clip(lower=0) * _TAX_RATE).round(2)
        out["Net profit"] = pre_tax - out["Tax"]
        return out.reset_index()

    pnl = _pnl_by(["name"])
    pnl_monthly = _pnl_by(["name", "month"])
    return alarms_f, gold_f, maintenance_f, period_end, period_start, pnl, pnl_monthly


@app.cell(hide_code=True)
def stat_card_helper(
    FONT_SM,
    NF_FG,
    NF_MUTED,
    NF_PANEL,
    NF_RULE,
    PANEL_GAP,
    PANEL_PAD,
    STATUS_BAD,
    STATUS_GOOD,
    mo,
    nf,
):
    def sparkline(values, *, width: int = 120, height: int = 40) -> str:
        """An inline-SVG trend line over `values` (oldest first)."""
        vals = [float(v) for v in values]
        if len(vals) < 2:
            return f'<svg width="{width}" height="{height}"></svg>'
        lo, hi = min(vals), max(vals)
        span = (hi - lo) or 1.0
        step = width / (len(vals) - 1)
        pts = " ".join(
            f"{i * step:.1f},{height - 3 - (v - lo) / span * (height - 6):.1f}"
            for i, v in enumerate(vals)
        )
        return (
            f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
            f'style="flex:none; overflow:visible;">'
            f'<polyline points="{pts}" fill="none" stroke="{nf.MINT}" stroke-width="2" '
            f'stroke-linejoin="round" stroke-linecap="round"/></svg>'
        )

    def delta_html(change: float | None, *, higher_is_better: bool, days: int = 7) -> str:
        """Change vs the `days` before the last `days`: arrow + percentage,
        colored better/worse (the arrow and number carry the meaning; color
        only reinforces it)."""
        window = f"vs prior {days} days"
        if change is None:
            return f'<span style="color:{NF_MUTED};">nothing to compare {window}</span>'
        if abs(change) < 0.0005:
            return f'<span style="color:{NF_MUTED};">&#9644; 0.0% {window}</span>'
        good = (change > 0) == higher_is_better
        arrow = "&#9650;" if change > 0 else "&#9660;"
        return (
            f'<span style="color:{STATUS_GOOD if good else STATUS_BAD}; font-weight:600;">'
            f"{arrow} {abs(change):.1%}</span>"
            f'<span style="color:{NF_MUTED};"> {window}</span>'
        )

    def stat_card(label: str, value: str, delta: str, trend: str) -> str:
        """One KPI tile: label, headline value (in text ink, not a series
        color) and its week-over-week delta on the left, a sparkline on the
        right - hand-rolled to match nf-dashboard.css's literal-color style
        rather than marimo's shared design tokens (see that file's docstring
        for why)."""
        return f"""
        <div style="
            background:{NF_PANEL}; border:1px solid {NF_RULE}; border-radius:10px;
            padding:8px {PANEL_PAD}px; min-width:0;
            display:flex; align-items:flex-end; justify-content:space-between; gap:12px;
        ">
          <div style="min-width:0;">
            <div style="color:{NF_MUTED}; font-size:{FONT_SM}px;">{label}</div>
            <div style="color:{NF_FG}; font-size:24px; font-weight:700; line-height:1.15;">{value}</div>
            <div style="font-size:{FONT_SM - 1}px; white-space:nowrap;">{delta}</div>
          </div>
          {trend}
        </div>
        """

    def stat_row(cards: list[str]) -> "mo.Html":
        # A 4-column grid (two rows of four), authored at `DASHBOARD_WIDTH`
        # and scaled to the page's actual width the same way the chart is
        # (nf-dashboard.css's `.react-grid-item:has(.nf-stat-cards)` rule -
        # `nf-stat-cards` is just the anchor its `:has()` finds this cell
        # by). Gaps - between cards, and below them before the charts - are
        # the panels' own `PANEL_GAP`, so cards and charts read as one grid.
        return mo.Html(
            f'<div class="nf-stat-cards" style="display:grid; '
            f"grid-template-columns:repeat(4, 1fr); gap:{PANEL_GAP}px; "
            f'padding-bottom:{PANEL_GAP}px; color:{NF_FG};">'
            f'{"".join(cards)}</div>'
        )

    return delta_html, sparkline, stat_card, stat_row


@app.cell(hide_code=True)
def cards(
    alarms_f,
    delta_html,
    explorer_view,
    gold_f,
    maintenance_f,
    pd,
    period_end,
    period_start,
    sparkline,
    stat_card,
    stat_row,
):
    # Each KPI is a function of the three filtered frames, so the same
    # definition gives the headline value (whole period) and both halves of
    # the week-over-week delta (the last 7 days vs the 7 before them).
    def _energy(b, a, m):
        return b["energy_generated_kwh"].sum()

    def _capacity_factor(b, a, m):
        # energy produced / what the plants' nameplate capacity could have
        # produced running flat out, over the same plant-days
        possible = (b["capacity_mw"] * 1000 * 24).sum()
        return b["energy_generated_kwh"].sum() / possible if possible else None

    def _revenue(b, a, m):
        return b["revenue_eur"].sum()

    def _price(b, a, m):
        exported = b["energy_exported_kwh"].sum()
        return b["revenue_eur"].sum() / exported * 1000 if exported else None

    def _alarms(b, a, m):
        return len(a)

    def _critical(b, a, m):
        return int((a["severity"] == "critical").sum())

    def _mttr(b, a, m):
        hours = (a["cleared_at"] - a["triggered_at"]).dt.total_seconds() / 3600
        return hours.mean() if len(hours) else None

    def _maint_cost(b, a, m):
        return m["cost_eur"].sum()

    _start, _end = period_start, period_end

    # Cross-filter: the plant clicked in the charts below. It lives in the
    # browser (the charts' shared `plant_sel`), but `mo.ui.altair_chart`
    # sends every selection change back here, so the cards follow it too -
    # a round trip through Python, unlike the charts' instant dimming.
    _picked = [
        n for n in (explorer_view.selections or {}).get("plant_sel", {}).get("name", []) if n
    ]
    _g, _al, _mt = gold_f, alarms_f, maintenance_f
    if _picked:
        _g, _al, _mt = (df[df["name"].isin(_picked)] for df in (_g, _al, _mt))
    _suffix = f" · {', '.join(n.removesuffix(' Solar Farm') for n in _picked)}" if _picked else ""

    def _window(lo, hi):
        """The three frames cut to days lo..hi (inclusive)."""
        return (
            _g[_g["date"].between(lo, hi)],
            _al[_al["triggered_at"].dt.tz_localize(None).dt.normalize().between(lo, hi)],
            _mt[_mt["scheduled_date"].between(lo, hi)],
        )

    # Deltas compare the last N days with the N before: a week for the
    # daily production/revenue KPIs, four weeks for the sparse event-based
    # ones (a week often has no alarms at all, leaving nothing to compare).
    def _change(metric, days):
        if _start > _end - pd.Timedelta(days=2 * days - 1):
            return None
        now = metric(*_window(_end - pd.Timedelta(days=days - 1), _end))
        before = metric(*_window(_end - pd.Timedelta(days=2 * days - 1), _end - pd.Timedelta(days=days)))
        if now is None or not before:
            return None
        return now / before - 1

    # Trends: ~60 points for the production/revenue KPIs, ~25 for the
    # sparse event-based ones (a few alarms a day would just be noise) -
    # daily/weekly over a short period, coarser buckets over two years.
    _n_days = (_end - _start).days + 1

    def _buckets(points, min_days):
        size = pd.Timedelta(days=max(min_days, -(-_n_days // points)))
        return pd.date_range(_start, _end, freq=size), size

    _fine, _coarse = _buckets(60, 1), _buckets(25, 7)

    def _trend(metric, starts, length):
        vals = [metric(*_window(d, d + length - pd.Timedelta(days=1))) for d in starts]
        return sparkline([0 if v is None else v for v in vals])

    def _eur(v):
        if v >= 1e6:
            return f"€{v / 1e6:.1f}M"
        return f"€{v / 1e3:.1f}k" if v >= 1e3 else f"€{v:.0f}"

    _b, _a, _m = _g, _al, _mt
    _cf, _price_v, _mttr_v = _capacity_factor(_b, _a, _m), _price(_b, _a, _m), _mttr(_b, _a, _m)
    _kpis = [
        # (label, value, metric, higher_is_better, trend buckets)
        ("Energy produced", f"{_energy(_b, _a, _m) / 1e6:,.1f} GWh", _energy, True, _fine),
        ("Capacity factor", "—" if _cf is None else f"{_cf:.1%}", _capacity_factor, True, _fine),
        ("Revenue", _eur(_revenue(_b, _a, _m)), _revenue, True, _fine),
        ("Avg. price", "—" if _price_v is None else f"€{_price_v:.1f}/MWh", _price, True, _fine),
        ("Alarms", f"{_alarms(_b, _a, _m):,}", _alarms, False, _coarse),
        ("Critical alarms", f"{_critical(_b, _a, _m):,}", _critical, False, _coarse),
        ("Mean time to resolve", "—" if _mttr_v is None else f"{_mttr_v:.1f} h", _mttr, False, _coarse),
        ("Maintenance cost", _eur(_maint_cost(_b, _a, _m)), _maint_cost, False, _coarse),
    ]
    stat_row(
        [
            stat_card(
                label + _suffix,
                value,
                delta_html(
                    _change(metric, 7 if buckets is _fine else 28),
                    higher_is_better=better,
                    days=7 if buckets is _fine else 28,
                ),
                _trend(metric, *buckets),
            )
            for label, value, metric, better, buckets in _kpis
        ]
    )
    return


@app.cell(hide_code=True)
def plant_selection(alt):
    # The shared cross-filter: a click-to-highlight selection keyed on plant
    # name, added to every chart below via `.add_params(plant_sel)`. This
    # mirrors `country_sel` in co2_gdp_dashboard.py's linked explorer.
    #
    # Only a click on something that *is* a plant selects: marks without a
    # plant name (panel backgrounds, table headers, the P&L flows) would
    # otherwise select "no plant" and dim everything - clicking those
    # clears the selection instead, as does a double-click anywhere.
    _has_plant = "event.item && event.item.datum && event.item.datum.name"
    plant_sel = alt.selection_point(
        fields=["name"],
        on=f"click[{_has_plant}]",
        clear=f"dblclick, click[!({_has_plant})]",
        empty="all",
        name="plant_sel",
    )
    return (plant_sel,)


@app.cell(hide_code=True)
def table_chart(
    FONT_SM,
    nf,
    NF_FG,
    NF_MUTED,
    NF_PANEL,
    NF_RULE,
    alarms_f,
    alt,
    gold_f,
    dim_plants,
    maintenance_f,
    panel,
    pd,
    period_end,
    period_start,
    plant_scale,
    plant_sel,
    plot_size,
):
    # The default top-left panel: one row of stats per plant. Drawn as
    # Vega-Lite marks rather than an HTML table so it's part of the same
    # compiled spec as the other three charts - clicking a row selects that
    # plant everywhere, exactly like clicking it on any chart.
    _w, _h = plot_size()
    _plants = dim_plants[dim_plants["name"].isin(gold_f["name"].unique())]
    _energy = gold_f.groupby("name")["energy_generated_kwh"].sum()
    _possible = (gold_f["capacity_mw"] * 1000 * 24).groupby(gold_f["name"]).sum()
    _stats = pd.DataFrame(
        {
            "name": _plants["name"].values,
            "country": _plants["country_code"].values,
            "capacity": _plants["capacity_mw"].values,
        }
    ).set_index("name")
    _stats["energy"] = _energy
    _stats["cf"] = _energy / _possible
    _stats["revenue"] = gold_f.groupby("name")["revenue_eur"].sum()
    _stats["alarms"] = alarms_f.groupby("name").size()
    _stats["maint"] = maintenance_f.groupby("name")["cost_eur"].sum()
    _stats = _stats.fillna(0).sort_values("energy", ascending=False).reset_index()
    # Lifecycle, next to the name: opened during the period, or closed.
    _life = dim_plants.set_index("name")
    _opened = _life["commissioning_date"].between(period_start, period_end)
    _closed = _life["decommissioning_date"].notna() & (_life["decommissioning_date"] <= period_end)
    _stats["status"] = _stats["name"].map(
        lambda n: "closed" if _closed.get(n, False) else ("new" if _opened.get(n, False) else "")
    )

    def _eur(v):
        return f"€{v / 1e6:.2f}M" if v >= 1e6 else f"€{v / 1e3:.1f}k"

    # (header, formatter) for each numeric column, right-aligned
    _COLUMNS = [
        ("Country", lambda r: r["country"]),
        ("Capacity", lambda r: f"{r['capacity']:.1f} MW"),
        ("Energy", lambda r: f"{r['energy'] / 1e6:.1f} GWh"),
        ("Cap. factor", lambda r: f"{r['cf']:.1%}"),
        ("Revenue", lambda r: _eur(r["revenue"])),
        ("Maint. cost", lambda r: _eur(r["maint"])),
        ("Alarms", lambda r: f"{int(r['alarms'])}"),
    ]
    # Pixel layout: the plant column takes a fixed share, the rest split
    # evenly; row height is fixed by the *full* plant count (+ header), so
    # filtering plants out leaves space below instead of stretching rows.
    _name_w = _w * 0.21
    _col_w = (_w - _name_w) / len(_COLUMNS)
    _row_h = _h / (len(dim_plants) + 1)
    _PAD = 10

    _rows = _stats.assign(
        y0=[(i + 1) * _row_h for i in range(len(_stats))],
        zebra=[i % 2 for i in range(len(_stats))],
    )
    _rows["y1"] = _rows["y0"] + _row_h
    _rows["y"] = _rows["y0"] + _row_h / 2
    _cells = pd.DataFrame(
        [
            {"name": r["name"], "y": r["y"], "x": _name_w + (j + 1) * _col_w - _PAD, "text": fmt(r)}
            for _, r in _rows.iterrows()
            for j, (_, fmt) in enumerate(_COLUMNS)
        ]
    )
    _headers = pd.DataFrame(
        [{"x": _name_w + (j + 1) * _col_w - _PAD, "text": h} for j, (h, _) in enumerate(_COLUMNS)]
    )
    _rows["label"] = _rows["name"].str.removesuffix(" Solar Farm")

    _px = {"scale": None}  # positions below are raw pixels, not data
    _dim = alt.condition(plant_sel, alt.value(1.0), alt.value(0.3))

    def _row_band(zebra, fill):
        return (
            alt.Chart(_rows[_rows["zebra"] == zebra])
            .mark_rect(fill=fill)
            .encode(
                x=alt.value(0),
                x2=alt.value(_w),
                y=alt.Y("y0:Q", **_px),
                y2="y1:Q",
                tooltip=alt.value(None),
            )
            .add_params(plant_sel)
        )

    _header_y = _row_h / 2
    _header = alt.Chart(_headers).mark_text(
        align="right", baseline="middle", color=NF_MUTED, fontSize=FONT_SM, fontWeight=600
    ).encode(x=alt.X("x:Q", **_px), y=alt.value(_header_y), text="text:N")
    _plant_header = alt.Chart(alt.InlineData(values=[{}])).mark_text(
        align="left", baseline="middle", color=NF_MUTED, fontSize=FONT_SM, fontWeight=600
    ).encode(x=alt.value(_PAD + 18), y=alt.value(_header_y), text=alt.value("Plant"))
    _rule = alt.Chart(alt.InlineData(values=[{}])).mark_rule(color=NF_RULE).encode(
        x=alt.value(0), x2=alt.value(_w), y=alt.value(_row_h)
    )
    _dots = (
        alt.Chart(_rows)
        .mark_circle(size=110, opacity=1)
        .encode(
            x=alt.value(_PAD + 4),
            y=alt.Y("y:Q", **_px),
            color=alt.Color("name:N", scale=plant_scale(dim_plants["name"]), legend=None),
            opacity=_dim,
        )
        .add_params(plant_sel)
    )
    _names = (
        alt.Chart(_rows)
        .mark_text(align="left", baseline="middle", color=NF_FG, fontSize=FONT_SM, fontWeight=600)
        .encode(x=alt.value(_PAD + 18), y=alt.Y("y:Q", **_px), text="label:N", opacity=_dim)
        .add_params(plant_sel)
    )
    def _status(kind, color):
        # fixed mark colors, not a color encoding: in this layer a second
        # color scale would merge with the dots' plant-color scale
        return (
            alt.Chart(_rows[_rows["status"] == kind])
            .mark_text(align="right", baseline="middle", fontSize=FONT_SM - 2, fontWeight=600, color=color)
            .encode(x=alt.value(_name_w - 2), y=alt.Y("y:Q", **_px), text="status:N", opacity=_dim)
            .add_params(plant_sel)
        )

    _values = (
        alt.Chart(_cells)
        .mark_text(align="right", baseline="middle", color=NF_FG, fontSize=FONT_SM)
        .encode(x=alt.X("x:Q", **_px), y=alt.Y("y:Q", **_px), text="text:N", opacity=_dim)
        # every mark in a row carries its plant, so a click anywhere on the
        # row - background, dot, name or value - selects that plant
        .add_params(plant_sel)
    )

    table_chart = alt.layer(
        _row_band(0, NF_PANEL),
        _row_band(1, "#101c4f"),
        _rule,
        _plant_header,
        _header,
        _dots,
        _names,
        _status("new", nf.MINT),
        _status("closed", NF_MUTED),
        _values,
    ).properties(width=_w, height=_h, title="Plant overview")
    table_panel = panel(table_chart)
    return (table_panel,)


@app.cell(hide_code=True)
def line_chart(alt, gold_f, dim_plants, panel, plant_scale, plant_sel, plot_size):
    _daily = (
        gold_f.groupby(["name", "date"], as_index=False)["energy_generated_kwh"]
        .sum()
    )
    # y-axis: fixed-width tick labels ("2.2M" via `~s`) plus its title;
    # x-axis: dates only - "Date" as a title would just restate the ticks.
    _Y_AXIS = 44
    _chrome = {"left": _Y_AXIS + 26, "bottom": 26}
    # Axes draw *under* a view's marks by default - here that's under the
    # panel card too, so they need lifting above it.
    _ON_TOP = 1
    _w, _h = plot_size(**_chrome)
    # Ticks to suit the period: weekly over a couple of months, quarterly
    # over two years.
    _span_days = (_daily["date"].max() - _daily["date"].min()).days if len(_daily) else 0
    _x_axis = (
        alt.Axis(format="%b %Y", tickCount={"interval": "month", "step": 3}, zindex=_ON_TOP)
        if _span_days > 150
        else alt.Axis(format="%b %d", tickCount="week", zindex=_ON_TOP)
    )

    line_chart = (
        alt.Chart(_daily)
        # A stacked *area* chart, not just stacked lines: each plant gets a
        # solid colored band (with a slightly brighter stroke on top) so the
        # per-plant contribution reads as a filled region, not just an
        # outline - `stack="zero"` is what stacks the bands in the first
        # place, one on top of the other in scale-domain order.
        .mark_area(line={"strokeWidth": 1.5}, interpolate="monotone")
        .encode(
            x=alt.X("date:T", title=None, axis=_x_axis),
            y=alt.Y(
                "energy_generated_kwh:Q",
                title="Energy generated (kWh)",
                stack="zero",
                # Plants open and close during the period: a day with no row
                # for a plant is 0 kWh, or its stacked band would bridge the
                # gap from its last day to its next one.
                impute=alt.ImputeParams(value=0),
                axis=alt.Axis(
                    format="~s", minExtent=_Y_AXIS, maxExtent=_Y_AXIS, zindex=_ON_TOP
                ),
            ),
            order=alt.Order("name:N"),
            color=alt.Color(
                "name:N", scale=plant_scale(dim_plants["name"]), legend=None
            ),
            opacity=alt.condition(plant_sel, alt.value(0.85), alt.value(0.15)),
            tooltip=[
                alt.Tooltip("name:N", title="Plant"),
                alt.Tooltip("date:T", title="Date"),
                alt.Tooltip("energy_generated_kwh:Q", title="kWh", format=",.0f"),
            ],
        )
        .properties(width=_w, height=_h, title="Daily energy production by plant")
        .add_params(plant_sel)
    )
    line_panel = panel(line_chart, **_chrome)
    return line_chart, line_panel


@app.cell(hide_code=True)
def sankey_helper(FONT_SM, NF_FG, alt, pd):
    #: scope name for the unfiltered sankey (see `sankey_chart`)
    ALL = "__all__"

    def sankey_chart(
        nodes_df: pd.DataFrame,
        links_df: pd.DataFrame,
        *,
        width: int,
        height: int,
        color_scale: alt.Scale,
        node_width: int = 12,
        gap: int = 5,
        min_slot: int = 16,
        ribbon_steps: int = 24,
        selection: alt.Parameter | None = None,
        left_margin: int = 0,
        right_margin: int = 0,
        col_positions: list[float] | None = None,
    ) -> alt.LayerChart:
        """Hand-rolled multi-column sankey built from mark_area ribbons (a
        generalisation of co2_gdp_dashboard.py's two-column one).

        nodes_df: id, label, column (0, 1, ...), value, order, color_key[, name]
        links_df: source (id), target (id), value, color_key[, name]

        Every column shares one px-per-unit scale, so flows keep their
        width from column to column. Each node gets at least `min_slot` px
        of vertical room (one label line), and a column whose nodes all
        come from one earlier node starts level with it (a breakdown sits
        next to what it breaks down). Column-0 labels go left of their
        nodes, all others right; `left_margin`/`right_margin` reserve room
        for them *inside* `width`; `col_positions` (0..1 per column, default
        evenly spaced) leaves room where a middle column's labels need it.
        Nodes/links that carry a `name` take part in `selection`.

        Optional `scope` column on both frames: several complete sankeys in
        one chart, of which it shows the one whose scope is the selected
        plant's name (`ALL` when nothing is selected) - cross-filtering a
        layout that has to be computed in Python, entirely in the browser.
        """
        n_cols = int(nodes_df["column"].max()) + 1
        span = width - left_margin - right_margin - node_width
        if col_positions is None:
            col_positions = [c / (n_cols - 1) if n_cols > 1 else 0 for c in range(n_cols)]
        col_x = {c: left_margin + span * f for c, f in enumerate(col_positions)}
        def _layout(nodes_df, links_df, scope):
            """Lay out one scope's nodes and ribbons (pixel positions)."""
            parents = links_df.groupby("target")["source"].agg(lambda s: sorted(set(s)))

            def layout_for(k):
                """Stack every column at `k` px per unit; returns (layout, fits)."""
                layout, fits = {}, True
                for col in range(n_cols):
                    grp = nodes_df[nodes_df["column"] == col].sort_values("order")
                    srcs = {src for nid in grp["id"] for src in parents.get(nid, [])}
                    y = layout[next(iter(srcs))]["y0"] if len(srcs) == 1 and next(iter(srcs)) in layout else 0.0
                    for _, row in grp.iterrows():
                        h = row["value"] * k
                        layout[row["id"]] = {**row.to_dict(), "y0": y, "y1": y + h}
                        y += max(h, min_slot) + gap
                    fits &= y - gap <= height
                return layout, fits

            k = height / nodes_df.groupby("column")["value"].sum().max()
            layout, fits = layout_for(k)
            while not fits and k > 0:
                k *= 0.97
                layout, fits = layout_for(k)

            out_cursor = {nid: n["y0"] for nid, n in layout.items()}
            in_cursor = dict(out_cursor)

            def ease(t: float) -> float:
                return t * t * (3 - 2 * t)

            ribbon_rows = []
            _links = links_df.assign(
                _s=links_df["source"].map(lambda n: layout[n]["order"]),
                _t=links_df["target"].map(lambda n: layout[n]["order"]),
            ).sort_values(["_s", "_t"])
            for i, (_, row) in enumerate(_links.iterrows()):
                s, t, h = row["source"], row["target"], row["value"] * k
                sy0, ty0 = out_cursor[s], in_cursor[t]
                out_cursor[s] += h
                in_cursor[t] += h
                xl = col_x[layout[s]["column"]] + node_width
                xr = col_x[layout[t]["column"]]
                for step in range(ribbon_steps + 1):
                    frac = step / ribbon_steps
                    e = ease(frac)
                    ribbon_rows.append({
                        "link_id": f"{scope}:{i}",
                        "x": xl + frac * (xr - xl),
                        "y_top": sy0 + e * (ty0 - sy0),
                        "y_bot": sy0 + h + e * (ty0 - sy0),
                        "color_key": row["color_key"],
                        "name": row.get("name"),
                        "scope": scope,
                    })
            ribbon_df = pd.DataFrame(ribbon_rows)

            node_df = pd.DataFrame(
                [
                    {
                        "id": nid, "label": n["label"], "column": n["column"],
                        "x0": col_x[n["column"]], "x1": col_x[n["column"]] + node_width,
                        "y0": n["y0"], "y1": max(n["y1"], n["y0"] + 1),
                        "mid": n["y0"] + max(n["y1"] - n["y0"], 1) / 2,
                        "color_key": n["color_key"], "name": n.get("name"),
                        "text": n.get("text", n["label"]),
                        "scope": scope,
                    }
                    for nid, n in layout.items()
                ]
            )

            return ribbon_df, node_df

        # One layout per scope (see the docstring): each is stacked and
        # scaled on its own, so a single plant's P&L fills the chart too.
        if "scope" not in nodes_df:
            nodes_df, links_df = nodes_df.assign(scope=ALL), links_df.assign(scope=ALL)
        _parts = [
            _layout(nodes_df[nodes_df["scope"] == sc], links_df[links_df["scope"] == sc], sc)
            for sc in nodes_df["scope"].unique()
        ]
        ribbon_df = pd.concat([r for r, _ in _parts], ignore_index=True)
        node_df = pd.concat([n for _, n in _parts], ignore_index=True)

        _px = {"scale": None}  # raw pixel positions
        _color = alt.Color("color_key:N", scale=color_scale, legend=None)

        # Show the scope matching the selected plant, or ALL with none.
        if selection is not None:
            _sel = selection.name
            _in_scope = (
                f"datum.scope == (isValid({_sel}) && isValid({_sel}.name) && isValid({_sel}.name[0])"
                f" ? {_sel}.name[0] : '{ALL}')"
            )
        else:
            _in_scope = f"datum.scope == '{ALL}'"

        def _inline(df):
            """Embed the frame in the spec as plain JSON rows. The default
            transport (an Arrow file, when pyarrow is installed) turned the
            string columns - labels, colour keys - into `null` in the browser."""
            return alt.InlineData(values=df.astype(object).where(df.notna(), None).to_dict("records"))

        def ribbons(df, opacity):
            chart = (
                alt.Chart(_inline(df))
                .transform_filter(_in_scope)
                .mark_area(interpolate="linear")
                .encode(
                    x=alt.X("x:Q", **_px),
                    y=alt.Y("y_bot:Q", **_px),
                    y2="y_top:Q",
                    detail="link_id:N",
                    color=_color,
                    opacity=opacity,
                )
            )
            return chart

        def nodes(df, opacity):
            return (
                alt.Chart(_inline(df))
                .transform_filter(_in_scope)
                .mark_rect()
                .encode(
                    x=alt.X("x0:Q", **_px), x2="x1:Q",
                    y=alt.Y("y0:Q", **_px), y2="y1:Q",
                    color=_color,
                    opacity=opacity,
                    tooltip=[alt.Tooltip("text:N", title="")],
                )
            )

        # Rows that carry a plant `name` (the plants' own nodes and ribbons)
        # are what a click selects - which then swaps in that plant's scope.
        _named = ribbon_df["name"].notna()
        layers = [
            ribbons(ribbon_df[~_named], alt.value(0.45)),
            ribbons(ribbon_df[_named], alt.value(0.55)),
            nodes(node_df[node_df["name"].isna()], alt.value(1.0)),
            nodes(node_df[node_df["name"].notna()], alt.value(1.0)),
        ]
        if selection is not None:
            layers[1] = layers[1].add_params(selection)
            layers[3] = layers[3].add_params(selection)

        _label = {"baseline": "middle", "color": NF_FG, "fontSize": FONT_SM - 1, "lineBreak": "\n"}
        layers += [
            alt.Chart(_inline(node_df[node_df["column"] == 0]))
            .transform_filter(_in_scope)
            .mark_text(align="right", dx=-5, **_label)
            .encode(x=alt.X("x0:Q", **_px), y=alt.Y("mid:Q", **_px), text="text:N"),
            alt.Chart(_inline(node_df[node_df["column"] > 0]))
            .transform_filter(_in_scope)
            .mark_text(align="left", dx=5, **_label)
            .encode(x=alt.X("x1:Q", **_px), y=alt.Y("mid:Q", **_px), text="text:N"),
        ]

        # No `.configure_view()` here: this chart gets concatenated with the
        # other three in `explorer_layout`, and Vega-Lite only allows "config"
        # properties on the single top-level spec of a composed chart.
        return alt.layer(*layers).properties(width=width, height=height)

    return ALL, sankey_chart


@app.cell(hide_code=True)
def sankey_build(
    ALL,
    NF_MUTED,
    alt,
    dim_plants,
    nf,
    panel,
    plant_scale,
    plant_sel,
    plot_size,
    pnl,
    pd,
    sankey_chart,
):
    # The fleet's P&L as a flow: each plant's revenue -> total revenue ->
    # where it goes (operating costs, depreciation, interest, tax, net
    # profit), with operating costs broken down once more on the right.
    # Built once for the whole fleet and once per plant: clicking a plant
    # anywhere swaps in that plant's own P&L (see `sankey_chart`'s scopes).
    _SPLIT = ["Operating costs", "Depreciation", "Interest", "Tax", "Net profit"]
    _OPEX = ["O&M contract", "Grid fees", "Land lease", "Insurance", "Asset management", "Corrective maintenance"]

    def _eur(v):
        return f"€{v / 1e6:.1f}M" if abs(v) >= 1e6 else f"€{v / 1e3:.0f}k"

    def _flow(rows, scope):
        tot = rows.drop(columns="name").sum()
        revenue = tot["Revenue"]
        pct = lambda v: f" ({v / revenue:.0%})" if revenue else ""
        nodes, links = [], []
        for i, r in enumerate(rows[rows["Revenue"] > 0].sort_values("Revenue", ascending=False).itertuples()):
            short = r.name.removesuffix(" Solar Farm")
            nodes.append({"id": r.name, "label": short, "text": short, "column": 0, "value": r.Revenue,
                          "order": i, "color_key": r.name, "name": r.name})
            links.append({"source": r.name, "target": "Revenue", "value": r.Revenue, "color_key": r.name, "name": r.name})
        nodes.append({"id": "Revenue", "label": "Revenue", "text": f"Revenue\n{_eur(revenue)}", "column": 1,
                      "value": revenue, "order": 0, "color_key": "Revenue"})
        for i, cat in enumerate(_SPLIT):
            key = "Profit" if cat == "Net profit" else "Cost"
            nodes.append({"id": cat, "label": cat, "text": f"{cat} {_eur(tot[cat])}{pct(tot[cat])}",
                          "column": 2, "value": max(tot[cat], 0), "order": i, "color_key": key})
            links.append({"source": "Revenue", "target": cat, "value": max(tot[cat], 0), "color_key": key})
        for i, cat in enumerate(_OPEX):
            label = "Corrective maint." if cat == "Corrective maintenance" else cat
            nodes.append({"id": cat, "label": label, "text": f"{label} {_eur(tot[cat])}", "column": 3,
                          "value": tot[cat], "order": i, "color_key": "Cost"})
            links.append({"source": "Operating costs", "target": cat, "value": tot[cat], "color_key": "Cost"})
        return (pd.DataFrame(nodes).assign(scope=scope), pd.DataFrame(links).assign(scope=scope))

    _scopes = [_flow(pnl, ALL)] + [
        _flow(pnl[pnl["name"] == n], n) for n in pnl.loc[pnl["Revenue"] > 0, "name"]
    ]
    _nodes = pd.concat([n for n, _ in _scopes], ignore_index=True)
    _links = pd.concat([l for _, l in _scopes], ignore_index=True)

    # Plants keep their own colors; money out is neutral gray, profit mint.
    _plant_colors = plant_scale(dim_plants["name"])
    _keys = list(_plant_colors.domain) + ["Revenue", "Cost", "Profit"]
    _range = list(_plant_colors.range) + [nf.BLUE, NF_MUTED, nf.MINT]

    _w, _h = plot_size()
    sankey_chart_out = sankey_chart(
        _nodes,
        _links,
        width=_w,
        height=_h,
        color_scale=alt.Scale(domain=_keys, range=_range),
        selection=plant_sel,
        left_margin=105,
        right_margin=150,
        # the middle column's labels ("Operating costs €2.0M (18%)") need
        # clear space before the breakdown column on the right
        col_positions=[0, 0.2, 0.44, 1],
    ).properties(title="Revenue allocation")
    sankey_panel = panel(sankey_chart_out)
    return (sankey_panel,)


@app.cell(hide_code=True)
def bar_chart(EVENT_COLORS, alt, maintenance_f, panel, plant_sel, plot_size):
    # Not in the layout right now (the revenue/cost/profit chart took its
    # slot) - kept so it can be swapped back in via `explorer_layout`.
    _cost_by_plant_type = (
        maintenance_f.groupby(["name", "event_type"], as_index=False)["cost_eur"].sum()
    )
    # Raw values are snake_case identifiers ("corrective_repair") - fine for
    # code, not for a legend/tooltip a human reads. Clean the *data* once
    # here rather than patching it up per-encoding with a Vega `labelExpr`,
    # so the legend and the tooltip (which shows the same field) both get
    # the readable form for free, and stay in sync if it changes.
    _cost_by_plant_type["event_type"] = _cost_by_plant_type["event_type"].str.replace(
        "_", " "
    ).str.capitalize()

    # y-axis: plant names at a fixed width; below the plot, the x-axis (with
    # its title) and then the event-type legend laid out in one row.
    _Y_AXIS = 120
    _chrome = {"left": _Y_AXIS + 4, "bottom": 72}
    _ON_TOP = 1  # axes above the panel card - see `line_chart`
    _w, _h = plot_size(**_chrome)

    bar_chart = (
        alt.Chart(_cost_by_plant_type)
        .mark_bar()
        .encode(
            x=alt.X(
                "cost_eur:Q",
                title="Maintenance cost (EUR)",
                stack="zero",
                axis=alt.Axis(format="~s", zindex=_ON_TOP),
            ),
            y=alt.Y(
                "name:N",
                title=None,
                sort="-x",
                # Same shortening as the sankey's node labels: every plant
                # name ends in "Solar Farm" (the tooltip keeps the full name).
                axis=alt.Axis(
                    labelExpr="replace(datum.label, ' Solar Farm', '')",
                    minExtent=_Y_AXIS,
                    maxExtent=_Y_AXIS,
                    labelLimit=_Y_AXIS,
                    zindex=_ON_TOP,
                ),
            ),
            color=alt.Color(
                "event_type:N",
                title="Event type",
                scale=alt.Scale(domain=list(EVENT_COLORS), range=list(EVENT_COLORS.values())),
                legend=alt.Legend(orient="bottom", direction="horizontal", titleOrient="left", offset=10),
            ),
            opacity=alt.condition(plant_sel, alt.value(1.0), alt.value(0.3)),
            tooltip=[
                alt.Tooltip("name:N", title="Plant"),
                alt.Tooltip("event_type:N", title="Event type"),
                alt.Tooltip("cost_eur:Q", title="Cost (EUR)", format=",.0f"),
            ],
        )
        .properties(width=_w, height=_h, title="Maintenance cost")
        .add_params(plant_sel)
    )
    bar_panel = panel(bar_chart, **_chrome)
    return (bar_panel,)


@app.cell(hide_code=True)
def pnl_chart(
    FONT_SM,
    NF_FG,
    NF_MUTED,
    PANEL_TITLE_H,
    alt,
    gold_f,
    nf,
    panel,
    pd,
    plant_sel,
    plot_size,
    pnl_monthly,
):
    # Fleet revenue, cost and profit per month - grouped bars, not split by
    # plant. It still takes part in the cross-filter, just differently from
    # the other charts: rather than dimming, it *filters* its per-plant rows
    # by `plant_sel` before summing, so clicking a plant elsewhere turns the
    # bars into that plant's own figures (and the empty selection -
    # `empty="all"` - keeps every plant). Same P&L as the sankey: cost is
    # everything between revenue and net profit (operating costs incl.
    # repairs, depreciation, interest, tax).
    _MEASURES = {"Revenue": nf.BLUE, "Cost": NF_MUTED, "Profit": nf.MINT}
    _long = pd.DataFrame(
        {
            "name": pnl_monthly["name"],
            "month": pnl_monthly["month"],
            "Revenue": pnl_monthly["Revenue"],
            "Cost": pnl_monthly["Revenue"] - pnl_monthly["Net profit"],
            "Profit": pnl_monthly["Net profit"],
        }
    ).melt(id_vars=["name", "month"], var_name="measure", value_name="amount")

    # Month labels. Over a few months, a partly-covered month says so
    # ("Jul 23–31") so a short bar reads as fewer days, not a bad month;
    # over two years that's too much text, so axis labels become "Jan 25"
    # (shown once a quarter) and the coverage moves into the tooltip.
    _days = gold_f.groupby(gold_f["date"].dt.strftime("%Y-%m"))["date"].agg(["min", "max"])
    _months = sorted(_long["month"].unique())
    _few = len(_months) <= 6

    def _coverage(m):
        lo, hi = _days.loc[m, "min"], _days.loc[m, "max"]
        if lo.day == 1 and hi.day == hi.days_in_month:
            return lo.strftime("%B %Y")
        return f"{lo.strftime('%b')} {lo.day}–{hi.day} {lo.year}"

    def _month_label(m):
        lo, hi = _days.loc[m, "min"], _days.loc[m, "max"]
        if not _few:
            return lo.strftime("%b %y")
        if lo.day == 1 and hi.day == hi.days_in_month:
            return lo.strftime("%b")  # the Period timeline shows the year
        return f"{lo.strftime('%b')} {lo.day}–{hi.day}"

    _long["month_label"] = _long["month"].map({m: _month_label(m) for m in _months})
    _long["coverage"] = _long["month"].map({m: _coverage(m) for m in _months})
    _month_order = [_month_label(m) for m in _months]

    _Y_AXIS = 44
    _chrome = {"left": _Y_AXIS + 4, "bottom": 56}
    _w, _h = plot_size(**_chrome)
    _ON_TOP = 1  # axes above the panel card - see `line_chart`
    _euro = "'€' + format(datum.{}, '.2~s')"

    _totals = (
        alt.Chart(_long)
        .transform_filter(plant_sel)
        .transform_aggregate(amount="sum(amount)", groupby=["month_label", "coverage", "measure"])
        .transform_calculate(label=_euro.format("amount"))
    )
    _x = alt.X(
        "month_label:N",
        sort=_month_order,
        title=None,
        scale=alt.Scale(paddingInner=0.3, paddingOuter=0.15),
        axis=alt.Axis(
            labelAngle=0,
            labelColor=NF_FG,
            labelFontSize=FONT_SM,
            zindex=_ON_TOP,
            ticks=_few,
            labelExpr=(
                "datum.label"
                if _few
                else "indexof(['Jan', 'Apr', 'Jul', 'Oct'], substring(datum.label, 0, 3)) >= 0 ? datum.label : ''"
            ),
        ),
    )
    _x_offset = alt.XOffset("measure:N", sort=list(_MEASURES), scale=alt.Scale(paddingInner=0.12))
    # The axis stays fixed at the fleet's best month (+ headroom for the
    # value labels): a selected plant's bars then visibly shrink to its
    # share, instead of the axis rescaling so every plant looks the same.
    _fleet_max = max(pnl_monthly.groupby("month")["Revenue"].sum().max(), 1)
    _y = alt.Y(
        "amount:Q",
        title=None,
        scale=alt.Scale(domain=[0, _fleet_max * 1.15]),
        axis=alt.Axis(
            labelExpr=_euro.format("value"),
            minExtent=_Y_AXIS,
            maxExtent=_Y_AXIS,
            tickCount=5,
            zindex=_ON_TOP,
        ),
    )
    _bars = _totals.mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
        x=_x,
        xOffset=_x_offset,
        y=_y,
        color=alt.Color(
            "measure:N",
            title=None,
            scale=alt.Scale(domain=list(_MEASURES), range=list(_MEASURES.values())),
            legend=alt.Legend(orient="bottom", direction="horizontal", offset=12),
        ),
        tooltip=[
            alt.Tooltip("coverage:N", title="Month"),
            alt.Tooltip("measure:N", title="Measure"),
            alt.Tooltip("amount:Q", title="EUR", format=",.0f"),
        ],
    )
    _values = _totals.mark_text(
        baseline="bottom", dy=-4, color=NF_FG, fontSize=FONT_SM - 2, fontWeight=600
    ).encode(x=_x, xOffset=_x_offset, y=_y, text="label:N")
    # Which plant the bars show right now - `plant_sel` resolves to
    # {name: [...]} once something is clicked, and to {} when cleared.
    _scope = (
        alt.Chart(alt.InlineData(values=[{}]))
        .transform_calculate(
            label="isValid(plant_sel.name) ? replace(plant_sel.name[0], ' Solar Farm', '') : 'All plants'"
        )
        # right end of the panel's title strip, level with the title
        .mark_text(align="right", baseline="top", color=NF_MUTED)
        .encode(x=alt.value(_w), y=alt.value(-(PANEL_TITLE_H + 2)), text="label:N")
    )

    # per-bar values only while there are few enough bars to label
    pnl_chart = alt.layer(*([_bars, _values] if _few else [_bars]), _scope).properties(
        width=_w, height=_h, title="Revenue, cost & profit by month"
    )
    pnl_panel = panel(pnl_chart, **_chrome)
    return (pnl_panel,)


@app.cell(hide_code=True)
def explorer_layout(
    PANEL_GAP,
    alt,
    line_panel,
    mo,
    pnl_panel,
    sankey_panel,
    table_panel,
    warnings,
):
    # Combine all four paneled charts into ONE compiled Vega-Lite spec (a
    # 2x2 grid via hconcat + vconcat) and wrap that combined spec in a single
    # `mo.ui.altair_chart` - this is what lets the one `plant_sel` selection,
    # added to each chart above, stay in sync across all of them live in the
    # browser: clicking a plant on any chart re-highlights it on the rest.
    # Vega-Lite's default "shared" scale resolution only unifies same-field
    # color scales within *one* concat operator - the sankey colors by plant
    # ("name") while the bar chart colors by `event_type`, so each column
    # needs its own independent resolve too, not just the outer one.
    #
    # Reusing the *same* `plant_sel` object across all four charts (rather
    # than four separate-but-identical selections) is exactly what makes
    # Vega-Lite treat them as one shared, synced selection - Altair's own
    # "deduplicated selection parameter" warning is just it noticing that on
    # purpose, so it's silenced here rather than left to alarm anyone
    # reading the terminal during a live demo.
    #
    # Grouped by ROW, and no alignment compensation needed: every panel's
    # card spans its chart's axes and legend (see grid_layout's `panel()`),
    # so all four grid slots are exactly the same size, and every chart has
    # the same top chrome (the title strip), so a row's plots line up too.
    # (Grouping by column instead would line up each column's *plot
    # origins* - different for the line and bar charts' different y-axes -
    # pushing their cards out of line. `alt.concat(..., align="all")` is
    # off the table too: in this combination it broke every tooltip and the
    # sankey's text labels.)
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore", message=r"Automatically deduplicated selection parameter.*"
        )
        _rows = [
            (table_panel | line_panel).resolve_scale(color="independent"),
            (sankey_panel | pnl_panel).resolve_scale(color="independent"),
        ]
        explorer = (
            alt.vconcat(*_rows, spacing=PANEL_GAP)
            .resolve_scale(color="independent")
            .resolve_legend(color="independent")
            # no outer padding, so the chart renders exactly DASHBOARD_WIDTH wide
            .properties(padding=0)
            .configure_concat(spacing=PANEL_GAP)
            # No grid lines: axes are lifted above the panel card (`zindex`
            # on each chart's axes), so grid lines would cross areas/bars.
            .configure_axis(grid=False)
            .configure_view(strokeWidth=0)
        )

    # No vega-embed "..." actions menu: while it's enabled, vega-embed pads
    # its wrapper 38px on the right for the button, which clips the last
    # 38px of this exactly-DASHBOARD_WIDTH chart. `mo.ui.altair_chart` reads
    # altair's renderer `embed_options` once, at construction - so scoping
    # them to this `with` keeps every other chart's menu as it is.
    with alt.renderers.enable(alt.renderers.active, embed_options={"actions": False}):
        explorer_view = mo.ui.altair_chart(explorer)
    explorer_view
    return (explorer_view,)


if __name__ == "__main__":
    app.run()
