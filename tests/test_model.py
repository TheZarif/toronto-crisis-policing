"""Checks that the count model specification recovers the effects built into the simulation.

scripts/01-simulate_data.py sets the log apprehension rate to rise by 0.015 per
percentage point of renter households and fall by 0.6 per unit of log median
income, with gamma-Poisson noise (shape 5, so overdispersion alpha = 0.2).
"""

from pathlib import Path

import numpy as np
import polars as pl
import pytest
import statsmodels.formula.api as smf

SIM_DIR = Path("data/00-simulated_data")
TRUE_RENTER, TRUE_LOG_INCOME, TRUE_ALPHA = 0.015, -0.6, 0.2


@pytest.fixture(scope="module")
def fitted():
    neighbourhoods = pl.read_parquet(SIM_DIR / "neighbourhoods.parquet")
    panel = (
        pl.read_parquet(SIM_DIR / "neighbourhood_year.parquet")
        .join(neighbourhoods.select("hood_id", "renter_pct", "median_household_income"), on="hood_id")
        .to_pandas()
    )
    return smf.negativebinomial(
        "apprehensions ~ renter_pct + np.log(median_household_income) + C(year)",
        data=panel,
        offset=np.log(panel["population"]),
    ).fit(disp=0, maxiter=300, cov_type="cluster", cov_kwds={"groups": panel["hood_id"]})


def test_recovers_renter_effect(fitted):
    low, high = fitted.conf_int().loc["renter_pct"]
    assert low < TRUE_RENTER < high


def test_recovers_income_effect(fitted):
    low, high = fitted.conf_int().loc["np.log(median_household_income)"]
    assert low < TRUE_LOG_INCOME < high


def test_recovers_overdispersion(fitted):
    assert fitted.params["alpha"] == pytest.approx(TRUE_ALPHA, abs=0.05)
