"""Package existing TASK-B-02 prototype runs; never invoke an evaluator."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


CASES = ("case_019", "case_034")
PROBLEMS = ("2", "3")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--drive-root", type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[3]
    output = Path(__file__).resolve().parent
    runs = repo / "result/a_prototype_runner"
    bundle = repo / "result/a_formal_runs/official_bundle"
    l3 = args.drive_root.resolve() / "04_Results/Phase2/TASK-B-02"
    ledger = json.loads((runs / "budget.json").read_text(encoding="utf-8"))
    assert ledger == {"max_evaluations": 4, "reserved_evaluations": 4}

    rows = []
    raw_files = []
    for case in CASES:
        for problem in PROBLEMS:
            records = list((runs / case / f"problem_{problem}" / "cores_2").glob("*/run_record.json"))
            assert len(records) == 1, (case, problem, len(records))
            record_path = records[0]
            record = json.loads(record_path.read_text(encoding="utf-8"))
            official_path = record_path.with_name("official_result.json")
            plan_path = record_path.with_name("plan.json")
            official = json.loads(official_path.read_text(encoding="utf-8"))
            movement = official["data_movement_bytes"]
            cache = official.get("cache_stats") or {}
            assert record["status"] == "success" and record["exit_code"] == 0
            assert record["timed_out"] is False and record["evaluation_budget"]["reservation_granted"]
            assert record["makespan"] == official["makespan"] == record["max_op_end"]
            assert record["max_op_end_matches_makespan"] is True
            for key in ("partition_added_copy_bytes", "spill_added_copy_bytes", "scheduled_copy_bytes", "original_graph_copy_bytes"):
                assert record[key] == movement[key]
            assert record["added_copy_bytes"] == movement["added_copy_bytes"]
            assert record["added_copy_bytes"] == record["partition_added_copy_bytes"] + record["spill_added_copy_bytes"]
            assert record["total_cache_access_bytes"] == (cache["hit_bytes"] + cache["miss_bytes"] if cache else None)
            assert record["physical_ddr_bytes_diagnostic"] == movement["scheduled_copy_bytes"] - cache.get("hit_bytes", 0)
            assert record["plan_sha256"] == digest(plan_path)
            assert record["input_sha256"] == digest(bundle / "data" / f"{case}.json")
            assert record["config_sha256"] == digest(bundle / "data/config.txt")
            assert record["official_script_sha256"] == digest(bundle / "code" / f"multicore_cut_evaluate_problem_{problem}.py")
            rows.append({key: record.get(key) for key in (
                "case_id", "problem", "core_count", "status", "makespan", "max_op_end",
                "max_op_end_matches_makespan", "original_graph_copy_bytes", "scheduled_copy_bytes",
                "added_copy_bytes", "partition_added_copy_bytes", "spill_added_copy_bytes",
                "cache_hit_bytes", "cache_miss_bytes", "total_cache_access_bytes", "cache_hit_rate",
                "physical_ddr_bytes_diagnostic", "physical_ddr_derivation", "pairing_key_sha256",
                "input_sha256", "config_sha256", "official_script_sha256", "plan_sha256",
                "evaluation_runtime_seconds", "exit_code", "timed_out", "timeout_seconds",
            )})
            for source in (record_path, official_path, plan_path):
                relative = source.relative_to(runs)
                target = l3 / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
                assert digest(source) == digest(target)
                raw_files.append({"source": str(source.relative_to(repo)).replace("\\", "/"),
                                  "l3_relative_path": str(relative).replace("\\", "/"),
                                  "size_bytes": source.stat().st_size, "sha256": digest(source)})
    assert len(rows) == 4
    for case in CASES:
        pair = [row for row in rows if row["case_id"] == case]
        assert len({row["pairing_key_sha256"] for row in pair}) == 1
        assert len({row["plan_sha256"] for row in pair}) == 1

    for source in (runs / "budget.json",):
        target = l3 / source.name
        shutil.copyfile(source, target)
        assert digest(source) == digest(target)
        raw_files.append({"source": str(source.relative_to(repo)).replace("\\", "/"),
                          "l3_relative_path": source.name, "size_bytes": source.stat().st_size,
                          "sha256": digest(source)})
    (output / "prototype_records.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    l2_names = (".gitattributes", "README.md", "build_evidence.py", "prototype_records.json")
    manifest = {
        "task_id": "TASK-B-02", "status": "EVIDENCE SHARED = PASS",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "base_main_commit": "09c198425fe401abdb75d236e4d1bab7ce5e8cfb",
        "previous_task_commit": "1a1d577",
        "method": "Extract four existing bounded prototype results and copy selected raw files; no evaluator calls during extraction.",
        "command": ".\\.venv\\Scripts\\python.exe shared_evidence/phase2/task_b_02/build_evidence.py --drive-root <resolved shared HuaweiCup2026 Drive directory>",
        "parameters": {"cases": list(CASES), "problems": list(PROBLEMS), "cores": 2,
                       "max_evaluations": 4, "timeout_seconds": 30, "plan_source": "existing B-01 Q2 pilot plan per case"},
        "budget_ledger": {"source": "result/a_prototype_runner/budget.json",
                          "sha256": digest(runs / "budget.json"), **ledger},
        "official_sources": {
            "config": {"path": "result/a_formal_runs/official_bundle/data/config.txt",
                       "sha256": digest(bundle / "data/config.txt")},
            **{f"problem_{problem}": {
                "path": f"result/a_formal_runs/official_bundle/code/multicore_cut_evaluate_problem_{problem}.py",
                "sha256": digest(bundle / "code" / f"multicore_cut_evaluate_problem_{problem}.py")
            } for problem in PROBLEMS},
        },
        "l2_files": [{"path": name, "sha256": digest(output / name)} for name in l2_names],
        "l3": {"logical_location": "Google Drive / 04_Results / Phase2 / TASK-B-02 /",
               "mounted_location": str(l3), "files": raw_files},
    }
    (output / "evidence_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"L2: {len(rows)} rows; L3: {len(raw_files)} hash-verified raw files at {l3}")


if __name__ == "__main__":
    main()
