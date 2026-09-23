"""Behavior checks for the wrapper; official scoring is exercised in the pilot."""

import json
import tempfile
import unittest
from pathlib import Path

from src.evaluate.a_official_runner import run_evaluation, sha256


class OfficialRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.code = self.root / "code"
        self.code.mkdir()
        self.graph = self.root / "case_001.json"
        self.graph.write_text('{"ops": [], "tensors": [], "edges": []}', encoding="utf-8")
        self.config = self.root / "config.txt"
        self.config.write_text("fixed-config", encoding="utf-8")
        self.plan = self.root / "plan.json"
        self.plan.write_text("{}", encoding="utf-8")

    def script(self, body):
        (self.code / "multicore_cut_evaluate_problem_1.py").write_text(
            "import sys, json, pathlib, time\n" + body, encoding="utf-8"
        )

    def run_case(self, timeout=2):
        return run_evaluation(
            self.graph, self.config, self.code, "1", 2,
            self.root / "runs", timeout, plan=self.plan,
        )

    def test_success_hash_metrics_and_files(self):
        self.script(
            "print('success stream')\n"
            "print('diagnostic', file=sys.stderr)\n"
            "out=pathlib.Path(sys.argv[sys.argv.index('--output')+1])\n"
            "out.write_text(json.dumps({'makespan': 42, 'data_movement_bytes': "
            "{'scheduled_copy_bytes': 15, 'original_graph_copy_bytes': 5}, "
            "'cache_stats': {'hit_rate': 0.5, 'hit_bytes': 10}}))\n"
        )
        record = self.run_case()
        self.assertEqual(record["status"], "success")
        self.assertEqual(record["makespan"], 42)
        self.assertEqual(record["added_copy_bytes"], 10)
        self.assertEqual(record["input_sha256"], sha256(self.graph))
        self.assertEqual(record["config_sha256"], sha256(self.config))
        self.assertEqual(record["plan_sha256"], sha256(self.plan))
        run_dir = Path(record["run_dir"])
        self.assertIn("success stream", (run_dir / "evaluation.stdout.txt").read_text())
        self.assertIn("diagnostic", (run_dir / "evaluation.stderr.txt").read_text())
        self.assertEqual(json.loads((run_dir / "run_record.json").read_text())["exit_code"], 0)
        self.assertTrue(Path(record["result_path"]).is_file())

    def test_illegal_plan_and_stderr(self):
        self.script("print('[EVALUATION ERROR] illegal plan', file=sys.stderr)\nsys.exit(1)\n")
        record = self.run_case()
        self.assertEqual(record["status"], "evaluation_failed")
        self.assertEqual(record["exit_code"], 1)
        self.assertFalse(Path(record["result_path"]).exists())
        self.assertIn("illegal plan", (Path(record["run_dir"]) / "evaluation.stderr.txt").read_text())

    def test_timeout(self):
        self.script("time.sleep(1)\n")
        record = self.run_case(timeout=0.05)
        self.assertEqual(record["status"], "timeout")
        self.assertTrue(record["timed_out"])
        self.assertIsNone(record["exit_code"])
        self.assertTrue((Path(record["run_dir"]) / "run_record.json").exists())

    def test_output_missing(self):
        self.script("print('completed without output')\n")
        record = self.run_case()
        self.assertEqual(record["status"], "output_missing")
        self.assertEqual(record["exit_code"], 0)


if __name__ == "__main__":
    unittest.main()
