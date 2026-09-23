from __future__ import annotations

import os
import subprocess
import sys
import unittest
from copy import deepcopy
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.evaluate.a_metric_audit import (
    audit_candidate_pair,
    audit_result,
    build_acceptance_matrix_from_c01,
    compare_results,
    recompute_cache_stats,
    recompute_data_movement,
    recompute_makespan,
    run_official_minimal_acceptance_check,
    run_official_validation_suite,
)


def sample_result(*, makespan: int = 20, hit_bytes: int = 20) -> dict:
    return {
        "makespan": makespan,
        "per_core_timeline": [
            {"core_id": 0, "ops": [{"op_id": 1, "end": 10}]},
            {"core_id": 1, "ops": [{"op_id": 2, "end": 20}]},
        ],
        "data_movement_bytes": {
            "original_graph_copy_bytes": 100,
            "scheduled_copy_bytes": 160,
            "added_copy_bytes": 60,
            "partition_added_copy_bytes": 40,
            "spill_added_copy_bytes": 20,
        },
        "cache_stats": {
            "copy_in_hits": 1,
            "copy_in_misses": 3,
            "hits": 1,
            "accesses": 4,
            "hit_bytes": hit_bytes,
            "miss_bytes": 60,
            "hit_rate": hit_bytes / (hit_bytes + 60),
        },
    }


def sample_record(
    *,
    problem: int,
    makespan: int = 20,
    plan_sha256: str = "a" * 64,
    core_count: int = 2,
    hit_bytes: int = 0,
) -> dict:
    miss_bytes = 60 if problem == 3 else 0
    total_bytes = hit_bytes + miss_bytes
    return {
        "case_id": "case_test",
        "problem": problem,
        "input_sha256": "b" * 64,
        "config_sha256": "c" * 64,
        "core_count": core_count,
        "plan_sha256": plan_sha256,
        "status": "success",
        "legal": True,
        "metrics": {
            "makespan": makespan,
            "original_graph_copy_bytes": 100,
            "scheduled_copy_bytes": 160,
            "added_copy_bytes": 60,
            "physical_ddr_bytes": 160 - hit_bytes,
            "cache_hit_bytes": hit_bytes,
            "cache_miss_bytes": miss_bytes,
            "cache_total_bytes": total_bytes,
            "cache_hit_rate": hit_bytes / total_bytes if total_bytes else 0.0,
            "metric_audit": "PASS",
        },
    }


class MetricAuditTests(unittest.TestCase):
    def test_independent_recomputation(self) -> None:
        result = sample_result()
        self.assertEqual(recompute_makespan(result), 20)
        movement = recompute_data_movement(result)
        self.assertEqual(movement["added_copy_bytes"], 60)
        self.assertEqual(movement["physical_ddr_bytes"], 140)
        cache = recompute_cache_stats(result)
        self.assertEqual(cache["total_bytes"], 80)
        self.assertAlmostEqual(cache["hit_rate"], 0.25)
        self.assertEqual(audit_result(result)["status"], "PASS")

    def test_detects_metric_mismatch(self) -> None:
        result = sample_result(makespan=19)
        result["data_movement_bytes"]["added_copy_bytes"] = 59
        result["cache_stats"]["hit_rate"] = 0.5
        audit = audit_result(result)
        self.assertEqual(audit["status"], "FAIL")
        self.assertGreaterEqual(len(audit["errors"]), 3)

    def test_pair_deltas_use_physical_ddr_semantics(self) -> None:
        control = sample_result(hit_bytes=0)
        control["cache_stats"]["hit_rate"] = 0.0
        treatment = sample_result(hit_bytes=20)
        comparison = compare_results(control, treatment)
        self.assertEqual(comparison["added_copy_bytes_delta"], 0)
        self.assertEqual(comparison["physical_ddr_bytes_delta"], -20)

    def test_acceptance_pair_passes_same_plan_q2_q3(self) -> None:
        control = sample_record(problem=2, makespan=20)
        treatment = sample_record(problem=3, makespan=19, hit_bytes=20)
        audit = audit_candidate_pair(control, treatment, expected_problems=(2, 3))
        self.assertEqual(audit["status"], "PASS")
        self.assertEqual(audit["attribution"], "ISOLATED_MECHANISM")
        self.assertEqual(audit["deltas"]["makespan"], -1)
        self.assertEqual(audit["deltas"]["physical_ddr_bytes"], -20)

    def test_acceptance_pair_fails_mismatched_plan_hash(self) -> None:
        control = sample_record(problem=1)
        treatment = sample_record(problem=2, plan_sha256="d" * 64)
        audit = audit_candidate_pair(control, treatment, expected_problems=(1, 2))
        self.assertEqual(audit["status"], "FAIL")
        self.assertIn("same plan_sha256", " ".join(audit["errors"]))

    def test_acceptance_pair_fails_anomalous_metric(self) -> None:
        control = sample_record(problem=2)
        treatment = sample_record(problem=3, makespan=19, hit_bytes=20)
        treatment["metrics"]["physical_ddr_bytes"] += 1
        audit = audit_candidate_pair(control, treatment, expected_problems=(2, 3))
        self.assertEqual(audit["status"], "FAIL")
        self.assertIn("physical_ddr_bytes mismatch", " ".join(audit["errors"]))

    def test_acceptance_pair_warns_on_hit_without_gain(self) -> None:
        control = sample_record(problem=2, makespan=20)
        treatment = sample_record(problem=3, makespan=20, hit_bytes=20)
        audit = audit_candidate_pair(control, treatment, expected_problems=(2, 3))
        self.assertEqual(audit["status"], "WARN")
        self.assertIn("Makespan did not improve", " ".join(audit["warnings"]))

    def test_acceptance_pair_labels_redesign(self) -> None:
        control = sample_record(problem=2)
        treatment = sample_record(problem=3, makespan=19, plan_sha256="d" * 64)
        audit = audit_candidate_pair(
            control,
            treatment,
            expected_problems=(2, 3),
            comparison_mode="redesign",
        )
        self.assertEqual(audit["status"], "WARN")
        self.assertEqual(audit["attribution"], "REDESIGN_ONLY")

    def test_c01_evidence_drives_falsifiable_acceptance_matrix(self) -> None:
        evidence_dir = PROJECT_ROOT / "shared_evidence" / "phase1" / "task_c_01"
        matrix = build_acceptance_matrix_from_c01(evidence_dir)
        self.assertEqual(matrix["status"], "PASS")
        observed = {
            row["case"]: row["audit"]["status"] for row in matrix["rows"]
        }
        self.assertEqual(
            observed,
            {
                "same_plan_q1_q2": "PASS",
                "same_plan_q2_q3": "PASS",
                "q3_hit_without_gain": "WARN",
                "mismatched_plan_hash": "FAIL",
                "anomalous_physical_ddr": "FAIL",
                "redesigned_plan": "WARN",
            },
        )

    def test_direct_cli_help_starts_outside_repository(self) -> None:
        script = PROJECT_ROOT / "src" / "evaluate" / "a_metric_audit.py"
        completed = subprocess.run(
            [sys.executable, str(script), "--help"],
            cwd=PROJECT_ROOT.parent,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("--acceptance-evidence-dir", completed.stdout)

    def test_official_minimal_acceptance_check(self) -> None:
        root_text = os.environ.get("A_OFFICIAL_ROOT")
        if not root_text:
            self.skipTest("A_OFFICIAL_ROOT is not set")
        root = Path(root_text)
        if not (root / "code").is_dir():
            self.skipTest(f"official code directory not found under {root}")
        evidence = run_official_minimal_acceptance_check(root)
        self.assertEqual(evidence["status"], "PASS")
        self.assertEqual(
            {record["metrics"]["makespan"] for record in evidence["records"].values()},
            {3},
        )
        self.assertEqual(evidence["pair_audits"]["q1_q2"]["status"], "PASS")
        self.assertEqual(evidence["pair_audits"]["q2_q3"]["status"], "PASS")

    def test_official_q2_q3_pairs_and_legality_parity(self) -> None:
        root_text = os.environ.get("A_OFFICIAL_ROOT")
        if not root_text:
            self.skipTest("A_OFFICIAL_ROOT is not set")
        root = Path(root_text)
        if not (root / "code").is_dir():
            self.skipTest(f"official code directory not found under {root}")
        evidence = run_official_validation_suite(root)
        self.assertEqual(
            evidence["status"],
            {
                "legality": "PASS",
                "metric_audit": "PASS",
                "q2_mechanism": "PASS",
                "q3_l2_mechanism": "PASS",
            },
        )
        self.assertTrue(all(row["match"] for row in evidence["legality_parity"]))
        self.assertEqual(
            evidence["q2_pair"]["control_q1_multiple_tasks_same_core"]["makespan"],
            800,
        )
        self.assertEqual(
            evidence["q2_pair"]["treatment_q2_merged_task_same_core"]["makespan"],
            400,
        )
        self.assertEqual(
            evidence["q3_pair"]["treatment_q3_split_with_l2"]["cache_stats"]["hit_bytes"],
            6000,
        )
        boundary = evidence["q3_pair"]["tiny_hit_no_latency_gain"]
        self.assertEqual(boundary["q2_no_l2"]["makespan"], boundary["q3_with_l2"]["makespan"])
        self.assertGreater(boundary["q3_with_l2"]["cache_stats"]["hit_bytes"], 0)


if __name__ == "__main__":
    unittest.main()
