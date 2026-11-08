import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_graph.py"
EXAMPLE = ROOT / "examples" / "graph.json"


class GraphValidatorTests(unittest.TestCase):
    def run_graph(self, graph):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "graph.json"
            path.write_text(json.dumps(graph), encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(VALIDATOR), str(path)],
                cwd=ROOT, capture_output=True, text=True, check=False
            )

    def load_example(self):
        return json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_example_graph_is_valid_and_levels_are_derived(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), str(EXAMPLE)],
            cwd=ROOT, capture_output=True, text=True, check=False
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("3 node(s), 3 execution level(s)", result.stdout)

    def test_unknown_dependency_is_rejected(self):
        graph = self.load_example()
        graph["nodes"][1]["depends_on"][0]["node"] = "MISSING"
        result = self.run_graph(graph)
        self.assertEqual(result.returncode, 1)
        self.assertIn("unknown dependency MISSING", result.stderr)

    def test_cycle_is_rejected(self):
        graph = self.load_example()
        graph["nodes"][0]["depends_on"] = [{"node": "N3", "because": "invalid cycle for test"}]
        result = self.run_graph(graph)
        self.assertEqual(result.returncode, 1)
        self.assertIn("dependency cycle detected", result.stderr)

    def test_dependency_reason_is_required(self):
        graph = self.load_example()
        graph["nodes"][1]["depends_on"][0]["because"] = "  "
        result = self.run_graph(graph)
        self.assertEqual(result.returncode, 1)
        self.assertIn("because must explain", result.stderr)

    def test_duplicate_node_id_is_rejected(self):
        graph = self.load_example()
        graph["nodes"][1]["id"] = "N1"
        result = self.run_graph(graph)
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate node id: N1", result.stderr)

    def test_empty_done_when_is_rejected(self):
        graph = self.load_example()
        graph["contract"]["done_when"] = []
        result = self.run_graph(graph)
        self.assertEqual(result.returncode, 1)
        self.assertIn("done_when must contain at least one", result.stderr)

    def test_empty_node_acceptance_is_rejected(self):
        graph = self.load_example()
        graph["nodes"][0]["acceptance"] = []
        result = self.run_graph(graph)
        self.assertEqual(result.returncode, 1)
        self.assertIn("acceptance must contain at least one", result.stderr)

    def test_non_string_risk_is_rejected_without_crashing(self):
        graph = self.load_example()
        graph["nodes"][0]["risk"] = ["low"]
        result = self.run_graph(graph)
        self.assertEqual(result.returncode, 1)
        self.assertIn("risk must be one of", result.stderr)


if __name__ == "__main__":
    unittest.main()
