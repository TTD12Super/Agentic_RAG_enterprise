"""Dependency-free helpers for DB-001 QA."""

from pathlib import Path
import json
import subprocess


ROOT = Path(__file__).resolve().parents[3]
DB_APP = ROOT / "backend" / "app" / "db"
MIGRATIONS = DB_APP / "migrations" / "versions"
ALEMBIC_INI = DB_APP / "alembic.ini"
ENV_PY = DB_APP / "migrations" / "env.py"
DATABASE_DOC = ROOT / "docs" / "database" / "database.md"
CONTRACT = ROOT / "docs" / "contracts" / "v1-baseline.md"
HANDOFF = ROOT / "harness" / "handoffs" / "DB-001.md"
TASKS = ROOT / "harness" / "tasks" / "tasks.json"
COMPOSE = ROOT / "infra" / "docker" / "postgres-test.compose.yml"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def migration_files() -> list[Path]:
    return sorted(MIGRATIONS.glob("*.py"))


def migration_text() -> str:
    return "\n".join(read(path) for path in migration_files())


def tasks() -> dict:
    return json.loads(read(TASKS))


def task(task_id: str) -> dict:
    return next(item for item in tasks()["tasks"] if item["id"] == task_id)


def compose_config_result() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", "compose", "-f", str(COMPOSE), "config", "--quiet"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
