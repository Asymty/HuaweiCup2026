"""常用回归与分类指标。"""
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)


def regression_metrics(y_true, y_pred) -> dict[str, float]:
    return {
        "MAE": float(mean_absolute_error(y_true, y_pred)),
        "RMSE": float(mean_squared_error(y_true, y_pred) ** 0.5),
        "R2": float(r2_score(y_true, y_pred)),
    }


def classification_metrics(y_true, y_pred) -> dict[str, float]:
    return {
        "Accuracy": float(accuracy_score(y_true, y_pred)),
        "Precision_macro": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        "Recall_macro": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "F1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
    }
