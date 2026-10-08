# LLM usage

**Tool:** Claude (Anthropic), used through Claude Code in VS Code, October 2026.

## What it was used for

- **Dataset discovery:** searching the Open Data Toronto catalogue for datasets with a social justice angle and more than 5,000 records, and checking row counts through the CKAN API.
- **Environment and repository setup:** conda + uv environment, `CLAUDE.md`, README.
- **Code:** simulation, download, cleaning, pytest data tests, exploratory analysis and figures (`scripts/`, `tests/`).
- **Data checks:** finding that Open Data Toronto's copy of the arrests dataset is truncated at 32,000 of 65,276 rows; harmonizing 2020/2021 labels; validating our strip-search rate against the published Toronto Police figure.
- **Writing support:** the EDA write-ups (`outputs/eda/*/eda_*.md`), literature reviews (`docs/literature/`) and early research questions.
- **Paper revision:** shortening the prose and tightening the layout of `paper/paper.qmd`, and checking every citation against Crossref and the original reports.

## How outputs were checked

- **Tests:** every cleaned and simulated table is covered by pytest, and the tests were themselves checked against deliberately corrupted data.
- **Figures:** every figure was rendered and inspected. Errors found this way (reversed map colours, misplaced labels, titles that overstated findings) were fixed.
- **Literature:** every citation was checked against the publisher, PubMed, the journal page or the original report before inclusion. Claims that couldn't be confirmed were removed or softened.
- **Decisions:** scope, research questions and framing were decided by the author. The model proposed options; the author chose.

## Limits

The full conversation is not exported here. Prompts and decisions are reflected in the commit history, and data decisions are listed in the README.
