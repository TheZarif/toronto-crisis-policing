# CLAUDE.md

## Project
Analysis of Toronto Police Mental Health Act (MHA) apprehensions by neighbourhood, examining whether crisis policing falls disproportionately on lower-income and racialized communities.

## Data (Open Data Toronto, CKAN API)
- `mental-health-apprehensions` — primary; ~137k rows, one per apprehension, 2014–present. No coordinates; spatial unit is `HOOD_158`. Youth (≤17) suppressed; ~1.5k rows lack a valid neighbourhood code.
- `neighbourhoods` — 158-model boundaries (GeoJSON, EPSG:4326); join on `AREA_SHORT_CODE` ↔ `HOOD_158`.
- `neighbourhood-profiles` — 2021 census covariates (population, income, visible minority share) for per-capita rates.
- Toronto Police race-based arrests and strip searches (2020–21), individual-level race data; may support or replace the apprehensions analysis (scope open). Pulled from the TPS ArcGIS layer `RBDC_ARR_TBL_001`, **not** Open Data Toronto (its copy is truncated at 32,000 of 65,276 rows).
- Optional: `persons-in-crisis-calls-for-service-attended`, `neighbourhood-improvement-areas`.

Never edit `data/01-raw_data/`; regenerate it via the download script.

## Stack
- Python only. Conda (`environment.yml`) provides Python 3.12, uv and Quarto; uv manages all Python packages via `pyproject.toml` + `uv.lock`.
- uv must target the conda env (`--active` ignores conda): `export UV_PROJECT_ENVIRONMENT="$CONDA_PREFIX"` after activating.
- Setup: `conda env create -f environment.yml && conda activate toronto-crisis-policing && UV_PROJECT_ENVIRONMENT="$CONDA_PREFIX" uv sync --inexact`.
- Add deps with `uv add --no-sync <pkg> && uv sync --inexact` (dev: `--dev`); never `pip install` or `conda install` Python packages. Run scripts with plain `python scripts/<file>.py` in the activated env.
- `polars` for data wrangling, `geopandas` for spatial work, `plotnine` (ggplot grammar) for all figures, `statsmodels` for models, `great_tables` for paper tables, `pytest` for tests.
- Report in Quarto (`paper/paper.qmd`, Python/Jupyter engine), rendered to PDF.

## Layout
- `scripts/` — numbered pipeline: simulate → download → clean → EDA (05a/05b) → model (06); tests live in `tests/`. Each script runs standalone from repo root.
- `data/` — `00-simulated_data`, `01-raw_data`, `02-analysis_data` (parquet preferred).
- `tests/` — pytest data tests; `table_checks.py` holds checks shared by simulated and analysis data. Run `python -m pytest`.
- `outputs/eda/<dataset>/` — one folder per dataset (`apprehensions` from `05a`, `arrests` from `05b`) holding figures, CSV tables and an `eda_<dataset>.md` write-up. Shared plot theme in `scripts/figure_style.py`.
- `outputs/paper_draft.md` — project overview linking the per-dataset EDA write-ups.
- `models/` (pickled statsmodels fits) and `outputs/model/` (tidy CSV results the paper reads), from `06-model_data.py`.
- `paper/`, `other/` (LLM usage log; `other/literature/` holds one literature review per dataset).

## Status
Progress, decisions and open issues live in `STATUS.md`; update it whenever a pipeline step or decision changes.

## Conventions
- Write as a production analysis repo: clear names, no course/assignment references, no leftover starter-template content. Legacy R starter files are to be replaced by Python equivalents.
- Report rates per 1,000 residents, not raw counts, when comparing neighbourhoods.
- Figures: consistent plotnine theme, colour-blind-safe palettes, labelled axes and sources.
- Seed all randomness; paths relative to repo root.
