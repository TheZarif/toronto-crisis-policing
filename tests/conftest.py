from functools import cache
from pathlib import Path

import polars as pl
import pytest


@cache
def load(data_dir: Path, table: str) -> pl.DataFrame:
    path = data_dir / f"{table}.parquet"
    if not path.exists():
        pytest.skip(f"{path} not found; run the pipeline scripts first")
    return pl.read_parquet(path)


@pytest.fixture
def apprehensions(request) -> pl.DataFrame:
    return load(request.cls.data_dir, "apprehensions")


@pytest.fixture
def neighbourhoods(request) -> pl.DataFrame:
    return load(request.cls.data_dir, "neighbourhoods")


@pytest.fixture
def neighbourhood_year(request) -> pl.DataFrame:
    return load(request.cls.data_dir, "neighbourhood_year")
