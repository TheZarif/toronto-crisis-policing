"""Tests for the analysis tables written by scripts/03-clean_data.py."""

from pathlib import Path

import geopandas as gpd
import polars as pl
import pytest

from table_checks import FIRST_YEAR, ArrestChecks, TableChecks

RAW_APPREHENSIONS = Path("data/01-raw_data/mental_health_apprehensions.csv")
RAW_ARRESTS = Path("data/01-raw_data/arrests_strip_searches.csv")
BOUNDARIES = Path("data/02-analysis_data/neighbourhood_boundaries.geojson")


@pytest.fixture(scope="module")
def raw_apprehensions() -> pl.DataFrame:
    if not RAW_APPREHENSIONS.exists():
        pytest.skip("raw data not found; run scripts/02-download_data.py")
    return pl.read_csv(RAW_APPREHENSIONS, infer_schema_length=0)


class TestAnalysisData(TableChecks):
    data_dir = Path("data/02-analysis_data")

    def test_only_complete_years_kept(self, apprehensions, raw_apprehensions):
        last_report = raw_apprehensions["REPORT_DATE"].str.to_date("%Y-%m-%d").max()
        partial_year = last_report.year if (last_report.month, last_report.day) != (12, 31) else None
        assert apprehensions["year"].max() != partial_year

    def test_no_rows_lost_in_period(self, apprehensions, raw_apprehensions):
        last_year = apprehensions["year"].max()
        in_period = raw_apprehensions.filter(
            pl.col("OCC_YEAR").cast(pl.Int32).is_between(FIRST_YEAR, last_year)
        )
        assert apprehensions.height == in_period.height

    def test_missing_neighbourhood_share_small(self, apprehensions):
        assert apprehensions["hood_id"].null_count() / apprehensions.height < 0.02

    def test_section_17_is_dominant(self, apprehensions):
        share = (
            apprehensions["apprehension_type"] == "Section 17: police officer's own authority"
        ).mean()
        assert 0.7 < share < 0.9

    def test_boundaries_match_neighbourhoods(self, neighbourhoods):
        boundaries = gpd.read_file(BOUNDARIES)
        assert sorted(boundaries["hood_id"]) == sorted(neighbourhoods["hood_id"])
        assert boundaries.geometry.is_valid.all()
        assert boundaries.crs.to_epsg() == 4326

    def test_census_values_plausible(self, neighbourhoods):
        # 2021 Census: Toronto population ~2.8M; neighbourhood medians $50k-$250k.
        assert 2_500_000 < neighbourhoods["population"].sum() < 3_000_000
        assert neighbourhoods["median_household_income"].is_between(40_000, 300_000).all()

    def test_improvement_areas_count(self, neighbourhoods):
        # TSNS 2020 designates 33 Neighbourhood Improvement Areas on the 158 model.
        assert (neighbourhoods["tsns_designation"] == "Improvement Area").sum() == 33


class TestAnalysisArrests(ArrestChecks):
    data_dir = Path("data/02-analysis_data")

    def test_all_raw_records_kept(self, arrests):
        # Full TPS release (Open Data Toronto's copy stops at 32,000 rows).
        raw = pl.read_csv(RAW_ARRESTS, columns=["ObjectId"])
        assert arrests.height == raw.height == 65_276

    def test_strip_search_share_plausible(self, arrests):
        assert 0.08 < arrests["strip_searched"].mean() < 0.15

    def test_population_matches_census_total(self, population_by_race):
        # 2021 Census private-household population of Toronto is about 2.76 million.
        total = population_by_race["population"].sum() / population_by_race["population_share"].sum()
        assert 2_700_000 < total < 2_800_000
