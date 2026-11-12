import unittest

from ._baseline import ALERTMANAGER, ALERTS, COMPOSE, DATASOURCE, DASHBOARD, MONITORING, OTEL, PROMETHEUS, read


class MonitoringBehaviorTests(unittest.TestCase):
    def test_monitoring_directory_exists(self):
        self.assertTrue(MONITORING.is_dir())

    def test_collector_config_exists(self):
        self.assertTrue(OTEL.is_file())

    def test_prometheus_config_exists(self):
        self.assertTrue(PROMETHEUS.is_file())

    def test_alert_rules_exist(self):
        self.assertTrue(ALERTS.is_file())

    def test_alertmanager_config_exists(self):
        self.assertTrue(ALERTMANAGER.is_file())

    def test_compose_boundary_exists(self):
        self.assertTrue(COMPOSE.is_file())

    def test_dashboard_exists(self):
        self.assertTrue(DASHBOARD.is_file())

    def test_grafana_datasource_exists(self):
        self.assertTrue(DATASOURCE.is_file())

    def test_collector_receives_otlp(self):
        text = read(OTEL)
        self.assertIn("otlp:", text)
        self.assertIn("grpc:", text)
        self.assertIn("http:", text)

    def test_collector_exports_prometheus(self):
        self.assertIn("exporters: [prometheus]", read(OTEL))


if __name__ == "__main__":
    unittest.main()
