---
name: competition-orchestrator
description: Coordinate three Codex agents during the formal 2026 Huawei Cup competition through fixed roles, task cards, shared status, handoffs, phase gates, and human approvals. Use for competition-wide planning and coordination; do not use as a substitute for modeling, experiment execution, or paper-writing guidance.
---

# Competition Orchestrator

Use this Skill only to organize the formal competition workflow. It coordinates work; it does not invent models, run experiments, or write paper content by itself.

## Required reading order

Before accepting a competition task, read repository `AGENTS.md`, this file, [README.md](README.md), and the role/protocol documents relevant to the task. For paper tasks, also read `skill/paper_writing/README.md` and its chapter-specific guide.

## Fixed roles

- Codex A — Chief Modeling Agent: **WHAT / WHY**.
- Codex B — Data & Experiment Engineer: **RUN / MEASURE**.
- Codex C — Validation & Paper Engineer: **CHECK / EXPLAIN**.

The three agents must not independently redesign the complete solution. A owns integration decisions; B supplies reproducible evidence; C independently validates and explains evidence. Read [roles.md](roles.md) before assigning work.

## Operating procedure

1. Identify the current phase in [phase_playbook.md](phase_playbook.md).
2. Create or accept one bounded task using [task_protocol.md](task_protocol.md).
3. Coordinate through [coordination_protocol.md](coordination_protocol.md).
4. Work only within the task's allowed files and role boundary.
5. Transfer evidence using [handoff_protocol.md](handoff_protocol.md).
6. Follow [git_workflow.md](git_workflow.md).
7. Before writing, use [paper_transition.md](paper_transition.md).
8. Before freeze or submission, apply [final_gate.md](final_gate.md).

Reusable prompts are in [prompts.md](prompts.md).

## Competition initialization

At formal competition start, if repository-root `coordination/` does not exist, Codex A copies [templates/](templates/) into it. Do not create or populate `coordination/` during Skill installation or rehearsal.

## Decision authority

Codex may analyze and recommend. The human captain must explicitly confirm final problem selection, core model-route switches, acceptance of anomalous but real results, MODEL FREEZE, final paper approval, and final submission.
