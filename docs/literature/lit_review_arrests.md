# Literature review: race, arrests and strip searches in Toronto

*Supports the race-based arrests and strip search analysis ([EDA](../../outputs/eda/arrests/eda_arrests.md)).*

## Introduction

Canada has long lacked the race-coded police data that has driven research in the United States and the United Kingdom. Toronto's 2020–2021 race-based data on arrests and strip searches is one of the first large datasets of its kind in the country. This review covers four areas:

1. Canadian evidence that came before this dataset.
2. The legal and policy history of strip searching in Ontario.
3. The statistical methods used to test for discrimination in police searches.
4. Research on how mental health shapes what happens at arrest.

## 1. Evidence on race and policing in Toronto

Before official data existed, researchers relied on surveys.
- **Wortley and Owusu-Bempah (2011)** used a 2007 survey of Toronto residents. Black respondents were far more likely than White or Asian respondents to see racial profiling as a major problem.
- Their own reports of being stopped and searched suggested that **this concern was justified**.
- The study set the main hypothesis that later administrative data has tested: Black Torontonians experience more police contact than their share of the population would predict.

Police stop data later confirmed the pattern and showed it has a geography.
- **Meng (2017)** analysed Toronto Police stop data from 2003–2012. For **Black youth**, the number of stops rose **42.7%** and the ratio of stops to arrests rose **44.9%** over the decade. For White youth, both fell steadily.
- Stops of Black youth were **most excessive in neighbourhoods with more White residents and/or higher crime rates**. The disparity depends on where people are, not only on who they are.
- Meng argued that police stops should be studied in their neighbourhood context. Our arrests data can't do this, since 45% of arrests lack a location. That makes the neighbourhood-level apprehensions analysis a useful complement.

The Ontario Human Rights Commission's inquiry into the Toronto Police Service tested that hypothesis with police records.
- In **A Disparate Impact (OHRC, 2020)**, Wortley and colleagues analysed 2013–2017 charge, arrest and use-of-force data. Black people were **8.8% of Toronto's population but 32.4% of people charged**, making them 3.9 times more likely than White people to appear in the charge data.
- The over-representation was **largest for low-level, discretionary charges**: Black people made up 42.5% of those charged with obstructing justice.
- Our finding that Black people were arrested at **3.1 times** the White rate in 2020–21 is close to the OHRC's 3.9 for 2013–17. This suggests the disparity persisted into the period covered by the new data.

## 2. Strip searching: law, overuse and reform

The legal standard comes from the Supreme Court of Canada.
- In **R v Golden (2001)**, the Court held that strip searches are **"inherently humiliating and degrading"** however they are carried out, so they **cannot be done simply as a matter of routine policy**.
- A lawful arrest does not automatically authorize a strip search. Police need reasonable and probable grounds to believe one is necessary in the specific circumstances of each arrest.

Toronto did not follow that standard for almost two decades.
- **Breaking the Golden Rule (OIPRD, 2019)**, by Ontario's police oversight body, found that **well over 22,000 strip searches** were carried out in Ontario each year, most of them by the Toronto Police Service.
- Toronto **strip searched 37–43% of everyone it arrested in 2014–2016**, while other large Ontario services reported rates **under 1%**.
- The report concluded that strip searches were still being done in breach of *Golden* and made 50 recommendations on authorization, documentation and training.

The Toronto Police Service's own analysis of the 2020 data appeared in **Race & Identity Based Data Collection Strategy: Understanding Use of Force & Strip Searches in 2020 (TPS, 2022)**.
- **22.2%** of people arrested in 2020 were strip searched. People perceived as Black were **31% of those strip searched**, compared with about 10% of the population and 27% of arrests.
- The procedure change in **October 2020** cut strip searches from about 27% of arrests to around 5%.
- Our cleaned data reproduces the 22.2% figure exactly (7,115 of 31,979 arrests in 2020), which validates our pipeline against the official source.

**The disparity you find depends on the denominator.** The TPS report shows Black people over-represented among those strip searched relative to their share of all arrests (31% vs 27%). Our analysis compares strip search rates among *booked* arrests, since searches happen during booking, and finds Black and White people searched at almost identical rates before the policy change (53% vs 52%). Both are correct. Black arrestees were booked slightly more often (56% vs 52%), so more of them reached the stage where strip searches happen. Showing the disparity at each stage (population → arrest → booking → search) is more informative than any single ratio.

## 3. Testing for discrimination: outcome tests and their limits

Comparing search *rates* can't on its own tell biased searching apart from real differences in what police are looking for. Economists proposed comparing search *outcomes* instead.
- **Knowles, Persico and Todd (2001)** introduced the **hit-rate or outcome test**. If police search to find contraband and aren't prejudiced, the share of searches that find something should be the same across groups.
- If one group's searches turn up contraband *less* often, police are applying a lower bar to that group.
- Applied to Maryland highway searches, their test found hit rates consistent with no prejudice against Black drivers.

The outcome test has a known weakness.
- **Simoiu, Corbett-Davies and Goel (2017)** showed it can mislead because of **infra-marginality**. Equal average hit rates can hide unequal search thresholds if the groups differ in their underlying risk.
- They developed a "threshold test" that estimates the bar for each group directly. In 4.5 million North Carolina stops, the two tests gave different answers.

At larger scale, the evidence points to bias.
- **Pierson et al. (2020)** analysed about 100 million US traffic stops. Using both outcome and threshold tests, they found that **the bar for searching Black and Hispanic drivers was lower** than for White drivers.
- They also found that Black drivers were less likely to be stopped after dark, when race is harder to see.

**For our data:** items were found in 34–38% of strip searches for every group, which on its face is the "no evidence of a lower bar" result. Simoiu et al. show that this is not conclusive, and we lack the detail needed to run a threshold test. The paper should report equal hit rates as **consistent with, but not proof of, equal search standards**. It should also note that **about 62% of strip searches found nothing**, which bears on the necessity standard set in *Golden*.

## 4. Mental health at the point of arrest

Our dataset records whether the officer saw "mental instability or possibly suicidal" behaviour, which links it to the apprehensions analysis.
- **Kesic, Thomas and Ogloff (2013)** examined 4,267 incidents in which Victoria (Australia) police used force between 1995 and 2008. In **7.2%**, the person appeared to have a mental disorder.
- In those incidents, weapons were more likely to be involved. The authors recommended better training in communication and de-escalation, and closer coordination between police and mental health services.
- The broader point is that apparent mental illness changes how police handle an encounter, often toward more coercion. Our finding fits this pattern: people flagged for mental instability were strip searched far more often (72% vs 48% of booked arrests before October 2020).
- **What our data adds** is the interaction with race: 80% of flagged Black people were strip searched, against 71% of flagged White people, while unflagged Black and White people were searched at identical rates. Combinations like this, of race with apparent mental illness, are rarely examined in published work, and we found no Canadian study that tests them with administrative data.

## Gaps this project addresses

1. **Mental illness and race combined at the search stage.** Research has studied racial disparities and mental illness in police encounters separately. Our data allows a direct, if small-sample, test of whether apparent mental illness leads to more invasive searches and whether that effect differs by race.
2. **Disparities across the stages of contact.** Most Toronto reports give a single disparity ratio. Breaking the disparity down from population to arrest, booking and search shows where it arises. Here, the Black–White gap arises mostly at arrest.
3. **A natural experiment from the October 2020 reform.** OIPRD (2019) called for the reform, and our data shows its effect: strip searches fell from 27% to about 1% of arrests. Comparing group disparities before and after shows whether reducing officer discretion also narrowed the gaps between groups.
4. **Outcome tests in a Canadian setting.** Hit-rate analysis is standard in US research but rare in Canada. Our equal hit rates, read with the infra-marginality caveat, add a first data point.
5. **Data quality.** The Open Data Toronto copy of this dataset is truncated at 32,000 of 65,276 records. Any study that relies on it uses half the data, a problem that hasn't been documented elsewhere as far as we know.

## References

- Kesic, D., Thomas, S. D. M., & Ogloff, J. R. P. (2013). Use of nonfatal force on and by persons with apparent mental disorder in encounters with police. *Criminal Justice and Behavior, 40*(3), 321–337.
- Knowles, J., Persico, N., & Todd, P. (2001). Racial bias in motor vehicle searches: Theory and evidence. *Journal of Political Economy, 109*(1), 203–229. https://doi.org/10.1086/318603
- Office of the Independent Police Review Director. (2019). *Breaking the golden rule: A review of police strip searches in Ontario*. Toronto: OIPRD.
- Ontario Human Rights Commission. (2020). *A disparate impact: Second interim report on the inquiry into racial profiling and racial discrimination of Black persons by the Toronto Police Service*. https://www.ohrc.on.ca/en/disparate-impact-second-interim-report-inquiry-racial-profiling-and-racial-discrimination-black
- Pierson, E., Simoiu, C., Overgoor, J., Corbett-Davies, S., Jenson, D., Shoemaker, A., Ramachandran, V., Barghouty, P., Phillips, C., Shroff, R., & Goel, S. (2020). A large-scale analysis of racial disparities in police stops across the United States. *Nature Human Behaviour, 4*, 736–745. https://doi.org/10.1038/s41562-020-0858-1
- Meng, Y. (2017). Profiling minorities: Police stop and search practices in Toronto, Canada. *Human Geographies, 11*(1), 5–23. https://doi.org/10.5719/hgeo.2017.111.1
- *R v Golden*, 2001 SCC 83, [2001] 3 SCR 679.
- Simoiu, C., Corbett-Davies, S., & Goel, S. (2017). The problem of infra-marginality in outcome tests for discrimination. *The Annals of Applied Statistics, 11*(3), 1193–1216.
- Toronto Police Service. (2022). *Race & identity based data collection strategy: Understanding use of force & strip searches in 2020 — Detailed report*. https://www.tps.ca/race-identity-based-data-collection/
- Wortley, S., & Owusu-Bempah, A. (2011). The usual suspects: Police stop and search practices in Canada. *Policing and Society, 21*, 395–407. https://doi.org/10.1080/10439463.2011.610198
