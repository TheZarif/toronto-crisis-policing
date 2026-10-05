#### Preamble ####
# Purpose: Downloads Mental Health Act apprehensions, neighbourhood boundaries
#   and 2021 neighbourhood census profiles from Open Data Toronto.
# Author: Zarif Masud
# Date: 5 October 2026
# Contact: zarif.masud@gmail.com
# License: MIT
# Pre-requisites: Activated `toronto-crisis-policing` environment; run from repo root.


#### Workspace setup ####
from pathlib import Path

import requests

CKAN_API = "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action"
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


#### Download data ####
for package_id, resource_name, file_name in SOURCES:
    url = resource_url(package_id, resource_name)
    response = requests.get(url, timeout=300)
    response.raise_for_status()

    #### Save data ####
    destination = RAW_DIR / file_name
    destination.write_bytes(response.content)
    print(f"Saved {destination} ({len(response.content) / 1e6:.1f} MB)")
