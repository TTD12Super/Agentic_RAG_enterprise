# PROMPT-001 handoff

## Status

`ACCEPTED — MAIN AGENT REVIEW COMPLETE`

## Delivered

- `backend/app/prompts/registry.py` provides immutable `PromptDefinition` records, frozen JSON-schema metadata, exact prompt versions, and a provider-neutral default registry for `system@v1`, `planner@v1`, and `answer@v1`.
- `backend/app/orchestration/context.py` provides `RetrievedEvidence`, `SecureContextBuilder`, and provider-neutral message records.
- The builder emits separate trusted system, user-query, and untrusted-retrieved-content sections. Retrieved content is explicitly marked as data, HTML-escaped so it cannot close the delimiters, and its chunk/document/version/page/span/citation metadata is preserved.
- Character and deterministic estimated-token limits fail closed. The builder accepts no conversation-history or authorization parameter and does not log context. Obvious credential patterns are redacted before assembly.
- `backend/tests/test_prompts.py` covers registry immutability/versioning, provenance preservation, injection delimiters, secret redaction, bounds, and absence of conversation-history input.

## Validation

- `/tmp/know-venv/bin/python -m pytest backend/tests/test_prompts.py -q` — PASS, 6 passed.
- `/tmp/know-venv/bin/python -m pytest tests/qa/prompt -q` — PASS, 40 passed.
- `/tmp/know-venv/bin/python -m pytest backend/tests tests/integration tests/evaluation -q` — PASS, 255 passed, 2 skipped.
- `git diff --check` — PASS.

## Approval boundaries and known limits

- No authorization, retrieval/RAG, frontend, infrastructure, contracts, task registry, commit, push, API key, or cloud changes were made.
- Authorization must be enforced by the retrieval/tool path before evidence reaches this builder; the builder preserves supplied provenance but does not grant access.
- Secret redaction is intentionally a small heuristic for this provider-neutral MVP; replace it with an approved DLP/secret-scanning control before production use.
- Token limits use a deterministic character estimate; wire the selected provider tokenizer when provider-specific accounting is approved.
- Graphify refresh is performed by Main Agent after acceptance and tracked with the phase checkpoint.
