# Literature review: police, mental health crises and neighbourhoods

*Supports the Mental Health Act apprehensions analysis ([EDA](../../outputs/eda/apprehensions/eda_apprehensions.md)).*

## Introduction

In Ontario, police are often the first and only responders when someone is in a mental health crisis. Section 17 of the *Mental Health Act* lets an officer take a person to hospital on their own judgement, and our data shows that this one power accounts for four in five of Toronto's roughly 12,700 annual apprehensions. This review brings together research on four questions our analysis touches:

1. How large a role do police play in mental health care?
2. Who ends up on a police pathway into care?
3. Why might apprehensions concentrate in particular neighbourhoods?
4. What happens when cities send non-police responders instead?

## 1. Police as a pathway into mental health care

Police contact is a routine part of living with a mental disorder, not a rare event.
- **Livingston (2016)** reviewed quantitative studies from several countries. Roughly **one in four** people with a mental disorder had been arrested, **one in ten** had police involved in their pathway to mental health care, and about **one in 100** police dispatches and encounters involved someone with a mental disorder.
- **Boyce, Rotenberg and Karam (2015)** used the 2012 Canadian Community Health Survey – Mental Health. **34%** of Canadians with a mental or substance use disorder had contact with police in the past year, about twice the rate for people without one (17%).
- Among people with a disorder who had police contact, **19%** said it was about their own emotional, mental health or substance use problems, compared with 2% of people without a disorder.

The Toronto-specific picture comes from inquiry, not statistics.
- **Iacobucci (2014)** was commissioned after the 2013 police shooting of Sammy Yatim on a streetcar. He reviewed how the Toronto Police Service handles people in crisis and made **84 recommendations** on training, de-escalation, mobile crisis teams and alternatives to lethal force.
- He identified a **"failed and underfunded" mental health system** as a root cause of fatal encounters. The point matters for interpreting our data: high apprehension counts may say as much about gaps in health services as about police behaviour.

Once police are involved, compulsion tends to follow.
- **Lebenbaum et al. (2018)** linked Ontario health records and found that **74% of psychiatric admissions** were involuntary, and the share was rising over time.
- **Police contact in the week before admission** raised the risk of an involuntary admission (risk ratio 1.20), as did being an immigrant (1.07).
- So the police pathway our data measures leads, more often than not, to involuntary care.

## 2. Who ends up on the police pathway

The strongest evidence on race comes from research on psychosis.
- **Anderson et al. (2014)** meta-analysed pathways to care at first-episode psychosis. **Black patients were significantly more likely to have police contact** and less likely to have a family doctor involved than White patients.
- They were also **far more likely to be compulsorily detained** (odds ratio 4.56). Asian patients did not show the same pattern.
- This matters for our data in two ways. It suggests apprehensions are unlikely to fall evenly across racial groups. It also warns against treating "visible minority" as one category; our EDA found no link between apprehension rates and overall visible-minority share but a positive one with Black share.

Housing status is just as important.
- **Kouyoumdjian et al. (2019)** followed homeless adults with mental illness in Toronto's At Home/Chez Soi trial. Being homeless raised the odds of any police interaction within three months by **47%** compared with being stably housed.
- These interactions included mental health crises, suicide attempts and victimization, not just suspected offending.
- This offers a direct explanation for the downtown concentration in our map: the neighbourhoods with the highest rates (Moss Park, Kensington-Chinatown, Downtown Yonge East) contain many of the city's shelters and drop-ins.

## 3. Why neighbourhoods matter, and how to measure them

Several studies treat place as a driver of crisis policing in its own right.
- **Morabito (2007)** argued that an officer's decision in a mental health encounter is shaped by **"horizons of context"**: what community mental health resources exist, what the officer already knows about the person, and the character of the place. Under this account, neighbourhood differences in apprehension rates reflect local services and local policing as well as local need.
- **Weich et al. (2017)** gave this idea strong quantitative support in a national study of over a million psychiatric patients in England. **Compulsory admission was more likely in more deprived small areas** (odds ratio 1.22) and in areas with more non-White residents, even after adjusting for each patient's own ethnicity.
- That is the closest published parallel to our design. It combines a neighbourhood-level analysis with explicit attention to deprivation and ethnic composition.

The measurement problem in our EDA is well known in spatial criminology.
- **Andresen (2011)** showed that dividing events by **residential population** gives misleading rates for places where many people work, shop, travel or spend time. He proposed using the **ambient population** (people present in an area over the day) instead.
- Our highest rates are in downtown neighbourhoods with few residents and large daytime populations, such as University (6,435 residents, 17 apprehensions per 1,000). This is the same problem, and it argues for sensitivity analyses that exclude or separately model the downtown core.

## 4. Alternatives to police response

The strongest causal evidence on non-police crisis response comes from Denver.
- **Dee and Pyne (2022)** evaluated the Support Team Assisted Response (STAR) program, which sends a mental health clinician and a paramedic instead of police to low-risk calls.
- STAR's six-month pilot served only some of Denver's police precincts. Dee and Pyne compared those precincts with the rest, before and after launch, in a preregistered study.
- Reports of the targeted, less serious crimes (trespassing, public disorder, resisting arrest) **fell by 34%**, with **no detectable effect on more serious crimes**. Part of the drop came because health responders are less likely to report the people they serve as offenders.
- Toronto's Community Crisis Service follows the same model and also started as area pilots in March 2022. Dee and Pyne's method, comparing areas served by a pilot with areas not yet served before and after launch, is therefore a template for evaluating it with our data.

## Gaps this project addresses

1. **No published neighbourhood-level analysis of Toronto apprehensions.** We found no study using the Toronto Police Mental Health Act apprehension data at neighbourhood level. Canadian work relies on surveys (Boyce et al.), health records (Lebenbaum et al.) or specific clinical groups (Kouyoumdjian et al.).
2. **Police-initiated apprehensions are rarely separated out.** Most studies cannot distinguish Section 17 apprehensions from those ordered by doctors or courts. Our data can, and Section 17 is the measure of police discretion that Morabito's framework points to.
3. **The Community Crisis Service is unevaluated.** Toronto's own reports describe call diversion but not effects on apprehensions. Our 12-year series, together with the pilot geography, makes a Dee and Pyne style evaluation possible.
4. **The denominator problem is rarely addressed.** Andresen's critique has seldom been applied to mental health policing. Testing whether our results hold without the downtown core is a modest but real methodological contribution.

## References

- Anderson, K. K., Flora, N., Archie, S., Morgan, C., & McKenzie, K. (2014). A meta-analysis of ethnic differences in pathways to care at the first episode of psychosis. *Acta Psychiatrica Scandinavica, 130*, 257–268. https://doi.org/10.1111/acps.12254
- Andresen, M. A. (2011). The ambient population and crime analysis. *The Professional Geographer, 63*(2), 193–212.
- Boyce, J., Rotenberg, C., & Karam, M. (2015). Mental health and contact with police in Canada, 2012. *Juristat* (Statistics Canada Catalogue no. 85-002-X). https://www150.statcan.gc.ca/n1/pub/85-002-x/2015001/article/14176-eng.htm
- Dee, T. S., & Pyne, J. (2022). A community response approach to mental health and substance abuse crises reduced crime. *Science Advances, 8*(23), eabm2106. https://doi.org/10.1126/sciadv.abm2106
- Iacobucci, F. (2014). *Police encounters with people in crisis: An independent review conducted for Chief of Police William Blair, Toronto Police Service*. Toronto Police Service.
- Kouyoumdjian, F. G., Wang, R., Mejia-Lancheros, C., Owusu-Bempah, A., Nisenbaum, R., O'Campo, P., Stergiopoulos, V., & Hwang, S. W. (2019). Interactions between police and persons who experience homelessness and mental illness in Toronto, Canada: Findings from a prospective study. *The Canadian Journal of Psychiatry, 64*(10), 718–725. https://doi.org/10.1177/0706743719861386
- Lebenbaum, M., Chiu, M., Vigod, S., & Kurdyak, P. (2018). Prevalence and predictors of involuntary psychiatric hospital admissions in Ontario, Canada: A population-based linked administrative database study. *BJPsych Open, 4*(2), 31–38.
- Livingston, J. D. (2016). Contact between police and people with mental disorders: A review of rates. *Psychiatric Services, 67*(8), 850–857. https://doi.org/10.1176/appi.ps.201500312
- Morabito, M. S. (2007). Horizons of context: Understanding the police decision to arrest people with mental illness. *Psychiatric Services, 58*(12), 1582–1587. https://doi.org/10.1176/ps.2007.58.12.1582
- Weich, S., McBride, O., Twigg, L., et al. (2017). Variation in compulsory psychiatric inpatient admission in England: A cross-classified, multilevel analysis. *The Lancet Psychiatry, 4*(8), 619–626.
