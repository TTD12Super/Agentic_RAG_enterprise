from pathlib import Path

from tests.evaluation.eval_001_runner import evaluate, render_report


if __name__ == "__main__":
    output = Path(__file__).resolve().parents[2] / "docs/testing/eval-001-report.md"
    output.write_text(render_report(evaluate()), encoding="utf-8")
    print(f"wrote {output}")
