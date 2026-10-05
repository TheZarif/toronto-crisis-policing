# Crisis Policing in Toronto

Are police Mental Health Act apprehensions spread evenly across Toronto, or concentrated in poorer, renter-heavy and racialized neighbourhoods? This project combines 12 years of Toronto Police apprehension records (2014–2025) with 2021 Census neighbourhood profiles. It adds Toronto Police race-based arrest and strip search data (2020–2021) as individual-level evidence on race and on how people in crisis are treated at arrest.

## Data

| Dataset | Source | Records |
|---|---|---|
| Mental Health Act Apprehensions | Toronto Police Service via [Open Data Toronto](https://open.toronto.ca/dataset/mental-health-apprehensions/) | 131,325 (cleaned) |
| Neighbourhoods (158 model) | City of Toronto via [Open Data Toronto](https://open.toronto.ca/dataset/neighbourhoods/) | 158 |
| Neighbourhood Profiles, 2021 Census | City of Toronto via [Open Data Toronto](https://open.toronto.ca/dataset/neighbourhood-profiles/) | 158 neighbourhoods |
| Race & Identity-Based Data: Arrests and Strip Searches | [Toronto Police Service ArcGIS](https://services.arcgis.com/S9th0jAJ7bqgIRjw/ArcGIS/rest/services/RBDC_ARR_TBL_001/FeatureServer) | 65,276 |

The Open Data Toronto copy of the arrests dataset is truncated at 32,000 rows, so it is downloaded from the police source instead.

## Reproducing

```bash
conda env create -f environment.yml
conda activate toronto-crisis-policing
UV_PROJECT_ENVIRONMENT="$CONDA_PREFIX" uv sync --inexact

python scripts/00-simulate_data.py
python scripts/02-download_data.py
python scripts/03-clean_data.py
python -m pytest
python scripts/05a-exploratory_data_analysis_apprehensions.py
python scripts/05b-exploratory_data_analysis_arrests.py
```

Run everything from the repository root.

## Structure

- `data/`: simulated (`00`), raw (`01`) and cleaned analysis (`02`) data.
- `scripts/`: numbered pipeline (simulate, download, clean, explore, model).
- `tests/`: pytest data tests, run against both the simulated and cleaned data.
- `outputs/eda/`: figures, tables and a write-up for each dataset. [`outputs/paper_draft.md`](outputs/paper_draft.md) summarizes findings and the proposed research questions.
- `other/literature/`: literature reviews for each dataset.
- `paper/`: Quarto source for the paper.

Project status and decisions are tracked in [`STATUS.md`](STATUS.md).

## Statement on LLM usage

Code, data cleaning, exploratory analysis and documentation were developed with the assistance of Claude (Anthropic) through Claude Code.
