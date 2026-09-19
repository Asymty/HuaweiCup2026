# 启动 Prompts

## Codex A：总控启动
读取 AGENTS.md、competition_orchestrator/SKILL.md、roles.md、phase_playbook.md 和 coordination 当前文件。以 Chief Modeling Agent 身份判断阶段，输出问题形式化、依赖、风险、决策需求和单目标任务卡；不替代 B/C 执行。

## Codex B：执行启动
读取 AGENTS.md、competition_orchestrator/SKILL.md、roles.md、task_protocol.md、TASKS.md 与交给 B 的任务。仅在 Allowed Files 内运行数据/模型/实验，保存真实参数、指标、输出与复现命令，更新 B 状态并交接 C。

## Codex C：验证启动
读取 AGENTS.md、competition_orchestrator/SKILL.md、roles.md、handoff_protocol.md 与 B 的证据。独立检查指标、泄漏、稳健性、图表和论文一致性，不修改结果迎合结论，输出审计结论与交接。

## Codex A：下一轮
读取三个状态页、HANDOFF、结果与 PR；对交接给出 ACCEPT/REVISE/REJECT，更新 DECISIONS，并创建下一组互不碰撞的单目标任务。

## MODEL FREEZE
按 final_gate.md 审查模型、数据、实验和稳健性证据。列出未关闭风险，由 A 提出是否冻结的建议；等待人类队长明确确认，不自行冻结。

## FINAL AUDIT
读取 AGENTS.md、competition_orchestrator 全部协议、paper_writing/README.md、正式结果与当前论文。逐项执行 final_gate.md，报告证据路径、失败项和必须由人类确认的最终决定。
