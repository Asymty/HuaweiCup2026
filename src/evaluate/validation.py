"""交叉验证工具。"""
from sklearn.model_selection import KFold, StratifiedKFold, cross_validate

from src.config import RANDOM_SEED


def make_cv(task: str, n_splits: int = 5, random_seed: int = RANDOM_SEED):
    """回归返回 KFold，分类返回 StratifiedKFold。"""
    common = {"n_splits": n_splits, "shuffle": True, "random_state": random_seed}
    if task.lower() == "regression":
        return KFold(**common)
    if task.lower() == "classification":
        return StratifiedKFold(**common)
    raise ValueError("task 必须是 regression 或 classification")


def cross_validate_model(model, X, y, task: str, scoring=None, n_splits: int = 5):
    """执行默认 5 折交叉验证并返回 sklearn 结果字典。"""
    return cross_validate(model, X, y, cv=make_cv(task, n_splits), scoring=scoring, return_train_score=False)
