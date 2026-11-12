# Administrative API boundary — v1.0

The normative envelope, authorization, idempotency, audit and privacy rules are defined in [`v1-baseline.md`](v1-baseline.md).

This document is the v1.0 approved boundary for implementation planning. It does not declare implemented endpoints or grant new privileges.

Backend owns the public `/api/v1` administration routes and orchestrates the existing identity, policy, document and ingestion services. Ingestion owns document-processing internals; Security reviews authorization. The initial document routes are proposed in `ingestion.md`. Before implementation, review and version the exact request/response schemas, pagination, error codes, asynchronous states and role-specific actions for:

- Document upload, validation status, two review decisions, publication, metadata, access grants, version history, soft deletion and permanent deletion subject to retention and legal hold.
- Administrator-provisioned account lifecycle, activation and role/department assignments; the Website Manager has website management but no code/system operations.
- `POST /api/v1/access-requests` records an employee access request without granting access. Authenticated requests use the server-derived principal tenant; anonymous requests use the deployment-only `BACKEND_ACCESS_REQUEST_TENANT_ID` setting, never a client-provided tenant. Managers use `GET /api/v1/access-requests` and `POST /api/v1/access-requests/{request_id}/review` for tenant-scoped, idempotent approve/reject decisions; approval remains pending provisioning and never sends email implicitly.
- Authorized audit and operational dashboard data without another user's conversation body, raw secrets or unrestricted source content.
- Feedback review and aggregate quality/usage dashboard data, with measurement time, estimates and unavailable values clearly distinguished. Exact data fields and feedback access policy require owner and security review.

Every route uses server-verified identity, current authorization and deny-by-default policy. Mutations require idempotency and audit events where applicable; download and preview enforce their separate permissions. No client role, document ID or LLM output grants access. The approved security matrix and explicit-deny precedence remain authoritative.

Backend, Frontend, Ingestion and Security review these schemas before implementation. Integration tests cover allowed and denied roles, Chairman and employee write denial, ACL revocation, two-review gates, account activation, privacy, malformed inputs and unavailable policy service.
