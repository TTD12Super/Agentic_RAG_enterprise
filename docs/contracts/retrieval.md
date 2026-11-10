# Secure Retrieval contract (proposal)

## Internal request (never untrusted client request)
```json
{"query":"warranty for product A","principal_ref":"server-session-reference","authorized_scope_ref":"policy-scoped-token","tenant_id":"tenant-a","top_k":8,"trace_id":"trace-1"}
```
`authorized_scope_ref` is issued/validated by backend. The model cannot choose it.

## Algorithm
1. Validate current principal + scope, tenant, document status and approved version.
2. Apply identical ACL/tenant/active filters in dense and BM25 branches **before results return**.
3. RRF fusion → reranking → deduplication → optional authorized parent expansion.
4. Revalidate each chunk/document in policy store before returning content.
5. Missing/denied docs remain invisible; failures fail closed.

## Response
```json
{"evidence":[{"chunk_id":"chunk-77","document_id":"doc-42","version_id":"v-2","page_start":4,"page_end":4,"source_span":{"start":101,"end":412},"text":"...","retrieval_method":"hybrid","citation_token":"signed-short-lived-reference"}],"query_id":"q-4"}
```
Never send privileged raw document paths to the client or LLM. Scores are ranking signals, not confidence probabilities.

## Owner-provided retrieval baseline

- MVP uses Qdrant dense and sparse/BM25 retrieval with RRF fusion; OpenSearch/Elasticsearch are deferred.
- Reranking is enabled by default on the authorized candidate set. Parent expansion is conditional on evidence need and token budget.
- Every branch filters tenant, current ACTIVE version and ACL before returning candidates, then rechecks authorization before content and citation delivery.
- Simple/complex execution allows at most two retrieval rounds, four subqueries and eight tool calls.
- Unknown or stale policy, tenant, classification or version fails closed and never broadens search.
