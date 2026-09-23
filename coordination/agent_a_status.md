# Codex A Status

- Current Task: TASK-A-02（`agent-a/task-a-02`）；Phase 1 FULLY ACCEPTED = YES。
- Status: TASK-A-02 = DONE；EVIDENCE SHARED = PASS（设计证据）；候选未实现、未跑官方 evaluator、未选出赢家；MODEL FREEZE = FALSE。
- Completed: TASK-A-01 已合并并正式 ACCEPT。核对 PR #6/#7/#8 实际合并文件、A_MODEL_INTERFACE、B runner/100 图画像、C 合法性与指标审计；复核官方题面 README/config/关键评估代码。更新模型指标与工程边界、P0 风险、证据协议；建立 B/C 的 01E 小型证据交接任务及依赖证据 Gate 的 A/B/C-02 候选任务。不执行 TASK-A-02、不重跑 B/C 第一轮完整任务、不启动正式全量实验。
- Key Findings: 选手只提交 `node_to_subgraph` 与 `core_schedules`；Q1 每子图一 Task，Q2/Q3 每核一 Task；Makespan 为主目标，added_copy_bytes 为逻辑新增 COPY 次指标。Q2 受控同方案 $800\to400$、added COPY $18000\to0$；Q3 受控同方案 $1200\to1124$、hit $6000$ bytes，逻辑 added COPY 不变；16 bytes 命中却 $705\to705$。Q2 spill 抵消、Q3 正式图关键路径收益、优化方案 evaluator 长尾仍未证实。B 的 8 图 pilot、约 1.6 小时 stub 成本估计不可当正式 100 图性能结论；Gate 两例约 49% 也不可外推。
- Outputs: coordination/A_MODEL_INTERFACE.md、MASTER_PLAN.md、TASKS.md、DECISIONS.md、HANDOFF.md；skill/competition_orchestrator/{task_protocol,coordination_protocol,handoff_protocol}.md；shared_evidence/README.md。官方本地 canonical 路径为 `题目/中文题目/A题/official_bundle/`，原始 ZIP 未修改，`题目/` 由本机 `.git/info/exclude` 排除。
- Metrics: A 本机 16 项 A 相关单元测试 PASS（含未修改官方 C 机制套件）；C 受控 legality 8/8 一致，Q2/Q3 对照与 boundary PASS/WARN 如上；B 100 图画像本机可生成，ops 766–38666、median 4223；一次 case_001 Q1 2 核官方 runner 成功且记录哈希。A 未取得 B/C 原有 ignored pilot/validation 全量原始记录，以上仅为抽样复核。
- Blockers: Phase 1 验收无阻断。C 审计脚本直接路径入口问题及大图 evaluator 长尾仍留待下一阶段处理。
- Need Decision: HUMAN DECISION REQUIRED = NO；未切换重大路线、未改变官方目标解释，MODEL FREEZE = FALSE。若后续候选原型需高风险成本显著不同的整体路线，再提交队长决策。
- PR: https://github.com/Asymty/HuaweiCup2026/pull/17（`agent-a/task-a-02` → `main`）；先前 Phase 1 PR 已合并。
- Next Suggestion: B/C 依据 `A_ALGORITHM_DESIGN.md` 分工实施和独立证伪；A 后续只据真实官方结果决定是否采纳或修订路线。B-02 PR #16 另行技术与证据审查，不因本任务自动 ACCEPT。
- Validation: Phase 1 技术审查分支此前的 `compileall src tests main.py`、`tests/smoke_test.py`、16 项 A 单元测试、C 官方模块套件和 B 小图 runner 均 PASS。本次仅核对现有证据和文档，`git diff --check` 与提交范围在提交前复核；未重跑模型实验。

## 2026-09-23 evidence review update

- PR #10/#11 已合并入 main。B L2 六个文件与 manifest 哈希吻合；100 个唯一图、47 条现有 pilot/timeout 记录（其中 24 条两核主记录）和 case_014/034/072 的关键字段与官方图/来源哈希一致。团队 Drive 的 TASK-B-01 目录可访问，case_034 Q2 原始 `run_record.json` 可读取，字段与 L2 对应；TASK-B-01E EVIDENCE SHARED = PASS，TASK-B-01 FORMAL ACCEPTANCE = ACCEPT。
- C L2 五个数据文件与 manifest 的 Git 标准化换行哈希一致；官方脚本/config 哈希及 legality 8/8、Q2 800→400、Q3 1200→1124、16-byte hit 但 705→705 均核对。C 的 L3 声明为 `Google Drive / 04_Results / Phase1 / TASK-C-01 /`，但当前连接的共享 Phase1 目录仅有 TASK-B-01，亦未搜到两份原始文件；TASK-C-01 FORMAL ACCEPTANCE = EVIDENCE_PENDING。
- 本轮只审核既有证据和合并 PR，没有重跑 B/C 第一轮实验；原先技术复核结果保持有效。B 的成本估计仍仅适用于 bounded official stub，C 的受控例不代表 100 图总体收益。

## 2026-09-23 final evidence gate update

- C 已把原有两份 L3 文件同步至与 B 同一共享 Phase1 目录：`Google Drive / 04_Results / Phase1 / TASK-C-01 /`。A 从该目录读取 `official_validation_evidence.json`（15,543 bytes，SHA-256 `a26d60a75f4bd05ce4c2c96f563ab509a16d60aca4cee4f43df0a997b49e2641`）和 `TASK-C-01_REPORT.md`（2,994 bytes，SHA-256 `d01214c86f6cf95b05302514d62831fb6859138829065ed740c95100cc14d8f1`），两者与修正 manifest 一致。
- 由于 PR #11 在路径校正提交前已经合并，校正提交 `abfd3b9` 由后续 PR #13 合并。TASK-C-01E EVIDENCE SHARED = PASS，TASK-C-01 FORMAL ACCEPTANCE = ACCEPT。TASK-A/B/C-01 均 ACCEPT，PHASE 1 FULLY ACCEPTED = YES。
- 保留 Q2 spill 抵消、Q3 正式图关键路径收益、优化方案大图 evaluator runtime 等后续风险；不将受控例或 Gate 抽样外推为总体成绩。不重跑 B/C 第一轮实验，不启动 A/B/C-02，不冻结模型。

## TASK-A-02 算法原型规范交接（2026-09-23）

- 完成：`coordination/A_ALGORITHM_DESIGN.md` 定义有界拓扑分块与通信亲和相邻合并两条确定性路线；统一内部 PlanSpec 与恰好两字段的官方方案边界；Q1 Task/搬运、Q2 驻留与 spill、Q3 FIFO/关键路径代理及失效条件；合法性维护、复杂度、Pareto 比较、停止条件和最多 2 图×2–5 核的分阶段 pilot。未实现候选生成器、未调用 evaluator，`official_evaluator_calls = 0`。
- L2：`shared_evidence/phase2/task_a_02/README.md`、`review_matrix.json`、`evidence_manifest.json`；manifest 记录 20 份只读/已合并来源和 3 份 L2 文件的 SHA-256，CRLF/LF 文本规范化口径明确。L3 = not_applicable，因为本任务仅有文档，无大型原始结果。EVIDENCE SHARED = PASS（设计证据）。
- 验证：20 个来源哈希、3 个 L2 哈希、JSON、章节与 $2\times4\times3\times3=72$ 官方调用上限算式检查 PASS；`compileall src tests main.py`、`tests/smoke_test.py` PASS；`git diff --check` 与提交文件范围在提交前复核。受控 Q2/Q3 数值仅引自 C-01，八图 runtime 仅引自 B-01，均未外推。
- 风险：静态拓扑区间不保证 Step2/3 与全局执行合法；0.8/1.25/32/64 等为未调优参数；Q2 spill 抵消、Q3 命中无时延收益和优化方案 evaluator 长尾仍待真实结果。MODEL FREEZE = FALSE，无人类强制决策项。
