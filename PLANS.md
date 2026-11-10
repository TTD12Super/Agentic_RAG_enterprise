# PLANS — Implementation roadmap & gates

The machine-readable task graph is `harness/tasks/tasks.json`; this document explains phases but **is not a competing status tracker**. Complete a phase only when its corresponding quality gate is signed off.

| Phase | Outcome | Primary owners | Gate |
|---|---|---|---|
| 0 | Harness + contract architecture | tech lead, QA | DAG valid; v1.0 contracts and 40-case contract tests accepted; owner approval |
| 1 | Runtime bootstraps, data governance, identity, policy, infrastructure, audit | backend, frontend, security, devops | backend/frontend build baselines, documented RBAC/ABAC/ACL policies + negative tests |
| 2 | Document ingestion, indexing and administration APIs | ingestion, backend | quarantine→approved→active; versioning, ACL and admin API integration |
| 3 | Secure Hybrid RAG and direct answer baseline + evaluation | rag, QA | reproducible answer metrics, no forbidden-source leakage in test suite |
| 4 | LangGraph, chat and dashboard APIs, durable jobs, memory and cache | orchestration, backend | bounded loops, authorized tools, isolated history, feedback and job integration |
| 5 | Admin + user UI | frontend, backend | admin / chairman / regular-user E2E scenarios |
| 6 | MVP release review | QA, backend, security, devops | E2E, revocation, monitoring and recovery evidence; owner go/no-go |
| 7 | Enterprise integration (optional) | backend, devops | source-specific authorization and approval controls |

## Dependency rules
1. Contract accepted → independent implementation with mocks allowed.
2. Implementations READY_FOR_INTEGRATION → integration tests → DONE.
3. No dependent task can become READY until every dependency is DONE. The current task schema has no contract-only exception.
4. Agent stops and reports `BLOCKED` rather than inventing a dependency.

## Scope of Phase 0
Produce schema and interface agreement first; do not commit to library versions or costly production infrastructure until architecture decisions are reviewed.

## Owner Approval Points

Explicit Project Owner approval is required:

- Before adding external services/paid dependencies.
- Before broadening document access or enabling side-effecting tools.
- Before merging phases into default branch or deploying.
- Before starting a new implementation phase.
- Before changing approved architecture or critical contracts.
- Before changing security or authorization policies.
- Before any Git commit, push, merge, or deployment.

## Task completion rules

- READY_FOR_INTEGRATION means implementation is complete,
  but required integration tests are pending.
- A task becomes DONE only after its acceptance criteria
  and required integration checks have passed.

Phase completion does not automatically authorize
the next phase.

See AGENTS.md for execution and approval rules.

