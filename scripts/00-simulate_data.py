#### Preamble ####
# Purpose: Simulates the analysis tables produced by 03-clean_data.py so that
#   tests and analysis code can be written before touching real data.
#   Apprehension rates are simulated to rise with renter share and fall with
#   income, and strip searches to be more likely for Black and Indigenous people
#   arrested: the relationships the analysis will test for.
# Author: Zarif Masud
# Date: 5 October 2026
# Contact: zarif.masud@gmail.com
# License: MIT
# Pre-requisites: Activated `toronto-crisis-policing` environment; run from repo root.


#### Workspace setup ####
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import polars as pl

rng = np.random.default_rng(853)
OUT_DIR = Path("data/00-simulated_data")
OUT_DIR.mkdir(parents=True, exist_ok=True)

N_NEIGHBOURHOODS = 158
YEARS = range(2014, 2026)

APPREHENSION_TYPES = [
    "Section 17: police officer's own authority",
    "Section 15: physician's application (Form 1)",
    "Section 16: justice of the peace order (Form 2)",
    "Section 33.4: community treatment order (Form 47)",
    "Section 28: return of absent patient (Form 9)",
]
TYPE_PROBS = [0.80, 0.08, 0.07, 0.04, 0.01]
AGE_GROUPS = ["18 to 24", "25 to 34", "35 to 44", "45 to 54", "55 to 64", "65+"]
PREMISES = ["Apartment", "House", "Outside", "Other", "Commercial", "Transit", "Educational"]
DIVISIONS = [f"D{d}" for d in (11, 12, 13, 14, 22, 23, 31, 32, 33, 41, 42, 43, 51, 52, 53, 54, 55)]

# Arrests: population benchmark (shares sum below 1; the rest have no police category)
RACE_POPULATION = {
    "White": 1_200_000, "Black": 265_000, "East/Southeast Asian": 576_000, "South Asian": 385_000,
    "Middle-Eastern": 111_000, "Latino": 92_000, "Indigenous": 23_000,
}
CITY_POPULATION = 2_761_000
# Arrest shares and strip search probabilities by perceived race.
ARREST_RACE_PROBS = {
    "White": 0.42, "Black": 0.27, "East/Southeast Asian": 0.07, "South Asian": 0.055,
    "Middle-Eastern": 0.05, "Latino": 0.027, "Indigenous": 0.03, "Unknown or Legacy": 0.078,
}
STRIP_PROB = {"Black": 0.15, "Indigenous": 0.16}  # all other groups: 0.11
ARREST_AGE_GROUPS = ["17 and under", "18 to 24", "25 to 34", "35 to 44", "45 to 54", "55 to 64", "65 and over"]
OFFENCES = [
    "Warrants, compliance & administrative", "Assault & crimes against persons", "Robbery & theft",
    "Other", "Vehicle related & impaired", "Mischief & fraud", "Drug related", "Harassment & threatening",
    "Weapons & homicide", "Break & enter", "Sexual offences & crimes against children", "Mental health",
]
ACTIONS = ["concealed_items", "combative", "resisted", "mental_instability", "assaulted_officer", "cooperative"]
ACTION_PROBS = [0.004, 0.044, 0.038, 0.033, 0.006, 0.45]
SEARCH_REASONS = ["search_reason_injury", "search_reason_escape", "search_reason_weapons", "search_reason_evidence"]


#### Simulate neighbourhoods ####
# Neighbourhood numbers in the 158 model are not contiguous (they run to 174).
hood_ids = np.sort(rng.choice(np.arange(1, 175), N_NEIGHBOURHOODS, replace=False))
median_income = rng.lognormal(np.log(85_000), 0.25, N_NEIGHBOURHOODS).round(-2)
renter_pct = np.clip(rng.normal(46, 16, N_NEIGHBOURHOODS), 5, 95)
visible_minority_pct = np.clip(rng.normal(52, 22, N_NEIGHBOURHOODS), 5, 98)

neighbourhoods = pl.DataFrame(
    {
        "hood_id": hood_ids,
        "neighbourhood": [f"Neighbourhood {i}" for i in hood_ids],
        "tsns_designation": rng.choice(
            ["Neither", "Emerging", "Improvement Area"], N_NEIGHBOURHOODS, p=[0.73, 0.06, 0.21]
        ),
        "population": rng.integers(6_000, 34_000, N_NEIGHBOURHOODS),
        "median_household_income": median_income,
        "low_income_pct": np.clip(rng.normal(13, 4.5, N_NEIGHBOURHOODS), 3, 35),
        "visible_minority_pct": visible_minority_pct,
        "black_pct": visible_minority_pct * rng.uniform(0.05, 0.35, N_NEIGHBOURHOODS),
        "indigenous_pct": rng.uniform(0.05, 3, N_NEIGHBOURHOODS),
        "renter_pct": renter_pct,
    },
    schema_overrides={"hood_id": pl.Int16, "population": pl.Int32},
)


#### Simulate neighbourhood-year counts ####
# Log rate per 1,000 residents: baseline ~3.5, higher with renters, lower with income.
log_rate = (
    np.log(3.5)
    + 0.015 * (renter_pct - renter_pct.mean())
    - 0.6 * np.log(median_income / np.median(median_income))
)

panel_rows = []
for i, hood_id in enumerate(hood_ids):
    for year in YEARS:
        trend = 1 + 0.04 * (year - YEARS[0])
        expected = np.exp(log_rate[i]) * trend * neighbourhoods["population"][i] / 1000
        panel_rows.append((hood_id, year, rng.poisson(expected)))

neighbourhood_year = (
    pl.DataFrame(panel_rows, schema={"hood_id": pl.Int16, "year": pl.Int16, "apprehensions": pl.Int32}, orient="row")
    .join(neighbourhoods.select("hood_id", "population"), on="hood_id")
    .select("hood_id", "population", "year", "apprehensions")
    .with_columns((1000 * pl.col("apprehensions") / pl.col("population")).alias("rate_per_1000"))
)

neighbourhoods = neighbourhoods.join(
    neighbourhood_year.group_by("hood_id").agg(
        pl.col("apprehensions").sum().alias("total_apprehensions"),
        pl.col("rate_per_1000").mean().alias("mean_annual_rate_per_1000"),
    ),
    on="hood_id",
).sort("hood_id")


#### Simulate individual apprehensions ####
# One row per apprehension, consistent with the panel counts.
events = neighbourhood_year.select(
    pl.col("hood_id").repeat_by("apprehensions").explode(empty_as_null=False),
    pl.col("year").repeat_by("apprehensions").explode(empty_as_null=False),
)
n = events.height

occurrence_date = [date(int(y), 1, 1) + timedelta(days=int(d)) for y, d in zip(events["year"], rng.integers(0, 365, n))]
report_lag = rng.choice([0, 0, 0, 1, 2], n)

apprehensions = (
    events.with_columns(
        pl.Series("occurrence_date", occurrence_date),
        pl.Series("report_lag", report_lag),
        pl.Series("occurrence_hour", rng.integers(0, 24, n), dtype=pl.Int8),
        pl.Series("police_division", rng.choice(DIVISIONS, n)),
        pl.Series("premises_type", rng.choice(PREMISES, n)),
        pl.Series("apprehension_type", rng.choice(APPREHENSION_TYPES, n, p=TYPE_PROBS)),
        pl.Series("sex", rng.choice(["Male", "Female"], n, p=[0.56, 0.44])),
        pl.Series("age_group", rng.choice(AGE_GROUPS, n)),
    )
    .with_columns(
        (pl.col("occurrence_date") + pl.duration(days=pl.col("report_lag"))).alias("report_date"),
        pl.format("GO-{}", pl.int_range(n, dtype=pl.Int64) + 20_140_000_000).alias("event_id"),
    )
    .select(
        "event_id",
        "occurrence_date",
        "report_date",
        "occurrence_hour",
        "police_division",
        "premises_type",
        "apprehension_type",
        "sex",
        "age_group",
        "hood_id",
        "year",
    )
    .sort("occurrence_date", "event_id")
)


#### Simulate arrests and strip searches ####
N_ARRESTS = 60_000
race = rng.choice(list(ARREST_RACE_PROBS), N_ARRESTS, p=list(ARREST_RACE_PROBS.values()))
strip_searched = rng.random(N_ARRESTS) < np.array([STRIP_PROB.get(r, 0.11) for r in race])


def when_searched(probability: float) -> pl.Series:
    """Boolean recorded only for strip searches; null otherwise."""
    values = rng.random(N_ARRESTS) < probability
    return pl.Series([bool(v) if s else None for v, s in zip(values, strip_searched)], dtype=pl.Boolean)


age_group = rng.choice(ARREST_AGE_GROUPS, N_ARRESTS, p=[0.05, 0.15, 0.32, 0.25, 0.14, 0.07, 0.02])
arrests = pl.DataFrame(
    {
        "year": rng.choice([2020, 2021], N_ARRESTS),
        "quarter": rng.choice(["Q1", "Q2", "Q3", "Q4"], N_ARRESTS),
        "event_id": rng.integers(1_000_000, 1_100_000, N_ARRESTS),
        "arrest_id": rng.permutation(np.arange(6_000_000, 6_000_000 + N_ARRESTS)),
        "person_id": rng.integers(300_000, 340_000, N_ARRESTS),
        "perceived_race": race,
        "sex": rng.choice(["Male", "Female"], N_ARRESTS, p=[0.81, 0.19]),
        "age_group": age_group,
        "police_division": rng.choice(DIVISIONS, N_ARRESTS),
        "offence_category": rng.choice(OFFENCES, N_ARRESTS),
        "strip_searched": strip_searched,
        "booked": strip_searched | (rng.random(N_ARRESTS) < 0.45),
        **{name: rng.random(N_ARRESTS) < p for name, p in zip(ACTIONS, ACTION_PROBS)},
        **{name: when_searched(0.5) for name in SEARCH_REASONS},
        "items_found": when_searched(0.37),
        "youth": age_group == "17 and under",
    },
    schema_overrides={"year": pl.Int16},
).sort("year", "quarter", "event_id", "person_id")

population_by_race = pl.DataFrame(
    {"perceived_race": list(RACE_POPULATION), "population": list(RACE_POPULATION.values())},
    schema_overrides={"population": pl.Int32},
).with_columns((pl.col("population") / CITY_POPULATION).alias("population_share"))


#### Save data ####
apprehensions.write_parquet(OUT_DIR / "apprehensions.parquet")
neighbourhoods.write_parquet(OUT_DIR / "neighbourhoods.parquet")
neighbourhood_year.write_parquet(OUT_DIR / "neighbourhood_year.parquet")
arrests.write_parquet(OUT_DIR / "arrests.parquet")
population_by_race.write_parquet(OUT_DIR / "population_by_race.parquet")

print(f"Simulated {apprehensions.height:,} apprehensions across {N_NEIGHBOURHOODS} neighbourhoods")
print(f"Simulated {arrests.height:,} arrest records")
