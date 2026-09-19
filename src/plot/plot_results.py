"""轻量、通用的论文结果绘图函数。"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.config import FINAL_FIGURES_DIR


def save_figure(fig, name: str, output_dir: str | Path = FINAL_FIGURES_DIR, dpi: int = 300) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    filename = name if Path(name).suffix else f"{name}.png"
    output = directory / filename
    fig.savefig(output, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return output


def line_plot(x, y, name: str, xlabel: str = "", ylabel: str = "", title: str = "") -> Path:
    fig, ax = plt.subplots()
    ax.plot(x, y, marker="o")
    ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    ax.grid(alpha=0.25)
    return save_figure(fig, name)


def bar_plot(labels, values, name: str, ylabel: str = "", title: str = "") -> Path:
    fig, ax = plt.subplots()
    ax.bar(labels, values, color="#4472C4")
    ax.set(ylabel=ylabel, title=title)
    fig.autofmt_xdate(rotation=30)
    return save_figure(fig, name)


def scatter_actual_vs_predicted(y_true, y_pred, name: str = "actual_vs_predicted") -> Path:
    fig, ax = plt.subplots()
    ax.scatter(y_true, y_pred, alpha=0.7)
    lower = min(min(y_true), min(y_pred))
    upper = max(max(y_true), max(y_pred))
    ax.plot([lower, upper], [lower, upper], "--", color="black", linewidth=1)
    ax.set(xlabel="Actual", ylabel="Predicted", title="Actual vs Predicted")
    return save_figure(fig, name)
