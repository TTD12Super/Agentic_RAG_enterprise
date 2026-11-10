# Handoff — AUTH-001

## Status

READY_FOR_INTEGRATION — trusted PDP/PEP implementation and focused negative-path tests complete; awaiting AUTH-QA-001 and Main Agent review.

## Delivered

- Provider-neutral, fail-closed authorization evaluator in `backend/app/authorization/policy.py`.
- Canonical actions, roles, PUBLIC/INTERNAL classifications and policy epochs.
- RBAC plus department membership plus document ACL evaluation.
- Explicit DENY precedence over every ALLOW and default deny.
- Tenant isolation, current-version checks, principal revocation and unavailable-policy denial.
- Anonymous PUBLIC-only reads and owner-only conversation body reads.
- Reusable PEP that raises a safe non-existence-revealing denial.

## Validation evidence

Executed from the repository root in a temporary backend environment:

    pytest -q tests/security/test_authorization.py backend/tests/test_identity.py backend/tests/test_app.py
    PASS — 25 passed

The focused authorization tests cover public/internal access, department and ACL
assignment, explicit deny precedence, Chairman read-only behavior, tenant
isolation, stale policy/version, principal revocation, policy-store outage,
unknown classification, malformed principals, PEP denial, and owner-only
conversation access.

## Boundaries and residual risks

- The policy store is an in-memory deterministic adapter; PostgreSQL policy reads,
  durable ACL management and transactional policy epochs belong to later integration.
- PEP call sites at retrieval, chunk/parent fetch, citation download, tools and
  memory/cache are downstream consumers and must not bypass this PDP.
- `AUTH-QA-001` must execute the required four families with at least 10
  materially different cases per family.

No commit or push was performed by this task.
