import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MONITORING = ROOT / "infra" / "monitoring"


def test_monitoring_configuration_files_exist():
    for path in (
        "otel-collector-config.yaml",
        "prometheus.yml",
        "alerts.yml",
        "alertmanager.yml",
        "compose.yml",
        "grafana/provisioning/datasources/prometheus.yml",
        "grafana/dashboards/enterprise-rag-overview.json",
    ):
        assert (MONITORING / path).is_file()


def test_dashboard_is_valid_json():
    json.loads((MONITORING / "grafana/dashboards/enterprise-rag-overview.json").read_text())


def test_collector_has_privacy_processor_and_metrics_pipeline():
    text = (MONITORING / "otel-collector-config.yaml").read_text()
    assert "attributes/privacy" in text
    assert "conversation.body" in text
    assert "pipelines:" in text
    assert "exporters: [prometheus]" in text


def test_prometheus_loads_rules_and_collector_target():
    text = (MONITORING / "prometheus.yml").read_text()
    assert "/etc/prometheus/rules/alerts.yml" in text
    assert "otel-collector:8889" in text


def test_alerts_have_severity_and_runbook():
    text = (MONITORING / "alerts.yml").read_text()
    assert "severity: P0" in text
    assert "severity: P1" in text
    assert "docs/operations/incident-response.md" in text


def test_alertmanager_has_no_external_recipient():
    text = (MONITORING / "alertmanager.yml").read_text()
    assert "local-sink" in text
    assert "webhook_configs" not in text


def test_compose_binds_monitoring_ports_to_loopback():
    text = (MONITORING / "compose.yml").read_text()
    assert '"127.0.0.1:9090:9090"' in text
    assert '"127.0.0.1:3000:3000"' in text
    assert '"127.0.0.1:9093:9093"' in text


def test_compose_config_is_read_only_and_non_privileged():
    text = (MONITORING / "compose.yml").read_text()
    assert text.count("read_only: true") == 4
    assert text.count("no-new-privileges:true") == 4


def test_dashboard_has_api_and_security_panels():
    dashboard = json.loads((MONITORING / "grafana/dashboards/enterprise-rag-overview.json").read_text())
    titles = {panel["title"] for panel in dashboard["panels"]}
    assert {"API request rate", "Authorization denials"} <= titles


def test_monitoring_docs_keep_provider_and_recipient_pending():
    docs = (ROOT / "docs/architecture/blocks/15-observability-audit.md").read_text()
    assert "Provider/backend pending" in docs
    assert "Actual recipients" in docs
