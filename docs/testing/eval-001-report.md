# EVAL-001 — Direct V1–V4 baseline evaluation

Status: **QA evidence collected; release/threshold decision PENDING_PROJECT_OWNER_APPROVAL**.

This report uses only the checked-in synthetic Golden Dataset and deterministic local seams. No provider API key, external model, production corpus, or provider metric is claimed.

## Reproduction

```sh
/tmp/know-venv/bin/python -m pytest --import-mode=importlib tests/evaluation tests/security
PYTHONPATH=. /tmp/know-venv/bin/python tests/evaluation/run_eval_001.py
```

Dataset: `tests/evaluation/golden_dataset.jsonl`; 200 records; model/provider: `deterministic-local embedding/reranker + synthetic answer seam` / `none`.

## V1–V4 result

| Version | Runtime mapping | Cases | Recall@10 | nDCG@10 | MRR | Citation accuracy | Answer correctness | No-answer accuracy | Unauthorized retrieval | Local p50/p95 ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V1 | Dense only | 200 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.464/0.822 |
| V2 | Dense+BM25+RRF | 200 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.570/0.989 |
| V3 | + deterministic reranker | 200 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.601/1.045 |
| V4 | NOT RUN — parent expansion seam absent | — | — | — | — | — | — | — | — | — |

The reported quality averages include all 200 records. `ACCESS_DENIED` and `INSUFFICIENT_EVIDENCE` are both treated as safe no-answer classes by the existing metric contract; the direct pipeline intentionally returns `INSUFFICIENT_EVIDENCE` when authorization-filtered retrieval is empty.

The 1.0000 quality values are a deterministic upper-bound smoke result: each answered case is isolated to its own synthetic authorized source set and the answer seam is an oracle. They are not evidence of production retrieval quality or provider performance.

## Dataset and security evidence

- Permission-negative cases: **50**; cross-tenant cases: **24**.
- Forbidden-source leakage cases: **V1=0, V2=0, V3=0**.
- Dataset schema/composition, source locator types, tenant/version binding, explicit deny, cross-tenant, unanswerable, injection and conflicting-version labels were validated by the existing four-family EVAL-PREP tests.
- Revoked-source behavior was exercised by existing deterministic backend/evidence tests; no backend code was changed by EVAL-001.
- No raw source content, credentials, provider output, or production identifiers were added.

## Thresholds and limitations

Recall@10 ≥90% and the calibrated answer-confidence floor of 80% were
approved by the Project Owner on 2026-11-10. The remaining citation,
answer-correctness, no-answer, latency and cost gates are
**PROPOSED/PENDING_PROJECT_OWNER_APPROVAL**. This run does not approve or
reject those remaining gates.

- Provider token/cost and external-provider latency are **NOT MEASURED**; local deterministic timings are not production performance claims.
- V4 is **NOT RUN** because parent expansion is documented but not exposed as a runtime retriever seam. Implementing it is outside this QA task and would require a backend owner decision.
- `AnswerCitation` carries document/version/page/span/chunk but not tenant/policy-epoch or the schema's DOCX heading/paragraph and XLSX sheet/cell-range locators; citation contract fidelity remains a production finding/reproducer, not a QA workaround.
- Synthetic answer generation is an oracle seam for repeatability, not a provider quality measurement.
- Error handling: synthetic answer-model failure returns `ERROR` with no answer/citations; empty input returns `ACCESS_DENIED`; unanswerable input returns safe `INSUFFICIENT_EVIDENCE`.

## Exact QA commands/results

- `/tmp/know-venv/bin/python -m pytest --import-mode=importlib tests/evaluation tests/security` → **PASS, 72 passed, exit 0**.
- `/tmp/know-venv/bin/python -m pytest --import-mode=importlib backend/tests/test_dense_retrieval.py backend/tests/test_hybrid_retrieval.py backend/tests/test_evidence.py` → **PASS, 16 passed, exit 0**.
- `PYTHONPATH=. /tmp/know-venv/bin/python tests/evaluation/run_eval_001.py` → **PASS, report written, exit 0**.
- `/tmp/know-venv/bin/python scripts/validate_harness.py` → **PASS, 17 blocks, 8 agents, 41 tasks, no dependency cycles** (scaffolding only).
- The runtime evaluator executed 200 Golden Dataset records for each of V1, V2 and V3; repeatability checks were true for all three.

