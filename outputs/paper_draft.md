# Paper draft: overview

Working notes on the project's data and what exploration has shown so far. The detailed exploratory analysis is split by dataset:

| Dataset | EDA write-up | Script | Figures and tables |
|---|---|---|---|
| Mental Health Act apprehensions + 2021 Census neighbourhoods | [eda_apprehensions.md](eda/apprehensions/eda_apprehensions.md) | `scripts/05a-exploratory_data_analysis_apprehensions.py` | `outputs/eda/apprehensions/` |
| Race-based arrests and strip searches | [eda_arrests.md](eda/arrests/eda_arrests.md) | `scripts/05b-exploratory_data_analysis_arrests.py` | `outputs/eda/arrests/` |

---

## 1. The question

The project asks how the burden of policing, especially crisis policing, falls across Toronto's neighbourhoods and racial groups. Two datasets approach this from different angles:

- **Mental Health Act apprehensions.** When someone is in a mental health crisis, police can detain them and take them to hospital. Are these **apprehensions** spread evenly across the city, or concentrated in poorer, renter-heavy and racialized neighbourhoods?
- **Arrests and strip searches.** Who do police arrest and strip search relative to their share of the population? Are people showing signs of a mental health crisis treated more harshly?

**Scope is still open.** The paper may combine both datasets, lead with one, or focus on the arrests and strip searches data alone (see §6).

## 2. Data at a glance

| | Apprehensions | Arrests and strip searches |
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
- **Who:** 56% men and 44% women, peaking at ages 25–34.
- **Trend:** apprehensions rose about 80% from 2014 to 2021, then levelled off around 12,700 a year after the Community Crisis Service launched in 2022.
- **Officer judgement:** 79% are Section 17, an officer's own on-the-spot judgement with no doctor or judge involved.
- **Where:** rates are highest downtown, with pockets in the northwest and east. They track **renter share (ρ 0.53), Indigenous share (0.53) and income (−0.41)**, not visible-minority share overall (−0.05).
- **Improvement Areas:** the city's official disadvantaged neighbourhoods have only modestly higher rates (3.9 vs 3.4 per 1,000).

**Arrests and strip searches** ([details](eda/arrests/eda_arrests.md)):
- **What and who:** a quarter of arrests are for warrants, breaches and administrative reasons. 81% are of men, peaking at ages 25–34.
- **Repeat arrests:** 72% of people were arrested once, but 2,143 people with five or more arrests account for 27% of all arrests.
- **Arrests by race:** relative to population, Black people were arrested at **3.1×** and Indigenous people at **2.8×** the White rate.
- **The policy change:** strip searches fell from about 27% of arrests to about 1% after the October 2020 procedure change.
- **Searches once booked:** Black and White people were strip searched at the same rate. The racial gap is at the arrest stage.
- **Mental health flag:** arrests flagged "mental instability or possibly suicidal" ended in a strip search 72% of the time vs 48% otherwise (before the change). It was 80% for flagged Black people vs 71% for flagged White people.
- **What searches found:** items were found in 34–38% of strip searches for every group.
- **Validation:** our cleaned data reproduces the police service's published 22.2% strip search rate for 2020.

## 4. How the two fit together

- **The apprehensions data shows *where* crisis policing concentrates.**
- **The arrests data shows *who* police arrest and search,** and that signs of a mental health crisis lead to harsher treatment at arrest.
- **They can't be linked record by record.** In a combined paper, one dataset has to lead and the other supports it. Either can lead; see §6.

## 5. Literature

Short reviews of related research, one per dataset, are in `other/literature/`:
- [lit_review_apprehensions.md](../other/literature/lit_review_apprehensions.md): police as a pathway into mental health care, race and housing on that pathway, neighbourhood effects and the denominator problem, and non-police crisis response.
- [lit_review_arrests.md](../other/literature/lit_review_arrests.md): race and policing in Toronto, the law and reform of strip searching, outcome tests for discrimination, and mental illness at arrest.

## 6. Proposed research questions

Each question builds on an EDA finding and fills a gap identified in the literature reviews.

### Apprehensions by neighbourhood

**RQ1. Which neighbourhood characteristics predict Mental Health Act apprehension rates once considered together, and do they hold outside the downtown core?**
- *From the EDA:* renter share (ρ 0.53), Indigenous share (0.53), income (−0.41) and Black share (0.27) are each correlated with rates, but they overlap, and downtown has extreme rates relative to its residents.
- *From the literature:* Weich et al. (2017) found deprivation and ethnic density predict compulsory admission in England. Andresen (2011) shows residential denominators distort rates in high-traffic areas.
- *Method:* a negative binomial regression of neighbourhood-year counts (158 × 12), adjusted for population, with all characteristics entered together. Run with and without the downtown core.

**RQ2. Do officer-initiated (Section 17) apprehensions track neighbourhood disadvantage more closely than those ordered by doctors or courts?**
- *From the EDA:* 79% of apprehensions are on an officer's own judgement, and the share is rising.
- *From the literature:* Morabito (2007) argues police discretion is shaped by local context. If so, the place-based patterns should be stronger for Section 17 than for apprehensions where a clinician or justice of the peace made the decision.
- *Method:* the RQ1 model fitted separately to Section 17 and to all other types, comparing the size of the associations.

**RQ3. Did apprehensions fall after the Community Crisis Service launched in March 2022?**
- *From the EDA:* the series rose 80% from 2014 to 2021, dipped in 2022–23, then partly rebounded.
- *From the literature:* Dee and Pyne (2022) found a 34% drop in targeted low-level crime in Denver precincts served by a similar program.
- *Method:* an interrupted time series on the monthly citywide series is feasible now. A pilot-area vs non-pilot-area comparison (difference-in-differences) would support a causal claim, but needs the pilot boundaries.

### Race-based arrests and strip searches

**RQ4. At which stage of police contact do racial disparities arise: arrest, booking or strip search? And did the October 2020 reform narrow them?**
- *From the EDA:* Black people were arrested at 3.1× the White rate, but once booked they were strip searched at the same rate. Strip searches fell from 27% to 1% of arrests after the reform.
- *From the literature:* OHRC (2020) and TPS (2022) report single disparity ratios. *Golden* and OIPRD (2019) set out the legal standard the reform aimed to restore.
- *Method:* disparity ratios at each stage (population → arrest → booking → strip search), before and after October 2020.

**RQ5. Are people showing signs of a mental health crisis at arrest strip searched more often, and does this differ by race?**
- *From the EDA:* 72% of flagged booked arrests were strip searched vs 48% of others (before October 2020). It was 80% for flagged Black people vs 71% for flagged White people, with identical rates (51%) among those not flagged.
- *From the literature:* Kesic et al. (2013) show apparent mental illness raises coercion in police encounters. Anderson et al. (2014) show Black people with psychosis are more likely to come into care through police. We found no Canadian study combining the two at the search stage.
- *Method:* a logistic regression of strip search on mental-instability flag × perceived race, adjusted for offence, age and sex, among booked arrests before the reform. Report uncertainty honestly given the small flagged groups.

### Scope options

| Option | Core questions | Supporting | Strengths | Trade-offs |
|---|---|---|---|---|
| **A. Apprehensions-led** | RQ1 + RQ2 (one model) | RQ5 for individual-level race; RQ3 as a descriptive trend | 12 years of data, neighbourhood geography, clearest model | Race only at neighbourhood level, so no individual claims |
| **B. Arrests-led** | RQ4 + RQ5 | RQ1 as neighbourhood context | Individual-level race; the October 2020 reform works as a natural experiment | Only 2 years; location mostly missing; small flagged groups for RQ5 |
| **C. Arrests only** | RQ4 + RQ5 | none | Tightest scope, simplest story | Loses the mental health apprehensions focus and the neighbourhood analysis |

In every option, RQ3 stays descriptive (an interrupted time series with no causal claims) unless we obtain the crisis service's pilot-area boundaries. Option A was the original recommendation. Option B suits a paper centred on racial disparity rather than crisis policing.
