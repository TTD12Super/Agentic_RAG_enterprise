# ING-QA-001 — Independent ingestion QA handoff

## Status

`PASS — initial finding resolved; 40/40 QA cases passed`

This handoff is independent QA evidence for the current, uncommitted ING-001
implementation. QA did not modify application code, migrations, contracts,
task registry or shared helpers, and did not commit or push.

## Graphify-first evidence

The mandatory first repository operation was this Graphify query, before any
grep, search or source-file read:

```text
/tmp/graphify-venv/bin/graphify query "ING-001 ingestion lifecycle quarantine scanning approval version publication index staging retry maintenance cleanup tenant ACL revocation retention error boundary" --graph graphify-out/graph.json
```

It reported `graphify-out/graph.json` with 1,646 nodes, BFS depth 2 and 381
scoped nodes. The displayed scope located the ingestion lifecycle boundary,
document/version metadata, model policy, derived-index failure types, existing
ingestion contract tests, retry/publication tests and maintenance tests. The
CLI truncated the display to 49 nodes because the default output budget was
smaller than the 381-node result.

## QA scope

Exactly 40 deterministic synthetic cases were added and executed:

| File | Cases | Result |
| --- | ---: | --- |
| `test_behavior_component.py` | 10 | 10 passed |
| `test_contract_integration.py` | 10 | 10 passed |
| `test_e2e_operational.py` | 10 | 10 passed |
| `test_security_adversarial.py` | 10 | Initial: 9 passed, 1 failed; revalidation: 10 passed |

Coverage includes quarantine/scanning/review gates, publication and index ACK,
retry/checksum/attempt identity, maintenance/watchdog/cleanup, tenant and
ACL isolation, revocation, soft/permanent deletion, audit redaction and
derived-index error boundaries.

## Boundary review

- Task registry: `ING-001` is Phase 2, now `DONE`, and depends on
  `AUTH-001`, `KNOW-001`, `MODEL-001` and `AUDIT-001`.
- `KNOW-001`: QA exercised the `ChunkMetadata` and `inherit_acl` boundary;
  no schema or migration was changed.
- `MODEL-001`: QA confirmed ING-001 remains provider-neutral and does not
  select a provider, read credentials or add model calls.
- Ingestion/document/security contracts: QA covered the private upload,
  two-review, publication ACK, retention/legal-hold, tenant/ACL and
  fail-closed retrieval requirements that are executable in the local test
  double.

## Exact validation commands

All commands were run from the repository root:

```text
PYTHONPATH=tests/qa/ingestion /tmp/know-venv/bin/python -m pytest tests/qa/ingestion -q
1 failed, 39 passed in 0.15s

/tmp/know-venv/bin/python -m pytest backend/tests/test_ingestion_behavior.py backend/tests/test_ingestion_contract.py backend/tests/test_ingestion_security.py backend/tests/test_ingestion_operational.py tests/integration/test_ingestion_lifecycle.py -q
51 passed in 0.13s

/tmp/know-venv/bin/python -m pytest backend/tests tests/integration -k ingestion -q
51 passed, 111 deselected in 0.30s

/tmp/know-venv/bin/python -m pytest backend/tests tests/integration -q
160 passed, 2 skipped in 0.55s

/tmp/know-venv/bin/python -m compileall -q backend/app/ingestion backend/tests/test_ingestion_*.py tests/integration/test_ingestion_lifecycle.py tests/qa/ingestion
PASS

python3 scripts/validate_harness.py
HARNESS VALID: 17 blocks, 8 agents, 41 tasks; no dependency cycles

git diff --check
PASS
```

The two skipped full-suite checks require the unavailable `DB001_DATABASE_URL`:

- `backend/tests/test_db_migrations.py`
- `backend/tests/test_knowledge_database.py`

## Finding

### ING-QA-001-F01 — Raw derived-index cleanup exception crosses lifecycle boundary

**Severity:** High — security/error-boundary blocker for acceptance.

**Evidence:**

- QA: `tests/qa/ingestion/test_security_adversarial.py::test_cleanup_backend_error_is_wrapped_without_secret_leakage`
- Call path: `IngestionService.revoke_version()` → `_safe_remove()` → `DerivedIndex.remove()`
- Location: `backend/app/ingestion/lifecycle.py:1053`

`_safe_remove()` catches `IngestionError` only. A generic derived-index adapter
failure propagates as raw `RuntimeError` with backend details. The synthetic
adapter raised `synthetic-secret-index-error`; the observed exception was the
same raw `RuntimeError`, so the case failed.

**Impact:** A Qdrant/search cleanup failure can cross the ingestion boundary
with internal backend details. The authority state is revoked before cleanup,
but callers receive an unsafe exception instead of a typed safe failure or a
recorded cleanup-pending result.

**Required follow-up:** Backend/ING owner should catch unexpected cleanup
exceptions at the derived-index boundary, map them to a safe typed
`DerivedIndexFailure` (or the documented cleanup-pending path), preserve
fail-closed retrieval, and add a regression test. QA does not apply this fix.

## Acceptance decision

Initial QA did not accept `ING-001` until F01 was fixed. The lifecycle boundary
now maps unexpected cleanup exceptions to `DerivedIndexFailure`, records cleanup
pending and preserves fail-closed retrieval. Revalidation passed all 40 cases.

## Remaining environment boundary

The implementation remains an in-memory/provider-neutral test double. Live
PostgreSQL, object storage, parser/OCR, Qdrant and cloud/provider runtime
validation remain blocked by the handoff scope and missing approved runtime
configuration.

## Revalidation

- `pytest tests/qa/ingestion -q`: 40 passed.
- ING implementation and integration tests: 51 passed.
- Full backend/integration suite: 160 passed, 2 skipped because `DB001_DATABASE_URL` was not configured.
- Compile, harness validation and `git diff --check`: PASS.
