"""项目统一命令行入口。"""
import argparse
from pathlib import Path

import numpy as np
from sklearn.model_selection import train_test_split

from src.evaluate.metrics import classification_metrics, regression_metrics
from src.evaluate.validation import cross_validate_model
from src.model.baseline import build_baseline_pipeline
from src.preprocess.eda import eda_summary, plot_missing_rate
from src.preprocess.load_data import load_data
from src.utils.io import save_json
from src.utils.seed import set_seed
from src.config import RANDOM_SEED, RESULT_DIR


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="2026 华为杯数学建模项目入口")
    parser.add_argument("--mode", required=True, choices=["eda", "baseline"])
    parser.add_argument("--input", type=Path, required=True, help="输入表格路径")
    parser.add_argument("--target", help="baseline 模式的目标列")
    parser.add_argument("--task", choices=["regression", "classification"], default="regression")
    parser.add_argument("--model", default="linear", choices=["linear", "logistic", "random_forest"])
    return parser.parse_args()


def run_eda(path: Path) -> None:
    df = load_data(path)
    summary = eda_summary(df)
    print(f"shape={summary['shape']}, duplicates={summary['duplicates']}")
    print(summary["missing"])
    print(summary["numeric_description"])
    print(f"missing-rate figure: {plot_missing_rate(df)}")


def run_baseline(path: Path, target: str, task: str, model_name: str) -> None:
    df = load_data(path)
    if target not in df.columns:
        raise KeyError(f"目标列不存在: {target}")
    X, y = df.drop(columns=target), df[target]
    stratify = y if task == "classification" else None
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=RANDOM_SEED,
        stratify=stratify,
    )

    pipeline = build_baseline_pipeline(task, model_name)
    pipeline.fit(X_train, y_train)
    prediction = pipeline.predict(X_test)
    holdout = (
        regression_metrics(y_test, prediction)
        if task == "regression"
        else classification_metrics(y_test, prediction)
    )

    if task == "regression":
        scoring = {
            "MAE": "neg_mean_absolute_error",
            "RMSE": "neg_root_mean_squared_error",
            "R2": "r2",
        }
        negative_metrics = {"MAE", "RMSE"}
    else:
        scoring = {
            "Accuracy": "accuracy",
            "Precision_macro": "precision_macro",
            "Recall_macro": "recall_macro",
            "F1_macro": "f1_macro",
        }
        negative_metrics = set()

    cv_result = cross_validate_model(
        pipeline, X_train, y_train, task=task, scoring=scoring, n_splits=5
    )
    cross_validation = {
        name: float(-np.mean(cv_result[f"test_{name}"]))
        if name in negative_metrics
        else float(np.mean(cv_result[f"test_{name}"]))
        for name in scoring
    }
    metrics = {"holdout": holdout, "cross_validation": cross_validation}
    output = save_json(metrics, RESULT_DIR / "baseline_metrics.json")
    print("Hold-out metrics:", holdout)
    print("CV metrics:", cross_validation)
    print(f"metrics saved: {output}")


def main() -> None:
    args = parse_args()
    set_seed()
    if args.mode == "eda":
        run_eda(args.input)
    else:
        if not args.target:
            raise SystemExit("baseline 模式必须提供 --target")
        run_baseline(args.input, args.target, args.task, args.model)


if __name__ == "__main__":
    main()
