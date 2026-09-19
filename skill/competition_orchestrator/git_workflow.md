# Git 工作流

队员无需手写 Git 命令，由 Codex 执行并报告：

`main → pull --ff-only → task branch → work → test → commit → push → PR → merge → next task`

建议分支：

- `agent-a/q1-model-formulation`
- `agent-b/q1-baseline`
- `agent-c/q1-validation`
- `docs/q1-paper-section`

一个 TASK 通常对应一个短分支和一个 PR。禁止直接提交 main、force push、`reset --hard`、改写共享历史或长期共用功能分支。冲突必须解释两侧改动后人工合并，不能整文件选择 ours/theirs。
