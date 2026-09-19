"""通用、保守的数据清洗函数。"""
import numpy as np
import pandas as pd


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates().copy()


def replace_inf_with_nan(df: pd.DataFrame) -> pd.DataFrame:
    return df.replace([np.inf, -np.inf], np.nan)


def high_missing_columns(df: pd.DataFrame, threshold: float = 0.5) -> pd.Series:
    """返回缺失率大于等于阈值的列及其缺失率。"""
    if not 0 <= threshold <= 1:
        raise ValueError("threshold 必须位于 [0, 1]")
    rates = df.isna().mean()
    return rates[rates >= threshold].sort_values(ascending=False)


def fill_numeric_median(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    columns = result.select_dtypes(include="number").columns
    result[columns] = result[columns].fillna(result[columns].median())
    return result


def clean_data(df: pd.DataFrame, fill_numeric: bool = True) -> pd.DataFrame:
    """去重、将无穷值转为空值，并可选地用中位数填补数值缺失。"""
    result = replace_inf_with_nan(remove_duplicates(df))
    return fill_numeric_median(result) if fill_numeric else result
