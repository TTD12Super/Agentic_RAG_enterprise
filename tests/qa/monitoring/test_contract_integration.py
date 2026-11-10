import unittest

from _baseline import ALERTMANAGER, ALERTS, DATASOURCE, DASHBOARD, INCIDENT, OTEL, PROMETHEUS, RUNBOOK, dashboard, read


class MonitoringContractTests(unittest.TestCase):
    def test_collector_has_memory_limit(self):
        self.assertIn("memory_limiter:", read(OTEL))

    def test_collector_has_batching(self):
        self.assertIn("batch:", read(OTEL))

    def test_collector_privacy_processor_is_in_metrics_pipeline(self):
        text = read(OTEL)
        self.assertIn("attributes/privacy", text)
        self.assertIn("processors: [memory_limiter, attributes/privacy, batch]", text)

    def test_prometheus_loads_alert_rules(self):
        self.assertIn("/etc/prometheus/rules/alerts.yml", read(PROMETHEUS))

    def test_prometheus_scrapes_collector(self):
        self.assertIn("otel-collector:8889", read(PROMETHEUS))

    def test_alert_rules_link_runbook(self):
        self.assertIn("docs/operations/incident-response.md", read(ALERTS))

    def test_alertmanager_has_local_route(self):
        self.assertIn("receiver: local-sink", read(ALERTMANAGER))

    def test_dashboard_has_schema_version(self):
        self.assertEqual(dashboard()["schemaVersion"], 39)

    def test_datasource_points_to_prometheus(self):
        self.assertIn("http://prometheus:9090", read(DATASOURCE))

    def test_runbook_documents_loopback_stack(self):
        self.assertIn("infra/monitoring/compose.yml", read(RUNBOOK))


if __name__ == "__main__":
    unittest.main()
