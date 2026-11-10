from functools import lru_cache
from pathlib import Path
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[3]
COMPOSE_PATH = REPO_ROOT / "infra/docker/postgres-test.compose.yml"
DATABASE_DOC = REPO_ROOT / "docs/database/database.md"
TESTING_DOC = REPO_ROOT / "docs/testing/README.md"
BOOT_HANDOFF = REPO_ROOT / "harness/handoffs/INFRA-BOOT-001.md"
TASKS = REPO_ROOT / "harness/tasks/tasks.json"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def compose_config_result() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", "compose", "-f", str(COMPOSE_PATH), "config", "--quiet"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def compose() -> str:
    return read(COMPOSE_PATH)


def database() -> str:
    return read(DATABASE_DOC)


def handoff() -> str:
    return read(BOOT_HANDOFF)


def tasks() -> str:
    return read(TASKS)


def testing() -> str:
    return read(TESTING_DOC)
