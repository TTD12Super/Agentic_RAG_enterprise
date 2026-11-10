# GUARD-001 handoff

## Status

`ACCEPTED — MAIN AGENT REVIEW COMPLETE`

## Delivered

- `backend/app/guardrails/guardrails.py` provides the provider-neutral guard boundary.
- `backend/app/guardrails/__init__.py` exports the boundary.
- `tests/security/test_guardrails.py` adds 8 focused regression tests.

The boundary normalizes Unicode/control characters, rejects oversized input rather than truncating it, detects direct and indirect injection patterns, redacts high-confidence secrets and PII, allowlists only the three read-only MVP tools, and validates citation-backed output. Every allowed tool decision has `authorization_granted=False` and `requires_authorization=True`.

## Exact validation evidence

- `/usr/bin/python3 -m unittest tests/security/test_guardrails.py` — PASS, 8 tests.
- `/usr/bin/python3 -m py_compile backend/app/guardrails/guardrails.py backend/app/guardrails/__init__.py tests/security/test_guardrails.py` — PASS.
- `/usr/bin/git diff --check` — PASS.
- `/tmp/know-venv/bin/python -m pytest tests/security/test_guardrails.py -q` — PASS, 8 passed.
- `/tmp/know-venv/bin/python -m pytest tests/qa/guardrails -q` — PASS, 40 passed.
- `/tmp/know-venv/bin/python -m pytest backend/tests tests/integration tests/evaluation tests/security tests/qa/guardrails -q` — PASS, 315 passed, 2 skipped.

## Integration and approval boundaries

- Backend authentication/authorization, retrieval ACL checks, provider egress policy, citation ACL rechecks, and audit policy remain authoritative and were not changed.
- The tool guardrail only checks the allowlist and action shape. It does not resolve a principal, scope, tenant, document permission, or approval.
- Callers must pass citations already authorized for the current principal and document/version state; the output checker does not grant citation access.
- Only `search_documents`, `read_authorized_chunk`, and `get_document_metadata` are allowlisted. Side-effecting tools remain denied.
- No API keys, cloud calls, model-provider code, contracts, identity,
  authorization, RAG, frontend, or infrastructure files were changed.

## Known limitations and false-positive boundary

- Injection detection is a high-confidence phrase heuristic, not a proof of safety. Security questions framed as attack-defense education are allowed only when no injection pattern is matched; authorization and tool policy must still stop any bypass.
- Output grounding is a conservative lexical overlap gate, not semantic entailment. It blocks missing/unrelated evidence and unsupported sensitive terms but cannot prove that every sentence is true.
- Redaction targets obvious/high-confidence email, phone, SSN, payment-card, JWT, private-key, and common token/secret formats. It is not a complete DLP engine.
- The 4x10 adversarial matrix passed in `GUARD-QA-001.md`.

## Required reviewer approval

Main Agent accepted the default size limits, injection pattern set, redaction
coverage, lexical grounding trade-off, and the explicit requirement that
backend authorization remains in the integration path.
