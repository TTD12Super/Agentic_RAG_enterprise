# CACHE-001 handoff

Status: `DONE — MAIN AGENT ACCEPTED`.

## Graphify evidence

Because `graphify-out/graph.json` existed, the required focused query ran before repository grep/source reads:

```text
graphify query 'CACHE-001 scoped cache and conversation-memory implementation: relevant backend files, contracts, tests, and callers' --budget 1200
```

Result: `graphify-out/graph.json` was traversed with BFS depth 2; 3,159 nodes were available and 98 relevant nodes were found (23 shown at the 1,200-token budget). Relevant results included `backend/app/authorization/policy.py`, `backend/tests/test_knowledge_behavior.py`, stale-cache security coverage, policy-epoch mismatch coverage, and tenant/principal scope coverage.

After implementation, the required graph refresh ran:

```text
graphify update .
```

Result: incremental AST update re-extracted 5 changed files and rebuilt the graph to 3,261 nodes, 9,459 edges, and 157 communities.

## Changed files

- `backend/app/cache/__init__.py`
- `backend/app/cache/scoped.py`
- `backend/app/memory/__init__.py`
- `backend/app/memory/store.py`
- `backend/tests/test_cache_memory.py`
- `harness/handoffs/CACHE-001.md`
- Required Graphify refresh outputs: `graphify-out/GRAPH_REPORT.md`, `graphify-out/graph.html`, `graphify-out/graph.json`, `graphify-out/manifest.json`

## Implementation

- Added `CacheScope` and `ScopedCacheKey` with tenant, principal, policy epoch, document version, entitlement fingerprint, corpus epoch and index generation in the scope prefix. Query/model/prompt inputs are hashed, so raw query or conversation text is not placed in keys.
- Added `ScopedCacheAdapter` for a later Redis/non-authoritative provider adapter and a bounded in-memory TTL adapter.
- Reads require the caller’s current exact scope; stale policy/version/principal/tenant scope is a miss. Writes under invalidated scope fail with `StaleScopeError`.
- Added privacy-safe invalidation events and hooks for ACL changes, principal revocation, policy changes, document-version changes and deletion.
- Added `ConversationMemoryRepository` for a later PostgreSQL-backed durable adapter and a bounded in-memory test adapter. Authenticated memory uses the 180-day last-activity baseline; anonymous memory uses 30-minute idle, 24-hour maximum-age and 7-day retention bounds.
- Conversation deletion removes entries and prevents recreation under the deleted scope. Message bodies are never included in keys, invalidation metadata or `repr()` output.

## Verification

```text
python3 -m compileall -q backend/app/cache backend/app/memory
  passed

python3 -m pytest backend/tests/test_cache_memory.py -q
  11 passed

python3 -m pytest backend/tests -k cache -q
  11 passed, 240 deselected

python3 -m pytest backend/tests -q
  249 passed, 2 skipped
  skips: optional disposable PostgreSQL checks requiring DB001_DATABASE_URL

git diff --check
  passed
```

No commit or push was made.

## Limitations and integration notes

- PostgreSQL persistence, Redis transport, ordered outbox delivery, PDP calls and lifecycle callers are not wired here; the task explicitly forbids edits to authorization, ingestion, orchestration, infra and contracts. The protocols and invalidation hooks are the integration boundary for those owners.
- The in-memory adapters are not durable authority and should not be used as the production checkpoint store.
- Callers must resolve and pass the current authoritative scope before reads/writes; these adapters do not replace PostgreSQL/PDP authorization checks.

## Main Agent review note

Main Agent added a regression test and fail-closed fix so an invalidation for a
specific document version also invalidates broad corpus-scoped cache entries
(`document_version_id=None`) while preserving unrelated version entries.
