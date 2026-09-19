# 2026 华为杯研究生数学建模

用于 2026 年“华为杯”中国研究生数学建模竞赛的本地 Python 工程，适配 Codex、PyCharm 与 Git。

## 目录职责

```text
data/raw/          原始数据（只读，不直接修改）
data/processed/    清洗、转换后的中间数据
data/external/     外部补充数据及其来源说明
src/               预处理、模型、评价、绘图和通用工具
tests/             最小可运行测试
result/Q1..Q4/     各问数值结果与表格
figures/draft/     探索阶段图片
figures/final/     论文正式图片
paper/             模板、工作稿、备份及现有 LaTeX 工程
references/        现有参考资料（原位保留）
skill/             竞赛协作提示模板
```

## 推荐流程

```text
data/raw → preprocess → eda → baseline → main model → evaluate → plot → result
```

原始数据只读：不要覆盖 `data/raw/` 中的文件，清洗产物写入 `data/processed/`。随机过程统一使用 `src/config.py` 中的 `RANDOM_SEED`；结果、参数和图表应保存到对应目录，以保证实验可复现。

## 常用命令

```powershell
python -m pip install -r requirements.txt
python main.py --mode eda --input data/raw/example.csv
python main.py --mode baseline --input data/processed/example_clean.csv --target y --task regression --model linear
python tests/smoke_test.py
python -m compileall .
```

分类基线可使用 `--task classification --model logistic`，回归或分类也可使用 `--model random_forest`。正式主模型在 `src/model/main_model.py` 中按赛题实现。

## 开发约定

- 路径使用 `pathlib.Path`，不写死本机绝对路径。
- 原始数据、处理中间文件、草图、工作稿和实验结果默认不提交 Git。
- `paper/Latex/` 与 `references/` 是整理前已有内容，未自动迁移或改写。
