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
- From: Codex B
- To: Codex A; Codex C
- Task: TASK-B-01
- Status: DONE, pending review
- What Changed: Added 100-graph profile and a reproducible, isolated runner for the unchanged official singlecore/Q1/Q2/Q3 CLIs; completed stratified pilot and bounded concurrent-case check.
- Files: `src/preprocess/a_graph_profile.py`; `src/evaluate/a_official_runner.py`; `tests/test_a_official_runner.py`; `coordination/agent_b_status.md`; ignored evidence under `result/a_graph_profile/` and `result/a_formal_runs/`.
- Key Results: 8 stratified cases × Q1/Q2/Q3 at 2 cores all completed. case_014 2-core evaluator wall seconds Q1/Q2/Q3 = 36.58/56.40/56.65; case_034 = 2.19/1.66/1.78. Official singlecore for case_014 and case_072 timed out at 90 s. Suggested bounded-subgraph timeout 120 s; separate large-Task/singlecore cap 600 s is provisional. Interpolated full 1,200-run cost ~1.6 h one worker, plausible 1.1–3.5 h for the official stub plan only.
- Evidence: `result/a_graph_profile/profile.csv`; `result/a_formal_runs/pilot_summary.csv`; per-run `run_record.json` and raw official outputs. Reproduction command and detailed method in `coordination/agent_b_status.md`. `python -m unittest discover -s tests -p test_a_official_runner.py -v`, `python -m compileall src tests main.py`, and `python tests/smoke_test.py` passed.
- Warnings: Pilot scores are not formal 100-case results. Official stub is a legal format example, not an optimized baseline. Large singlecore Makespans remain unknown; 600 s limit has not yet been tested. Concurrency tested only on two small/medium cases.
- Open Questions: How should formal plans constrain Task/subgraph size to avoid evaluator long tails? What singlecore timeout and worker memory budget should formal runs use?
- Recommended Next Action: A review cost and Task-size evidence before selecting a formal run policy; C audit metric semantics and paired Q2/Q3 interpretation. Do not start TASK-B-02 from this handoff.
- PR: https://github.com/Asymty/HuaweiCup2026/pull/8
