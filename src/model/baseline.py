"""自动处理数值与类别特征的 sklearn 基线模型。"""
from collections.abc import Sequence

from sklearn.compose import ColumnTransformer, make_column_selector
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config import RANDOM_SEED


def build_baseline_pipeline(task: str, model: str = "linear", random_seed: int = RANDOM_SEED) -> Pipeline:
    """构造回归或分类 Pipeline；列类型在 fit 时自动识别。"""
    task = task.lower()
    model = model.lower()

    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])
    preprocessing = ColumnTransformer([
        ("numeric", numeric_pipeline, make_column_selector(dtype_include="number")),
        ("categorical", categorical_pipeline, make_column_selector(dtype_exclude="number")),
    ])

    estimators = {
        ("regression", "linear"): LinearRegression(),
        ("regression", "random_forest"): RandomForestRegressor(
            n_estimators=200, random_state=random_seed, n_jobs=-1
        ),
        ("classification", "logistic"): LogisticRegression(
            max_iter=1000, random_state=random_seed
        ),
        ("classification", "random_forest"): RandomForestClassifier(
            n_estimators=200, random_state=random_seed, n_jobs=-1
        ),
    }
    key: Sequence[str] = (task, model)
    if key not in estimators:
        choices = ", ".join(f"{t}/{m}" for t, m in estimators)
        raise ValueError(f"未知 task/model: {task}/{model}；可选: {choices}")
    return Pipeline([("preprocess", preprocessing), ("model", estimators[key])])
