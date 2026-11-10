# RAG-002 QA handoff

## Outcome

`PASS — MAIN AGENT FIX VERIFIED`

The QA suite contains exactly 40 independent tests: 10 behavior/component,
10 contract/integration, 10 E2E/operational and 10 security/adversarial.
Synthetic in-memory fixtures and deterministic local model doubles are used;
no network calls or API keys are required.

## Changed files

- `tests/qa/rag_hybrid/test_behavior_component.py`
- `tests/qa/rag_hybrid/test_contract_integration.py`
- `tests/qa/rag_hybrid/test_e2e_operational.py`
- `tests/qa/rag_hybrid/test_security_adversarial.py`
- `harness/handoffs/RAG-002-QA.md`

No production code, task registry, contracts, frontend, infrastructure or
existing RAG-002 implementation files were changed by this QA task.

## Coverage

- BM25 tokenization, term frequency, length normalization and configuration.
- RRF rank contribution and duplicate suppression.
- Deterministic reranking, hybrid composition and stable ordering.
- Citation/version/source-span contract and source-fetch redaction.
- Top-k/query/config validation and regression metrics.
- Tenant, ACL, current ACTIVE version, ACTIVE index and policy-epoch filters in
  both dense and BM25 branches.
- Policy-store outage, reranker failure, embedding failure and unauthorized
  candidate leakage cases.

## Required Graphify orientation

Command:

```text
/tmp/graphify-venv/bin/graphify query --graph graphify-out/graph.json --query "backend rag dense hybrid BM25 RRF reranker authorization citation" --limit 20
```

Result: PASS. Graphify reported `graphify-out/graph.json` with 2,166 nodes,
70 nodes found and 60 displayed due to the output budget. The neighborhood was
primarily existing QA/evaluation graph nodes; source inspection then followed
the scoped RAG instructions and contracts.

## Commands and results

QA suite:

```text
/tmp/know-venv/bin/python -m pytest tests/qa/rag_hybrid -q
```

Result: **PASS — 40 passed**.

Initial failed test (fixed before final PASS):

```text
tests/qa/rag_hybrid/test_security_adversarial.py::test_embedding_failure_fails_closed_without_bm25_fallback_leak
```

Focused backend/evaluation tests:

```text
PYTHONPATH=tests/evaluation /tmp/know-venv/bin/python -m pytest backend/tests/test_dense_retrieval.py backend/tests/test_hybrid_retrieval.py tests/evaluation/test_rag_002_metrics.py -q -s
```

Result: **PASS — 9 passed in 0.08s**. Reported dense, BM25, RRF and hybrid
metrics were all Recall@5 1.0, nDCG@5 1.0 and MRR 1.0.

Full backend/integration tests:

```text
/tmp/know-venv/bin/python -m pytest backend/tests tests/integration -q
```

Result: **PASS — 208 passed, 2 skipped in 2.01s**. Skips require the optional
`DB001_DATABASE_URL` disposable PostgreSQL service.

Compile check:

```text
/tmp/graphify-venv/bin/python -m compileall -q backend/app/rag backend/tests/test_dense_retrieval.py backend/tests/test_hybrid_retrieval.py tests/evaluation/test_rag_002_metrics.py tests/qa/rag_hybrid
```

Result: **PASS**.

Whitespace/diff checks:

```text
git diff --check
```

Result: **PASS**.

The four untracked QA files were also checked with `git diff --no-index --check
/dev/null <file>`; result: **PASS — no whitespace errors**.

## Production defect and revalidation

Initial QA found that dense embedding failure was converted to an empty result,
allowing hybrid retrieval to continue with BM25 and return `OK` evidence.
Main fixed the boundary: dense embedding failure returns `ERROR`, and hybrid
retrieval stops before BM25/reranking. The adversarial case now passes.

Revalidation: `/tmp/know-venv/bin/python -m pytest tests/qa/rag_hybrid -q` —
`40 passed`.

## Approval boundary

RAG-002 QA is accepted for the deterministic local scope. Live Qdrant,
PostgreSQL and provider tests remain outside this environment. No commit or
push was performed by QA.
