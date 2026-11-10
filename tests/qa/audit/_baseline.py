from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[3]
OBS = ROOT / "backend" / "app" / "observability"
AUDIT = OBS / "audit.py"
CONTEXT = OBS / "context.py"
IDENTITY_API = ROOT / "backend" / "app" / "api" / "identity.py"
MAIN = ROOT / "backend" / "app" / "main.py"
EVENTS_CONTRACT = ROOT / "docs" / "contracts" / "events-and-audit.md"
BASELINE_CONTRACT = ROOT / "docs" / "contracts" / "v1-baseline.md"
HANDOFF = ROOT / "harness" / "handoffs" / "AUDIT-001.md"
TASKS = ROOT / "harness" / "tasks" / "tasks.json"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def tasks() -> dict:
    return json.loads(read(TASKS))


def task(task_id: str) -> dict:
    return next(item for item in tasks()["tasks"] if item["id"] == task_id)
