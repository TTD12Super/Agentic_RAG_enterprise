# Frontend — Enterprise Agentic RAG

## 1. Overview

The Frontend provides user interfaces for authentication, enterprise knowledge chat, document management, conversation history, and authorized administrative operations.

Backend services remain responsible for authentication and authorization enforcement.

**Status:** `UI-001` shell implemented; chat API-client wiring is integrated with the local backend/RAG path.

## 2. Technology Stack

- Framework: React
- Language: TypeScript
- Backend: FastAPI
- UI Design: Figma (`docs/design/`)
- Build: Vite
- Tests: Vitest + Testing Library

## 3. Project Structure

```text
frontend/
├── public/           # Static assets
├── src/
│   ├── api/          # Backend API integration
│   ├── components/   # Reusable UI components
│   ├── features/     # Feature-specific logic
│   ├── hooks/        # Custom React hooks
│   ├── pages/        # Application pages
│   └── types/        # Shared TypeScript types
├── AGENTS.md
└── README.md
```

## 4. Architecture & Conventions

- Follow feature-oriented architecture.
- Reuse existing components.
- Keep API integration separate from UI presentation.
- Follow accepted API contracts.
- Follow approved Figma designs.
- Do not invent backend functionality.
- Treat backend authorization as authoritative.
- Follow existing coding conventions.

## 5. Development & Testing

Before implementation:

1. Inspect existing code and dependencies.
2. Read the assigned task and applicable contracts.
3. Review relevant Figma specifications.
4. Implement only the approved scope.
5. Run relevant tests, lint, and build checks.

Use commands defined in the project's `package.json`.

Do not assume scripts exist before verifying them.

### Local commands

```bash
npm install
npm run dev
npm run typecheck
npm run lint
npm test
npm run build
```

Copy `.env.example` to `.env.local` when a local API URL is needed. `VITE_*` values are browser-visible configuration, never API keys or other secrets. Vite proxies `/api` to `http://127.0.0.1:8000` during local development; set `VITE_DEV_BACKEND_URL` to override it.

### Contract boundary

The shell follows the approved v1 contract and `docs/design/IMPLEMENTATION-BOUNDARY.md`: canonical role identifiers, backend-authoritative authorization, durable-job polling, and no MVP token streaming. The chat composer now calls the local `/api/v1` conversation and query-job endpoints; Figma remains the visual source of truth.

The UI-001 gate provides the four required QA families with at least 10 materially different cases per family (40 cases total) in `tests/qa/frontend_boot`, plus 10 Vitest interaction tests and manual browser visual QA. Admin screens still use fixtures until their API clients are connected.

## 6. References

- `../AGENTS.md` — Repository governance.
- `AGENTS.md` — Frontend-specific instructions.
- `../docs/design/` — Figma and UI specifications.
- `../docs/contracts/` — API contracts.
- `../docs/architecture/` — System architecture.
- `../docs/testing/` — Testing standards.
- `../docs/git-worktrees.md` — Git governance.
- `../harness/tasks/tasks.json` — Tasks and dependencies.
