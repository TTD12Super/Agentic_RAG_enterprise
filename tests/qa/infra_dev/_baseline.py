from pathlib import Path
import json
import subprocess


ROOT = Path(__file__).resolve().parents[3]
COMPOSE = ROOT / "infra" / "docker" / "development.compose.yml"
SCRIPT = ROOT / "infra" / "scripts" / "migrate.sh"
HANDOFF = ROOT / "harness" / "handoffs" / "INFRA-001.md"
TASKS = ROOT / "harness" / "tasks" / "tasks.json"
README = ROOT / "infra" / "README.md"
RUNBOOK = ROOT / "docs" / "operations" / "deployment-runbook.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def tasks() -> dict:
    return json.loads(read(TASKS))


def task(task_id: str) -> dict:
    return next(item for item in tasks()["tasks"] if item["id"] == task_id)


def compose_config() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", "compose", "-f", str(COMPOSE), "config", "--quiet"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
