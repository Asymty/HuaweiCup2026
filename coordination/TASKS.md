# TASKS — Phase 1 Evidence Handoff Gate 与下一阶段候选

FINAL PROBLEM = A；MODEL FREEZE = FALSE。PR #6/#7/#8/#10/#11/#12/#13 已合并。Phase 1 技术审查与 B/C 的 Evidence Handoff Gate 均通过；TASK-A/B/C-01 均正式 ACCEPT，PHASE 1 FULLY ACCEPTED = YES。TASK-A/B/C-02 的启动依赖已满足，但本次验收不执行下一阶段任务。共同前提 DECISION-001 已满足。`题目/` 是 Git 本地排除的只读官方来源，canonical 附件相对路径为 `题目/中文题目/A题/official_bundle/`；`result/**` 中的 official_bundle 只是运行副本。

## TASK-A-01

- Owner: Codex A
- Priority: P0
- Status: DONE
- Depends On: None；DECISION-001 已满足。B/C 可按官方接口和 MASTER_PLAN v1 同时开工。
- Goal: 完成 A 题统一数学形式化与 Q1/Q2/Q3 模型及算法接口设计，使 B 能实现、C 能独立验证。本任务不追求最终高级算法。
- Context: Phase 1；官方 evaluator 是合法性与指标判据。Q1 的双核负载均衡 Gate 结果不能替代 Q2 同核复用或 Q3 L2 创新。
- Inputs: A 题正式题面；全部官方附件的 README、docs、方案格式、config 与 Q1/Q2/Q3 evaluator；coordination/DECISIONS.md；coordination/MASTER_PLAN.md；result/a_feasibility_gate/GATE_REPORT.md（仅参考）。
- Allowed Files: coordination/A_MODEL_INTERFACE.md（新建）、coordination/MASTER_PLAN.md、coordination/DECISIONS.md、coordination/TASKS.md、coordination/agent_a_status.md；必要时仅新建 src/model/a_*.py，避免修改既有通用骨架。
- Forbidden Files: 官方题包与 evaluator 源码、data/raw/**、src/preprocess/**、src/evaluate/a_official_runner.py、src/evaluate/a_legality.py、src/evaluate/a_metric_audit.py、coordination/agent_b_status.md、coordination/agent_c_status.md、paper/**、B/C 的结果目录。
- Expected Outputs:
  1. 图、op、tensor、subgraph、task、core 的统一符号及其与 JSON 字段的映射；
  2. Q1 决策变量、合法性约束、Makespan 的官方计算关系及 added_copy_bytes 的定义；
  3. Q2 相比 Q1 的 Task 合并、同核复用、容量、跨核同步机制；
  4. Q3 相比 Q2 的 shared read-only L2、FIFO 命中、带宽与效用关系；
  5. 三问共用的数据结构、方案生成和 evaluator 调用接口；
  6. 合法性、Makespan、额外搬运、计算成本、Q2/Q3 专属收益的后续优化目标层次。
- Validation: 对照官方题面、README、config、校验器及三个 evaluator 检查每个定义；给出至少一个可落成官方方案 JSON 的接口示例；标记尚待 B/C 验证的假设，不把 Gate 抽样写成正式结论。若新增代码，运行 AGENTS.md 的 compileall、smoke_test 及最小对应检查。
- Completion Criteria: 上述九类内容在 A_MODEL_INTERFACE.md 可定位；B 能按接口实现，C 能据定义提出可证伪检查；状态页列出证据路径、开放问题、验证命令；无未经确认的路线冻结。
- Handoff Target: Codex B、Codex C；经 A 的状态页和完成时序列化追加到 coordination/HANDOFF.md。

## TASK-B-01

- Owner: Codex B
- Priority: P0
- Status: DONE
- Formal Acceptance: ACCEPT（TASK-B-01E L2 哈希与汇总、官方来源及共享 L3 原始记录已由 A 抽样核对）
- Depends On: None；DECISION-001 已满足。可先按官方 JSON/CLI 契约与 MASTER_PLAN v1 建设施；若 A-01 后续细化接口，再对齐而不等待其完成。
- Goal: 建立正式 100 图实验运行与性能画像基础设施，先做代表性 pilot，定位 evaluator 长尾；不盲跑全部组合。
- Context: Gate 已证实官方 Q1/Q2/Q3 能跑通小图，但 case_014 的大 Task 超过 300 秒。Gate 两种方案只是参考，不是正式最终算法。
- Inputs: 100 个官方计算图、config、未经修改的 Q1/Q2/Q3 与 singlecore evaluator、官方示例/校验器、Gate 记录、MASTER_PLAN v1。
- Allowed Files: 新建 src/preprocess/a_graph_profile.py、src/evaluate/a_official_runner.py、tests/test_a_official_runner.py；result/a_formal_runs/**、result/a_graph_profile/**；coordination/agent_b_status.md。coordination/HANDOFF.md 仅在完成时确认无并发编辑后追加。
- Forbidden Files: 官方 evaluator 与原始计算图、data/raw/**、src/model/**、src/evaluate/a_legality.py、src/evaluate/a_metric_audit.py、coordination/MASTER_PLAN.md、coordination/DECISIONS.md、coordination/TASKS.md、C 的状态页与验证结果、paper/**。
- Expected Outputs:
  1. 统一 evaluator runner，按 case、problem、core count 保存 Makespan、added_copy_bytes、Q3 Cache hit_rate、方案生成与评估 runtime、exit code、timeout、输入/配置哈希和结果路径；
  2. 官方单核合法 baseline 及可扩展的逐例正式结果格式；
  3. 100 图的规模/结构统计与分层，明确 op/tensor/edge、依赖及任务规模特征；
  4. 小、中、大代表性 pilot，重点含 case_014、case_034 与其他大图，不立即全量遍历；
  5. runtime 与图特征关系、建议 timeout、跨 case 多进程隔离安全性、全量所需时间的有依据估算。
- Validation: 不修改官方评分逻辑；runner 用官方程序真实调用，保存原始 stdout/stderr、结果 JSON 和退出状态；对成功/非法/超时分别检查落盘行为；对独立 case 的并行运行做有限验证；运行 AGENTS.md 的 compileall、smoke_test 和必要的 runner 测试。
- Completion Criteria: 任一 pilot 可从命令重现并找到原始输出和汇总行；100 图画像完整；给出长尾分层、超时与全量成本估算及其不确定性；状态页列出实际参数、用例、时间和异常，不把 pilot 外推为正式总体成绩。正式 ACCEPT 另需 TASK-B-01E 的 `EVIDENCE SHARED = PASS`。
- Handoff Target: Codex A（路线与成本决策）、Codex C（独立核查）；完成时序列化追加 coordination/HANDOFF.md。

## TASK-C-01

- Owner: Codex C
- Priority: P0
- Status: DONE
- Formal Acceptance: ACCEPT（TASK-C-01E L2/L3 与官方来源经 A 抽样核对）
- Depends On: None；DECISION-001 已满足。可按官方校验器和 MASTER_PLAN v1 独立设计检查，不等待 B 的 runner 完成。
- Goal: 建立独立合法性、指标语义和 Q2/Q3 专属收益验证方案，并向 A 报告 PASS / WARN / FAIL 与必须处理的模型风险。
- Context: Gate 的同一份单子图/每核一子图方案在 Q1/Q2/Q3 上得到相同 Makespan；case_019 虽有 Q3 Cache 命中，却未出现 L2 时延收益。不能接受三问只换 evaluator、方法实际上相同。
- Inputs: A 题题面、官方 README/docs/config、校验器及三个 evaluator、Gate 方案/结果、MASTER_PLAN v1；B 后续 pilot 结果可作为追加证据，但不是启动依赖。
- Allowed Files: 新建 src/evaluate/a_legality.py、src/evaluate/a_metric_audit.py、tests/test_a_legality.py、tests/test_a_metric_audit.py、src/plot/a_validation_*.py（必要时）；result/a_validation/**；coordination/agent_c_status.md。coordination/HANDOFF.md 仅在完成时确认无并发编辑后追加。
- Forbidden Files: 官方 evaluator 与原始计算图、data/raw/**、src/model/**、src/preprocess/**、src/evaluate/a_official_runner.py、result/a_formal_runs/**、coordination/MASTER_PLAN.md、coordination/DECISIONS.md、coordination/TASKS.md、B 的状态页、paper/**。
- Expected Outputs:
  1. 独立检查 op 完整映射、sgid 唯一调度、依赖、同核顺序、子图/组合执行无环和官方非法判定边界；
  2. Makespan 与 added_copy_bytes 的字段及计算语义、Cache hit_rate 的按字节定义；
  3. 能真正区分 Q1 Task 边界、Q2 Task 合并/同核复用、Q3 shared L2 命中对时延与搬运影响的验证场景和成对对照口径；
  4. 每项 PASS / WARN / FAIL、证据路径、A 必须处理的模型风险。明确命中率上升但 Makespan 不降的情形。
- Validation: 用官方 evaluator 对可区分机制的小例或已有可信用例做最小成对验证；独立复算指标并覆盖缺失映射、重复 sgid、非法依赖等负例；运行 AGENTS.md 的 compileall、smoke_test 和必要的独立检查测试；不修改官方程序。
- Completion Criteria: 验证矩阵能分别证伪 Q1/Q2/Q3 的错误解释，PASS / WARN / FAIL 有实际日志或可复现命令；状态页列出开放风险，未把 Gate 结果冒充正式结论。正式 ACCEPT 另需 TASK-C-01E 的 `EVIDENCE SHARED = PASS`。
- Handoff Target: Codex A（模型修订与决策）、Codex B（实验口径）；完成时序列化追加 coordination/HANDOFF.md。

## 文件互斥约定

A 主写 MASTER_PLAN/DECISIONS/TASKS 和 A 模型接口；B 主写预处理、官方 runner 与正式运行结果；C 主写独立合法性/指标审计及验证结果。B/C 虽均在 src/evaluate/ 下工作，但具体文件名互不相同，禁止顺手改对方文件。各角色仅主写自己的状态页；HANDOFF.md 在任务完成后按交接协议顺序追加，不并发覆盖。凡需要跨边界改动，先在状态页说明并由 A 调整任务卡。

## Phase 1 正式验收记录

| Task | Implementation | Technical Review | Formal Acceptance | 当前证据边界 |
| --- | --- | --- | --- | --- |
| TASK-A-01 | DONE | PASS | ACCEPT | A_MODEL_INTERFACE 与官方题面/代码、B/C 后续受控证据一致，已由 A 细化。 |
| TASK-B-01 | DONE | PASS_WITH_WARNING | ACCEPT | PR #10 已合并；L2 100 图/47 条 pilot、哈希与关键 case 核对通过；共享 Drive L3 记录可读取。大图和单核超时仍是后续实验风险。 |
| TASK-C-01 | DONE | PASS_WITH_WARNING | ACCEPT | PR #11/#13 已合并；L2 哈希、8/8 合法性、Q2/Q3 对照及边界通过；共享 Drive L3 两份原始文件的大小和 SHA-256 与修正 manifest 一致。 |

`Status: DONE` 与正式 `ACCEPT` 分开。A 通过 L2/L3 有限抽查完成 B/C 的正式验收，未重做第一轮实验。PHASE 1 FULLY ACCEPTED = YES；A/B/C-02 的依赖已满足，但尚未启动。

## TASK-B-01E

- Owner: Codex B
- Priority: P0
- Status: DONE；EVIDENCE SHARED = PASS；A REVIEW = ACCEPT
- Depends On: TASK-B-01 implementation DONE；PR #8 已合并。
- Goal: 从 B 本机已有 `result/**` 整理 TASK-B-01 的跨机器最小证据包；不重新运行 100 图画像、pilot、singlecore 或并行试验。
- Context: A 已做代码与局部官方抽查；B 的 8 图 pilot、runtime 估计和 timeout/concurrency 原始记录尚需 L2/L3 交接以完成正式 ACCEPT。
- Inputs: B 本机 `result/a_graph_profile/**`、`result/a_formal_runs/**` 现有记录；已合并 `src/preprocess/a_graph_profile.py`、`src/evaluate/a_official_runner.py`；官方原始 ZIP 与 canonical `题目/中文题目/A题/official_bundle/`（只读）；coordination/agent_b_status.md。
- Allowed Files: `shared_evidence/phase1/task_b_01/**`；`coordination/agent_b_status.md`；`coordination/HANDOFF.md` 仅在无并发编辑且同步最新 main 后追加交接。
- Forbidden Files: 官方题包及 `题目/**`、`data/raw/**`、B/C/A 模型及 runner 源码、`coordination/TASKS.md`、`coordination/MASTER_PLAN.md`、`coordination/DECISIONS.md`、C 状态/证据、`paper/**`；不得重跑实验或改已有结果。
- Expected Outputs: `graph_profile_summary.csv`（100 行，case_id、ops、edges、tensor 数/字节及已有结构字段）；`pilot_summary.csv`（8 个分层 case 的 Q1/Q2/Q3 2 核记录及已存在的其他核数记录，含 cores、evaluator 秒数、Makespan、COPY、exit/timeout）；`key_cases.json`（case_014、case_034，case_072 有记录则纳入）；`evidence_manifest.json`（来源/证据 SHA-256、官方脚本/config 哈希、命令、参数、时间戳、任务提交号、提取方法、L3 实际位置）；`README.md`（pilot/estimate/timeout 删失、1.6 h 与 1.1–3.5 h 插值口径、原始大文件位置）。只共享必要已有原始记录到 `Google Drive / 04_Results / Phase1 / TASK-B-01 /`。
- Validation: 不调用 evaluator；从原始已有记录机械抽取并校验行数、case 唯一性、哈希、字段来源及状态页数值；对 case_014/034/072 的 timeout 与运行时间标注来源；`git diff --check`；检查 L2 不含大型 Trace/stdout/官方附件。
- Completion Criteria: L2 文件可读、manifest 所列 SHA-256 全部匹配，必要 L3 位置真实可定位，`EVIDENCE SHARED = PASS`；A 可从包核对 100 图汇总、8 图 pilot、一个真实 runner 记录及估算方法；B 状态页记录路径与 PR。不重跑旧实验。
- Handoff Target: Codex A 正式验收 TASK-B-01；Codex C 可只读复核指标。

## TASK-C-01E

- Owner: Codex C
- Priority: P0
- Status: DONE；EVIDENCE SHARED = PASS；A REVIEW = ACCEPT
- Depends On: TASK-C-01 implementation DONE；PR #7 已合并。
- Goal: 从 C 本机已有 `result/a_validation/**` 整理 TASK-C-01 的跨机器最小证据包；不重跑受控机制套件。
- Context: A 已独立复核技术机制；原始受控结果与哈希尚未形成 Git 管理的可移植 L2 包。
- Inputs: C 本机 `result/a_validation/official_validation_evidence.json` 与报告、已合并 C 审计代码/测试、官方 canonical 附件（只读）、coordination/agent_c_status.md。
- Allowed Files: `shared_evidence/phase1/task_c_01/**`；`coordination/agent_c_status.md`；`coordination/HANDOFF.md` 仅在无并发编辑且同步最新 main 后追加交接。
- Forbidden Files: 官方题包及 `题目/**`、`data/raw/**`、`src/model/**`、B runner/画像、C 审计源码与测试（本任务不修代码）、`coordination/TASKS.md`、`coordination/MASTER_PLAN.md`、`coordination/DECISIONS.md`、B 状态/证据、`paper/**`；不得重跑旧实验或改已有结果。
- Expected Outputs: `legality_matrix.json`（8 个案例、独立与官方判定）；`q2_mechanism.json`（800→400、scheduled COPY 30000→12000、added COPY 18000→0）；`q3_mechanism.json`（1200→1124、hit/miss/total bytes、字节命中率 1/3、DDR 30000→24000、added COPY 不变）；`q3_boundary.json`（hit_bytes>0 而 705→705）；`evidence_manifest.json`（原始与 L2 文件/官方脚本/config 哈希、测试输入、命令、时间戳、任务提交号、提取方法、L3 实际位置）；`README.md`（受控机制验证不等于 100 图总体收益）。只共享必要已有原始记录到 `Google Drive / 04_Results / Phase1 / TASK-C-01 /`。
- Validation: 不调用 evaluator；由旧 evidence 机械提取并校验 8 行判定、成对方案/参数一致性、数值、哈希与状态页口径；`git diff --check`；检查 L2 无大 Trace/stdout/官方附件。
- Completion Criteria: L2 文件与 manifest 可读且哈希一致，必要 L3 位置真实可定位，`EVIDENCE SHARED = PASS`；A 可抽查 Q2 pair、Q3 pair 和 boundary；C 状态页记录路径与 PR。不重跑旧实验。
- Handoff Target: Codex A 正式验收 TASK-C-01；Codex B 可只读对齐 runner 字段。

## TASK-A-02（Phase 2；依赖已满足，可启动）

- Owner: Codex A
- Priority: P1
- Status: TODO
- Depends On: TASK-B-01E、TASK-C-01E 的 L2/L3 Gate 均 PASS；A 将 B/C 第一轮正式 ACCEPT，Phase 1 FULLY ACCEPTED = YES。
- Goal: 给出可执行、计算预算受控的 Q1/Q2/Q3 候选优化原型规范与统一 PlanSpec，不预设胜出的算法。
- Context: Q1 以官方 Makespan 为主、added COPY 为次；Q2 需计同核复用与 spill，Q3 需计 FIFO 窗口及关键路径，evaluator 长尾限制搜索次数。
- Inputs: A_MODEL_INTERFACE.md、B/C L2 证据与 A 验收记录、官方只读题包、现有 runner/validator 接口。
- Allowed Files: `coordination/A_ALGORITHM_DESIGN.md`、必要的 `coordination/A_MODEL_INTERFACE.md` 小幅订正、`coordination/agent_a_status.md`、`coordination/DECISIONS.md`（仅形成新路线决定时）、`shared_evidence/phase2/task_a_02/**`。
- Forbidden Files: 官方题包、`data/raw/**`、B/C 源码与结果、`paper/**`、正式全量实验输出。
- Expected Outputs: 两条可比较的合法切图/分核候选路线（有界拓扑分块与通信亲和合并）、Q2 驻留/spill 代理、Q3 FIFO/关键路径代理、统一 JSON/资源预算接口、候选淘汰条件与最多 2 图×2–5 核的小 pilot 设计；不先宣称赢家。
- Validation: 每个候选说明合法性维护、主要计算复杂度、官方调用上限、Makespan/added COPY/时长三指标及同方案 Q1/Q2/Q3 对照；C 可据此设计反例，B 可据此实现；不执行正式实验。
- Completion Criteria: 方案规范足够让 B/C 独立执行与证伪；明确停止条件、风险及 `EVIDENCE SHARED = PASS`（文档、来源和审核记录进入本任务 L2）；A 状态页与 handoff 完整。
- Handoff Target: Codex B 实现与测量、Codex C 独立验证。

## TASK-B-02（Phase 2；依赖已满足，可启动）

- Owner: Codex B
- Priority: P1
- Status: TODO
- Depends On: TASK-B-01E、TASK-C-01E Gate PASS；Phase 1 fully accepted。可与 TASK-A-02/C-02 并行启动，不等待 A-02 的算法结论。
- Goal: 将现有官方 runner 扩为预算受控且字段完整的原型评估接口；只做小规模真实调用验证，不实现优化算法。
- Context: 当前 compact run_record 可恢复原始结果，但缺 partition/spill COPY、max_op_end、total cache access bytes 与显式 DDR 诊断量；大 Task 和 singlecore 存在长尾。
- Inputs: 已合并 runner/测试、B-01 L2 证据、C-01 L2 指标语义、canonical 官方附件只读副本。
- Allowed Files: `src/evaluate/a_official_runner.py`、`tests/test_a_official_runner.py`、`result/a_prototype_runner/**`、`shared_evidence/phase2/task_b_02/**`、`coordination/agent_b_status.md`；HANDOFF 仅序列化追加。
- Forbidden Files: 官方题包、`data/raw/**`、`src/model/**`、C 的审计源码/测试、A 的模型文档、正式 100 图最终实验、`paper/**`。
- Expected Outputs: compact record 新增官方 partition/spill、独立 max_op_end 校验、Q3 hit+miss total、标明推导前提的 DDR 诊断量；按方案/图/配置哈希安全配对；显式 evaluator 调用预算与 timeout 状态；最多 case_019/034 两图、2 核、同方案 Q2/Q3 各一次的最小验证记录。
- Validation: runner 成功/非法/超时单测与官方最小调用；新增字段和完整官方 result 一致；不把 censored 单核结果补成数值；compileall、smoke_test、`git diff --check`。
- Completion Criteria: 新字段、预算和异常路径可复现，L2 有小型 manifest/记录及必要 L3 位置，`EVIDENCE SHARED = PASS`；无正式全量运行。
- Handoff Target: Codex A 评估算法预算、Codex C 独立核查字段。

## TASK-C-02（Phase 2；依赖已满足，可启动）

- Owner: Codex C
- Priority: P1
- Status: TODO
- Depends On: TASK-B-01E、TASK-C-01E Gate PASS；Phase 1 fully accepted。可与 TASK-A-02/B-02 并行启动，不等待新算法结果。
- Goal: 建立原型候选的独立接受/证伪门槛，使同方案机制收益与重新分核收益可区分。
- Context: C-01 的受控机制已成立，但正式图收益未知；命中率、逻辑 COPY 和 Makespan 不能互相替代。
- Inputs: C-01 L2 证据、A_MODEL_INTERFACE.md、已合并独立审计代码与官方只读题包；B runner 只读。
- Allowed Files: `src/evaluate/a_metric_audit.py`、`tests/test_a_metric_audit.py`、`src/evaluate/a_legality.py`、`tests/test_a_legality.py`（仅必要修补）、`shared_evidence/phase2/task_c_02/**`、`result/a_validation_prototype/**`、`coordination/agent_c_status.md`；HANDOFF 仅序列化追加。
- Forbidden Files: 官方题包、`data/raw/**`、`src/model/**`、B runner/画像、A 的模型/决策文件、正式 100 图最终实验、`paper/**`。
- Expected Outputs: 接受矩阵检查合法性、同图/同核/同 plan hash 的 Q1↔Q2 与 Q2↔Q3 对照、Makespan 和逻辑/物理搬运一致性、Cache 命中却无收益的 WARN；修复审计 CLI 直接启动的导入路径问题并测试；用旧 C-01 evidence 加至多一个官方小图检验，不做新的全量机制实验。
- Validation: 故意错配 plan hash 与异常指标时给出 FAIL/WARN；同方案正确记录给出 PASS；compileall、smoke_test、官方最小核验及 `git diff --check`。
- Completion Criteria: 接受矩阵有可证伪例、命令与小型 L2 证据，必要 L3 位置、`EVIDENCE SHARED = PASS`；不预设正式图效益。
- Handoff Target: Codex A 决定候选淘汰，Codex B 对齐记录格式。
