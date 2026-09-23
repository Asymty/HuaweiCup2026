# 交接协议

交接必须包含：`From`、`To`、`Task`、`Status`、`What Changed`、`Files`、`Key Results`、`Evidence`、`Warnings`、`Open Questions`、`Recommended Next Action`、`PR`。

A 接收交接后必须读取状态页、输出和 PR，并明确给出 `ACCEPT`、`ACCEPT PENDING EVIDENCE HANDOFF`、`REVISE` 或 `REJECT`；形成新路线决策时更新 `DECISIONS.md`，再建立下一任务。没有证据路径或验证命令的“已完成”不得正式接受；证据仅因跨机器尚未交接时使用 pending 状态。

## 跨 Agent Evidence Handoff

- **L1 — Status / Handoff：** `coordination/agent_*_status.md` 和 `coordination/HANDOFF.md` 记录结论、命令、风险、L2 索引、L3 位置及证据状态；不能仅凭文字结论验收。
- **L2 — Minimal Review Evidence：** Owner 在 `shared_evidence/<phase>/<task_id>/` 提交 `README.md`、`evidence_manifest.json` 与足以审核的小型 CSV/JSON；可选少量关键 case 结果。manifest 至少记录原任务与其已合并提交号、来源文件及 SHA-256、官方脚本和固定 config 的 SHA-256、生成方法、命令、参数、时间戳、其他 L2 证据文件及 SHA-256、L3 位置。manifest 不记录自身哈希或本次证据提交号，避免自引用；证据 PR 的提交号记在 L1 状态/交接。不得放入大规模 Trace、完整 stdout/stderr、临时文件或官方附件副本。
- **L3 — Raw Evidence：** 大型原始结果保留在 `Google Drive / 04_Results / <Phase> / <TASK-ID> /`；只共享必要的现有原始结果、Trace 和运行记录。manifest 给出实际可访问位置，不得虚构链接。若任务本身无大型原始证据，manifest 明确写 `not_applicable` 及原因。

Owner 不为制作证据包重跑已完成实验；从已有 `result/**` 整理即可。A 优先核对 L1、L2、必要的 L3，再抽样对照官方原始输入、已合并代码和关键结果。`EVIDENCE SHARED = PASS` 要求 L2 manifest 与文件可读、哈希一致，并且必要的 L3 位置可定位。缺少可移植证据时使用 `FORMAL ACCEPTANCE = EVIDENCE_PENDING`；只有证据数字矛盾、哈希不符、官方程序来源无法确认、关键结果无法复现或关键字段来源不明等实质问题才判 `REVISE`。普通大日志缺席不构成 `REJECT`。
