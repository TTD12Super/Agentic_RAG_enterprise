# EVID-001 — Evidence and citation verification

## Status

`ACCEPTED — MAIN AGENT REVIEW COMPLETE`

## Scope delivered

- Added immutable `SourceSpan`, `CitationRecord`, and `EvidenceRecord` models.
- Added `EvidenceVerifier` with deterministic lexical claim-to-evidence support.
- Added `SUPPORTED`, `UNSUPPORTED`, `CONFLICTING`, `PARTIAL`, and `ACCESS_DENIED` outcomes.
- Added fail-closed tenant, document/version, `ACTIVE`, current-version, revocation, malformed-input, callback-error, and authorization checks.
- Denied results contain no source text; source text is used only inside verification.
- Added focused tests for support, insufficiency, conflicting numeric spans, stale versions, revocation, tenant mismatch, denial redaction, and immutability.

The verifier is provider-neutral and does not access a database or cloud service. The supplied callback is the PEP boundary and must return an authoritative `AuthorizationDecision` matching the citation's tenant/document/version, with `status="ACTIVE"`, the same `current_version_id`, and `revoked=False`.

## Files

- `backend/app/evidence/__init__.py`
- `backend/app/evidence/verifier.py`
- `backend/tests/test_evidence.py`

## Commands and results

Required first graph query:

```text
/tmp/graphify-venv/bin/graphify query --graph graphify-out/graph.json --query "backend evidence citation retrieval source span ACTIVE version revoked authorization" --limit 20
```

Result: exit 0. Graphify reported 2,457 nodes, 76 nodes found, and truncated the display after 59 nodes.

Focused pytest command:

```text
pytest backend/tests -k evidence
```

Result: exit 127 — `pytest` is not installed as a command.

Additional pytest check:

```text
python3 -m pytest backend/tests -k evidence
```

Result: exit 1 — the available Python 3.15 environment had no `pytest` module.

Main validation:

```text
/tmp/know-venv/bin/python -m pytest backend/tests/test_evidence.py -q
```

Result: `8 passed`.

```text
/tmp/know-venv/bin/python -m pytest tests/qa/evidence -q
```

Result: initial `38 passed, 2 failed`; after Main fixed duplicate citation
IDs to fail closed, `40 passed`.

```text
/tmp/know-venv/bin/python -m pytest --import-mode=importlib backend/tests tests/integration tests/evaluation tests/security tests/qa/guardrails tests/qa/evidence -q
```

Result: `363 passed, 2 skipped`; the skips require `DB001_DATABASE_URL`.

Standard-library verification:

```text
python3 -m compileall -q backend/app/evidence backend/tests/test_evidence.py && python3 - <<'PY'
import importlib.util
from pathlib import Path

path = Path('backend/tests/test_evidence.py')
spec = importlib.util.spec_from_file_location('test_evidence_manual', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
tests = [name for name in dir(module) if name.startswith('test_')]
for name in tests:
    getattr(module, name)()
print(f'{len(tests)} focused evidence tests passed')
PY
```

Result: exit 0 — 8 focused evidence tests passed.

```text
git diff --check
```

Result: exit 0.

## CHAT-001 integration boundary

CHAT-001 must call the authorization/PEP boundary again for every citation preview and original-source/download request. It must recheck the current principal, tenant, document ACL, policy freshness, and the citation's exact ACTIVE version/revocation state; a newer version must never be substituted for a stale citation. On denial or stale state, return only a safe unavailable/denied response and no excerpt, source text, path, or link. This verifier's claim result is not a download authorization token.

## Limitations

- Lexical support uses an 80% normalized-token overlap heuristic plus simple negation/numeric contradiction checks; it is not semantic entailment and does not guarantee factual correctness.
- Current-version and revocation truth remains owned by the callback/PDP/PEP; this task intentionally does not edit or integrate the authorization, retrieval, ingestion, prompt, guardrail, frontend, infra, or contract layers.
- Lexical verification remains a heuristic; semantic entailment and live
  citation preview/download rechecks remain downstream work in CHAT-001.
