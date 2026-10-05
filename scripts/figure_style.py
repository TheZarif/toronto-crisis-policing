"""Shared plotnine theme and palette for project figures.

Colours are the validated categorical slots 1-2 and a one-hue blue sequential ramp.
"""

from pathlib import Path

from plotnine import (
    element_blank,
    element_line,
    element_rect,
    element_text,
    theme,
    theme_minimal,
)

BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, INK_MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
SEQUENTIAL_BLUES = ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]

THEME = theme_minimal(base_size=10) + theme(
    figure_size=(7, 4.2),
    text=element_text(color=INK),
    plot_title=element_text(size=12, weight="bold", ha="left"),
    plot_subtitle=element_text(size=9.5, color=INK_MUTED, ha="left"),
    plot_caption=element_text(size=7.5, color=INK_MUTED, ha="left"),
    axis_text=element_text(color=INK_MUTED),
    panel_grid_major=element_line(color=GRID, size=0.4),
    panel_grid_minor=element_blank(),
    legend_position="top",
    legend_title=element_blank(),
    plot_background=element_rect(fill="white", color="white"),
    plot_title_position="plot",
    plot_caption_position="plot",
)


def save(plot, out_dir: Path, name: str, **size) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    plot.save(out_dir / f"{name}.png", dpi=200, verbose=False, **size)
