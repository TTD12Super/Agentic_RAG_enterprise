# ANSWER-BASE-QA-001 — Direct answer baseline QA

## Status

`QA COMPLETE — 48 TESTS PASS`

## Scope

Independent QA coverage was added without changing production code:

- `tests/qa/answer_baseline/test_behavior_component.py` — 12 tests
- `tests/qa/answer_baseline/test_contract_integration.py` — 13 tests
- `tests/qa/answer_baseline/test_security_adversarial.py` — 12 tests
- `tests/qa/answer_baseline/test_e2e_operational.py` — 11 tests

The tests use deterministic synthetic documents, the existing local hybrid
retrieval fixtures, fake answer gateways, and controlled failure seams. No API
key, external provider, real database, or proprietary document is used.

## Coverage

- `ANSWERED`, `PARTIAL`, `INSUFFICIENT_EVIDENCE`, `ACCESS_DENIED`, and `ERROR`
- Citation document/version/page/source-span/chunk metadata and SHA-256 snapshot hash
- Tenant, document, version, current-version, `ACTIVE` status, and revocation checks
- Direct and indirect prompt injection, secret and PII redaction, and output injection
- Cross-tenant, ACL-denied, superseded, revoked, staging, and stale-policy retrieval
- Retrieval, embedding, reranker, model, model-egress, and verifier failures
- Malformed model values, duplicate/unknown citation IDs, conflicting evidence
- Fail-closed empty answer/citations and denied-content non-disclosure
- Secure context markers, `INTERNAL` model classification, repeatability, and input bounds

## Validation evidence

Interpreter used: `/tmp/know-venv/bin/python`.

```text
/tmp/know-venv/bin/python -m pytest tests/qa/answer_baseline/test_behavior_component.py -q --import-mode=importlib
12 passed in 0.21s

/tmp/know-venv/bin/python -m pytest tests/qa/answer_baseline/test_contract_integration.py -q --import-mode=importlib
13 passed in 0.19s

/tmp/know-venv/bin/python -m pytest tests/qa/answer_baseline/test_security_adversarial.py -q --import-mode=importlib
12 passed in 0.19s

/tmp/know-venv/bin/python -m pytest tests/qa/answer_baseline/test_e2e_operational.py -q --import-mode=importlib
11 passed in 0.21s

/tmp/know-venv/bin/python -m pytest tests/qa/answer_baseline -q --import-mode=importlib
48 passed in 0.19s

git diff --check
PASS
```

An initial attempt with `python -m pytest ...` was not executed because this
shell has no `python` command (`zsh: command not found: python`). All reported
test results above use the repository's available test interpreter.

## Findings

No production defect was exposed by the final QA suite. Early failures were
test-fixture mistakes only (a tenant value used before setup, a deliberately
stale policy epoch, an output assertion that included redacted secret text,
and a conflict fixture using number words outside the verifier's numeric
heuristic); they were corrected without weakening assertions.

## Scope and risk

- Production files were not edited.
- No commit or push was performed.
- `graphify update .` was not run because it writes generated files under
  `graphify-out/`, outside the requested QA write scope.
- The suite validates the direct baseline with deterministic in-process seams;
  real provider latency, network egress, PostgreSQL/Qdrant availability, and
  citation preview/download HTTP endpoints remain outside this task.
