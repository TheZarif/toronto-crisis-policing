# Paper draft: overview

Working notes on the project's data and what exploration has shown so far. The detailed exploratory analysis is split by dataset:

| Dataset | EDA write-up | Script | Figures and tables |
|---|---|---|---|
| Mental Health Act apprehensions + 2021 Census neighbourhoods (main) | [eda_apprehensions.md](eda/apprehensions/eda_apprehensions.md) | `scripts/05a-exploratory_data_analysis_apprehensions.py` | `outputs/eda/apprehensions/` |
| Race-based arrests and strip searches (supplementary) | [eda_arrests.md](eda/arrests/eda_arrests.md) | `scripts/05b-exploratory_data_analysis_arrests.py` | `outputs/eda/arrests/` |

---

## 1. The question

When someone in Toronto is in a mental health crisis, police can detain them and take them to hospital under the Ontario *Mental Health Act*. This is called an **apprehension**. We ask: **are apprehensions spread evenly across the city, or concentrated in poorer, renter-heavy and racialized neighbourhoods?** Supplementary data on arrests and strip searches adds individual-level evidence on race and on how people in crisis are treated.

## 2. Data at a glance

| | Apprehensions (main) | Arrests and strip searches (supplementary) |
|---|---|---|
| Source | Toronto Police via Open Data Toronto | Toronto Police ArcGIS (Open Data Toronto copy is truncated) |
| Unit | One apprehension | One person arrested |
| Size | 131,325 apprehensions | 65,276 arrests (37,347 people) |
| Years | 2014–2025 | 2020–2021 |
| Race | Neighbourhood level only (2021 Census) | Individual, officer-perceived |
| Geography | 158 neighbourhoods | Mostly unknown |
| Linked to | Census income, renting, race, NIA status | Census population by race (benchmark) |

## 3. Headline findings

**Apprehensions** ([details](eda/apprehensions/eda_apprehensions.md)):
- **Trend:** apprehensions rose about 80% from 2014 to 2021, then levelled off around 12,700 a year after the Community Crisis Service launched in 2022.
- **Officer judgement:** 79% are Section 17, an officer's own on-the-spot judgement with no doctor or judge involved.
- **Where:** rates are highest downtown, with pockets in the northwest and east. They track **renter share (ρ 0.53), Indigenous share (0.53) and income (−0.41)**, not visible-minority share overall (−0.05).
- **Improvement Areas:** the city's official disadvantaged neighbourhoods have only modestly higher rates (3.9 vs 3.4 per 1,000).

**Arrests and strip searches** ([details](eda/arrests/eda_arrests.md)):
- **Arrests by race:** relative to population, Black people were arrested at **3.1×** and Indigenous people at **2.8×** the White rate.
- **The policy change:** strip searches fell from about 27% of arrests to about 1% after the October 2020 procedure change.
- **Searches once booked:** Black and White people were strip searched at the same rate. The racial gap is at the arrest stage.
- **Mental health flag:** arrests flagged "mental instability or possibly suicidal" ended in a strip search 72% of the time vs 48% otherwise (before the change). It was 80% for flagged Black people vs 71% for flagged White people.
- **What searches found:** items were found in 34–38% of strip searches for every group.

## 4. How the two fit together

- **The apprehensions data shows *where* crisis policing concentrates.**
- **The arrests data shows *who* police arrest and search,** and that signs of a mental health crisis lead to harsher treatment at arrest.
- **They can't be linked record by record,** so the paper leads with the neighbourhood analysis and uses the arrests data as supporting evidence about individual-level disparities.

## 5. Next steps

1. **Model:** a negative binomial regression of neighbourhood-year apprehension counts with a population offset. Details are in [eda_apprehensions.md §5](eda/apprehensions/eda_apprehensions.md#5-implications-for-the-model).
2. **Paper:** turn these notes into `paper/paper.qmd`.
