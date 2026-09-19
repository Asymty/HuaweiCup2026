"""统一设置随机种子。"""
import random

import numpy as np

from src.config import RANDOM_SEED


def set_seed(seed: int = RANDOM_SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)
