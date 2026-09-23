"""Extract TASK-B-01 review evidence from existing local results only.

No graph profiling, plan generation, or evaluator is invoked here.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PROFILE = REPO / "result/a_graph_profile/profile.json"
RUNS = REPO / "result/a_formal_runs"
OFFICIAL_ARCHIVE = REPO / "题目/中文题目/A题/通用神经网络处理器下的多核调度问题  附件.zip"
CASES = ("case_019", "case_080", "case_035", "case_034", "case_020", "case_054", "case_072", "case_014")
KEY_CASES = ("case_014", "case_034", "case_072")
PROBLEMS = ("1", "2", "3")


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return path.resolve().relative_to(REPO).as_posix()


def write_json(path: Path, value: object) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def write_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    with path.open("w", newline="\n", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows({column: row.get(column) for column in columns} for row in rows)


def load_sources() -> tuple[list[dict], list[dict]]:
    profiles = json.loads(PROFILE.read_text(encoding="utf-8"))
    if len(profiles) != 100 or len({row["case_id"] for row in profiles}) != 100:
        raise ValueError("profile must contain 100 distinct cases")
    records = []
    for path in sorted(RUNS.glob("case_*/problem_*/cores_*/*/run_record.json")):
        row = json.loads(path.read_text(encoding="utf-8"))
        if row["case_id"] not in CASES or row["status"] not in ("success", "timeout"):
            continue
        if row["input_sha256"] != hash_file(Path(row["input_path"])):
            raise ValueError(f"graph hash mismatch: {path}")
        if row["config_sha256"] != hash_file(Path(row["config_path"])):
            raise ValueError(f"config hash mismatch: {path}")
        if row["official_script_sha256"] != hash_file(Path(row["official_script"])):
            raise ValueError(f"official script hash mismatch: {path}")
        if row["plan_sha256"] is not None and row["plan_sha256"] != hash_file(Path(row["plan_path"])):
            raise ValueError(f"plan hash mismatch: {path}")
        if row["status"] == "success":
            result = json.loads(Path(row["result_path"]).read_text(encoding="utf-8"))
            movement = result["data_movement_bytes"]
            if row["makespan"] != result["makespan"]:
                raise ValueError(f"makespan mismatch: {path}")
            if row["added_copy_bytes"] != movement["scheduled_copy_bytes"] - movement["original_graph_copy_bytes"]:
                raise ValueError(f"COPY mismatch: {path}")
            if row["problem"] == "3" and row["cache_hit_rate"] != result["cache_stats"]["hit_rate"]:
                raise ValueError(f"Q3 hit rate mismatch: {path}")
        elif row.get("makespan") is not None or Path(row["result_path"]).exists():
            raise ValueError(f"censored timeout has a result: {path}")
        row["source_run_record"] = relative(path)
        row["source_record_sha256"] = hash_file(path)
        records.append(row)
    if len({row["case_id"] for row in records}) != 8:
        raise ValueError("pilot must contain eight distinct cases")
    for case_id in CASES:
        for problem in PROBLEMS:
            matches = [row for row in records if row["case_id"] == case_id and row["problem"] == problem and row["core_count"] == 2 and row["status"] == "success"]
            if not matches:
                raise ValueError(f"missing 2-core pilot: {case_id}, Q{problem}")
    return profiles, records


def copy_l3(source: Path, l3: Path, copied: list[dict]) -> None:
    destination = l3 / relative(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    expected = hash_file(source)
    if destination.exists():
        if hash_file(destination) != expected:
            raise ValueError(f"L3 differs from source: {destination}")
    else:
        shutil.copy2(source, destination)
    if hash_file(destination) != expected:
        raise ValueError(f"L3 copy failed hash check: {destination}")
    copied.append({"source": relative(source), "l3_relative_path": destination.relative_to(l3).as_posix(),
                   "sha256": expected, "bytes": source.stat().st_size})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--drive-root", required=True, type=Path,
                        help="Existing Google Drive project root containing 04_Results")
    args = parser.parse_args()
    if not (args.drive_root / "04_Results").is_dir():
        raise FileNotFoundError(args.drive_root / "04_Results")
    l3 = args.drive_root / "04_Results/Phase1/TASK-B-01"
    profiles, records = load_sources()
    HERE.mkdir(parents=True, exist_ok=True)
    graph_columns = [key for key in profiles[0] if key != "input_path"]
    write_csv(HERE / "graph_profile_summary.csv", profiles, graph_columns)

    grouped = defaultdict(list)
    for row in records:
        grouped[(row["case_id"], row["problem"], row["core_count"])].append(row)
    primary = {key: min(items, key=lambda item: item["source_run_record"])["source_run_record"]
               for key, items in grouped.items()}
    pilot = []
    for row in sorted(records, key=lambda item: (item["case_id"], item["problem"], item["core_count"], item["source_run_record"])):
        key = (row["case_id"], row["problem"], row["core_count"])
        role = "timeout_censored" if row["status"] == "timeout" else (
            "repeat_or_parallel_check" if row["source_run_record"] != primary[key] else (
                "singlecore_reference" if row["problem"] == "singlecore" else (
                    "two_core_pilot" if row["core_count"] == 2 else "core_count_probe")))
        pilot.append({
            "case_id": row["case_id"], "problem": row["problem"], "core_count": row["core_count"],
            "run_role": role, "status": row["status"], "makespan": row.get("makespan"),
            "original_graph_copy_bytes": row.get("original_graph_copy_bytes"),
            "scheduled_copy_bytes": row.get("scheduled_copy_bytes"),
            "added_copy_bytes": row.get("added_copy_bytes"),
            "cache_hit_rate": row.get("cache_hit_rate"),
            "plan_runtime_seconds": row.get("plan_runtime_seconds"),
            "evaluation_runtime_seconds": row.get("evaluation_runtime_seconds"),
            "exit_code": row.get("exit_code"), "timed_out": row.get("timed_out"),
            "timeout_seconds": row.get("timeout_seconds"),
            "input_sha256": row["input_sha256"], "config_sha256": row["config_sha256"],
            "official_script_sha256": row["official_script_sha256"], "plan_sha256": row.get("plan_sha256"),
            "source_run_record": row["source_run_record"],
            "source_record_sha256": row["source_record_sha256"],
        })
    pilot_columns = list(pilot[0])
    write_csv(HERE / "pilot_summary.csv", pilot, pilot_columns)
    profile_by_case = {row["case_id"]: row for row in profiles}
    write_json(HERE / "key_cases.json", {
        case_id: {"graph_profile": {key: value for key, value in profile_by_case[case_id].items() if key != "input_path"},
                  "runs": [row for row in pilot if row["case_id"] == case_id]}
        for case_id in KEY_CASES
    })

    copied: list[dict] = []
    copy_l3(PROFILE, l3, copied)
    for case_id in CASES:
        for problem in PROBLEMS:
            row = min((row for row in records if row["case_id"] == case_id and row["problem"] == problem and row["core_count"] == 2),
                      key=lambda item: item["source_run_record"])
            if problem == "2" or case_id in KEY_CASES:
                copy_l3(REPO / row["source_run_record"], l3, copied)
            if (case_id, problem) in (("case_014", "2"), ("case_034", "3"), ("case_072", "2")):
                copy_l3(Path(row["plan_path"]), l3, copied)
                copy_l3(Path(row["result_path"]), l3, copied)
    for case_id in KEY_CASES:
        matches = [row for row in records if row["case_id"] == case_id and row["problem"] == "singlecore"]
        if matches:
            row = min(matches, key=lambda item: item["source_run_record"])
            copy_l3(REPO / row["source_run_record"], l3, copied)
            if row["status"] == "success":
                copy_l3(Path(row["result_path"]), l3, copied)
    for case_id in ("case_019", "case_034"):
        repeats = sorted((row for row in records if row["case_id"] == case_id and row["problem"] == "1" and row["core_count"] == 2),
                         key=lambda item: item["source_run_record"])
        if len(repeats) > 1:
            copy_l3(REPO / repeats[-1]["source_run_record"], l3, copied)

    readme = f"""# TASK-B-01 Phase 1 evidence handoff

This package is extracted from existing local `result/a_graph_profile/**` and `result/a_formal_runs/**`. The extraction did not run a graph profiler, plan generator, evaluator, singlecore baseline, or parallel experiment. TASK-B-01 code was introduced at `93a2b2c`, with original task handoff commit `1a1d577`; PR #8 merged it into main.

For source verification only, the fixed config and five used official scripts in the pre-existing result-bundle copy were hashed and compared byte-for-byte with the original read-only official attachment ZIP. The ZIP and its copy are not included in L2 or L3.

## Contents and interpretation

- `graph_profile_summary.csv`: 100 unique official cases; existing op, tensor, edge, dependency, depth, size and tensor-byte fields from `profile.json`. Absolute local input paths are omitted.
- `pilot_summary.csv`: {len(pilot)} existing success/timeout records across eight stratified cases. The 24 Q1/Q2/Q3 two-core primary entries are pilot runs using the unchanged official random-format stub (seed 0; 50–100 eligible ops per subgraph). Additional existing core-count, singlecore and repeat records have explicit `run_role`; repeats are not independent sample cases. The one invalid-plan negative test is excluded from the pilot table.
- `key_cases.json`: case_014, case_034 and case_072 graph structures and all their included run rows. `source_run_record` and SHA-256 link each row to the raw record. Successful rows take Makespan and COPY fields from official result JSON through the saved runner record; `evaluation_runtime_seconds`, exit code and timeout come from the runner wall clock/subprocess.
- Timeout rows for case_014 and case_072 official singlecore runs are *right-censored at 90 seconds*. They have no Makespan; never treat 90 seconds or a blank value as a measured baseline. case_014's >300-second Gate large-Task observation is contextual only, not a pilot result.

## Full-run cost estimate, not a formal score

The earlier estimate concerns 100 cases × four core counts (2–5) × Q1/Q2/Q3 = 1,200 evaluator calls **for the bounded official stub plan only**. For each problem, sort the eight two-core pilot anchors by `op_count`; linearly interpolate evaluator wall seconds by op count at each of the 100 profiled graphs, clamping outside the anchor range. Summing all problems gives about 1,403.4 seconds at two cores. Multiplying by four core counts gives about 5,614 seconds. Existing plan-generation anchors interpolated the same way add about 224 seconds over 1,200 calls, yielding about 1.6 hours on one worker. A broad 0.7–2.1 multiplier on evaluator time plus generator time gives roughly 1.1–3.5 hours after rounding, to cover unmeasured core/case combinations, I/O and tail uncertainty. This interval is judgmental, not a confidence interval. Optimized or large-Task plans may cost much more; no full 1,200-call run occurred.

Observed largest bounded-plan evaluator wall time was 56.65 seconds (case_014 Q3 at two cores), so 120 seconds is a staged bounded-plan timeout recommendation. A separate 600-second large-Task/singlecore cap is provisional and untested. Two-worker independence was only checked on small/medium cases; do not assume long-tail throughput doubles.

## Raw evidence (L3)

Google Drive project shortcut: `G:\\我的云端硬盘\\HuaweiCup2026.lnk` on this machine. Actual mounted location: `{l3}`. Logical team location: `Google Drive / 04_Results / Phase1 / TASK-B-01 /`. Only existing selected run records, three key official results and their plans, case_034 singlecore result, and the original profile JSON are copied there. No large Trace, stdout/stderr collection, or official bundle is in Git. The manifest lists exact L3 relative paths, bytes and SHA-256. All other raw local runs remain under `result/a_formal_runs/**` on B's machine.

Rebuild from existing files only: `.\\.venv\\Scripts\\python.exe shared_evidence/phase1/task_b_01/build_evidence.py --drive-root \"{args.drive_root}\"`. The script verifies recorded graph/config/script/plan hashes and compares successful metrics to unchanged official result JSON. It does not call evaluators.
"""
    with (HERE / "README.md").open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(readme)
    official_scripts = sorted({row["official_script"] for row in records})
    official_scripts.append(str(RUNS / "official_bundle/code/stub_multicore_cut_and_schedule.py"))
    config_paths = sorted({row["config_path"] for row in records})
    official_files = sorted(set(official_scripts + config_paths))
    archive_members = []
    with zipfile.ZipFile(OFFICIAL_ARCHIVE) as archive:
        for value in official_files:
            path = Path(value)
            member = path.resolve().relative_to((RUNS / "official_bundle").resolve()).as_posix()
            digest = hashlib.sha256(archive.read(member)).hexdigest()
            if digest != hash_file(path):
                raise ValueError(f"official ZIP/copy mismatch: {member}")
            archive_members.append({"member": member, "sha256": digest})
    manifest = {
        "task": "TASK-B-01E", "source_task": "TASK-B-01", "source_task_commit": "1a1d577",
        "source_code_commit": "93a2b2c", "source_merged_main_commit": "e38202e",
        "extracted_at_utc": datetime.now(timezone.utc).isoformat(),
        "method": "read-only mechanical extraction from pre-existing profile.json and run_record.json; successful metrics cross-checked against saved official_result.json; selected raw files copied and SHA-256 verified",
        "command": f'.\\.venv\\Scripts\\python.exe shared_evidence/phase1/task_b_01/build_evidence.py --drive-root "{args.drive_root}"',
        "parameters": {"pilot_cases": list(CASES), "key_cases": list(KEY_CASES), "stub_seed": 0,
                       "min_subgraph_size": 50, "max_subgraph_size": 100,
                       "primary_problem_core_count": 2, "source_records_included": len(records)},
        "sources": [{"path": relative(PROFILE), "sha256": hash_file(PROFILE)},
                    {"path": "result/a_formal_runs/pilot_summary.csv", "sha256": hash_file(RUNS / "pilot_summary.csv")}] +
                   [{"path": row["source_run_record"], "sha256": row["source_record_sha256"]} for row in records],
        "official_scripts": [{"path": relative(Path(path)), "sha256": hash_file(Path(path))} for path in sorted(set(official_scripts))],
        "fixed_configs": [{"path": relative(Path(path)), "sha256": hash_file(Path(path))} for path in config_paths],
        "official_archive_verification": {"path": relative(OFFICIAL_ARCHIVE), "sha256": hash_file(OFFICIAL_ARCHIVE),
                                           "members": archive_members, "all_match": True},
        "l2_files": [{"path": path.name, "sha256": hash_file(path), "bytes": path.stat().st_size}
                     for path in [HERE / "graph_profile_summary.csv", HERE / "pilot_summary.csv",
                                  HERE / "key_cases.json", HERE / "README.md", HERE / "build_evidence.py",
                                  HERE / ".gitattributes"]],
        "l3": {"logical_location": "Google Drive / 04_Results / Phase1 / TASK-B-01 /",
               "mounted_location": str(l3), "status": "copied_and_hash_verified", "files": copied},
    }
    write_json(HERE / "evidence_manifest.json", manifest)
    print(f"profiles={len(profiles)} pilot_rows={len(pilot)} L3_files={len(copied)} L3_bytes={sum(item['bytes'] for item in copied)}")


if __name__ == "__main__":
    main()
