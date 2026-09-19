"""无需 pytest 的最小端到端冒烟测试。"""
from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.evaluate.metrics import classification_metrics, regression_metrics
from src.evaluate.validation import cross_validate_model, make_cv
from src.model.baseline import build_baseline_pipeline
from src.preprocess.clean_data import clean_data


def run_smoke_test() -> None:
    regression_df = pd.DataFrame({
        "number": [1.0, 2.0, None, 4.0, 5.0, 6.0],
        "category": ["a", "a", "b", "b", "a", "b"],
        "target": [2.0, 4.1, 5.9, 8.2, 10.1, 12.0],
    })
    clean = clean_data(regression_df)
    X_reg, y_reg = clean.drop(columns="target"), clean["target"]
    regressor = build_baseline_pipeline("regression", "linear")
    regressor.fit(X_reg, y_reg)
    reg_prediction = regressor.predict(X_reg)
    assert len(reg_prediction) == len(y_reg)
    assert set(regression_metrics(y_reg, reg_prediction)) == {"MAE", "RMSE", "R2"}

    classification_df = pd.DataFrame({
        "number": [0, 1, 2, 3, 4, 5, 6, 7],
        "category": ["a", "a", "b", "b", "a", "a", "b", "b"],
        "target": [0, 0, 0, 1, 0, 1, 1, 1],
    })
    X_cls = classification_df.drop(columns="target")
    y_cls = classification_df["target"]
    classifier = build_baseline_pipeline("classification", "logistic")
    classifier.fit(X_cls, y_cls)
    cls_prediction = classifier.predict(X_cls)
    assert len(cls_prediction) == len(y_cls)
    assert set(classification_metrics(y_cls, cls_prediction)) == {
        "Accuracy", "Precision_macro", "Recall_macro", "F1_macro"
    }

    cv = make_cv("regression")
    assert cv.n_splits == 5
    cv_result = cross_validate_model(
        regressor, X_reg, y_reg, task="regression", scoring="neg_mean_absolute_error"
    )
    assert len(cv_result["test_score"]) == 5


if __name__ == "__main__":
    run_smoke_test()
    print("SMOKE TEST = PASS")
