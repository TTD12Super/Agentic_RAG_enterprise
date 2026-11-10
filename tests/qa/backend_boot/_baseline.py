"""Small, dependency-free inspection helpers for backend bootstrap QA."""

from __future__ import annotations

import ast
import json
import os
from pathlib import Path
import subprocess
import sys
import tomllib
from typing import Iterable


ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "backend"
MAIN_PATH = BACKEND / "app" / "main.py"
CONFIG_PATH = BACKEND / "app" / "core" / "config.py"
CONTRACT_PATH = ROOT / "docs" / "contracts" / "v1-baseline.md"
HANDOFF_PATH = ROOT / "harness" / "handoffs" / "BACKEND-BOOT-001.md"
README_PATH = BACKEND / "README.md"
PYPROJECT_PATH = BACKEND / "pyproject.toml"
TASKS_PATH = ROOT / "harness" / "tasks" / "tasks.json"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def tree(path: Path) -> ast.Module:
    return ast.parse(read(path), filename=str(path))


def function(tree_node: ast.AST, name: str) -> ast.FunctionDef | ast.AsyncFunctionDef:
    for node in ast.walk(tree_node):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    raise AssertionError(f"function {name!r} not found")


def calls(tree_node: ast.AST, name: str) -> list[ast.Call]:
    return [
        node
        for node in ast.walk(tree_node)
        if isinstance(node, ast.Call)
        and (
            isinstance(node.func, ast.Name) and node.func.id == name
            or isinstance(node.func, ast.Attribute) and node.func.attr == name
        )
    ]


def route_calls(tree_node: ast.AST) -> list[ast.Call]:
    routes: list[ast.Call] = []
    for node in ast.walk(tree_node):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if (
            isinstance(node.func.value, ast.Name)
            and node.func.value.id == "app"
            and node.func.attr in {"get", "post", "put", "patch", "delete", "head", "options", "trace"}
        ):
            routes.append(node)
    return routes


def route_path(route: ast.Call) -> str:
    if not route.args or not isinstance(route.args[0], ast.Constant):
        raise AssertionError("route has no literal path")
    return str(route.args[0].value)


def assignment(tree_node: ast.AST, name: str) -> ast.Assign | ast.AnnAssign:
    for node in ast.walk(tree_node):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets: Iterable[ast.expr]
            if isinstance(node, ast.Assign):
                targets = node.targets
            else:
                targets = (node.target,)
            if any(isinstance(target, ast.Name) and target.id == name for target in targets):
                return node
    raise AssertionError(f"assignment {name!r} not found")


def literal(value: ast.expr | None) -> object:
    return ast.literal_eval(value)  # type: ignore[arg-type]


def pyproject() -> dict[str, object]:
    with PYPROJECT_PATH.open("rb") as handle:
        return tomllib.load(handle)


def task_packet() -> dict[str, object]:
    return json.loads(read(TASKS_PATH))


def backend_boot_task() -> dict[str, object]:
    for task in task_packet()["tasks"]:  # type: ignore[index]
        if task["id"] == "BACKEND-BOOT-001":  # type: ignore[index]
            return task
    raise AssertionError("BACKEND-BOOT-001 task not found")


def compile_sources_without_writes(paths: Iterable[Path]) -> subprocess.CompletedProcess[str]:
    """Compile source text in a child interpreter without creating pyc files."""

    script = (
        "import pathlib, sys\n"
        "for raw in sys.argv[1:]:\n"
        "    path = pathlib.Path(raw)\n"
        "    compile(path.read_text(encoding='utf-8'), str(path), 'exec')\n"
        "print('compiled', len(sys.argv) - 1, 'files')\n"
    )
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, "-c", script, *(str(path) for path in paths)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
