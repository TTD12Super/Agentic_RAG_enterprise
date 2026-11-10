# Handoff — KNOW-QA-001 / Independent QA for KNOW-001

- Task ID: KNOW-QA-001
- Target: KNOW-001
- Agent role: QA
- Status: PASS — initial findings resolved and revalidated; no application files changed by QA
- Scope: only `tests/qa/knowledge/*` and this handoff

## Graphify-first evidence

Executed before any repository search or source read:

```text
/tmp/graphify-venv/bin/graphify query "KNOW-001 knowledge models tenant version parent child ACL Qdrant projection database boundary" --graph graphify-out/graph.json
```

The query scoped review to `backend/app/knowledge/models.py`, the four existing KNOW-001 backend test modules, DB-001 migrations and the document/ingestion/retrieval/identity contracts.

## Coverage added

The QA package contains 40 materially different deterministic synthetic cases:

- `test_behavior_component.py`: 10 behavior/component cases.
- `test_contract_integration.py`: 10 document/chunk/Qdrant/database-boundary contract cases.
- `test_security_adversarial.py`: 10 tenant/parent/ACL/projection denial cases.
- `test_e2e_operational.py`: 10 registry/handoff/graph/validator/backend-test operational cases.

## Commands and results

Run from repository root:

```text
python3 -m unittest discover -s tests/qa/knowledge -p 'test_*.py' -v
BLOCKED — system Python has no pydantic dependency

/tmp/know-venv/bin/python -m unittest discover -s tests/qa/knowledge -p 'test_*.py' -v
Initial run: FAIL — 36 passed, 4 failed
Revalidation: PASS — 40 passed

/tmp/know-venv/bin/python -m pytest backend/tests -k knowledge -q
PASS — 39 passed, 1 skipped, 18 deselected

/tmp/know-venv/bin/python -m pytest backend/tests -q
PASS — 96 passed, 2 skipped

python3 scripts/validate_harness.py
PASS — HARNESS VALID

/tmp/know-venv/bin/python -m compileall -q backend/app/knowledge backend/tests tests/qa/knowledge
PASS — no compile errors

rg -c '^    def test_' tests/qa/knowledge/test_*.py
PASS — 10 cases in each of the four QA files
```

The live PostgreSQL probe remains `BLOCKED/NOT RUN` without the approved disposable `DB001_DATABASE_URL`; the existing static database-boundary checks pass.

## Findings

1. **FAIL — `DocumentMetadata` permits an invalid INTERNAL document without a department.** `FR-DOC-003` and the data-governance block require INTERNAL content to carry department information. `DocumentMetadata(classification="INTERNAL", owner_department_id=None, ...)` currently succeeds.

2. **FAIL — `DocumentMetadata` permits `ACTIVE` without `current_version_id`.** The model has no current-version invariant, although the document contract and retrieval/lifecycle requirements require retrieval to bind to the current approved ACTIVE version.

3. **FAIL — `DocumentVersionMetadata.status` cannot represent publication lifecycle states.** The document contract exposes version status `ACTIVE` and terminal states such as `REVOKED`/`SOFT_DELETED`, while the model accepts only processing states. The model also has no separate publication-status field, so it cannot represent the authoritative DB-001 split without an adapter.

The initial findings were fixed in `backend/app/knowledge/models.py` and the valid synthetic fixtures were aligned with the new invariants. Revalidation passed; this QA task did not modify application code, migrations or contracts.

## Registry and handoff status

`KNOW-001` remains a Main Agent/Tech Lead acceptance decision in the task registry. The three initial findings are resolved and no follow-up migration is required.

## Not checked

No live PostgreSQL, Qdrant, object storage, ingestion worker or end-to-end HTTP workflow was available/configured. No commit or push was performed.
