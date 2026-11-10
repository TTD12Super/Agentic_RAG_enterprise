"""Deterministic ING-001 QA fixtures and repository evidence."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from backend.app.ingestion import InMemoryDerivedIndex, IngestionService
from backend.tests._ingestion_fixtures import (
    Clock,
    active,
    make_chunks,
    make_manifest,
    new_service,
    quarantine,
    staged,
    validated,
)


ROOT = Path(__file__).resolve().parents[3]
TASKS = ROOT / "harness/tasks/tasks.json"
HANDOFF = ROOT / "harness/handoffs/ING-001.md"
GRAPH = ROOT / "graphify-out/graph.json"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def task(task_id: str) -> dict[str, Any]:
    payload = json.loads(read(TASKS))
    return next(item for item in payload["tasks"] if item["id"] == task_id)


def graph_labels() -> set[str]:
    payload = json.loads(read(GRAPH))
    return {str(node["label"]) for node in payload.get("nodes", [])}


def run_graph_query(query: str) -> subprocess.CompletedProcess[str]:
    executable = shutil.which("graphify") or "/tmp/graphify-venv/bin/graphify"
    return subprocess.run(
        [executable, "query", query, "--graph", str(GRAPH), "--budget", "3000"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class RuntimeFailureOnRemove(InMemoryDerivedIndex):
    """Synthetic adapter that exposes raw backend failure at cleanup."""

    def remove(self, publication_id: str) -> None:
        raise RuntimeError("synthetic-secret-index-error")


def service_with_index(index: InMemoryDerivedIndex) -> tuple[IngestionService, Clock]:
    clock = Clock()
    return IngestionService(derived_index=index, clock=clock), clock


__all__ = [
    "GRAPH",
    "HANDOFF",
    "ROOT",
    "RuntimeFailureOnRemove",
    "active",
    "graph_labels",
    "make_chunks",
    "make_manifest",
    "new_service",
    "quarantine",
    "read",
    "run_graph_query",
    "service_with_index",
    "staged",
    "sys",
    "task",
    "validated",
]
