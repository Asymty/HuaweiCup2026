# AGENTS.md

## 项目定位

这是 2026 华为杯研究生数学建模竞赛的共享代码仓库。团队 3 人主要通过各自的 Codex 完成代码工作，因此本文件中的协作规则优先于“直接改完就提交”的默认做法。

详细流程见：`skill/three_codex_workflow.md`。

正式比赛期间，任何 Codex 在接受赛题相关任务前，必须先读取 `skill/competition_orchestrator/SKILL.md`。如果任务涉及论文写作，还必须同时读取 `skill/paper_writing/README.md`。

## 三个 Codex 的核心协作规则

- 不要默认自己独占仓库。始终假设另外两个 Codex 可能正在并行工作。
- 开始任何任务前，先检查 Git 状态并同步 `main`：
  - `git status`
  - `git checkout main`
  - `git pull --ff-only origin main`
- 不要直接在 `main` 上开发。每个任务创建独立短分支，例如：
  - `agent-a/q1-baseline`
  - `agent-b/q2-preprocess`
  - `agent-c/q3-plot`
- 如果用户没有说明当前 Codex 是 A、B、C 中哪一个，且分支命名需要角色信息，只询问一次角色；不要猜。
- 一个分支只处理一个明确任务。不要顺手重构无关文件。
- 尽量避免两个 Codex 同时修改同一个文件。发现目标文件可能正在被其他分支修改时，先报告风险，再继续。
- 禁止 `force push`、`reset --hard`、改写共享提交历史，除非用户明确授权。
- 合并到 `main` 前必须先通过测试，并优先通过 Pull Request 合并。
- 遇到 merge conflict 时，不要自动“全部接受 ours/theirs”；先解释冲突文件、两侧改动和拟采用的合并方案。

## 目录边界

Git 管理：
- `src/`
- `tests/`
- `skill/`
- `main.py`
- `README.md`
- requirements 文件
- 项目级配置与协作说明

默认不进入 Git：
- `data/`
- `result/`
- `figures/`
- `paper/`
- `references/`
- `.venv/`
- `.idea/`

这些内容主要通过 Google Drive 或本地文件协作。不要因为 Git 中看不到它们就删除、重建或覆盖本地对应内容。

## 论文写作 Skill

任何 Codex 在新增或大幅修改论文正文前，必须先读取 `skill/paper_writing/README.md`，再读取当前章节对应指南：模型读 `model_writing.md`，实验读 `experiment_results.md`，摘要读 `abstract.md`，图表读 `figures_tables.md`；所有数值、模型与结论必须来自实际代码、正式结果和当前论文上下文。

## 修改代码前

先阅读与任务直接相关的文件，不要根据文件名猜实现。

在开始修改前明确：
1. 当前任务属于哪一问（Q1/Q2/Q3/Q4）；
2. 输入数据是什么；
3. 预期输出是什么；
4. 评价指标是什么；
5. 当前分支只需要改哪些文件。

信息不足时优先做最小可验证实现，不要凭空补业务假设。

## 代码要求

- 路径使用 `pathlib.Path`，不要写死个人绝对路径。
- 随机过程统一使用项目随机种子。
- 原始数据只读，不覆盖 `data/raw/`。
- 先做简单 baseline，再增加复杂模型。
- 训练、验证、测试必须避免数据泄漏。
- 新增正式模型时，同时补充必要的评价、保存结果和最小测试。
- 不为了“代码更漂亮”进行与当前赛题无关的大重构。

## 完成任务的最低标准

代码修改后至少运行：

```powershell
.\.venv\Scripts\python.exe -m compileall src tests main.py
.\.venv\Scripts\python.exe tests\smoke_test.py
```

若任务涉及具体模型，还需要运行对应最小实验，并报告：
- 使用的数据；
- 参数；
- 指标；
- 输出文件；
- 是否存在异常或警告。

测试失败时不要提交为“已完成”。

## Git 提交流程

任务完成后：

```powershell
git status
git add <本任务相关文件>
git commit -m "<type>: <简短任务说明>"
git push -u origin <当前分支>
```

推荐提交类型：
- `feat:` 新模型/新功能
- `fix:` 修复错误
- `data:` 数据处理逻辑
- `eval:` 评价/验证
- `plot:` 绘图
- `docs:` 文档
- `refactor:` 不改变结果的重构

不要默认执行 `git add .`；多人并行阶段优先精确暂存本任务文件。

## Codex 输出要求

每次较大的任务结束时，用简短清单告诉用户：
- 修改了哪些文件；
- 为什么修改；
- 跑了哪些命令；
- 测试是否通过；
- 当前分支；
- commit hash（如已提交）；
- 是否已经 push；
- 是否存在需要其他 Codex/队员注意的冲突风险。

## AI 使用记录

本项目大量使用 Codex。凡计划进入竞赛最终提交材料的 AI 辅助代码，必须保留可追溯的 AI 使用信息，并按当届官方规则完成披露。不要伪造工具版本、模型名或来源；不确定时先记录“待核实”，并在最终提交前统一检查。
