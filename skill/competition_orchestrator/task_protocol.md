# 任务协议

每张任务卡只解决一个清晰目标，禁止“完成全部 Q1”之类的宽泛任务。

必填字段：`TASK ID`、`Owner`、`Priority`、`Status`、`Depends On`、`Goal`、`Context`、`Inputs`、`Allowed Files`、`Forbidden Files`、`Expected Outputs`、`Validation`、`Completion Criteria`、`Handoff Target`。

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
