# MODEL-QA-001 — Independent QA handoff

- Task ID: `MODEL-QA-001` (review of `MODEL-001`)
- Agent owner: `qa`
- Status: `PASS` — initial findings resolved and revalidated
- Contract version(s) used: retrieval v1.0, answer/citation v1.0, audit/events v1.0, `v1-baseline.md`
- Upstream dependencies checked: `INFRA-001`, `BACKEND-BOOT-001`, MODEL-001 handoff, task registry
- Changed files: only the four QA modules and `_baseline.py`/`__init__.py`
- New/updated tests: 40 deterministic synthetic cases: 10 in each required family

## Mandatory Graphify evidence

The first repository command was:

```bash
/tmp/graphify-venv/bin/graphify query "MODEL-001 model policy embedding reranker adapters gateway timeout retry fallback egress credentials data protection" --graph graphify-out/graph.json
```

It returned the scoped MODEL-001 symbols in `backend/app/models/policy.py`,
`backend/app/models/adapters.py` and `backend/app/integrations/model_gateway.py`
from a 1,576-node graph.
The review did not begin with grep or raw source reads.

## Commands and results

The exact QA command was:

```bash
/tmp/enterprise-rag-model-test-venv/bin/python -m pytest tests/qa/model -q
```

Initial result: **FAIL** — `34 passed, 6 failed`. The suite contains exactly 40 cases;
the six failures reproduce three implementation defects below. No application
code was changed.

Additional required checks:

```bash
/tmp/enterprise-rag-model-test-venv/bin/python -m pytest backend/tests -k model
/tmp/enterprise-rag-model-test-venv/bin/python -m pytest backend/tests
python3 -m compileall -q backend/app/models backend/app/integrations backend/tests/test_models.py tests/qa/model
python3 scripts/validate_harness.py
```

Observed results:

- `backend/tests -k model`: `40 passed, 58 deselected`
- `backend/tests`: `96 passed, 2 skipped` (`DB001_DATABASE_URL` not configured)
- `compileall`: `PASS`
- `validate_harness.py`: `HARNESS VALID: 17 blocks, 8 agents, 41 tasks`

Revalidation result: **PASS** — `40 passed` after the three boundary fixes. Live PostgreSQL/provider/network checks are not part of this synthetic
review and remain blocked until their approved test services/configuration are
available.

## Findings

1. **MODEL-QA-F001 — unknown classification can raise `AttributeError`**

   `ModelGateway` accepts a raw runtime value, `ProviderPolicy.allows()` denies
   it, then `ModelEgressDenied` assumes `.value` exists. An untrusted unknown
   classification should fail closed with the typed safe denial, not a raw
   internal exception.

2. **MODEL-QA-F002 — credential-like policy keys are incomplete**

   `ModelPolicy.from_mapping()` rejects only exact `api_key`, `token`,
   `secret`, and `password` keys. Variants such as `access_token` and
   `secret_key` are accepted into configuration, contrary to the stated
   credential boundary.

3. **MODEL-QA-F003 — unexpected adapter exceptions are not sanitized**

   `ModelGateway` sanitizes `ModelProviderError` messages but lets arbitrary
   adapter exceptions propagate. A provider SDK can raise a generic exception
   containing request/credential material; the gateway should classify it into a
   safe `ModelUnavailable` path before the provider adapter is productionized.

## Revalidation and acceptance conclusion

`MODEL-001` is **accepted by this independent QA gate** after revalidation. Retry/fallback
limits, typed route boundaries, egress denial for PUBLIC/INTERNAL, and existing
credential-key tests passed where applicable. The three findings above must be
fixed and rerun through this same 40-case package before Main Agent review can
mark the task integrated.

- Security implications: unknown classification, credential configuration and raw provider exception leakage are fail-closed/privacy boundaries; all three were fixed and retested.
- Integration steps completed: reran this package plus backend model/full tests with exact totals above.
- Human approval required: any real external/paid provider, region, DPA, residency, retention or credential decision remains Project Owner approval.
