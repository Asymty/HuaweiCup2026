"""探索性数据分析摘要与缺失率绘图。"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.config import DRAFT_FIGURES_DIR


def eda_summary(df: pd.DataFrame) -> dict[str, object]:
    """返回规模、缺失值、重复值和数值描述统计。"""
    return {
        "shape": df.shape,
        "missing": df.isna().sum().sort_values(ascending=False),
        "missing_rate": df.isna().mean().sort_values(ascending=False),
        "duplicates": int(df.duplicated().sum()),
        "numeric_description": df.describe(include="number").transpose(),
    }


def plot_missing_rate(df: pd.DataFrame, output: str | Path | None = None) -> Path:
    """绘制并保存各列缺失率条形图。"""
    rates = df.isna().mean().sort_values(ascending=False)
    destination = Path(output) if output else DRAFT_FIGURES_DIR / "missing_rate.png"
    destination.parent.mkdir(parents=True, exist_ok=True)
    width = max(6.0, min(16.0, len(rates) * 0.45))
    fig, ax = plt.subplots(figsize=(width, 4.5))
    rates.plot.bar(ax=ax, color="#4472C4")
    ax.set_ylabel("Missing rate")
    ax.set_ylim(0, 1)
    ax.set_title("Missing values by column")
    fig.tight_layout()
    fig.savefig(destination, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return destination
