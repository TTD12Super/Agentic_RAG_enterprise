# Task Dependencies — Source: `tasks.json`

This diagram describes the dependency graph in `harness/tasks/tasks.json`. **Only `tasks.json` is the source of truth for task dependencies and statuses.** Update it first; keep this document synchronized. This file does not schedule agents automatically.

## Dependency Graph

An arrow `A → B` means **B depends on A**. All direct `depends_on` edges are shown below.

```mermaid
flowchart TD
  subgraph PHASE_0["Phase 0: Architecture & Contracts"]
    ARCH_001["ARCH-001"]
    CONTRACT_001["CONTRACT-001"]
  end

  subgraph PHASE_1["Phase 1: Foundations, Security & Evaluation Preparation"]
    BACKEND_BOOT_001["BACKEND-BOOT-001"]
    FRONTEND_BOOT_001["FRONTEND-BOOT-001"]
    INFRA_BOOT_001["INFRA-BOOT-001"]
    DB_001["DB-001"]
    INFRA_001["INFRA-001"]
    INFRA_002["INFRA-002"]
    INFRA_003["INFRA-003"]
    IDENT_001["IDENT-001"]
    AUTH_001["AUTH-001"]
    AUDIT_001["AUDIT-001"]
    EVAL_PREP_001["EVAL-PREP-001"]
  end

  subgraph PHASE_2["Phase 2: Knowledge & Ingestion"]
    MODEL_001["MODEL-001"]
    KNOW_001["KNOW-001"]
    ING_001["ING-001"]
    ADMIN_API_001["ADMIN-API-001"]
  end

  subgraph PHASE_3["Phase 3: Secure Hybrid RAG & Evaluation"]
    RAG_001["RAG-001"]
    RAG_002["RAG-002"]
    PROMPT_001["PROMPT-001"]
    GUARD_001["GUARD-001"]
    EVID_001["EVID-001"]
    ANSWER_BASE_001["ANSWER-BASE-001"]
    EVAL_001["EVAL-001"]
  end

  subgraph PHASE_4["Phase 4: Agent Orchestration"]
    ORCH_001["ORCH-001"]
    CACHE_001["CACHE-001"]
    CHAT_001["CHAT-001"]
    DASH_API_001["DASH-API-001"]
  end

  subgraph PHASE_5["Phase 5: User Interface"]
    UI_001["UI-001"]
  end

  subgraph PHASE_6["Phase 6: MVP Release"]
    RELEASE_001["RELEASE-001"]
  end

  subgraph PHASE_7["Phase 7: Optional Enterprise Integration"]
    INT_001["INT-001"]
  end

  ARCH_001 --> CONTRACT_001
  CONTRACT_001 --> BACKEND_BOOT_001
  CONTRACT_001 --> FRONTEND_BOOT_001
  CONTRACT_001 --> INFRA_BOOT_001
  CONTRACT_001 --> INFRA_001
  CONTRACT_001 --> DB_001
  BACKEND_BOOT_001 --> DB_001
  INFRA_BOOT_001 --> DB_001
  BACKEND_BOOT_001 --> INFRA_001
  DB_001 --> INFRA_001
  FRONTEND_BOOT_001 --> INFRA_001
  BACKEND_BOOT_001 --> IDENT_001
  BACKEND_BOOT_001 --> MODEL_001
  BACKEND_BOOT_001 --> PROMPT_001
  FRONTEND_BOOT_001 --> UI_001
  CHAT_001 --> UI_001
  ADMIN_API_001 --> UI_001
  DASH_API_001 --> UI_001
  INFRA_001 --> INFRA_003
  INFRA_002 --> INFRA_003
  AUDIT_001 --> INFRA_003
  CONTRACT_001 --> IDENT_001
  IDENT_001 --> AUTH_001
  CONTRACT_001 --> AUTH_001
  IDENT_001 --> AUDIT_001
  INFRA_001 --> AUDIT_001
  CONTRACT_001 --> EVAL_PREP_001
  INFRA_001 --> MODEL_001
  CONTRACT_001 --> KNOW_001
  INFRA_001 --> KNOW_001
  DB_001 --> KNOW_001
  AUTH_001 --> ING_001
  KNOW_001 --> ING_001
  MODEL_001 --> ING_001
  AUDIT_001 --> ING_001
  ING_001 --> ADMIN_API_001
  IDENT_001 --> ADMIN_API_001
  AUTH_001 --> ADMIN_API_001
  DB_001 --> ADMIN_API_001
  ING_001 --> RAG_001
  AUTH_001 --> RAG_001
  RAG_001 --> RAG_002
  CONTRACT_001 --> PROMPT_001
  AUTH_001 --> GUARD_001
  PROMPT_001 --> GUARD_001
  RAG_002 --> EVID_001
  PROMPT_001 --> EVID_001
  RAG_002 --> ANSWER_BASE_001
  EVID_001 --> ANSWER_BASE_001
  PROMPT_001 --> ANSWER_BASE_001
  MODEL_001 --> ANSWER_BASE_001
  GUARD_001 --> ANSWER_BASE_001
  RAG_002 --> EVAL_001
  EVID_001 --> EVAL_001
  GUARD_001 --> EVAL_001
  EVAL_PREP_001 --> EVAL_001
  ANSWER_BASE_001 --> EVAL_001
  EVAL_001 --> ORCH_001
  EVID_001 --> ORCH_001
  AUTH_001 --> ORCH_001
  GUARD_001 --> ORCH_001
  IDENT_001 --> UI_001
  ING_001 --> UI_001
  ORCH_001 --> UI_001
  ORCH_001 --> CACHE_001
  AUTH_001 --> CACHE_001
  ORCH_001 --> CHAT_001
  CACHE_001 --> CHAT_001
  IDENT_001 --> CHAT_001
  DB_001 --> CHAT_001
  CHAT_001 --> DASH_API_001
  ADMIN_API_001 --> DASH_API_001
  EVAL_001 --> DASH_API_001
  INFRA_003 --> DASH_API_001
  UI_001 --> RELEASE_001
  CACHE_001 --> RELEASE_001
  AUDIT_001 --> RELEASE_001
  INFRA_003 --> RELEASE_001
  EVAL_001 --> RELEASE_001
  GUARD_001 --> RELEASE_001
  RELEASE_001 --> INT_001
```

## Contract-First Parallel Work

- Shared contracts must be reviewed and **approved** before dependent integrations use them.
- Independent `READY` tasks may run in parallel with separate file ownership/worktrees. Local mocks may support contract-based testing but do not prove real integration.
- An implementation may reach `READY_FOR_INTEGRATION`; it becomes `DONE` only after required acceptance checks and real integration evidence are reviewed.
- A downstream task is not `READY` until every listed dependency is `DONE`. The current JSON schema lists task IDs only; it does **not** define a `contract_only` exception.
- When blocked, the agent reports the blocking task IDs, reason, and a handoff using `harness/handoffs/TEMPLATE.md`; the Main Agent may assign other independent `READY` work.

## Coordination and Approval

- The Main Agent coordinates task assignments and reviews evidence; `tasks.json` is updated only after review.
- Passing a phase gate does **not** authorize the next phase automatically; explicit Project Owner approval is required.
- `RELEASE-001` is the Phase 6 **MVP release review**. `INT-001` is Phase 7 **optional integration**, and must not block MVP release.
- Keep contract approval, security review, and Git approvals consistent with `AGENTS.md`, `PLANS.md`, and `docs/contracts/CHANGE-PROCESS.md`.
