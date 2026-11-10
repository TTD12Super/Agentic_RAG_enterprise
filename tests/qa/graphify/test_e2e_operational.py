import subprocess
import unittest

from _baseline import GRAPH, HTML, REPORT, ROOT, SCRIPT, graphify_bin, run_graphify


@unittest.skipUnless(graphify_bin(), "graphify CLI is not installed")
class GraphifyOperationalTests(unittest.TestCase):
    def test_help(self): self.assertEqual(run_graphify("--help").returncode, 0)
    def test_graph_query(self): self.assertIn(run_graphify("query", "backend").returncode, (0, 3, 4))
    def test_god_nodes(self): self.assertEqual(run_graphify("god-nodes", "--top", "3").returncode, 0)
    def test_report_is_nonempty(self): self.assertGreater(REPORT.stat().st_size, 0)
    def test_html_is_nonempty(self): self.assertGreater(HTML.stat().st_size, 0)
    def test_graph_is_nonempty(self): self.assertGreater(GRAPH.stat().st_size, 0)
    def test_script_syntax(self): self.assertEqual(subprocess.run(["sh", "-n", str(SCRIPT)], cwd=ROOT).returncode, 0)
    def test_script_is_in_repo(self): self.assertTrue(SCRIPT.is_file())
    def test_graph_query_has_output(self):
        result = run_graphify("query", "RAG")
        self.assertTrue(result.stdout.strip() or result.stderr.strip())
    def test_graph_explain_is_callable(self): self.assertIn(run_graphify("explain", "FastAPI").returncode, (0, 3, 4))


if __name__ == "__main__": unittest.main()
