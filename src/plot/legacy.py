"""Plotting helpers.

Read clean data or model outputs and save figures into ``figures/``.
Use consistent styles and export both PNG (paper) and a vector/300dpi
version.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIG_DIR = Path(__file__).resolve().parents[1] / "figures"


def save(fig, name: str, dpi: int = 300):
    fig.savefig(FIG_DIR / f"{name}.png", dpi=dpi, bbox_inches="tight")
    return FIG_DIR / f"{name}.png"


def line_plot(x, y, name: str):
    fig, ax = plt.subplots()
    ax.plot(x, y)
    return save(fig, name)
