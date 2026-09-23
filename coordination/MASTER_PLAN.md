# MASTER PLAN v2 — A 题 Phase 1 技术审查

- FINAL PROBLEM = A：通用神经网络处理器下的多核调度问题
- PHASE = Phase 1 技术审查通过；B 的 Evidence Handoff Gate 已完成，C 的 L3 原始文件待共享定位。Phase 2 算法原型任务已设计，尚未启动。
- PHASE 1 REVIEW = PASS（技术链路）；PHASE 1 FULLY ACCEPTED = NO（C L3 证据待交接）。
- MODEL FREEZE = FALSE
- Model Version: v1.1（依据 B/C 第一轮受控证据修订指标与工程边界；正式算法尚未确定）
- Decision Authority: 人类队长已确认选题；后续核心路线变更、MODEL FREEZE 和最终提交仍需人类确认。
- Primary Sources: 题目/中文题目/A题/ 的原始题包及只读解压副本 official_bundle/（本地专用、Git 排除）；其 README.md、docs/、code/、data/config.txt、100 个 case JSON；result/a_feasibility_gate/GATE_REPORT.md 仅作 Gate 参考。result/** 中的 official_bundle 只是运行工作副本，不是 canonical source。官方程序为合法性和指标的最终判据。
- Current Selection: Q1、Q2、Q3；本题没有 Q4。

## 共同问题与交付口径

给定计算图 G（ops、tensors、edges）、官方固定配置和核心数 N，输出一份可执行方案：node_to_subgraph 将每个非 COPY_IN/COPY_OUT 操作映射到一个非负 sgid；core_schedules 为长度 N 的列表，依次列出每个核心执行的 sgid。决策包括操作的子图归属、每个子图所属核心、每核子图顺序。选手不直接指定核内逐 op 顺序或自行改写官方 COPY、spill、事件模拟逻辑。

所有非 COPY 操作须且仅须映射一次；每个 sgid 须且仅须调度一次；子图依赖图必须无环；同核顺序不得逆转依赖；最终组合执行图不能有等待环。原图结构、ID、操作字段等也必须满足官方输入校验。L1/UB 容量是执行硬约束，官方核内调度在必要时自动插入 spill；不可仅因原始工作集大于容量就判定选手方案非法。

主指标为官方多核事件模拟的 Makespan，即所有执行操作最晚完成时刻。辅助指标 added_copy_bytes 按官方结果字段定义：scheduled_copy_bytes 减 original_graph_copy_bytes。Q3 另报告按命中字节计的 Cache hit_rate。方案生成耗时与评估器 wall time须分别记录；官方示例随机生成器只演示方案格式，不是性能 baseline。

正式实验：全部 100 个官方图使用原始固定 config；Q1/Q2 各报告 2–5 核结果和 1 核参照，逐例保留 Makespan 与 added_copy_bytes；Q3 对相同图、相同核数报告无 L2 与只读 Cache 两种配置，逐例保留 Makespan、added_copy_bytes、Cache hit_rate。平均加速比的单核分母必须来自官方 singlecore_evaluate.py；Q3 的 L2 相对加速比使用相同核数下无 L2 的 Makespan 作分母。正式实验不得把 Gate 抽样当总体结果。

固定参数：L1 = 524288 bytes，UB = 131072 bytes，共享 DDR = 60 bytes/cycle；Q1 跨核 Task 等待 1000 cycles、同核 Task 切换等待 100 cycles；Q2/Q3 跨核 COPY 同步延迟 500 cycles；Q3 只读 FIFO L2 = 1048576 bytes、250 bytes/cycle，带宽独立于 DDR。未经题目要求的敏感性实验不能替代固定配置正式结果。

## Q1 — 场景 A：每个子图一个 Task

- 输入：官方计算图、固定配置、核心数 N（正式多核 2–5；1 核作参照）。
- 输出：上述统一方案 JSON，以及由官方问题 1 评估器生成的结果 JSON、Trace、日志。
- 决策变量：非 COPY 操作至 sgid 的映射；sgid 至核心的分配；每核 sgid 顺序。子图数量由方案决定。
- 硬约束：共同合法性规则；每个子图单独成为 Task；跨任意子图的边界数据必须按官方规则经 DDR；Task 依赖与同核顺序可执行；官方容量、Pipe 与共享带宽规则成立。
- 主指标：尽量缩短问题 1 官方 Makespan。
- 次指标：控制问题 1 官方 added_copy_bytes；记录方案生成时间及官方评估时间。不能只优化负载均衡而忽略 Task 等待和 DDR 争用。

## Q2 — 场景 B：每核合并一个 Task

- 输入：同一图、配置、核心数及统一方案格式；以 Q1 的图划分和调度表示为基础。
- 输出：统一方案 JSON；官方问题 2 的结果 JSON、Trace、日志；与 Q1 可比较的逐例指标。
- 决策变量：同 Q1，但分核、子图相邻关系和顺序还决定同核数据驻留与跨核 COPY。
- 硬约束：共同合法性规则；同一核心全部子图合并为一个 Task；同核边界可在 L1/UB 复用，不插入跨 Task COPY；跨核依赖由 COPY_OUT/COPY_IN 与 500-cycle 同步处理；L1/UB 容量由官方核内调度严格执行，必要时 spill。
- 主指标：尽量缩短问题 2 官方 Makespan。
- 次指标：控制问题 2 官方 added_copy_bytes，尤其跨核通信与 spill；单独量化 Task 合并/同核复用对结果的作用。

## Q3 — 场景 B + shared read-only L2

- 输入：Q2 的图、配置、核心数及方案格式；官方 Q2 无 L2 结果可作同核数参照。
- 输出：统一方案 JSON；官方问题 3 的结果 JSON、Trace、日志；相同核数的无 L2 / L2 对比及按字节计的 Cache hit_rate。
- 决策变量：同 Q2；在建模与方案生成时还需考虑共享输入的复用机会、访问时序及 FIFO 容量/带宽。
- 硬约束：全部 Q2 约束；共享只读 FIFO L2 容量 1 MB、带宽 250 bytes/cycle；Cache 命中读取与 DDR 带宽池相互独立，命中/淘汰由官方模拟决定。
- 主指标：尽量缩短问题 3 官方 Makespan，并报告相同核数相对无 L2 的加速比。
- 次指标：官方 added_copy_bytes 与按命中字节计的 hit_rate。Cache 命中不自动等于时延收益，也不能假定 hit_rate 上升必然降低 added_copy_bytes；需用同一方案的 Q2/Q3 成对评估隔离 L2 作用，再说明方案变化的额外影响。

## 统一主线与阶段依赖

1. 共享基础机制：图依赖、合法切图、子图分核、每核顺序、官方核内调度及多核事件模拟，统一使用 node_to_subgraph + core_schedules 接口。
2. Q1 先建立可执行切图/调度与跨 Task 通信权衡。
3. Q2 在同一输入输出接口上改变 Task 组织和通信规则，新增同核 L1/UB 复用、容量驻留与跨核同步；需要独立证据证明区别于 Q1。
4. Q3 沿用 Q2 的 Task 结构，加入共享只读 L2 的 FIFO 命中及独立读带宽；需要独立证据证明 L2 对时延/搬运的实际作用。

第一轮 A/B/C 的代码与文档已合并到 main。A 的形式化和 B 的 runner/画像、C 的合法性/指标与受控机制套件足以支持下一阶段的算法设计；形式化接口仍以官方程序为最终判据。优化目标层次为合法可执行 → 降低官方 Makespan → 控制逻辑 added_copy_bytes → 约束生成与评估成本 → 解释 Q2/Q3 专属收益，不发明加权总分。C 的 Q2/Q3 受控图只证明机制可生效，不证明 100 图总体收益。B 的 8 图 pilot 和约 1.6 小时估算只针对官方 stub 方案，正式优化方案成本仍未知。

## Phase 1 验收边界与下阶段门槛

- TASK-A-01：正式 ACCEPT。模型字段、目标、约束与官方题面/代码及 B/C 受控复核一致；本计划与 A_MODEL_INTERFACE.md 已按实际证据细化。
- TASK-B-01：IMPLEMENTATION = DONE；TECHNICAL REVIEW = PASS_WITH_WARNING；FORMAL ACCEPTANCE = ACCEPT。PR #10 的 L2 manifest、100 图、47 条 pilot、关键 case 与官方哈希通过 A 抽查；共享 Drive L3 原始 runner 记录可读取。长尾和单核超时仍属后续风险。
- TASK-C-01：IMPLEMENTATION = DONE；TECHNICAL REVIEW = PASS_WITH_WARNING；FORMAL ACCEPTANCE = EVIDENCE_PENDING。PR #11 的 L2 哈希、8/8 合法性、Q2/Q3 受控对照和边界通过 A 抽查；C 声明的 L3 原始文件尚未在团队共享 Drive 定位。`python src/evaluate/a_metric_audit.py` 直接启动有 `src` 导入路径问题；模块入口和测试可用。
- Evidence Handoff Gate：B/C 均已从已有 `result/**` 整理 L2，PR #10/#11 已合并；B 的共享 L3 已定位并抽查，C 的 L3 仍待提供可访问链接或同步到团队 `Google Drive / 04_Results / Phase1 / TASK-C-01 /`。不重跑第一轮实验。C 原始文件可读取并抽样核对后，A 再决定其正式 ACCEPT 与 Phase 1 FULLY ACCEPTED。
- TASK-A-02/B-02/C-02 是下一阶段候选任务卡，均依赖 Evidence Handoff Gate；在 gate 前不执行。不得启动正式 100 图最终实验、MODEL FREEZE 或论文结果包装。

## P0 风险登记

| ID | 风险 | 状态 | Phase 1 证据与后续处理 |
| --- | --- | --- | --- |
| RISK-001 | evaluator 长尾限制搜索 | PARTIALLY_RESOLVED | B 8 图 stub pilot 最慢 case_014 Q3 56.65 秒，case_014/072 单核在 90 秒删失；Gate 大 Task 超过 300 秒。Task 大小须作工程约束，官方调用预算有限；优化方案长尾与 600 秒建议仍待测。 |
| RISK-002 | Makespan 与 added COPY 取舍 | PARTIALLY_RESOLVED | 官方主次指标已定且 C 独立复核语义；尚无正式图的 Pareto 分布。候选方案同时报告两项，不设虚构权重。 |
| RISK-003 | Q2 同核复用的独立净收益 | PARTIALLY_RESOLVED | C 受控同方案 Q1/Q2 为 Makespan 800→400、added COPY 18000→0；正式图上的 L1/UB 压力与 spill 抵消仍未知。 |
| RISK-004 | Q3 shared L2 的独立作用 | PARTIALLY_RESOLVED | C 受控同方案 Q2/Q3 为 1200→1124、命中 6000 bytes；16 bytes 命中案例 705→705。正式图的 FIFO 时序与关键路径收益仍未知。 |
| RISK-005 | Gate 两例约 49% 改善被错误外推 | RESOLVED（表述边界） | 已明确仅为两例 Gate 抽样；未写作 100 图总体结果。正式总体收益仍需后续实验。 |
| RISK-006 | 跨 Agent 原始证据可访问性 | OPEN（仅 C） | B 的 L2/L3 已共享并经 A 抽查；C 的 L2 已核对，但其 L3 原始文件在团队共享 Drive 尚不可见，定位后关闭。 |

## 第一轮里程碑与下一步

- TASK-A-01：统一数学形式化与三问模型/算法接口，供 B 实现、C 验证。
- TASK-B-01：100 图运行器与规模/结构画像，先代表性 pilot，特别检查 case_014、case_034。
- TASK-C-01：独立合法性和指标语义核查，给出 Q2/Q3 专属收益验证场景及 PASS / WARN / FAIL。
- Phase 1 技术链路已通过；C 的完整正式验收仍以可访问的 L3 原始证据为前提。A/B/C 下一阶段候选任务见 TASKS.md，目前均未启动。MODEL FREEZE 仍为 FALSE，未经队长确认不得冻结或将 Gate 数值用于正式论文。
