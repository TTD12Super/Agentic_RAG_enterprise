import unittest

from ._baseline import IGNORE, ROOT, RUNBOOK, SCRIPT, read


class GraphifyContractTests(unittest.TestCase):
    def test_script_uses_update_for_existing_graph(self): self.assertIn("run_graphify update .", read(SCRIPT))
    def test_script_uses_code_only_for_first_build(self): self.assertIn("extract . --code-only", read(SCRIPT))
    def test_script_exports_html(self): self.assertIn("export html", read(SCRIPT))
    def test_script_checks_graph_json(self): self.assertIn("graphify-out/graph.json", read(SCRIPT))
    def test_script_checks_graph_html(self): self.assertIn("graphify-out/graph.html", read(SCRIPT))
    def test_script_checks_report(self): self.assertIn("GRAPH_REPORT.md", read(SCRIPT))
    def test_ignore_contains_graph_output(self): self.assertIn("graphify-out/", read(ROOT / ".gitignore"))
    def test_ignore_contains_private_data(self): self.assertIn("data/private/", read(IGNORE))
    def test_runbook_documents_hook(self): self.assertIn("graphify hook install", read(RUNBOOK))
    def test_runbook_documents_query(self): self.assertIn("graphify query", read(RUNBOOK))


if __name__ == "__main__": unittest.main()
