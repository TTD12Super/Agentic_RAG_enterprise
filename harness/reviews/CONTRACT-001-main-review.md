# Main Agent Review — CONTRACT-001

- Task: `CONTRACT-001`
- Review status: `DONE`
- Reviewed handoff: `harness/handoffs/CONTRACT-001.md`
- Reviewer: Main Agent
- Review date: 2026-11-10

## Decision

The Security Agent review is accepted as a valid review package. The Main Agent recorded contract v1.0 plus the delegated decisions for worker trust/replay, ACL/scope semantics, same-admin review, cache epochs, durable jobs, retention/lifecycle safeguards and the current repository/runtime boundary. All six affected-agent compatibility reviews completed with final `PASS` or `IMPLEMENTATION_DEFERRED`; no contract contradiction or serious security gap remains.

`CONTRACT-001` is `DONE` after the affected-agent review and v1.0 compatibility evidence were integrated. Cloud/provider/model/alert/benchmark decisions remain pending for their affected tasks only.

## Findings accepted for integration planning

- Add a common versioned envelope and explicit compatibility/unknown-field rules.
- Define authenticated worker command/result binding, expiry, replay protection and revocation.
- Make `AuthorizedScope` and ACL precedence machine-checkable; preserve default deny and explicit deny over allow.
- Define citation version binding and separate source download authorization.
- Define atomic cache invalidation/revocation behavior and fail-closed stale-read handling.
- Define job/maintenance transitions, lease/checkpoint/retry/replay semantics.
- Define field-level privacy-safe audit/telemetry; never expose another user's conversation body.
- Normalize idempotency and W3C trace propagation across API, queue, worker, event and checkpoint boundaries.
- Define versioned read-only tool manifest and ingestion attempt/publication invariants.

## Decisions recorded under delegation

1. Same administrator may perform review 1 and review 2, but as two independent, authorized and idempotent recorded decisions.
2. Worker trust/revocation uses TLS plus short-lived asymmetric service JWTs with audience, job/tenant binding, expiry and `jti` replay checks.
3. ACL/scope semantics preserve RBAC + department + document ACL + default deny + explicit deny precedence.
4. Cache/data ownership uses authoritative PostgreSQL epochs and fail-closed invalidation behavior.
5. Maintenance/retry/checkpoint and upload review/delete safeguards follow the durable v1.0 state rules.

The remaining provider/cloud/alert/benchmark choices stay pending and block only their affected tasks.

## Test evidence requirement

The handoff contains the required 40-case proposal: 10 behavior/component, 10 contract/integration, 10 security/adversarial and 10 E2E/operational cases. No runtime tests were claimed because this review task had no implementation write scope.

## Next step

The Main Agent authored the v1.0 contract change through `docs/contracts/CHANGE-PROCESS.md`, integrated all compatibility evidence and may now open eligible Phase 1 foundation tasks.

## Final evidence

- Security review: `harness/handoffs/CONTRACT-001.md`.
- Compatibility: `CONTRACT-001-backend.md`, `-devops.md`, `-frontend.md`, `-ingestion.md`, `-orchestration.md`, `-rag.md`; all final rechecks pass or defer only runtime implementation evidence.
- QA: `harness/handoffs/CONTRACT-TEST-001.md`; 40/40 static/schema checks pass with `python3`.
- Harness validation: `HARNESS VALID: 17 blocks, 8 agents, 32 tasks; no dependency cycles`.
