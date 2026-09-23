from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.evaluate.a_legality import check_execution_graph, check_plan_legality


def direct_graph(edges: list[tuple[int, int]], op_ids: list[int]) -> dict:
    return {
        "tensors": [],
        "ops": [
            {"id": op_id, "op": "ADD", "pipe": "PIPE_V", "cycles": 1}
            for op_id in op_ids
        ],
        "edges": [{"source": source, "target": target} for source, target in edges],
    }


class LegalityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = direct_graph([(11, 12)], [11, 12])
        self.plan = {
            "node_to_subgraph": {"11": 0, "12": 1},
            "core_schedules": [[0, 1], []],
        }

    def test_legal_positive(self) -> None:
        report = check_plan_legality(self.graph, self.plan, problem=1)
        self.assertTrue(report.legal, report.to_dict())
        self.assertEqual(report.details["task_count"], 2)

    def test_missing_mapping(self) -> None:
        plan = {
            "node_to_subgraph": {"11": 0},
            "core_schedules": [[0]],
        }
        report = check_plan_legality(self.graph, plan)
        self.assertFalse(report.legal)
        self.assertEqual(report.errors[0].code, "mapping_coverage")

    def test_duplicate_integer_mapping_alias(self) -> None:
        plan = {
            "node_to_subgraph": {"11": 0, "011": 0, "12": 1},
            "core_schedules": [[0, 1]],
        }
        report = check_plan_legality(self.graph, plan)
        self.assertFalse(report.legal)
        self.assertEqual(report.errors[0].code, "duplicate_mapping")

    def test_duplicate_subgraph_schedule(self) -> None:
        plan = {
            "node_to_subgraph": {"11": 0, "12": 1},
            "core_schedules": [[0, 1], [1]],
        }
        report = check_plan_legality(self.graph, plan)
        self.assertFalse(report.legal)
        self.assertEqual(report.errors[0].code, "schedule_coverage")

    def test_dependency_order_violation(self) -> None:
        plan = {
            "node_to_subgraph": {"11": 0, "12": 1},
            "core_schedules": [[1, 0]],
        }
        report = check_plan_legality(self.graph, plan)
        self.assertFalse(report.legal)
        self.assertEqual(report.errors[0].code, "dependency_order")

    def test_contracted_subgraph_cycle(self) -> None:
        graph = direct_graph([(11, 12), (12, 13)], [11, 12, 13])
        plan = {
            "node_to_subgraph": {"11": 0, "12": 1, "13": 0},
            "core_schedules": [[0, 1]],
        }
        report = check_plan_legality(graph, plan)
        self.assertFalse(report.legal)
        self.assertEqual(report.errors[0].code, "subgraph_cycle")

    def test_q1_task_order_combination_cycle(self) -> None:
        graph = direct_graph([(11, 12), (13, 14)], [11, 12, 13, 14])
        plan = {
            "node_to_subgraph": {"11": 0, "12": 1, "13": 2, "14": 3},
            "core_schedules": [[3, 0], [1, 2]],
        }
        report = check_plan_legality(graph, plan, problem=1)
        self.assertFalse(report.legal)
        self.assertEqual(report.errors[0].code, "task_schedule_cycle")

    def test_expanded_execution_cycle(self) -> None:
        report = check_execution_graph(
            nodes=[("c0", 1), ("c0", 2), ("c1", 3)],
            dependency_edges=[(("c0", 1), ("c0", 2))],
            fifo_edges=[(("c1", 3), ("c0", 1))],
            cross_core_edges=[(("c0", 2), ("c1", 3))],
        )
        self.assertFalse(report.legal)
        self.assertEqual(report.errors[0].code, "execution_cycle")


if __name__ == "__main__":
    unittest.main()
