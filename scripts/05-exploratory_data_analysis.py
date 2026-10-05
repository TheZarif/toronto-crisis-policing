#### Preamble ####
# Purpose: Exploratory analysis of Mental Health Act apprehensions: trends over
#   time, apprehension types, who is apprehended, where, and how neighbourhood
#   rates relate to income, race and housing tenure.
# Author: Zarif Masud
# Date: 5 October 2026
# Contact: zarif.masud@gmail.com
# License: MIT
# Pre-requisites: Run 03-clean_data.py first; run from repo root.
#   Figures and tables are written to outputs/eda/.


#### Workspace setup ####
from datetime import date
from itertools import pairwise
from pathlib import Path

import geopandas as gpd
import pandas as pd
import polars as pl
from mizani.formatters import comma_format, percent_format
from plotnine import (
    aes,
    annotate,
    coord_flip,
    element_blank,
    element_rect,
    element_text,
    facet_wrap,
    geom_boxplot,
    geom_col,
    geom_jitter,
    geom_line,
    geom_map,
    geom_point,
    geom_smooth,
    geom_text,
    geom_vline,
    ggplot,
    labs,
    position_dodge,
    scale_color_manual,
    scale_fill_manual,
    scale_x_date,
    scale_y_continuous,
    scale_y_log10,
    theme,
    theme_void,
)

from figure_style import BLUE, INK, INK_MUTED, ORANGE, SEQUENTIAL_BLUES, THEME, save

DATA_DIR = Path("data/02-analysis_data")
OUT_DIR = Path("outputs/eda")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Toronto Community Crisis Service (non-police crisis response) pilot launch.
CRISIS_SERVICE_LAUNCH = date(2022, 3, 31)
SOURCE_POLICE = "Source: Toronto Police Service via Open Data Toronto"
SOURCE = SOURCE_POLICE + "; Statistics Canada 2021 Census"
LOG_BREAKS = [1, 2, 3, 5, 10, 20]

#### Read data ####
apprehensions = pl.read_parquet(DATA_DIR / "apprehensions.parquet")
neighbourhoods = pl.read_parquet(DATA_DIR / "neighbourhoods.parquet")
boundaries = gpd.read_file(DATA_DIR / "neighbourhood_boundaries.geojson")

first_year, last_year = apprehensions["year"].min(), apprehensions["year"].max()
period = f"{first_year}–{last_year}"


#### Trend over time ####
monthly = (
    apprehensions.group_by(pl.col("occurrence_date").dt.truncate("1mo").alias("month"))
    .len("apprehensions")
    .sort("month")
    .with_columns(pl.col("apprehensions").rolling_mean(12).alias("rolling_12"))
)

trend = (
    ggplot(monthly, aes("month"))
    + geom_line(aes(y="apprehensions"), color=BLUE, alpha=0.35, size=0.6)
    + geom_line(aes(y="rolling_12"), data=monthly.drop_nulls("rolling_12"), color=BLUE, size=1.2)
    + geom_vline(xintercept=CRISIS_SERVICE_LAUNCH, linetype="dashed", color=INK_MUTED, size=0.5)
    + annotate(
        "text", x=CRISIS_SERVICE_LAUNCH, y=monthly["apprehensions"].min(),
        label=" Community Crisis Service\n launches (Mar 2022)",
        ha="left", va="bottom", size=7.5, color=INK_MUTED,
    )
    + scale_x_date(date_breaks="2 years", date_labels="%Y")
    + scale_y_continuous(labels=comma_format(), limits=(0, None))
    + labs(
        title="Apprehensions rose about 80% from 2014 to 2021, then levelled off",
        subtitle="Mental Health Act apprehensions per month (faint) and 12-month rolling average (bold)",
        x="", y="Apprehensions per month", caption=SOURCE_POLICE,
    )
    + THEME
)
save(trend, OUT_DIR, "01_monthly_trend")

yearly = apprehensions.group_by("year").len("apprehensions").sort("year")
yearly.write_csv(OUT_DIR / "yearly_counts.csv")


#### Apprehension types ####
type_share = (
    apprehensions.group_by("apprehension_type")
    .len("n")
    .with_columns((pl.col("n") / pl.col("n").sum()).alias("share"))
    .sort("n")
)
type_order = type_share["apprehension_type"].to_list()

types = (
    ggplot(type_share.to_pandas().assign(
        apprehension_type=lambda d: d["apprehension_type"].astype(
            pd.CategoricalDtype(type_order, ordered=True)
        )
    ), aes("apprehension_type", "share"))
    + geom_col(fill=BLUE, width=0.6)
    + geom_text(aes(label="share"), format_string="{:.0%}", ha="left", nudge_y=0.01, size=8, color=INK)
    + coord_flip()
    + scale_y_continuous(labels=percent_format(), limits=(0, 0.95), expand=(0, 0))
    + labs(
        title="Four in five apprehensions rest on an officer's own judgement",
        subtitle=f"Share of apprehensions by Mental Health Act authority, {period}",
        x="", y="", caption=SOURCE_POLICE,
    )
    + THEME
    + theme(panel_grid_major_y=element_blank(), figure_size=(7, 3.2))
)
save(types, OUT_DIR, "02_apprehension_types")

type_by_year = (
    apprehensions.group_by("year")
    .agg((pl.col("apprehension_type").str.starts_with("Section 17")).mean().alias("section_17_share"))
    .sort("year")
)
type_by_year.write_csv(OUT_DIR / "section_17_share_by_year.csv")


#### Who is apprehended ####
age_sex = (
    apprehensions.drop_nulls(["sex", "age_group"])
    .group_by("age_group", "sex")
    .len("n")
    .with_columns((pl.col("n") / (last_year - first_year + 1)).alias("per_year"))
    .sort("age_group")
)

demographics = (
    ggplot(age_sex, aes("age_group", "per_year", fill="sex"))
    + geom_col(position=position_dodge(width=0.75), width=0.7)
    + scale_fill_manual(values={"Male": BLUE, "Female": ORANGE})
    + scale_y_continuous(labels=comma_format(), expand=(0, 0, 0.05, 0))
    + labs(
        title="Young adults, especially men aged 25–34, are apprehended most",
        subtitle=f"Average apprehensions per year by age group and sex, {period}",
        x="Age group", y="Apprehensions per year", caption=SOURCE_POLICE + ". Under-18s suppressed at source.",
    )
    + THEME
    + theme(panel_grid_major_x=element_blank())
)
save(demographics, OUT_DIR, "03_age_sex")


#### Where: neighbourhood rates ####
# Quintile bands labelled with their rate ranges, ordered low to high.
edges = [neighbourhoods["mean_annual_rate_per_1000"].quantile(q) for q in (0.2, 0.4, 0.6, 0.8)]
band_labels = [
    f"Under {edges[0]:.1f}",
    *(f"{lo:.1f}–{hi:.1f}" for lo, hi in pairwise(edges)),
    f"{edges[-1]:.1f} or more",
]
rates = neighbourhoods.with_columns(
    pl.col("mean_annual_rate_per_1000").cut(edges, labels=band_labels, left_closed=True).alias("rate_band")
)
map_data = boundaries.merge(rates.to_pandas(), on=["hood_id", "neighbourhood"])
map_data["rate_band"] = map_data["rate_band"].astype(pd.CategoricalDtype(band_labels, ordered=True))

choropleth = (
    ggplot(map_data)
    + geom_map(aes(fill="rate_band"), color="white", size=0.15)
    + scale_fill_manual(values=SEQUENTIAL_BLUES)
    + labs(
        title="Rates are highest downtown, with pockets in the northwest and east",
        subtitle=f"Average annual apprehensions per 1,000 residents, {period}, in quintiles",
        caption=SOURCE + ".\nRates use residents as the denominator, but apprehensions are recorded where they occur.",
    )
    + theme_void(base_size=10)
    + theme(
        figure_size=(8, 5.5),
        plot_title=element_text(size=12, weight="bold", ha="left"),
        plot_subtitle=element_text(size=9, color=INK_MUTED, ha="left"),
        plot_caption=element_text(size=7.5, color=INK_MUTED, ha="left"),
        legend_position="bottom",
        legend_title=element_blank(),
        plot_background=element_rect(fill="white", color="white"),
        plot_title_position="plot",
        plot_caption_position="plot",
    )
)
save(choropleth, OUT_DIR, "04_rate_map")

rates.select(
    "hood_id", "neighbourhood", "tsns_designation", "population",
    "total_apprehensions", "mean_annual_rate_per_1000",
).sort("mean_annual_rate_per_1000", descending=True).write_csv(OUT_DIR / "neighbourhood_rates.csv")


#### Rates vs neighbourhood characteristics ####
COVARIATES = {
    "median_household_income": "Median household income ($000s)",
    "low_income_pct": "Low-income share (LIM-AT, %)",
    "visible_minority_pct": "Visible minority share (%)",
    "black_pct": "Black share (%)",
    "renter_pct": "Renter households (%)",
    "indigenous_pct": "Indigenous share (%)",
}

long = (
    neighbourhoods.with_columns(
        pl.col("median_household_income") / 1000,
        pl.when(pl.col("tsns_designation") == "Improvement Area")
        .then(pl.lit("Neighbourhood Improvement Area"))
        .otherwise(pl.lit("Other neighbourhood"))
        .alias("nia")
    )
    .unpivot(index=["neighbourhood", "nia", "mean_annual_rate_per_1000"], on=list(COVARIATES), variable_name="covariate")
    .with_columns(pl.col("covariate").replace_strict(COVARIATES))
    .to_pandas()
)
long["covariate"] = long["covariate"].astype(pd.CategoricalDtype(list(COVARIATES.values()), ordered=True))

scatter = (
    ggplot(long, aes("value", "mean_annual_rate_per_1000"))
    + geom_point(aes(color="nia"), size=1.6, alpha=0.8, stroke=0)
    + geom_smooth(method="lm", color=INK_MUTED, size=0.6, se=False)
    + facet_wrap("covariate", scales="free_x", ncol=3)
    + scale_y_log10(breaks=LOG_BREAKS)
    + scale_color_manual(values={"Other neighbourhood": BLUE, "Neighbourhood Improvement Area": ORANGE})
    + labs(
        title="Rates track renting, poverty and Indigenous share, not visible-minority share",
        subtitle=f"Average annual apprehensions per 1,000 residents ({period}, log scale) against 2021 Census characteristics",
        x="", y="Apprehensions per 1,000 (log)", caption=SOURCE + ". Grey line: linear fit on the log scale.",
    )
    + THEME
    + theme(figure_size=(9, 6), strip_text=element_text(weight="bold", ha="left"))
)
save(scatter, OUT_DIR, "05_rate_vs_covariates")

correlations = pl.DataFrame(
    {
        "covariate": list(COVARIATES.values()),
        "spearman_rho": [
            neighbourhoods.select(pl.corr(column, "mean_annual_rate_per_1000", method="spearman")).item()
            for column in COVARIATES
        ],
    }
).sort("spearman_rho")
correlations.write_csv(OUT_DIR / "rate_correlations.csv")


#### Improvement Areas vs the rest ####
nia_plot = (
    ggplot(
        neighbourhoods.to_pandas().assign(
            tsns_designation=lambda d: d["tsns_designation"].astype(
                pd.CategoricalDtype(["Neither", "Emerging", "Improvement Area"], ordered=True)
            )
        ),
        aes("tsns_designation", "mean_annual_rate_per_1000"),
    )
    + geom_boxplot(outlier_shape="", width=0.5, color=INK_MUTED, fill="white")
    + geom_jitter(width=0.15, height=0, random_state=853, color=BLUE, alpha=0.6, size=1.4, stroke=0)
    + scale_y_log10(breaks=LOG_BREAKS)
    + labs(
        title="Improvement Areas have only modestly higher rates than other neighbourhoods",
        subtitle=f"Average annual apprehensions per 1,000 residents by 2020 TSNS designation, {period} (log scale)",
        x="", y="Apprehensions per 1,000 (log)", caption=SOURCE,
    )
    + THEME
    + theme(panel_grid_major_x=element_blank(), figure_size=(7, 4))
)
save(nia_plot, OUT_DIR, "06_rate_by_designation")


#### Console summary ####
print(f"{apprehensions.height:,} apprehensions, {period}")
print(yearly)
print(type_by_year)
print(correlations)
print(
    neighbourhoods.group_by("tsns_designation").agg(
        pl.len().alias("neighbourhoods"),
        pl.col("mean_annual_rate_per_1000").median().alias("median_rate"),
    )
)
print(f"Figures and tables written to {OUT_DIR}/")

