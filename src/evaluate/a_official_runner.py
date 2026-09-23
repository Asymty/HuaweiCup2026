"""Run unchanged official A evaluators and preserve reproducible run evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path


SCRIPT = {
    "singlecore": "singlecore_evaluate.py",
    "1": "multicore_cut_evaluate_problem_1.py",
    "2": "multicore_cut_evaluate_problem_2.py",
    "3": "multicore_cut_evaluate_problem_3.py",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _invoke(command: list[str], timeout_seconds: float) -> dict:
    start = time.perf_counter()
    try:
        completed = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=timeout_seconds, check=False,
        )
        return {
            "runtime_seconds": time.perf_counter() - start,
            "exit_code": completed.returncode,
            "timed_out": False,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    except subprocess.TimeoutExpired as error:
        def decode(value: bytes | str | None) -> str:
            if isinstance(value, bytes):
                return value.decode("utf-8", errors="replace")
            return value or ""
        return {
            "runtime_seconds": time.perf_counter() - start,
            "exit_code": None,
            "timed_out": True,
            "stdout": decode(error.stdout),
            "stderr": decode(error.stderr),
        }


def _save_streams(run_dir: Path, prefix: str, outcome: dict) -> None:
    (run_dir / f"{prefix}.stdout.txt").write_text(outcome["stdout"], encoding="utf-8")
    (run_dir / f"{prefix}.stderr.txt").write_text(outcome["stderr"], encoding="utf-8")


def _metrics(result: dict) -> dict:
    movement = result.get("data_movement_bytes") or {}
    cache = result.get("cache_stats") or {}
    scheduled = movement.get("scheduled_copy_bytes")
    original = movement.get("original_graph_copy_bytes")
    return {
        "makespan": result.get("makespan"),
        "added_copy_bytes": scheduled - original if scheduled is not None and original is not None else None,
        "scheduled_copy_bytes": scheduled,
        "original_graph_copy_bytes": original,
        "cache_hit_rate": cache.get("hit_rate"),
        "cache_hit_bytes": cache.get("hit_bytes"),
        "cache_miss_bytes": cache.get("miss_bytes"),
        "cache_hits": cache.get("hits"),
        "cache_accesses": cache.get("accesses"),
    }


def run_evaluation(
    graph: Path, config: Path, official_code: Path, problem: str,
    core_count: int, output_root: Path, timeout_seconds: float,
    plan: Path | None = None, seed: int = 0,
    min_subgraph_size: int = 50, max_subgraph_size: int = 100,
    python: str = sys.executable,
) -> dict:
    """Call the official CLI in an isolated run directory; never evaluate in process."""
    graph, config, official_code = graph.resolve(), config.resolve(), official_code.resolve()
    if problem not in SCRIPT:
        raise ValueError("problem must be singlecore, 1, 2, or 3")
    if problem == "singlecore" and core_count != 1:
        raise ValueError("singlecore requires core_count=1")
    if problem != "singlecore" and core_count < 1:
        raise ValueError("core_count must be positive")
    for path in (graph, config, official_code / SCRIPT[problem]):
        if not path.is_file():
            raise FileNotFoundError(path)
    if problem != "singlecore" and plan is None and not (official_code / "stub_multicore_cut_and_schedule.py").is_file():
        raise FileNotFoundError(official_code / "stub_multicore_cut_and_schedule.py")
    if plan is not None and not plan.is_file():
        raise FileNotFoundError(plan)

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "_" + uuid.uuid4().hex[:8]
    run_dir = output_root.resolve() / graph.stem / f"problem_{problem}" / f"cores_{core_count}" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    result_path = run_dir / "official_result.json"
    trace_path = run_dir / "official_trace.json"
    log_path = run_dir / "official_log.txt"
    plan_path = run_dir / "plan.json" if problem != "singlecore" else None
    record = {
        "case_id": graph.stem, "problem": problem, "core_count": core_count,
        "input_path": str(graph), "input_sha256": sha256(graph),
        "config_path": str(config), "config_sha256": sha256(config),
        "official_script": str(official_code / SCRIPT[problem]),
        "official_script_sha256": sha256(official_code / SCRIPT[problem]),
        "plan_path": str(plan_path) if plan_path else None,
        "plan_source": "official_stub" if plan is None and plan_path else ("provided" if plan else "official_singlecore"),
        "seed": seed if plan is None and plan_path else None,
        "min_subgraph_size": min_subgraph_size if plan is None and plan_path else None,
        "max_subgraph_size": max_subgraph_size if plan is None and plan_path else None,
        "timeout_seconds": timeout_seconds,
        "plan_runtime_seconds": 0.0,
        "evaluation_runtime_seconds": None,
        "result_path": str(result_path), "trace_path": str(trace_path), "log_path": str(log_path),
        "run_dir": str(run_dir),
    }
    if plan_path:
        if plan:
            shutil.copyfile(plan, plan_path)
        else:
            command = [python, str(official_code / "stub_multicore_cut_and_schedule.py"),
                       str(graph), "-n", str(core_count), "--seed", str(seed),
                       "--min-subgraph-size", str(min_subgraph_size),
                       "--max-subgraph-size", str(max_subgraph_size),
                       "-o", str(plan_path)]
            generated = _invoke(command, timeout_seconds)
            _save_streams(run_dir, "plan", generated)
            record["plan_command"] = command
            record["plan_runtime_seconds"] = generated["runtime_seconds"]
            record["plan_exit_code"] = generated["exit_code"]
            record["plan_timed_out"] = generated["timed_out"]
            if generated["exit_code"] != 0 or generated["timed_out"] or not plan_path.is_file():
                record.update(status="plan_failed", exit_code=generated["exit_code"],
                              timed_out=generated["timed_out"], plan_sha256=None)
                _save_record(run_dir, record)
                return record
        record["plan_sha256"] = sha256(plan_path)
    else:
        record["plan_sha256"] = None

    command = [python, str(official_code / SCRIPT[problem]), str(graph)]
    if plan_path:
        command.append(str(plan_path))
    command += ["--config", str(config), "--output", str(result_path),
                "--trace-output", str(trace_path), "--log-output", str(log_path)]
    outcome = _invoke(command, timeout_seconds)
    _save_streams(run_dir, "evaluation", outcome)
    record.update(
        evaluation_command=command,
        evaluation_runtime_seconds=outcome["runtime_seconds"],
        exit_code=outcome["exit_code"], timed_out=outcome["timed_out"],
    )
    if outcome["timed_out"]:
        record["status"] = "timeout"
    elif outcome["exit_code"] != 0:
        record["status"] = "evaluation_failed"
    elif not result_path.is_file():
        record["status"] = "output_missing"
    else:
        try:
            record.update(_metrics(json.loads(result_path.read_text(encoding="utf-8"))))
            record["status"] = "success"
        except (OSError, ValueError, TypeError) as error:
            record["status"] = "result_parse_failed"
            record["parse_error"] = str(error)
    _save_record(run_dir, record)
    return record


def _save_record(run_dir: Path, record: dict) -> None:
    (run_dir / "run_record.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("graph", type=Path)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--official-code", type=Path, required=True)
    parser.add_argument("--problem", choices=list(SCRIPT), required=True)
    parser.add_argument("--cores", type=int, default=1)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--min-subgraph-size", type=int, default=50)
    parser.add_argument("--max-subgraph-size", type=int, default=100)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--output-root", type=Path, default=Path("result/a_formal_runs"))
    args = parser.parse_args()
    record = run_evaluation(
        args.graph, args.config, args.official_code, args.problem, args.cores,
        args.output_root, args.timeout, args.plan, args.seed,
        args.min_subgraph_size, args.max_subgraph_size,
    )
    print(json.dumps({key: record.get(key) for key in (
        "case_id", "problem", "core_count", "status", "makespan",
        "added_copy_bytes", "cache_hit_rate", "plan_runtime_seconds",
        "evaluation_runtime_seconds", "run_dir")}, ensure_ascii=False))
    if record["status"] != "success":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
