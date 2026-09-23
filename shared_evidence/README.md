# 跨 Agent 最小审核证据

每个任务使用 `shared_evidence/<phase>/<task_id>/`，至少包含 `README.md`、`evidence_manifest.json` 和支撑结论的小型 CSV/JSON。任务 Owner 从已有结果提取，记录来源哈希、官方脚本与 config 哈希、命令、参数、时间戳、任务提交号，以及 `Google Drive / 04_Results /` 中必要原始证据的位置。

Git 中不保存大型 Trace、完整 stdout/stderr、临时文件、官方题包或完整 `result/**`。详细验收门槛见 `skill/competition_orchestrator/handoff_protocol.md`。
