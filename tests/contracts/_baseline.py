"""Small stdlib-only helpers for checking the normative v1 markdown baseline."""

from __future__ import annotations

import json
import re
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
BASELINE_PATH = REPOSITORY_ROOT / "docs" / "contracts" / "v1-baseline.md"
BASELINE = BASELINE_PATH.read_text(encoding="utf-8")


def section(number: int) -> str:
    """Return one numbered top-level section from the baseline."""

    match = re.search(
        rf"^## {number}\. .*?(?=^## \d+\. |\Z)",
        BASELINE,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not match:
        raise AssertionError(f"missing baseline section {number}")
    return match.group(0)


def json_blocks(text: str) -> list[dict[str, object]]:
    """Parse valid JSON objects from fenced JSON examples."""

    objects: list[dict[str, object]] = []
    for raw in re.findall(r"```json\s*\n(.*?)\n```", text, flags=re.DOTALL):
        value = json.loads(raw)
        if isinstance(value, dict):
            objects.append(value)
    return objects


def require_all(test_case, text: str, *needles: str) -> None:
    for needle in needles:
        test_case.assertIn(needle, text, msg=f"baseline is missing: {needle}")
