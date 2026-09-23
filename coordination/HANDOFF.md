# HANDOFF

## HANDOFF-001
- From: Codex A
- To: Codex B
- Task: TASK-A-01
- Status: DONE；接收确认待 B 填写
- What Changed: 建立三问统一数学符号、合法方案 JSON、Q1/Q2/Q3 官方执行差异、资源约束、结果指标和可落地的运行接口。
- Files: coordination/A_MODEL_INTERFACE.md；coordination/agent_a_status.md；coordination/TASKS.md。
- Key Results: 可提交方案始终只有 node_to_subgraph 与 core_schedules；Q1 每子图一 Task，Q2/Q3 每核一 Task；新增 COPY/spill、核内调度和 Cache 状态由官方评估器派生。官方最小图三问均返回 Makespan 6、added_copy_bytes 0，属于接口检查而非正式性能结果。
- Evidence: A_MODEL_INTERFACE.md 第 1–7、9 节；官方题包 README.md、config.txt、problem_1/2/3.py；已运行 .\.venv\Scripts\python.exe -m compileall src tests main.py 和 .\.venv\Scripts\python.exe tests\smoke_test.py，均 PASS；官方最小图三个未修改评估函数均 PASS。
- Warnings: Gate 两例约 49% 收益不得外推；Q2 同核复用与 Q3 L2 独立收益尚未证实；最大图有评估长尾。严禁把 Step3 local_makespan 或示例随机方案当正式评分/性能 baseline。
- Open Questions: 100 图中是否含直接 Op→Op 边；大 Task 运行时间与哪些结构特征相关；同一方案 Q1/Q2/Q3 分别在哪些图上出现机制差异。
- Recommended Next Action: 按 TASK-B-01 实现只读官方图解析、严格两字段方案的 runner、单核参照、结果与哈希记录；先做包含 case_014/case_034 的分层 pilot，不盲跑全量；给 C 保留同方案成对比较入口。若接口解释与官方代码不一致，保存最小复现实例并回报 A。
- PR: agent-a/task-a-01 → main，待网络恢复后推送与创建；不自动 merge。

## HANDOFF-002

- From: Codex A
- To: Codex C
- Task: TASK-A-01
- Status: DONE；接收确认待 C 填写
- What Changed: 明确可提交变量与官方派生状态的边界，并分别给出 Q1 Task 边界、Q2 同核复用、Q3 完整 tensor FIFO Cache 的可证伪命题。
- Files: coordination/A_MODEL_INTERFACE.md；coordination/agent_a_status.md；coordination/TASKS.md。
- Key Results: Q2/Q3 不增加方案 JSON 字段；Q3 只对 COPY_IN 按逻辑 tensor id 查询，命中不刷新 FIFO，hit_rate 按字节计算。Cache hit > 0 不推出 Makespan 降低，也不保证 added_copy_bytes 改变。
- Evidence: A_MODEL_INTERFACE.md 第 2、5、6、8、9 节；官方 derive_multicore_plan、problem_2.py、problem_3.py 与技术说明；官方最小图三问均 Makespan 6、added_copy_bytes 0；模型文档 JSON/标题/LaTeX 块检查 PASS。
- Warnings: 题面写二部图，官方代码可处理直接 Op→Op；需要独立复核正式图实际情况。Q2 容量不足可触发 spill，不应直接将原始工作集超容量判为非法。Q3 超出 Cache 容量的正字节 COPY_IN 仍会计入未命中统计。
- Open Questions: Q2 同核驻留是否带来净效益；Q3 L2 命中何时影响关键路径；哪些风险需要 A 修订模型接口。
- Recommended Next Action: 按 TASK-C-01 设计缺失 op、重复 sgid、子图/组合执行环等负例；使用同图同核同方案的 Q1/Q2 与 Q2/Q3 成对测试，报告 PASS/WARN/FAIL 和证据路径。若发现差异，先独立复核再反馈 A，不直接改模型主线。
- PR: agent-a/task-a-01 → main，待网络恢复后推送与创建；不自动 merge。

## HANDOFF-003

- From: Codex C
- To: Codex A; Codex B
- Task: TASK-C-01
- Status: DONE
- What Changed: Added independent legality and metric audit modules, negative/positive tests, and controlled official Q1/Q2/Q3 mechanism comparisons.
- Files: src/evaluate/a_legality.py; src/evaluate/a_metric_audit.py; tests/test_a_legality.py; tests/test_a_metric_audit.py; coordination/agent_c_status.md; coordination/HANDOFF.md. Local gitignored evidence is under result/a_validation/.
- Key Results: LEGALITY=PASS; METRIC AUDIT=PASS; Q2 MECHANISM=PASS; Q3 L2 MECHANISM=PASS; Q3 boundary=WARN. Q2 controlled pair: Makespan 800->400, scheduled COPY 30000->12000, and added COPY 18000->0. Q3 same-plan pair: Makespan 1200->1124, hit_bytes=6000, byte hit rate=1/3, physical DDR 30000->24000, while added_copy_bytes remains 18000. A 16-byte hit case has Makespan 705->705, demonstrating that Cache hit > 0 does not imply lower Makespan.
- Evidence: result/a_validation/official_validation_evidence.json; result/a_validation/TASK-C-01_REPORT.md; run `python tests/test_a_legality.py` and set A_OFFICIAL_ROOT before `python tests/test_a_metric_audit.py`.
- Warnings: Controlled synthetic cases prove mechanisms, not performance over 100 official graphs. Q2 merge can be negated by L1/UB pressure and spill. Q3 hit rate is byte-weighted and does not itself prove lower Makespan. Official added_copy_bytes is logical scheduled COPY traffic, not physical DDR bytes, and does not subtract Cache hit bytes.
- Open Questions: Which formal cases exhibit positive Q3 hit bytes without latency benefit, and how often do Q2 merges trigger spill that offsets saved boundary COPY?
- Recommended Next Action: A reviews and updates TASK-C-01 in TASKS.md; B records all fields listed in agent_c_status.md and retains same-plan Q2/Q3 pairs.
- PR: https://github.com/Asymty/HuaweiCup2026/pull/7 — agent-c/task-c-01 -> main; do not auto-merge.
