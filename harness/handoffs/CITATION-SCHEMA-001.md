# CITATION-SCHEMA-001 — Provider-neutral citation schema

## Outcome

`DONE — MAIN AGENT ACCEPTED`

Citation output is now provider-neutral and fail-closed end-to-end:

- `tenant_id` and request-bound `policy_epoch` propagate through dense/hybrid retrieval into `AnswerCitation`.
- `audience` and timezone-aware `expires_at` are present in the answer citation contract; default answer references are bounded to a five-minute pipeline lifetime and explicit expired references fail closed.
- Typed immutable locators cover PDF (`page` + `source_span`), DOCX (`heading` + `paragraph`) and XLSX (`sheet` + validated A1 `cell_range`).
- Existing `document_id`, `version_id`, `chunk_id` and SHA-256 `evidence_snapshot_hash` remain present.
- Legacy PDF `page` and `source_span` properties/serialized fields remain available alongside the typed `locator`.
- Tenant mismatch, policy-epoch mismatch, malformed/missing locators, stale versions and revoked citations are omitted before model context or answer delivery.
- Citation objects and locator models are immutable and support deterministic `to_dict()` / `to_json()` serialization.

## Changed files

- `backend/app/knowledge/models.py`
- `backend/app/rag/dense.py`
- `backend/app/rag/hybrid.py`
- `backend/app/rag/answer.py`
- `backend/app/knowledge/__init__.py`
- `backend/app/rag/__init__.py`
- `docs/contracts/answer-and-citation.md`
- `docs/contracts/v1-baseline.md`
- `backend/tests/test_answer_citations.py`
- `tests/integration/test_answer_citation_schema.py`
- `backend/tests/test_hybrid_retrieval.py`
- `harness/handoffs/CITATION-SCHEMA-001.md`

No authorization, orchestration, frontend, infrastructure or task-registry files were changed. No dependency, provider API key, commit or push was added.

## Verification

Required graph orientation command:

```text
GRAPHIFY_BIN=/tmp/graphify-venv/bin/graphify
$GRAPHIFY_BIN query --graph graphify-out/graph.json --query "AnswerCitation tenant policy_epoch PDF DOCX XLSX source locator citation reauthorization" --limit 20
```

Result: exit 0; graph reported 2,737 nodes, traversed 77 nodes and displayed 58 due to the output budget.

Focused citation/schema tests:

```text
/tmp/know-venv/bin/python -m pytest backend/tests/test_answer_citations.py tests/integration/test_answer_citation_schema.py -q
```

Result: `30 passed` in the combined focused citation/parent/runtime suite.

Focused regression tests:

```text
/tmp/know-venv/bin/python -m pytest backend/tests/test_answer_citations.py tests/integration/test_answer_citation_schema.py backend/tests/test_dense_retrieval.py backend/tests/test_hybrid_retrieval.py backend/tests/test_knowledge_contract.py -q
```

Result: included in the combined focused suite above; no failure.

Full backend/integration/evaluation regression:

```text
/tmp/know-venv/bin/python -m pytest backend/tests tests/integration tests/evaluation -q
```

Result: `490 passed, 2 skipped` with the project QA suites included.

Skipped tests require `DB001_DATABASE_URL` for the disposable PostgreSQL service.

Additional checks:

```text
/tmp/graphify-venv/bin/python -m compileall -q backend/app/knowledge backend/app/rag backend/tests/test_answer_citations.py tests/integration/test_answer_citation_schema.py
git diff --check
```

Both passed with no output.

## Limits

- The existing evidence verifier still accepts its required internal normalized span; DOCX/XLSX typed locators are the authoritative user-visible citation location.
- Live PostgreSQL, Qdrant, object storage and provider-backed answer generation were not exercised; existing DB tests remain skipped without `DB001_DATABASE_URL`.
- Production provider, PostgreSQL, Qdrant and object-storage adapters were not exercised; the deterministic local baseline is the accepted scope for this blocker.
