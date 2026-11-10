# Backend — Enterprise Agentic RAG

## 1. Overview

The Backend provides APIs, identity management, authorization, persistence, and service integration for the Enterprise Agentic RAG system.

It serves as the authoritative layer for access control, data integrity, and business logic.

**Status:** Runtime shell implemented; feature modules remain task-scoped.

## 2. Technology Stack

- Language: Python
- Framework: FastAPI
- Primary Database: PostgreSQL
- Vector Database: Qdrant
- Cache: Redis (optional)
- Document Storage: Object storage
- Architecture: Modular Monolith
- Other libraries: Follow approved architecture decisions.

## 3. Project Structure

```text
backend/
├── app/
│   ├── api/             # HTTP routes and middleware
│   ├── core/            # Application configuration
│   ├── identity/        # Authentication and identity
│   ├── authorization/   # RBAC, ABAC, ACL enforcement
│   ├── db/              # Database and migrations
│   ├── ingestion/       # Document processing
│   ├── knowledge/       # Document metadata and lifecycle
│   ├── rag/             # Retrieval and ranking
│   ├── evidence/        # Citation verification
│   ├── orchestration/   # Agent workflows
│   ├── guardrails/      # Security guardrails
│   ├── integrations/    # External services
│   ├── models/          # Model adapters
│   ├── prompts/         # Prompt management
│   ├── tools/           # Tool integration
│   ├── memory/          # Conversation memory
│   ├── cache/           # Application caching
│   ├── governance/      # Data governance
│   ├── observability/   # Logging and monitoring
│   └── feedback/        # Feedback processing
├── tests/
├── AGENTS.md
└── README.md
```

Directories represent planned module boundaries and may not yet contain implementations.

## Local runtime commands

Run these commands from the repository root after creating a local environment:

```bash
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -e 'backend[dev]'
backend/.venv/bin/python -m compileall backend
backend/.venv/bin/python -m pytest backend/tests

For the Backend-owned migration runner, install the database extra and use the
disposable PostgreSQL service from infra/docker/postgres-test.compose.yml:

    backend/.venv/bin/python -m pip install -e 'backend[db]'
    export DB001_DATABASE_URL='postgresql+psycopg://enterprise_rag_test:synthetic_only_not_secret@127.0.0.1:55432/enterprise_rag_test'
    backend/.venv/bin/alembic -c backend/app/db/alembic.ini upgrade head
    backend/.venv/bin/alembic -c backend/app/db/alembic.ini downgrade base

Only synthetic disposable credentials belong in local commands. Production
database URLs must come from the approved secret-management path.
```

Start the shell locally from the repository root with:

```bash
backend/.venv/bin/python -m uvicorn backend.app.main:app --reload
```

The only route in this task is `GET /healthz`, which checks process liveness
without contacting PostgreSQL, Qdrant, Redis, object storage or an LLM.

`.env.example` lists configuration names only. Copy it to `.env` only for
local configuration; never commit real credentials.

## 4. Architecture & Conventions

- Follow the approved modular monolith architecture.
- Maintain clear separation of concerns.
- Keep API routes separate from business logic.
- Reuse existing services and abstractions.
- Follow accepted API and database contracts.
- Enforce authorization through trusted backend components.
- Preserve tenant isolation and document access controls.
- Follow established error handling and logging conventions.
- Do not introduce unnecessary dependencies.
- Do not silently modify shared interfaces or schemas.
- Backend owns PostgreSQL schema and migration definitions through `DB-001`. Ingestion and other modules propose database changes through the Backend owner; DevOps owns only runtime infrastructure and migration execution.

## 5. Development & Testing

Before implementation:

1. Inspect existing modules and dependencies.
2. Read the assigned task and acceptance criteria.
3. Verify upstream dependencies and accepted contracts.
4. Discover existing APIs, services, and database models.
5. Reuse existing implementations where appropriate.
6. Implement only the approved task scope.
7. Run relevant unit, integration, contract, and security tests.
8. Report actual results and integration readiness.

Use development and testing commands defined by the actual project configuration.

Do not assume scripts, entry points, or services exist without verification.

## 6. References

- `../AGENTS.md` — Repository governance.
- `AGENTS.md` — Backend-specific instructions.
- `../docs/architecture/` — System architecture.
- `../docs/contracts/` — API and interface contracts.
- `../docs/security/` — Security and authorization.
- `../docs/rag/` — Retrieval and ingestion design.
- `../docs/testing/` — Testing standards.
- `../docs/git-worktrees.md` — Git governance.
- `../harness/tasks/tasks.json` — Tasks and dependencies.
