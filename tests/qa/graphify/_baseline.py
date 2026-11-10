from pathlib import Path
import json
import os
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "sync_graph.sh"
IGNORE = ROOT / ".graphifyignore"
RUNBOOK = ROOT / "docs" / "operations" / "graphify-runbook.md"
GRAPH_DIR = ROOT / "graphify-out"
GRAPH = GRAPH_DIR / "graph.json"
HTML = GRAPH_DIR / "graph.html"
REPORT = GRAPH_DIR / "GRAPH_REPORT.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def graphify_bin() -> str | None:
    configured = os.environ.get("GRAPHIFY_BIN")
    if configured and shutil.which(configured):
        return configured
    return shutil.which("graphify") or ("/tmp/graphify-venv/bin/graphify" if Path("/tmp/graphify-venv/bin/graphify").is_file() else None)


def graph() -> dict:
    return json.loads(read(GRAPH))


def run_graphify(*args: str) -> subprocess.CompletedProcess[str]:
    binary = graphify_bin()
    if binary is None:
        raise unittest.SkipTest("graphify CLI is not installed")
    return subprocess.run([binary, *args], cwd=ROOT, text=True, capture_output=True, check=False)
