# 协调协议

`coordination/` 是正式比赛共享黑板，由 A 首次从 `templates/` 复制。

`shared_evidence/<phase>/<task_id>/` 是跨 Agent 的 Git 管理最小审核证据，不能代替 `coordination/` 的结论与交接，也不能混入大型原始结果。证据分层和正式验收门槛见 [handoff_protocol.md](handoff_protocol.md)。

- `MASTER_PLAN.md`：A 主维护总体方向与阶段。
- `DECISIONS.md`：A 记录采纳决策与证据。
- `TASKS.md`：A 维护当前任务、依赖和状态。
- `agent_a_status.md`、`agent_b_status.md`、`agent_c_status.md`：各角色主写自己的状态。
- `HANDOFF.md`：交出方追加，接收方确认。

状态页与 HANDOFF 必须给出 L2 manifest 路径、必要的 L3 共享位置和 `EVIDENCE SHARED` 状态。A 可依据已合并代码、测试及有限官方抽查先作技术审查；没有可移植证据时，只能记录 `EVIDENCE_PENDING`，不得把 Owner 的状态结论写成已独立复核。

状态页字段：`Current Task`、`Status`、`Completed`、`Key Findings`、`Outputs`、`Metrics`、`Blockers`、`Need Decision`、`PR`、`Next Suggestion`。

决策字段：`Time`、`Decision`、`Reason`、`Evidence`、`Alternatives Rejected`、`Affected Tasks`。

同一时段一个文件只有一个主编辑者；修改前检查任务、状态与分支；不覆盖未合并成果；阻塞写入状态页；路线决策交给 A，强制人类决策交给队长。
