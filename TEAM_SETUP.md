# TEAM_SETUP.md

## 适用场景

本仓库由 3 名队员协作，每个人主要通过自己的 Codex 完成代码与 Git 操作。队员不需要手工掌握复杂 Git 命令，但必须让 Codex 遵守仓库根目录的 `AGENTS.md`。

## 第一次接入

### 1. 接受 GitHub 仓库邀请

仓库：

`https://github.com/Asymty/HuaweiCup2026`

仓库为 Private。只有接受邀请后才能 clone/pull/push。

### 2. 每个人使用独立本地目录

推荐：

- 队员 A：`D:\Coding\HuaweiCup2026-A`
- 队员 B：`D:\Coding\HuaweiCup2026-B`
- 队员 C：`D:\Coding\HuaweiCup2026-C`

不要三个人共用同一个本地目录，也不要把 Git 仓库放进 Google Drive 同步目录。

### 3. 第一次让 Codex 完成初始化

把下面内容发给自己的 Codex：

```text
这是 2026 华为杯团队共享代码仓库。

我的角色是：Codex A / Codex B / Codex C（按实际填写）。

仓库：
https://github.com/Asymty/HuaweiCup2026.git

请先读取仓库根目录 AGENTS.md 和 skill/three_codex_workflow.md，并严格遵守。

我是不会手工处理 Git 的队员，请你负责：
1. 检查本机 Git 和 Python 是否可用；
2. 如果本地还没有项目，则 clone Private 仓库；
3. 创建项目自己的 .venv；
4. 安装 requirements.txt；
5. 运行 smoke test；
6. 确认 main 与 origin/main 一致；
7. 不修改任何业务代码；
8. 完成后报告当前路径、Python 解释器、分支、HEAD commit、测试结果。

禁止：
- force push
- reset --hard
- 修改共享历史
- 删除远程分支
- 在 main 上直接开发
```

## 每次正式做题前

所有 Codex 都先执行：

```powershell
git status
git checkout main
git pull --ff-only origin main
```

然后为当前任务创建独立分支。

示例：

- `agent-a/q1-model`
- `agent-b/q1-data`
- `agent-c/q1-evaluation`

## 赛题出来后的推荐三路并行

### Codex A：建模主线

主要负责：
- 题意数学化；
- 变量、假设、约束；
- baseline 数学模型；
- 主模型；
- 算法实现。

### Codex B：数据与实验

主要负责：
- 数据读取；
- 清洗；
- EDA；
- baseline 跑通；
- 批量实验；
- 结果表格。

### Codex C：验证与论文图表

主要负责：
- 评价指标；
- 交叉验证；
- 敏感性/稳健性；
- 对比实验；
- 正式绘图；
- 结果核查。

如果某一问工作量不同，可以临时调整。核心原则是尽量避免多个 Codex 同时修改同一文件。

## 每个任务结束时

要求 Codex 输出：

- 当前分支；
- 修改文件；
- 测试命令；
- 测试结果；
- commit hash；
- 是否 push；
- 是否创建 PR；
- 是否存在冲突风险。

## Google Drive 与 GitHub 的职责

GitHub：
- Python 代码；
- tests；
- skill；
- README / AGENTS；
- 配置与协作说明。

Google Drive：
- 官方题目；
- 大体积数据；
- 实验结果；
- 正式图片；
- 参考资料；
- 论文；
- 最终提交文件。

不要把 .git 放进 Google Drive。

## 比赛期间的最低规则

1. main 必须尽量保持可运行。
2. 每一问先 baseline，再升级。
3. 用于论文的关键结果必须能追溯到 commit。
4. 任何冲突都先让 Codex解释，再处理。
5. 三个 Codex 的输出必须由团队统一核对，不能直接拼接。
