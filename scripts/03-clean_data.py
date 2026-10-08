#### Preamble ####
# Purpose: Cleans raw apprehension, boundary and census data into analysis tables:
#   - apprehensions.parquet: one row per apprehension, 2014 to last complete year
#   - neighbourhoods.parquet: one row per neighbourhood with census covariates
#     and a downtown flag
#   - neighbourhood_year.parquet: apprehension counts (all and Section 17) and
#     rates per neighbourhood-year
#   - neighbourhood_boundaries.geojson: 158-model boundaries keyed by hood_id
#   - arrests.parquet: one row per person arrested (or strip searched), 2020-2021
#   - population_by_race.parquet: 2021 Toronto population in police race categories
# Author: Zarif Masud
# Date: 5 October 2026
# Contact: zarif.masud@gmail.com
# License: MIT
# Pre-requisites: Run 02-download_data.py first; run from repo root.


#### Workspace setup ####
from pathlib import Path

import geopandas as gpd
import polars as pl

RAW_DIR = Path("data/01-raw_data")
OUT_DIR = Path("data/02-analysis_data")
OUT_DIR.mkdir(parents=True, exist_ok=True)

FIRST_YEAR = 2014

# Downtown core, approximating the City's Downtown Plan area: neighbourhoods whose
# centroid lies east of Bathurst Street, west of the Don River and south of Bloor Street.
DOWNTOWN_WEST_LON, DOWNTOWN_EAST_LON, DOWNTOWN_NORTH_LAT = -79.4065, -79.356, 43.6705

APPREHENSION_TYPES = {
    "Mha Sec 17 (Power Of App)": "Section 17: police officer's own authority",
    "Mha Sec 15 (Form 1)": "Section 15: physician's application (Form 1)",
    "Mha Sec 16 (Form 2)": "Section 16: justice of the peace order (Form 2)",
    "Mha Sec 33.4 (Form 47 Cto)": "Section 33.4: community treatment order (Form 47)",
    "Mha Sec 28(1) (Form 9 Elopee)": "Section 28: return of absent patient (Form 9)",
}

TSNS_DESIGNATIONS = {
    "Neighbourhood Improvement Area": "Improvement Area",
    "Neighbourhood Improvement Area (formerly Woburn)": "Improvement Area",
    "Neighbourhood Improvement Area (formerly Downsview-Roding-CFB)": "Improvement Area",
    "Emerging Neighbourhood": "Emerging",
    "Not an NIA or Emerging Neighbourhood": "Neither",
}

# Police changed category labels between 2020 and 2021; map both to one scheme.
OFFENCE_CATEGORIES = {
    "Assault": "Assault & crimes against persons",
    "Assault & Other crimes against persons": "Assault & crimes against persons",
    "Break & Enter": "Break & enter",
    "Break and Enter": "Break & enter",
    "Crimes against Children": "Sexual offences & crimes against children",
    "Sexual Related Crime": "Sexual offences & crimes against children",
    "Sexual Related Crimes & Crimes Against Children": "Sexual offences & crimes against children",
    "Drug Related": "Drug related",
    "FTA/FTC, Compliance Check & Parollee": "Warrants, compliance & administrative",
    "FTA/FTC/Compliance Check/Parollee": "Warrants, compliance & administrative",
    "Warrant": "Warrants, compliance & administrative",
    "Police Category - Administrative": "Warrants, compliance & administrative",
    "Fraud": "Mischief & fraud",
    "Mischief": "Mischief & fraud",
    "Mischief & Fraud": "Mischief & fraud",
    "Harassment & Threatening": "Harassment & threatening",
    "Harassment/Threatening": "Harassment & threatening",
    "Homicide": "Weapons & homicide",
    "Weapons": "Weapons & homicide",
    "Weapons & Homicide": "Weapons & homicide",
    "Impaired": "Vehicle related & impaired",
    "Vehicle Related": "Vehicle related & impaired",
    "Vehicle Related (inc. Impaired)": "Vehicle related & impaired",
    "Robbery & Theft": "Robbery & theft",
    "Robbery/Theft": "Robbery & theft",
    "Mental Health": "Mental health",
    "LLA": "Other",
    "Other Offence": "Other",
    "Other Statute": "Other",
    "Other Statute & Other Incident Type": "Other",
    "Police Category - Incident": "Other",
}

ARREST_AGE_GROUPS = {
    "Aged 17 years and under": "17 and under",
    "Aged 17 years and younger": "17 and under",
    "Aged 18 to 24 years": "18 to 24",
    "Aged 25 to 34 years": "25 to 34",
    "Aged 35 to 44 years": "35 to 44",
    "Aged 45 to 54 years": "45 to 54",
    "Aged 55 to 64 years": "55 to 64",
    "Aged 65 and older": "65 and over",
    "Aged 65 years and older": "65 and over",
}

QUARTERS = {"Jan-Mar": "Q1", "Apr-June": "Q2", "July-Sept": "Q3", "Oct-Dec": "Q4"}

ARREST_ACTIONS = {
    "Actions_at_arrest___Concealed_i": "concealed_items",
    "Actions_at_arrest___Combative__": "combative",
    "Actions_at_arrest___Resisted__d": "resisted",
    "Actions_at_arrest___Mental_inst": "mental_instability",
    "Actions_at_arrest___Assaulted_o": "assaulted_officer",
    "Actions_at_arrest___Cooperative": "cooperative",
}

# Reasons for a strip search; recorded only when one took place.
SEARCH_REASONS = {
    "SearchReason_CauseInjury": "search_reason_injury",
    "SearchReason_AssistEscape": "search_reason_escape",
    "SearchReason_PossessWeapons": "search_reason_weapons",
    "SearchReason_PossessEvidence": "search_reason_evidence",
}


#### Clean apprehensions ####
raw = pl.read_csv(RAW_DIR / "mental_health_apprehensions.csv", infer_schema_length=0)

# The source is refreshed mid-year; keep only complete calendar years.
last_report = raw["REPORT_DATE"].str.to_date("%Y-%m-%d").max()
last_complete_year = last_report.year if (last_report.month, last_report.day) == (12, 31) else last_report.year - 1


def not_recorded_to_null(column: str) -> pl.Expr:
    return pl.when(pl.col(column).is_in(["NSA", "Not Recorded"])).then(None).otherwise(pl.col(column))


apprehensions = (
    raw.select(
        pl.col("EVENT_UNIQUE_ID").alias("event_id"),
        pl.col("OCC_DATE").str.to_date("%Y-%m-%d").alias("occurrence_date"),
        pl.col("REPORT_DATE").str.to_date("%Y-%m-%d").alias("report_date"),
        pl.col("OCC_HOUR").cast(pl.Int8).alias("occurrence_hour"),
        not_recorded_to_null("DIVISION").alias("police_division"),
        pl.col("PREMISES_TYPE").alias("premises_type"),
        pl.col("APPREHENSION_TYPE").replace_strict(APPREHENSION_TYPES).alias("apprehension_type"),
        not_recorded_to_null("SEX").alias("sex"),
        not_recorded_to_null("AGE_COHORT").alias("age_group"),
        not_recorded_to_null("HOOD_158").cast(pl.Int16).alias("hood_id"),
    )
    .with_columns(pl.col("occurrence_date").dt.year().cast(pl.Int16).alias("year"))
    .filter(pl.col("year").is_between(FIRST_YEAR, last_complete_year))
    .sort("occurrence_date", "event_id")
)


#### Clean neighbourhood boundaries ####
boundaries = gpd.read_file(RAW_DIR / "neighbourhoods.geojson")
boundaries = boundaries.assign(
    hood_id=boundaries["AREA_SHORT_CODE"].astype(int),
    neighbourhood=boundaries["AREA_NAME"].str.replace(r"\s*\(\d+\)$", "", regex=True),
)[["hood_id", "neighbourhood", "geometry"]].sort_values("hood_id")

# Centroids in a projected CRS (UTM 17N) to avoid distortion, then back to lon/lat.
centroids = boundaries.to_crs(32617).centroid.to_crs(4326)
downtown = pl.DataFrame(
    {
        "hood_id": boundaries["hood_id"].to_numpy(),
        "downtown": (
            centroids.x.between(DOWNTOWN_WEST_LON, DOWNTOWN_EAST_LON)
            & (centroids.y < DOWNTOWN_NORTH_LAT)
        ).to_numpy(),
    },
    schema={"hood_id": pl.Int16, "downtown": pl.Boolean},
)


#### Clean 2021 census profiles ####
# The profile is wide (one row per census characteristic, one column per
# neighbourhood) and many labels repeat under different parents, so each value
# is located as the first row matching `label` at or after its parent `anchor`.
profile = pl.read_excel(
    RAW_DIR / "neighbourhood_profiles_2021.xlsx",
    sheet_name="hd2021_census_profile",
    has_header=False,
    infer_schema_length=0,
)
labels = profile.get_column(profile.columns[0]).str.strip_chars().to_list()


def profile_row(label: str, anchor: str | None = None) -> list[str]:
    start = labels.index(anchor) if anchor else 0
    row = labels.index(label, start)
    return profile.row(row)[1:]


VISIBLE_MINORITY = "Total - Visible minority for the population in private households - 25% sample data"
INDIGENOUS = "Total - Indigenous identity for the population in private households - 25% sample data"
TENURE = "Total - Private households by tenure - 25% sample data"

census = pl.DataFrame(
    {
        "hood_id": profile_row("Neighbourhood Number"),
        "tsns_designation": profile_row("TSNS 2020 Designation"),
        "population": profile_row("Total - Age groups of the population - 25% sample data"),
        "median_household_income": profile_row("Median total income of household in 2020 ($)"),
        "low_income_pct": profile_row(
            "Prevalence of low income based on the Low-income measure, after tax (LIM-AT) (%)"
        ),
        "_vm_total": profile_row(VISIBLE_MINORITY),
        "_vm": profile_row("Total visible minority population", VISIBLE_MINORITY),
        "_black": profile_row("Black", VISIBLE_MINORITY),
        "_ind_total": profile_row(INDIGENOUS),
        "_ind": profile_row("Indigenous identity", INDIGENOUS),
        "_households": profile_row(TENURE),
        "_renters": profile_row("Renter", TENURE),
    }
)

numeric = [c for c in census.columns if c not in ("tsns_designation",)]
neighbourhoods = (
    census.with_columns(pl.col(numeric).cast(pl.Float64))
    .with_columns(
        pl.col("hood_id").cast(pl.Int16),
        pl.col("population").cast(pl.Int32),
        pl.col("tsns_designation").replace_strict(TSNS_DESIGNATIONS),
        (100 * pl.col("_vm") / pl.col("_vm_total")).alias("visible_minority_pct"),
        (100 * pl.col("_black") / pl.col("_vm_total")).alias("black_pct"),
        (100 * pl.col("_ind") / pl.col("_ind_total")).alias("indigenous_pct"),
        (100 * pl.col("_renters") / pl.col("_households")).alias("renter_pct"),
    )
    .drop(pl.selectors.starts_with("_"))
    .join(
        pl.from_pandas(boundaries[["hood_id", "neighbourhood"]]).cast({"hood_id": pl.Int16}),
        on="hood_id",
        how="full",
        coalesce=True,
        validate="1:1",
    )
    .join(downtown, on="hood_id", how="left", validate="1:1")
    .select("hood_id", "neighbourhood", pl.exclude("hood_id", "neighbourhood"))
    .sort("hood_id")
)


#### Build neighbourhood-year panel ####
# Cross join so neighbourhood-years with no apprehensions appear as zeros.
years = pl.DataFrame({"year": range(FIRST_YEAR, last_complete_year + 1)}, schema={"year": pl.Int16})
counts = (
    apprehensions.drop_nulls("hood_id")
    .group_by("hood_id", "year")
    .agg(
        pl.len().alias("apprehensions"),
        pl.col("apprehension_type").str.starts_with("Section 17").sum().alias("section_17"),
    )
)

neighbourhood_year = (
    neighbourhoods.select("hood_id", "population")
    .join(years, how="cross")
    .join(counts, on=["hood_id", "year"], how="left")
    .with_columns(pl.col("apprehensions", "section_17").fill_null(0).cast(pl.Int32))
    .with_columns((1000 * pl.col("apprehensions") / pl.col("population")).alias("rate_per_1000"))
    .sort("hood_id", "year")
)

neighbourhoods = neighbourhoods.join(
    neighbourhood_year.group_by("hood_id").agg(
        pl.col("apprehensions").sum().alias("total_apprehensions"),
        pl.col("rate_per_1000").mean().alias("mean_annual_rate_per_1000"),
    ),
    on="hood_id",
    how="left",
)


#### Clean arrests and strip searches ####
raw_arrests = pl.read_csv(RAW_DIR / "arrests_strip_searches.csv", infer_schema_length=None)

arrests = (
    raw_arrests.select(
        pl.col("Arrest_Year").cast(pl.Int16).alias("year"),
        pl.col("Arrest_Month").replace_strict(QUARTERS).alias("quarter"),
        pl.col("EventID").alias("event_id"),
        pl.col("ArrestID").alias("arrest_id"),
        pl.col("PersonID").alias("person_id"),
        pl.col("Perceived_Race").alias("perceived_race"),
        pl.col("Sex").replace_strict({"M": "Male", "F": "Female", "U": None}).alias("sex"),
        pl.col("Age_group__at_arrest_").replace_strict(ARREST_AGE_GROUPS, default=None).alias("age_group"),
        pl.when(pl.col("ArrestLocDiv") == "XX")
        .then(None)
        .otherwise(pl.format("D{}", pl.col("ArrestLocDiv")))
        .alias("police_division"),
        pl.col("Occurrence_Category").replace_strict(OFFENCE_CATEGORIES, default=None).alias("offence_category"),
        (pl.col("StripSearch") == 1).alias("strip_searched"),
        # Source documentation: a strip search implies a booking even when not recorded.
        ((pl.col("Booked") == 1) | (pl.col("StripSearch") == 1)).alias("booked"),
        *[(pl.col(source) == 1).alias(name) for source, name in ARREST_ACTIONS.items()],
        *[(pl.col(source) == 1).alias(name) for source, name in SEARCH_REASONS.items()],
        (pl.col("ItemsFound") == 1).alias("items_found"),
        pl.col("Youth_at_arrest__under_18_years").str.starts_with("Youth").alias("youth"),
    )
    .sort("year", "quarter", "event_id", "person_id")
)


#### Toronto population by police race category ####
# City totals are summed from the 158 neighbourhood columns of the 2021 profile.
# Census groups are combined to match the Toronto Police perceived-race categories.
# Indigenous people are not counted as visible minorities by Statistics Canada,
# so "White" is approximated as "not a visible minority" minus Indigenous identity.
def city_total(label: str, anchor: str) -> float:
    return sum(float(value) for value in profile_row(label, anchor) if value not in (None, ""))


census_groups = {
    group: city_total(group, VISIBLE_MINORITY)
    for group in [
        "South Asian", "Chinese", "Black", "Filipino", "Arab", "Latin American",
        "Southeast Asian", "West Asian", "Korean", "Japanese", "Not a visible minority",
    ]
}
indigenous_total = city_total("Indigenous identity", INDIGENOUS)
population_total = city_total(VISIBLE_MINORITY, VISIBLE_MINORITY)

population_by_race = (
    pl.DataFrame(
        {
            "perceived_race": [
                "White", "Black", "East/Southeast Asian", "South Asian",
                "Middle-Eastern", "Latino", "Indigenous",
            ],
            "population": [
                census_groups["Not a visible minority"] - indigenous_total,
                census_groups["Black"],
                census_groups["Chinese"] + census_groups["Filipino"] + census_groups["Southeast Asian"]
                + census_groups["Korean"] + census_groups["Japanese"],
                census_groups["South Asian"],
                census_groups["Arab"] + census_groups["West Asian"],
                census_groups["Latin American"],
                indigenous_total,
            ],
        }
    )
    .with_columns((pl.col("population") / population_total).alias("population_share"))
    .with_columns(pl.col("population").cast(pl.Int32))
)


#### Save data ####
apprehensions.write_parquet(OUT_DIR / "apprehensions.parquet")
neighbourhoods.write_parquet(OUT_DIR / "neighbourhoods.parquet")
neighbourhood_year.write_parquet(OUT_DIR / "neighbourhood_year.parquet")
boundaries.to_file(OUT_DIR / "neighbourhood_boundaries.geojson", driver="GeoJSON")
arrests.write_parquet(OUT_DIR / "arrests.parquet")
population_by_race.write_parquet(OUT_DIR / "population_by_race.parquet")

print(f"Years {FIRST_YEAR}-{last_complete_year}: {apprehensions.height:,} apprehensions")
print(f"{neighbourhoods.height} neighbourhoods; {neighbourhood_year.height:,} neighbourhood-years")
print(f"{arrests.height:,} arrest records, {arrests['year'].min()}-{arrests['year'].max()}")
