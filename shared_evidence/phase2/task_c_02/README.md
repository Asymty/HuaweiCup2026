# TASK-C-02 原型接受门槛证据

本目录记录 TASK-C-02 的独立接受矩阵和一次最小官方合同核验。接受矩阵由已正式验收的 C-01 L2 证据机械生成；官方核验只使用一个最小图，并未重跑 C-01 机制套件，也未启动正式 100 图实验。

## 接受规则

- 机制归因模式要求 Q1↔Q2 或 Q2↔Q3 两侧具有相同 `case_id`、输入哈希、config 哈希、核数和 `plan_sha256`，且两侧独立合法、指标代数一致。
- Q2↔Q3 同方案还要求原始、scheduled 和 added COPY 三个逻辑搬运字段不变；物理 DDR 按 `scheduled_copy_bytes - cache_hit_bytes` 独立核对。
- plan hash 或核数发生变化时，只能标为 `REDESIGN_ONLY`，不得把差值归因于 Q2 Task 合并或 Q3 shared L2。
- Cache 命中字节大于零而 Makespan 不降时记录 `WARN`，不伪造加速结论。

## 可证伪矩阵结果

- 同方案 Q1→Q2：`PASS`，Makespan `800 -> 400`，added COPY `18000 -> 0`。
- 同方案 Q2→Q3：`PASS`，Makespan `1200 -> 1124`，物理 DDR `30000 -> 24000`，added COPY 不变。
- 16-byte 命中但 Makespan `705 -> 705`：`WARN`。
- 故意错配 plan hash：`FAIL`。
- 故意把 Q3 物理 DDR 改为 `24001`：`FAIL`，正确重算值为 `24000`。
- 换 plan 的重新设计对照：`WARN / REDESIGN_ONLY`。

## 最小官方核验

一个 3-op、2-core 的最小图以同一方案分别通过未修改的 Q1/Q2/Q3 evaluator。三问均为 Makespan `3`、scheduled COPY `64`、added COPY `0`；Q3 无命中。Q1↔Q2、Q2↔Q3 合同检查均为 `PASS`。这只验证接口、哈希、同方案口径和指标一致性，不代表正式图性能。

## 复现命令

```powershell
.\.venv\Scripts\python.exe src\evaluate\a_metric_audit.py --acceptance-evidence-dir shared_evidence\phase1\task_c_01 --official-minimal-check --official-root "<official-root>" --output-dir result\a_validation_prototype
.\.venv\Scripts\python.exe tests\test_a_metric_audit.py
$env:A_OFFICIAL_ROOT = "<official-root>"
.\.venv\Scripts\python.exe -m unittest tests.test_a_metric_audit.MetricAuditTests.test_official_minimal_acceptance_check -v
```

原始 C-02 JSON 共享于 `Google Drive / 04_Results / Phase2 / TASK-C-02 /`。本目录不含官方附件副本、完整 Trace 或正式全量结果。
