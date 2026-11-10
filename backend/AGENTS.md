# Backend scoped instructions

Follow root AGENTS.md, `docs/contracts/`, ADRs and assigned task IDs. Python/FastAPI modular monolith; type-annotate public surfaces; keep I/O, domain policy and services separate. No business-specific document assumptions.

- PostgreSQL holds authoritative identities, document lifecycle, permissions and citations; Qdrant is a derived index.
- Reuse policy service through explicit interfaces; do not pass authenticated principal from model/user text.
- Database migrations have one coordinated owner at a time.
- Implement typed structured errors and async I/O where appropriate.
- Add unit and integration tests for negative/timeout paths.
