import marimo

__generated_with = "0.24.0"
app = marimo.App(
    width="full",
    layout_file="layouts/solar_dashboard.grid.json",
    css_file="nf-dashboard.css",
)


@app.cell
def intro(mo):
    # No page title by design (redundant with the browser tab/app title) -
    # just the interaction hint, kept to one compact row so it costs as
    # little vertical space as possible - see grid_layout's WIDTH_HALF/
    # ROW_HEIGHT and the small `eyebrow()` section labels further down.
    mo.Html(
        '<div style="color:#8f9ab8; font-size:12px;">'
        "Filter below, then <strong>click a plant</strong> on any chart to "
        "highlight it everywhere (double-click to clear)."
        "</div>"
    )
    return


@app.cell(hide_code=True)
def imports():
    import itertools
    from pathlib import Path

    import altair as alt
    import marimo as mo
    import pandas as pd
    from vega_datasets import data as vega_data

    from template import theme as nf

    return Path, alt, itertools, mo, nf, pd, vega_data


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
                "title": {"color": NF_FG, "fontSize": 15, "fontWeight": 600, "anchor": "start"},
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

    return CARD_ACCENTS, NF_BG, NF_FG, NF_MUTED, NF_RULE, plant_scale


@app.cell(hide_code=True)
def grid_layout():
    # A 12-column dashboard grid. The app runs at `width="full"` (no marimo
    # max-width margin, just its own small page gutter), so the *declared*
    # chart width below is tuned to the actual rendered width, which is
    # substantially larger once Vega-Lite adds axis labels/legends on top of
    # it - 924 declared renders to roughly the available column width on a
    # 14"+ screen without forcing horizontal scrolling. Row height has no
    # such ceiling (the page scrolls vertically), so it's sized generously.
    GRID_COLUMNS = 12
    GRID_UNIT = 77  # px per column, at a ~924px design width
    WIDTH_FULL = GRID_UNIT * GRID_COLUMNS  # 924 (12/12)
    WIDTH_HALF = GRID_UNIT * 6  # 462 (6/12)

    #: Shared row height so same-row charts (matched widths summing to 12
    #: columns) line up top and bottom, not just left and right.
    ROW_HEIGHT = 320
    return ROW_HEIGHT, WIDTH_HALF


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
def filters(billing, dim_plants, eyebrow, mo):
    _min_date = billing["billing_date"].min().date()
    _max_date = billing["billing_date"].max().date()

    location_filter = mo.ui.multiselect(
        options=sorted(dim_plants["name"]),
        value=sorted(dim_plants["name"]),
        label="Location (plant)",
    )
    date_from = mo.ui.date(value=_min_date, start=_min_date, stop=_max_date, label="Date from")
    date_to = mo.ui.date(value=_max_date, start=_min_date, stop=_max_date, label="Date to")

    mo.vstack(
        [
            eyebrow("Filters"),
            mo.hstack([location_filter, date_from, date_to], justify="start", gap=2),
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
def stat_card_helper(NF_BG, NF_FG, NF_MUTED, NF_RULE, mo):
    def stat_card(value: str, label: str, accent: str) -> str:
        """A single brand-styled stat tile: a big accent-colored number over a
        muted label, in a bordered navy card - hand-rolled to match
        nf-dashboard.css's literal-color style rather than marimo's shared
        design tokens (see that file's docstring for why). Padding/font sizes
        are kept small so the whole dashboard fits a 14" laptop screen."""
        return f"""
        <div style="
            background:{NF_BG}; border:1px solid {NF_RULE}; border-radius:10px;
            padding:6px 10px; flex:1; min-width:0;
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
        return mo.Html(
            f'<div style="display:flex; gap:10px; color:{NF_FG};">{"".join(cards)}</div>'
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
    NF_FG,
    ROW_HEIGHT,
    WIDTH_HALF,
    alt,
    dim_plants,
    location_filter,
    plant_scale,
    plant_sel,
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

    _basemap = (
        alt.Chart(_world)
        .mark_geoshape(fill="#0a1440", stroke="#1e2a54", strokeWidth=0.4)
    )

    _points = (
        alt.Chart(_plants_in_scope)
        .mark_circle(stroke="#000e38", strokeWidth=0.6)
        .encode(
            longitude="longitude:Q",
            latitude="latitude:Q",
            size=alt.Size(
                "capacity_mw:Q",
                title="Capacity (MW)",
                scale=alt.Scale(range=[80, 900]),
                legend=alt.Legend(
                    # Size-legend swatches default to a black fill, invisible
                    # on the navy background - force them to a light,
                    # high-contrast color instead (independent of the
                    # per-plant point colors).
                    symbolFillColor=NF_FG,
                    symbolStrokeColor=NF_FG,
                    # naturalEarth1 leaves a wide empty gap of open ocean at
                    # the left of this map (none of the plants are in the
                    # Pacific) - a corner orientation renders as an inset
                    # *inside* the plot bounds (unlike "left"/"right", which
                    # reserve extra room outside it), dropping the legend
                    # into that dead space instead of a separate column.
                    orient="top-left",
                    fillColor="transparent",
                ),
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
        .project("naturalEarth1")
        .properties(width=WIDTH_HALF, height=ROW_HEIGHT, title="Plant locations")
    )
    return (map_chart,)


@app.cell(hide_code=True)
def line_chart(ROW_HEIGHT, WIDTH_HALF, alt, billing_f, plant_scale, plant_sel):
    _daily = (
        billing_f.groupby(["name", "billing_date"], as_index=False)["energy_generated_kwh"]
        .sum()
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
            x=alt.X("billing_date:T", title="Date"),
            y=alt.Y(
                "energy_generated_kwh:Q", title="Energy generated (kWh)", stack="zero"
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
        .properties(width=WIDTH_HALF, height=ROW_HEIGHT, title="Daily energy production by plant (stacked)")
        .add_params(plant_sel)
    )
    return (line_chart,)


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
    ) -> alt.LayerChart:
        """Hand-rolled two-column sankey (source -> target) built from mark_area
        ribbons - copied from co2_gdp_dashboard.py's sankey_helper and extended
        with an optional shared click `selection` so plant nodes/ribbons can
        take part in this dashboard's cross-filter.

        nodes_df: id, label, column (0=left, 1=right), value, order[, name]
        links_df: source (id), target (id), value, color (grouping field)[, name]
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

        node_x = {0: (0, node_width), 1: (width - node_width, width)}

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
                x=alt.X("x:Q", axis=None),
                y=alt.Y("y_bot:Q", axis=None, scale=alt.Scale(reverse=True)),
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
    ROW_HEIGHT,
    WIDTH_HALF,
    billing_f,
    pd,
    plant_scale,
    plant_sel,
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
                "id": f"plant::{name}", "label": name, "name": name,
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

    sankey_chart_out = sankey_chart(
        sankey_nodes,
        sankey_links,
        width=WIDTH_HALF,
        height=ROW_HEIGHT,
        color_scale=plant_scale(_plant_names),
        selection=plant_sel,
    ).properties(title="Energy allocation by plant: generated → exported / self-consumed / curtailed")
    return (sankey_chart_out,)


@app.cell(hide_code=True)
def bar_chart(ROW_HEIGHT, WIDTH_HALF, alt, maintenance_f, plant_sel):
    _cost_by_plant_type = (
        maintenance_f.groupby(["name", "event_type"], as_index=False)["cost_eur"].sum()
    )

    bar_chart = (
        alt.Chart(_cost_by_plant_type)
        .mark_bar()
        .encode(
            x=alt.X("cost_eur:Q", title="Maintenance cost (EUR)", stack="zero"),
            y=alt.Y("name:N", title=None, sort="-x"),
            color=alt.Color(
                "event_type:N",
                title="Event type",
                scale=alt.Scale(scheme="set2"),
            ),
            opacity=alt.condition(plant_sel, alt.value(1.0), alt.value(0.3)),
            tooltip=[
                alt.Tooltip("name:N", title="Plant"),
                alt.Tooltip("event_type:N", title="Event type"),
                alt.Tooltip("cost_eur:Q", title="Cost (EUR)", format=",.0f"),
            ],
        )
        .properties(width=WIDTH_HALF, height=ROW_HEIGHT, title="Maintenance cost by plant")
        .add_params(plant_sel)
    )
    return (bar_chart,)


@app.cell(hide_code=True)
def explorer_layout(bar_chart, line_chart, map_chart, mo, sankey_chart_out):
    # Combine all four unit charts into ONE compiled Vega-Lite spec (a 2x2
    # grid via hconcat + vconcat) and wrap that combined spec in a single
    # `mo.ui.altair_chart` - this is what lets the one `plant_sel` selection,
    # added to each chart above, stay in sync across all of them live in the
    # browser: clicking a plant on any chart re-highlights it on the rest.
    # Vega-Lite's default "shared" scale resolution only unifies same-field
    # color scales within *one* concat operator - `sankey_chart_out` colors by
    # plant ("name") while `bar_chart` colors by `event_type`, so that inner
    # hconcat needs its own independent resolve too, not just the outer one.
    # `size="independent"` keeps the map's own Capacity legend anchored next
    # to the map instead of drifting to the right of the whole row (its
    # default position once resolution is "shared", the line chart's side).
    _row1 = (map_chart | line_chart).resolve_scale(color="independent").resolve_legend(
        size="independent"
    )
    _row2 = (sankey_chart_out | bar_chart).resolve_scale(color="independent")
    explorer = (
        (_row1 & _row2)
        .resolve_scale(color="independent")
        .resolve_legend(color="independent")
        .configure_view(strokeWidth=0)
    )

    explorer_view = mo.ui.altair_chart(explorer)
    explorer_view
    return


if __name__ == "__main__":
    app.run()
