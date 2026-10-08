# Status

_Last updated: 5 October 2026_

## Pipeline

| Step | Script | State |
|---|---|---|
| Simulate | `scripts/00-simulate_data.py` | Done |
| Test simulated data | `tests/test_simulated_data.py` | Done |
| Download | `scripts/02-download_data.py` | Done |
| Clean | `scripts/03-clean_data.py` | Done |
| Test analysis data | `tests/test_analysis_data.py` | Done |
| Exploratory analysis (apprehensions) | `scripts/05a-exploratory_data_analysis_apprehensions.py` → `outputs/eda/apprehensions/` | Done |
| Exploratory analysis (arrests) | `scripts/05b-exploratory_data_analysis_arrests.py` → `outputs/eda/arrests/` | Done |
| Model | `scripts/06-model_data.py` | To do |
| Draft notes | `outputs/paper_draft.md` (overview) + `outputs/eda/*/eda_*.md` (per-dataset EDA write-ups) | Done |
| Literature review | `other/literature/lit_review_apprehensions.md`, `lit_review_arrests.md` (10 and 11 verified sources) | Done |
| Research questions | `outputs/paper_draft.md` §6 (RQ1–RQ5; scope options A apprehensions-led, B arrests-led, C arrests only) | Proposed, awaiting decision |
| Paper | `paper/paper.qmd` | To do (still starter template) |

Run tests with `python -m pytest` (88 tests; shared checks in `tests/table_checks.py` run against both datasets).

Remaining starter leftovers to remove or replace: `scripts/06`–`07` (R), `models/first_model.rds`, `starter_folder.Rproj`, `paper/` template content.

## Data outputs

`data/02-analysis_data/` (simulated equivalents in `data/00-simulated_data/` share the same schema):

- `apprehensions.parquet`: one row per apprehension, 131,325 rows, 2014–2025.
- `neighbourhoods.parquet`: 158 neighbourhoods with 2021 census covariates, NIA designation, total apprehensions and mean annual rate per 1,000 residents.
- `neighbourhood_year.parquet`: 158 × 12 panel of counts and rates, with zeros filled.
- `neighbourhood_boundaries.geojson`: 158-model boundaries keyed by `hood_id`.
- `arrests.parquet`: 65,276 race-based arrest and strip search records, 2020–2021 (one row per person arrested).
- `population_by_race.parquet`: 2021 Toronto population in the seven police perceived-race categories (benchmark for disparity ratios).

## Exploratory findings

From `outputs/eda/apprehensions/` (write-up: `eda_apprehensions.md`):

- **Trend:** annual apprehensions rose about 80% from 7,387 (2014) to a peak of 13,350 (2021), then levelled off around 12,000–12,800. There was a dip in 2022–23 after the Community Crisis Service launched, but it doesn't establish cause on its own.
- **Authority:** 79% are Section 17 (officer's own judgement); this share edged up from 78% in 2014 to 82% in 2025.
- **Who:** the 25–34 age group is the largest; men outnumber women in every age group.
- **Where:** rates are highest in the downtown core (University, Kensington-Chinatown, Downtown Yonge East, Yonge-Bay, Moss Park), with pockets in the northwest (West Humber-Clairville, York University Heights) and east (West Hill).
- **Neighbourhood correlates (Spearman ρ with mean annual rate):** Indigenous share 0.53, renter share 0.53, median income −0.41, low-income share 0.38, Black share 0.27, visible-minority share −0.05.
- **Improvement Areas:** median rate 3.9 vs 3.4 elsewhere, only a modest difference.

### Arrests and strip searches

From `outputs/eda/arrests/` (write-up: `eda_arrests.md`):


- People arrested per 1,000 residents of the same group, 2020–21: Black 38.6 (3.1× White), Indigenous 35.6 (2.8×), Middle-Eastern 21.1, Latino 13.9, White 12.5, South Asian 7.3, East/Southeast Asian 6.0.
- Strip searches fell from 26–28% of arrests to 1–5% after the October 2020 search-of-persons procedure change; compare rates within a period.
- Before the change, among booked arrests: Indigenous 59%, Black 53%, White 52% strip searched vs 33–35% for other groups. So the Black–White gap is at arrest, not search.
- Arrests flagged "mental instability or possibly suicidal" (3.3%) were strip searched 72% vs 48% (booked, pre-change); Black flagged 80% vs White flagged 71%, while unflagged were equal at 51%.
- Items were found in 34–38% of strip searches for every group (no outcome-test evidence of a lower search threshold for any group).

## Decisions

- **Period:** 2014 to the last complete calendar year (currently 2025), by occurrence date. The cutoff is derived from the data. Excluded: 13 rows with pre-2014 occurrence dates and partial 2026.
- **Missing codes:** `NSA` / `Not Recorded` become null. 1,438 in-period rows lack a neighbourhood; they stay in `apprehensions` for city-wide trends but are excluded from neighbourhood tables.
- **Repeated event IDs:** `event_id` identifies an incident, not a person or row. 298 incidents have 2–3 rows (several people apprehended), including 115 rows identical on every field. All rows are kept because the source defines each row as a distinct apprehension and there is no person ID to deduplicate on (<0.1% of rows).
- **Census measures:** 2021 census (25% sample). Population comes from the age-groups total. Percentages for visible minority, Black and Indigenous use the private-household population as denominator; renter % uses private households.
- **Arrests source:** downloaded from the Toronto Police ArcGIS layer `RBDC_ARR_TBL_001`, because Open Data Toronto's copy is truncated at 32,000 of 65,276 rows. 2020/2021 label schemes harmonized (offence categories into 12 groups, age groups, youth). Strip searched implies booked, per source documentation.
- **Race benchmark:** census groups combined to match police categories (East/Southeast Asian = Chinese + Filipino + Southeast Asian + Korean + Japanese; Middle-Eastern = Arab + West Asian; White = not a visible minority minus Indigenous identity). Covers 96% of residents.
- **Raw data committed:** snapshot of the source data (28.7 MB CSV) kept in the repo for reproducibility, since the source is refreshed quarterly.
- **Environment:** conda supplies Python, uv and Quarto; uv installs packages into the conda env via `UV_PROJECT_ENVIRONMENT`. See `CLAUDE.md`.

## Open issues

- **Arrests data limits:** race is officer-perceived; 7.7% Unknown or Legacy; 45% of arrests lack a location; people arrested include non-residents but the benchmark is residents; only 2020–21 (pandemic years); flagged-mental-instability subgroups are small (Indigenous n=29 pre-change).

- **Denominator problem:** apprehensions are recorded where they occur, not where the person lives. Downtown neighbourhoods with hospitals, shelters and many visitors have inflated per-resident rates (University: 17 per 1,000 vs a city median of about 3.5). Options: sensitivity analysis excluding the downtown core, controls for shelter or hospital presence, or framing results as "where crisis policing happens."
- **No individual race data:** race can only be analysed at neighbourhood level (ecological), so the paper must avoid individual-level claims.
- **Youth suppressed:** people 17 and under are removed at source, so results cover adults only.
- **Repeat individuals:** one person can appear multiple times; counts are apprehensions, not people.

## Plan to finish

Base spec: [Telling Stories with Data, Paper One](https://tellingstorieswithdata.com/25-papers.html#sec-paper-one), adapted for PhD flexibility.

**Decisions (7 Oct 2026):**
- **Python stays.** Cite Python and every package in place of R, and note the substitution in the README.
- **Scope:** a Paper One data paper plus one light model, about 6–10 pages.
- **Lead dataset:** apprehensions (option A), with arrests and strip searches as a short individual-level section.
- **Title page:** author Zarif Masud; date set at render time; no fixed deadline.

**Paper outline (`paper/paper.qmd`, Python/Jupyter engine, renders to PDF):**
1. Title, author, date, abstract (3–4 sentences), repo link in a footnote.
2. **Introduction:** 3–4 paragraphs (estimand, findings, why it matters), plus a roadmap paragraph.
3. **Data:**
   - sources and context
   - **measurement**: how an event becomes a row (MHA sections, officer discretion, NSA coding, youth suppression, officer-perceived race)
   - cleaning decisions
   - a summary table
   - figures of the actual observations: monthly trend, neighbourhood map, 158-neighbourhood scatter, apprehension types
   - a short subsection on race-based arrests (arrest rates by race, the mental-instability flag)
   - ethics
4. **Model:** negative binomial regression on neighbourhood-year counts with a log-population offset. Predictors: renter share, low-income share, Indigenous share, Black share, NIA status, year effects. Fit on simulated data first to check that it recovers the known effects. Covers RQ1, plus RQ2 by fitting Section 17 and other types separately.
5. **Results:** incidence-rate-ratio table and figure, plus the downtown sensitivity check.
6. **Discussion:** findings, the ecological fallacy, the residents-vs-visitors denominator problem, the Community Crisis Service (descriptive only), weaknesses, next steps.
7. **Appendix:** cleaning details, model diagnostics, strip-search logistic model (RQ5), staged disparity table (RQ4).

**Phases:**
1. **Clean up:** delete leftover R scripts, `.Rproj`, `first_model.rds`, the template paper and starter sketches; replace `other/llm_usage/usage.txt`.
2. **Model:** `scripts/06-model_data.py` saves fitted models and tidy results to `models/` and `outputs/model/`; tests on model inputs.
3. **References:** `paper/references.bib` with the literature, datasets, Python, packages, Quarto and the textbook.
4. **Write `paper.qmd`:** figures with plotnine and tables with great_tables, generated in hidden code chunks from saved data.
5. **Sketches:** hand-drawn dataset and graph sketches (Zarif) filed in `other/sketches/`.
6. **Checks:** banned-words script, clean PDF render, cross-references, captions, typo pass.
7. **Wrap up:** update README and STATUS, commit, push.
