"""Data loading and preprocessing.

Read raw data from ``data/``, clean it, and write a tidy intermediate
file so that modeling code only ever sees clean input.
"""
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def load_data(path: Path):
    """Load one raw file based on its extension.

    Returns
    -------
    pandas.DataFrame
    """
    raise NotImplementedError("detect format (csv/xlsx/json) and load it")


def clean(df):
    """Handle missing values, duplicates, and type coercion."""
    raise NotImplementedError


def save_clean(df, name: str):
    out = DATA_DIR / f"{name}_clean.csv"
    df.to_csv(out, index=False)
    return out
