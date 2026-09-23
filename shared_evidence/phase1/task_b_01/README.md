# TASK-B-01 Phase 1 evidence handoff

This package is extracted from existing local `result/a_graph_profile/**` and `result/a_formal_runs/**`. The extraction did not run a graph profiler, plan generator, evaluator, singlecore baseline, or parallel experiment. TASK-B-01 code was introduced at `93a2b2c`, with original task handoff commit `1a1d577`; PR #8 merged it into main.

For source verification only, the fixed config and five used official scripts in the pre-existing result-bundle copy were hashed and compared byte-for-byte with the original read-only official attachment ZIP. The ZIP and its copy are not included in L2 or L3.

## Contents and interpretation

- `graph_profile_summary.csv`: 100 unique official cases; existing op, tensor, edge, dependency, depth, size and tensor-byte fields from `profile.json`. Absolute local input paths are omitted.
- `pilot_summary.csv`: 47 existing success/timeout records across eight stratified cases. The 24 Q1/Q2/Q3 two-core primary entries are pilot runs using the unchanged official random-format stub (seed 0; 50–100 eligible ops per subgraph). Additional existing core-count, singlecore and repeat records have explicit `run_role`; repeats are not independent sample cases. The one invalid-plan negative test is excluded from the pilot table.
- `key_cases.json`: case_014, case_034 and case_072 graph structures and all their included run rows. `source_run_record` and SHA-256 link each row to the raw record. Successful rows take Makespan and COPY fields from official result JSON through the saved runner record; `evaluation_runtime_seconds`, exit code and timeout come from the runner wall clock/subprocess.
- Timeout rows for case_014 and case_072 official singlecore runs are *right-censored at 90 seconds*. They have no Makespan; never treat 90 seconds or a blank value as a measured baseline. case_014's >300-second Gate large-Task observation is contextual only, not a pilot result.

## Full-run cost estimate, not a formal score

The earlier estimate concerns 100 cases × four core counts (2–5) × Q1/Q2/Q3 = 1,200 evaluator calls **for the bounded official stub plan only**. For each problem, sort the eight two-core pilot anchors by `op_count`; linearly interpolate evaluator wall seconds by op count at each of the 100 profiled graphs, clamping outside the anchor range. Summing all problems gives about 1,403.4 seconds at two cores. Multiplying by four core counts gives about 5,614 seconds. Existing plan-generation anchors interpolated the same way add about 224 seconds over 1,200 calls, yielding about 1.6 hours on one worker. A broad 0.7–2.1 multiplier on evaluator time plus generator time gives roughly 1.1–3.5 hours after rounding, to cover unmeasured core/case combinations, I/O and tail uncertainty. This interval is judgmental, not a confidence interval. Optimized or large-Task plans may cost much more; no full 1,200-call run occurred.

Observed largest bounded-plan evaluator wall time was 56.65 seconds (case_014 Q3 at two cores), so 120 seconds is a staged bounded-plan timeout recommendation. A separate 600-second large-Task/singlecore cap is provisional and untested. Two-worker independence was only checked on small/medium cases; do not assume long-tail throughput doubles.

## Raw evidence (L3)

Google Drive project shortcut: `G:\我的云端硬盘\HuaweiCup2026.lnk` on this machine. Actual mounted location: `G:\.shortcut-targets-by-id\1A2sgFCDpS1YiCptPPK52xN8mek3fY5C5\HuaweiCup2026\04_Results\Phase1\TASK-B-01`. Logical team location: `Google Drive / 04_Results / Phase1 / TASK-B-01 /`. Only existing selected run records, three key official results and their plans, case_034 singlecore result, and the original profile JSON are copied there. No large Trace, stdout/stderr collection, or official bundle is in Git. The manifest lists exact L3 relative paths, bytes and SHA-256. All other raw local runs remain under `result/a_formal_runs/**` on B's machine.

Rebuild from existing files only: `.\.venv\Scripts\python.exe shared_evidence/phase1/task_b_01/build_evidence.py --drive-root "G:\.shortcut-targets-by-id\1A2sgFCDpS1YiCptPPK52xN8mek3fY5C5\HuaweiCup2026"`. The script verifies recorded graph/config/script/plan hashes and compares successful metrics to unchanged official result JSON. It does not call evaluators.
