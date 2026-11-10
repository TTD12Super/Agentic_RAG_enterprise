import subprocess
import sys
import unittest

from _baseline import ALERTS, COMPOSE, HANDOFF, MONITORING, ROOT, task, read


class MonitoringOperationalTests(unittest.TestCase):
    def test_compose_yaml_is_accepted_by_docker(self):
        result = subprocess.run(["docker", "compose", "-f", str(COMPOSE), "config", "--quiet"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_all_monitoring_yaml_files_are_nonempty(self):
        for path in MONITORING.glob("*.yml"):
            with self.subTest(path=path.name):
                self.assertGreater(path.stat().st_size, 20)

    def test_dashboard_json_compiles(self):
        result = subprocess.run([sys.executable, "-c", "import json,sys; json.load(open(sys.argv[1]))", str(MONITORING / "grafana/dashboards/enterprise-rag-overview.json")], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_monitoring_task_is_done(self):
        self.assertEqual(task("INFRA-003")["status"], "DONE")

    def test_monitoring_qa_depends_on_monitoring(self):
        self.assertEqual(task("INFRA-MONITOR-QA-001")["depends_on"], ["INFRA-003"])

    def test_alerts_define_p0(self):
        self.assertIn("severity: P0", read(ALERTS))

    def test_alerts_define_p1(self):
        self.assertIn("severity: P1", read(ALERTS))

    def test_handoff_records_config_validation(self):
        self.assertIn("docker compose", read(HANDOFF))

    def test_handoff_records_synthetic_boundary(self):
        self.assertIn("synthetic", read(HANDOFF).lower())

    def test_handoff_records_no_api_key(self):
        self.assertIn("API key", read(HANDOFF))


if __name__ == "__main__":
    unittest.main()
