# Status

_Last updated: 5 October 2026_

## Pipeline

| Step | Script | State |
|---|---|---|
| Simulate | `scripts/00-simulate_data.py` | Done |
| Test simulated data | `tests/test_simulated_data.py` (replaces `01-test_simulated_data.R`) | To do |
| Download | `scripts/02-download_data.py` | Done |
| Clean | `scripts/03-clean_data.py` | Done |
| Test analysis data | `tests/test_analysis_data.py` (replaces `04-test_analysis_data.R`) | To do |
| Exploratory analysis | `scripts/05-exploratory_data_analysis.py` | To do |
| Model | `scripts/06-model_data.py` | To do |
| Paper | `paper/paper.qmd` | To do (still starter template) |

Remaining starter leftovers to remove or replace: `scripts/01`, `04`–`07` (R), `models/first_model.rds`, `starter_folder.Rproj`, `README.md`, `paper/` template content.

## Data outputs

`data/02-analysis_data/` (simulated equivalents in `data/00-simulated_data/` share the same schema):

- `apprehensions.parquet`: one row per apprehension, 131,325 rows, 2014–2025.
- `neighbourhoods.parquet`: 158 neighbourhoods with 2021 census covariates, NIA designation, total apprehensions and mean annual rate per 1,000 residents.
- `neighbourhood_year.parquet`: 158 × 12 panel of counts and rates, with zeros filled.
- `neighbourhood_boundaries.geojson`: 158-model boundaries keyed by `hood_id`.

## Decisions

- **Period:** 2014 to the last complete calendar year (currently 2025), by occurrence date. The cutoff is derived from the data. Excluded: 13 rows with pre-2014 occurrence dates and partial 2026.
- **Missing codes:** `NSA` / `Not Recorded` become null. 1,438 in-period rows lack a neighbourhood; they stay in `apprehensions` for city-wide trends but are excluded from neighbourhood tables.
- **Census measures:** 2021 census (25% sample). Population comes from the age-groups total. Percentages for visible minority, Black and Indigenous use the private-household population as denominator; renter % uses private households.
- **Raw data committed:** snapshot of the source data (28.7 MB CSV) kept in the repo for reproducibility, since the source is refreshed quarterly.
- **Environment:** conda supplies Python, uv and Quarto; uv installs packages into the conda env via `UV_PROJECT_ENVIRONMENT`. See `CLAUDE.md`.

## Open issues

- **Denominator problem:** apprehensions are recorded where they occur, not where the person lives. Downtown neighbourhoods with hospitals, shelters and many visitors have inflated per-resident rates (University: 17 per 1,000 vs a city median of about 3.5). Options: sensitivity analysis excluding the downtown core, controls for shelter or hospital presence, or framing results as "where crisis policing happens."
- **No individual race data:** race can only be analysed at neighbourhood level (ecological), so the paper must avoid individual-level claims.
- **Youth suppressed:** people 17 and under are removed at source, so results cover adults only.
- **Repeat individuals:** one person can appear multiple times; counts are apprehensions, not people.

## Next steps

1. Write pytest suites for simulated and analysis data; remove R test scripts.
2. Exploratory analysis: yearly trend (note 2022 launch of the Toronto Community Crisis Service), type breakdown, rate choropleth, rate vs income / visible-minority / renter share.
3. Negative binomial model of counts with a population offset; decide how to handle the downtown core.
4. Replace starter README, `.Rproj`, paper template and leftover R scripts.
