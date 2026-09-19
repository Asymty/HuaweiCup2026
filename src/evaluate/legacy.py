"""Metrics and result tables.

Write metric values and tables into ``result/``. Keep plotting separate,
in ``plot.py``.
"""
from pathlib import Path

RESULT_DIR = Path(__file__).resolve().parents[1] / "result"


def metrics(y_true, y_pred):
    raise NotImplementedError("rmse / mae / r2 / accuracy / auc, ...")


def save_table(df, name: str):
    out = RESULT_DIR / f"{name}.csv"
    df.to_csv(out, index=False)
    return out


def save_metrics(d: dict, name: str = "metrics"):
    import json

    out = RESULT_DIR / f"{name}.json"
    out.write_text(json.dumps(d, indent=2, ensure_ascii=False))
    return out
