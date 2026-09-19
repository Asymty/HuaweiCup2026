# 协调协议

`coordination/` 是正式比赛共享黑板，由 A 首次从 `templates/` 复制。

- `MASTER_PLAN.md`：A 主维护总体方向与阶段。
- `DECISIONS.md`：A 记录采纳决策与证据。
- `TASKS.md`：A 维护当前任务、依赖和状态。
- `agent_a_status.md`、`agent_b_status.md`、`agent_c_status.md`：各角色主写自己的状态。
- `HANDOFF.md`：交出方追加，接收方确认。

状态页字段：`Current Task`、`Status`、`Completed`、`Key Findings`、`Outputs`、`Metrics`、`Blockers`、`Need Decision`、`PR`、`Next Suggestion`。

决策字段：`Time`、`Decision`、`Reason`、`Evidence`、`Alternatives Rejected`、`Affected Tasks`。

同一时段一个文件只有一个主编辑者；修改前检查任务、状态与分支；不覆盖未合并成果；阻塞写入状态页；路线决策交给 A，强制人类决策交给队长。
