# CACHE-001 QA handoff

Status: QA complete; no production, contract, task-registry, frontend, or infra files were changed.

## Focused Graphify query

The existing `graphify-out/graph.json` was queried with:

```text
/tmp/graphify-venv/bin/graphify query "cache memory scoped tenant principal policy epoch document version invalidation TTL deletion fail closed" --budget 1200
```

Result: PASS. Graphify loaded `graphify-out/graph.json` with 3,261 nodes, traversed BFS depth 2, and found 545 nodes; the 1,200-token display showed 32. The relevant neighborhood included `CacheScope`, `ScopedCacheKey`, `InvalidationEvent`, `InMemoryScopedCache`, `memory/store.py`, lifecycle deletion, and policy-epoch paths.

## QA files

- `tests/qa/cache_memory/test_behavior_component.py` — 10 component cases.
- `tests/qa/cache_memory/test_contract_integration.py` — 10 contract/integration cases.
- `tests/qa/cache_memory/test_security_adversarial.py` — 10 adversarial cases.
- `tests/qa/cache_memory/test_e2e_operational.py` — 10 deterministic operational cases.

Coverage includes tenant/principal/policy/version isolation, corpus/index/entitlement partitions, broad and narrow invalidation, TTL and byte/message limits, authenticated last-activity retention, anonymous idle/max-age/retention bounds, deletion, stale/revoked fail-closed writes, redacted representations, provider-neutral protocols, and fake invalidation delivery.

## Exact verification

```text
python3 -m pytest tests/qa/cache_memory -q
40 passed in 0.04s

python3 -m pytest backend/tests/test_cache_memory.py -q
12 passed in 0.01s

python3 -m pytest tests/qa/cache_memory backend/tests/test_cache_memory.py -q
52 passed in 0.03s

git diff --check
passed
```

## Findings and risk

- PASS — all 40 new QA cases passed; no scoped functional defect was observed.
- PASS — all fixtures use synthetic values, deterministic clocks, and fakes; no external service or real document data was used.
- Risk — the tested adapters are intentionally in-memory test/local doubles. PostgreSQL durability, Redis transport, ordered outbox acknowledgement, and real caller wiring remain outside this QA-only scope.

No commit or push was performed.
