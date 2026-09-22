import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium", css_file="nf-dashboard.css")


@app.cell
def intro(mo):
    mo.md(r"""
    # CO2 Emissions & GDP Dashboard

    Explore Our World in Data's country-year CO2/GDP dataset and Climate
    Watch's greenhouse-gas-by-sector dataset: a world map of per-capita
    emissions, a source-to-sector sankey, emissions trends over time, a
    GDP-vs-CO2 "gapminder" view, the top emitters, and the global fuel mix.

    **Sources:** [Our World in Data - CO2 and GHG emissions](https://github.com/owid/co2-data),
    [Climate Watch - GHG emissions by sector](https://ourworldindata.org/grapher/ghg-emissions-by-sector)
    """)
    return


@app.cell(hide_code=True)
def imports():
    import marimo as mo
    import pandas as pd
    import numpy as np
    import altair as alt
    from pathlib import Path
    from vega_datasets import data as vega_data
    import pycountry
    import pycountry_convert as pc
    from template import theme as nf

    return Path, alt, mo, nf, pc, pd, pycountry, vega_data


@app.cell(hide_code=True)
def branding(alt, nf):
    # Nearform brand tokens, imported from the shared presentation/template package
    # (presentation/template/theme.py) so the dashboard and the deck stay in sync.
    _tone = nf.TONES["navy"]
    NF_BG = _tone.bg
    NF_FG = _tone.fg
    NF_MUTED = _tone.muted
    NF_ACCENT = _tone.accent
    NF_RULE = _tone.rule

    #: Six solid, distinguishable marks that read clearly against the navy
    #: background (this is theme.py's own ACCENTS ramp).
    NF_CATEGORICAL = list(nf.ACCENTS)

    #: Dim -> bright brand ramp for quantitative (sequential) scales on a dark
    #: ground: a near-invisible hairline tone rising through blue to mint.
    NF_SEQUENTIAL = [NF_RULE, nf.BLUE, nf.MINT]

    #: Fixed value -> color assignments, shared across every chart that plots
    #: this dimension, so "Coal" or "Africa" is always the same color everywhere.
    SOURCE_COLORS = dict(
        zip(["Coal", "Oil", "Gas", "Cement", "Flaring", "Land-use change"], NF_CATEGORICAL)
    )
    CONTINENT_COLORS = dict(
        zip(
            ["Asia", "Africa", "Europe", "North America", "South America", "Oceania"],
            NF_CATEGORICAL,
        )
    )


    def nf_scale(color_map: dict[str, str]) -> alt.Scale:
        """An Altair color scale with an explicit domain -> brand-color mapping."""
        return alt.Scale(domain=list(color_map), range=list(color_map.values()))


    @alt.theme.register("nearform", enable=True)
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

    return (
        CONTINENT_COLORS,
        NF_CATEGORICAL,
        NF_FG,
        NF_RULE,
        NF_SEQUENTIAL,
        SOURCE_COLORS,
        nf_scale,
    )


@app.cell(hide_code=True)
def grid_layout():
    # A 12-column dashboard grid sized for a 16:9 screen: a chart's `.properties`
    # width should always be one of these (full / two-thirds / half / third of
    # a 1200px-wide, 12-column row) so any combination that sums to 12 columns
    # lines up cleanly - e.g. two half-width charts, or a third + two-thirds.
    GRID_COLUMNS = 12
    GRID_UNIT = 100  # px per column, at a 1200px design width
    WIDTH_FULL = GRID_UNIT * GRID_COLUMNS  # 1200 (12/12)
    WIDTH_TWO_THIRDS = GRID_UNIT * 8  # 800 (8/12)
    WIDTH_HALF = GRID_UNIT * 6  # 600 (6/12)
    WIDTH_THIRD = GRID_UNIT * 4  # 400 (4/12)

    #: Shared row height so same-row charts (matched widths summing to 12
    #: columns) line up top and bottom, not just left and right.
    ROW_HEIGHT = 380
    return ROW_HEIGHT, WIDTH_FULL, WIDTH_HALF, WIDTH_TWO_THIRDS


@app.cell(hide_code=True)
def load_data(Path, pd):
    DATA_DIR = Path(__file__).resolve().parent.parent / "data"

    df_raw = pd.read_csv(DATA_DIR / "owid_co2_gdp_raw.csv")
    df_sector_raw = pd.read_csv(DATA_DIR / "ghg_emissions_by_sector.csv")

    df_countries = df_raw[df_raw["iso_code"].notna()].copy()

    df_raw.shape, df_sector_raw.shape, df_countries.shape
    return df_countries, df_raw, df_sector_raw


@app.cell(hide_code=True)
def continent_mapping(df_countries, pc, pycountry):
    _CONTINENT_NAMES = {
        "NA": "North America",
        "SA": "South America",
        "AS": "Asia",
        "EU": "Europe",
        "AF": "Africa",
        "OC": "Oceania",
        "AN": "Antarctica",
    }


    def iso3_to_continent(iso3: str) -> str | None:
        try:
            alpha2 = pycountry.countries.get(alpha_3=iso3).alpha_2
            code = pc.country_alpha2_to_continent_code(alpha2)
            return _CONTINENT_NAMES.get(code)
        except (AttributeError, KeyError):
            return None


    df_geo = df_countries.copy()
    df_geo["continent"] = df_geo["iso_code"].map(iso3_to_continent)
    _n_missing = df_geo["continent"].isna().sum()
    df_geo = df_geo[df_geo["continent"].notna()].copy()

    f"dropped {_n_missing} rows without a continent mapping, {len(df_geo)} remain"
    return (df_geo,)


@app.cell(hide_code=True)
def explorer_heading(mo):
    mo.md(r"""
    ## Linked Explorer — World Map, Top Emitters & GDP vs CO2

    These three views share one selection: **click a country** in the map,
    the bar chart, or the scatter plot to highlight it in all three at once
    (double-click to clear). All three read the same year.
    """)
    return


@app.cell(hide_code=True)
def explorer_controls(df_geo, mo):
    _explorer_years = sorted(
        df_geo.loc[
            df_geo["co2_per_capita"].notna() & df_geo["gdp"].notna() & df_geo["population"].notna(),
            "year",
        ].unique()
    )
    explorer_year = mo.ui.slider(
        start=int(_explorer_years[0]),
        stop=int(_explorer_years[-1]),
        value=2021 if 2021 in _explorer_years else int(_explorer_years[-1]),
        step=1,
        label="Year",
        full_width=True,
    )
    explorer_top_n = mo.ui.slider(start=5, stop=30, value=15, step=1, label="Top N countries (bar)")
    explorer_metric = mo.ui.radio(
        options={"Total CO2 (Mt)": "co2", "CO2 per capita (t)": "co2_per_capita"},
        value="Total CO2 (Mt)",
        label="Bar chart metric",
    )
    mo.hstack([explorer_year, explorer_top_n, explorer_metric], justify="start", gap=2)
    return explorer_metric, explorer_top_n, explorer_year


@app.cell(hide_code=True)
def explorer_chart(
    CONTINENT_COLORS,
    NF_RULE,
    NF_SEQUENTIAL,
    ROW_HEIGHT,
    WIDTH_FULL,
    alt,
    df_geo,
    explorer_metric,
    explorer_top_n,
    explorer_year,
    mo,
    nf_scale,
    pycountry,
    vega_data,
):
    def _iso3_to_numeric(iso3: str) -> int | None:
        try:
            return int(pycountry.countries.get(alpha_3=iso3).numeric)
        except (AttributeError, TypeError):
            return None


    _year_df = df_geo[df_geo["year"] == explorer_year.value].copy()
    _year_df["gdp_per_capita"] = _year_df["gdp"] / _year_df["population"]

    country_sel = alt.selection_point(
        fields=["country"], on="click", clear="dblclick", empty="all", name="country_sel"
    )

    # --- World map ---
    _map_df = _year_df[_year_df["co2_per_capita"].notna()][
        ["iso_code", "country", "co2_per_capita"]
    ].copy()
    _map_df["id"] = _map_df["iso_code"].map(_iso3_to_numeric)
    _world = alt.topo_feature(vega_data.world_110m.url, "countries")

    _explorer_map = (
        alt.Chart(_world, width=680, height=ROW_HEIGHT, title="CO2 per capita")
        .mark_geoshape(stroke=NF_RULE, strokeWidth=0.3)
        .transform_lookup(
            lookup="id", from_=alt.LookupData(_map_df, "id", ["country", "co2_per_capita"])
        )
        .encode(
            color=alt.Color(
                "co2_per_capita:Q",
                scale=alt.Scale(range=NF_SEQUENTIAL),
                title="t CO2/capita",
                legend=alt.Legend(orient="bottom"),
            ),
            opacity=alt.condition(country_sel, alt.value(1.0), alt.value(0.25)),
            tooltip=[
                alt.Tooltip("country:N", title="Country"),
                alt.Tooltip("co2_per_capita:Q", title="t CO2/capita", format=".2f"),
            ],
        )
        .project("naturalEarth1")
        .add_params(country_sel)
    )

    # --- Top emitters bar chart ---
    _metric_title = [k for k, v in explorer_metric.options.items() if v == explorer_metric.value][0]
    _bar_df = _year_df[_year_df[explorer_metric.value].notna()].nlargest(
        explorer_top_n.value, explorer_metric.value
    )

    _explorer_bar = (
        alt.Chart(_bar_df, width=480, height=ROW_HEIGHT, title=f"Top {explorer_top_n.value} emitters")
        .mark_bar()
        .encode(
            x=alt.X(f"{explorer_metric.value}:Q", title=_metric_title),
            y=alt.Y("country:N", sort="-x", title=None),
            color=alt.condition(
                country_sel,
                alt.Color("continent:N", scale=nf_scale(CONTINENT_COLORS), legend=None),
                alt.value(NF_RULE),
            ),
            opacity=alt.condition(country_sel, alt.value(1.0), alt.value(0.35)),
            tooltip=[
                alt.Tooltip("country:N", title="Country"),
                alt.Tooltip(f"{explorer_metric.value}:Q", title=_metric_title, format=",.2f"),
            ],
        )
        .add_params(country_sel)
    )

    # --- GDP vs CO2 scatter ---
    _gap_df = _year_df[
        _year_df["gdp_per_capita"].notna()
        & _year_df["co2_per_capita"].notna()
        & _year_df["population"].notna()
        & (_year_df["gdp_per_capita"] > 0)
        & (_year_df["co2_per_capita"] > 0)
    ]

    _explorer_scatter = (
        alt.Chart(_gap_df, width=WIDTH_FULL, height=320, title="GDP per capita vs CO2 per capita")
        .mark_circle()
        .encode(
            x=alt.X("gdp_per_capita:Q", title="GDP per capita ($)", scale=alt.Scale(type="log")),
            y=alt.Y("co2_per_capita:Q", title="CO2 per capita (t)", scale=alt.Scale(type="log")),
            size=alt.Size(
                "population:Q", title="Population", scale=alt.Scale(range=[20, 2000]), legend=None
            ),
            color=alt.condition(
                country_sel,
                alt.Color("continent:N", scale=nf_scale(CONTINENT_COLORS), title="Continent"),
                alt.value(NF_RULE),
            ),
            opacity=alt.condition(country_sel, alt.value(0.85), alt.value(0.15)),
            tooltip=[
                alt.Tooltip("country:N", title="Country"),
                alt.Tooltip("gdp_per_capita:Q", title="GDP/capita", format=",.0f"),
                alt.Tooltip("co2_per_capita:Q", title="CO2/capita (t)", format=",.2f"),
                alt.Tooltip("population:Q", title="Population", format=",.0f"),
            ],
        )
        .add_params(country_sel)
    )

    explorer_chart = mo.ui.altair_chart(
        (alt.hconcat(_explorer_map, _explorer_bar) & _explorer_scatter)
        .resolve_scale(color="independent")
        .resolve_legend(color="independent")
    )
    explorer_chart
    return


@app.cell(hide_code=True)
def sankey_heading(mo):
    mo.md(r"""
    ## Sankey — CO2 Source → Emitting Sector

    Left: fossil-fuel & industrial CO2 sources (OWID). Right: emitting
    sectors, all greenhouse gases (Climate Watch, via OWID) rescaled to the
    same total. No public CO2-only source→sector crosswalk exists, so
    flows are an **illustrative proportional allocation** (each source is
    split across sectors using the global average sector mix) — not a
    measured link. Treat this as "what share of emissions plausibly flows
    where", not exact accounting.
    """)
    return


@app.cell(hide_code=True)
def sankey_helper(NF_CATEGORICAL, NF_FG, alt, pd):
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
    ) -> alt.LayerChart:
        """Hand-rolled two-column sankey (source -> target) built from mark_area ribbons.

        nodes_df: id, label, column (0=left, 1=right), value, order
        links_df: source (id), target (id), value, color (grouping field)
        """
        color_scale = color_scale or alt.Scale(range=NF_CATEGORICAL)

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
            for step in range(ribbon_steps + 1):
                frac = step / ribbon_steps
                e = ease(frac)
                ribbon_rows.append({
                    "link_id": i,
                    "x": xl + frac * (xr - xl),
                    "y_top": sy0 + e * (ty0 - sy0),
                    "y_bot": sy1 + e * (ty1 - sy1),
                    "color": color,
                })
        ribbon_df = pd.DataFrame(ribbon_rows)

        node_rows = [
            {
                "id": nid, "x0": node_x[info["column"]][0], "x1": node_x[info["column"]][1],
                "y0": info["y0"], "y1": info["y1"], "label": info["label"],
                "value": info["value"], "column": info["column"],
            }
            for nid, info in layout.items()
        ]
        node_df = pd.DataFrame(node_rows)

        ribbons = (
            alt.Chart(ribbon_df)
            .mark_area(interpolate="linear", opacity=0.65)
            .encode(
                x=alt.X("x:Q", axis=None),
                y=alt.Y("y_bot:Q", axis=None, scale=alt.Scale(reverse=True)),
                y2="y_top:Q",
                detail="link_id:N",
                color=alt.Color("color:N", scale=color_scale, legend=alt.Legend(title="Source")),
            )
        )

        node_rects = (
            alt.Chart(node_df)
            .mark_rect(color=node_color)
            .encode(
                x="x0:Q", x2="x1:Q",
                y=alt.Y("y0:Q", axis=None, scale=alt.Scale(reverse=True)), y2="y1:Q",
                tooltip=["label:N", alt.Tooltip("value:Q", format=",.0f", title="Mt CO2")],
            )
        )

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

        return (
            (ribbons + node_rects + left_labels + right_labels)
            .properties(width=width, height=height)
            .configure_view(strokeWidth=0)
        )

    return (sankey_chart,)


@app.cell(hide_code=True)
def sankey_controls(df_raw, df_sector_raw, mo):
    _sec_years = set(df_sector_raw.loc[df_sector_raw["Entity"] == "World", "Year"])
    _src_years = set(
        df_raw.loc[(df_raw["country"] == "World") & df_raw["coal_co2"].notna(), "year"]
    )
    sankey_years = sorted(_sec_years & _src_years)

    sankey_year = mo.ui.slider(
        start=sankey_years[0],
        stop=sankey_years[-1],
        value=sankey_years[-1],
        step=1,
        label="Year",
        full_width=True,
    )
    sankey_year
    return (sankey_year,)


@app.cell(hide_code=True)
def sankey_build(
    NF_FG,
    ROW_HEIGHT,
    SOURCE_COLORS,
    WIDTH_HALF,
    df_raw,
    df_sector_raw,
    nf_scale,
    pd,
    sankey_chart,
    sankey_year,
):
    _SOURCE_COLS = {
        "Coal": "coal_co2",
        "Oil": "oil_co2",
        "Gas": "gas_co2",
        "Cement": "cement_co2",
        "Flaring": "flaring_co2",
        "Land-use change": "land_use_change_co2",
    }
    _SECTOR_COLS = {
        "Energy": [
            "Electricity and heat", "Manufacturing and construction", "Buildings",
            "Fugitive emissions", "Other fuel combustion", "Aviation and shipping",
        ],
        "Transport": ["Transport"],
        "Industry": ["Industry"],
        "Agriculture": ["Agriculture"],
        "Waste": ["Waste"],
        "Land-use change": ["Land-use change and forestry"],
    }

    _src_row = df_raw[(df_raw["country"] == "World") & (df_raw["year"] == sankey_year.value)].iloc[0]
    _sec_row = df_sector_raw[
        (df_sector_raw["Entity"] == "World") & (df_sector_raw["Year"] == sankey_year.value)
    ].iloc[0]

    _source_vals = {name: float(_src_row[col]) for name, col in _SOURCE_COLS.items()}
    # sector dataset is in tonnes, source dataset in million tonnes (Mt) -> convert to Mt
    _sector_vals = {
        name: sum(_sec_row[c] for c in cols) / 1e6 for name, cols in _SECTOR_COLS.items()
    }

    _total_source = sum(_source_vals.values())
    _total_sector = sum(_sector_vals.values())

    sankey_nodes = pd.DataFrame(
        [
            {"id": f"src::{name}", "label": name, "column": 0, "value": val, "order": i}
            for i, (name, val) in enumerate(_source_vals.items())
        ]
        + [
            {
                "id": f"sec::{name}",
                "label": name,
                "column": 1,
                # rescale sector node heights onto the source total so both
                # columns of the diagram represent the same overall flow
                "value": val * (_total_source / _total_sector),
                "order": i,
            }
            for i, (name, val) in enumerate(_sector_vals.items())
        ]
    )

    sankey_links = pd.DataFrame(
        [
            {
                "source": f"src::{sname}",
                "target": f"sec::{tname}",
                # independence assumption: each source is split across sectors
                # using the global average sector mix (illustrative, not measured)
                "value": sval * (tval / _total_sector),
                "color": sname,
            }
            for sname, sval in _source_vals.items()
            for tname, tval in _sector_vals.items()
        ]
    )
    sankey_links = sankey_links[sankey_links["value"] > 0]

    sankey_chart(
        sankey_nodes,
        sankey_links,
        width=WIDTH_HALF,
        height=ROW_HEIGHT,
        color_scale=nf_scale(SOURCE_COLORS),
        node_color=NF_FG,
    ).properties(
        title=f"Illustrative CO2 source → sector allocation, {sankey_year.value}"
    )
    return


@app.cell(hide_code=True)
def line_heading(mo):
    mo.md("""
    ## CO2 Emissions Over Time
    """)
    return


@app.cell(hide_code=True)
def line_controls(df_raw, mo):
    line_entities = mo.ui.multiselect(
        options=sorted(df_raw["country"].unique()),
        value=["World", "China", "United States", "India", "European Union (27)"],
        label="Countries / regions",
    )
    line_year_range = mo.ui.range_slider(
        start=1850,
        stop=int(df_raw["year"].max()),
        value=(1950, int(df_raw["year"].max())),
        step=1,
        label="Year range",
        full_width=True,
    )
    line_metric = mo.ui.radio(
        options={"Total CO2 (Mt)": "co2", "CO2 per capita (t)": "co2_per_capita"},
        value="Total CO2 (Mt)",
        label="Metric",
    )
    mo.vstack([line_entities, line_year_range, line_metric])
    return line_entities, line_metric, line_year_range


@app.cell(hide_code=True)
def line_chart(
    NF_CATEGORICAL,
    ROW_HEIGHT,
    WIDTH_HALF,
    alt,
    df_raw,
    line_entities,
    line_metric,
    line_year_range,
):
    _line_df = df_raw[
        df_raw["country"].isin(line_entities.value)
        & df_raw["year"].between(*line_year_range.value)
        & df_raw[line_metric.value].notna()
    ]

    _metric_title = [k for k, v in line_metric.options.items() if v == line_metric.value][0]

    line_chart = (
        alt.Chart(_line_df)
        .mark_line(point=False)
        .encode(
            x=alt.X(
                "year:Q",
                title="Year",
                axis=alt.Axis(format="d", tickCount=10, tickMinStep=1, labelAngle=0),
            ),
            y=alt.Y(f"{line_metric.value}:Q", title=_metric_title),
            color=alt.Color(
                "country:N", title="Country / region", scale=alt.Scale(range=NF_CATEGORICAL)
            ),
            tooltip=[
                alt.Tooltip("country:N", title="Country"),
                alt.Tooltip("year:O", title="Year"),
                alt.Tooltip(f"{line_metric.value}:Q", title=_metric_title, format=",.2f"),
            ],
        )
        .properties(width=WIDTH_HALF, height=ROW_HEIGHT, title=f"{_metric_title} over time")
    )
    line_chart
    return


@app.cell(hide_code=True)
def area_heading(mo):
    mo.md("""
    ## Global CO2 Emissions by Source, Over Time
    """)
    return


@app.cell(hide_code=True)
def area_controls(df_raw, mo):
    _world_source_years = df_raw.loc[
        (df_raw["country"] == "World") & df_raw["coal_co2"].notna(), "year"
    ]
    area_year_range = mo.ui.range_slider(
        start=int(_world_source_years.min()),
        stop=int(_world_source_years.max()),
        value=(1900, int(_world_source_years.max())),
        step=1,
        label="Year range",
        full_width=True,
    )
    area_year_range
    return (area_year_range,)


@app.cell(hide_code=True)
def area_chart(
    ROW_HEIGHT,
    SOURCE_COLORS,
    WIDTH_TWO_THIRDS,
    alt,
    area_year_range,
    df_raw,
    nf_scale,
):
    _SOURCE_COLS = {
        "Coal": "coal_co2",
        "Oil": "oil_co2",
        "Gas": "gas_co2",
        "Cement": "cement_co2",
        "Flaring": "flaring_co2",
        "Land-use change": "land_use_change_co2",
    }

    _world_df = df_raw[
        (df_raw["country"] == "World") & df_raw["year"].between(*area_year_range.value)
    ][["year", *_SOURCE_COLS.values()]].rename(columns={v: k for k, v in _SOURCE_COLS.items()})

    _area_long = _world_df.melt(id_vars="year", var_name="source", value_name="co2_mt").dropna()

    area_chart = (
        alt.Chart(_area_long)
        .mark_area()
        .encode(
            x=alt.X(
                "year:Q",
                title="Year",
                axis=alt.Axis(format="d", tickCount=10, tickMinStep=1, labelAngle=0),
            ),
            y=alt.Y("co2_mt:Q", title="CO2 emissions (Mt)", stack="zero"),
            color=alt.Color("source:N", title="Source", scale=nf_scale(SOURCE_COLORS)),
            order=alt.Order("source:N"),
            tooltip=[
                alt.Tooltip("year:O", title="Year"),
                alt.Tooltip("source:N", title="Source"),
                alt.Tooltip("co2_mt:Q", title="Mt CO2", format=",.1f"),
            ],
        )
        .properties(width=WIDTH_TWO_THIRDS, height=ROW_HEIGHT, title="Global CO2 emissions by source")
    )
    area_chart
    return


if __name__ == "__main__":
    app.run()
