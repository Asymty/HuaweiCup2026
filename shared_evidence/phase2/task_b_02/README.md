# TASK-B-02 prototype runner evidence

This package contains four bounded **prototype interface checks**, not an optimized algorithm or a formal 100-graph experiment. The cases are case_019 and case_034, each with one Q2 and one Q3 official evaluator call at 2 cores. Each Q2/Q3 pair uses the same pre-existing B-01 pilot plan, graph and fixed config. `prototype_records.json` is the compact review table; `evidence_manifest.json` gives source, official config/script, L2 and L3 SHA-256 hashes. The manifest does not hash itself.

Runner CLI flags `--budget-ledger` and `--max-evaluations` reserve a shared invocation slot before starting the official evaluator. A crashed or timed-out call still consumes a slot. The four-call ledger is exhausted. Each call used `--timeout 30`; none timed out. All four exited 0. Illegal-plan, timeout, missing-output, budget-exhausted and metric-mismatch paths are covered by wrapper tests and are excluded from successful metrics. Existing 90-second censored singlecore results remain without Makespan.

New compact fields are copied from the unchanged official `data_movement_bytes` (partition/spill), or computed from official `per_core_timeline[*].ops[*].end` (max op end), Q3 cache hit+miss bytes, and scheduled COPY minus Q3 hit bytes. The last is a **diagnostic derivation**, not an official score or a substitute for logical `added_copy_bytes`. `max_op_end_matches_makespan` is checked on each successful result. `pairing_key_sha256` hashes graph, config and plan SHA-256 plus core count; equal keys require the same input and plan, not merely equal filenames.

Reproduction uses `src/evaluate/a_official_runner.py` with the fixed config and evaluator scripts in `result/a_formal_runs/official_bundle/`, `--plan` set to each pre-existing Q2 pilot plan (paths below), `--cores 2`, `--timeout 30`, `--output-root result/a_prototype_runner`, `--budget-ledger result/a_prototype_runner/budget.json`, and `--max-evaluations 4`. The pairing plans are:

- case_019: `result/a_formal_runs/case_019/problem_2/cores_2/20260923T024908975000Z_4ad32fad/plan.json`
- case_034: `result/a_formal_runs/case_034/problem_2/cores_2/20260923T024922136942Z_74716c83/plan.json`

The necessary raw `run_record.json`, `official_result.json`, copied plan files and budget ledger are in `Google Drive / 04_Results / Phase2 / TASK-B-02 /`; the manifest records the actual mounted path and every relative path and hash. No large traces, stdout/stderr or official attachment are in Git. Rebuild this L2 package from the **existing** local results with:

```powershell
.\.venv\Scripts\python.exe shared_evidence/phase2/task_b_02/build_evidence.py --drive-root <resolved-shared-HuaweiCup2026-Drive-directory>
```

Validation commands: `.\.venv\Scripts\python.exe -m unittest tests.test_a_official_runner`, `.\.venv\Scripts\python.exe -m compileall src tests main.py`, `.\.venv\Scripts\python.exe tests\smoke_test.py`, and `git diff --check`. The runner never modifies official source or scoring logic.
