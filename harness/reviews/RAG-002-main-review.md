# RAG-002 — Main Agent review

## Decision

`ACCEPTED`

BM25, RRF and the provider-neutral deterministic reranker are accepted for
the local hybrid baseline. Both retrieval branches reuse the RAG-001
authorization/lifecycle gate before candidates are scored or returned.

## Evidence

- Focused RAG-001/RAG-002 and metrics tests: `9 passed`.
- Required QA matrix: initial `39 passed, 1 failed`; after the fix,
  `40 passed`.
- Full backend/integration/evaluation suite: `249 passed, 2 skipped`.
- Metrics on the declared three-chunk corpus: Dense, BM25, RRF and reranked
  Recall@5/nDCG@5/MRR all `1.0`.
- The root evaluation import-path defect was fixed in test imports; the exact
  retrieval command now passes.

## Security fix

Dense embedding failure now returns `ERROR`, and HybridRetriever stops before
BM25/reranking. It cannot silently downgrade a failed hybrid request into a
lexical-only result.

## Scope boundary

This remains an in-memory deterministic baseline. Qdrant, durable indexes,
production cross-encoder selection, parent expansion, API/orchestration
wiring and cloud/provider decisions remain deferred.
