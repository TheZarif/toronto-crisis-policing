# Crisis Policing in Toronto

Are police Mental Health Act apprehensions spread evenly across Toronto, or concentrated in poorer, renter-heavy and racialized neighbourhoods? This project combines 12 years of Toronto Police apprehension records (2014–2025) with 2021 Census neighbourhood profiles. It adds Toronto Police race-based arrest and strip search data (2020–2021) as individual-level evidence on race and on how people in crisis are treated at arrest.

The final scope is still open. The paper may combine both datasets, or focus on the arrests and strip searches data instead of the apprehensions.

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
python scripts/06-model_data.py
```

Run everything from the repository root. The project uses Python in place of R; Python and every package are cited in `paper/references.bib`.

## Structure

Built on Rohan Alexander's [starter folder](https://github.com/RohanAlexander/starter_folder) for *Telling Stories with Data*, adapted to Python.

- `data/`: simulated (`00`), raw (`01`) and cleaned analysis (`02`) data.
- `scripts/`: numbered pipeline (simulate, download, clean, explore, model).
- `tests/`: pytest data tests, run against both the simulated and cleaned data. `tests/test_model.py` checks that the model recovers the effects built into the simulation.
- `models/` and `outputs/model/`: fitted models and their tidy results.
- `outputs/eda/`: figures, tables and a write-up for each dataset. [`outputs/paper_draft.md`](outputs/paper_draft.md) summarizes findings and the proposed research questions.
- `other/literature/`: literature reviews for each dataset.
- `paper/`: Quarto source for the paper.

Project status and decisions are tracked in [`STATUS.md`](STATUS.md).

## Statement on LLM usage

Initial 'scaffolding' was done with LLMs. Code, data cleaning, exploratory analysis and documentation were developed on the starter repository with the assistance of Claude (Anthropic). An initial literature exploration was also done with the help of LLMs that will next be augmented with search in Google Scholar and other research bibliography websites like Research Gate or DPLB. 

Use of LLMs require critical reflection throughout the process, including and not limited to examining bias and addressing questions of ownership and plagiarism. I remain committed to ethical use of LLM tools, and in my adoption of this technology in research and data analysis, I acknowledge the risks,  and I believe we can develop standards of rigour that can leverage the speed and potential of LLM tools while addressing the gaps.