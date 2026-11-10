# Contract change process

1. Agent files a request with current behavior, proposed new schema, compatibility risks and affected owners.
2. Main Agent identifies consumers, checks ADR and security implications.
3. Affected agents review a versioned contract change; owner approves breaking changes.
4. Update contract *before* implementation; add contract tests and migration strategy.
5. Update dependent tasks and communicate to all owners; avoid parallel edits to contract file.
6. Tech Lead integrates and verifies tests. Never quietly treat a failing dependency as DONE.

Status: DRAFT → REVIEW → APPROVED → IMPLEMENTING → VERIFIED → DEPRECATED (or REJECTED during review).

The MVP baseline is `enterprise-agentic-rag` `schema_version=1.0`, recorded in `v1-baseline.md`. Version 1.0 is approved for implementation; later changes must create a new version or a documented additive revision and repeat affected-agent compatibility review.
