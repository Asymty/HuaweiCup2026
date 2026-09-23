# MASTER PLAN v1 — A 题

- FINAL PROBLEM = A：通用神经网络处理器下的多核调度问题
- PHASE = PHASE 1: Problem Formalization
- MODEL FREEZE = FALSE
- Model Version: v1（阶段计划与官方接口口径；正式算法尚未确定）
- Decision Authority: 人类队长已确认选题；后续核心路线变更、MODEL FREEZE 和最终提交仍需人类确认。
- Primary Sources: 题目/中文题目/A题.zip；嵌套官方附件中的 README.md、docs/、code/、data/config.txt、100 个 case JSON；result/a_feasibility_gate/GATE_REPORT.md。官方程序为合法性和指标的最终判据。
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

三 Codex 的第一轮工作可同时开始：A 形式化接口，B 以官方格式构建运行与成本画像，C 独立检查合法性与 Q2/Q3 区分场景。B/C 可先按本计划及官方接口开工，后续接口细节由 A 的 TASK-A-01 输出统一；不得各自重新设计完整方案。优化目标层次暂定：合法可执行 → 降低 Makespan → 控制新增搬运 → 约束生成与评估成本 → 解释 Q2/Q3 专属收益。此层次不宣称全局最优。

## P0 风险登记

| ID | 风险 | 当前证据 | 第一轮处理 |
| --- | --- | --- | --- |
| RISK-001 | 全量 evaluator 计算长尾 | case_014 大 Task 的 Q1 超过 300 秒；小子图示例 34.40 秒完成但质量差 | B 先做分层 pilot、逐例限时与运行成本画像；A 将子图/Task 规模纳入可计算性约束 |
| RISK-002 | 简单多核负载均衡可能以大量 COPY 换时延 | Gate 两例下降约 49%，但新增搬运；case_014 官方示例的新增搬运极大 | A 明确主次目标与 trade-off；B 同时记录 Makespan 与 added_copy_bytes；C 复核指标 |
| RISK-003 | Q2 必须证明 Task 合并与核内复用的独立收益 | Gate 每核一个子图，Q1/Q2 数值相同 | C 设计区分场景；A 在模型中单列驻留/跨核机制；B 后续做成对评估 |
| RISK-004 | Q3 必须证明 shared L2 的独立作用 | Gate case_019 有命中但 Q2/Q3 Makespan 相同 | C 区分 hit_rate 与有效时延收益；A 建模 FIFO/共享输入；B 记录 Q2/Q3 同方案对照 |
| RISK-005 | Gate 两例约 49% 改善不得写成总体结论 | Gate 仅抽样 case_001、case_019 | 正式阶段覆盖全部 100 图、2–5 核及单核参照，逐例保存证据 |

## 第一轮里程碑

- TASK-A-01：统一数学形式化与三问模型/算法接口，供 B 实现、C 验证。
- TASK-B-01：100 图运行器与规模/结构画像，先代表性 pilot，特别检查 case_014、case_034。
- TASK-C-01：独立合法性和指标语义核查，给出 Q2/Q3 专属收益验证场景及 PASS / WARN / FAIL。
- Phase 1 完成条件：三方交接有文件路径、命令和事实证据；A 汇总模型风险。MODEL FREEZE 仍为 FALSE，未经队长确认不得冻结或将 Gate 数值用于正式论文。
