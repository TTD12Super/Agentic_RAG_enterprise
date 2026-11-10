# Security index

- `threat-model.md`: trust boundaries, STRIDE-like threats.
- `authorization-matrix.md`: illustrative action matrix; policy is authoritative.
- `prompt-injection-defense.md`: direct/indirect defense-in-depth.
- `data-protection.md`: DLP, provider egress, logging, retention.
- `security-test-cases.md`: negative test cases / release gate.

Security checks happen during ingestion, each retrieval branch, tool execution, output and cached-content access.

## Owner-provided security baseline

- MVP product classification is `PUBLIC`/`INTERNAL`; unknown data denies. Future higher-sensitivity egress tiers remain stricter than INTERNAL and require explicit policy.
- Authorization is RBAC + department + document ACL with default deny and explicit-deny override.
- Chairman, Website Manager and System Admin require MFA. System Admin must not automatically read user conversation bodies.
- External model calls are permitted only to approved providers under data-processing and retention terms; fallback cannot broaden egress.
- Audit is append-only/immutable where possible, raw prompts and conversation bodies are not logged by default, and P0/P1 incidents alert the relevant on-call immediately.
- The full owner-provided proposal register is [`../requirements/owner-decision-baseline.md`](../requirements/owner-decision-baseline.md).
