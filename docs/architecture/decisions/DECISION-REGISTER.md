# Decision Register — Project Owner Escalations

This register lists unresolved choices that agents must not settle autonomously. The Main Agent may prepare options and evidence; the Project Owner makes the final decision. A task is `BLOCKED` when it needs one of these decisions before its affected stage can be accepted.

| ID | Decision | Status | Affected tasks | Blocks | Evidence for Owner review |
|---|---|---|---|---|---|
| DEC-001 | Primary and fallback LLM, embedding and reranker providers/models | PENDING | `MODEL-001`, `ING-001`, `ANSWER-BASE-001`, `EVAL-001`, `RELEASE-001` | Provider implementation, egress and production release | Quality, latency, cost, data-processing and fallback comparison |
| DEC-002 | Cloud provider, region, topology and managed-service profile | PENDING | `INFRA-002`, `RELEASE-001`, `INT-001` | Production deployment and availability claims | Cost, residency, network, backup, capacity and student/demo comparison |
| DEC-003 | Trace and redacted operational log backend | PENDING | `INFRA-003`, `AUDIT-001`, `RELEASE-001` | Production telemetry retention and investigation workflow | Privacy, access control, retention, cost and export behavior |
| DEC-004 | Approved alert recipients and notification channels | PENDING | `INFRA-003`, `RELEASE-001` | Production alert routing and incident readiness | On-call ownership, severity policy and notification test |
| DEC-005 | Final retention, deletion and legal-hold policy | APPROVED | `DB-001`, `AUDIT-001`, `CACHE-001`, `RELEASE-001` | Production data-lifecycle guarantee | Main Agent decision under Project Owner delegation; baseline retention/tombstone rules recorded in contract v1.0 |
| DEC-006 | Queue priority, capacity profile and benchmark thresholds | PENDING | `EVAL-PREP-001`, `EVAL-001`, `RELEASE-001` | Capacity and quality claims | Declared workload, corpus, model settings and measured benchmark |
| DEC-007 | Maintenance ceiling and provider-specific pause/resume behavior | APPROVED | `ING-001`, `ORCH-001`, `RELEASE-001` | Final maintenance/recovery behavior | Main Agent decision under Project Owner delegation; 30-minute approval expiry, 60-minute watchdog and safe checkpoint rules recorded in contract v1.0 |
| DEC-008 | Final backend runtime, Rust/Python ownership and repository migration scope | PENDING | `ARCH-001`, `INFRA-001`, `RELEASE-001` | Runtime migration and module ownership | Benchmark, migration plan, compatibility and owner approval |
| DEC-009 | Authoritative database, vector/lexical search, object storage, cache/checkpoint stores and data ownership | APPROVED | `DB-001`, `KNOW-001`, `CACHE-001`, `INFRA-001`, `RELEASE-001` | Persistence and retrieval topology | Main Agent decision under Project Owner delegation; PostgreSQL authority, Qdrant index projection, private object storage and optional Redis recorded in contract v1.0 |
| DEC-010 | Cross-language transport, worker authentication and revocation-aware trust boundary | APPROVED | `CONTRACT-001`, `INFRA-001`, `IDENT-001`, `AUTH-001` | Protected Core/worker integration | Main Agent decision under Project Owner delegation; TLS, short-lived asymmetric service JWT, audience/job binding, expiry and jti replay checks recorded in contract v1.0 |
| DEC-011 | Role/department/document ACL precedence, Chairman/Admin exceptions and signed access scope | APPROVED | `AUTH-001`, `ADMIN-API-001`, `RAG-001`, `EVID-001`, `ANSWER-BASE-001`, `UI-001` | Fail-closed authorization behavior | Owner-provided RBAC + department + document ACL + default deny + explicit deny precedence; machine-checkable scope rules recorded in contract v1.0 |
| DEC-012 | Upload validation, metadata, review actors, retention and permanent-delete safeguards | APPROVED | `DB-001`, `KNOW-001`, `ING-001`, `ADMIN-API-001`, `RELEASE-001` | Document lifecycle acceptance | Main Agent decision under Project Owner delegation; same admin allowed for two independent reviews, atomic publication and retention/legal-hold checks recorded in contract v1.0 |
| DEC-013 | Response measurement, RPO/RTO and operational alert thresholds | PENDING | `EVAL-PREP-001`, `EVAL-001`, `INFRA-003`, `RELEASE-001` | Verifiable performance and recovery claims | Workload definition, restore drills and alert tests |
| DEC-014 | Target repository layout and synchronized contract/ADR/module/task migration plan | APPROVED | `ARCH-001`, `CONTRACT-001`, `INFRA-001`, `RELEASE-001` | Controlled implementation migration | Main Agent decision under Project Owner delegation; current modular-monolith repository remains authoritative for MVP; Rust remains benchmark-gated |

## Escalation rule

- Agents may document options and run approved, reversible evidence-gathering work.
- If no approved option exists, options have material trade-offs, or the choice changes shared behavior or MVP scope, the affected task is `BLOCKED`.
- The Main Agent presents the alternatives and recommendation to the Project Owner.
- Rows marked `APPROVED` above were decided by the Main Agent under the Project Owner delegation recorded on 2026-11-10 and are reflected in contract v1.0. Cloud/provider, model, alert-recipient and benchmark/release rows remain `PENDING`.
