import marimo

__generated_with = "0.24.0"
app = marimo.App(
    width="full",
    layout_file="layouts/solar_dashboard.grid.json",
    css_file="nf-dashboard.css",
)


@app.cell(hide_code=True)
def imports():
    import itertools
    import math
    import warnings
    from pathlib import Path

    import altair as alt
    import marimo as mo
    import pandas as pd
    from vega_datasets import data as vega_data

    from template import theme as nf

    return Path, alt, itertools, math, mo, nf, pd, vega_data, warnings


@app.cell(hide_code=True)
def branding(alt, itertools, nf):
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

    #: Six solid, distinguishable marks that read clearly against the navy
    #: background (this is theme.py's own ACCENTS ramp).
    NF_CATEGORICAL = list(nf.ACCENTS)

    #: Dim -> bright brand ramp for quantitative (sequential) scales on a dark
    #: ground: a near-invisible hairline tone rising through blue to mint.
    NF_SEQUENTIAL = [NF_RULE, nf.BLUE, nf.MINT]

    #: Card accent colors, cycled across the four stat cards.
    CARD_ACCENTS = [nf.MINT, nf.BLUE, nf.PURPLE, nf.LAVENDER]


    def plant_scale(plant_names: list[str]) -> alt.Scale:
        """A per-plant color scale, cycling the brand accents (there are more
        plants than brand accent colors)."""
        colors = list(itertools.islice(itertools.cycle(NF_CATEGORICAL), len(plant_names)))
        return alt.Scale(domain=plant_names, range=colors)


    @alt.theme.register("nearform-solar", enable=True)
    def nearform_theme() -> alt.theme.ThemeConfig:
        return {
            "config": {
                "background": NF_BG,
                "font": nf.SANS,
                "title": {"color": NF_FG, "fontSize": 15, "fontWeight": 600, "anchor": "middle"},
                "axis": {
                    "labelColor": NF_MUTED,
                    "titleColor": NF_FG,
                    "gridColor": NF_RULE,
                    "domainColor": NF_RULE,
                    "tickColor": NF_RULE,
                },
                "legend": {"labelColor": NF_FG, "titleColor": NF_FG},
                "view": {"stroke": "transparent"},
                "range": {
                    "category": NF_CATEGORICAL,
                    "ramp": NF_SEQUENTIAL,
                    "heatmap": NF_SEQUENTIAL,
                },
            }
        }

    return CARD_ACCENTS, NF_BG, NF_FG, NF_MUTED, NF_PANEL, NF_RULE, plant_scale


@app.cell(hide_code=True)
def grid_layout(NF_FG, NF_PANEL, NF_RULE, alt):
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
    #: Sized so the whole dashboard fits one slide in the deck without
    #: scrolling (filters + stat cards + two rows of panels).
    PANEL_H = 375
    PANEL_PAD = 14
    PANEL_TITLE_H = 28  # title strip across the top of each panel

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
        in a rounded card with its title top-left, Power BI style.

        The card and title are just two extra layers - a `mark_rect` and a
        `mark_text` positioned in pixels *around* the plot area, past its
        axes - rather than HTML around the chart: all four charts have to
        stay one compiled spec for the shared click selection to sync
        (see `explorer_layout`), so there's no per-chart DOM node to style.
        """
        w, h = chart.width, chart.height
        x0, y0 = -(PANEL_PAD + left), -(PANEL_PAD + PANEL_TITLE_H)
        one_row = alt.InlineData(values=[{}])
        card = alt.Chart(one_row).mark_rect(
            fill=NF_PANEL, stroke=NF_RULE, cornerRadius=10
        ).encode(
            x=alt.value(x0),
            x2=alt.value(w + PANEL_PAD + right),
            y=alt.value(y0),
            y2=alt.value(h + PANEL_PAD + bottom),
        )
        title = alt.Chart(one_row).mark_text(
            align="left", baseline="top", color=NF_FG, fontSize=14, fontWeight=600
        ).encode(
            x=alt.value(x0 + PANEL_PAD),
            y=alt.value(y0 + PANEL_PAD - 2),
            text=alt.value(chart.title),
        )
        body = chart.copy()
        body.title = body.width = body.height = alt.Undefined
        return alt.layer(card, title, body).properties(width=w, height=h)

    return DASHBOARD_WIDTH, PANEL_GAP, panel, plot_size


@app.cell(hide_code=True)
def load_data(Path, pd):
    # All four datasets were produced by the SolarDataPlatform project's
    # `solar-data-gen` generator (7 synthetic plants, 60 days of daily
    # billing/alarms/maintenance) and copied into presentation/data/solar/ -
    # see data/solar/README.md for how to regenerate them.
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
    return dim_plants, fact_alarms, fact_billing, fact_maintenance


@app.cell(hide_code=True)
def denormalize(dim_plants, fact_alarms, fact_billing, fact_maintenance):
    # Every fact table only carries `plant_id`; join in the human-readable
    # plant `name` once here so every downstream chart/filter can work with
    # "location" (plant name) directly instead of repeating the join.
    _plant_names = dim_plants[["plant_id", "name", "country_code"]]

    billing = fact_billing.merge(_plant_names, on="plant_id")
    alarms = fact_alarms.merge(_plant_names, on="plant_id")
    maintenance = fact_maintenance.merge(_plant_names, on="plant_id")
    return alarms, billing, maintenance


@app.cell(hide_code=True)
def section_label_helper(mo):
    def eyebrow(text: str) -> "mo.Html":
        """A compact uppercase section label - a full `## heading` costs far
        more vertical space than this dashboard's one-screen budget allows."""
        return mo.Html(
            f'<div style="color:#8f9ab8; font-size:11px; font-weight:600; '
            f'letter-spacing:.06em; text-transform:uppercase; margin-bottom:4px;">'
            f"{text}</div>"
        )

    return (eyebrow,)


@app.cell(hide_code=True)
def filters(NF_FG, billing, dim_plants, eyebrow, mo):
    _min_date = billing["billing_date"].min().date()
    _max_date = billing["billing_date"].max().date()

    location_filter = mo.ui.multiselect(
        options=sorted(dim_plants["name"]),
        value=sorted(dim_plants["name"]),
        label="Location (plant)",
    )
    date_from = mo.ui.date(value=_min_date, start=_min_date, stop=_max_date, label="Date from")
    date_to = mo.ui.date(value=_max_date, start=_min_date, stop=_max_date, label="Date to")

    # marimo's date widget colors its *background* via a token that reads
    # the computed `color-scheme` (this notebook's own page is `body.light.
    # light-theme`, so left alone it's white) - `color-scheme: dark` here
    # fixes that the same way a custom property would, crossing the shadow
    # boundary as a normal inherited CSS property, no `:host-context` class
    # selector needed for it. But the widget's *text* just inherits `color`
    # from its ancestors like any other element - with only `color-scheme`
    # set, that inheritance still reaches past this wrapper to the page's
    # own (dark-on-light) body text color, so the background went dark but
    # the text didn't, which is just as unreadable as the original white-on-
    # white (dark-on-dark instead of white-on-white). Set `color` here too
    # so both the property `light-dark()` reads and the one plain
    # inheritance carries are covered (nf-dashboard.css deliberately leaves
    # marimo's own design tokens alone otherwise - see that file's docstring
    # for why).
    _widgets = mo.as_html(
        mo.hstack([location_filter, date_from, date_to], justify="start", gap=2)
    ).text
    mo.vstack(
        [
            eyebrow("Filters"),
            mo.Html(
                f'<div class="dark" style="color-scheme:dark; color:{NF_FG};">'
                f"{_widgets}</div>"
            ),
        ],
        gap=0,
    )
    return date_from, date_to, location_filter


@app.cell(hide_code=True)
def apply_filters(
    alarms,
    billing,
    date_from,
    date_to,
    location_filter,
    maintenance,
):
    # The single filtered view every card and chart below reads from - a
    # plant/date scope, distinct from the click-based cross-filter selection
    # (`plant_sel`, defined further down) that only *highlights* within it.
    _locations = location_filter.value
    _start, _end = date_from.value, date_to.value

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
    return alarms_f, billing_f, maintenance_f


@app.cell(hide_code=True)
def stat_card_helper(NF_FG, NF_MUTED, NF_PANEL, NF_RULE, mo):
    def stat_card(value: str, label: str, accent: str) -> str:
        """A single brand-styled stat tile: a big accent-colored number over a
        muted label, in a bordered navy card - hand-rolled to match
        nf-dashboard.css's literal-color style rather than marimo's shared
        design tokens (see that file's docstring for why). Padding/font sizes
        are kept small so the whole dashboard fits a 14" laptop screen."""
        return f"""
        <div style="
            background:{NF_PANEL}; border:1px solid {NF_RULE}; border-radius:10px;
            padding:6px 10px; min-width:0;
        ">
          <div style="color:{accent}; font-size:17px; font-weight:800; line-height:1.1; overflow-wrap:anywhere;">
            {value}
          </div>
          <div style="color:{NF_MUTED}; font-size:10px; margin-top:1px;">
            {label}
          </div>
        </div>
        """


    def stat_row(cards: list[str]) -> "mo.Html":
        # A 4-column grid, one card per column, authored at `DASHBOARD_WIDTH`
        # and scaled to the page's actual width the same way the chart is
        # (nf-dashboard.css's `.react-grid-item:has(.nf-stat-cards)` rule) -
        # rather than `display:flex` filling whatever width the page
        # happens to give this block (under `width="full"`, close to the
        # full viewport), which left a wide empty gap between the cards and
        # the (fixed-size, chrome-and-all) chart below it. `nf-stat-cards`
        # is just an anchor for that CSS rule's `:has()` to find this cell's
        # grid item by - the scaling itself happens there, not here, for
        # the same reason the chart's own scaling lives in that CSS file
        # rather than in a cell: this cell's own output sits *inside* that
        # grid item's own padding, so a container-type/zoom pair declared
        # from here can only ever fill the padded content area, not the
        # full cell (which is what actually left it narrower than the
        # chart next to it).
        return mo.Html(
            f'<div class="nf-stat-cards" style="display:grid; '
            f'grid-template-columns:repeat(4, 1fr); gap:10px; color:{NF_FG};">'
            f'{"".join(cards)}</div>'
        )

    return stat_card, stat_row


@app.cell(hide_code=True)
def cards(
    CARD_ACCENTS,
    alarms_f,
    billing_f,
    eyebrow,
    maintenance_f,
    mo,
    stat_card,
    stat_row,
):
    _total_energy_gwh = billing_f["energy_generated_kwh"].sum() / 1e6
    _total_revenue = billing_f["revenue_eur"].sum()
    _total_incidents = len(alarms_f)
    _total_cost = maintenance_f["cost_eur"].sum()

    mo.vstack(
        [
            eyebrow("Fleet summary"),
            stat_row(
                [
                    stat_card(
                        f"{_total_energy_gwh:,.1f} GWh",
                        "Total energy production",
                        CARD_ACCENTS[0],
                    ),
                    stat_card(f"€{_total_revenue:,.0f}", "Total revenue", CARD_ACCENTS[1]),
                    stat_card(f"{_total_incidents:,}", "Total incidents", CARD_ACCENTS[2]),
                    stat_card(
                        f"€{_total_cost:,.0f}", "Total maintenance cost", CARD_ACCENTS[3]
                    ),
                ]
            ),
        ],
        gap=0,
    )
    return


@app.cell(hide_code=True)
def crossfilter_heading(eyebrow):
    eyebrow("Linked explorer — map, production, energy allocation & maintenance cost")
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
def map_chart(
    alt,
    dim_plants,
    location_filter,
    math,
    panel,
    plant_scale,
    plant_sel,
    plot_size,
    vega_data,
):
    # A single combined chart (this cell, `line_chart`, `sankey_chart_out` and
    # `bar_chart` below) is assembled once in `explorer_layout` - Vega-Lite
    # only synchronizes a selection param live across sub-views when they are
    # all part of the *same* compiled spec, so the shared `plant_sel` click
    # selection has to be added to each of these four unit charts here, but
    # they must not be individually wrapped/displayed on their own.
    _plants_in_scope = dim_plants[dim_plants["name"].isin(location_filter.value)].copy()
    _world = alt.topo_feature(vega_data.world_110m.url, "countries")
    _w, _h = plot_size()  # no axes or legend - the map fills its panel

    # Vega's automatic projection-fitting frames the *whole world* topojson,
    # which - since none of the plants are anywhere near the Pacific - left
    # a lot of empty ocean bunched up on the left specifically, rather than
    # cropped away. `center`/`rotate` alone can't fix this: auto-fit always
    # re-centers the *whole world's* bounding box regardless of rotation,
    # so the result looks identical no matter where you recenter it.
    #
    # Fixing it means computing `scale`/`translate` by hand from D3's own
    # naturalEarth1 formula (the reference implementation; this deck's other
    # projections all fit the whole world so didn't need this) - projecting
    # every plant, then choosing a scale/translate that frames *just* that
    # bounding box (all plants, not only the currently filtered ones, so
    # the map doesn't rezoom every time the location filter changes).
    def _natural_earth1_xy(lon_deg, lat_deg):
        lam, phi = math.radians(lon_deg), math.radians(lat_deg)
        phi2 = phi * phi
        phi4 = phi2 * phi2
        x = lam * (
            0.8707
            + phi2 * (-0.131979 + phi4 * (-0.013791 + phi4 * (0.003971 * phi2 - 0.001529 * phi4)))
        )
        y = phi * (
            1.007226 + phi2 * (0.015085 + phi4 * (-0.044475 + 0.028874 * phi2 - 0.005916 * phi4))
        )
        return x, y

    _xy = [_natural_earth1_xy(lon, lat) for lon, lat in zip(dim_plants["longitude"], dim_plants["latitude"])]
    _xs, _ys = [p[0] for p in _xy], [p[1] for p in _xy]
    _pad = 1.15  # extra room around the data so points don't sit flush on an edge
    _span_x, _span_y = (max(_xs) - min(_xs)) * _pad, (max(_ys) - min(_ys)) * _pad
    _map_scale = min(_w / _span_x, _h / _span_y)
    _cx, _cy = (max(_xs) + min(_xs)) / 2, (max(_ys) + min(_ys)) / 2
    # D3/Vega's own projection pipeline negates y internally (so that north -
    # positive latitude, positive raw y - ends up at the *smaller* screen y,
    # i.e. the top): the actual on-screen y is `translate[1] - scale * y`, not
    # `+`. Solving `_h/2 == translate[1] - scale*cy` for the center
    # therefore needs a `+` here, even though the x version above is a `-`.
    # Getting this backwards doesn't show up at a loose pad - the resulting
    # vertical offset error is small enough that points stay on-canvas by
    # luck - but it silently pushes points off the top of the frame once
    # `scale` grows for a tighter pad, which is exactly the bug that made 5
    # of these 7 plants vanish from the map when `_pad` was tightened.
    _map_translate = [_w / 2 - _map_scale * _cx, _h / 2 + _map_scale * _cy]

    _basemap = (
        alt.Chart(_world)
        # Land one step lighter than the panel it sits on (the panel itself
        # took over this basemap's old fill), clipped to the plot area so
        # the countries cropped out by the tight framing don't spill past
        # the panel's edges.
        .mark_geoshape(fill="#16225a", stroke="#2a3868", strokeWidth=0.4, clip=True)
    )

    _points = (
        alt.Chart(_plants_in_scope)
        .mark_circle(stroke="#000e38", strokeWidth=0.6)
        .encode(
            longitude="longitude:Q",
            latitude="latitude:Q",
            size=alt.Size(
                "capacity_mw:Q",
                scale=alt.Scale(range=[80, 900]),
                # This fleet is spread across the whole globe, so at this
                # map's tight framing there's no corner a legend can sit in
                # that's guaranteed clear of every plant point - it always
                # ends up overlapping *something*. Simplest fix: no legend;
                # tooltips already carry each plant's exact capacity.
                legend=None,
            ),
            # No color legend: with 7 plants sharing a 6-color ramp, a legend
            # doesn't add much and clutters the row - tooltips and the shared
            # click cross-filter already identify a plant by name.
            color=alt.Color(
                "name:N", scale=plant_scale(sorted(dim_plants["name"])), legend=None
            ),
            opacity=alt.condition(plant_sel, alt.value(0.95), alt.value(0.25)),
            tooltip=[
                alt.Tooltip("name:N", title="Plant"),
                alt.Tooltip("country_code:N", title="Country"),
                alt.Tooltip("capacity_mw:Q", title="Capacity (MW)", format=",.1f"),
                alt.Tooltip("status:N", title="Status"),
            ],
        )
        .add_params(plant_sel)
    )

    map_chart = (
        (_basemap + _points)
        .project("naturalEarth1", scale=_map_scale, translate=_map_translate)
        .properties(width=_w, height=_h, title="Plant locations")
    )
    map_panel = panel(map_chart)
    return (map_panel,)


@app.cell(hide_code=True)
def line_chart(alt, billing_f, panel, plant_scale, plant_sel, plot_size):
    _daily = (
        billing_f.groupby(["name", "billing_date"], as_index=False)["energy_generated_kwh"]
        .sum()
    )
    # y-axis: fixed-width tick labels ("2.2M" via `~s`) plus its title;
    # x-axis: dates only - "Date" as a title would just restate the ticks.
    _Y_AXIS = 40
    _chrome = {"left": _Y_AXIS + 22, "bottom": 22}
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
            x=alt.X("billing_date:T", title=None, axis=alt.Axis(format="%b %d", zindex=_ON_TOP)),
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
                "name:N", scale=plant_scale(sorted(_daily["name"].unique())), legend=None
            ),
            opacity=alt.condition(plant_sel, alt.value(0.85), alt.value(0.15)),
            tooltip=[
                alt.Tooltip("name:N", title="Plant"),
                alt.Tooltip("billing_date:T", title="Date"),
                alt.Tooltip("energy_generated_kwh:Q", title="kWh", format=",.0f"),
            ],
        )
        .properties(width=_w, height=_h, title="Daily energy production by plant (stacked)")
        .add_params(plant_sel)
    )
    line_panel = panel(line_chart, **_chrome)
    return line_chart, line_panel


@app.cell(hide_code=True)
def sankey_helper(NF_FG, alt, pd):
    def sankey_chart(
        nodes_df: pd.DataFrame,
        links_df: pd.DataFrame,
        *,
        width: int = 760,
        height: int = 440,
        node_width: int = 16,
        gap: int = 6,
        ribbon_steps: int = 24,
        color_field: str = "color",
        color_scale: alt.Scale | None = None,
        node_color: str = NF_FG,
        selection: alt.Parameter | None = None,
        label_margin: int = 0,
    ) -> alt.LayerChart:
        """Hand-rolled two-column sankey (source -> target) built from mark_area
        ribbons - copied from co2_gdp_dashboard.py's sankey_helper and extended
        with an optional shared click `selection` so plant nodes/ribbons can
        take part in this dashboard's cross-filter.

        nodes_df: id, label, column (0=left, 1=right), value, order[, name]
        links_df: source (id), target (id), value, color (grouping field)[, name]

        `label_margin` reserves that many px on each side for the node
        labels, inset *within* the declared `width` rather than the default
        0 (the original co2_gdp_dashboard.py behavior, labels drawn past the
        node edge via a negative/positive `dx` - fine on its own, but this
        chart is composed with three others in a grid elsewhere, and a
        Vega-Lite grid that has to keep multiple views aligned can end up
        clipping content that overflows a view's declared bounds like that).
        """
        color_scale = color_scale if color_scale is not None else alt.Scale()

        layout: dict[str, dict] = {}
        for col, grp in nodes_df.groupby("column"):
            grp = grp.sort_values("order") if "order" in grp else grp
            total = grp["value"].sum()
            total_gap = gap * max(len(grp) - 1, 0)
            available = height - total_gap
            y = 0.0
            for _, row in grp.iterrows():
                h = (row["value"] / total) * available if total > 0 else 0
                layout[row["id"]] = {
                    "y0": y, "y1": y + h, "column": col,
                    "value": row["value"], "label": row["label"],
                    "name": row["name"] if "name" in row else None,
                }
                y += h + gap

        out_cursor = {nid: layout[nid]["y0"] for nid in layout}
        in_cursor = {nid: layout[nid]["y0"] for nid in layout}

        node_x = {
            0: (label_margin, label_margin + node_width),
            1: (width - label_margin - node_width, width - label_margin),
        }

        def ease(t: float) -> float:
            return t * t * (3 - 2 * t)

        ribbon_rows = []
        for i, row in links_df.sort_values(["source", "target"]).reset_index(drop=True).iterrows():
            s, t, v = row["source"], row["target"], row["value"]
            s_span = layout[s]["y1"] - layout[s]["y0"]
            t_span = layout[t]["y1"] - layout[t]["y0"]
            s_h = (v / layout[s]["value"]) * s_span if layout[s]["value"] > 0 else 0
            t_h = (v / layout[t]["value"]) * t_span if layout[t]["value"] > 0 else 0
            sy0, sy1 = out_cursor[s], out_cursor[s] + s_h
            ty0, ty1 = in_cursor[t], in_cursor[t] + t_h
            out_cursor[s] += s_h
            in_cursor[t] += t_h

            xl, xr = node_x[0][1], node_x[1][0]
            color = row[color_field] if color_field in row else s
            name = row["name"] if "name" in row else None
            for step in range(ribbon_steps + 1):
                frac = step / ribbon_steps
                e = ease(frac)
                ribbon_rows.append({
                    "link_id": i,
                    "x": xl + frac * (xr - xl),
                    "y_top": sy0 + e * (ty0 - sy0),
                    "y_bot": sy1 + e * (ty1 - sy1),
                    "color": color,
                    "name": name,
                })
        ribbon_df = pd.DataFrame(ribbon_rows)

        node_rows = [
            {
                "id": nid, "x0": node_x[info["column"]][0], "x1": node_x[info["column"]][1],
                "y0": info["y0"], "y1": info["y1"], "label": info["label"],
                "value": info["value"], "column": info["column"], "name": info["name"],
            }
            for nid, info in layout.items()
        ]
        node_df = pd.DataFrame(node_rows)

        _opacity = (
            alt.condition(selection, alt.value(0.65), alt.value(0.15))
            if selection is not None
            else alt.value(0.65)
        )
        ribbons = (
            alt.Chart(ribbon_df)
            .mark_area(interpolate="linear")
            .encode(
                # Pin both scales to the declared pixel box: left to the data
                # extent, x would start at the first node (`label_margin`),
                # not 0, stretching the diagram over the space reserved for
                # its labels and pushing them outside the chart.
                x=alt.X("x:Q", axis=None, scale=alt.Scale(domain=[0, width])),
                y=alt.Y("y_bot:Q", axis=None, scale=alt.Scale(domain=[0, height], reverse=True)),
                y2="y_top:Q",
                detail="link_id:N",
                color=alt.Color("color:N", scale=color_scale, legend=None),
                opacity=_opacity,
            )
        )
        if selection is not None:
            ribbons = ribbons.add_params(selection)

        # Split node rects by column: only column-0 (plant) nodes carry a
        # `name` that matches the shared selection's field, so only they (and
        # the ribbons above) dim when another plant is selected - column-1
        # (allocation-category) nodes stay fully visible regardless.
        _plant_node_opacity = (
            alt.condition(selection, alt.value(1.0), alt.value(0.35))
            if selection is not None
            else alt.value(1.0)
        )
        _node_tooltip = ["label:N", alt.Tooltip("value:Q", format=",.0f", title="Value")]
        plant_node_rects = (
            alt.Chart(node_df[node_df["column"] == 0])
            .mark_rect(color=node_color)
            .encode(
                x="x0:Q", x2="x1:Q",
                y=alt.Y("y0:Q", axis=None, scale=alt.Scale(reverse=True)), y2="y1:Q",
                opacity=_plant_node_opacity,
                tooltip=_node_tooltip,
            )
        )
        if selection is not None:
            plant_node_rects = plant_node_rects.add_params(selection)

        alloc_node_rects = (
            alt.Chart(node_df[node_df["column"] == 1])
            .mark_rect(color=node_color)
            .encode(
                x="x0:Q", x2="x1:Q",
                y=alt.Y("y0:Q", axis=None, scale=alt.Scale(reverse=True)), y2="y1:Q",
                tooltip=_node_tooltip,
            )
        )
        node_rects = plant_node_rects + alloc_node_rects

        left_labels = (
            alt.Chart(node_df[node_df["column"] == 0])
            .mark_text(align="right", dx=-node_width - 4, color=NF_FG)
            .transform_calculate(_mid="(datum.y0 + datum.y1) / 2")
            .encode(x="x0:Q", y=alt.Y("_mid:Q", axis=None, scale=alt.Scale(reverse=True)), text="label:N")
        )
        right_labels = (
            alt.Chart(node_df[node_df["column"] == 1])
            .mark_text(align="left", dx=node_width + 4, color=NF_FG)
            .transform_calculate(_mid="(datum.y0 + datum.y1) / 2")
            .encode(x="x1:Q", y=alt.Y("_mid:Q", axis=None, scale=alt.Scale(reverse=True)), text="label:N")
        )

        # No `.configure_view()` here: this chart gets concatenated with the
        # other three in `explorer_layout`, and Vega-Lite only allows "config"
        # properties on the single top-level spec of a composed chart.
        return (ribbons + node_rects + left_labels + right_labels).properties(
            width=width, height=height
        )

    return (sankey_chart,)


@app.cell(hide_code=True)
def sankey_build(
    billing_f,
    panel,
    pd,
    plant_scale,
    plant_sel,
    plot_size,
    sankey_chart,
):
    # Real accounting, not an assumption: `fact_energy_billing` already
    # splits each day's generated energy into self-consumption, curtailment
    # and exported kWh, so the plant -> allocation flows below are actual
    # sums over the filtered date range, not a modeled/illustrative split.
    _ALLOC_COLS = {
        "Exported": "energy_exported_kwh",
        "Self-consumption": "self_consumption_kwh",
        "Curtailment": "curtailment_kwh",
    }

    _by_plant = billing_f.groupby("name", as_index=False)[list(_ALLOC_COLS.values())].sum()
    _plant_names = sorted(_by_plant["name"])

    _plant_totals = {
        row["name"]: sum(row[c] for c in _ALLOC_COLS.values()) for _, row in _by_plant.iterrows()
    }
    _alloc_totals = {name: _by_plant[col].sum() for name, col in _ALLOC_COLS.items()}
    _total_plant = sum(_plant_totals.values())
    _total_alloc = sum(_alloc_totals.values())

    sankey_nodes = pd.DataFrame(
        [
            {
                "id": f"plant::{name}",
                # Every plant name here ends in "Solar Farm" - dropping that
                # redundant suffix (the tooltip and every other chart still
                # show the full name) roughly halves the longest label,
                # which is what actually lets `label_margin` below stay
                # small instead of eating most of the chart's width.
                "label": name.removesuffix(" Solar Farm"),
                "name": name,
                "column": 0, "value": val, "order": i,
            }
            for i, (name, val) in enumerate(_plant_totals.items())
        ]
        + [
            {
                "id": f"alloc::{name}", "label": name, "name": None,
                "column": 1,
                # rescale allocation-node heights onto the plant total so both
                # columns of the diagram represent the same overall flow
                "value": val * (_total_plant / _total_alloc) if _total_alloc > 0 else 0,
                "order": i,
            }
            for i, (name, val) in enumerate(_alloc_totals.items())
        ]
    )

    sankey_links = pd.DataFrame(
        [
            {
                "source": f"plant::{prow['name']}",
                "target": f"alloc::{aname}",
                "value": prow[acol],
                "color": prow["name"],
                "name": prow["name"],
            }
            for _, prow in _by_plant.iterrows()
            for aname, acol in _ALLOC_COLS.items()
        ]
    )
    sankey_links = sankey_links[sankey_links["value"] > 0]

    # Node labels are inset within the plot (`label_margin`), so no chrome.
    _w, _h = plot_size()
    sankey_chart_out = sankey_chart(
        sankey_nodes,
        sankey_links,
        width=_w,
        height=_h,
        color_scale=plant_scale(_plant_names),
        selection=plant_sel,
        label_margin=110,
    ).properties(title="Energy allocation by plant: generated → exported / self-consumed / curtailed")
    sankey_panel = panel(sankey_chart_out)
    return (sankey_panel,)


@app.cell(hide_code=True)
def bar_chart(alt, maintenance_f, panel, plant_sel, plot_size):
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
    _Y_AXIS = 100
    _chrome = {"left": _Y_AXIS + 4, "bottom": 62}
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
                scale=alt.Scale(scheme="set2"),
                legend=alt.Legend(orient="bottom", direction="horizontal", titleOrient="left", offset=10),
            ),
            opacity=alt.condition(plant_sel, alt.value(1.0), alt.value(0.3)),
            tooltip=[
                alt.Tooltip("name:N", title="Plant"),
                alt.Tooltip("event_type:N", title="Event type"),
                alt.Tooltip("cost_eur:Q", title="Cost (EUR)", format=",.0f"),
            ],
        )
        .properties(width=_w, height=_h, title="Maintenance cost by plant")
        .add_params(plant_sel)
    )
    bar_panel = panel(bar_chart, **_chrome)
    return (bar_panel,)


@app.cell(hide_code=True)
def explorer_layout(
    PANEL_GAP,
    alt,
    bar_panel,
    line_panel,
    map_panel,
    mo,
    sankey_panel,
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
            (map_panel | line_panel).resolve_scale(color="independent"),
            (sankey_panel | bar_panel).resolve_scale(color="independent"),
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
