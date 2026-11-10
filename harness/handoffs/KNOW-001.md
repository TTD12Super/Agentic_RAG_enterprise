# Handoff — KNOW-001 / Ingestion-Knowledge

- Task ID: KNOW-001
- Agent owner: Ingestion/Knowledge
- Status: ACCEPTED — MAIN AGENT REVIEW
- Contract version(s) used: document & chunk schema v1.0; ingestion API & job contract v1.0; secure retrieval v1.0; identity & policy v1.0
- Upstream dependencies checked: CONTRACT-001, INFRA-001, DB-001

## Graphify-first evidence

Mandatory query executed from the repository root before source inspection:

```text
/tmp/graphify-venv/bin/graphify query "KNOW-001 metadata parent child chunk schema immutable document version tenant ACL inheritance SQLAlchemy knowledge tests" --graph graphify-out/graph.json
```

Findings: the graph located `backend/app/db/migrations/versions/0001_identity_tenants.py`, `backend/app/db/migrations/versions/0002_documents.py`, the existing document-version uniqueness test, tenant/ACL authorization tests, and `backend/app/authorization/policy.py`. A narrowed follow-up query located the existing `documents`, `document_versions`, `document_heads`, `chunks` migration boundary and the relevant tenant/ACL symbols. The existing DB-001 schema already provides the required tenant/version composite keys and parent foreign key, so no migration was added.

## Delivered

- Immutable Pydantic metadata models for documents, document versions, source spans and chunks.
- Stable document-version identity tuple: tenant, document, version UUID and version number.
- Parent-child validation requiring the same tenant, document and version.
- ACL inheritance helper that rejects child ACL broadening and copies the parent policy reference.
- Derived Qdrant payload projection containing tenant/version/chunk provenance and no source text or authorization authority.
- Four knowledge test families with 10 cases each: behavior, contract, security and database.
- Opt-in PostgreSQL probe for the already-approved DB-001 schema.

## Changed files

Application and tests added by this task:

- `backend/app/knowledge/__init__.py`
- `backend/app/knowledge/models.py`
- `backend/tests/test_knowledge_behavior.py`
- `backend/tests/test_knowledge_contract.py`
- `backend/tests/test_knowledge_security.py`
- `backend/tests/test_knowledge_database.py`
- `harness/handoffs/KNOW-001.md`

Required Graphify refresh also regenerated these derived local graph artifacts:

- `graphify-out/GRAPH_REPORT.md`
- `graphify-out/graph.html`
- `graphify-out/graph.json`
- `graphify-out/manifest.json`

No migration, contract, authorization, RAG, frontend, infrastructure, or task-registry file was edited.

## Validation evidence

Executed from repository root:

```text
/tmp/know-venv/bin/python -m pytest backend/tests -k knowledge -q
39 passed, 1 skipped, 18 deselected

/tmp/know-venv/bin/python -m pytest backend/tests -q
56 passed, 2 skipped

python3 scripts/validate_harness.py
HARNESS VALID: 17 blocks, 8 agents, 41 tasks; no dependency cycles

git diff --check
PASS

/tmp/know-venv/bin/python -m compileall -q backend/app/knowledge backend/tests
PASS

/tmp/graphify-venv/bin/graphify update .
Rebuilt: 1465 nodes, 2735 edges, 85 communities
```

The one skipped KNOW-001 test is the live PostgreSQL probe because `DB001_DATABASE_URL` was not configured. The static migration-contract checks ran successfully.

## Security and integration notes

- PostgreSQL remains authoritative for lifecycle, tenant isolation and policy inputs.
- Qdrant metadata is a derived projection and cannot grant access.
- Active chunks require an inherited ACL reference before projection.
- Original content is not included in the Qdrant payload.
- No real company data, API key, cloud resource or production database was used.

## Unresolved decisions / limits

- Live PostgreSQL integration evidence remains pending a disposable `DB001_DATABASE_URL`.
- Runtime repository wiring and lifecycle writes belong to downstream Backend/Ingestion tasks; this task intentionally does not create a migration or repository.
- The model validates ACL-reference inheritance only; authorization evaluation remains owned by the existing PDP/PEP.

## Integration boundary

Main Agent review accepted the task after the independent QA revalidation. No commit or push was performed by this task.

## Main Agent revalidation

- Fixed INTERNAL owner-department, ACTIVE current-version and publication-status invariants found by independent QA.
- Independent QA rerun: 40/40 passed.
- Backend rerun: 96 passed, 2 skipped because `DB001_DATABASE_URL` was not configured.
- Main review: `harness/reviews/KNOW-001-main-review.md`.

## Pre-existing workspace changes

Model adapter files were completed by the parallel MODEL-001 task and are tracked separately in its handoff.
