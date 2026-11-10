# EVAL-PREP-001 — QA Handoff

**Status:** READY_FOR_MAIN_REVIEW
**Owner:** qa_tester
**Scope:** synthetic evaluation fixtures and pre-runtime metric self-checks only
**Date:** 2026-11-10

## Delivered

- `tests/evaluation/golden_dataset.jsonl`
  - 200 synthetic JSONL records; no real PII or proprietary documents.
  - 140 Vietnamese / 60 English.
  - 140 simple / 60 complex.
  - 50 permission-negative records, including explicit-deny and cross-tenant cases.
  - 30 unanswerable records.
  - PDF, DOCX and XLSX provenance; version conflicts; OCR; long tables; multi-hop evidence; indirect-injection labels.
- `tests/evaluation/_evaluation_harness.py`
  - JSONL/schema and dataset-composition validation.
  - Deterministic Recall@k, nDCG@k, MRR, citation accuracy, answer correctness, no-answer accuracy and unauthorized-retrieval-rate helpers.
- `tests/evaluation/README.md`
  - Evaluation protocol and metric definitions.
  - Explicitly leaves thresholds, provider/model and release decisions pending Project Owner.
- Four distinct test families, 10 materially different cases each:
  - `test_behavior_component.py`
  - `test_contract_integration.py`
  - `test_security_adversarial.py`
  - `test_e2e_operational.py`

## Evidence

Exact evaluation validation command:

```sh
python3 -m unittest discover -s tests/evaluation -p 'test_*.py'
```

Result: **PASS — 40 tests, OK, exit 0**.

Harness validation:

```sh
python3 scripts/validate_harness.py
```

Result: **PASS — 17 blocks, 8 agents, 32 tasks; no dependency cycles**. This is scaffolding validation only.

## Acceptance interpretation

- Golden fixtures cover authorized, denied and unanswerable outcomes.
- File-type locators and tenant/version bindings are validated.
- Metric calculations have deterministic synthetic self-checks.
- No quality threshold is approved. Proposed Recall/citation/answer/no-answer/latency/cost gates remain Project Owner decisions after benchmark evidence.
- Full runtime answer evaluation is deferred to `EVAL-001` after retrieval, evidence, guardrails and answer baseline tasks exist.

## Residual risks

- The harness is stdlib-only and validates fixture shape/metric arithmetic; it does not prove backend authorization or live retrieval behavior.
- Thresholds are intentionally pending Project Owner approval.
- Runtime model, provider, latency and cost measurements are not available in this phase.

No commit or push was performed by this QA task.
