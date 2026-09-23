# DECISIONS

## DECISION-001：正式锁定 A 题

- Time: 2026-09-23 09:23 Asia/Shanghai
- Decision: 人类队长确认 FINAL PROBLEM = A（通用神经网络处理器下的多核调度问题）。选题阶段结束，进入 PHASE 1: Problem Formalization。MODEL FREEZE = FALSE。
- Reason: A 题给出固定的方案格式、100 个正式计算图、三问官方评估器和单核参照入口。可先构造合法方案，再以官方 Makespan 与辅助指标衡量改进；三问共用切图与调度接口，场景机制逐步扩展。最终选题决定由人类队长作出，不由 Codex 的 Gate 自动替代。
- Evidence:
  1. Codex A/B/C 独立审查均将 A 保留为主要候选。B 的审查确认题包含 100 图和三问评估器；C 的审查把评估器可运行及合法基线列为前提。证据：D:/Downloads/Codex B 习题分析.md、D:/Downloads/Codex C 习题分析.md，以及 Codex A 先前选题审查。
  2. A 题 Q1/Q2/Q3 官方评估器在 case_001 与 case_019 上均成功运行，最小合法 baseline 被全部三问接受。证据：result/a_feasibility_gate/GATE_REPORT.md 与 runs/<case>/<plan>/problem_<n>/run_record.json。
  3. 两个结构不同的测试图上，轻量改进使官方 Makespan 分别下降约 49.87%（case_001）和 49.00%（case_019）。这些只是 Gate 抽样，不是正式总体成绩。
  4. Q1 的跨 Task DDR、Q2 的同核 Task 合并与复用、Q3 的共享只读 L2 形成递进关系；三 Codex 可按建模、运行、独立验证并行工作。
  5. 最大图 case_014 的大 Task 方案在 300 秒内未完成；官方小子图示例方案 Q1 在 34.40 秒完成，但质量差。此证据支持可运行性，也明确暴露计算长尾。
- Warnings:
  1. 不得将两个 Gate 样例约 49% 的改善外推到全部 100 图，或写成正式论文结论。
  2. Q2 的 Task 合并与同核 L1/UB 复用是否带来独立收益，尚未验证。
  3. Q3 有 Cache 命中记录，但 L2 对 Makespan 或搬运的独立效用尚未验证。
  4. 最大图存在明显 evaluator 长尾；最大图 Q2/Q3 成本仍未实测。
  5. 正式全量结果须覆盖全部 100 图、2–5 核，并采用官方单核参照与固定配置。
- Alternatives Rejected: D、E 保留为此前备选，但队长已正式选择 A；本阶段不重新比较 A–F。
- Affected Tasks: TASK-A-01、TASK-B-01、TASK-C-01。三任务均可从官方题面、附件、固定配置和本决策同时启动。

## DECISION-002：Phase 1 技术通过，正式验收先过 Evidence Handoff Gate

- Time: 2026-09-23 12:03 Asia/Shanghai
- Decision: `PHASE 1 REVIEW = PASS` 仅指核心建模、runner、合法性与 Q2/Q3 受控机制的技术链路可支持下一阶段原型设计；`PHASE 1 FULLY ACCEPTED = NO`。TASK-A-01 正式 ACCEPT；TASK-B-01、TASK-C-01 均为 `IMPLEMENTATION = DONE`、`TECHNICAL REVIEW = PASS_WITH_WARNING`、`FORMAL ACCEPTANCE = EVIDENCE_PENDING`，不得因 A 本机没有 ignored `result/**` 判 REVISE/REJECT，也不得在证据交接前写成正式 ACCEPT。先执行仅整理旧结果的 TASK-B-01E/C-01E；A/B/C-02 候选任务依赖二者证据 Gate，通过前不得启动。MODEL FREEZE = FALSE，不启动正式大规模最终实验。
- Reason: 已合并代码和 A 本机小规模官方抽查足以核对机制与接口，但 B/C 第一轮原始 pilot/validation 证据主要留在各自本机，仓库尚无可移植的最小审核包。长期采用 L1 status/handoff、L2 `shared_evidence/<phase>/<task_id>/`、L3 `Google Drive / 04_Results /` 三层证据；B/C 任务正式 ACCEPT 需 `IMPLEMENTATION DONE + VALIDATION PASS + EVIDENCE SHARED PASS`。官方 canonical 相对路径统一为 `题目/中文题目/A题/official_bundle/`，原始 ZIP 只读；整个 `题目/` 仅以本机 `.git/info/exclude` 排除，不改共享 `.gitignore`。
- Evidence: PR #6/#7/#8 已合并；A 本机 16 项 A 相关测试、官方 C 受控机制套件、100 图画像再生成和一次 case_001 Q1 runner 抽查均 PASS。C 受控 Q2 为 Makespan 800→400、added COPY 18000→0；Q3 同方案为 1200→1124、hit 6000 bytes 且 added COPY 不变；16 bytes 命中边界为 705→705。B 状态页记录 8 图 pilot 与 case_014/072 singlecore 90 秒删失，但其原始记录在 B 本机，当前只作部分核验。C 审计文件路径直接启动失败，模块入口与测试可用；留待后续小修。上述受控图和 Gate 两例均不得外推到 100 图。
- Alternatives Rejected: 不为缺少跨机器证据重跑 B/C 第一轮任务；不把 Owner 状态文字当独立验收；不在证据缺席但技术链路已成立时误判 REJECT/REVISE；不立即启动全量最终实验或 MODEL FREEZE。
- Affected Tasks: TASK-B-01E、TASK-C-01E 是即时 P0 证据交接；TASK-A-02、TASK-B-02、TASK-C-02 是依赖 Gate 的下一阶段候选任务。A 收到 L2/L3 后只按任务卡有限抽样复核，再更新正式 ACCEPT 与阶段状态。
## DECISION-003：B 证据 Gate 通过，C 保持 L3 待核对

- Date: 2026-09-23
- Decision: PR #10/#11 已合并。TASK-B-01E 的 L2/L3 可定位并经有限独立抽查，TASK-B-01 正式 ACCEPT。TASK-C-01E 的 L2 内容及哈希通过，但声明的 L3 原始文件在当前可访问的团队 Drive 未定位；TASK-C-01 仍为 EVIDENCE_PENDING，Phase 1 FULLY ACCEPTED = NO，A/B/C-02 不启动。
- Evidence: `shared_evidence/phase1/task_b_01/` 的 100 图、47 条 pilot 和共享 Drive 原始 case_034 Q2 记录；`shared_evidence/phase1/task_c_01/` 的 8/8 legality、Q2/Q3 对照及边界。A 仅抽样审核既有证据，未重跑 B/C 第一轮实验。
- Next: C 提供团队可访问的 L3 链接或同步原有两份文件；A 对照 manifest 抽查后再决定 C 正式验收。MODEL FREEZE = FALSE。

## DECISION-004：Phase 1 正式验收通过

- Date: 2026-09-23
- Decision: TASK-C-01E 的共享 L3 两份原始文件已由 A 独立读取并核对大小、SHA-256；其修正 manifest 经 PR #13 合并。TASK-C-01 正式 ACCEPT；连同既有 TASK-A/B-01 ACCEPT，PHASE 1 FULLY ACCEPTED = YES，RISK-006 CLOSED。TASK-A/B/C-02 的证据 Gate 依赖已满足，本次未启动下一阶段任务。MODEL FREEZE = FALSE。
- Evidence: 团队共享 [TASK-C-01 L3 目录](https://drive.google.com/drive/folders/1hTQdO02EM8tjuvZBrwdqs507673F_XAG)；`official_validation_evidence.json` SHA-256 `a26d60a75f4bd05ce4c2c96f563ab509a16d60aca4cee4f43df0a997b49e2641`，`TASK-C-01_REPORT.md` SHA-256 `d01214c86f6cf95b05302514d62831fb6859138829065ed740c95100cc14d8f1`；L2 8/8 legality、Q2/Q3 受控对照和边界已在前次审查核对。
- Boundary: 这是 Phase 1 证据与技术验收，不构成正式 100 图性能结论、模型冻结或大规模实验授权；B/C 第一轮实验未重跑。
