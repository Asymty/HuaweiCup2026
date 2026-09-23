# TASK-C-01 最小审核证据

本目录是 TASK-C-01 的 L2 可移植审核包，由 C 本机已有的 `result/a_validation/official_validation_evidence.json` 和 `TASK-C-01_REPORT.md` 机械整理而成。本次未调用 evaluator，也未重跑第一轮机制实验。

## 文件

- `legality_matrix.json`：8 个合法性案例的独立判定、官方判定和一致性结果；8/8 一致。
- `q2_mechanism.json`：同一受控图、同一映射和同一核调度在 Q1/Q2 下的机制对照；Makespan `800 -> 400`，scheduled COPY `30000 -> 12000`，added COPY `18000 -> 0`。
- `q3_mechanism.json`：同一受控图和完全相同的 split-core plan 在 Q2/Q3 下的成对对照；Makespan `1200 -> 1124`，命中 `6000` 字节，字节命中率 `1/3`，物理 DDR `30000 -> 24000`，而逻辑 `added_copy_bytes` 保持 `18000`。
- `q3_boundary.json`：16 字节命中存在但 Makespan `705 -> 705` 的 WARN 反例。
- `evidence_manifest.json`：来源、哈希、测试输入、提取/验证命令、时间戳、原 TASK-C-01 提交和 L3 位置。manifest 不记录自身哈希。

## 结论边界

这些结果只验证受控合成 DAG 上的合法性与 Q2/Q3 机制语义，不等于 100 个正式图上的总体性能收益。特别是 Cache 命中率上升不能单独推出 Makespan 下降，官方 `added_copy_bytes` 是逻辑 scheduled COPY 流量，也不等于扣除 Cache 命中后的物理 DDR 字节数。

## L3 原始记录

必要的既有原始记录已共享至 `Google Drive / 04_Results / Phase1 / TASK-C-01 /`：

- `official_validation_evidence.json`
- `TASK-C-01_REPORT.md`

本目录不包含大型 Trace、完整 stdout/stderr 或官方附件副本。
