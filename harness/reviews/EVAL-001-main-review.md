# EVAL-001 — Main Agent Review Draft

## Decision posture

**ACCEPTED FOR DEVELOPMENT; NOT PRODUCTION SIGN-OFF.** The deterministic QA evaluation is reproducible for V1–V3 and shows zero unauthorized retrieval in the synthetic negative suite. V4 is explicitly not run because the current backend has no parent-expansion runtime seam. The Project Owner has approved Recall@10 ≥90% and an answer-confidence floor of 80%; the remaining numeric release thresholds are deferred to the project-wide quality gate.

## Evidence reviewed

- `docs/testing/eval-001-report.md`
- `tests/evaluation/eval_001_runner.py`
- `tests/evaluation/test_eval_001_runtime.py`
- Existing EVAL-PREP four-family suites: 40 cases total, 10 per required family.
- Exact suite result: `72 passed`, exit 0.
- Relevant retrieval/evidence result: `16 passed`, exit 0.
- Harness validation: valid, no dependency cycles.

## Findings

1. **V4 is not evaluable in the current runtime.** Parent/child metadata and ACL inheritance exist, but no parent expansion API is callable by the direct evaluation runner. This is a scope/integration blocker, not a QA failure. Do not claim V4 metrics.
2. **Citation schema fidelity is incomplete for non-PDF sources.** The direct `AnswerCitation` shape does not carry tenant/policy epoch or DOCX heading/paragraph and XLSX sheet/cell-range locators. The runner preserves the Golden Dataset locators out-of-band only for measurement; it does not mask the production gap.
3. **Perfect V1–V3 quality metrics are synthetic upper-bound smoke results.** Each answered case is isolated to its authorized source set and uses a deterministic answer oracle. They validate arithmetic, wiring, direct outcome mapping and leakage behavior—not provider quality, discrimination under corpus noise, cost or capacity.

## Security conclusion

The exercised authorization paths passed: 50 permission-negative records, including 24 cross-tenant records, produced zero forbidden-source leakage for V1–V3. Denied content remained absent from retrieved evidence and citations. Existing backend/evidence suites cover revoked/stale source behavior. No backend/frontend/infra/data file was changed.

## Approval requests

The project-wide quality gate remains required before production release. Main Agent will schedule follow-up V4/citation-schema work as development proceeds; EVAL-001 is complete as technical evaluation evidence only.

No task registry change, commit or push was performed.
