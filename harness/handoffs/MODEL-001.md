# MODEL-001 — Model adapter boundary handoff

## Status

`ACCEPTED — MAIN AGENT REVIEW`

This task adds a provider-neutral embedding/reranker boundary without selecting
an external provider, requesting credentials, or changing contracts, RAG,
authorization, infrastructure, or the task registry.

## Graphify-first evidence

The mandatory first command was:

```bash
/tmp/graphify-venv/bin/graphify query "embedding reranker model provider timeout retry fallback data egress" --graph graphify-out/graph.json
```

Findings: Graphify found no existing `embedding` or `reranker` nodes. It did
locate the existing provider-neutral identity boundary, authorization evaluator,
audit sink, and operational timeout/fallback tests. The scoped implementation
therefore creates the missing model/integration boundary without modifying
those existing modules or contracts.

After implementation, the graph query:

```bash
/tmp/graphify-venv/bin/graphify query "ModelGateway ModelPolicy EmbeddingAdapter RerankerAdapter" --graph graphify-out/graph.json --budget 3000
```

located all four new symbols and their adapter/gateway relationships in
`backend/app/models` and `backend/app/integrations`.

## Changed files

- `backend/app/models/__init__.py`
- `backend/app/models/policy.py`
- `backend/app/models/adapters.py`
- `backend/app/integrations/__init__.py`
- `backend/app/integrations/model_gateway.py`
- `backend/tests/test_models.py`
- `harness/handoffs/MODEL-001.md`

## Implemented behavior

- Immutable `ModelPolicy` with policy version, model revision, primary and
  fallback routes for embedding and reranking.
- Typed embedding/reranker request, result and adapter protocols.
- Explicit PUBLIC/INTERNAL classification and LOCAL/EXTERNAL egress policy.
- External routes require approval, explicit request-retention policy, no
  provider training, and DPA/residency approval for INTERNAL data.
- Primary route retries are bounded to at most two retries; fallback is tried
  once and is independently checked against the same classification policy.
- Provider calls receive a maximum 60-second timeout budget.
- Credential-like fields are rejected by policy mapping; no API key is read or
  stored.
- Deterministic test doubles are kept in the test module; no model SDK or
  network provider was added.

## Validation

```text
/tmp/enterprise-rag-model-test-venv/bin/python -m pytest backend/tests -k model
40 passed, 58 deselected

/tmp/enterprise-rag-model-test-venv/bin/python -m pytest backend/tests
96 passed, 2 skipped
```

The two skips are the existing disposable PostgreSQL migration tests because
`DB001_DATABASE_URL` was not configured. Additional checks:

```text
python3 -m compileall -q backend/app/models backend/app/integrations backend/tests/test_models.py
PASS

git diff --check
PASS
```

## Unresolved decisions / review gates

- Primary/fallback provider, region, DPA, residency, retention terms and API
  credentials remain Owner/ADR decisions. No provider was guessed.
- The adapter timeout is passed as a hard provider-call budget; concrete HTTP
  adapters must enforce it when a provider is selected.
- Main Agent should review the gateway error taxonomy and integrate this
  boundary with the later retrieval/ingestion tasks.

No commit or push was performed by this task agent.

## Main Agent revalidation

- Fixed unknown-classification denial, credential-key variant rejection and generic provider-exception sanitization.
- Independent QA rerun: 40/40 passed.
- Backend rerun: 96 passed, 2 skipped because `DB001_DATABASE_URL` was not configured.
- Main review: `harness/reviews/MODEL-001-main-review.md`.
