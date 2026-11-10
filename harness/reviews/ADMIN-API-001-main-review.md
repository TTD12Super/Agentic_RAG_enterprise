# ADMIN-API-001 — Main Agent review

## Decision

`ACCEPTED`

The provider-neutral administration boundary is accepted for Phase 2. The
implementation reuses the existing identity, PDP/PEP, ingestion and audit
boundaries; it does not claim durable PostgreSQL, object storage, queue,
parser/OCR, Qdrant or cloud integration.

## Evidence

- Focused admin API and integration tests: `40 passed`.
- Required QA matrix: `40 passed` (`10` behavior, `10` contract/integration,
  `10` E2E/operational, `10` security/adversarial).
- Full backend and integration suite: `200 passed, 2 skipped`.
- Compile, harness validation and `git diff --check`: passed.
- Two QA findings were fixed and revalidated: quarantine reads now fail closed
  before publication, and upload idempotency reuse uses
  `IDEMPOTENCY_KEY_REUSED` as required by the v1 contract.

## Accepted behaviors

- Website Manager/System Admin management actions are allowed through the
  existing PDP/PEP; Chairman, employee and anonymous management actions are
  denied without existence leakage.
- Upload, two-review publication, ACL updates, revocation, soft delete and
  retention/legal-hold protected permanent delete are wired to the ingestion
  authority.
- Account responses exclude passwords; no conversation-content endpoint was
  added.

## Deferred boundary

The two PostgreSQL probes remain skipped because `DB001_DATABASE_URL` is not
configured. Durable repositories and production upload/storage adapters must
preserve the tested tenant, policy epoch, idempotency, review and revocation
semantics before production release. `/accounts` is the preferred UI path;
`/users` remains a compatibility alias for now.
