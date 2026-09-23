# A 题 Phase 2 候选原型规范（TASK-A-02）

- 状态：**设计完成，候选未实现、未评估、未选出赢家**。MODEL FREEZE = FALSE。
- 适用范围：同一个官方计算图、固定 config、核心数 $N\in\{2,3,4,5\}$ 下的 Q1/Q2/Q3。这里只定义 A 负责的建模选择和接口；B 负责实现与真实测量，C 负责独立证伪。
- 权威判据：官方 `derive_multicore_plan`、三问 evaluator 的退出状态与结果 JSON。文中的代价均是**排序代理**，不是自写评分器。受控机制数值和八图随机 stub pilot 只用于识别风险，不是候选方案的成绩。
- 已满足的依赖：TASK-A/B/C-01 均正式 ACCEPT；B/C 的 Phase 1 L2/L3 Evidence Handoff Gate 均 PASS。来源和哈希见 `shared_evidence/phase2/task_a_02/evidence_manifest.json`。

## 1. 输入、输出、目标与不变量

**输入。** 只读官方图 $G$ 的 `ops/tensors/edges`、固定 `config.txt`、核心数 $N$、方案生成参数与资源预算。预处理先从含 tensor 中转和直接 Op→Op 边的原图推导 Op DAG，再按官方规则收缩不参与切图的 `COPY_IN/COPY_OUT`，得到可切分 Op 集 $O^\star$ 和依赖 $D^\star$。不把 tensor 连通关系直接当依赖，不假设 100 图均严格二部。

**提交输出。** 对所有 $o\in O^\star$ 给出非负整数子图号 $f(o)$，并给出长度恰为 $N$ 的 `core_schedules`。提交文件的顶层**恰好**是 `node_to_subgraph` 与 `core_schedules`；内部预测、Task、Cache、种子、指标均不得写入官方方案 JSON。`node_to_subgraph` 的键是十进制 op id 字符串；一个 sgid 恰在一个核心列表出现一次；空核心允许。

**硬约束。** 原图和 JSON 先经官方解析与 `derive_multicore_plan` 检查完整映射、子图 DAG、同核依赖顺序。Q1 还要检查子图依赖与 Task 顺序合并后无环；Q2/Q3 还要检查扩展操作图、Pipe FIFO、跨核 COPY 与内存依赖无环。官方 Step2/3 或事件模拟拒绝的方案一律记为非法，不修饰为低分。L1/UB 容量分别为 524288/131072 bytes；预估超容量只是风险，Step2 spill 可能修复也可能失败。

**目标顺序。** 首先合法且在预算内完成评估；随后按同图、同核数、同问题的官方 Makespan $T_p$ 比较；同时原样报告逻辑 `added_copy_bytes` $\Delta B_p$、其 partition/spill 分量、运行时间与超时。没有官方固定权重，不发明 $T+\lambda\Delta B$ 总分；存在 $T$ 与 $\Delta B$ 互换时保留 Pareto 对照，不擅自宣称绝对更优。Q3 的物理 DDR 诊断量与逻辑 $\Delta B_3$ 分开。

## 2. 统一 PlanSpec 与可复现接口

PlanSpec 是**内部 sidecar 规范**，不直接提交给官方 evaluator。字段建议如下；B 可按已有 runner 的命名实现等价结构，C 可据此复核，不要求本任务新增代码。

```json
{
  "schema_version": "a02.v1",
  "case_id": "case_019",
  "graph_sha256": "<sha256>",
  "config_sha256": "<sha256>",
  "num_cores": 2,
  "candidate_id": "bounded_topo_v1",
  "seed": 0,
  "generator_parameters": {"max_eligible_ops_per_block": 64},
  "solution": {
    "node_to_subgraph": {"<non_COPY_op_id>": 0},
    "core_schedules": [[0], []]
  },
  "preview": {"status": "estimated_only"}
}
```

`solution` 只表示结构，示意键不是可运行实例。落盘的官方 plan 只取 `solution` 两字段；其 SHA-256 按实际落盘字节计算。序列化应确定性：按数值 op id 排序映射键、保留 core 和 sgid 列表顺序，统一 UTF-8 与换行策略；同一方案评估三问时**直接复用同一 plan 文件**，不重新生成。评价记录至少带 `case_id`、图/config/plan/官方脚本哈希、`candidate_id`、$N$、问题号、生成秒数、evaluator 秒数、退出码、超时、官方原始结果路径与关键指标；B-02 补齐的 partition/spill、`max_op_end`、Q3 hit/miss/total 与 DDR 诊断量应沿用，A 不修改 B runner。

令 `pair_key = (graph_sha256, config_sha256, num_cores, plan_sha256)`。Q1→Q2、Q2→Q3 的**机制对照**必须具有相同 pair_key；不同 plan 的比较另列为“方案变化”，不能归因于机制。若题目要求不同 $N$，必须重新生成长度为该 $N$ 的 `core_schedules`，且不同 $N$ 不作同方案机制配对。

建议的模块边界：`build_graph_view` → `contract_copy_dependencies` → `make_candidate(route, G, N, parameters)` → `emit_solution` → `official_static_check` → B 的 `run_evaluation` → C 的 `audit_result`。生成器返回 `solution` 和 sidecar preview；B/C 可独立读取官方原图，不依赖 A 的私有运行目录。

## 3. 候选路线 A：有界拓扑分块 + 负载分核

**构造。** 在 $D^\star$ 上做确定性 Kahn 拓扑排序，ready 集按 op id 递增打破平局。把该序列切成连续区间，每块最多 64 个可切分 Op；最后一块可更小。按区间先后赋连续 sgid。以 $W_s=\sum_{o\in S_s}\mathrm{cycles}(o)$ 作为粗计算量，从小 sgid 到大 sgid逐块选择当前 $L_k=\sum_{s:c(s)=k}W_s$ 最小的核心，平局选较小 core id，并把 sgid 追加到该核列表。这里的 64 是**首次原型的固定设计参数**，比既有随机 stub 的 50–100 上界更谨慎；没有证据表明 64 最优。

**合法性维护。** 连续拓扑区间使每条跨块依赖从小 sgid 指向大 sgid；任何核心列表也是递增 sgid。故静态子图 DAG、同核直接依赖与 Q1 的 Task 顺序边没有反向边。Op 覆盖唯一、sgid 只排一次。这个论证**不涵盖** Step2/3 生成的 spill、Pipe/内存边或 Q2/Q3 跨核等待环；每个输出仍须由官方入口逐问确认。若失败，不把局部排序检查当成合法证明，也不自动改官方程序。

**作用与代价。** 本路线优先保证块大小与负载均衡，可能产生较多跨块 COPY：Q1 同核跨 Task 也会搬运，Q2/Q3 则主要看跨核依赖。它是可执行的确定性比较基点，不是声称优于官方随机 stub 的 baseline。构图与拓扑排序的主要成本随显式依赖规模约为 $O(|O|+|E|+|D^\star|)$；分块和分核另为 $O(|O^\star|+K N)$，$K$ 为块数。COPY 收缩本身可能展开大量依赖，实际时间与峰值内存必须单独测量。

## 4. 候选路线 B：通信亲和的相邻块合并 + 容量保护分核

**构造。** 使用与路线 A 相同的确定性 Op 拓扑序，先切为最多 32 Op 的连续微块。对每对**相邻**块估计：跨块的不同逻辑 tensor 的总字节、被两块共同消费的图输入 tensor 字节，以及合并后 Q1 Task 边界可能消失的字节；同一 tensor 在一对块内去重计数。没有可定位 tensor 字节的直接 Op→Op 依赖只保留为顺序约束，不捏造通信量。优先合并亲和量最大的相邻块，平局按左块 sgid；仅在合并后不超过 64 Op、预测 L1/UB 峰值未越过下述软保护线且亲和量为正时合并，之后重算相邻候选，直到没有可合并对。最后重新编号为连续 sgid。

**分核。** 从小 sgid 到大 sgid，先估计每个核心的累计计算量 $L_k$ 和把当前块放入核心 $k$ 后的**不同 tensor** 跨核字节 $C_{s,k}$。优先考虑满足 $L_k+W_s\le\max(1.25 W_{\rm total}/N,\max_j W_j)$ 的核心；在可选核心中先取较小 $C_{s,k}$、再取较小预计负载、最后取较小 core id。若集合为空，选预计负载最小的核心。1.25 是预注册的探索性负载保护参数，不是官方阈值或已调优数值。块内和核内仍严格按全局拓扑区间顺序排列，不能把高亲和的非相邻块任意融合；这种保守限制会错过部分潜在收益，但保持明确的无环构造。

**合法性与计算。** 相邻区间合并后依旧是全局拓扑连续区间，跨块依赖只向前；核内列表也只向前。与路线 A 一样，最终还需官方静态校验及三问 evaluator。亲和只用于候选排序，官方可能因 spill、Pipe、跨核组合依赖拒绝或给出更差 Makespan。朴素重算全部相邻合并可达 $O(K^2+|D^\star|)$；实现时宜缓存相邻亲和并用堆维护，目标约 $O((K+|D^\star|)\log K+K N)$（不含图依赖构造和容量预估）。B 应报告实际生成时间，超预算即停止该路线。

## 5. 三问的轻量代理及其失效边界

| 代理 | 计算口径 | 只用于 | 主要失效情形 |
| --- | --- | --- | --- |
| Q1 Task/边界 | 每块一个 Task；统计跨块的不同 tensor 字节，不论两块是否同核；另记录同核 100-cycle、跨核 1000-cycle 等待的依赖次数及最长代理路径 | 比较分块粒度、标记高通信区间 | 多消费者 COPY、Pipe 并行、共享 DDR 与真实 Task 激活可能使简单字节/边数预测失准 |
| Q2 同核驻留/spill | 按各核心块顺序，估计片上 tensor 从首次生产或读入到最后消费的闭区间；在各区间端点按 `pos=L1/UB` 分别累计不同 tensor `size`，取峰值 $\widehat M_{k,m}$；跨核独立计通信 | 合并与分核的软保护、解释 partition 与 spill 取舍 | 官方 Step1–3 会重排、生成边界 COPY 和 spill，预测的生命周期不是真实驻留；跨核输入的缓冲与多生产者不确定时必须标记低置信 |
| Q3 FIFO/关键路径 | 从候选的预期 COPY_IN 顺序构造 tensor-id 全量访问列表；仅对 $b_t\le1048576$ 的项模拟“未命中后插入、命中不刷新”的 FIFO；记录预期 hit bytes 与重复读；对可能在粗最长路径上的命中另估 $\max(0,\lceil b_t/60\rceil-\lceil b_t/250\rceil)$ | 识别值得由官方 Q2/Q3 成对核验的重复读与潜在服务时间差 | 真正发射/完成顺序、两个共享带宽池和关键路径由官方事件模拟决定；该差值既非 Makespan 下界也非保证收益 |

Q2 的软保护线暂取 $\widehat M_{k,\mathrm{L1}}\le0.8\times524288$、$\widehat M_{k,\mathrm{UB}}\le0.8\times131072$。0.8 不是合法性条件，只用于暂缓高风险合并；原始 tensor 已超过单区容量、生命周期无法可靠推导或预测溢出时，记录 `preview_uncertain`，保留未合并版本供官方核验，不自行插入 spill。若后续实际 `spill_added_copy_bytes` 抵消了预期 partition 节省，应修正代理，不宣称 Q2 复用成功。

Q3 代理绝不把 hit_rate 当优化目标本身。受控证据中 6000-byte hit 曾使 $T_2=1200$ 降至 $T_3=1124$，而 16-byte hit 的 $T_2=T_3=705$；后者在两种带宽下均向上取整为一个周期。Q3 的 `scheduled_copy_bytes` 与 `added_copy_bytes` 仍是逻辑量；`scheduled_copy_bytes-hit_bytes` 只是经 C 核对后使用的 DDR 服务诊断量，必须和官方 Cache 事件一并保留。

## 6. 预算内 pilot 设计（**本任务不执行**）

**固定对象。** 首轮仅 `case_019`（647 eligible Op，深度 81）和 `case_034`（3745 eligible Op，深度 26），均来自 B 的 100 图画像；先 $N=2$。每个图/核数生成：已存在的官方随机 stub seed 0、50–100 Op/块作为格式对照，以及路线 A、路线 B 各一份固定参数方案。同一方案按固定次序运行 Q1/Q2/Q3，保持 pair_key 不变。可复用已有、哈希匹配的 stub 记录；不为凑样本重跑第一轮 pilot。B-02 的官方最小调用可复用记录，但 B-02 不负责实现路线 A/B。

**分阶段上限。** 第一段最多 $2$ 图 $\times1$ 核数 $\times3$ 方案 $\times3$ 问 $=18$ 次官方调用。若两图各路线均有合法、非超时的成对记录，再按 $N=4$、随后 $N=3,5$ 的顺序扩展；无论如何不超过 $2\times4\times3\times3=72$ 次。单次 evaluator 初始限 60 秒，生成单份方案限 10 秒，全部候选加官方评估累计墙钟限 20 分钟；任一全局预算先到即停。上述上限是**未来 pilot 设计**，不是本任务的实际调用或对优化方案 runtime 的预测。60 秒超过既有 case_034 随机 stub pilot 时间，但优化 Task 的长尾未知；一旦超时，不在同轮加时重跑，也不给失败项编造成绩。B/C 可依据实际 runner 安全性提出缩小预算，扩大预算需另行记录决定。

**记录与配对。** 每次保存生成/官方评估耗时、status、timeout、输入/配置/方案/脚本哈希、原始结果、$T_p$、$\Delta B_p$、partition/spill 分量、Q3 hit/miss/total、物理 DDR 诊断量和最大 op 结束时刻；字段缺失记缺失，不估填。对于同一 pair_key，Q1→Q2 核对同核复用与 spill，Q2→Q3 核对 Cache 事件、DDR 诊断量与 Makespan。不同路线或不同 $N$ 的成绩分表呈现。单核官方基线仅在现有可信结果可用时引用；case_014/072 的 90 秒删失单核不写成数字，本 pilot 不调用它们。

## 7. 筛选、停止条件与独立证伪

1. **立即停用单个方案：** JSON/官方静态检查失败，任一必需场景 evaluator 失败或超时，哈希不一致，或生成超过 10 秒。失败只淘汰该图/核数下的方案实例；不能由两张图否定整个路线。
2. **同条件比较：** 先列合法方案在各问题的 $(T_p,\Delta B_p)$ 及运行时间。若方案 X 在同图同核同问题的 $T$ 与 $\Delta B$ 均不优于 Y 且至少一项严格更差，X 在该条件下被 Pareto 支配；不以未验证的代理替代官方数值。时间成本较高时另列运行预算风险，不藏入得分。
3. **Q2 机制：** 同一 pair_key 下报告 $T_1-T_2$、partition/spill COPY 变化；若同核复用预计收益被 spill 抵消，标 WARN 并定位 tensor 生命周期，不声称 Q2 净收益。
4. **Q3 机制：** 同一 pair_key 下报告 $T_2-T_3$、命中/未命中字节及关键路径证据。`hit_bytes>0` 但 $T_2=T_3$ 是可接受的 WARN；如果只有方案变化而无同方案收益，不把它写成 L2 加速。
5. **全局停止：** 达到调用、单次或总墙钟预算；两路线都无合法候选；或 B/C 发现字段来源、配对哈希、官方程序版本相互矛盾。保留原始失败/删失记录，交由 A 决定下一轮缩小范围或修订路线。

**给 B 的可实现接口。** 在 B-02 runner 字段稳定后，另立实现任务；它接收 graph/config/N/固定参数，输出确定性 `solution.json` 与 sidecar，不改官方包，调用前先做静态校验。方案生成与 evaluator 的墙钟分开计时；大日志留 `result/**`，小型哈希与汇总放 L2。B 不需要按本文件自行决定正式 100 图实验或最优路线。

**给 C 的反例接口。** 对两路线分别检查：微块合并后是否仍覆盖全部 $O^\star$ 且只含连续拓扑区间；调度是否因重复 sgid、逆序依赖或官方全局执行环而被拒；Q2 预测驻留低但官方发生 spill 的案例；Q3 预测 hit 但实际 FIFO 顺序改变、或 hit 存在而 Makespan 不变的案例。C-02 可用旧受控证据和任务卡允许的一个小图，不能把本设计代理自我验证为 PASS。

## 8. 结论边界与待处理风险

- 两条路线仅是有边界、可证伪的原型候选。路线 A 的分块粒度、路线 B 的 32/64/0.8/1.25 参数均未调优；没有赢家、平均加速或正式 100 图结果。
- 静态拓扑区间保证不了官方扩展执行图合法；容量代理、COPY 字节代理和 FIFO 代理也不能取代官方 evaluator。
- B 的八图随机 stub 画像只提示评价成本长尾：case_014 两核 Q2/Q3 约 56 秒，单核 case_014/072 在 90 秒限时下删失。不同切图可能显著改变成本，因此本任务不预测 72 次 pilot 的实际总耗时。
- Q2 的理论同核复用可被 spill 抵消；Q3 的命中可不在关键路径；降低 Makespan 可能提高逻辑 COPY。若 pilot 出现异常但真实的结果，先保存证据交 C 独立核查，路线切换或 MODEL FREEZE 仍遵守人类队长决策门槛。
