# ANSWER-BASE-001 — Direct RAG answer baseline

## Status

`IMPLEMENTED — INTEGRATION EVIDENCE RECORDED`

## Delivered

- Added `DirectAnswerPipeline` in `backend/app/rag/answer.py`.
- The path is direct and single-pass: authorized hybrid retrieval → input and
  untrusted-context guardrails → citation reauthorization → secure context →
  answer-capable model gateway → evidence verification → output/citation
  guardrail.
- Returned statuses are `ANSWERED`, `PARTIAL`, `INSUFFICIENT_EVIDENCE`,
  `ACCESS_DENIED`, and `ERROR`; only verified authorized citations are exposed.
- Revoked, denied, malformed, stale, cross-tenant, guardrail-blocked, model,
  egress, and evidence-verification failures do not return answer text or
  citation metadata from the rejected source.
- Added deterministic synthetic integration coverage for supported, partial,
  insufficient-evidence, revoked-source, model-egress, and indirect-injection
  cases.

## Changed files

- `backend/app/rag/answer.py`
- `backend/app/rag/__init__.py`
- `tests/integration/test_answer_baseline.py`
- `harness/handoffs/ANSWER-BASE-001.md`

No authorization, model, orchestration, frontend, infrastructure, contract,
task-registry, commit, or push changes were made.

## Validation

```text
/tmp/know-venv/bin/python -m pytest tests/integration/test_answer_baseline.py -q
6 passed in 0.17s

/tmp/know-venv/bin/python -m pytest backend/tests/test_dense_retrieval.py backend/tests/test_hybrid_retrieval.py backend/tests/test_evidence.py backend/tests/test_prompts.py tests/integration/test_answer_baseline.py -q
28 passed in 0.19s

/tmp/know-venv/bin/python -m pytest backend/tests tests/integration -q
228 passed, 2 skipped in 4.59s
Skipped tests require `DB001_DATABASE_URL` for the disposable PostgreSQL service.

python3 -m compileall -q backend/app/rag backend/tests tests/integration/test_answer_baseline.py
PASS

git diff --check
PASS
```

All answer tests use synthetic documents, deterministic existing hybrid
retrieval, a fake answer gateway, and a fake citation authorization callback.
No API key or external provider was used.

## Deliberate provider-neutral boundary / owner decision

`MODEL-001` currently exposes embedding and reranker operations only; the
shared `ModelGateway` has no answer-generation method or approved answer-model
route. This task therefore defines the smallest local `AnswerModelGateway`
protocol in the allowed RAG scope and tests it with a deterministic fake. The
next model/integration owner must decide whether to add answer generation to
the shared gateway and approve its provider/egress policy before production
runtime wiring. No provider or contract was guessed here.

The current hybrid baseline may return a ranked authorized candidate for a
zero-relevance dense match because retrieval scores are ranking signals, not
confidence. Insufficient evidence is consequently exercised through the
model's structured abstention and the verifier's unsupported outcome; a
calibrated relevance/abstention policy remains an evaluation decision.

`graphify update .` was not run because it writes `graphify-out/`, outside the
user-authorized write paths.

No commit or push was performed.
