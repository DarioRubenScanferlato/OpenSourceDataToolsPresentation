# Logos

Drop logo files here using the names below and they appear automatically — in
the platform tab strip and next to each service on the "Data Platforms" slide.
Anything missing falls back to an initials chip, so the slide always reads as
finished. Nothing here is required.

PNG with transparency (or SVG) works best; they're height-constrained and
`object-fit: contain`, so any aspect ratio is fine. ~200px tall is plenty.

## Already here

Fetched from Simple Icons (official brand colours) and Wikimedia Commons:

    databricks.svg  snowflake.svg  spark.svg    streamlit.svg
    fabric-git.svg  powerbi.svg    iceberg.svg

Fetched from Simple Icons for the OS technologies slides. Current Simple Icons
releases ship the path data without a `fill`, so the hex from each icon's own
`simple-icons.json` entry was added onto the outer `<svg>` by hand (same
convention as the files above):

    postgresql.svg  duckdb.svg   clickhouse.svg  airflow.svg
    prefect.svg     trino.svg    airbyte.svg     superset.svg
    metabase.svg    parquet.svg  nodejs.svg

dbt has no icon on Simple Icons any more. `dbt.svg` is the orange mark from
dbt Labs' own docs repo (github.com/dbt-labs/docs.getdbt.com -
website/static/img/dbt-logo-light.svg, Apache-2.0), with the wordmark paths
dropped so it is square like the others; `dbt-wordmark.svg` is that file
unmodified.

Prefect's Simple Icons mark is near-black (#070E10), so it disappears on the
navy slides - the Prefect slide shows a UI screenshot instead of the logo.

UI screenshots in `../images/` (Apache-2.0, from each project's own docs):

    airflow-grid.png, airflow-graph.png
                 github.com/apache/airflow - airflow-core/docs/img/ui-dark/
    prefect-flow-run.png, prefect-dashboard.png, prefect-flow-runs-list.png
                 github.com/PrefectHQ/prefect - docs/v3/img/ui/
                 (flow-run-details.png, dashboard-oss.png, timeline-flows.png)

The extension doesn't have to match what the slide asks for - `logos/x.png`
finds `logos/x.svg`. Drop in a replacement under either name.

## Still missing (no reliable free source)

Microsoft Fabric, Delta Lake, Unity Catalog, Purview, OneLake and the
Snowflake sub-products have no logo on Simple Icons or Wikimedia Commons.
Take those from each vendor's own brand/press page:

    fabric.png      https://www.microsoft.com/en-us/microsoft-fabric  (brand assets)
    delta-lake.png  https://delta.io
    unity-catalog.png / lakeflow.png / aibi.png   https://www.databricks.com/company/newsroom/media-kit
    purview.png     Microsoft brand assets
    snowsight.png / snowpipe.png / snowpark.png   https://www.snowflake.com/en/media-kit/

## Services

Microsoft Fabric      fabric-data-factory.png, onelake.png, fabric-notebooks.png,
                      dataflows.png, fabric-monitor.png, fabric-git.png,
                      powerbi.png, purview.png
Databricks            lakeflow.png, delta-lake.png, spark.png, aibi.png,
                      unity-catalog.png
Snowflake             snowpipe.png, iceberg.png, dynamic-tables.png,
                      snowpark.png, snowflake-tasks.png, snowflake-cli.png,
                      snowsight.png, streamlit.png, horizon.png

Taken from each project's own sources for the "How the dashboard is built"
diagram (`assets/diagrams/dashboard_pipeline.svg`), unmodified:

    pandas.svg   pandas.pydata.org/static/img/pandas_mark_white.svg
                 (the white variant, for the navy slides)
    altair.svg   github.com/vega/altair - design/altair-logo-light.svg
    marimo.png   github.com/marimo-team/marimo -
                 frontend/public/apple-touch-icon.png (180x180, the app icon;
                 the repo has no SVG of this mark)

For the Data Platforms slide, from each vendor's official source, unmodified:

    fabric.svg  fabric-data-factory.svg  onelake.svg  fabric-notebooks.svg
    dataflows.svg  purview.svg
                 Microsoft's official Fabric icon set (Icons.zip in
                 github.com/microsoft/fabric-samples, docs-samples/), linked
                 from learn.microsoft.com/fabric/fundamentals/icons - Microsoft
                 permits them in slide decks; don't crop, recolour or distort.
                 Files: fabric_48_color, data_factory_48_color,
                 one_lake_48_color, notebook_64_item, dataflow_gen2_64_item,
                 purview_48_color.
    delta-lake.svg     github.com/delta-io/delta - docs/public/favicon.svg
                       (the icon-only mark; the wordmark repeats the label)
    unity-catalog.png  github.com/unitycatalog/unitycatalog -
                       docs/assets/images/uc-logo-mark-reverse.png

Still missing, and left as initials chips on purpose: Databricks' Lakeflow and
AI/BI, Snowflake's Snowpipe, Snowpark, Dynamic Tables, Tasks, CLI, Snowsight
and Horizon, and Fabric's Monitoring hub. Neither vendor publishes those as
individual files (Databricks' are behind brand.databricks.com, Snowflake's
only inside its slide template), and the downloadable "icon packs" online
are third-party.

`assets.listing()` shows what's actually here; the file names live in the
`_PLATFORMS` dict on the Data Platforms cell if you want to change them.

## A note on other people's trademarks

These are vendor marks. Using them to identify the products in a conference
talk is normal, but take them from each vendor's own brand/press page rather
than a search result, and don't restyle or recolour them.

For the data visualization slides. Simple Icons (CC0), with the brand hex
added as `fill`: `plotly.svg`, `d3.svg`, `echarts.svg` (apacheecharts),
`grafana.svg`, and `observable.svg` (white - its #353E58 vanishes on navy).
From each project's own repo, unmodified: `vega.svg` (vega/logos),
`matplotlib.svg` (matplotlib mpl-data/images), `bokeh.svg` (bokeh/pm),
`deckgl.svg` (deck.gl pydeck docs), `perspective.svg` (finos/perspective docs),
`evidence.svg` (evidence-dev/evidence docs favicon). Dash uses `plotly.svg`
(Simple Icons' "Dash" is the cryptocurrency). Lightdash, Redash and Pyodide
fall back to initials chips.
