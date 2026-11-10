# Testing map

- Unit: parsers, chunkers, query normalization, policy decisions, tool schemas.
- Contract: API schema and error semantics.
- Integration: Postgres/Qdrant/storage, publish workflow, ACL-filtered retrieval.
- Security: role/tenant denial, prompt injection, poisoned source, cache revocation.
- Evaluation: labelled retrieval/answer dataset and per-version metrics.
- E2E: admin upload, Chairman read, employee denial, citation preview.

All pass claims require a recorded actual command and exit status. No mock policy service in production deployment paths.

## Required test package for each implementation goal

For every small implementation goal, the Test Agent prepares four distinct test families and at least 10 materially different cases in each family (40 cases minimum):

1. **Behavior/component:** unit-level behavior, boundaries, invalid input and state transitions.
2. **Contract/integration:** API/schema semantics and interactions with the affected database, index, storage, queue or provider boundary.
3. **Security/adversarial:** authentication, authorization, tenant isolation, explicit deny, privacy, injection, tampering and abuse cases relevant to the goal.
4. **E2E/operational:** a user-visible workflow plus timeout, retry, failure, recovery, observability and compatibility cases relevant to the goal.

Cases must be materially different scenarios, not the same assertion copied with cosmetic values changed. Use deterministic synthetic fixtures and record the exact command, result, coverage matrix and residual risks. If a family has no applicable runtime surface, the Test Agent records the reason and supplies equivalent static/schema/validation checks rather than silently omitting the family.

The Test Agent reports findings and evidence to the Main Agent. The Main Agent reviews the suite, accepts or rejects minor local conclusions and records the decision in the task handoff. Escalate only decisions with material security, privacy, cost, architecture, availability, scope or unresolved-option impact to the Project Owner.

## Owner-provided baseline profile

- Load profile: 200 concurrent sessions/15 queries per minute normal; 500 concurrent sessions/30 queries per minute peak; 60 queries per minute for a five-minute burst.
- Mix: 70% simple and 30% complex; test cache hit rates at 0% and 30%; include 100-document baseline and 1,000-document scale scenarios.
- Include 200 MB uploads, scanned PDF OCR, complex XLSX, multi-tenant permission mixes, maintenance pause/resume, provider rate limits and fallback.
- Production no-go conditions include any cross-tenant leakage, unauthorized retrieval, use of non-ACTIVE content, or unsafe restore/revocation behavior.
- Proposed target gates are recorded in [`../requirements/owner-decision-baseline.md`](../requirements/owner-decision-baseline.md) and remain subject to benchmark approval.
