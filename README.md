# Crisis Policing in Toronto's Neighbourhoods

Code, data and paper for *Crisis Policing in Toronto's Neighbourhoods: Mental Health Act apprehensions are more frequent where more households rent and more Indigenous people live, 2014–2025* (Masud, 2026).

**Paper:** [`paper/paper.pdf`](paper/paper.pdf)

## Summary

Toronto police detained people under Ontario's *Mental Health Act* about 11,000 times a year between 2014 and 2025, four times in five on an officer's own judgement. We link 131,325 apprehensions to 2021 Census profiles of the city's 158 neighbourhoods and add the Toronto Police Service's race-based data on 65,276 arrests in 2020–2021.

- Apprehension rates are about 16% higher per standard-deviation increase in the share of households that rent, and about 21% higher per standard-deviation increase in the Indigenous share of residents. Both associations hold outside the downtown core.
- Neighbourhood low income matters only through the downtown core; Black population share and the City's Neighbourhood Improvement Area designation add little.
- Black and Indigenous people were arrested at about three times the White rate relative to population. A mental-instability flag at arrest raised the probability of a strip search for every group, most of all for Black people.

## Repository layout

```
├── paper/            Quarto source (paper.qmd), bibliography and rendered PDF
├── scripts/          Numbered pipeline: simulate → download → clean → explore → model
├── tests/            pytest checks on the simulated data, cleaned data and model
├── data/
│   ├── 00-simulated_data/   Simulated tables with the same schema as the analysis data
│   ├── 01-raw_data/         Snapshot of the source data (never edited by hand)
│   └── 02-analysis_data/    Cleaned tables used by the paper
├── models/           Fitted statsmodels objects
├── outputs/
│   ├── model/        Tidy model results read by the paper
│   └── eda/          Exploratory figures, tables and a write-up for each dataset
└── docs/             Literature reviews and the LLM usage statement
```

## Reproducing the analysis

The environment uses conda for Python 3.12, uv and Quarto, and uv for Python packages (`pyproject.toml`, `uv.lock`). Run everything from the repository root.

```bash
conda env create -f environment.yml
conda activate toronto-crisis-policing
UV_PROJECT_ENVIRONMENT="$CONDA_PREFIX" uv sync --inexact

python scripts/01-simulate_data.py          # simulated tables for testing
python scripts/02-download_data.py          # refresh data/01-raw_data (optional)
python scripts/03-clean_data.py             # build data/02-analysis_data
python -m pytest                            # data and model tests
python scripts/04a-exploratory_data_analysis_apprehensions.py
python scripts/04b-exploratory_data_analysis_arrests.py
python scripts/05-model_data.py             # fit models, write outputs/model
quarto render paper/paper.qmd               # build paper/paper.pdf
```

Rendering the PDF needs a LaTeX distribution (`quarto install tinytex`). `scripts/check_prose.py` flags filler words in the paper text.

## Data

| Dataset | Source | Records |
|---|---|---|
| Mental Health Act Apprehensions | Toronto Police Service via [Open Data Toronto](https://open.toronto.ca/dataset/mental-health-apprehensions/) | 131,325 (cleaned) |
| Neighbourhoods (158 model) | City of Toronto via [Open Data Toronto](https://open.toronto.ca/dataset/neighbourhoods/) | 158 |
| Neighbourhood Profiles, 2021 Census | City of Toronto via [Open Data Toronto](https://open.toronto.ca/dataset/neighbourhood-profiles/) | 158 neighbourhoods |
| Race & Identity-Based Data: Arrests and Strip Searches | [Toronto Police Service](https://services.arcgis.com/S9th0jAJ7bqgIRjw/ArcGIS/rest/services/RBDC_ARR_TBL_001/FeatureServer) | 65,276 |

The Open Data Toronto copy of the arrests dataset is truncated at 32,000 rows, so it is downloaded from the police source instead. A snapshot of the raw data is committed in `data/01-raw_data/` because the sources are refreshed quarterly.

### Data decisions

- **Period:** 2014 to the last complete calendar year (currently 2025), by occurrence date. The cutoff is derived from the data; 13 rows with earlier occurrence dates and the partial current year are dropped.
- **Missing codes:** "NSA" and "Not Recorded" become missing values. The 1,438 apprehensions without a neighbourhood count towards citywide totals but are excluded from neighbourhood tables.
- **Repeated incidents:** `event_id` identifies an incident, not a person. In the raw file, 298 incidents have two or three rows and 115 rows are identical on every field. All rows are kept, because the source defines each row as a separate apprehension and there is no person identifier to deduplicate on (under 0.1% of rows).
- **Census measures:** 2021 Census long-form (25% sample). Population is the age-group total; visible minority, Black and Indigenous shares use the private-household population as denominator, and renter share uses private households.
- **Arrest labels:** the 2020 and 2021 label schemes are harmonized (offence categories into 12 groups, age groups, youth status). A strip search implies the person was booked, following the source documentation.
- **Race benchmark:** census groups are combined to match the police categories. East/Southeast Asian is Chinese, Filipino, Southeast Asian, Korean and Japanese; Middle-Eastern is Arab and West Asian; White is residents who are neither a visible minority nor Indigenous. The benchmark covers 96% of residents.

## Citation

```bibtex
@misc{masud2026crisis,
  title  = {Crisis Policing in {Toronto's} Neighbourhoods: {Mental Health Act} Apprehensions Are More Frequent Where More Households Rent and More {Indigenous} People Live, 2014--2025},
  author = {Masud, Zarif},
  year   = {2026},
  url    = {https://github.com/TheZarif/toronto-crisis-policing}
}
```

Citation metadata is also in [`CITATION.cff`](CITATION.cff).

## Licence

Code is released under the [MIT License](LICENSE). The Open Data Toronto datasets are used under the [Open Government Licence – Toronto](https://open.toronto.ca/open-data-licence/); the arrests and strip searches data are published by the Toronto Police Service and are subject to its terms of use.

## Use of large language models

Claude (Anthropic) assisted with code, data cleaning, exploratory analysis, documentation, an initial literature search and revision of the paper. Every citation was checked against the publisher, Crossref or the original report, and every figure and model result was checked by the author. Details are in [`docs/llm_usage.md`](docs/llm_usage.md).

Using LLMs in research calls for critical reflection throughout, including attention to bias, ownership and plagiarism. I am committed to using these tools ethically. I acknowledge their risks, and I believe we can develop standards of rigour that make use of their speed while addressing their gaps.

## Acknowledgements

The repository layout is adapted from Rohan Alexander's [starter folder](https://github.com/RohanAlexander/starter_folder).
