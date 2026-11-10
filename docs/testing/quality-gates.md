# Quality gates and Definition of Done

## Per task
- Accepted contract, tests, changed-file report, no unauthorized scope expansion, handoff checked by Main Agent.

## Before Secure RAG baseline sign-off
- API, policy, document and retrieval contract tests.
- Allowed and denied roles tested in dense, sparse, parent and citation endpoints.
- Source/version provenance preserved; unavailable Qdrant and PDP handled explicitly.
- Baseline eval report with latency and cost; no claims of universal performance.

## Before LangGraph sign-off
- Tool registry is server controlled, tool access checked, bounded loops, abort/retry and partial-answer behavior tested.

## Before external deployment
- Secrets rotation, backup restore rehearsal, network isolation, incident runbook, data-retention policy and security review.

## Owner-provided release gates

- Security negative tests: 100% pass for the defined suite.
- Cross-tenant leakage and unauthorized retrieval: zero.
- Citation correctness: at least 95%; retrieval Recall@10: at least 90%; answer correctness and no-answer accuracy: at least 90%.
- Calibrated answer confidence: at least 80% to release an answer; below 80% must abstain with `INSUFFICIENT_EVIDENCE`.
- p95 latency target at peak profile: simple ≤30 seconds, complex ≤90 seconds; measure queue, maintenance and processing time separately.
- API/job error rate target is below 1%, excluding deliberate 429/503 overload protection but reporting those separately.
- Cost target is at most $0.05/simple and $0.20/complex.
- Restore drill must demonstrate the proposed RPO ≤1 hour and RTO ≤4 hours, including tombstone/revocation replay.
- Maintenance pause/resume must not lose or duplicate jobs and must pass ACL/version rechecks.
- Valid 200 MB uploads must not cause OOM; oversized or over-complex files must return safe, explicit errors.
