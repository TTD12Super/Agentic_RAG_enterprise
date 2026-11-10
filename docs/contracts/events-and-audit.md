# Audit & event contract (proposal)

Example event:
```json
{"event":"DOCUMENT_READ_DECISION","trace_id":"trace-1","principal_id":"u-123","tenant_id":"tenant-a","resource_id":"doc-42","action":"document:read","decision":"DENY","policy_version":"policy-v7","occurred_at":"2026-11-08T10:00:00Z"}
```
Events should be structured with severity, timestamp, target, outcome, code version and correlation ID. Do not record full prompts, complete documents, tokens, passwords or raw user PII by default. Define retention and protected access. Loss of audit sink must be handled according to documented policy rather than silently disabling enforcement.

## Owner-provided audit baseline

- Audit is append-only, preferably immutable/WORM, and covers login, upload, approval, permission change, download, export, denied access and deletion.
- Website Manager sees business login/document/approval/permission events in scope; System Admin sees security/operational metadata but not conversation bodies by default.
- Raw prompts, outputs and conversation bodies are not logged by default. Investigation access is time-limited, approved and itself audited.
- Retention targets are two years for audit and 30 days for ordinary application logs.
- P0/P1 incidents alert the security/technical on-call immediately; P2/P3 follow dashboard and working-hours notification policy.
