#### Preamble ####
# Purpose: Fits the paper's models and saves tidy results.
#   1. Negative binomial regressions of neighbourhood-year apprehension counts
#      on 2021 Census characteristics, with log population as an offset and
#      year effects, fitted to all neighbourhoods, excluding the downtown
#      core, Section 17 apprehensions only and other apprehension types.
#   2. Logistic regression of strip searches on the "mental instability" flag
#      by perceived race, among booked arrests before the October 2020
#      procedure change.
# Author: Zarif Masud
# Date: 7 October 2026
# Contact: zarif.masud@gmail.com
# License: MIT
# Pre-requisites: Run 03-clean_data.py first; run from repo root.


#### Workspace setup ####
from pathlib import Path

import numpy as np
import pandas as pd
import patsy
import polars as pl
import statsmodels.formula.api as smf
from scipy.special import expit

rng = np.random.default_rng(853)

DATA_DIR = Path("data/02-analysis_data")
MODEL_DIR = Path("models")
OUT_DIR = Path("outputs/model")
MODEL_DIR.mkdir(exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Census characteristics, standardized so each rate ratio is per one standard
# deviation across neighbourhoods. Median income is omitted: it is strongly
# correlated with low-income share (r = -0.70) and measures the same thing.
PREDICTORS = ["renter_pct", "low_income_pct", "indigenous_pct", "black_pct"]
COUNT_FORMULA = "{outcome} ~ " + " + ".join(f"{p}_z" for p in PREDICTORS) + " + nia + C(year)"

STRIP_FORMULA = (
    "strip_searched ~ mental_instability * C(race_group, Treatment('White'))"
    " + C(offence_category) + C(age_group) + sex"
)
RACE_GROUPS = {
    "White": "White",
    "Black": "Black",
    "Indigenous": "Indigenous",
    "East/Southeast Asian": "Other groups",
    "South Asian": "Other groups",
    "Middle-Eastern": "Other groups",
    "Latino": "Other groups",
}


def tidy(result, model: str, exponentiate_terms: str) -> pd.DataFrame:
    """Exponentiated estimates with 95% CIs for terms matching a regex."""
    params = result.params.filter(regex=exponentiate_terms)
    ci = result.conf_int().loc[params.index]
    return pd.DataFrame(
        {
            "model": model,
            "term": params.index,
            "estimate": np.exp(params.to_numpy()),
            "ci_low": np.exp(ci[0].to_numpy()),
            "ci_high": np.exp(ci[1].to_numpy()),
            "p_value": result.pvalues.loc[params.index].to_numpy(),
            "n": int(result.nobs),
        }
    )


#### Neighbourhood count models ####
neighbourhoods = pl.read_parquet(DATA_DIR / "neighbourhoods.parquet")
neighbourhood_year = pl.read_parquet(DATA_DIR / "neighbourhood_year.parquet")

panel = (
    neighbourhood_year.join(
        neighbourhoods.select("hood_id", "neighbourhood", *PREDICTORS, "tsns_designation", "downtown"),
        on="hood_id",
    )
    .with_columns(
        [((pl.col(p) - pl.col(p).mean()) / pl.col(p).std()).alias(f"{p}_z") for p in PREDICTORS]
    )
    .with_columns(
        (pl.col("tsns_designation") == "Improvement Area").alias("nia"),
        pl.col("population").log().alias("log_population"),
        (pl.col("apprehensions") - pl.col("section_17")).alias("other_types"),
    )
    .to_pandas()
)

specifications = {
    "All apprehensions": ("apprehensions", panel),
    "Excluding downtown core": ("apprehensions", panel[~panel["downtown"]]),
    "Section 17 only": ("section_17", panel),
    "Other apprehension types": ("other_types", panel),
}

count_results = []
fit_stats = []
for name, (outcome, data) in specifications.items():
    result = smf.negativebinomial(
        COUNT_FORMULA.format(outcome=outcome), data=data, offset=data["log_population"]
    ).fit(
        disp=0,
        maxiter=500,
        # Twelve years per neighbourhood are not independent: cluster by neighbourhood.
        cov_type="cluster",
        cov_kwds={"groups": data["hood_id"]},
    )
    count_results.append(tidy(result, name, r"_z$|^nia"))
    fit_stats.append(
        {
            "model": name,
            "n": int(result.nobs),
            "neighbourhoods": data["hood_id"].nunique(),
            "alpha": result.params["alpha"],
            "log_likelihood": result.llf,
            "aic": result.aic,
        }
    )
    slug = name.lower().replace(" ", "_")
    result.save(MODEL_DIR / f"apprehensions_{slug}.pickle", remove_data=True)

    if name == "All apprehensions":
        # Observed and fitted counts for model checking in the paper's appendix.
        data.assign(fitted=result.predict(data, offset=data["log_population"])).loc[
            :, ["hood_id", "neighbourhood", "year", "downtown", "apprehensions", "fitted"]
        ].to_csv(OUT_DIR / "count_model_fitted.csv", index=False)

count_table = pd.concat(count_results, ignore_index=True)
count_table["term"] = count_table["term"].str.replace("_z", "", regex=False).replace({"nia[T.True]": "nia"})
count_table.to_csv(OUT_DIR / "count_model_rate_ratios.csv", index=False)
pd.DataFrame(fit_stats).to_csv(OUT_DIR / "count_model_fit.csv", index=False)


#### Strip search model ####
arrests = (
    pl.read_parquet(DATA_DIR / "arrests.parquet")
    .filter(
        pl.col("booked")
        # Before the October 2020 search-of-persons procedure change.
        & (pl.col("year") == 2020)
        & pl.col("quarter").is_in(["Q1", "Q2", "Q3"])
        & pl.col("perceived_race").is_in(list(RACE_GROUPS))
    )
    .drop_nulls(["offence_category", "age_group", "sex"])
    .with_columns(
        pl.col("perceived_race").replace_strict(RACE_GROUPS).alias("race_group"),
        pl.col("strip_searched").cast(pl.Int8),
        pl.col("mental_instability").cast(pl.Int8),
    )
    .to_pandas()
)

strip = smf.logit(STRIP_FORMULA, data=arrests).fit(
    disp=0,
    # People arrested more than once appear repeatedly: cluster by person.
    cov_type="cluster",
    cov_kwds={"groups": arrests["person_id"]},
)
design_info = strip.model.data.model_spec  # patsy DesignInfo in statsmodels 0.15
strip.save(MODEL_DIR / "strip_search_logit.pickle", remove_data=True)
tidy(strip, "Strip search", r"mental_instability|race_group").to_csv(
    OUT_DIR / "strip_search_odds_ratios.csv", index=False
)

# Average predicted probability of a strip search by flag and race group, holding
# each arrest's other characteristics at their observed values. Intervals come
# from 2,000 draws of the coefficients from their estimated sampling distribution.
coef_draws = rng.multivariate_normal(strip.params.to_numpy(), strip.cov_params().to_numpy(), size=2000)
predicted = []
for group in ["White", "Black", "Indigenous", "Other groups"]:
    for flag in [0, 1]:
        scenario = arrests.assign(race_group=group, mental_instability=flag)
        design = np.asarray(patsy.build_design_matrices([design_info], scenario)[0])
        draws = expit(design @ coef_draws.T).mean(axis=0)
        predicted.append(
            {
                "race_group": group,
                "mental_instability": bool(flag),
                "predicted_probability": strip.predict(scenario).mean(),
                "ci_low": np.quantile(draws, 0.025),
                "ci_high": np.quantile(draws, 0.975),
                "flagged_in_group": int(
                    ((arrests["race_group"] == group) & (arrests["mental_instability"] == 1)).sum()
                ),
            }
        )
pd.DataFrame(predicted).to_csv(OUT_DIR / "strip_search_predicted.csv", index=False)


#### Console summary ####
print(count_table.round(3).to_string(index=False))
print(pd.DataFrame(fit_stats).round(3).to_string(index=False))
print(pd.DataFrame(predicted).round(3).to_string(index=False))
print(f"Models saved to {MODEL_DIR}/, tables to {OUT_DIR}/")
