from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
FRONTEND = ROOT / "frontend"


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def read_frontend(relative: str) -> str:
    return (FRONTEND / relative).read_text(encoding="utf-8")


def load_frontend_json(relative: str) -> dict:
    return json.loads(read_frontend(relative))


def run_frontend(args: list[str], timeout: int = 120) -> str:
    env = os.environ.copy()
    env["CI"] = "1"
    try:
        result = subprocess.run(
            args,
            cwd=FRONTEND,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except OSError as exc:
        raise AssertionError(f"could not execute {' '.join(args)}: {exc}") from exc
    output = f"{result.stdout}\n{result.stderr}"
    if result.returncode != 0:
        raise AssertionError(f"{' '.join(args)} exited {result.returncode}:\n{output}")
    return output
