import json
import os
import stat
import unittest

from ._baseline import GRAPH, GRAPH_DIR, HTML, REPORT, RUNBOOK, SCRIPT, read


class GraphifyBehaviorTests(unittest.TestCase):
    def test_graph_directory_exists(self): self.assertTrue(GRAPH_DIR.is_dir())
    def test_graph_json_exists(self): self.assertTrue(GRAPH.is_file())
    def test_graph_html_exists(self): self.assertTrue(HTML.is_file())
    def test_graph_report_exists(self): self.assertTrue(REPORT.is_file())
    def test_graph_json_is_valid(self): self.assertIsInstance(json.loads(read(GRAPH)), dict)
    def test_graph_has_nodes(self): self.assertTrue(json.loads(read(GRAPH)).get("nodes"))
    def test_graph_has_edges(self):
        payload = json.loads(read(GRAPH))
        self.assertTrue(payload.get("edges") or payload.get("links"))
    def test_sync_script_exists(self): self.assertTrue(SCRIPT.is_file())
    def test_sync_script_is_executable(self): self.assertTrue(os.stat(SCRIPT).st_mode & stat.S_IXUSR)
    def test_runbook_exists(self): self.assertTrue(RUNBOOK.is_file())


if __name__ == "__main__": unittest.main()
