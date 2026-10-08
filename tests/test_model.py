"""Checks that the count model specification recovers the effects built into the simulation.

scripts/01-simulate_data.py sets the log apprehension rate to rise by 0.015 per
percentage point of renter households and fall by 0.6 per unit of log median
income, with gamma-Poisson noise (shape 5, so overdispersion alpha = 0.2), and
monthly apprehensions in Crisis Service pilot divisions to fall by 15% after launch.
"""

from pathlib import Path

import numpy as np
import polars as pl
import pytest
import statsmodels.formula.api as smf

SIM_DIR = Path("data/00-simulated_data")
TRUE_RENTER, TRUE_LOG_INCOME, TRUE_ALPHA = 0.015, -0.6, 0.2
TRUE_PILOT_EFFECT = 0.85


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


@pytest.fixture(scope="module")
def crisis_service():
    """Difference-in-differences on the simulated division-month panel, as in 05-model_data.py."""
    panel = (
        pl.read_parquet(SIM_DIR / "division_month.parquet")
        .filter(pl.col("month").is_between(pl.date(2017, 1, 1), pl.date(2024, 8, 1)))
        .with_columns(
            (pl.col("pilot") & (pl.col("month") > pl.col("launch_date"))).fill_null(False).alias("treated"),
            pl.col("month").cast(pl.String).alias("month_label"),
        )
        .to_pandas()
    )
    return smf.negativebinomial(
        "apprehensions ~ treated + C(police_division) + C(month_label)", data=panel
    ).fit(disp=0, maxiter=500, cov_type="cluster", cov_kwds={"groups": panel["police_division"]})


def test_recovers_crisis_service_effect(crisis_service):
    low, high = np.exp(crisis_service.conf_int().loc["treated[T.True]"])
    assert low < TRUE_PILOT_EFFECT < high
