# Retrieval and answer evaluation plan

Compare V1 dense-only → V2 dense+BM25+RRF → V3 + reranker → V4 + parent-child → V5 + bounded multi-step Agent.

`EVAL-001` evaluates the direct V1–V4 baseline after `ANSWER-BASE-001`; the V5 agentic evaluation runs at release after `ORCH-001`. No Phase 3 gate requires the Phase 4 agent to exist.

For each version record Recall@5, nDCG@10, MRR, citation accuracy, answer grounding/correctness, unauthorized-retrieval rate, p50/p95 latency, token/cost per query and no-answer accuracy.

Gold data structure: query, tenant, principal/role/scope fixture, expected authorized source span(s), expected answer/abstention, security category. Keep confidential corpora out of tests; use synthetic fixtures.

Avoid interpreting similarity/rerank scores as calibrated probabilities. Require evidence-backed acceptance thresholds approved by project owner after baseline measurements.

## Owner-provided proposal targets

- Golden Dataset: at least 200 cases; 70% Vietnamese and 30% English; 70% simple and 30% complex; at least 50 permission-negative and 30 unanswerable cases, with overlap allowed.
- Proposed thresholds: Recall@10 ≥90%, citation accuracy ≥95%, citation grounding precision ≥95%, answer correctness ≥90%, no-answer accuracy ≥90% and zero unauthorized retrieval/cross-tenant leakage.
- Proposed load target: p95 simple ≤30 seconds and complex ≤90 seconds at the Q33 profile (500 active sessions, 30 queries/minute sustained, 60 queries/minute burst).
- Cost targets are ≤$0.05/simple and ≤$0.20/complex. These values are targets, not production SLAs, until the selected provider and benchmark are approved.
