"""简单计时上下文管理器。"""
from contextlib import contextmanager
from time import perf_counter


@contextmanager
def timer(label: str = "elapsed"):
    start = perf_counter()
    try:
        yield
    finally:
        print(f"{label}: {perf_counter() - start:.3f}s")
