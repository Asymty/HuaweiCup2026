# HANDOFF

## HANDOFF-001
- From: Codex B
- To: Codex A; Codex C
- Task: TASK-B-01
- Status: DONE, pending review
- What Changed: Added 100-graph profile and a reproducible, isolated runner for the unchanged official singlecore/Q1/Q2/Q3 CLIs; completed stratified pilot and bounded concurrent-case check.
- Files: `src/preprocess/a_graph_profile.py`; `src/evaluate/a_official_runner.py`; `tests/test_a_official_runner.py`; `coordination/agent_b_status.md`; ignored evidence under `result/a_graph_profile/` and `result/a_formal_runs/`.
- Key Results: 8 stratified cases × Q1/Q2/Q3 at 2 cores all completed. case_014 2-core evaluator wall seconds Q1/Q2/Q3 = 36.58/56.40/56.65; case_034 = 2.19/1.66/1.78. Official singlecore for case_014 and case_072 timed out at 90 s. Suggested bounded-subgraph timeout 120 s; separate large-Task/singlecore cap 600 s is provisional. Interpolated full 1,200-run cost ~1.6 h one worker, plausible 1.1–3.5 h for the official stub plan only.
- Evidence: `result/a_graph_profile/profile.csv`; `result/a_formal_runs/pilot_summary.csv`; per-run `run_record.json` and raw official outputs. Reproduction command and detailed method in `coordination/agent_b_status.md`. `python -m unittest discover -s tests -p test_a_official_runner.py -v`, `python -m compileall src tests main.py`, and `python tests/smoke_test.py` passed.
- Warnings: Pilot scores are not formal 100-case results. Official stub is a legal format example, not an optimized baseline. Large singlecore Makespans remain unknown; 600 s limit has not yet been tested. Concurrency tested only on two small/medium cases.
- Open Questions: How should formal plans constrain Task/subgraph size to avoid evaluator long tails? What singlecore timeout and worker memory budget should formal runs use?
- Recommended Next Action: A review cost and Task-size evidence before selecting a formal run policy; C audit metric semantics and paired Q2/Q3 interpretation. Do not start TASK-B-02 from this handoff.
- PR: Pending.
