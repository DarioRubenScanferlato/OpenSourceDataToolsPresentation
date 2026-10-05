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

dbt has no icon on Simple Icons any more (its current mark is a two-colour
gradient, not a flat brand colour) - the "dbt" tool on the Transformation
slide falls back to the initials chip on purpose.

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

`assets.listing()` shows what's actually here; the file names live in the
`_PLATFORMS` dict on the Data Platforms cell if you want to change them.

## A note on other people's trademarks

These are vendor marks. Using them to identify the products in a conference
talk is normal, but take them from each vendor's own brand/press page rather
than a search result, and don't restyle or recolour them.
