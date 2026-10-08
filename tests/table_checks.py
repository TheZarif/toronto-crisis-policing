"""Checks shared by the simulated and analysis datasets.

Subclasses set `data_dir`; the fixtures in conftest.py load tables from it.
"""

from pathlib import Path

import polars as pl

N_NEIGHBOURHOODS = 158
FIRST_YEAR = 2014

APPREHENSION_TYPES = {
    "Section 17: police officer's own authority",
    "Section 15: physician's application (Form 1)",
    "Section 16: justice of the peace order (Form 2)",
    "Section 33.4: community treatment order (Form 47)",
    "Section 28: return of absent patient (Form 9)",
}
SEXES = {"Male", "Female"}
AGE_GROUPS = {"18 to 24", "25 to 34", "35 to 44", "45 to 54", "55 to 64", "65+"}
PREMISES = {"Apartment", "House", "Outside", "Other", "Commercial", "Transit", "Educational"}
TSNS_DESIGNATIONS = {"Improvement Area", "Emerging", "Neither"}
PERCENT_COLUMNS = ["low_income_pct", "visible_minority_pct", "black_pct", "indigenous_pct", "renter_pct"]

APPREHENSIONS_SCHEMA = {
    "event_id": pl.String,
    "occurrence_date": pl.Date,
    "report_date": pl.Date,
    "occurrence_hour": pl.Int8,
    "police_division": pl.String,
    "premises_type": pl.String,
    "apprehension_type": pl.String,
    "sex": pl.String,
    "age_group": pl.String,
    "hood_id": pl.Int16,
    "year": pl.Int16,
}
NEIGHBOURHOODS_SCHEMA = {
    "hood_id": pl.Int16,
    "neighbourhood": pl.String,
    "tsns_designation": pl.String,
    "population": pl.Int32,
    "median_household_income": pl.Float64,
    "low_income_pct": pl.Float64,
    "visible_minority_pct": pl.Float64,
    "black_pct": pl.Float64,
    "indigenous_pct": pl.Float64,
    "renter_pct": pl.Float64,
    "downtown": pl.Boolean,
    "total_apprehensions": pl.Int32,
    "mean_annual_rate_per_1000": pl.Float64,
}
NEIGHBOURHOOD_YEAR_SCHEMA = {
    "hood_id": pl.Int16,
    "population": pl.Int32,
    "year": pl.Int16,
    "apprehensions": pl.Int32,
    "section_17": pl.Int32,
    "rate_per_1000": pl.Float64,
}

PERCEIVED_RACES = {
    "White", "Black", "East/Southeast Asian", "South Asian", "Middle-Eastern", "Latino", "Indigenous",
}
ARREST_AGE_GROUPS = {"17 and under", "18 to 24", "25 to 34", "35 to 44", "45 to 54", "55 to 64", "65 and over"}
OFFENCE_CATEGORIES = {
    "Warrants, compliance & administrative", "Assault & crimes against persons", "Robbery & theft",
    "Other", "Vehicle related & impaired", "Mischief & fraud", "Drug related", "Harassment & threatening",
    "Weapons & homicide", "Break & enter", "Sexual offences & crimes against children", "Mental health",
}
ARREST_FLAGS = ["concealed_items", "combative", "resisted", "mental_instability", "assaulted_officer", "cooperative"]
SEARCH_FIELDS = [
    "search_reason_injury", "search_reason_escape", "search_reason_weapons", "search_reason_evidence", "items_found",
]

ARRESTS_SCHEMA = {
    "year": pl.Int16,
    "quarter": pl.String,
    "event_id": pl.Int64,
    "arrest_id": pl.Int64,
    "person_id": pl.Int64,
    "perceived_race": pl.String,
    "sex": pl.String,
    "age_group": pl.String,
    "police_division": pl.String,
    "offence_category": pl.String,
    "strip_searched": pl.Boolean,
    "booked": pl.Boolean,
    **{flag: pl.Boolean for flag in ARREST_FLAGS},
    **{field: pl.Boolean for field in SEARCH_FIELDS},
    "youth": pl.Boolean,
}
POPULATION_BY_RACE_SCHEMA = {"perceived_race": pl.String, "population": pl.Int32, "population_share": pl.Float64}


def values_outside(series: pl.Series, allowed: set) -> set:
    return set(series.drop_nulls().unique()) - allowed


class TableChecks:
    data_dir: Path

    #### Schemas ####
    def test_apprehensions_schema(self, apprehensions):
        assert dict(apprehensions.schema) == APPREHENSIONS_SCHEMA

    def test_neighbourhoods_schema(self, neighbourhoods):
        assert dict(neighbourhoods.schema) == NEIGHBOURHOODS_SCHEMA

    def test_neighbourhood_year_schema(self, neighbourhood_year):
        assert dict(neighbourhood_year.schema) == NEIGHBOURHOOD_YEAR_SCHEMA

    #### Apprehensions ####
    def test_apprehensions_required_fields_present(self, apprehensions):
        required = ["event_id", "occurrence_date", "report_date", "occurrence_hour",
                    "premises_type", "apprehension_type", "year"]
        assert apprehensions.select(pl.col(required).null_count()).sum_horizontal().item() == 0

    def test_year_matches_occurrence_date(self, apprehensions):
        assert (apprehensions["occurrence_date"].dt.year() == apprehensions["year"]).all()

    def test_years_start_in_2014(self, apprehensions):
        assert apprehensions["year"].min() == FIRST_YEAR

    def test_reported_on_or_after_occurrence(self, apprehensions):
        assert (apprehensions["report_date"] >= apprehensions["occurrence_date"]).all()

    def test_occurrence_hour_in_range(self, apprehensions):
        assert apprehensions["occurrence_hour"].is_between(0, 23).all()

    def test_categorical_values_valid(self, apprehensions):
        assert not values_outside(apprehensions["apprehension_type"], APPREHENSION_TYPES)
        assert not values_outside(apprehensions["sex"], SEXES)
        assert not values_outside(apprehensions["age_group"], AGE_GROUPS)
        assert not values_outside(apprehensions["premises_type"], PREMISES)

    def test_police_division_format(self, apprehensions):
        assert apprehensions["police_division"].drop_nulls().str.contains(r"^D\d{2}$").all()

    def test_no_youth_records(self, apprehensions):
        # Under-18s are suppressed at source; none should appear.
        assert not apprehensions["age_group"].drop_nulls().str.contains("^(0|1[0-7]) ").any()

    def test_hood_ids_known(self, apprehensions, neighbourhoods):
        assert apprehensions["hood_id"].drop_nulls().is_in(neighbourhoods["hood_id"].implode()).all()

    #### Neighbourhoods ####
    def test_one_row_per_neighbourhood(self, neighbourhoods):
        assert neighbourhoods.height == N_NEIGHBOURHOODS
        assert neighbourhoods["hood_id"].is_unique().all()
        assert neighbourhoods["neighbourhood"].is_unique().all()

    def test_hood_ids_in_158_model_range(self, neighbourhoods):
        assert neighbourhoods["hood_id"].is_between(1, 174).all()

    def test_neighbourhoods_complete(self, neighbourhoods):
        assert neighbourhoods.null_count().sum_horizontal().item() == 0

    def test_population_and_income_positive(self, neighbourhoods):
        assert (neighbourhoods["population"] > 0).all()
        assert (neighbourhoods["median_household_income"] > 0).all()

    def test_percentages_in_range(self, neighbourhoods):
        for column in PERCENT_COLUMNS:
            assert neighbourhoods[column].is_between(0, 100).all(), column

    def test_black_share_within_visible_minority(self, neighbourhoods):
        assert (neighbourhoods["black_pct"] <= neighbourhoods["visible_minority_pct"]).all()

    def test_tsns_designation_valid(self, neighbourhoods):
        assert not values_outside(neighbourhoods["tsns_designation"], TSNS_DESIGNATIONS)

    #### Neighbourhood-year panel ####
    def test_panel_is_complete_grid(self, neighbourhood_year):
        years = neighbourhood_year["year"].unique().sort()
        assert years.to_list() == list(range(years.min(), years.max() + 1))
        assert neighbourhood_year.height == N_NEIGHBOURHOODS * years.len()
        assert not neighbourhood_year.select("hood_id", "year").is_duplicated().any()

    def test_panel_values_valid(self, neighbourhood_year):
        assert neighbourhood_year.null_count().sum_horizontal().item() == 0
        assert (neighbourhood_year["apprehensions"] >= 0).all()

    def test_section_17_within_total(self, neighbourhood_year):
        assert neighbourhood_year["section_17"].is_between(0, neighbourhood_year["apprehensions"]).all()

    def test_section_17_matches_apprehensions(self, apprehensions, neighbourhood_year):
        rows = apprehensions.drop_nulls("hood_id")["apprehension_type"].str.starts_with("Section 17").sum()
        assert neighbourhood_year["section_17"].sum() == rows

    def test_downtown_core_has_13_neighbourhoods(self, neighbourhoods):
        assert neighbourhoods["downtown"].sum() == 13

    def test_rate_matches_count_and_population(self, neighbourhood_year):
        expected = 1000 * neighbourhood_year["apprehensions"] / neighbourhood_year["population"]
        assert ((neighbourhood_year["rate_per_1000"] - expected).abs() < 1e-9).all()

    #### Consistency across tables ####
    def test_panel_years_match_apprehensions(self, apprehensions, neighbourhood_year):
        assert set(neighbourhood_year["year"]) == set(apprehensions["year"])

    def test_panel_counts_match_apprehensions(self, apprehensions, neighbourhood_year):
        counts = apprehensions.drop_nulls("hood_id").group_by("hood_id", "year").len("n")
        merged = neighbourhood_year.join(counts, on=["hood_id", "year"], how="left").with_columns(
            pl.col("n").fill_null(0)
        )
        assert (merged["apprehensions"] == merged["n"]).all()

    def test_panel_population_matches_neighbourhoods(self, neighbourhoods, neighbourhood_year):
        merged = neighbourhood_year.join(neighbourhoods, on="hood_id", suffix="_n")
        assert (merged["population"] == merged["population_n"]).all()

    def test_neighbourhood_totals_match_panel(self, neighbourhoods, neighbourhood_year):
        totals = neighbourhood_year.group_by("hood_id").agg(
            pl.col("apprehensions").sum().alias("total"),
            pl.col("rate_per_1000").mean().alias("mean_rate"),
        )
        merged = neighbourhoods.join(totals, on="hood_id")
        assert (merged["total_apprehensions"] == merged["total"]).all()
        assert ((merged["mean_annual_rate_per_1000"] - merged["mean_rate"]).abs() < 1e-9).all()


class ArrestChecks:
    """Checks for the race-based arrests and strip search tables."""

    data_dir: Path

    def test_arrests_schema(self, arrests):
        assert dict(arrests.schema) == ARRESTS_SCHEMA

    def test_population_by_race_schema(self, population_by_race):
        assert dict(population_by_race.schema) == POPULATION_BY_RACE_SCHEMA

    def test_years_2020_2021(self, arrests):
        assert set(arrests["year"]) == {2020, 2021}

    def test_required_fields_present(self, arrests):
        required = ["year", "quarter", "event_id", "person_id", "strip_searched", "booked", *ARREST_FLAGS, "youth"]
        assert arrests.select(pl.col(required).null_count()).sum_horizontal().item() == 0

    def test_categorical_values_valid(self, arrests):
        assert not values_outside(arrests["quarter"], {"Q1", "Q2", "Q3", "Q4"})
        assert not values_outside(arrests["perceived_race"], PERCEIVED_RACES | {"Unknown or Legacy"})
        assert not values_outside(arrests["sex"], SEXES)
        assert not values_outside(arrests["age_group"], ARREST_AGE_GROUPS)
        assert not values_outside(arrests["offence_category"], OFFENCE_CATEGORIES)

    def test_police_division_format(self, arrests):
        assert arrests["police_division"].drop_nulls().str.contains(r"^D\d{2}$").all()

    def test_youth_matches_age_group(self, arrests):
        known = arrests.drop_nulls("age_group")
        assert (known["youth"] == (known["age_group"] == "17 and under")).all()

    def test_strip_search_implies_booking(self, arrests):
        assert arrests.filter(pl.col("strip_searched"))["booked"].all()

    def test_search_fields_only_for_strip_searches(self, arrests):
        searched = arrests.filter(pl.col("strip_searched"))
        not_searched = arrests.filter(~pl.col("strip_searched"))
        assert searched.select(pl.col(SEARCH_FIELDS).null_count()).sum_horizontal().item() == 0
        assert not_searched.select(pl.col(SEARCH_FIELDS).is_not_null().any()).sum_horizontal().item() == 0

    def test_population_covers_police_categories(self, population_by_race):
        assert set(population_by_race["perceived_race"]) == PERCEIVED_RACES
        assert (population_by_race["population"] > 0).all()

    def test_population_shares_valid(self, population_by_race):
        shares = population_by_race["population_share"]
        assert shares.is_between(0, 1).all()
        # The rest of the population falls in census groups with no police category.
        assert 0.9 < shares.sum() <= 1
