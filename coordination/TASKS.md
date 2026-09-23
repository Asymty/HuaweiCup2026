# TASKS — Phase 1: Problem Formalization

FINAL PROBLEM = A。以下三个 P0 任务均已就绪，状态为 TODO；三者无相互完成依赖，可在各自独立分支同时开始。共同前提 DECISION-001 已由人类队长确认。任务开始前各 Owner 仍须依 AGENTS.md 同步 main、检查 Git、建立自己的短分支。官方题包和 data/raw/ 只读；Gate 结果仅作参考，不进入正式结果表。

## TASK-A-01

- Owner: Codex A
- Priority: P0
- Status: TODO
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
- Status: TODO
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
- Completion Criteria: 任一 pilot 可从命令重现并找到原始输出和汇总行；100 图画像完整；给出长尾分层、超时与全量成本估算及其不确定性；状态页列出实际参数、用例、时间和异常，不把 pilot 外推为正式总体成绩。
- Handoff Target: Codex A（路线与成本决策）、Codex C（独立核查）；完成时序列化追加 coordination/HANDOFF.md。

## TASK-C-01

- Owner: Codex C
- Priority: P0
- Status: TODO
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
- Completion Criteria: 验证矩阵能分别证伪 Q1/Q2/Q3 的错误解释，PASS / WARN / FAIL 有实际日志或可复现命令；状态页列出开放风险，未把 Gate 结果冒充正式结论。
- Handoff Target: Codex A（模型修订与决策）、Codex B（实验口径）；完成时序列化追加 coordination/HANDOFF.md。

## 文件互斥约定

A 主写 MASTER_PLAN/DECISIONS/TASKS 和 A 模型接口；B 主写预处理、官方 runner 与正式运行结果；C 主写独立合法性/指标审计及验证结果。B/C 虽均在 src/evaluate/ 下工作，但具体文件名互不相同，禁止顺手改对方文件。各角色仅主写自己的状态页；HANDOFF.md 在任务完成后按交接协议顺序追加，不并发覆盖。凡需要跨边界改动，先在状态页说明并由 A 调整任务卡。
