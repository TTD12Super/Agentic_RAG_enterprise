from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[3]
MONITORING = ROOT / "infra" / "monitoring"
OTEL = MONITORING / "otel-collector-config.yaml"
PROMETHEUS = MONITORING / "prometheus.yml"
ALERTS = MONITORING / "alerts.yml"
ALERTMANAGER = MONITORING / "alertmanager.yml"
COMPOSE = MONITORING / "compose.yml"
DASHBOARD = MONITORING / "grafana/dashboards/enterprise-rag-overview.json"
DATASOURCE = MONITORING / "grafana/provisioning/datasources/prometheus.yml"
RUNBOOK = ROOT / "docs/operations/deployment-runbook.md"
INCIDENT = ROOT / "docs/operations/incident-response.md"
HANDOFF = ROOT / "harness/handoffs/INFRA-003.md"
TASKS = ROOT / "harness/tasks/tasks.json"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def task(task_id: str) -> dict:
    import json
    packet = json.loads(read(TASKS))
    return next(item for item in packet["tasks"] if item["id"] == task_id)


def dashboard() -> dict:
    return json.loads(read(DASHBOARD))
