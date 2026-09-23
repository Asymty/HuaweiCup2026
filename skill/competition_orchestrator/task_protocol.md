# 任务协议

每张任务卡只解决一个清晰目标，禁止“完成全部 Q1”之类的宽泛任务。

必填字段：`TASK ID`、`Owner`、`Priority`、`Status`、`Depends On`、`Goal`、`Context`、`Inputs`、`Allowed Files`、`Forbidden Files`、`Expected Outputs`、`Validation`、`Completion Criteria`、`Handoff Target`。

每个正式任务的 `Completion Criteria` 还必须写明 `EVIDENCE SHARED = PASS`：按 [handoff_protocol.md](handoff_protocol.md) 提供可移植的 L2 最小证据包，并在存在大型原始结果时给出 L3 共享位置。`Status: DONE` 表示 Owner 完成实现，不自动等于 A 的正式 `ACCEPT`。A 仅在 `IMPLEMENTATION = DONE`、`VALIDATION = PASS`、`EVIDENCE SHARED = PASS` 且关键抽查一致时正式接受 B/C 任务；证据尚未交接记为 `FORMAL ACCEPTANCE = EVIDENCE_PENDING`，不因本机缺少 gitignored 的 `result/**` 直接判 `REVISE` 或 `REJECT`。

Status 只能是 `TODO`、`IN_PROGRESS`、`BLOCKED`、`DONE`、`SUPERSEDED`。编号采用 `TASK-A-01`、`TASK-B-01`、`TASK-C-01`。

~~~markdown
## TASK-B-01
- Owner: Codex B
- Priority: P0
- Status: TODO
- Depends On: TASK-A-01
- Goal: 为 Q1 已确认目标建立可复现 baseline
- Context: 使用 A 已冻结的输入、输出和评价定义
- Inputs: data/raw/...；coordination/DECISIONS.md 对应决策
- Allowed Files: src/model/baseline.py；result/Q1/；tests/
- Forbidden Files: paper/Latex/sections/；data/raw/
- Expected Outputs: baseline 指标、运行参数、结果文件路径
- Validation: hold-out 与五折交叉验证均可复现
- Completion Criteria: 命令成功、指标落盘、状态页记录证据
- Handoff Target: Codex C
~~~
