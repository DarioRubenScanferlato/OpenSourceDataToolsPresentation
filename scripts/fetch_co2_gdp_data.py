"""Fetch CO2 emissions and GDP data from Our World in Data and save it locally.

Source: https://github.com/owid/co2-data (owid-co2-data.csv), OWID's maintained
country-year dataset combining CO2/emissions metrics with GDP and population.
"""

from pathlib import Path

import pandas as pd
import requests

SOURCE_URL = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"
SECTOR_SOURCE_URL = "https://ourworldindata.org/grapher/ghg-emissions-by-sector.csv"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

RAW_FILE = DATA_DIR / "owid_co2_gdp_raw.csv"
CO2_FILE = DATA_DIR / "co2_emissions.csv"
GDP_FILE = DATA_DIR / "gdp.csv"
SECTOR_FILE = DATA_DIR / "ghg_emissions_by_sector.csv"

CO2_COLUMNS = [
    "country",
    "year",
    "iso_code",
    "population",
    "co2",
    "co2_per_capita",
    "co2_growth_abs",
    "co2_growth_prct",
    "cumulative_co2",
    "share_global_co2",
]

GDP_COLUMNS = [
    "country",
    "year",
    "iso_code",
    "population",
    "gdp",
]


def fetch_raw_data() -> pd.DataFrame:
    response = requests.get(SOURCE_URL, timeout=60)
    response.raise_for_status()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    RAW_FILE.write_bytes(response.content)
    print(f"Saved raw OWID dataset to {RAW_FILE}")

    return pd.read_csv(RAW_FILE)


def save_co2_extract(df: pd.DataFrame) -> None:
    co2_df = df[CO2_COLUMNS].dropna(subset=["co2"])
    co2_df.to_csv(CO2_FILE, index=False)
    print(f"Saved CO2 emissions extract to {CO2_FILE} ({len(co2_df)} rows)")


def save_gdp_extract(df: pd.DataFrame) -> None:
    gdp_df = df[GDP_COLUMNS].dropna(subset=["gdp"]).copy()
    gdp_df["gdp_per_capita"] = gdp_df["gdp"] / gdp_df["population"]
    gdp_df.to_csv(GDP_FILE, index=False)
    print(f"Saved GDP extract to {GDP_FILE} ({len(gdp_df)} rows)")


def fetch_sector_data() -> None:
    """Greenhouse gas emissions by sector (Climate Watch, via OWID grapher).

    Used for the source -> sector sankey breakdown; covers all GHGs (not CO2
    alone), since no public CO2-only source/sector crosswalk is available.
    """
    response = requests.get(SECTOR_SOURCE_URL, timeout=60)
    response.raise_for_status()
    SECTOR_FILE.write_bytes(response.content)
    print(f"Saved GHG-by-sector dataset to {SECTOR_FILE}")


def main() -> None:
    df = fetch_raw_data()
    save_co2_extract(df)
    save_gdp_extract(df)
    fetch_sector_data()


if __name__ == "__main__":
    main()
