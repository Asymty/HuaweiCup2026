# 三个 Codex 并行协作流程

## 目标

团队 3 人都可以不会手写代码，但每个人都使用自己的 Codex。协作方式不是“3 个 Codex 同时改 main”，而是：

```text
Codex A ── 独立分支 ──┐
Codex B ── 独立分支 ──┼─> Pull Request / 审核 ─> main
Codex C ── 独立分支 ──┘
```

`main` 始终尽量保持可运行。

## 每个队员第一次使用

在自己的电脑上 clone 仓库，不要三个人共享同一个本地工作目录。

然后创建自己的 Python 虚拟环境并安装核心依赖。

数据、论文、图片、结果和参考资料主要从团队 Google Drive 获取；GitHub 只负责代码及代码相关说明。

## 每次开始任务

把下面的意图直接告诉 Codex：

```text
你是本次任务的 Codex A/B/C。
先读取根目录 AGENTS.md。
本次只负责：<具体任务>。
对应问题：Q1/Q2/Q3/Q4。
不要直接修改 main。
先同步 main，再创建独立分支。
```

Codex 应执行：

```powershell
git status
git checkout main
git pull --ff-only origin main
git checkout -b agent-a/q1-example
```

把 `agent-a` 换成自己的角色，把后半段换成任务名。

## 推荐三路分工

赛题确定后再细化，但默认可按以下思路分：

- Codex A：题意拆解、数学模型、核心算法、公式到代码。
- Codex B：数据清洗、EDA、baseline、实验执行、结果汇总。
- Codex C：评价验证、敏感性/稳健性、绘图、论文所需表格与可复现检查。

这不是永久绑定。某一问需要两个人时，拆成不同文件或不同子任务，不要让两个 Codex 同时改同一段代码。

## 最重要的冲突避免规则

### 情况 1：两个人都要改同一个文件

不要直接同时改。

优先拆分：
- 把新模型放不同模块；
- 把评价逻辑放 `src/evaluate/`；
- 把绘图放 `src/plot/`；
- 让其中一个 PR 先合并，另一个再同步 main 后继续。

### 情况 2：发现 main 更新了

当前分支尚未 push 时，不要擅自重写历史。

让 Codex先：
1. 保存当前工作；
2. 检查差异；
3. 根据情况 commit；
4. 再决定 merge/rebase。

不熟悉 Git 的队员不要自己猜命令，让 Codex先解释风险再执行。

### 情况 3：merge conflict

把完整冲突交给 Codex处理，但要求它先输出：
- 哪些文件冲突；
- ours 改了什么；
- theirs 改了什么；
- 准备如何合并；
- 会不会改变实验结果。

确认逻辑后再解决冲突并重新测试。

## 一个标准任务的完整流程

```text
用户给任务
  ↓
Codex 读取 AGENTS.md
  ↓
同步 main
  ↓
创建独立 branch
  ↓
阅读相关代码
  ↓
做最小实现
  ↓
运行测试/实验
  ↓
检查 git diff
  ↓
只暂存本任务文件
  ↓
commit
  ↓
push 分支
  ↓
创建 PR
  ↓
另一个人/Codex 做快速审查
  ↓
合并 main
```

## 给不会 Git 的队员的固定提示词

直接复制：

```text
先读取项目根目录 AGENTS.md，并严格遵守。

我是 Codex A/B/C（按实际填写）。
本次任务：<填写任务>。

你负责完整处理 Git 操作，我不会手工解决 Git 问题。

要求：
1. 先检查 git status。
2. 切回 main 并执行 git pull --ff-only origin main。
3. 不要直接在 main 开发。
4. 为本任务创建独立分支。
5. 只修改完成本任务所必须的文件。
6. 修改后运行项目要求的测试。
7. 测试通过后检查 git diff。
8. 只 add 本任务相关文件，不要无脑 git add .。
9. commit 后 push 当前分支。
10. 最后告诉我当前分支、commit hash、测试结果，以及下一步是否应该创建 PR。

禁止 force push、reset --hard、删除他人分支或改写共享历史。
遇到冲突先解释，不要自行粗暴覆盖。
```

## 合并后的动作

PR 合并后，每个人下一次任务开始前都要：

```powershell
git checkout main
git pull --ff-only origin main
```

旧任务分支不继续拿来做新任务；新任务重新创建短分支。

## 比赛期间的原则

- 每一问先 baseline，确认能跑，再升级。
- 一个成功可复现的简单模型，比三个跑不通的复杂模型更有价值。
- 正式结果必须能追溯到代码 commit。
- 任何用于论文的关键数字，都记录数据版本、参数和 commit。
- 三个 Codex 可以并行，但最终结果必须由团队共同检查，而不是把三个模型输出直接拼在一起。
