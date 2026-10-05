#### Preamble ####
# Purpose: Exploratory analysis of Toronto Police race-based arrest and strip
#   search data (2020-2021): arrest rates by perceived race relative to
#   population, the October 2020 strip search policy change, strip search rates
#   by race, the role of "mental instability" flags, and search outcomes.
# Author: Zarif Masud
# Date: 5 October 2026
# Contact: zarif.masud@gmail.com
# License: MIT
# Pre-requisites: Run 03-clean_data.py first; run from repo root.
#   Figures and tables are written to outputs/eda/arrests/.


#### Workspace setup ####
from pathlib import Path

import pandas as pd
import polars as pl
from mizani.formatters import percent_format
from plotnine import (
    aes,
    annotate,
    coord_flip,
    element_blank,
    geom_col,
    geom_line,
    geom_point,
    geom_text,
    geom_vline,
    ggplot,
    labs,
    position_dodge,
    scale_fill_manual,
    scale_y_continuous,
    theme,
)

from figure_style import BLUE, INK, INK_MUTED, ORANGE, THEME, save

DATA_DIR = Path("data/02-analysis_data")
OUT_DIR = Path("outputs/eda/arrests")
OUT_DIR.mkdir(parents=True, exist_ok=True)

SOURCE = "Source: Toronto Police Service race-based data collection (arrests and strip searches, 2020–2021)"
SOURCE_CENSUS = SOURCE + "; Statistics Canada 2021 Census"

# Toronto Police overhauled its search-of-persons procedure in October 2020.
BEFORE, AFTER = "Before policy change (Jan–Sep 2020)", "After policy change (Oct 2020–Dec 2021)"
OTHER_GROUPS = ["East/Southeast Asian", "South Asian", "Middle-Eastern", "Latino"]


def ordered(df: pd.DataFrame, column: str, levels: list[str]) -> pd.DataFrame:
    df[column] = df[column].astype(pd.CategoricalDtype(levels, ordered=True))
    return df


#### Read data ####
arrests = pl.read_parquet(DATA_DIR / "arrests.parquet").with_columns(
    pl.when((pl.col("year") == 2020) & pl.col("quarter").is_in(["Q1", "Q2", "Q3"]))
    .then(pl.lit(BEFORE))
    .otherwise(pl.lit(AFTER))
    .alias("period")
)
population = pl.read_parquet(DATA_DIR / "population_by_race.parquet")
races = population["perceived_race"].to_list()
known_race = arrests.filter(pl.col("perceived_race").is_in(races))


#### Arrest rates relative to population ####
# People (not arrests) avoids counting repeat arrests of the same person.
arrest_rates = (
    known_race.group_by("perceived_race")
    .agg(pl.len().alias("arrests"), pl.col("person_id").n_unique().alias("people_arrested"))
    .join(population, on="perceived_race")
    .with_columns((1000 * pl.col("people_arrested") / pl.col("population")).alias("people_per_1000"))
)
white_rate = arrest_rates.filter(pl.col("perceived_race") == "White")["people_per_1000"].item()
arrest_rates = arrest_rates.with_columns(
    (pl.col("people_per_1000") / white_rate).alias("ratio_to_white"),
    (pl.col("arrests") / pl.col("arrests").sum()).alias("arrest_share"),
    (pl.col("population") / pl.col("population").sum()).alias("population_share_of_known"),
).sort("people_per_1000")

rate_order = arrest_rates["perceived_race"].to_list()
rate_plot = (
    ggplot(
        ordered(
            arrest_rates.with_columns(
                pl.format(
                    "{}  ({}× White)",
                    pl.col("people_per_1000").round(1),
                    pl.col("ratio_to_white").round(1),
                ).alias("label")
            ).to_pandas(),
            "perceived_race",
            rate_order,
        ),
        aes("perceived_race", "people_per_1000"),
    )
    + geom_col(fill=BLUE, width=0.6)
    + geom_text(aes(label="label"), ha="left", nudge_y=0.6, size=8, color=INK)
    + coord_flip()
    + scale_y_continuous(limits=(0, arrest_rates["people_per_1000"].max() * 1.45), expand=(0, 0))
    + labs(
        title="Black and Indigenous people were arrested at about 3× the White rate",
        subtitle="People arrested at least once in 2020–2021 per 1,000 Toronto residents of the same group",
        x="", y="People arrested per 1,000 residents",
        caption=SOURCE_CENSUS + ".\nPopulation groups combined from census visible-minority categories to match police"
        " categories; people arrested include non-residents.",
    )
    + THEME
    + theme(panel_grid_major_y=element_blank(), figure_size=(7.5, 3.8))
)
save(rate_plot, OUT_DIR, "01_arrest_rate_by_race")
arrest_rates.write_csv(OUT_DIR / "arrest_rates_by_race.csv")


#### Strip searches over time ####
quarterly = (
    arrests.group_by("year", "quarter")
    .agg(pl.len().alias("arrests"), pl.col("strip_searched").mean().alias("strip_search_rate"))
    .sort("year", "quarter")
    .with_columns(pl.format("{} {}", pl.col("year"), pl.col("quarter")).alias("period_label"))
)
quarter_order = quarterly["period_label"].to_list()

trend = (
    ggplot(ordered(quarterly.to_pandas(), "period_label", quarter_order), aes("period_label", "strip_search_rate", group=1))
    + geom_line(color=BLUE, size=1.2)
    + geom_point(color=BLUE, size=2.5)
    # Discrete layers first so the x scale is discrete; 3.5 sits between 2020 Q3 and Q4.
    + geom_vline(xintercept=3.5, linetype="dashed", color=INK_MUTED, size=0.5)
    + annotate(
        "text", x=3.6, y=0.22, label="New search-of-persons\nprocedure (Oct 2020)",
        ha="left", va="bottom", size=7.5, color=INK_MUTED,
    )
    + geom_text(aes(label="strip_search_rate"), format_string="{:.0%}", va="bottom", nudge_y=0.012, size=7.5, color=INK)
    + scale_y_continuous(labels=percent_format(), limits=(0, 0.32))
    + labs(
        title="Strip searches nearly stopped after the October 2020 policy change",
        subtitle="Share of arrests that included a strip search, by quarter",
        x="", y="Arrests with a strip search", caption=SOURCE,
    )
    + THEME
)
save(trend, OUT_DIR, "02_strip_search_trend")
quarterly.write_csv(OUT_DIR / "strip_search_by_quarter.csv")


#### Strip search rates by race, among people booked ####
# Strip searches happen during booking, so booked arrests are the fair denominator.
by_race = (
    known_race.filter(pl.col("booked"))
    .group_by("perceived_race", "period")
    .agg(pl.len().alias("booked"), pl.col("strip_searched").mean().alias("strip_search_rate"))
)
race_order = (
    by_race.filter(pl.col("period") == BEFORE).sort("strip_search_rate")["perceived_race"].to_list()
)

race_plot = (
    ggplot(
        ordered(ordered(by_race.to_pandas(), "perceived_race", race_order), "period", [AFTER, BEFORE]),
        aes("perceived_race", "strip_search_rate", fill="period"),
    )
    + geom_col(position=position_dodge(width=0.8), width=0.75)
    + geom_text(
        aes(label="strip_search_rate", group="period"), format_string="  {:.0%}", position=position_dodge(width=0.8),
        ha="left", size=7.5, color=INK,
    )
    + coord_flip()
    + scale_fill_manual(values={BEFORE: BLUE, AFTER: ORANGE}, breaks=[BEFORE, AFTER])
    + scale_y_continuous(labels=percent_format(), limits=(0, 0.72), expand=(0, 0))
    + labs(
        title="Before October 2020, over half of booked White, Black and Indigenous people were strip searched",
        subtitle="Share of booked arrests that included a strip search, by perceived race",
        x="", y="Booked arrests with a strip search", caption=SOURCE,
    )
    + THEME
    + theme(panel_grid_major_y=element_blank(), figure_size=(8, 4.8))
)
save(race_plot, OUT_DIR, "03_strip_search_by_race")
by_race.sort("period", "strip_search_rate").write_csv(OUT_DIR / "strip_search_by_race.csv")


#### Mental instability flags ####
# Before the policy change, so strip search rates are large enough to compare.
mental = (
    known_race.filter(pl.col("booked") & (pl.col("period") == BEFORE))
    .with_columns(
        pl.when(pl.col("perceived_race").is_in(OTHER_GROUPS))
        .then(pl.lit("Other groups"))
        .otherwise(pl.col("perceived_race"))
        .alias("group"),
        pl.when(pl.col("mental_instability"))
        .then(pl.lit("Flagged mental instability"))
        .otherwise(pl.lit("Not flagged"))
        .alias("flag"),
    )
)
mental = pl.concat([mental, mental.with_columns(pl.lit("All groups").alias("group"))])
mental_rates = mental.group_by("group", "flag").agg(
    pl.len().alias("booked"), pl.col("strip_searched").mean().alias("strip_search_rate")
)
group_order = ["Other groups", "Indigenous", "White", "Black", "All groups"]
flagged_counts = ", ".join(
    f"{group} {n}"
    for group, n in mental_rates.filter(pl.col("flag") == "Flagged mental instability")
    .sort("booked", descending=True)
    .select("group", "booked")
    .iter_rows()
    if group != "All groups"
)

mental_plot = (
    ggplot(
        ordered(ordered(mental_rates.to_pandas(), "group", group_order), "flag", ["Not flagged", "Flagged mental instability"]),
        aes("group", "strip_search_rate", fill="flag"),
    )
    + geom_col(position=position_dodge(width=0.8), width=0.75)
    + geom_text(
        aes(label="strip_search_rate", group="flag"), format_string="  {:.0%}", position=position_dodge(width=0.8),
        ha="left", size=7.5, color=INK,
    )
    + coord_flip()
    + scale_fill_manual(
        values={"Flagged mental instability": ORANGE, "Not flagged": BLUE},
        breaks=["Flagged mental instability", "Not flagged"],
    )
    + scale_y_continuous(labels=percent_format(), limits=(0, 0.95), expand=(0, 0))
    + labs(
        title="People flagged as mentally unstable were far more likely to be strip searched",
        subtitle="Share of booked arrests with a strip search, Jan–Sep 2020, by whether police flagged\n"
        "\"mental instability or possibly suicidal\" at arrest",
        x="", y="Booked arrests with a strip search",
        caption=SOURCE + ".\nOther groups: East/Southeast Asian, South Asian, Middle-Eastern and Latino combined.\n"
        f"People flagged: {flagged_counts}.",
    )
    + THEME
    + theme(panel_grid_major_y=element_blank(), figure_size=(7.5, 4.2))
)
save(mental_plot, OUT_DIR, "04_mental_instability_strip_search")
mental_rates.sort("group", "flag").write_csv(OUT_DIR / "mental_instability_strip_search.csv")


#### Search outcomes ####
found = (
    known_race.filter(pl.col("strip_searched"))
    .group_by("perceived_race")
    .agg(pl.len().alias("strip_searches"), pl.col("items_found").mean().alias("items_found_rate"))
    .sort("items_found_rate")
)

found_plot = (
    ggplot(
        ordered(found.to_pandas(), "perceived_race", found["perceived_race"].to_list()),
        aes("perceived_race", "items_found_rate"),
    )
    + geom_col(fill=BLUE, width=0.6)
    + geom_text(
        aes(label="items_found_rate"), format_string="{:.0%}", ha="left", nudge_y=0.008, size=8, color=INK
    )
    + coord_flip()
    + scale_y_continuous(labels=percent_format(), limits=(0, 0.5), expand=(0, 0))
    + labs(
        title="Strip searches found items at similar rates for every group",
        subtitle="Share of strip searches in which police found items, 2020–2021, by perceived race",
        x="", y="Strip searches that found items", caption=SOURCE,
    )
    + THEME
    + theme(panel_grid_major_y=element_blank(), figure_size=(7, 3.6))
)
save(found_plot, OUT_DIR, "05_items_found")
found.write_csv(OUT_DIR / "items_found_by_race.csv")


#### Console summary ####
print(f"{arrests.height:,} arrest records; {known_race.height / arrests.height:.1%} with a known race category")
print(arrest_rates.select("perceived_race", "people_arrested", "people_per_1000", "ratio_to_white"))
print(quarterly.select("period_label", "arrests", "strip_search_rate"))
print(by_race.sort("period", "strip_search_rate", descending=True))
print(mental_rates.sort("group", "flag"))
print(found)
print(f"Figures and tables written to {OUT_DIR}/")
