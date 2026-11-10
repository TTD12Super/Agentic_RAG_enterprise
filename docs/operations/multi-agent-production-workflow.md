# Multi-agent delivery workflow — from scaffold to production

**Status:** execution plan, not evidence of implementation or permission to deploy. The task registry is authoritative for task status and dependencies. An owner-provided proposal is not a production approval.

## 1. Outcome and boundaries

Deliver the approved single-enterprise MVP: Vercel-hosted frontend, Python/FastAPI backend, separate RAG and ingestion workers, PostgreSQL, private file storage, authorized retrieval and monitoring. The backend/worker production provider, region, model providers and data-processing terms remain owner decisions in `docs/architecture/decisions/DECISION-REGISTER.md`. Student/free profiles are development or demo options, not evidence of production readiness. Figma remains owned and approved by the Project Owner.

## 2. Who does what

| Role | Responsibility | Read before assignment |
|---|---|---|
| Main Agent / Tech Lead | Select READY tasks, resolve minor non-breaking choices, guard shared files, review handoffs and integrate evidence | `AGENTS.md`, `PLANS.md`, `docs/agent-collaboration.md`, `harness/tasks/tasks.json`, decision register |
| Backend | API, identity, database schema/migrations, application audit and telemetry, model gateway, cache | `backend/AGENTS.md`, assigned packet, `docs/database/database.md`, applicable contracts |
| Security | Authorization, guardrails and negative security review | `docs/security/`, `docs/contracts/identity-and-policy.md`, assigned packet |
| Ingestion | Quarantine, parsing, staged indexing and two-review lifecycle | `docs/rag/ingestion-design.md`, document/ingestion contracts, assigned packet |
| RAG Engineer | Authorized retrieval, reranking, evidence and citations | `docs/rag/`, retrieval and citation contracts, assigned packet |
| Orchestration | Bounded LangGraph workflow, approved prompt and read-only tool interfaces | `docs/prompts/`, `docs/contracts/agent-tools.md`, assigned packet |
| Frontend | Approved Figma implementation, API integration, role-specific states and accessibility | `frontend/AGENTS.md`, owner-approved Figma, UI task and contracts |
| DevOps | Disposable test services, infrastructure, deployment, secrets configuration and monitoring platform | `infra/AGENTS.md`, `infra/README.md`, operations runbooks, assigned packet |
| QA Tester | Synthetic fixtures, evaluation, integration/security/E2E and release evidence | `tests/AGENTS.md`, `docs/testing/`, `docs/security/security-test-cases.md` |

There are eight specialist profiles plus the Main Agent. Activate only the agents required by eligible tasks, with separate contexts and bounded task packets. The configured ceiling of 10 is a planning limit, not proof that the installed runtime can launch ten agents: verify supported settings and actual capacity at execution time. Agents do not share conversation memory; pass decisions and evidence through files and handoffs. The Main Agent prevents concurrent edits to the same file, including migrations, shared tests and contracts; serialize or explicitly partition work. `requested_agents` is a requested count, not an automatic scheduler.

## 3. Preflight and approvals

1. Main Agent runs `python3 scripts/validate_harness.py`, checks actual runtime/subagent availability, reads `tasks.json` and lists the currently READY tasks. Do not mark a task DONE from a document or mock alone.
2. Review `ARCH-001`, requirements, database proposal, role policy and `CONTRACT-001`. The Project Owner accepts required architecture and contracts; Security and affected agents review. Unresolved `DEC-*` decisions block only the affected work or release stage. Record owner decisions and evidence in the register and handoffs.
3. DevOps produces `INFRA-002`: inventory accounts, billing, regions, provider terms, quotas, domains, DNS, TLS, access, environment variables, secret storage and spending caps. The agent reports what is needed; the Project Owner creates accounts, supplies secrets through the approved secret manager and performs account verification. Never paste keys into Git, issues, prompts or handoffs. Report required variable names and verification result, not values.
4. Project Owner supplies the approved Figma file and confirms which screens and states are in scope. Missing screens or ambiguous interactions are escalated rather than invented.
5. Each phase requires the Project Owner's existing phase approval. Starting work, Git operations, deployment and paid resources remain separately governed by `AGENTS.md` and `PLANS.md`.

## 4. Execution order

The table is a guide; `depends_on` and owner-approved gates control the actual order. Within a phase, parallelize independent READY tasks only after the Main Agent assigns non-overlapping concrete files or subdirectories inside each task's allowed write paths. Shared parent directories such as `backend/tests` or `harness/handoffs` do not by themselves prevent parallel work. Reserve each task's own handoff file; serialize edits to shared fixtures, migrations, configuration or contracts. If a file cannot be partitioned safely, assign one writer or run the tasks serially.

| Stage | Tasks and handoff | Required evidence before continuing |
|---|---|---|
| 0 — Architecture and contracts | Main Agent `ARCH-001`; Security reviews `CONTRACT-001`; Owner approves shared contracts | Approved ADRs/contracts and documented open decisions; no invented provider or policy |
| 1 — Foundations | Backend `BACKEND-BOOT-001`, `DB-001`, `IDENT-001`, `AUDIT-001`; Frontend `FRONTEND-BOOT-001`; Security `AUTH-001`; DevOps `INFRA-BOOT-001`, `INFRA-001`, `INFRA-002`, `INFRA-003`; QA `EVAL-PREP-001` | DevOps supplies isolated PostgreSQL through `INFRA-BOOT-001` before DB-001; Backend proves real upgrade/rollback. Audit and monitoring test real identity/API telemetry and synthetic future-signal configurations; live source-wide tracing waits for release. Policy negative tests are checked at their gate. |
| 2 — Documents | Backend `MODEL-001`, `ADMIN-API-001`; Ingestion `KNOW-001`, `ING-001` | Synthetic PDF/DOCX/XLSX tests, malware/limits, two reviews, version activation, account/document API authorization, failure recovery and revoked content exclusion |
| 3 — Retrieval and evaluation | RAG `RAG-001`, `RAG-002`, `EVID-001`, `ANSWER-BASE-001`; Orchestration `PROMPT-001`; Security `GUARD-001`; QA `EVAL-001` | Direct integrated answer baseline before Golden Dataset evaluation, policy, PostgreSQL, index and source retrieval; denied-source evidence; no invented quality claims |
| 4 — Agentic workflow and chat API | Orchestration `ORCH-001`; Backend `CACHE-001`, `CHAT-001`, `DASH-API-001` with Security review | Approved read-only tools, bounded rounds/time/cost; real Core/worker job, conversation privacy, feedback, citation endpoints, role-limited dashboard, durable queue and maintenance tests |
| 5 — Website | Frontend `UI-001` using approved Figma, Backend and QA | Authenticated and anonymous journeys, role restrictions, maintenance, citations, accessibility and browser E2E |
| 6 — Release | QA `RELEASE-001`; Backend, DevOps and Security supply operational evidence | Cache revocation, real end-to-end tracing, `INFRA-003` monitoring, backup/restore, security and load evidence, owner go/no-go |
| 7 — Optional | `INT-001` only after separate approval | No optional connector is a prerequisite for MVP release |

For each task: Main Agent checks dependencies and the phase gate, selects the minimum agent count, sends the role-specific packet and expected handoff, then reviews actual changed paths and executed tests. A task with unmet acceptance checks is `BLOCKED` or `READY_FOR_INTEGRATION`, not `DONE`. Development integration can use synthetic data; production integration is a separate gate.

At the end of each phase, after all required tasks have acceptance evidence and the phase gate is satisfied, the Main Agent creates one phase commit and pushes it to the configured `main` remote. The commit message must identify the phase or milestone without using internal tool/vendor names. A failed gate, unresolved major decision or incomplete evidence prevents the phase push; this does not authorize deployment.

For each implementation goal, the QA/Test Agent must produce a four-family test package: behavior/component, contract/integration, security/adversarial and E2E/operational, with at least 10 materially different cases per family. The Test Agent reports to the Main Agent, who reviews and records minor approvals in the handoff. Only material decisions, conflicting requirements or an unclear implementation option are escalated to the Project Owner; this does not waive the existing architecture, contract, security, deployment or release approvals.

If a later task needs a schema change after DB-001 is DONE, its agent records a request and marks the dependent work BLOCKED. The Main Agent creates a new Backend-owned migration task with the exact schema scope, dependencies and real upgrade/rollback and isolation tests, updates the registry, dependency graph and phase checklist, and makes the affected task depend on it. Backend owns the migration; DevOps only supplies/runtime-executes infrastructure. Do not reopen or silently rewrite the completed DB-001 history. Escalate changes to approved security, data policy or contracts to the Project Owner.

## 5. Production gate

Before asking for deployment authorization, prepare a reviewable release candidate with versioned source, configuration inventory, migration/rollback plan, release notes, test commands and results. At minimum verify:

- Real identity, MFA, PUBLIC/INTERNAL, explicit-deny and Chairman/employee/admin negative cases; no other user's conversation body exposed to administrators.
- Two-review publication, quarantine, deletion/revocation, queue maintenance/resume, cache invalidation and current-version citations. Failed/denied paths must not leak content.
- E2E browser flows on the approved Figma, API contract checks, synthetic golden dataset and injection tests. Record model/provider, dataset version, latency, cost and thresholds; unapproved targets are not SLAs.
- Isolated dev/staging/production credentials and data, private networks, encrypted storage, least privilege, approved provider egress, secret rotation, TLS/DNS, alert routing and incident ownership.
- Real backup and restore with tombstone replay, tested migration upgrade/rollback, failure recovery and release rollback. Measure RPO/RTO and perform load tests using the approved workload and limits; do not claim 500-session capacity without evidence.
- `DEC-001`–`DEC-014` and other relevant pending choices are reviewed per affected release scope; no row is marked approved without owner evidence. Missing mandatory evidence means **NO-GO**.

QA records pass/fail/not-run, residual risk, links to logs/reports without secrets, and a proposed go/no-go. Main Agent checks the evidence and asks the Project Owner for the release decision and deployment authorization. DevOps deploys only after that authorization; verify post-deploy smoke tests, alerts and rollback readiness. A failed smoke test triggers the approved rollback/incident process, not an unsupported success claim.

## 6. Handoff format

Every task handoff records task ID, agent, approved input versions, changed files, exact executed commands and results, integration boundaries, unresolved decisions, security/data impact, and next eligible task. Use `harness/handoffs/TEMPLATE.md`; never store private documents, raw secrets or private conversation bodies in the handoff.
