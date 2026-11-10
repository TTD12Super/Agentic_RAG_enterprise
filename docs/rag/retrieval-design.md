# Secure Hybrid Retrieval design

## Steps
1. Validate principal, session, PDP/PEP and corpus/index version.
2. Normalize user query; optional standalone rewrite or multi-query decomposition.
3. Search authorized ACTIVE versions in **both** dense and BM25 branches.
4. Fuse ranks with RRF; rerank only authorized candidate texts.
5. Expand child→parent only if permitted and necessary; deduplicate and construct token-bounded evidence context.
6. Context guard prevents retrieved text from becoming instructions.
7. Check evidence sufficiency; Agent may replan within budgets.
8. Cite source spans and verify claim grounding before response.

## Initial execution bounds
- retrieval rounds: 2 max; subqueries: 4 max; candidate counts: evaluate ~30/branch, ~20 rerank, 5–8 final chunks.
- Timeout and token limits decided by environment + measurement; use explicit policy in code.

## Failure handling
No authorized match → `INSUFFICIENT_EVIDENCE` (never silently broaden scope). PDP unavailable → `ACCESS_DENIED`/service unavailable, not unrestricted search. Unauthorized source must not leak via rank features, snippets, facets or citation titles.

## Owner-provided execution limits

- Use Qdrant dense+sparse/BM25 with RRF. OpenSearch/Elasticsearch are outside the MVP.
- Use `BAAI/bge-m3` embeddings and `BAAI/bge-reranker-v2-m3` as baselines; reranking is on by default unless a measured rule bypasses it.
- Rule-based routing comes first. Complex work means multi-source synthesis/comparison, dependent subquestions or insufficient first-pass evidence; it is not defined merely by corpus size.
- Maximum two retrieval rounds, four subqueries and eight tool calls. Simple budget is 16k input/2k output tokens; complex budget is 32k/4k.
- Target query cost is at most $0.05 simple and $0.20 complex, subject to provider benchmark and approval.
