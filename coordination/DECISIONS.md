# DECISIONS

## DECISION-001：正式锁定 A 题

- Time: 2026-09-23 09:23 Asia/Shanghai
- Decision: 人类队长确认 FINAL PROBLEM = A（通用神经网络处理器下的多核调度问题）。选题阶段结束，进入 PHASE 1: Problem Formalization。MODEL FREEZE = FALSE。
- Reason: A 题给出固定的方案格式、100 个正式计算图、三问官方评估器和单核参照入口。可先构造合法方案，再以官方 Makespan 与辅助指标衡量改进；三问共用切图与调度接口，场景机制逐步扩展。最终选题决定由人类队长作出，不由 Codex 的 Gate 自动替代。
- Evidence:
  1. Codex A/B/C 独立审查均将 A 保留为主要候选。B 的审查确认题包含 100 图和三问评估器；C 的审查把评估器可运行及合法基线列为前提。证据：D:/Downloads/Codex B 习题分析.md、D:/Downloads/Codex C 习题分析.md，以及 Codex A 先前选题审查。
  2. A 题 Q1/Q2/Q3 官方评估器在 case_001 与 case_019 上均成功运行，最小合法 baseline 被全部三问接受。证据：result/a_feasibility_gate/GATE_REPORT.md 与 runs/<case>/<plan>/problem_<n>/run_record.json。
  3. 两个结构不同的测试图上，轻量改进使官方 Makespan 分别下降约 49.87%（case_001）和 49.00%（case_019）。这些只是 Gate 抽样，不是正式总体成绩。
  4. Q1 的跨 Task DDR、Q2 的同核 Task 合并与复用、Q3 的共享只读 L2 形成递进关系；三 Codex 可按建模、运行、独立验证并行工作。
  5. 最大图 case_014 的大 Task 方案在 300 秒内未完成；官方小子图示例方案 Q1 在 34.40 秒完成，但质量差。此证据支持可运行性，也明确暴露计算长尾。
- Warnings:
  1. 不得将两个 Gate 样例约 49% 的改善外推到全部 100 图，或写成正式论文结论。
  2. Q2 的 Task 合并与同核 L1/UB 复用是否带来独立收益，尚未验证。
  3. Q3 有 Cache 命中记录，但 L2 对 Makespan 或搬运的独立效用尚未验证。
  4. 最大图存在明显 evaluator 长尾；最大图 Q2/Q3 成本仍未实测。
  5. 正式全量结果须覆盖全部 100 图、2–5 核，并采用官方单核参照与固定配置。
- Alternatives Rejected: D、E 保留为此前备选，但队长已正式选择 A；本阶段不重新比较 A–F。
- Affected Tasks: TASK-A-01、TASK-B-01、TASK-C-01。三任务均可从官方题面、附件、固定配置和本决策同时启动。
