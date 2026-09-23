# Codex A Status

- Current Task: Phase 1 Evidence Handoff 复核（`agent-a/phase1-evidence-review`）；TASK-A-02 未启动。
- Status: Phase 1 技术审查 PASS；TASK-B-01 正式 ACCEPT；TASK-C-01 EVIDENCE_PENDING（L3 未定位）；Phase 1 FULLY ACCEPTED = NO。
- Completed: TASK-A-01 已合并并正式 ACCEPT。核对 PR #6/#7/#8 实际合并文件、A_MODEL_INTERFACE、B runner/100 图画像、C 合法性与指标审计；复核官方题面 README/config/关键评估代码。更新模型指标与工程边界、P0 风险、证据协议；建立 B/C 的 01E 小型证据交接任务及依赖证据 Gate 的 A/B/C-02 候选任务。不执行 TASK-A-02、不重跑 B/C 第一轮完整任务、不启动正式全量实验。
- Key Findings: 选手只提交 `node_to_subgraph` 与 `core_schedules`；Q1 每子图一 Task，Q2/Q3 每核一 Task；Makespan 为主目标，added_copy_bytes 为逻辑新增 COPY 次指标。Q2 受控同方案 $800\to400$、added COPY $18000\to0$；Q3 受控同方案 $1200\to1124$、hit $6000$ bytes，逻辑 added COPY 不变；16 bytes 命中却 $705\to705$。Q2 spill 抵消、Q3 正式图关键路径收益、优化方案 evaluator 长尾仍未证实。B 的 8 图 pilot、约 1.6 小时 stub 成本估计不可当正式 100 图性能结论；Gate 两例约 49% 也不可外推。
- Outputs: coordination/A_MODEL_INTERFACE.md、MASTER_PLAN.md、TASKS.md、DECISIONS.md、HANDOFF.md；skill/competition_orchestrator/{task_protocol,coordination_protocol,handoff_protocol}.md；shared_evidence/README.md。官方本地 canonical 路径为 `题目/中文题目/A题/official_bundle/`，原始 ZIP 未修改，`题目/` 由本机 `.git/info/exclude` 排除。
- Metrics: A 本机 16 项 A 相关单元测试 PASS（含未修改官方 C 机制套件）；C 受控 legality 8/8 一致，Q2/Q3 对照与 boundary PASS/WARN 如上；B 100 图画像本机可生成，ops 766–38666、median 4223；一次 case_001 Q1 2 核官方 runner 成功且记录哈希。A 未取得 B/C 原有 ignored pilot/validation 全量原始记录，以上仅为抽样复核。
- Blockers: C 的 L2 已合并并通过抽查，但其声明的 L3 两个原始文件在当前可访问的团队 Drive `04_Results/Phase1/` 下未出现；因此 C 正式 ACCEPT 与 Phase 1 FULLY ACCEPTED 暂缓。C 审计脚本直接路径入口问题仍留待后续。
- Need Decision: HUMAN DECISION REQUIRED = NO；未切换重大路线、未改变官方目标解释，MODEL FREEZE = FALSE。若后续候选原型需高风险成本显著不同的整体路线，再提交队长决策。
- PR: PR #10/#11 已由 A 审查并合并；本次总控复核分支待提交、push 和 PR。
- Next Suggestion: C 提供可访问的 L3 文件夹链接或把原有两份文件同步到团队共享 Drive；A 只抽查原始文件与 manifest 哈希，不重跑第一轮实验。A/B/C-02 在 Evidence Gate 前均不启动。
- Validation: 当前分支 `compileall src tests main.py`、`tests/smoke_test.py`、16 项 A 单元测试 PASS；C 官方模块套件 PASS；B 官方小图 runner PASS；`git diff --check` 与最终文件范围在提交前复核。

## 2026-09-23 evidence review update

- PR #10/#11 已合并入 main。B L2 六个文件与 manifest 哈希吻合；100 个唯一图、47 条现有 pilot/timeout 记录（其中 24 条两核主记录）和 case_014/034/072 的关键字段与官方图/来源哈希一致。团队 Drive 的 TASK-B-01 目录可访问，case_034 Q2 原始 `run_record.json` 可读取，字段与 L2 对应；TASK-B-01E EVIDENCE SHARED = PASS，TASK-B-01 FORMAL ACCEPTANCE = ACCEPT。
- C L2 五个数据文件与 manifest 的 Git 标准化换行哈希一致；官方脚本/config 哈希及 legality 8/8、Q2 800→400、Q3 1200→1124、16-byte hit 但 705→705 均核对。C 的 L3 声明为 `Google Drive / 04_Results / Phase1 / TASK-C-01 /`，但当前连接的共享 Phase1 目录仅有 TASK-B-01，亦未搜到两份原始文件；TASK-C-01 FORMAL ACCEPTANCE = EVIDENCE_PENDING。
- 本轮只审核既有证据和合并 PR，没有重跑 B/C 第一轮实验；原先技术复核结果保持有效。B 的成本估计仍仅适用于 bounded official stub，C 的受控例不代表 100 图总体收益。
