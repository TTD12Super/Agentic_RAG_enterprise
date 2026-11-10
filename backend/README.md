# Backend — Enterprise Agentic RAG

## 1. Overview

The Backend provides APIs, identity management, authorization, persistence, and service integration for the Enterprise Agentic RAG system.

It serves as the authoritative layer for access control, data integrity, and business logic.

**Status:** Development harness; implementation pending.

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
