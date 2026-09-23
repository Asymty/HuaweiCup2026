# A 题统一数学形式化与模型接口（TASK-A-01）

- 状态：Phase 1 形式化接口；MODEL FREEZE = FALSE；本文不是正式算法或论文结论。
- 适用题目：A 题《通用神经网络处理器下的多核调度问题》的 Q1/Q2/Q3。
- 权威来源：本地 `题目/中文题目/A题/` 的正式题面与原始附件 ZIP；只读解压副本 `official_bundle/` 中的 README.md、docs/、data/config.txt、code/stub_multicore_cut_and_schedule.py、code/evaluation_validation.py、code/multicore_cut_evaluate_problem_1.py、problem_2.py、problem_3.py、code/schedule_step1/2/3.py。原始 ZIP 不修改，整个 `题目/` 不入 Git；`result/**/official_bundle/` 仅是运行副本。官方评估器的实际判定优先于本文的简化表达。
- 证据边界：result/a_feasibility_gate/GATE_REPORT.md 只证明 Gate 的局部可行性。其两例改善不得用作全部 100 图的总体结论。
- 术语约定：选手方案只含切图与子图的分核、排序；Task、COPY、spill、逐 Pipe 顺序、L2 状态是官方评估器派生的执行对象。本文用“方案变量”与“派生状态”分别标记，避免让 B 实现不存在的 JSON 字段。

## 1. 对象、符号与官方字段

| 对象 | 数学符号 | 官方图 / 方案字段 | 作用 |
| --- | --- | --- | --- |
| Graph | $G=(O\dot\cup T,E)$ | 图 JSON 顶层 ops、tensors、edges | 有向无环数据流图；节点 id 在 op/tensor 间全局唯一 |
| Op | $o\in O$ | ops[i].id、op、pipe、cycles | op 为类型，pipe 为四条流水线之一，cycles 为计算参考周期 |
| Tensor | $t\in T$ | tensors[i].id、pos、size | pos 为 DDR/L1/UB；size 是非负字节数 |
| Edge | $e=(u,v)\in E$ | edges[i].source、target | 题面以 Tensor→Op、Op→Tensor 为主，数据量由 tensor.size 给出 |
| 可切分 Op | $O^\star=\{o\in O:\mathrm{type}(o)\notin\{\mathrm{COPY\_IN},\mathrm{COPY\_OUT}\}\}$ | node_to_subgraph 的全部键 | 原有 COPY 节点不由选手分配 sgid |
| Subgraph | $S_s=f^{-1}(s)$，$s\in\mathcal S$ | node_to_subgraph: 十进制 op id 字符串 → 非负整数 sgid | 方案变量 $f:O^\star\to\mathcal S$，sgid 不要求连续 |
| Core | $k\in\{0,\ldots,N-1\}$ | core_schedules 的外层数组下标 | $N$ 等于该数组长度；正式多核比较为 2–5 核 |
| Core assignment | $c(s)=k$ | sgid 出现在哪个 core_schedules[k] | 由每个 sgid 的唯一出现位置推导，无单独 JSON 字段 |
| Core schedule | $\pi_k=(s_{k,1},\ldots,s_{k,m_k})$ | core_schedules[k] | 方案变量：核心 $k$ 的 sgid 执行顺序；空列表合法 |
| Task | $\mathcal T_{p,j}$ | 评估器按 problem 从方案构造；方案无 Task 字段 | Q1 每 sgid 一个 Task；Q2/Q3 每核心合并一个 Task |
| 执行时间线 | $F_v$ 为扩展执行 op 的结束周期 | 结果 JSON 的 makespan、Trace、各 Task/Op 时间字段 | 由官方 Step1–3 与多核事件模拟计算，不由方案直接给出 |

原图 JSON 至少含 tensors、ops、edges；tensor 属性为 id/pos/size，op 属性为 id/op/pipe/cycles，edge 属性为 source/target。题面要求二部图；官方校验器实际允许直接 Op→Op 边，并在依赖推导中处理它，同时拒绝 Tensor→Tensor 边。因此 B 的解析器和 C 的检查应以官方校验器为准，不可只依赖严格二部图假设。NEEDS B/C VALIDATION：100 张正式图是否实际含直接 Op→Op 边。

四条 Pipe 为 PIPE_MTE2、PIPE_MTE3、PIPE_M、PIPE_V；官方 Step3 每核每 Pipe 同时最多一条在途指令。COPY_IN/COPY_OUT 若访问 DDR，共同争用固定 60 bytes/cycle DDR 总带宽；计算 op 使用图中 cycles。Step3 的单 Task 局部时间只用于确定顺序，不能替代最终多核 Makespan。

## 2. 方案 JSON 与共同合法性

参赛方案必须是 UTF-8 JSON，顶层**恰好**含 node_to_subgraph 与 core_schedules 两字段。最小示例沿用官方题面附录 B 的图：仅一个非 COPY 操作，id=11，分配到核心 0；核心 1 空闲。

~~~json
{
  "node_to_subgraph": {"11": 0},
  "core_schedules": [[0], []]
}
~~~

对于任意输入图，构造依赖视图 $H=(O^\star,D^\star)$：先按官方规则由原图 tensor 生产者/消费者与可能的直接 Op→Op 边得到 Op 依赖，再收缩不参与切图的 COPY_IN/COPY_OUT 节点。这里的 $D^\star$ 以官方 derive_multicore_plan 的依赖视图为准；不把普通图遍历得到的任意弱连通关系误写为数据前驱。

共同的可提交方案约束：

$$
\operatorname{dom}(f)=O^\star,\quad f(o)\in\mathbb Z_{\ge0},\quad
\mathcal S=\{f(o):o\in O^\star\}.
$$

JSON 键必须是对应 op id 的十进制字符串；不同文本键转为同一整数 id 也非法。令 $\pi_0\Vert\cdots\Vert\pi_{N-1}$ 为各核列表串接，则

$$
\forall s\in\mathcal S:\quad
\sum_{k=0}^{N-1}\sum_{j=1}^{m_k}\mathbf 1[\pi_{k,j}=s]=1,\qquad
\forall s\notin\mathcal S:\quad
\sum_{k=0}^{N-1}\sum_{j=1}^{m_k}\mathbf 1[\pi_{k,j}=s]=0
$$

表示每个 sgid 恰好出现一次且无额外 sgid；各 $\pi_k$ 可为空。程序判定是串接列表的长度与去重长度相等，且其集合等于 $\mathcal S$。

子图依赖边集由 $D^\star$ 投影：

$$
D_{\mathcal S}=\{(f(u),f(v)):(u,v)\in D^\star,\ f(u)\ne f(v)\}.
$$

$(\mathcal S,D_{\mathcal S})$ 必须无环。同核顺序不能逆转其依赖。Q1 还将相邻 Task 顺序边并入依赖图检查无环；Q2/Q3 的核内 Pipe FIFO、存储复用与跨核 COPY 组合执行图也须无环。即使上述静态条件满足，后续 Step2/3 或全局执行检查仍可能拒绝方案；官方 evaluator 的零退出码和结果 JSON 才是最终合法性证据。原图需满足唯一非负整数 id、有效端点、非负 size/cycles、合法 pos/pipe、无重复边且无环等校验。

L1 = 524288 bytes，UB = 131072 bytes 是**执行期硬容量**。官方 Step2 在必要时插入 spill，若单个张量过大或没有合法换出对象，Task 仍会失败。不能仅因原始子图工作集超过缓存就直接判方案无效，也不能假定 Step2 总能修复容量问题。

## 3. 共用的评估关系与指标

设 $P=(f,\pi_0,\ldots,\pi_{N-1})$，$\theta$ 为不得修改的官方 config；$p\in\{1,2,3\}$ 表示问题。正式评估关系写为

$$
R_p=\operatorname{OfficialEval}_p(G,P;\theta),\qquad
T_p(G,P;\theta)=R_p[\mathrm{makespan}]
=\max_{v\in O_p^{\mathrm{expanded}}}F_v.
$$

$O_p^{\mathrm{expanded}}$ 包括官方重建的边界 COPY 与必要 spill。Makespan 依赖各 Task 的激活、数据依赖、每核四条 Pipe、L1/UB 驻留、共享 DDR 带宽和 Q3 的共享 Cache 池，不能用各核计算 cycles 总和或 Step3 的 local_makespan 直接替代。官方同时返回结果 JSON、Perfetto Trace 和简短日志；非法方案以非零退出码及 EVALUATION ERROR 拒绝，不给有效成绩。

官方次指标取结果 JSON 的 data_movement_bytes：

$$
\Delta B_p
=B_{p,\mathrm{scheduled\_copy}}
-B_{\mathrm{original\_graph\_copy}}
=B_{p,\mathrm{partition\_added}}+B_{p,\mathrm{spill\_added}}.
$$

$\Delta B_p$ 对应 added_copy_bytes。B 应保留其分量字段而非自行估算。Q3 的 Cache 命中会改变 COPY_IN 实际走 Cache 读带宽池还是 DDR 带宽池，但不应假设它必然改变上述按调度 COPY 统计的 added_copy_bytes。

**逻辑搬运与物理 DDR 服务分开记录。** 官方 `scheduled_copy_bytes` 与 `added_copy_bytes` 统计调度生成的 COPY 字节，Q3 命中仍保留该条逻辑 COPY。C 的受控同方案 Q2/Q3 对照中，按 `scheduled_copy_bytes - cache_stats.hit_bytes` 重算的 DDR 服务字节为 $30000\to24000$，但两侧 `added_copy_bytes` 均为 $18000$。这个重算量是由官方 COPY 和 Cache 计数导出的诊断指标，不是官方独立评分字段；正式图须保留原始 COPY 分量、Cache 事件与时间线，并核对 COPY 路径后使用，不能把它与 $\Delta B_p$ 混称。

**扩展执行图的共同资源约束。** 若 $S_v,F_v$ 为官方扩展 op 的发射与完成时刻，依赖边 $u\to v$ 至少要求 $S_v\ge F_u$（跨核 COPY 或 Task 激活另加该场景规定的延迟）。对每核 $k$、每条 Pipe $p$ 和任一时刻 $\tau$，同 Pipe 在途 op 数不超过 1；对私有存储的实际驻留集合 $\mathcal R_{k,m}(\tau)$，有

$$
|\mathcal A_{k,p}(\tau)|\le 1,\qquad
\sum_{t\in\mathcal R_{k,\mathrm{L1}}(\tau)}b_t\le 524288,\qquad
\sum_{t\in\mathcal R_{k,\mathrm{UB}}(\tau)}b_t\le 131072.
$$

对某共享带宽池 $r$，若时刻 $\tau$ 有 $n_r(\tau)$ 个在途搬运，官方按池内公平共享推进每个搬运的剩余参考工作量，而不是给每个核心各分配一份完整带宽。DDR 池总带宽为 60 bytes/cycle；Q3 的 CACHE_READ 池为独立的 250 bytes/cycle。存储分配/释放、spill、FIFO Pipe 次序及公平共享的确切事件顺序仍以官方模拟为准，以上不等式不能单独当作一个自写评分器。

正式单核参照 $T_{\mathrm{single}}(G)$ 来自官方 singlecore_evaluate.py，而不是把随机多核示例当作基线。对相同图和 $N$ 核，Q1/Q2 的加速比为 $T_{\mathrm{single}}(G)/T_p(G,P_N)$；Q3 报告相同核数下 $T_2(G,P_N^{\mathrm{noL2}})/T_3(G,P_N^{\mathrm{L2}})$，比较时必须注明两边是否使用同一方案。平均曲线的具体跨用例聚合口径应由 B/C 对照正式题面复核，不能把“平均单核时间 / 平均多核时间”擅自当成“逐例加速比的平均”。

后续目标层次暂定为：先保证合法且能在合理预算内生成、评估，再尽量降低官方 Makespan，同时控制 $\Delta B_p$，最后说明 Q2/Q3 机制的独立贡献。没有官方给出的固定加权和系数，不人为发明总分或宣称全局最优。

**评估成本也是方案筛选约束。** B 的 8 图 × 3 问、2 核 stub pilot 中，case_014 的 Q1/Q2/Q3 分别为 36.58/56.40/56.65 秒；同图与 case_072 的官方 singlecore 在 90 秒限时下未完成。该结果只表明 evaluator 存在图与 Task 结构相关的长尾，不能外推为任意优化方案的耗时。后续算法须限制候选 Task/子图规模、限制官方调用次数，分开记录方案生成和 evaluator 时间，并对超时结果作删失记录；120 秒多核、600 秒大 Task/单核仅是待验证的工程预算建议。


## 4. Q1：场景 A 的切图与多核 Task 调度

**输入与输出。** 输入为 $G$、官方 $\theta$、核心数 $N$；输出仍是仅含 $f$ 与 $\pi_k$ 的方案 JSON。官方 problem_1 evaluator 再输出 Makespan、added_copy_bytes、结果 JSON/Trace/日志。原图 COPY_IN/COPY_OUT 不参与 $f$。

**方案决策。** 同时选择子图集合 $\{S_s\}$、每个子图的核心 $c(s)$ 和每核顺序 $\pi_k$。三者不可拆成互不相关的优化，因为跨子图依赖决定 COPY 与等待，核心分配决定并行/跨核通信，同核顺序决定 Task 串行和缓存清空次数。

**Task 与边界。** 官方构造 $\mathcal T_{1,s}=S_s$，即每个子图一个 Task。跨子图数据即使发生在同一核心，也不能直接驻留到下一个 Task，需按关联 tensor.size 建立 DDR 边界 COPY；图输入、最终输出同样按官方规则重建。B 不能简单将“跨核边条数”当作 Q1 的全部额外搬运量，因为同核跨 Task 也会搬运，且一个 tensor 被多个 Task 使用时可能重复读取。

**执行约束。** 共同合法性约束之外，Q1 将同核相邻 Task 顺序边与子图依赖边合并检查无环。对相邻同核 Task $a\prec_k b$，其激活至少满足

$$
A_b\ge F_a+100.
$$

对跨核依赖前驱 Task $a\to b$，至少满足

$$
A_b\ge F_a+1000.
$$

这只是 Task 激活下界；实际 $A_b$ 取全部条件的最大值，实际结束时刻还受边界 COPY、四 Pipe、L1/UB、spill 与所有核共享 60 bytes/cycle DDR 带宽影响。不得以这两条不等式单独计算最终 Makespan。

**目标。** 以官方 $T_1(G,P;\theta)$ 为主目标，$\Delta B_1$ 为次指标；在合法性和计算预算可接受前提下改进。Q1 的方案可供 Q2/Q3 复用接口，但 Q1 双核负载均衡本身不构成后两问机制贡献。

## 5. Q2：场景 B 的 Task 合并与片上复用

**沿用的方案变量。** 仍仅提交 $f$、$c(s)$ 的隐式位置和 $\pi_k$，方案 JSON 完全不变。Q2 没有必须新增的独立提交字段；不能把“是否保留 tensor”或“插入哪条 COPY”塞进方案 JSON。

**新增的执行对象。** 官方对每个核心构造一个合并 Task：

$$
\mathcal T_{2,k}
=\bigcup_{s\in\pi_k}S_s ,
$$

其中 $\pi_k$ 决定同核子图在该 Task 内的相对执行顺序；空核可有空 Task。原属不同子图而被分到**同一核心**的生产者与消费者，可在 L1/UB 中通过同一个局部 tensor 通信，不再为这个边界插入 Q1 的 Task 间 DDR COPY。该复用能否保留，仍受 L1/UB 生存期与容量约束；Step2 可能为长驻留 tensor 插入 spill，从而抵消理论节省。

**跨核机制。** 只有跨核心的数据依赖需由源核 COPY_OUT、目标核 COPY_IN 及固定 500-cycle 同步延迟串接；目标 COPY_IN 在源 COPY_OUT 完成并等待 500 cycles 后才可能就绪。原始 DDR 输入可能被每个消费核心各自读入；对某 tensor 的跨核通信由官方按实际源核—目标核连接构造，不能用单纯“跨子图边数 × tensor.size”代替。COPY 和 spill 仍竞争共享 DDR 带宽。

**模型中需新增而不提交的派生状态。** 可用 $\rho_{t,k}(\tau)\in\{0,1\}$ 表示时刻 $\tau$ tensor $t$ 在核心 $k$ 的 L1/UB 驻留，用 $\chi_{t,k\ell}$ 表示 $t$ 的生产与消费跨越源核 $k$、目标核 $\ell$，用 $L_{t,k}$ 表示驻留生存期。这些用于构造通信/容量代价代理或解释结果；真实 $\rho$、spill 与 COPY 集由官方 Step1–3 和事件模拟确定，不是可直接写入 JSON 的新决策。容量条件应施加在官方扩展执行过程中，而非假设“同核总 tensor 大小必须小于 L1/UB”。

**Q2 专属验证命题。** 需选择存在“跨子图、同核心、可复用 tensor”的合法方案，在**同一图、同一 $N$、同一 JSON 方案**下分别运行 Q1/Q2，核对 Task 边界 COPY、spill、$\Delta B$ 与 $T$。若两问只得到相同负载均衡收益，尚不能宣称 Q2 同核复用有效。NEEDS B/C VALIDATION：哪些正式图与切分粒度能产生独立、稳定的 Q2 收益；复用可能因额外驻留/spill 而净收益为零或为负。

C 的官方受控图已验证这一机制**能够生效**：同图、同核数、同方案的 Q1→Q2 得到 Makespan $800\to400$、scheduled COPY $30000\to12000$、added COPY $18000\to0$，该例无 spill。它不证明正式 100 图的平均净收益；若合并后张量生存期加长并触发 L1/UB spill，节省的边界 COPY 可能被抵消。因此 Q2 候选方案不能机械沿用 Q1 最优切分，应同时考察同核亲和、驻留生存期、容量峰值、spill 与跨核通信。

## 6. Q3：场景 B 加共享只读 L2

**沿用与新增。** Q3 沿用 Q2 的 $f$、$c(s)$、$\pi_k$、每核一个 Task、同核复用、跨核 COPY 与 500-cycle 同步。方案 JSON 仍无 Cache 控制字段。新增的派生状态为共享 Cache 队列 $Q(\tau)$、COPY_IN 的命中标记 $h_i$、Cache/DDR 两个并发带宽池及访问时间；这些状态由方案影响但由官方模拟生成。

**传输单位与 Cache key。** 官方代码在 COPY_IN 发射时提取该搬运关联的核内 tensor，其 key 为 logical_tid（若有）或 tensor id，其容量占用和计数字节均取该 tensor 的完整 size。**题面及代码没有固定字节数的 cache line；不得自设 64 B 等行大小。**一个 tensor 大于 1048576 bytes 时不缓存。COPY_OUT 不查询只读 Cache。

**命中、未命中与 FIFO。** 当符合条件的 COPY_IN 发射时，若 key 已在 $Q(\tau)$，则为命中，使用共享 250 bytes/cycle 的 CACHE_READ 池，不占 DDR 池；命中不会把条目移至队尾。否则为未命中，走共享 60 bytes/cycle DDR 池；该 COPY_IN 完成后，若整个 tensor 可放入缓存，则先逐个淘汰最早进入者直至有容量，再插入。Cache 与 DDR 各自对同时在途访问公平分摊带宽；一次独占传输的参考工作量约为 $\max(1,\lceil b_i/\beta\rceil)$ cycles，真实完成时刻仍由事件模拟按争用重算。

**按字节的命中率。** 对官方统计的 COPY_IN 访问集合 $\mathcal I$（key 非空且传输字节数大于零；超出 Cache 容量的 tensor 也计入未命中），设 $b_i$ 为传输字节数，则

$$
B_{\mathrm{hit}}=\sum_{i\in\mathcal I}h_i b_i,\qquad
B_{\mathrm{miss}}=\sum_{i\in\mathcal I}(1-h_i)b_i,\qquad
H_3=\frac{B_{\mathrm{hit}}}{B_{\mathrm{hit}}+B_{\mathrm{miss}}}
$$

在分母为零时官方令 $H_3=0$。结果字段为 cache_stats.hit_bytes、miss_bytes、hit_rate，并另有 copy_in_hits/misses 计数；不能把计数命中率冒充字节命中率。

**作用路径与目标。** L2 只可能通过“COPY_IN 走更快且独立的 CACHE_READ 池、减少 DDR 池争用”改变关键路径和 $T_3$。若命中发生在非关键路径、读带宽池本身拥堵，或其他资源决定 makespan，则 $H_3>0$ 仍可能 $T_3=T_2$；官方的 added_copy_bytes 也可能不变，因为它统计的是调度生成的 COPY 字节而非命中后实际经过 DDR 的字节。Q3 的目标不是盲目最大化 $H_3$，而是在容量/FIFO 窗口和共享输入复用下改善官方 $T_3$ 并解释 $\Delta B_3$。

**Q3 专属验证命题。** 使用同一图、同一 $N$、同一方案成对运行 problem_2（无 L2）和 problem_3（只读 L2），核对 Cache 事件、命中字节、COPY_IN 路径与 $T_2/T_3$。若要比较 Q3 专属方案与 Q2 方案，另做方案变化对照，防止把重新分核产生的收益误归因于 L2。NEEDS B/C VALIDATION：正式用例中是否存在可复现的 $T_3<T_2$，及其与 hit bytes、DDR 争用和关键路径的关系。

C 的受控同方案 Q2→Q3 对照已得到 Makespan $1200\to1124$、命中 $6000$ bytes、字节命中率 $1/3$，而 added COPY 保持 $18000$。另一个 $16$ bytes 命中案例仍为 $705\to705$。这只证明 Cache 可改变传输路径和关键路径时延；正式算法应优先考虑可在 FIFO 驻留窗口内被重复读取、且读取位于关键路径或 DDR 拥堵区间的 tensor，而不是单独最大化 hit rate。FIFO 命中不刷新队列顺序，映射和调度都可能改变后续命中机会；正式图上的独立收益仍待评估。


## 7. 三问共用的数据结构与算法接口契约

本任务只定义接口，不新增最终算法代码。B 可以据此建立 runner，C 可以据此写独立检查器；两者均应以官方输入/输出为最终契约。

| 阶段 / 建议接口 | 输入 | 输出与不变量 | 谁负责 |
| --- | --- | --- | --- |
| load_graph(path) | 官方 case JSON 路径（只读） | GraphView：ops、tensors、edges、id 索引、tensor.size/pos、op.pipe/cycles；不得改写原图 | B 实现，C 核查 |
| derive_op_view(graph) | GraphView | $O^\star$ 和按官方 COPY 收缩规则得到的 Op 依赖 $D^\star$；保留直接 Op→Op 兼容性 | A 定义，B 实现，C 对官方校验器复核 |
| propose_partition(graph, N, scene, budget) | GraphView、核心数、场景、时间预算 | $f:O^\star\to\mathcal S$；每个可切分 op 有且仅有一个 sgid，子图依赖无环 | 后续模型实现；TASK-A-01 不实现求解器 |
| assign_and_order(graph, f, N, scene) | 图、划分、核数、场景 | 长度 $N$ 的 $\pi_k$，sgid 恰好出现一次，同核顺序与全局依赖兼容 | 后续模型实现 |
| derive_task_preview(graph, f, $\pi$, scene) | 已有划分、分核、顺序 | Q1 一子图一 Task；Q2/Q3 一核一 Task 的通信与容量代价**预测**，仅用于方案选择 | 后续模型实现；不得代替官方构造 |
| emit_plan(f, $\pi$) | 已检验的映射与顺序 | **仅** node_to_subgraph、core_schedules 两字段的 UTF-8 JSON；字符串 op id、整数 sgid | B/模型实现，C 核查 |
| run_official(problem, graph_path, plan_path, config_path) | 原图、方案、原始 config 与隔离输出目录 | 官方 result JSON/Trace/log、退出码、wall time；记录原始 COPY 分量、Q3 Cache 分量、哈希与超时；禁止改评估器 | B 实现 |
| audit_result(graph, plan, result) | 原图、方案、官方结果 | 合法性及 Makespan、$\Delta B$、Q3 hit_rate 的独立核查，PASS/WARN/FAIL | C 实现 |

**真实顺序。** 用户侧方案生成是

Graph input → Op 依赖视图 → partition → core assignment → core schedule → solution JSON → official evaluator → metrics。

Task construction 依赖具体的 core assignment 与 core schedule；因此若模型内部需预测 Task，应在它们确定后调用 derive_task_preview。**权威** Task construction、Step1–3 核内调度及全局事件模拟发生在 solution JSON 提交给官方 evaluator **之后**。这解释了为什么“先 Task construction 再 core assignment”的线性接口无法直接等同于官方程序顺序。

三问共用一份 PlanSpec，按 problem=1/2/3 选择不同评估器；不得为 Q2/Q3 添加自定义 Task 或 Cache 字段。B 的 runner 应把 scenario、N、case、方案文件哈希、固定 config 哈希、评估器文件标识、退出码、timeout、墙钟时间及结果路径并列记录，保证 C 能做**同方案**成对对照。N 与 core_schedules 长度必须一致；官方会从数组长度推断核心数，若外部请求 N=4 却输出两个列表，程序会按 2 核评估，属于 runner/方案接口错误。

官方 CLI 契约：分别调用 code/multicore_cut_evaluate_problem_1.py、problem_2.py、problem_3.py，传入图路径、方案路径、显式 --config 固定配置和独立的 -o / --trace-output / --log-output 路径。单核参照调用 code/singlecore_evaluate.py。默认方案文件名为 <case>_multicore_res.json；正式 runner 宜显式传路径，避免不同问题或核心数覆盖同名文件。非法、异常或超时记录不得进入成功成绩表。

## 8. 可证伪的检查点与假设审计

| 命题 | 状态 | 依据 / 待证内容 | 接收方 |
| --- | --- | --- | --- |
| 方案 JSON 恰好两字段；可切分 op 完整映射、sgid 唯一调度 | CONFIRMED | 题面附录 B、官方 derive_multicore_plan；C 仍须覆盖负例 | B/C |
| 原图题面称二部图，但官方解析兼容直接 Op→Op | CONFIRMED（代码） / NEEDS B/C VALIDATION（100 图出现频率） | evaluation_validation.py 与 schedule_step3.py；B 画像、C 对照解析 | B/C |
| Q1 每子图一 Task；Q2/Q3 每核一 Task | CONFIRMED | 三个官方 evaluator 的任务构造函数 | B/C |
| Q2 同核复用机制可在受控图上降低 Makespan 与 $\Delta B$ | CONFIRMED（受控图） / UNVERIFIED（100 图净收益） | C 同方案 Q1/Q2：$800\to400$，added COPY $18000\to0$；正式图的 spill 抵消率待证 | B/C |
| Q3 L2 命中可在受控图上产生独立时延收益 | CONFIRMED（受控图） / UNVERIFIED（100 图净收益） | C 同方案 Q2/Q3：$1200\to1124$，hit $6000$ bytes；$16$ bytes 命中无时延收益 | B/C |
| 图与 Task 结构影响 evaluator 成本 | PARTIALLY CONFIRMED | B 8 图分层 pilot 与单核 90 秒删失支持长尾；完整 runtime 分布及优化方案成本未证 | B |
| 降低 Makespan 所需的额外搬运 trade-off 可由固定权重刻画 | UNVERIFIED | 官方未给权重；先分别记录 $T_p$ 和 $\Delta B_p$，必要时呈现 Pareto 对照 | B/C |
| 更高 Cache hit_rate 必然降低 Makespan 或 added_copy_bytes | REJECTED AS ASSUMPTION | 官方两种带宽池、关键路径与逻辑 COPY 统计使此推论不成立 | B/C |
| Gate 两例约 49% 收益代表全部 100 图 | REJECTED AS ASSUMPTION | Gate 只有 case_001、case_019，且 Q2/Q3 专属收益未验证 | 全员 |

C 至少应设计三类可证伪场景：①跨子图同核 tensor，使 Q1 的 Task 边界搬运与 Q2 同核驻留机制不同；②跨核共享同一输入且访问顺序可能导致 Cache 命中，使 Q2/Q3 的访存路径不同；③有 hit bytes 但关键路径不变，使“命中即加速”的错误推断暴露。B 将场景和正式图分层，保存逐例原始结果。场景设计与检验由 C 独立完成，A 不代替 C 宣布 PASS。

## 9. TASK-A-01 的最小落地核验与交接

**官方题面最小图。** 原图含 DDR tensor 1、UB tensor 2/3、DDR tensor 4，以及 COPY_IN op 10、ADD op 11、COPY_OUT op 12；边为 1→10→2→11→3→12→4。第 2 节的方案只映射 op 11。它同时证明：原有 COPY 不得写入 node_to_subgraph、空核心列表允许、Task/Cache 无须 JSON 字段。题面附录给出三问固定配置下 Makespan 6 cycles、原图及调度 COPY 各 32 bytes、added_copy_bytes 0、Cache 命中 0。验证时应以未修改官方代码复算，而不把该样例当性能 baseline。

**交接给 B。** 读取第 1–7 节，将 GraphView、PlanSpec 和 runner 的记录字段落地；先以官方最小图和代表性 pilot 验证严格 JSON、核心数、结果字段、异常/超时分流。尤其不要用局部 Step3 makespan 或简单总 cycles 作为官方得分；保留 Q1/Q2/Q3 同方案评估能力及输入哈希。B 的大型图成本画像和全量时间估计属于 TASK-B-01。

**交接给 C。** 读取第 2、5、6、8 节，独立对照官方 validator 建立负例与成对机制检查；检查 Q2 的同核复用条件、Q3 完整 tensor FIFO 及字节命中率，区分 Cache hit 与 Makespan 改善。对本文标记 NEEDS B/C VALIDATION 的命题给出 PASS/WARN/FAIL、可复现输入/命令和风险建议。C 的独立结论属于 TASK-C-01。

**收束条件。** 本文只冻结字段与官方语义的工作接口，不冻结算法路线。若 B/C 发现题面与代码实现差异或异常但真实的评估结果，先保留原始证据并在各自状态页提出；A 再依据交接审阅并记录后续决策。TASK-A-01 完成不自动进入 Phase 2，也不授权论文结论。
