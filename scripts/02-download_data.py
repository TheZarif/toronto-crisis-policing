#### Preamble ####
# Purpose: Downloads Mental Health Act apprehensions, neighbourhood boundaries
#   and 2021 neighbourhood census profiles from Open Data Toronto, and race-based
#   arrest and strip search records from the Toronto Police Service.
# Author: Zarif Masud
# Date: 5 October 2026
# Contact: zarif.masud@gmail.com
# License: MIT
# Pre-requisites: Activated `toronto-crisis-policing` environment; run from repo root.


#### Workspace setup ####
from pathlib import Path

import polars as pl
import requests

CKAN_API = "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action"
# Open Data Toronto's copy of the race-based arrests data is truncated at 32,000
# of 65,276 rows, so it is pulled from the Toronto Police Service source instead.
ARRESTS_LAYER = (
    "https://services.arcgis.com/S9th0jAJ7bqgIRjw/ArcGIS/rest/services/"
    "RBDC_ARR_TBL_001/FeatureServer/0"
)
RAW_DIR = Path("data/01-raw_data")
RAW_DIR.mkdir(parents=True, exist_ok=True)

# (package id, resource name on the portal, local file name)
SOURCES = [
    (
        "mental-health-apprehensions",
        "mental-health-apprehensions.csv",
        "mental_health_apprehensions.csv",
    ),
    (
        "neighbourhoods",
        "Neighbourhoods - 4326.geojson",
        "neighbourhoods.geojson",
    ),
    (
        "neighbourhood-profiles",
        "neighbourhood-profiles-2021-158-model",
        "neighbourhood_profiles_2021.xlsx",
    ),
]


def resource_url(package_id: str, resource_name: str) -> str:
    """Look up the current download URL of a named resource in a CKAN package."""
    response = requests.get(
        f"{CKAN_API}/package_show", params={"id": package_id}, timeout=60
    )
    response.raise_for_status()
    for resource in response.json()["result"]["resources"]:
        if resource["name"] == resource_name:
            return resource["url"]
    raise LookupError(f"No resource '{resource_name}' in package '{package_id}'")


def query_layer(params: dict) -> dict:
    response = requests.get(f"{ARRESTS_LAYER}/query", params={"f": "json", **params}, timeout=120)
    response.raise_for_status()
    return response.json()


def download_arrests() -> pl.DataFrame:
    """Page through the ArcGIS layer (max 1,000 records per request)."""
    expected = query_layer({"where": "1=1", "returnCountOnly": "true"})["count"]
    records: list[dict] = []
    while len(records) < expected:
        page = query_layer(
            {
                "where": "1=1",
                "outFields": "*",
                "orderByFields": "ObjectId",
                "resultOffset": len(records),
                "resultRecordCount": 1000,
            }
        )
        features = page["features"]
        if not features:
            break
        records.extend(feature["attributes"] for feature in features)
    if len(records) != expected:
        raise RuntimeError(f"Downloaded {len(records)} arrest records, expected {expected}")
    return pl.DataFrame(records, infer_schema_length=None)


#### Download data ####
for package_id, resource_name, file_name in SOURCES:
    url = resource_url(package_id, resource_name)
    response = requests.get(url, timeout=300)
    response.raise_for_status()

    #### Save data ####
    destination = RAW_DIR / file_name
    destination.write_bytes(response.content)
    print(f"Saved {destination} ({len(response.content) / 1e6:.1f} MB)")

arrests = download_arrests()
arrests.write_csv(RAW_DIR / "arrests_strip_searches.csv")
print(f"Saved {RAW_DIR / 'arrests_strip_searches.csv'} ({arrests.height:,} rows)")
