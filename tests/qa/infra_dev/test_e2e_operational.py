import subprocess
import unittest

from ._baseline import COMPOSE, HANDOFF, ROOT, SCRIPT, task, read, compose_config


class InfrastructureOperationalTests(unittest.TestCase):
    def test_compose_config_is_valid(self):
        result = compose_config()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_migration_script_has_valid_shell_syntax(self):
        result = subprocess.run(["sh", "-n", str(SCRIPT)], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_compose_healthcheck_is_bounded(self):
        text = read(COMPOSE)
        self.assertIn("interval: 2s", text)
        self.assertIn("timeout: 3s", text)
        self.assertIn("retries: 15", text)

    def test_compose_restart_is_disabled(self):
        self.assertIn('restart: "no"', read(COMPOSE))

    def test_handoff_records_healthy_database(self):
        self.assertIn("PostgreSQL healthy", read(HANDOFF))

    def test_handoff_records_no_cloud_use(self):
        self.assertIn("No cloud account", read(HANDOFF))

    def test_handoff_records_production_boundary(self):
        self.assertIn("not a production deployment", read(HANDOFF))

    def test_task_is_integration_ready(self):
        self.assertEqual(task("INFRA-001")["status"], "DONE")

    def test_qa_task_depends_on_infra_task(self):
        self.assertEqual(task("INFRA-QA-001")["depends_on"], ["INFRA-001"])

    def test_migration_runner_has_usage_guard(self):
        self.assertIn("Usage:", read(SCRIPT))


if __name__ == "__main__":
    unittest.main()
