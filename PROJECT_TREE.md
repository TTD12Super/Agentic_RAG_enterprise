# Full project tree

> `.gitkeep` preserves intentional implementation directories.

```text
enterprise-agentic-rag-harness/
├── .codex/
│   ├── agents/
│   │   ├── backend.toml
│   │   ├── devops.toml
│   │   ├── frontend.toml
│   │   ├── ingestion.toml
│   │   ├── orchestration.toml
│   │   ├── qa_tester.toml
│   │   ├── rag_engineer.toml
│   │   └── security.toml
│   ├── config.toml
│   └── README.md
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   └── task.md
│   ├── workflows/
│   │   └── harness-validate.yml
│   └── PULL_REQUEST_TEMPLATE.md
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── middleware/
│   │   │   │   └── .gitkeep
│   │   │   └── routes/
│   │   │       └── .gitkeep
│   │   ├── authorization/
│   │   │   ├── .gitkeep
│   │   │   └── AGENTS.md
│   │   ├── cache/
│   │   │   └── .gitkeep
│   │   ├── core/
│   │   │   └── .gitkeep
│   │   ├── db/
│   │   │   └── migrations/
│   │   │       └── .gitkeep
│   │   ├── evidence/
│   │   │   └── .gitkeep
│   │   ├── feedback/
│   │   │   └── .gitkeep
│   │   ├── governance/
│   │   │   └── .gitkeep
│   │   ├── guardrails/
│   │   │   ├── .gitkeep
│   │   │   └── AGENTS.md
│   │   ├── identity/
│   │   │   └── .gitkeep
│   │   ├── ingestion/
│   │   │   ├── chunkers/
│   │   │   │   └── .gitkeep
│   │   │   ├── parsers/
│   │   │   │   └── .gitkeep
│   │   │   └── AGENTS.md
│   │   ├── integrations/
│   │   │   └── .gitkeep
│   │   ├── knowledge/
│   │   │   └── .gitkeep
│   │   ├── memory/
│   │   │   └── .gitkeep
│   │   ├── models/
│   │   │   └── .gitkeep
│   │   ├── observability/
│   │   │   └── .gitkeep
│   │   ├── orchestration/
│   │   │   ├── nodes/
│   │   │   │   └── .gitkeep
│   │   │   └── AGENTS.md
│   │   ├── prompts/
│   │   │   └── .gitkeep
│   │   ├── rag/
│   │   │   ├── rerankers/
│   │   │   │   └── .gitkeep
│   │   │   ├── retrievers/
│   │   │   │   └── .gitkeep
│   │   │   └── AGENTS.md
│   │   └── tools/
│   │       └── .gitkeep
│   ├── tests/
│   │   └── .gitkeep
│   ├── AGENTS.md
│   └── README.md
├── data/
│   ├── cache/
│   │   └── .gitkeep
│   ├── exports/
│   │   └── .gitkeep
│   ├── processed/
│   │   └── .gitkeep
│   ├── raw/
│   │   └── .gitkeep
│   ├── synthetic/
│   │   └── .gitkeep
│   ├── uploads/
│   │   └── .gitkeep
│   └── README.md
├── docs/
│   ├── architecture/
│   │   ├── blocks/
│   │   │   ├── 01-presentation-layer.md
│   │   │   ├── 02-api-identity.md
│   │   │   ├── 03-authorization.md
│   │   │   ├── 04-security-guardrails.md
│   │   │   ├── 05-agent-orchestration.md
│   │   │   ├── 06-model-management.md
│   │   │   ├── 07-prompt-management.md
│   │   │   ├── 08-rag-engine.md
│   │   │   ├── 09-evidence-verification.md
│   │   │   ├── 10-knowledge-management.md
│   │   │   ├── 11-document-lifecycle.md
│   │   │   ├── 12-data-governance.md
│   │   │   ├── 13-memory-caching.md
│   │   │   ├── 14-integration-layer.md
│   │   │   ├── 15-observability-audit.md
│   │   │   ├── 16-evaluation-feedback.md
│   │   │   └── 17-infrastructure-llmops.md
│   │   ├── decisions/
│   │   │   ├── ADR-0001.md
│   │   │   ├── ADR-0002.md
│   │   │   ├── ADR-0003.md
│   │   │   ├── ADR-0004.md
│   │   │   ├── ADR-0005.md
│   │   │   ├── ADR-TEMPLATE.md
│   │   │   ├── DECISION-REGISTER.md
│   │   │   └── README.md
│   │   ├── workflows/
│   │   │   ├── admin-ingestion.md
│   │   │   └── user-query.md
│   │   └── overview.md
│   ├── contracts/
│   │   ├── admin-management.md
│   │   ├── agent-tools.md
│   │   ├── answer-and-citation.md
│   │   ├── cache-and-memory.md
│   │   ├── chat-and-jobs.md
│   │   ├── CHANGE-PROCESS.md
│   │   ├── document.md
│   │   ├── events-and-audit.md
│   │   ├── identity-and-policy.md
│   │   ├── ingestion.md
│   │   ├── README.md
│   │   └── retrieval.md
│   ├── operations/
│   │   ├── deployment-runbook.md
│   │   ├── incident-response.md
│   │   └── multi-agent-production-workflow.md
│   ├── prompts/
│   │   ├── answer-v1.md
│   │   ├── planner-v1.md
│   │   ├── README.md
│   │   └── system-v1.md
│   ├── rag/
│   │   ├── evaluation-plan.md
│   │   ├── ingestion-design.md
│   │   ├── README.md
│   │   └── retrieval-design.md
│   ├── security/
│   │   ├── authorization-matrix.md
│   │   ├── data-protection.md
│   │   ├── prompt-injection-defense.md
│   │   ├── README.md
│   │   ├── security-test-cases.md
│   │   └── threat-model.md
│   ├── testing/
│   │   ├── golden-dataset-schema.md
│   │   ├── quality-gates.md
│   │   └── README.md
│   ├── agent-collaboration.md
│   ├── file-ownership.md
│   ├── git-worktrees.md
│   └── README.md
├── frontend/
│   ├── public/
│   │   └── .gitkeep
│   ├── src/
│   │   ├── api/
│   │   │   └── .gitkeep
│   │   ├── components/
│   │   │   ├── admin/
│   │   │   │   └── .gitkeep
│   │   │   ├── chat/
│   │   │   │   └── .gitkeep
│   │   │   └── citations/
│   │   │       └── .gitkeep
│   │   ├── features/
│   │   │   ├── auth/
│   │   │   │   └── .gitkeep
│   │   │   ├── conversations/
│   │   │   │   └── .gitkeep
│   │   │   └── documents/
│   │   │       └── .gitkeep
│   │   ├── hooks/
│   │   │   └── .gitkeep
│   │   ├── pages/
│   │   │   └── .gitkeep
│   │   └── types/
│   │       └── .gitkeep
│   ├── AGENTS.md
│   └── README.md
├── harness/
│   ├── build/
│   │   └── README.md
│   ├── checklists/
│   │   ├── phase-0.md
│   │   ├── phase-1.md
│   │   ├── phase-2.md
│   │   ├── phase-3.md
│   │   ├── phase-4.md
│   │   ├── phase-5.md
│   │   ├── phase-6.md
│   │   └── phase-7.md
│   ├── context/
│   │   └── README.md
│   ├── handoffs/
│   │   ├── README.md
│   │   └── TEMPLATE.md
│   ├── reviews/
│   │   └── .gitkeep
│   ├── tasks/
│   │   ├── DEPENDENCIES.md
│   │   ├── README.md
│   │   └── tasks.json
│   ├── build-log.md
│   ├── file-manifest.json
│   └── README.md
├── infra/
│   ├── docker/
│   │   └── .gitkeep
│   ├── monitoring/
│   │   └── .gitkeep
│   ├── scripts/
│   │   └── .gitkeep
│   ├── AGENTS.md
│   └── README.md
├── scripts/
│   ├── .gitkeep
│   └── validate_harness.py
├── tests/
│   ├── contracts/
│   │   └── .gitkeep
│   ├── e2e/
│   │   └── .gitkeep
│   ├── evaluation/
│   │   └── .gitkeep
│   ├── integration/
│   │   └── .gitkeep
│   ├── security/
│   │   └── .gitkeep
│   ├── unit/
│   │   └── .gitkeep
│   ├── AGENTS.md
│   └── README.md
├── .env.example
├── .gitignore
├── AGENTS.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── diagram.md
├── GOALS.md
├── PLANS.md
├── PROJECT_TREE.md
├── PROMPTS.md
├── README.md
└── SECURITY.md
```
