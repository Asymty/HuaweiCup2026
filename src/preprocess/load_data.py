"""表格数据读取与处理后数据保存。"""
from pathlib import Path

import pandas as pd

from src.config import PROCESSED_DATA_DIR

SUPPORTED_EXTENSIONS = {".csv", ".tsv", ".xlsx", ".xls", ".parquet"}


def load_data(path: str | Path, **kwargs) -> pd.DataFrame:
    """按扩展名读取 CSV、TSV、Excel 或 Parquet 文件。"""
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"数据文件不存在: {source}")

    suffix = source.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(source, **kwargs)
    if suffix == ".tsv":
        return pd.read_csv(source, sep="\t", **kwargs)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(source, **kwargs)
    if suffix == ".parquet":
        return pd.read_parquet(source, **kwargs)
    raise ValueError(f"不支持的文件类型 {suffix!r}，支持: {sorted(SUPPORTED_EXTENSIONS)}")


def save_clean(df: pd.DataFrame, name: str, output_dir: str | Path = PROCESSED_DATA_DIR) -> Path:
    """将清洗后的数据保存为 CSV。"""
    destination_dir = Path(output_dir)
    destination_dir.mkdir(parents=True, exist_ok=True)
    filename = name if name.lower().endswith(".csv") else f"{name}_clean.csv"
    output = destination_dir / filename
    df.to_csv(output, index=False)
    return output
