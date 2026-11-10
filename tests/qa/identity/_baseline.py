from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[3]
IDENTITY = ROOT / "backend" / "app" / "identity"
API = ROOT / "backend" / "app" / "api"
MAIN = ROOT / "backend" / "app" / "main.py"
CONTRACT = ROOT / "docs" / "contracts" / "identity-and-policy.md"
BASELINE = ROOT / "docs" / "contracts" / "v1-baseline.md"
HANDOFF = ROOT / "harness" / "handoffs" / "IDENT-001.md"
TASKS = ROOT / "harness" / "tasks" / "tasks.json"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def tasks() -> dict:
    return json.loads(read(TASKS))


def task(task_id: str) -> dict:
    return next(item for item in tasks()["tasks"] if item["id"] == task_id)
