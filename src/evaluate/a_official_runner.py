"""Run unchanged official A evaluators and preserve reproducible run evidence."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
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
    timeline = result.get("per_core_timeline") or []
    op_ends = [op["end"] for core in timeline for op in core.get("ops", [])]
    max_op_end = max(op_ends, default=None)
    makespan = result.get("makespan")
    hit = cache.get("hit_bytes")
    miss = cache.get("miss_bytes")
    return {
        "makespan": makespan,
        "max_op_end": max_op_end,
        "max_op_end_matches_makespan": max_op_end == makespan if max_op_end is not None else None,
        "added_copy_bytes": scheduled - original if scheduled is not None and original is not None else None,
        "scheduled_copy_bytes": scheduled,
        "original_graph_copy_bytes": original,
        "partition_added_copy_bytes": movement.get("partition_added_copy_bytes"),
        "spill_added_copy_bytes": movement.get("spill_added_copy_bytes"),
        "cache_hit_rate": cache.get("hit_rate"),
        "cache_hit_bytes": hit,
        "cache_miss_bytes": miss,
        "total_cache_access_bytes": hit + miss if hit is not None and miss is not None else None,
        "physical_ddr_bytes_diagnostic": scheduled - (hit or 0) if scheduled is not None and (hit is not None or not cache) else None,
        "physical_ddr_derivation": "scheduled_copy_bytes - cache_hit_bytes; Q1/Q2 hit treated as zero" if scheduled is not None and (hit is not None or not cache) else None,
        "cache_hits": cache.get("hits"),
        "cache_accesses": cache.get("accesses"),
    }


@contextmanager
def _budget_lock(path: Path):
    """Serialize reservations between independent runner processes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as lock:
        lock.seek(0)
        if lock.read(1) != b"1":
            lock.seek(0)
            lock.write(b"1")
            lock.flush()
        lock.seek(0)
        if sys.platform == "win32":
            import msvcrt
            msvcrt.locking(lock.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            lock.seek(0)
            if sys.platform == "win32":
                msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def _reserve_evaluation(ledger: Path, max_calls: int) -> dict:
    """Reserve one official evaluator invocation before starting it; crashes still spend a slot."""
    if max_calls < 1:
        raise ValueError("max_evaluations must be positive")
    ledger = ledger.resolve()
    with _budget_lock(ledger.with_suffix(ledger.suffix + ".lock")):
        state = json.loads(ledger.read_text(encoding="utf-8")) if ledger.exists() else {
            "max_evaluations": max_calls, "reserved_evaluations": 0,
        }
        if state["max_evaluations"] != max_calls:
            raise ValueError("budget ledger maximum differs from requested maximum")
        if state["reserved_evaluations"] >= max_calls:
            return {**state, "reservation_granted": False, "ledger_path": str(ledger)}
        state["reserved_evaluations"] += 1
        temporary = ledger.with_name(ledger.name + ".tmp." + uuid.uuid4().hex)
        temporary.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        temporary.replace(ledger)
        return {**state, "reservation_granted": True, "ledger_path": str(ledger)}


def run_evaluation(
    graph: Path, config: Path, official_code: Path, problem: str,
    core_count: int, output_root: Path, timeout_seconds: float,
    plan: Path | None = None, seed: int = 0,
    min_subgraph_size: int = 50, max_subgraph_size: int = 100,
    python: str = sys.executable,
    budget_ledger: Path | None = None, max_evaluations: int | None = None,
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
    if (budget_ledger is None) != (max_evaluations is None):
        raise ValueError("budget_ledger and max_evaluations must be supplied together")
    if plan is not None:
        with plan.open(encoding="utf-8") as file:
            provided_plan = json.load(file)
        if len(provided_plan["core_schedules"]) != core_count:
            raise ValueError("plan core_schedules length differs from core_count")

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

    if plan_path:
        with plan_path.open(encoding="utf-8") as file:
            generated_plan = json.load(file)
        if len(generated_plan["core_schedules"]) != core_count:
            record.update(status="plan_core_count_mismatch", exit_code=None, timed_out=False)
            _save_record(run_dir, record)
            return record
        pair_text = "|".join((record["input_sha256"], record["config_sha256"],
                              record["plan_sha256"], str(core_count)))
        record["pairing_key_sha256"] = hashlib.sha256(pair_text.encode("ascii")).hexdigest()
    if budget_ledger is not None:
        budget = _reserve_evaluation(budget_ledger, max_evaluations)
        record["evaluation_budget"] = budget
        if not budget["reservation_granted"]:
            record.update(status="budget_exhausted", exit_code=None, timed_out=False)
            _save_record(run_dir, record)
            return record

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
            record["status"] = "success" if record["max_op_end_matches_makespan"] is not False else "metric_mismatch"
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
    parser.add_argument("--budget-ledger", type=Path)
    parser.add_argument("--max-evaluations", type=int)
    args = parser.parse_args()
    record = run_evaluation(
        args.graph, args.config, args.official_code, args.problem, args.cores,
        args.output_root, args.timeout, args.plan, args.seed,
        args.min_subgraph_size, args.max_subgraph_size,
        budget_ledger=args.budget_ledger, max_evaluations=args.max_evaluations,
    )
    print(json.dumps({key: record.get(key) for key in (
        "case_id", "problem", "core_count", "status", "makespan",
        "added_copy_bytes", "cache_hit_rate", "plan_runtime_seconds",
        "evaluation_runtime_seconds", "run_dir")}, ensure_ascii=False))
    if record["status"] != "success":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
