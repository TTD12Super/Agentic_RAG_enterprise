# Directory ownership (coordination convention, not OS permissions)

| Scope | Primary agent | Review |
|---|---|---|
| `backend/app/api`, `backend/app/identity`, `backend/app/db`, `backend/app/observability`, `backend/app/feedback`, `docs/database` | backend | security/ingestion/devops |
| `backend/app/authorization`, `backend/app/guardrails` | security | QA/backend |
| `backend/app/ingestion`, `backend/app/knowledge` | ingestion | security |
| `backend/app/rag`, `backend/app/evidence` | rag_engineer | security/QA |
| `backend/app/orchestration`, `backend/app/tools`, `backend/app/prompts` | orchestration | security |
| `frontend` | frontend | backend/security |
| `infra`, `.github/workflows` | devops | security |
| `tests` | qa_tester | module owner |
| `docs/contracts`, `docs/architecture/decisions`, `harness/tasks/tasks.json` | Main Agent with Project Owner approval | Security and all affected agents review |

A module owner may coordinate exceptions in the task handoff. Do not edit another active agent's files without explicit coordination.

Backend owns database schema and migration definitions. DevOps owns database runtime infrastructure, containers, migration execution and rollback orchestration; Ingestion may propose domain metadata changes but must route migration edits through Backend.

After DB-001 is DONE, the Main Agent assigns later schema changes as new Backend-owned migration tasks; affected work waits for their reviewed completion. Shared directories may have multiple agents only with concrete non-overlapping file assignments.
