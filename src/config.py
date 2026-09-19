"""项目级配置：路径与随机种子统一从这里读取。"""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"
RESULT_DIR = PROJECT_ROOT / "result"
FIGURES_DIR = PROJECT_ROOT / "figures"
DRAFT_FIGURES_DIR = FIGURES_DIR / "draft"
FINAL_FIGURES_DIR = FIGURES_DIR / "final"

RANDOM_SEED = 2026


def ensure_output_dirs() -> None:
    """创建程序可能写入的输出目录，不改动其中已有内容。"""
    for path in (PROCESSED_DATA_DIR, RESULT_DIR, DRAFT_FIGURES_DIR, FINAL_FIGURES_DIR):
        path.mkdir(parents=True, exist_ok=True)
