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

    return Path, alt, mo, nf, pd, warnings


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

    #: One color per plant (7), assigned alphabetically - never cycled, so
    #: no two plants share one. The brand accents plus two brand-derived
    #: steps (a mint shade, a purple tint) in place of theme.py's PALE_BLUE,
    #: which read as the same near-gray as PALE_MINT. Checked with the
    #: dataviz skill's palette validator on NF_PANEL: in this order every
    #: *adjacent* pair - neighbors in the stacked area and the sankey -
    #: clears ΔE 31 (normal vision) / 21 (color-blind). The weakest pair
    #: overall is BLUE vs PURPLE, never adjacent; the table and tooltips
    #: always name plants too. The bright brand accents sit above the validator's
    #: dark-mode lightness band by design.
    PLANT_COLORS = [
        nf.LAVENDER,
        nf.PURPLE,
        "#00B383",  # mint, one step darker
        nf.PALE_MINT,
        nf.BLUE,
        nf.MINT,
        "#B18CFF",  # purple, one step lighter
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
def load_data(Path, pd):
    # All five datasets were produced by the SolarDataPlatform project's
    # `solar-data-gen` generator (7 synthetic plants, 60 days of daily
    # billing/costs/alarms/maintenance) and copied into data/solar/ - see
    # data/solar/README.md for how to regenerate them.
    DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "solar"

    dim_plants = pd.read_csv(DATA_DIR / "dim_plants.csv", parse_dates=["commissioning_date"])
    fact_billing = pd.read_csv(DATA_DIR / "fact_energy_billing.csv", parse_dates=["billing_date"])
    fact_alarms = pd.read_csv(
        DATA_DIR / "fact_alarm_events.csv", parse_dates=["triggered_at", "cleared_at"]
    )
    fact_maintenance = pd.read_csv(
        DATA_DIR / "fact_maintenance_events.csv",
        parse_dates=["scheduled_date", "completed_date"],
    )
    fact_costs = pd.read_csv(DATA_DIR / "fact_plant_costs.csv", parse_dates=["cost_date"])
    return dim_plants, fact_alarms, fact_billing, fact_costs, fact_maintenance


@app.cell(hide_code=True)
def denormalize(dim_plants, fact_alarms, fact_billing, fact_costs, fact_maintenance):
    # Every fact table only carries `plant_id`; join in the human-readable
    # plant `name` once here so every downstream chart/filter can work with
    # "location" (plant name) directly instead of repeating the join.
    # `capacity_mw` rides along for the capacity-factor KPI.
    _plant_names = dim_plants[["plant_id", "name", "country_code", "capacity_mw"]]

    billing = fact_billing.merge(_plant_names, on="plant_id")
    alarms = fact_alarms.merge(_plant_names, on="plant_id")
    maintenance = fact_maintenance.merge(_plant_names, on="plant_id")
    costs = fact_costs.merge(_plant_names, on="plant_id")

    #: Business regions for the Region filter. With one plant per country a
    #: country filter would just duplicate the Plants one.
    REGIONS = {"GB": "EMEA", "NL": "EMEA", "DE": "EMEA", "RU": "EMEA", "CA": "Americas", "BR": "Americas", "MM": "APAC"}
    plant_region = dict(zip(dim_plants["name"], dim_plants["country_code"].map(REGIONS).fillna("Other")))
    return alarms, billing, costs, maintenance, plant_region


@app.cell(hide_code=True)
def filters(
    FONT_SM,
    NF_FG,
    NF_MUTED,
    NF_RULE,
    PANEL_GAP,
    alt,
    billing,
    dim_plants,
    mo,
    nf,
    pd,
    plant_region,
):
    _min_date, _max_date = billing["billing_date"].min(), billing["billing_date"].max()

    # Short labels ("Dorval"), full names as values: every plant name ends
    # in "Solar Farm", which only made the selected chips overflow.
    location_filter = mo.ui.multiselect(
        options={n.removesuffix(" Solar Farm"): n for n in sorted(dim_plants["name"])},
        value=[n.removesuffix(" Solar Farm") for n in sorted(dim_plants["name"])],
        full_width=True,
    )
    _regions = sorted(set(plant_region.values()))
    region_filter = mo.ui.multiselect(options=_regions, value=_regions, full_width=True)

    # Period: a timeline "range slider" over the last two years - marimo's
    # own range slider is numeric-only (no date labels), so this is a thin
    # Vega-Lite strip instead: daily fleet energy shows where there's data,
    # and dragging a brush across it picks the period. The brush starts on
    # the range the data actually covers.
    _W = 2 * 367 + PANEL_GAP  # spans two card columns
    _timeline_days = pd.DataFrame(
        {"date": pd.date_range(_max_date - pd.DateOffset(years=2), _max_date, freq="D")}
    )
    _timeline_days["energy"] = (
        _timeline_days["date"]
        .map(billing.groupby("billing_date")["energy_generated_kwh"].sum())
        .fillna(0)
    )
    _dt = lambda d: alt.DateTime(year=d.year, month=d.month, date=d.day)
    _brush = alt.selection_interval(
        name="period",
        encodings=["x"],
        value={"x": [_dt(_min_date), _dt(_max_date)]},
        mark=alt.BrushConfig(fill=nf.MINT, fillOpacity=0.18, stroke=nf.MINT, strokeWidth=1),
    )
    _timeline = (
        alt.Chart(_timeline_days)
        .mark_area(color=nf.MINT, opacity=0.7, interpolate="step-after")
        .encode(
            x=alt.X(
                "date:T",
                title=None,
                axis=alt.Axis(
                    format="%b %Y",
                    tickCount={"interval": "month", "step": 3},
                    labelColor=NF_MUTED,
                    labelFontSize=FONT_SM - 1,
                    domainColor=NF_RULE,
                    tickColor=NF_RULE,
                    grid=False,
                ),
            ),
            y=alt.Y("energy:Q", axis=None),
        )
        .add_params(_brush)
        .properties(
            width=_W,
            height=18,
            # fit the *width* (month labels included) to the two columns;
            # the height is the strip itself, with the axis below it
            autosize=alt.AutoSizeParams(type="fit-x", contains="padding"),
            padding={"left": 2, "right": 24, "top": 2, "bottom": 0},
        )
        .configure_view(strokeWidth=1, stroke=NF_RULE)
    )
    # no "..." actions menu - it reserves 38px on the right (see explorer_layout)
    with alt.renderers.enable(alt.renderers.active, embed_options={"actions": False}):
        period_filter = mo.ui.altair_chart(_timeline, legend_selection=False)

    def _slot(label, widget, *, span=1):
        """One filter per stat-card column (or `span` of them): its label
        above, the control stretched to the column's full width."""
        return (
            f'<div style="min-width:0; grid-column:span {span};">'
            f'<div style="color:{NF_MUTED}; font-size:{FONT_SM}px; margin-bottom:4px;">{label}</div>'
            f"{mo.as_html(widget).text}</div>"
        )

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
        f'{_slot("Period - drag across the timeline", period_filter, span=2)}'
        f'{_slot("Region", region_filter)}</div>'
    )
    return location_filter, period_filter, region_filter


@app.cell(hide_code=True)
def apply_filters(
    alarms,
    billing,
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

    # The timeline brush's range, as `{"period": {"date": [start_ms, end_ms]}}`
    # - epoch milliseconds of the *browser's local* time, so a local
    # midnight arrives as e.g. 22:00 UTC the day before. Rounding to the
    # nearest day (rather than truncating) lands on the intended date for
    # any browser timezone within ±12h. No brush (never dragged, or
    # cleared) means the whole data range.
    _brushed = (period_filter.selections or {}).get("period", {}).get("date")
    if _brushed and len(_brushed) == 2:
        period_start, period_end = (
            (pd.to_datetime(v, unit="ms") if isinstance(v, (int, float)) else pd.to_datetime(v))
            .tz_localize(None)
            .round("D")
            for v in _brushed
        )
    else:
        period_start, period_end = billing["billing_date"].min(), billing["billing_date"].max()
    _start, _end = period_start.date(), period_end.date()

    billing_f = billing[
        billing["name"].isin(_locations) & billing["billing_date"].dt.date.between(_start, _end)
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
    _b = billing_f.assign(month=_month(billing_f["billing_date"]))
    _c = costs_f.assign(month=_month(costs_f["cost_date"]))
    _m = maintenance_f.assign(month=_month(maintenance_f["scheduled_date"]))

    def _pnl_by(keys):
        out = _b.groupby(keys)[["revenue_eur"]].sum().rename(columns={"revenue_eur": "Revenue"})
        by_cat = _c.pivot_table(index=keys, columns="category", values="amount_eur", aggfunc="sum")
        for cat in _OPEX + ["Depreciation", "Interest"]:
            out[cat] = by_cat[cat] if cat in by_cat else 0.0
        out["Corrective maintenance"] = _m.groupby(keys)["cost_eur"].sum()
        out = out.fillna(0.0)
        out["Operating costs"] = out[_OPEX + ["Corrective maintenance"]].sum(axis=1)
        pre_tax = out["Revenue"] - out["Operating costs"] - out["Depreciation"] - out["Interest"]
        out["Tax"] = (pre_tax.clip(lower=0) * _TAX_RATE).round(2)
        out["Net profit"] = pre_tax - out["Tax"]
        return out.reset_index()

    pnl = _pnl_by(["name"])
    pnl_monthly = _pnl_by(["name", "month"])
    return alarms_f, billing_f, maintenance_f, period_end, period_start, pnl, pnl_monthly


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

    def delta_html(change: float | None, *, higher_is_better: bool) -> str:
        """Week-over-week change: arrow + percentage, colored better/worse
        (the arrow and number carry the meaning; color only reinforces it)."""
        if change is None:
            return f'<span style="color:{NF_MUTED};">no prior week to compare</span>'
        if abs(change) < 0.0005:
            return f'<span style="color:{NF_MUTED};">&#9644; 0.0% vs prior 7 days</span>'
        good = (change > 0) == higher_is_better
        arrow = "&#9650;" if change > 0 else "&#9660;"
        return (
            f'<span style="color:{STATUS_GOOD if good else STATUS_BAD}; font-weight:600;">'
            f"{arrow} {abs(change):.1%}</span>"
            f'<span style="color:{NF_MUTED};"> vs prior 7 days</span>'
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
    billing_f,
    delta_html,
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

    def _window(lo, hi):
        """The three frames cut to days lo..hi (inclusive)."""
        return (
            billing_f[billing_f["billing_date"].between(lo, hi)],
            alarms_f[alarms_f["triggered_at"].dt.tz_localize(None).dt.normalize().between(lo, hi)],
            maintenance_f[maintenance_f["scheduled_date"].between(lo, hi)],
        )

    _last = _window(_end - pd.Timedelta(days=6), _end)
    _prior = _window(_end - pd.Timedelta(days=13), _end - pd.Timedelta(days=7))
    _has_prior = _start <= _end - pd.Timedelta(days=13)

    def _change(metric):
        if not _has_prior:
            return None
        now, before = metric(*_last), metric(*_prior)
        if now is None or not before:
            return None
        return now / before - 1

    # Trends: daily for the production/revenue KPIs, weekly for the sparse
    # event-based ones (a few alarms a day would just be noise).
    _days = pd.date_range(_start, _end, freq="D")
    _weeks = pd.date_range(_start, _end, freq="7D")

    def _trend(metric, starts, length):
        vals = [metric(*_window(d, d + length - pd.Timedelta(days=1))) for d in starts]
        return sparkline([0 if v is None else v for v in vals])

    _day, _week = pd.Timedelta(days=1), pd.Timedelta(days=7)

    def _eur(v):
        if v >= 1e6:
            return f"€{v / 1e6:.1f}M"
        return f"€{v / 1e3:.1f}k" if v >= 1e3 else f"€{v:.0f}"

    _b, _a, _m = billing_f, alarms_f, maintenance_f
    _cf, _price_v, _mttr_v = _capacity_factor(_b, _a, _m), _price(_b, _a, _m), _mttr(_b, _a, _m)
    _kpis = [
        # (label, value, metric, higher_is_better, trend buckets)
        ("Energy produced", f"{_energy(_b, _a, _m) / 1e6:,.1f} GWh", _energy, True, (_days, _day)),
        ("Capacity factor", "—" if _cf is None else f"{_cf:.1%}", _capacity_factor, True, (_days, _day)),
        ("Revenue", _eur(_revenue(_b, _a, _m)), _revenue, True, (_days, _day)),
        ("Avg. price", "—" if _price_v is None else f"€{_price_v:.1f}/MWh", _price, True, (_days, _day)),
        ("Alarms", f"{_alarms(_b, _a, _m):,}", _alarms, False, (_weeks, _week)),
        ("Critical alarms", f"{_critical(_b, _a, _m):,}", _critical, False, (_weeks, _week)),
        ("Mean time to resolve", "—" if _mttr_v is None else f"{_mttr_v:.1f} h", _mttr, False, (_weeks, _week)),
        ("Maintenance cost", _eur(_maint_cost(_b, _a, _m)), _maint_cost, False, (_weeks, _week)),
    ]
    stat_row(
        [
            stat_card(
                label,
                value,
                delta_html(_change(metric), higher_is_better=better),
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
    plant_sel = alt.selection_point(
        fields=["name"], on="click", clear="dblclick", empty="all", name="plant_sel"
    )
    return (plant_sel,)


@app.cell(hide_code=True)
def table_chart(
    FONT_SM,
    NF_FG,
    NF_MUTED,
    NF_PANEL,
    NF_RULE,
    alarms_f,
    alt,
    billing_f,
    dim_plants,
    maintenance_f,
    panel,
    pd,
    plant_scale,
    plant_sel,
    plot_size,
):
    # The default top-left panel: one row of stats per plant. Drawn as
    # Vega-Lite marks rather than an HTML table so it's part of the same
    # compiled spec as the other three charts - clicking a row selects that
    # plant everywhere, exactly like clicking it on any chart.
    _w, _h = plot_size()
    _plants = dim_plants[dim_plants["name"].isin(billing_f["name"].unique())]
    _energy = billing_f.groupby("name")["energy_generated_kwh"].sum()
    _possible = (billing_f["capacity_mw"] * 1000 * 24).groupby(billing_f["name"]).sum()
    _stats = pd.DataFrame(
        {
            "name": _plants["name"].values,
            "country": _plants["country_code"].values,
            "capacity": _plants["capacity_mw"].values,
        }
    ).set_index("name")
    _stats["energy"] = _energy
    _stats["cf"] = _energy / _possible
    _stats["revenue"] = billing_f.groupby("name")["revenue_eur"].sum()
    _stats["alarms"] = alarms_f.groupby("name").size()
    _stats["maint"] = maintenance_f.groupby("name")["cost_eur"].sum()
    _stats = _stats.fillna(0).sort_values("energy", ascending=False).reset_index()

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
        _values,
    ).properties(width=_w, height=_h, title="Plant overview")
    table_panel = panel(table_chart)
    return (table_panel,)


@app.cell(hide_code=True)
def line_chart(alt, billing_f, dim_plants, panel, plant_scale, plant_sel, plot_size):
    _daily = (
        billing_f.groupby(["name", "billing_date"], as_index=False)["energy_generated_kwh"]
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

    line_chart = (
        alt.Chart(_daily)
        # A stacked *area* chart, not just stacked lines: each plant gets a
        # solid colored band (with a slightly brighter stroke on top) so the
        # per-plant contribution reads as a filled region, not just an
        # outline - `stack="zero"` is what stacks the bands in the first
        # place, one on top of the other in scale-domain order.
        .mark_area(line={"strokeWidth": 1.5}, interpolate="monotone")
        .encode(
            x=alt.X(
                "billing_date:T",
                title=None,
                # one tick a week - left to itself Vega crams in near-daily ticks
                axis=alt.Axis(format="%b %d", tickCount="week", zindex=_ON_TOP),
            ),
            y=alt.Y(
                "energy_generated_kwh:Q",
                title="Energy generated (kWh)",
                stack="zero",
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
                alt.Tooltip("billing_date:T", title="Date"),
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
        Nodes/links that carry a `name` take part in `selection` (dimming
        when another plant is selected).
        """
        n_cols = int(nodes_df["column"].max()) + 1
        span = width - left_margin - right_margin - node_width
        if col_positions is None:
            col_positions = [c / (n_cols - 1) if n_cols > 1 else 0 for c in range(n_cols)]
        col_x = {c: left_margin + span * f for c, f in enumerate(col_positions)}
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
                    "link_id": i,
                    "x": xl + frac * (xr - xl),
                    "y_top": sy0 + e * (ty0 - sy0),
                    "y_bot": sy0 + h + e * (ty0 - sy0),
                    "color_key": row["color_key"],
                    "name": row.get("name"),
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
                }
                for nid, n in layout.items()
            ]
        )

        _px = {"scale": None}  # raw pixel positions
        _color = alt.Color("color_key:N", scale=color_scale, legend=None)

        def _dimmed(on, off):
            return alt.condition(selection, alt.value(on), alt.value(off)) if selection is not None else alt.value(on)

        def ribbons(df, opacity):
            chart = (
                alt.Chart(df)
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
                alt.Chart(df)
                .mark_rect()
                .encode(
                    x=alt.X("x0:Q", **_px), x2="x1:Q",
                    y=alt.Y("y0:Q", **_px), y2="y1:Q",
                    color=_color,
                    opacity=opacity,
                    tooltip=[alt.Tooltip("text:N", title="")],
                )
            )

        # Only rows that carry a plant `name` take part in the selection:
        # plant nodes and their ribbons dim when another plant is picked,
        # the P&L breakdown downstream stays as it is.
        _named = ribbon_df["name"].notna()
        layers = [
            ribbons(ribbon_df[~_named], alt.value(0.45)),
            ribbons(ribbon_df[_named], _dimmed(0.55, 0.12)),
            nodes(node_df[node_df["name"].isna()], alt.value(1.0)),
            nodes(node_df[node_df["name"].notna()], _dimmed(1.0, 0.3)),
        ]
        if selection is not None:
            layers[1] = layers[1].add_params(selection)
            layers[3] = layers[3].add_params(selection)

        _label = dict(baseline="middle", color=NF_FG, fontSize=FONT_SM - 1, lineBreak="\n")
        layers += [
            alt.Chart(node_df[node_df["column"] == 0])
            .mark_text(align="right", dx=-5, **_label)
            .encode(x=alt.X("x0:Q", **_px), y=alt.Y("mid:Q", **_px), text="text:N"),
            alt.Chart(node_df[node_df["column"] > 0])
            .mark_text(align="left", dx=5, **_label)
            .encode(x=alt.X("x1:Q", **_px), y=alt.Y("mid:Q", **_px), text="text:N"),
        ]

        # No `.configure_view()` here: this chart gets concatenated with the
        # other three in `explorer_layout`, and Vega-Lite only allows "config"
        # properties on the single top-level spec of a composed chart.
        return alt.layer(*layers).properties(width=width, height=height)

    return (sankey_chart,)


@app.cell(hide_code=True)
def sankey_build(
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
    _tot = pnl.drop(columns="name").sum()
    _revenue = _tot["Revenue"]

    def _eur(v):
        return f"€{v / 1e6:.1f}M" if abs(v) >= 1e6 else f"€{v / 1e3:.0f}k"

    def _pct(v):
        return f" ({v / _revenue:.0%})" if _revenue else ""

    _SPLIT = ["Operating costs", "Depreciation", "Interest", "Tax", "Net profit"]
    _OPEX = ["O&M contract", "Grid fees", "Land lease", "Insurance", "Asset management", "Corrective maintenance"]
    _nodes, _links = [], []
    _plants = pnl[pnl["Revenue"] > 0].sort_values("Revenue", ascending=False)
    for i, r in enumerate(_plants.itertuples()):
        short = r.name.removesuffix(" Solar Farm")
        _nodes.append({"id": r.name, "label": short, "text": short, "column": 0, "value": r.Revenue,
                       "order": i, "color_key": r.name, "name": r.name})
        _links.append({"source": r.name, "target": "Revenue", "value": r.Revenue, "color_key": r.name, "name": r.name})
    _nodes.append({"id": "Revenue", "label": "Revenue", "text": f"Revenue\n{_eur(_revenue)}", "column": 1,
                   "value": _revenue, "order": 0, "color_key": "Revenue"})
    for i, cat in enumerate(_SPLIT):
        key = "Profit" if cat == "Net profit" else "Cost"
        _nodes.append({"id": cat, "label": cat, "text": f"{cat} {_eur(_tot[cat])}{_pct(_tot[cat])}",
                       "column": 2, "value": max(_tot[cat], 0), "order": i, "color_key": key})
        _links.append({"source": "Revenue", "target": cat, "value": max(_tot[cat], 0), "color_key": key})
    for i, cat in enumerate(_OPEX):
        label = "Corrective maint." if cat == "Corrective maintenance" else cat
        _nodes.append({"id": cat, "label": label, "text": f"{label} {_eur(_tot[cat])}", "column": 3,
                       "value": _tot[cat], "order": i, "color_key": "Cost"})
        _links.append({"source": "Operating costs", "target": cat, "value": _tot[cat], "color_key": "Cost"})

    # Plants keep their own colors; money out is neutral gray, profit mint.
    _plant_colors = plant_scale(dim_plants["name"])
    _keys = list(_plant_colors.domain) + ["Revenue", "Cost", "Profit"]
    _range = list(_plant_colors.range) + [nf.BLUE, NF_MUTED, nf.MINT]

    _w, _h = plot_size()
    sankey_chart_out = sankey_chart(
        pd.DataFrame(_nodes),
        pd.DataFrame(_links),
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
    billing_f,
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

    # Month labels say when a month is only partly covered by the period
    # ("Jul 23–31"), so a short bar reads as fewer days, not a bad month.
    _days = billing_f.groupby(billing_f["billing_date"].dt.strftime("%Y-%m"))["billing_date"].agg(["min", "max"])
    def _month_label(m):
        lo, hi = _days.loc[m, "min"], _days.loc[m, "max"]
        if lo.day == 1 and hi.day == hi.days_in_month:
            return lo.strftime("%b")  # the Period timeline shows the year
        return f"{lo.strftime('%b')} {lo.day}–{hi.day}"
    _months = sorted(_long["month"].unique())
    _long["month_label"] = _long["month"].map({m: _month_label(m) for m in _months})
    _month_order = [_month_label(m) for m in _months]

    _Y_AXIS = 44
    _chrome = {"left": _Y_AXIS + 4, "bottom": 56}
    _w, _h = plot_size(**_chrome)
    _ON_TOP = 1  # axes above the panel card - see `line_chart`
    _euro = "'€' + format(datum.{}, '.2~s')"

    _totals = (
        alt.Chart(_long)
        .transform_filter(plant_sel)
        .transform_aggregate(amount="sum(amount)", groupby=["month_label", "measure"])
        .transform_calculate(label=_euro.format("amount"))
    )
    _x = alt.X(
        "month_label:N",
        sort=_month_order,
        title=None,
        scale=alt.Scale(paddingInner=0.3, paddingOuter=0.15),
        axis=alt.Axis(labelAngle=0, labelColor=NF_FG, labelFontSize=FONT_SM, zindex=_ON_TOP),
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
            alt.Tooltip("month_label:N", title="Month"),
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

    pnl_chart = alt.layer(_bars, _values, _scope).properties(
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
    return


if __name__ == "__main__":
    app.run()
