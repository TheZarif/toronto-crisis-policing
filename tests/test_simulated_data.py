"""Tests for the simulated tables written by scripts/00-simulate_data.py."""

from pathlib import Path

import numpy as np

from table_checks import TableChecks


class TestSimulatedData(TableChecks):
    data_dir = Path("data/00-simulated_data")

    def test_years_cover_2014_to_2025(self, neighbourhood_year):
        assert neighbourhood_year["year"].unique().sort().to_list() == list(range(2014, 2026))

    def test_rate_falls_with_income(self, neighbourhoods):
        # The simulation builds in a negative income effect; the data should show it.
        r = np.corrcoef(
            np.log(neighbourhoods["median_household_income"]),
            np.log(neighbourhoods["mean_annual_rate_per_1000"]),
        )[0, 1]
        assert r < -0.2

    def test_rate_rises_with_renter_share(self, neighbourhoods):
        r = np.corrcoef(
            neighbourhoods["renter_pct"], np.log(neighbourhoods["mean_annual_rate_per_1000"])
        )[0, 1]
        assert r > 0.2
