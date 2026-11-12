import subprocess
import sys
import unittest

from ._baseline import AUDIT, CONTEXT, HANDOFF, IDENTITY_API, MAIN, ROOT, task, read


class AuditOperationalTests(unittest.TestCase):
    def test_observability_sources_compile(self):
        paths = sorted((ROOT / "backend" / "app" / "observability").glob("*.py"))
        result = subprocess.run([sys.executable, "-m", "py_compile", *(str(path) for path in paths)], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_api_and_main_sources_compile(self):
        result = subprocess.run([sys.executable, "-m", "py_compile", str(IDENTITY_API), str(MAIN)], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_audit_task_is_done(self):
        self.assertEqual(task("AUDIT-001")["status"], "DONE")

    def test_audit_qa_task_depends_on_audit(self):
        self.assertEqual(task("AUDIT-QA-001")["depends_on"], ["AUDIT-001"])

    def test_task_validation_mentions_audit_tests(self):
        self.assertTrue(any("audit" in value.lower() for value in task("AUDIT-001")["validation"]))

    def test_handoff_has_correlation_evidence(self):
        self.assertIn("correlation", read(HANDOFF).lower())

    def test_handoff_has_redaction_evidence(self):
        self.assertIn("redaction", read(HANDOFF).lower())

    def test_handoff_has_unavailable_sink_evidence(self):
        self.assertIn("unavailable", read(HANDOFF).lower())

    def test_handoff_declares_process_local_limit(self):
        self.assertIn("process-local", read(HANDOFF))

    def test_audit_does_not_provision_cloud(self):
        self.assertIn("No OpenTelemetry collector/exporter", read(HANDOFF))


if __name__ == "__main__":
    unittest.main()
