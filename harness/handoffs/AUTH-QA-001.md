# Handoff — AUTH-QA-001

## Exact command

`/tmp/erag-auth-venv/bin/python -m unittest discover -s tests/qa/authorization -p 'test_*.py'`

## Count

- 4 unittest files
- 10 deterministic cases per family
- 40 total cases

## Result

PASS — 40/40 cases passed in the backend dependency environment. The bare host command `python3 -m unittest discover -s tests/qa/authorization -p 'test_*.py'` is BLOCKED at collection because `pydantic` is not installed there.

Coverage includes PDP/PEP behavior, contract/export integration, explicit-deny precedence, tenant isolation, malformed identity and classification rejection, policy outage fail-closed behavior, revocation, current-version enforcement, safe PEP denial, and offline operational checks.

## Residual risks

- These tests exercise the implemented in-memory PDP/PEP only; live policy storage, endpoint wiring, retrieval branches, tool gateway, citation delivery, and cache integrations remain integration responsibilities.
- Running with a Python environment that lacks the backend dependencies will fail at collection; no dependency installation was performed.
- No external services or API keys were used, so provider-specific failure modes and deployment configuration were not exercised.
