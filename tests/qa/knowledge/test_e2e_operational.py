import json
import subprocess
import sys
import unittest

from ._baseline import GRAPH, HANDOFF, ROOT, read, task


class KnowledgeOperationalTests(unittest.TestCase):
    def test_task_registry_contains_know001(self):
        self.assertEqual(task("KNOW-001")["title"], "Implement metadata and parent-child chunk schema")

    def test_task_registry_has_required_dependencies(self):
        self.assertEqual(task("KNOW-001")["depends_on"], ["CONTRACT-001", "INFRA-001", "DB-001"])

    def test_task_registry_keeps_tech_lead_acceptance_boundary(self):
        self.assertIn("Tech Lead review", task("KNOW-001")["acceptance"])

    def test_task_scope_forbids_unauthorized_modules(self):
        forbidden = task("KNOW-001")["scope"]["forbidden_paths"]
        self.assertTrue({"backend/app/authorization", "backend/app/rag", "frontend", "infra", "docs/contracts"} <= set(forbidden))

    def test_task_scope_allows_only_knowledge_backend_tests_and_handoff(self):
        self.assertEqual(task("KNOW-001")["scope"]["write_paths"], ["backend/app/knowledge", "backend/tests", "harness/handoffs"])

    def test_handoff_records_main_review_acceptance(self):
        self.assertIn("ACCEPTED — MAIN AGENT REVIEW", read(HANDOFF))

    def test_handoff_records_database_probe_boundary(self):
        handoff = read(HANDOFF)
        self.assertIn("DB001_DATABASE_URL", handoff)
        self.assertIn("live PostgreSQL probe", handoff)

    def test_graph_contains_knowledge_source_node(self):
        self.assertTrue(GRAPH.is_file())
        graph = json.loads(read(GRAPH))
        nodes = graph.get("nodes", [])
        self.assertTrue(any("knowledge/models.py" in str(node) for node in nodes))

    def test_harness_validator_passes(self):
        result = subprocess.run([sys.executable, "scripts/validate_harness.py"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_relevant_backend_knowledge_tests_pass(self):
        result = subprocess.run([sys.executable, "-m", "pytest", "backend/tests", "-k", "knowledge", "-q"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
