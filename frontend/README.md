# Frontend — Enterprise Agentic RAG

## 1. Overview

The Frontend provides user interfaces for authentication, enterprise knowledge chat, document management, conversation history, and authorized administrative operations.

Backend services remain responsible for authentication and authorization enforcement.

**Status:** Frontend bootstrap baseline; product screens are deferred to `UI-001`.

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

Copy `.env.example` to `.env.local` when a local API URL is needed. `VITE_*` values are browser-visible configuration, never API keys or other secrets. The shell does not call the backend yet.

### Contract boundary

The shell follows the approved v1 contract and `docs/design/IMPLEMENTATION-BOUNDARY.md`: canonical role identifiers, backend-authoritative authorization, durable-job polling, and no MVP token streaming. Figma remains the visual source of truth; this task adds no product feature or API integration.

The later frontend implementation goal must provide the required four test families with at least 10 materially different cases per family (40 cases total): behavior/component, contract/integration, security/adversarial, and E2E/operational. This bootstrap only proves the shell renders; it does not claim those later feature gates.

## 6. References

- `../AGENTS.md` — Repository governance.
- `AGENTS.md` — Frontend-specific instructions.
- `../docs/design/` — Figma and UI specifications.
- `../docs/contracts/` — API contracts.
- `../docs/architecture/` — System architecture.
- `../docs/testing/` — Testing standards.
- `../docs/git-worktrees.md` — Git governance.
- `../harness/tasks/tasks.json` — Tasks and dependencies.
