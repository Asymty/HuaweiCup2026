from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.evaluate.a_metric_audit import (
    audit_result,
    compare_results,
    recompute_cache_stats,
    recompute_data_movement,
    recompute_makespan,
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
