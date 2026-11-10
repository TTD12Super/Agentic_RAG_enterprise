# RAG implementation decisions

Baseline: **permission-aware Dense + BM25 + RRF + Cross-Encoder reranking**, optional parent-child expansion, bounded query rewrite and claim-level validation. Compare against dense-only baseline on synthetic/test corpora before asserting improvement.

- `ingestion-design.md`: parse, split, parent-child, index.
- `retrieval-design.md`: query processing, ACL, fusion/rerank and loops.
- `evaluation-plan.md`: metrics, gold labels and failure analysis.

## Owner-provided baseline

- Dense and sparse/BM25 retrieval run in Qdrant and fuse with RRF.
- Baseline embedding is `BAAI/bge-m3`; baseline reranker is `BAAI/bge-reranker-v2-m3`.
- Structure-aware chunks target 500–800 tokens, 10–15% overlap and parent sections up to 2,000 tokens.
- Simple/complex execution is bounded at two retrieval rounds, four subqueries and eight tool calls.
- The owner-provided proposal and remaining blockers are recorded in [`../requirements/owner-decision-baseline.md`](../requirements/owner-decision-baseline.md).
