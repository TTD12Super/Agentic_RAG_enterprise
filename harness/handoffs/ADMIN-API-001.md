# ADMIN-API-001 — Administration API handoff

## Status

`ACCEPTED — MAIN AGENT REVIEW COMPLETE`

This task is provider-neutral and uses deterministic in-memory identity,
policy, ingestion and audit doubles. It does not claim durable PostgreSQL,
object storage, queue, parser/OCR, Qdrant or cloud integration. No commit or
push was performed.

## Graphify-first evidence

The mandatory first repository command ran from the repository root before any
grep, search or source-file read:

```text
/tmp/graphify-venv/bin/graphify query "ADMIN-API-001 versioned document account administration API identity policy ingestion audit boundaries" --graph graphify-out/graph.json
```

The pre-change graph reported 1,878 nodes and located `AuthenticatedPrincipal`,
`AuthorizationEvaluator`, `PolicyEnforcementPoint`, `IngestionService`, the
identity API, document metadata, audit sink and existing permission-negative
tests. Those findings scoped the implementation to the existing boundaries;
no authorization implementation, migration or contract file was changed.

After implementation, Graphify was refreshed:

```text
/tmp/graphify-venv/bin/graphify update .
Rebuilt: 2,016 nodes, 4,972 edges, 114 communities
```

Follow-up query:

```text
/tmp/graphify-venv/bin/graphify query "ADMIN-API-001 administration routes identity PDP PEP IngestionService two-review ACL revocation audit idempotency" --graph graphify-out/graph.json --budget 6000
```

It located `AdminApiState`, `create_user`, `activate_user`,
`upload_document`, `approve_document_version`, `publish_document_version`,
`revoke_document_version`, `permanently_delete_document`, ACL updates,
`AuthenticatedPrincipal`, the PEP and the ingestion/audit boundaries.

## Changed files

- `backend/app/api/admin.py`
- `backend/app/api/identity.py`
- `backend/app/identity/__init__.py`
- `backend/app/identity/models.py`
- `backend/app/identity/store.py`
- `backend/tests/_admin_api_fixtures.py`
- `backend/tests/test_admin_api_behavior.py`
- `backend/tests/test_admin_api_contract.py`
- `backend/tests/test_admin_api_security.py`
- `tests/integration/test_admin_api.py`
- `harness/handoffs/ADMIN-API-001.md`

## Implemented boundary

- Admin routes are available under `/api/v1` while preserving the existing
  `/api/v1/auth/*` routes. Account aliases use `/users` and `/accounts`.
- Only Website Manager and System Admin pass the existing PDP/PEP management
  check. Chairman, employee and anonymous callers are denied without resource
  existence leakage; policy-store outage fails closed with `AUTH_UNAVAILABLE`.
- Account listing, provisioning, activation, role/department assignment and
  department administration are tenant-scoped. Passwords are never returned.
  Privileged account provisioning requires MFA enrollment; System Admin is the
  only role allowed to provision `system_admin`.
- Document upload creates only a quarantined asynchronous job. Supported
  PDF/DOCX/XLSX metadata, private source URI, checksum, MIME/signature, size,
  classification and INTERNAL department rules are delegated to
  `UploadManifest`/`IngestionService`.
- Version status, job status and version history are exposed as redacted
  metadata. Review-1 and review-2 are separate idempotent calls; publication
  remains blocked until the existing worker boundary has processed chunks,
  staged the derived index and acknowledged it.
- Document ACL updates accept ALLOW/DENY grants for read/download. The
  existing PDP retains explicit-deny precedence, and policy epoch is bumped on
  ACL, publication, revocation and deletion changes.
- Revoke, soft-delete and retention/legal-hold-protected permanent delete are
  separate operations. Revoke/delete remove retrieval eligibility through the
  existing ingestion authority; permanent deletion does not bypass retention.
- Mutating calls use idempotency admission. Upload and review use the existing
  ingestion idempotency boundary; publication returns the original safe result
  for the same key and rejects key reuse for a different version.
- Existing privacy-safe audit events are emitted through the established audit
  sink; no conversation or conversation-body route was added.

## Validation evidence

Executed from the repository root:

```text
/tmp/know-venv/bin/python -m pytest backend/tests/test_admin_api_behavior.py backend/tests/test_admin_api_contract.py backend/tests/test_admin_api_security.py tests/integration/test_admin_api.py -q
40 passed

/tmp/know-venv/bin/python -m pytest backend/tests tests/integration -q
200 passed, 2 skipped

/tmp/know-venv/bin/python -m compileall -q backend tests/integration
PASS

python3 scripts/validate_harness.py
HARNESS VALID: 17 blocks, 8 agents, 41 tasks; no dependency cycles

git diff --check
PASS
```

The two skipped tests are the pre-existing disposable PostgreSQL probes;
`DB001_DATABASE_URL` was not configured:

- `backend/tests/test_db_migrations.py`
- `backend/tests/test_knowledge_database.py`

The ADMIN test package has exactly four families with ten test functions each:

- behavior/component: 10
- contract/integration: 10
- security/adversarial: 10
- E2E/operational integration: 10

## Scope and integration limits

- The task deliberately does not add migrations, a PostgreSQL repository,
  object-storage upload streaming, parser/OCR execution, queue workers,
  Qdrant adapters, provider/API-key configuration or cloud deployment.
- The API accepts a validated upload manifest/source URI as the current
  provider-neutral boundary; a production multipart/object-storage adapter
  must preserve the same quarantine and idempotency gates.
- Processing/index staging is exercised through the accepted
  `IngestionService` test double; `CHAT-001` still owns conversation routes and
  maintenance pause/resume integration.
- Identity and department records remain in-memory until the durable identity
  repository is wired to DB-001 by the Backend owner.

## Main Agent review requests

1. Review the public route aliases and choose one canonical account path before
   frontend integration; `/accounts` is available for the current UI boundary,
   while `/users` remains a compatibility alias.
2. Run the skipped PostgreSQL checks with an approved disposable
   `DB001_DATABASE_URL` before marking the task integrated.
3. Confirm the production repository/object-storage adapter preserves the
   in-memory API's PEP, two-review, ACL epoch and revocation semantics.

## Main Agent acceptance

- Reviewed the implementation and QA handoff after the two QA findings were
  fixed: quarantined documents are not readable until they have a current
  published version; upload idempotency reuse returns the normative
  `IDEMPOTENCY_KEY_REUSED` code.
- Focused API and QA validation: 80 passed.
- Full backend/integration validation: 200 passed, 2 skipped because
  `DB001_DATABASE_URL` is not configured.
- Accepted as the provider-neutral Phase 2 API boundary. Durable PostgreSQL,
  object storage, parser/OCR, queue, Qdrant and cloud integration remain
  downstream work and are not silently claimed here.
