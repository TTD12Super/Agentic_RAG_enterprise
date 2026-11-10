# Identity & Policy contract (proposal)

## AuthenticatedPrincipal
```json
{"user_id":"u-123","tenant_id":"tenant-a","roles":["chairman"],"groups":["leadership"],"session_id":"s-1","auth_time":"2026-11-08T10:00:00Z"}
```
Built only from validated IdP/token server-side; client cannot choose tenant, role or group.

Canonical MVP roles are `system_admin`, `website_manager`, `employee` and `chairman`, plus anonymous public access. `system_admin` may perform system/developer operations and all website management but cannot read other users' conversation bodies; `website_manager` has website-management powers but no code/system powers; `employee` can access PUBLIC and assigned INTERNAL documents; `chairman` has published-document read access without website-management powers; anonymous access is limited to `PUBLIC` documents. Explicit deny and current-version checks apply to document reads.

## PolicyDecision
```json
{"decision":"ALLOW","principal_id":"u-123","resource_type":"document","resource_id":"doc-42","action":"document:read","policy_version":"policy-v7","reason_code":"ACL_ALLOW","evaluated_at":"2026-11-08T10:02:00Z"}
```
Fail closed on policy store unavailability, stale policy version, unknown classification or malformed principal.

## Actions
`document:create`, `document:read`, `document:update`, `document:delete`, `document:approve`, `document:publish`, `source:download`, `tool:execute`, `conversation:read`, `feedback:create`.

## Retrieval scope
Provide a server-issued, opaque `AuthorizedScope` (tenant, policy version, classification constraints, filtered approved document/version IDs). Retriever receives a scope internally; never accept an arbitrary `allowed_document_ids` from the LLM or web client.

## API rule
Use **PDP** to compute decision; **PEP** at endpoints, retriever, tool gateway, parent fetch and citation download. Never infer that `chairman` can upload, that `website_manager` can execute code/system operations, or that a client-supplied `admin` role can read every restricted document.

## Owner-provided policy baseline

- MVP product classification is `PUBLIC` or `INTERNAL`; future higher-sensitivity egress tiers remain subject to separate approval.
- Authorization uses RBAC, department membership and document-level ACLs with default deny.
- Explicit deny overrides role allow. Chairman's broad read role does not bypass an explicit deny.
- Employee onboarding requires an access request followed by administrator approval and provisioning.
- Chairman, Website Manager and System Admin require MFA. System Admin must not automatically read user conversation bodies.
- Workers use short-lived service identities and recheck tenant, ACL, policy version and document version before work, resume, chunk access and citation delivery.
