# Synthetic evaluation harness

This directory contains the smallest deterministic pre-runtime evaluation package for `EVAL-PREP-001`.

## Dataset

`golden_dataset.jsonl` contains 200 synthetic cases only:

- 140 Vietnamese / 60 English cases.
- 140 simple / 60 complex cases.
- 50 permission-negative cases, including explicit-deny and cross-tenant cases.
- 30 unanswerable cases (overlap with permission-negative is allowed by the schema).
- Synthetic PDF, DOCX and XLSX locators, version conflicts, OCR, long tables, multi-hop evidence and indirect-injection labels.

Each line follows `docs/testing/golden-dataset-schema.md` and may add evaluation metadata without changing the shared contract.

## Protocol and metrics

`_evaluation_harness.py` validates JSONL shape, status/source invariants, file-type locators, tenant binding and the owner-provided composition requirements.

Metrics are deterministic, uncalibrated measurements:

- `Recall@k`: expected source spans recovered in the first `k` results.
- `nDCG@k`: graded rank score with binary relevance for expected spans.
- `MRR`: reciprocal rank of the first expected span.
- `citation_accuracy`: returned citations matching expected spans divided by returned citations; no citation is correct for a no-answer case.
- `answer_correctness`: Jaccard overlap between expected and returned fact sets.
- `no_answer_accuracy`: whether expected and actual statuses agree on answerable versus no-answer.
- `unauthorized_retrieval_rate`: unauthorized retrieval outcomes divided by evaluated outcomes.

Thresholds, latency/cost gates, model choice and release decisions are intentionally not approved here; the Project Owner must decide them after benchmark evidence.

## Exact validation command

```sh
python3 -m unittest discover -s tests/evaluation -p 'test_*.py'
```

The four family files contain exactly 10 materially different cases each (40 total). The tests validate fixtures and metric calculations only; full runtime answer evaluation remains `EVAL-001`.
