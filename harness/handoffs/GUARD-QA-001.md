# GUARD-QA-001 handoff

## Outcome

PASS — the requested GUARD-001 QA suite contains exactly 40 independent tests:
10 behavior/component, 10 contract/integration, 10 E2E/operational, and 10
security/adversarial. All 40 pass. No production defect was found in the
tested guardrail scope.

No production code, task registry, contracts, frontend, infrastructure, or
existing tests were changed. The new tests use deterministic local functions
and synthetic values only; they make no network calls and require no API keys.

## Changed files

- `tests/qa/guardrails/test_behavior_component.py`
- `tests/qa/guardrails/test_contract_integration.py`
- `tests/qa/guardrails/test_e2e_operational.py`
- `tests/qa/guardrails/test_security_adversarial.py`
- `harness/handoffs/GUARD-QA-001.md`

The worktree already contained unrelated untracked guardrail implementation
and security-test files; they were left unchanged.

## Coverage

- Unicode normalization, control-character handling, input/context/output
  limits, and deterministic results.
- Direct and indirect prompt injection in English and Vietnamese, including
  educational false-positive boundaries.
- Secret, PII, payment, private-key, and JWT redaction without raw sensitive
  values in results.
- Exact MVP tool allowlist, unsafe tools, forged tenant/role/scope arguments,
  and the non-authoritative authorization boundary.
- Citation authorization, lexical grounding, unsupported sensitive claims, and
  safe abstention.
- GUARD-001 task metadata and the three listed security contracts.

## Commands and results

Required Graphify orientation:

```text
/tmp/graphify-venv/bin/graphify query --graph graphify-out/graph.json --query "backend guardrails prompt injection unsafe tool output leakage authorization" --limit 20
```

PASS — exit 0. Graphify reported 2,366 nodes, found 75 nodes, and displayed
60 before truncation.

Focused QA suite:

```text
/tmp/know-venv/bin/python -m pytest tests/qa/guardrails -q
```

PASS — `40 passed in 0.03s`.

Existing guardrail regression tests plus the new suite:

```text
/tmp/know-venv/bin/python -m pytest tests/qa/guardrails tests/security/test_guardrails.py -q
```

PASS — `48 passed in 0.03s`.

Full backend/integration/evaluation run:

```text
/tmp/know-venv/bin/python -m pytest backend/tests tests/integration tests/evaluation -q
```

PASS — `255 passed, 2 skipped in 2.06s`. The skips require the disposable
PostgreSQL service via `DB001_DATABASE_URL` in
`backend/tests/test_db_migrations.py` and
`backend/tests/test_knowledge_database.py`.

All scoped QA plus backend/integration/evaluation:

```text
/tmp/know-venv/bin/python -m pytest tests/qa/guardrails backend/tests tests/integration tests/evaluation -q
```

PASS — `295 passed, 2 skipped in 2.08s`, with the same two disposable
PostgreSQL skips.

Compile check:

```text
/tmp/graphify-venv/bin/python -m compileall -q backend/app/guardrails tests/qa/guardrails
```

PASS — exit 0.

Whitespace/diff check:

```text
git diff --check
```

PASS — exit 0. The four new test files also have no trailing whitespace.

Test-count check:

```text
for f in tests/qa/guardrails/test_*.py; do printf '%s: ' "$f"; rg -c '^    def test_' "$f"; done
```

PASS — each file reports `10`; total `40`.

## Security findings and limits

- PASS — direct and indirect injection is denied at the appropriate input or
  untrusted-content boundary.
- PASS — allowed tools remain `requires_authorization=True` with
  `authorization_granted=False`; backend authorization remains authoritative.
- PASS — unauthorized citations, unsupported sensitive claims, oversized
  outputs, and unsafe tools fail closed.
- PASS — raw synthetic secret/PII values do not survive returned guardrail
  values or representations.
- Live external providers, PostgreSQL-backed policy, Qdrant, and production
  tool execution were not exercised; those require separate integration
  environments.
- `graphify update .` was not run because the user restricted writes to the
  four QA files and this handoff; no graph artifact was changed.

## Approval boundary

QA is ready for Tech Lead review. No commit or push was performed.
