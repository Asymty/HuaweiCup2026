"""Model construction and solving.

Each model should expose a small, testable function. Keep data I/O out
of here; pass clean DataFrames/arrays in and numeric results out.
"""
import numpy as np


def solve(X, y):
    """Fit a model and return predictions or a solution object."""
    raise NotImplementedError


def main_pipeline():
    raise NotImplementedError("wire preprocess -> model here if needed")
