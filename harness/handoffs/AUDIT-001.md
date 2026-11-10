# Handoff — AUDIT-001

## Status

READY_FOR_INTEGRATION — provider-neutral application telemetry foundation and
focused identity/API instrumentation are implemented and locally verified.

## Contract version(s) used

- `docs/contracts/events-and-audit.md` v1.0
- `docs/contracts/v1-baseline.md` v1.0
- `docs/architecture/blocks/15-observability-audit.md`
- `docs/security/data-protection.md`

## Delivered

- Bounded `X-Request-ID` correlation with server generation when absent or
  malformed.
- W3C `traceparent` validation, trace ID extraction and child-span helper.
- Immutable structured `AuditEvent` records and an injected `AuditSink`
  protocol for a later database/WORM adapter.
- Thread-safe append-only in-memory sink with explicit unavailable behavior.
- Allowlist redaction for bounded operational metadata. Unknown fields and
  credentials, tokens, raw prompts, answers, document text, queries and
  conversation bodies are excluded.
- Identity API events for sign-in success/denial/failure, identity lookup and
  sign-out, carrying request/trace correlation and server-derived principal
  identifiers only.
- Audit sink failure returns `AUTH_UNAVAILABLE`; a newly-created sign-in
  session is revoked before that failure is returned.

## Changed files

- `backend/app/observability/__init__.py`
- `backend/app/observability/audit.py`
- `backend/app/observability/context.py`
- `backend/app/api/identity.py`
- `backend/tests/test_observability.py`
- `tests/integration/test_audit_identity.py`
- `harness/handoffs/AUDIT-001.md`

No task files, infrastructure, frontend, authorization, contract, `.env`,
database migration or cloud/provider files were changed by AUDIT-001.

## Validation evidence

Executed from the repository root using the temporary environment
`/private/tmp/audit001-qUiVFX` with `backend[dev]` installed:

    /private/tmp/audit001-qUiVFX/bin/python -m pytest \
      backend/tests/test_observability.py \
      tests/integration/test_audit_identity.py -q
    PASS — 7 passed

    /private/tmp/audit001-qUiVFX/bin/python -m pytest backend/tests -q
    PASS — 17 passed, 1 skipped
    SKIP — DB migration smoke test requires DB001_DATABASE_URL

    /private/tmp/audit001-qUiVFX/bin/python -m compileall -q backend tests/integration
    PASS

Focused coverage includes correlated success, denial, unavailable sink,
append-only event behavior, trace context, and sensitive-field redaction.
The system Python initially lacked `pytest` and the declared backend runtime
packages; no repository dependency files were changed.

## Security implications

- Audit is metadata-only at this boundary; credentials and raw content are
  not passed to the sink.
- Authentication does not succeed to the caller when its success event cannot
  be appended.
- Correlation IDs are bounded and never used as authorization claims.
- The in-memory sink is not a security or authorization authority.

## Residual risks and integration steps

- The sink is process-local memory, not durable, immutable/WORM storage; a
  database adapter must provide persistence, retention, protected access and
  multi-process ordering before production use.
- Instrumentation is limited to the existing identity API because `main.py`
  was outside AUDIT-001's allowed write scope. A later API integration should
  add request middleware so generated correlation IDs also reach all routes
  and global error responses, then connect the approved telemetry backend.
- No OpenTelemetry collector/exporter, metrics backend, alerting, or cloud
  resource is provisioned here; those remain infrastructure work.
- The existing identity store remains synthetic in-memory state; durable
  identity and audit integration are still required.
- The PostgreSQL migration smoke test was not run because
  `DB001_DATABASE_URL` was not set.

Main Agent should review the event shape, replace the in-memory sink with the
durable adapter, and perform the broader integration/operational test gate.

No commit or push was performed by this task.
