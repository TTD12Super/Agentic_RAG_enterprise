# Decision Register — Project Owner Escalations

This register lists unresolved choices that agents must not settle autonomously. The Main Agent may prepare options and evidence; the Project Owner makes the final decision. A task is `BLOCKED` when it needs one of these decisions before its affected stage can be accepted.

| ID | Decision | Status | Affected tasks | Blocks | Evidence for Owner review |
|---|---|---|---|---|---|
| DEC-001 | Primary and fallback LLM, embedding and reranker providers/models | PENDING | `MODEL-001`, `ING-001`, `ANSWER-BASE-001`, `EVAL-001`, `RELEASE-001` | Provider implementation, egress and production release | Quality, latency, cost, data-processing and fallback comparison |
| DEC-002 | Cloud provider, region, topology and managed-service profile | PENDING | `INFRA-002`, `RELEASE-001`, `INT-001` | Production deployment and availability claims | Cost, residency, network, backup, capacity and student/demo comparison |
| DEC-003 | Trace and redacted operational log backend | PENDING | `INFRA-003`, `AUDIT-001`, `RELEASE-001` | Production telemetry retention and investigation workflow | Privacy, access control, retention, cost and export behavior |
| DEC-004 | Approved alert recipients and notification channels | PENDING | `INFRA-003`, `RELEASE-001` | Production alert routing and incident readiness | On-call ownership, severity policy and notification test |
| DEC-005 | Final retention, deletion and legal-hold policy | PENDING | `DB-001`, `AUDIT-001`, `CACHE-001`, `RELEASE-001` | Production data-lifecycle guarantee | Data inventory, legal hold, restore/tombstone and compliance review |
| DEC-006 | Queue priority, capacity profile and benchmark thresholds | PENDING | `EVAL-PREP-001`, `EVAL-001`, `RELEASE-001` | Capacity and quality claims | Declared workload, corpus, model settings and measured benchmark |
| DEC-007 | Maintenance ceiling and provider-specific pause/resume behavior | PENDING | `ING-001`, `ORCH-001`, `RELEASE-001` | Final maintenance/recovery behavior | Failure injection, checkpoint safety, provider timeout and recovery evidence |
| DEC-008 | Final backend runtime, Rust/Python ownership and repository migration scope | PENDING | `ARCH-001`, `INFRA-001`, `RELEASE-001` | Runtime migration and module ownership | Benchmark, migration plan, compatibility and owner approval |
| DEC-009 | Authoritative database, vector/lexical search, object storage, cache/checkpoint stores and data ownership | PENDING | `DB-001`, `KNOW-001`, `CACHE-001`, `INFRA-001`, `RELEASE-001` | Persistence and retrieval topology | Isolation, recovery, cost and operational comparison |
| DEC-010 | Cross-language transport, worker authentication and revocation-aware trust boundary | PENDING | `CONTRACT-001`, `INFRA-001`, `IDENT-001`, `AUTH-001` | Protected Core/worker integration | Versioned schemas, identity lifecycle and negative-path tests |
| DEC-011 | Role/department/document ACL precedence, Chairman/Admin exceptions and signed access scope | PENDING | `AUTH-001`, `ADMIN-API-001`, `RAG-001`, `EVID-001`, `ANSWER-BASE-001`, `UI-001` | Fail-closed authorization behavior | Authorization matrix and permission-negative tests |
| DEC-012 | Upload validation, metadata, review actors, retention and permanent-delete safeguards | PENDING | `DB-001`, `KNOW-001`, `ING-001`, `ADMIN-API-001`, `RELEASE-001` | Document lifecycle acceptance | Format fixtures, review workflow and deletion/hold tests |
| DEC-013 | Response measurement, RPO/RTO and operational alert thresholds | PENDING | `EVAL-PREP-001`, `EVAL-001`, `INFRA-003`, `RELEASE-001` | Verifiable performance and recovery claims | Workload definition, restore drills and alert tests |
| DEC-014 | Target repository layout and synchronized contract/ADR/module/task migration plan | PENDING | `ARCH-001`, `CONTRACT-001`, `INFRA-001`, `RELEASE-001` | Controlled implementation migration | Repository comparison, dependency impact and owner approval |

## Escalation rule

- Agents may document options and run approved, reversible evidence-gathering work.
- If no approved option exists, options have material trade-offs, or the choice changes shared behavior or MVP scope, the affected task is `BLOCKED`.
- The Main Agent presents the alternatives and recommendation to the Project Owner.
- No row is changed to `APPROVED` without explicit Project Owner evidence. Approval must then be reflected in the relevant ADR, contract, task handoff and dependency status.
