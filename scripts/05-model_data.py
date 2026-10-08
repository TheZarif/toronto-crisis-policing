#### Preamble ####
# Purpose: Fits the paper's frequentist models and saves tidy results.
#   1. Screening of neighbourhood race and ethnicity shares (correlations and
#      variance inflation) used to choose the count-model predictors.
#   2. Negative binomial regressions of neighbourhood-year apprehension counts
#      on 2021 Census characteristics, with log population as an offset and
#      year effects: all neighbourhoods, excluding the downtown core, Section 17
#      apprehensions only and other apprehension types, with predicted rates and
#      an out-of-sample check.
#   3. Toronto Community Crisis Service: negative binomial difference-in-differences
#      and event study of monthly apprehensions in pilot and other police divisions.
#   4. Logistic regression of strip searches on the "mental instability" flag
#      by perceived race, among booked arrests before the October 2020
#      procedure change.
# Author: Zarif Masud
# Date: 8 October 2026
# Contact: zarif.masud@gmail.com
# License: MIT
# Pre-requisites: Run 03-clean_data.py first; run from repo root.


#### Workspace setup ####
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import patsy
import polars as pl
import statsmodels.formula.api as smf
from scipy.special import expit
from scipy.stats import spearmanr
from statsmodels.stats.outliers_influence import variance_inflation_factor

rng = np.random.default_rng(853)

DATA_DIR = Path("data/02-analysis_data")
MODEL_DIR = Path("models")
OUT_DIR = Path("outputs/model")
MODEL_DIR.mkdir(exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Census characteristics, standardized so each rate ratio is per one standard
# deviation across neighbourhoods. Race and ethnicity shares follow the police
# perceived-race categories; White (the remainder) is the implicit reference.
# Median income is omitted: it is strongly correlated with low-income share
# (r = -0.70) and measures the same thing.
PREDICTORS = [
    "renter_pct", "low_income_pct", "indigenous_pct", "black_pct", "south_asian_pct",
    "east_southeast_asian_pct", "middle_eastern_pct", "latin_american_pct",
]
SCREENED = [*PREDICTORS, "visible_minority_pct"]
COUNT_FORMULA = "{outcome} ~ " + " + ".join(f"{p}_z" for p in PREDICTORS) + " + nia + C(year)"
HOLDOUT_YEARS = (2024, 2025)
CURVE_PREDICTORS = ["renter_pct", "low_income_pct", "indigenous_pct"]

# Crisis Service comparison window: three full years before the first launch,
# ending before the service went citywide on 26 September 2024.
WINDOW = ("2017-01-01", "2024-08-01")
EVENT_QUARTERS = (-12, 8)  # quarters relative to launch; endpoints are binned

STRIP_FORMULA = (
    "strip_searched ~ mental_instability * C(perceived_race, Treatment('White'))"
    " + C(offence_category) + C(age_group) + sex"
)
RACE_GROUPS = ["White", "Black", "Indigenous", "East/Southeast Asian", "South Asian", "Middle-Eastern", "Latino"]


def tidy(result, model: str, terms: str) -> pd.DataFrame:
    """Exponentiated estimates with 95% CIs for terms matching a regex."""
    params = result.params.filter(regex=terms)
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


def neighbour_weights(hood_ids: np.ndarray) -> np.ndarray:
    """Row-standardized contiguity weights (neighbourhoods that share a border or corner)."""
    boundaries = gpd.read_file(DATA_DIR / "neighbourhood_boundaries.geojson").set_index("hood_id").loc[hood_ids]
    geoms = boundaries.geometry.to_numpy()
    adjacency = np.array([[i != j and a.intersects(b) for j, b in enumerate(geoms)] for i, a in enumerate(geoms)], float)
    return adjacency / adjacency.sum(axis=1, keepdims=True)


def morans_i(values: np.ndarray, weights: np.ndarray, permutations: int = 999) -> tuple[float, float]:
    """Moran's I with a one-sided permutation p-value."""
    z = values - values.mean()

    def statistic(v):
        return len(v) / weights.sum() * (v @ weights @ v) / (v @ v)

    observed = statistic(z)
    null = np.array([statistic(rng.permutation(z)) for _ in range(permutations)])
    return observed, (np.sum(null >= observed) + 1) / (permutations + 1)


#### Screen race and ethnicity shares ####
neighbourhoods = pl.read_parquet(DATA_DIR / "neighbourhoods.parquet").to_pandas()
nia = (neighbourhoods["tsns_designation"] == "Improvement Area").astype(float)
standardized = (neighbourhoods[PREDICTORS] - neighbourhoods[PREDICTORS].mean()) / neighbourhoods[PREDICTORS].std()
design = np.column_stack([np.ones(len(standardized)), standardized, (nia - nia.mean()) / nia.std()])
vif = {p: variance_inflation_factor(design, i + 1) for i, p in enumerate(PREDICTORS)}
outside = ~neighbourhoods["downtown"]
screening = pd.DataFrame(
    {
        "measure": SCREENED,
        "city_share": [
            np.average(neighbourhoods[m], weights=neighbourhoods["population"]) for m in SCREENED
        ],
        "rho_all": [spearmanr(neighbourhoods[m], neighbourhoods["mean_annual_rate_per_1000"])[0] for m in SCREENED],
        "rho_outside_downtown": [
            spearmanr(neighbourhoods.loc[outside, m], neighbourhoods.loc[outside, "mean_annual_rate_per_1000"])[0]
            for m in SCREENED
        ],
        "vif": [vif.get(m, np.nan) for m in SCREENED],
    }
)
screening.to_csv(OUT_DIR / "predictor_screening.csv", index=False)


#### Neighbourhood count models ####
neighbourhood_year = pl.read_parquet(DATA_DIR / "neighbourhood_year.parquet").to_pandas()
means, sds = neighbourhoods[PREDICTORS].mean(), neighbourhoods[PREDICTORS].std()
panel = neighbourhood_year.merge(
    neighbourhoods[["hood_id", "neighbourhood", *PREDICTORS, "tsns_designation", "downtown"]], on="hood_id"
)
for p in PREDICTORS:
    panel[f"{p}_z"] = (panel[p] - means[p]) / sds[p]
panel["nia"] = panel["tsns_designation"] == "Improvement Area"
panel["log_population"] = np.log(panel["population"])
panel["other_types"] = panel["apprehensions"] - panel["section_17"]

specifications = {
    "All apprehensions": ("apprehensions", panel),
    "Excluding downtown core": ("apprehensions", panel[~panel["downtown"]]),
    "Section 17 only": ("section_17", panel),
    "Other apprehension types": ("other_types", panel),
}


def fit_count_model(outcome: str, data: pd.DataFrame):
    return smf.negativebinomial(
        COUNT_FORMULA.format(outcome=outcome), data=data, offset=data["log_population"]
    ).fit(
        disp=0,
        maxiter=500,
        # Twelve years per neighbourhood are not independent: cluster by neighbourhood.
        cov_type="cluster",
        cov_kwds={"groups": data["hood_id"]},
    )


count_results, fit_stats = [], []
for name, (outcome, data) in specifications.items():
    result = fit_count_model(outcome, data)
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
        fitted = data.assign(fitted=result.predict(data, offset=data["log_population"]))
        fitted[["hood_id", "neighbourhood", "year", "downtown", "apprehensions", "fitted"]].to_csv(
            OUT_DIR / "count_model_fitted.csv", index=False
        )
        # Spatial dependence left in the residuals: average Pearson residual per neighbourhood.
        alpha = result.params["alpha"]
        pearson = (fitted["apprehensions"] - fitted["fitted"]) / np.sqrt(fitted["fitted"] + alpha * fitted["fitted"] ** 2)
        mean_residual = pearson.groupby(fitted["hood_id"]).mean()
        moran, moran_p = morans_i(mean_residual.to_numpy(), neighbour_weights(mean_residual.index.to_numpy()))
        fit_stats[-1] |= {"morans_i": moran, "morans_i_p": moran_p}

        # Predicted rate per 1,000 residents across the observed range of each key share,
        # with the other shares at their means, outside an Improvement Area, in the last
        # year. Intervals come from 2,000 draws of the coefficients.
        draws = rng.multivariate_normal(result.params.to_numpy(), result.cov_params().to_numpy(), size=2000)
        draws = pd.DataFrame(draws, columns=result.params.index)
        last_year = f"C(year)[T.{panel['year'].max()}]"
        curves = []
        for p in CURVE_PREDICTORS:
            for value in np.linspace(neighbourhoods[p].quantile(0.02), neighbourhoods[p].quantile(0.98), 40):
                log_rate = draws["Intercept"] + draws[last_year] + draws[f"{p}_z"] * (value - means[p]) / sds[p]
                rate = 1000 * np.exp(log_rate)
                curves.append(
                    {"predictor": p, "value": value, "estimate": float(np.median(rate)),
                     "ci_low": float(np.quantile(rate, 0.025)), "ci_high": float(np.quantile(rate, 0.975))}
                )
        pd.DataFrame(curves).to_csv(OUT_DIR / "count_model_predicted_rates.csv", index=False)

count_table = pd.concat(count_results, ignore_index=True)
count_table["term"] = count_table["term"].str.replace("_z", "", regex=False).replace({"nia[T.True]": "nia"})
count_table.to_csv(OUT_DIR / "count_model_rate_ratios.csv", index=False)

# Out-of-sample check: fit to 2014-2023, predict the two held-out years.
train = panel[panel["year"] < HOLDOUT_YEARS[0]]
test = panel[panel["year"].isin(HOLDOUT_YEARS)].assign(year=HOLDOUT_YEARS[0] - 1)  # last fitted year effect
holdout = fit_count_model("apprehensions", train)
predicted = holdout.predict(test, offset=test["log_population"])
fit_stats[0] |= {
    "holdout_rmse": float(np.sqrt(np.mean((test["apprehensions"] - predicted) ** 2))),
    "holdout_mae": float(np.mean(np.abs(test["apprehensions"] - predicted))),
}
pd.DataFrame(fit_stats).to_csv(OUT_DIR / "count_model_fit.csv", index=False)


#### Toronto Community Crisis Service ####
division_month = (
    pl.read_parquet(DATA_DIR / "division_month.parquet")
    .filter(pl.col("month").is_between(pl.lit(WINDOW[0]).str.to_date(), pl.lit(WINDOW[1]).str.to_date()))
    .with_columns(
        # Treated from the first full month after launch.
        (pl.col("pilot") & (pl.col("month") > pl.col("launch_date"))).fill_null(False).alias("treated"),
        (
            (pl.col("month").dt.year() - pl.col("launch_date").dt.year()) * 4
            + (pl.col("month").dt.month() - 1) // 3
            - (pl.col("launch_date").dt.month() - 1) // 3
        ).alias("event_quarter"),
    )
    .to_pandas()
)
division_month["month_label"] = division_month["month"].astype(str)

did = smf.negativebinomial(
    "apprehensions ~ treated + C(police_division) + C(month_label)", data=division_month
).fit(disp=0, maxiter=500, cov_type="cluster", cov_kwds={"groups": division_month["police_division"]})
did.save(MODEL_DIR / "crisis_service_did.pickle", remove_data=True)
did_table = tidy(did, "Pilot divisions after launch", r"^treated").assign(
    divisions=division_month["police_division"].nunique(),
    pilot_divisions=division_month.loc[division_month["pilot"], "police_division"].nunique(),
    alpha=did.params["alpha"],
)
did_table.to_csv(OUT_DIR / "crisis_service_did.csv", index=False)

# Event study: pilot divisions' rate in each quarter around launch, relative to the
# quarter before launch, against the same months in other divisions.
low, high = EVENT_QUARTERS
event = division_month.assign(
    k=lambda d: d["event_quarter"].clip(low, high).where(d["pilot"]).fillna(-1).astype(int)
)
event_fit = smf.negativebinomial(
    "apprehensions ~ C(k, Treatment(-1)) + C(police_division) + C(month_label)", data=event
).fit(disp=0, maxiter=500, cov_type="cluster", cov_kwds={"groups": event["police_division"]})
event_table = tidy(event_fit, "Event study", r"^C\(k").assign(
    quarter=lambda d: d["term"].str.extract(r"\[T\.(-?\d+)\]")[0].astype(int)
)
event_table = pd.concat(
    [event_table, pd.DataFrame([{"model": "Event study", "term": "reference", "estimate": 1.0,
                                 "ci_low": 1.0, "ci_high": 1.0, "quarter": -1}])],
    ignore_index=True,
).sort_values("quarter")
event_table.to_csv(OUT_DIR / "crisis_service_event_study.csv", index=False)


#### Strip search model ####
arrests = (
    pl.read_parquet(DATA_DIR / "arrests.parquet")
    .filter(
        pl.col("booked")
        # Before the October 2020 search-of-persons procedure change.
        & (pl.col("year") == 2020)
        & pl.col("quarter").is_in(["Q1", "Q2", "Q3"])
        & pl.col("perceived_race").is_in(RACE_GROUPS)
    )
    .drop_nulls(["offence_category", "age_group", "sex"])
    .with_columns(pl.col("strip_searched").cast(pl.Int8), pl.col("mental_instability").cast(pl.Int8))
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
tidy(strip, "Strip search", r"mental_instability|perceived_race").to_csv(
    OUT_DIR / "strip_search_odds_ratios.csv", index=False
)

# Average predicted probability of a strip search by flag and group, holding each
# arrest's other characteristics at their observed values. Intervals come from
# 2,000 draws of the coefficients from their estimated sampling distribution.
coef_draws = rng.multivariate_normal(strip.params.to_numpy(), strip.cov_params().to_numpy(), size=2000)
predicted_strip = []
for group in RACE_GROUPS:
    for flag in [0, 1]:
        scenario = arrests.assign(perceived_race=group, mental_instability=flag)
        design = np.asarray(patsy.build_design_matrices([design_info], scenario)[0])
        draws = expit(design @ coef_draws.T).mean(axis=0)
        in_group = arrests["perceived_race"] == group
        predicted_strip.append(
            {
                "race_group": group,
                "mental_instability": bool(flag),
                "predicted_probability": strip.predict(scenario).mean(),
                "ci_low": np.quantile(draws, 0.025),
                "ci_high": np.quantile(draws, 0.975),
                "booked_in_group": int(in_group.sum()),
                "flagged_in_group": int((in_group & (arrests["mental_instability"] == 1)).sum()),
            }
        )
pd.DataFrame(predicted_strip).to_csv(OUT_DIR / "strip_search_predicted.csv", index=False)


#### Console summary ####
print(screening.round(2).to_string(index=False))
print(count_table.round(3).to_string(index=False))
print(pd.DataFrame(fit_stats).round(3).to_string(index=False))
print(did_table.round(3).to_string(index=False))
print(event_table[["quarter", "estimate", "ci_low", "ci_high"]].round(3).to_string(index=False))
print(pd.DataFrame(predicted_strip).round(3).to_string(index=False))
print(f"Models saved to {MODEL_DIR}/, tables to {OUT_DIR}/")
