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

## HANDOFF-004

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

## HANDOFF-005

- From: Codex A
- To: Codex B; Codex C; human captain
- Task: Phase 1 总验收与 Evidence Handoff 编排
- Status: PHASE 1 REVIEW = PASS（技术链路）；PHASE 1 FULLY ACCEPTED = NO；TASK-A-01 = ACCEPT；TASK-B-01/C-01 = ACCEPT PENDING EVIDENCE HANDOFF。
- What Changed: A 根据已合并代码、官方程序和小规模抽查细化模型指标与风险；建立 L1/L2/L3 证据协议；创建即时 TASK-B-01E/C-01E 与依赖 Evidence Gate 的 A/B/C-02 候选任务。
- Files: coordination/A_MODEL_INTERFACE.md、MASTER_PLAN.md、TASKS.md、DECISIONS.md、agent_a_status.md、HANDOFF.md；skill/competition_orchestrator/{task_protocol,coordination_protocol,handoff_protocol}.md；shared_evidence/README.md。
- Key Results: Q2/Q3 的受控机制可真实生效，但不是 100 图总体收益。逻辑 added_copy_bytes 与 Q3 命中后的物理 DDR 诊断量分开；B 的 8 图 stub pilot 与正式优化运行成本分开。A/B/C-02 尚未启动。
- Evidence: PR #6/#7/#8 已合并；A 本机 16 项测试、C 官方受控套件、B 100 图画像及一次 case_001 Q1 runner 抽查 PASS。B/C 原有 ignored `result/**` 未随 Git 交接，故 L2/L3 证据仍待 Owner 整理。即时任务卡与字段见 TASKS.md 的 TASK-B-01E/C-01E。
- Warnings: 不为制作证据包重跑第一轮实验；不得把 `Status: DONE` 当正式 ACCEPT、把 C 受控图或 Gate 约 49% 当总体结论。C 审计脚本应使用模块入口，直接文件路径入口待后续修复。官方原始 ZIP 只读，`题目/中文题目/A题/official_bundle/` 是本地 canonical 解压副本，整个 `题目/` 不入 Git。
- Open Questions: B/C L2 manifest 与必要 L3 原始位置是否能完成哈希核对；正式图上 Q2 spill 抵消及 Q3 关键路径收益；优化方案的大图 evaluator 分布。
- Recommended Next Action: B/C 各自从最新 main 建独立分支执行且仅执行 01E，提交小型证据包、push、开 PR 后停止；A 后续有限抽查并更新正式验收，再按 Gate 决定是否启动 A/B/C-02。
- PR: 本总控 `agent-a/phase1-review` → main 待创建；不自动 merge。

## HANDOFF-006

- From: Codex B
- To: Codex A; Codex C (read-only metric review)
- Task: TASK-B-01E
- Status: DONE; EVIDENCE SHARED = PASS; formal TASK-B-01 ACCEPT belongs to A.
- What Changed: Extracted a portable L2 evidence package from existing TASK-B-01 results and copied only selected existing raw evidence into the team Google Drive L3 folder. No profiler, plan generator, evaluator, singlecore or parallel experiment was rerun.
- Files: `shared_evidence/phase1/task_b_01/` (`graph_profile_summary.csv`, `pilot_summary.csv`, `key_cases.json`, `README.md`, `evidence_manifest.json`, `build_evidence.py`); `coordination/agent_b_status.md`; this appended handoff. No A/C/runner/model/official files changed.
- Key Results: 100 unique profile rows; 47 existing success/timeout run rows over eight cases, including 24 primary two-core Q1/Q2/Q3 rows. case_014 and case_072 singlecore results remain censored at 90 seconds. The 1.6-hour central and 1.1–3.5-hour range remain bounded-stub-plan cost estimates, not formal scores.
- Evidence: L2 manifest `shared_evidence/phase1/task_b_01/evidence_manifest.json` lists all source, official script/config and L2 SHA-256; 27 selected raw L3 files totaling 75,835,567 bytes were read back and hash-checked. L3 actual path: `G:\.shortcut-targets-by-id\1A2sgFCDpS1YiCptPPK52xN8mek3fY5C5\HuaweiCup2026\04_Results\Phase1\TASK-B-01\`; logical team location: `Google Drive / 04_Results / Phase1 / TASK-B-01 /`. Validation commands and extraction parameters are in the L2 README and manifest.
- Warnings: L2 excludes large Trace/stdout and official attachments. This machine lacks the separately named canonical `题目/中文题目/A题/official_bundle/` path; the pre-existing result-bundle fixed config and five official scripts matched the original read-only ZIP byte-for-byte, with hashes in the manifest. Long-tail concurrency beyond small/medium cases was never measured.
- Open Questions: A to check selected raw L3 records against the L2 manifest and canonical official package, then decide formal TASK-B-01 acceptance. Large singlecore Makespans remain unknown.
- Recommended Next Action: A perform a finite independent evidence sample and update `TASKS.md`/formal acceptance; C may read the metric rows and official hashes. Do not start TASK-B-02 until the Evidence Gate is met and separately authorized.
- PR: https://github.com/Asymty/HuaweiCup2026/pull/10, `agent-b/task-b-01e` → `main`; do not auto-merge.
## HANDOFF-007

- From: Codex A
- To: Codex B; Codex C; human captain
- Task: Phase 1 evidence review after TASK-B-01E/C-01E
- Status: TASK-B-01 = ACCEPT; TASK-C-01 = EVIDENCE_PENDING; PHASE 1 FULLY ACCEPTED = NO.
- Evidence: PR #10/#11 merged; B L2 100 profiles, 47 pilot rows, case_014/034/072 and official hashes checked; B L3 TASK-B-01 folder and case_034 Q2 raw runner record accessible. C L2 manifest/hashes, 8/8 legality, Q2/Q3 pairs and 16-byte boundary checked; C L3 raw folder/files not visible in the shared Drive Phase1 directory.
- Next Action: C supplies an accessible TASK-C-01 L3 link or syncs the two existing raw files; A performs finite hash/sample verification. Do not rerun TASK-C-01, start A/B/C-02, or freeze the model before the remaining Gate passes.

## HANDOFF-A02

- From: Codex A
- To: Codex B; Codex C
- Task: TASK-A-02
- Status: DONE; EVIDENCE SHARED = PASS for design evidence; candidate plans and official evaluations = 0.
- What Changed: Specified two bounded, deterministic partition/assignment routes and a unified PlanSpec; defined Q1/Q2/Q3 proxies, legality gates, paired comparisons, call/time budgets and stop rules. No official source, B/C runner, model implementation, result or paper file changed.
- Files: `coordination/A_ALGORITHM_DESIGN.md`, `coordination/agent_a_status.md`, A-owned TASKS status, `shared_evidence/phase2/task_a_02/` and this handoff.
- Key Results: Bounded topological blocks and communication-affinity adjacent merges remain competing untested routes. Initial pilot design is 18 official calls; absolute ceiling is 72 over at most two graphs and N=2–5, subject to a stricter overall wall-time stop. No winner or formal score is claimed.
- Evidence: `shared_evidence/phase2/task_a_02/evidence_manifest.json`, `README.md` and `review_matrix.json`; 20 source hashes and 3 L2 hashes verified; L3 = not_applicable (documentation-only task). `compileall`, smoke test, JSON/hash checks and `git diff --check` passed.
- Warnings: Static construction is not a substitute for official Step2/3 and global-cycle checks. Memory/FIFO proxies are uncalibrated; C-01 controlled results and B-01 random-stub runtime are not optimized-plan aggregate evidence.
- Open Questions: Which route produces legal, budget-feasible plans with better official Makespan and acceptable logical COPY? How often do Q2 spill and Q3 noncritical Cache hits erase predicted gains?
- Recommended Next Action: B/C use this specification to plan later implementation and independent falsification after their own TASK-B/C-02 handoffs. A reviews their evidence before any route choice. Do not start a full 100-graph experiment or freeze the model from this document.
- PR: https://github.com/Asymty/HuaweiCup2026/pull/17（`agent-a/task-a-02` → `main`）。

## HANDOFF-008

- From: Codex A
- To: Codex B; Codex C; human captain
- Task: Phase 1 final evidence acceptance
- Status: TASK-A/B/C-01 = ACCEPT; TASK-B/C-01E EVIDENCE SHARED = PASS; PHASE 1 FULLY ACCEPTED = YES; MODEL FREEZE = FALSE.
- Evidence: PR #13 merged C's corrected shared Drive path. A read both raw C files under the same shared Phase1 parent as B and independently matched sizes and SHA-256 to `shared_evidence/phase1/task_c_01/evidence_manifest.json`; earlier L2 legality and Q2/Q3 controlled values had passed. B's L2/L3 review was recorded in HANDOFF-007.
- Remaining Risks: Q2 spill offset, Q3 critical-path benefit on formal graphs, optimized-plan evaluator long tails, and direct-path C audit CLI behavior. Controlled examples and Gate samples are not aggregate results.
- Next Action: A/B/C-02 task dependencies are satisfied. No Phase 2 task, full experiment, paper writing or model freeze was started by this acceptance update.
