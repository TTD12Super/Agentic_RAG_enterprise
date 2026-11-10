# Handoff — ARCH-001 / Main Architecture-Tech Lead

- Task ID: `ARCH-001`
- Agent owner: `tech_lead` (Main Agent)
- Status: `DONE`
- Contract version(s) used: None; shared contract approval is delegated to `CONTRACT-001`.
- Upstream dependencies checked: None required; `ARCH-001` has no dependencies.
- Changed files:
  - `docs/architecture/decisions/ADR-0002.md` — corrected a truncated sentence; architecture meaning unchanged.
  - `harness/handoffs/ARCH-001.md` — this handoff.
- New/updated tests: None; this task is architecture/ADR review only.

## Review evidence

- Read the task-scoped sources: `AGENTS.md`, `GOALS.md`, `PLANS.md`, `docs/architecture/overview.md`, all files in `docs/architecture/decisions/`, all 17 files in `docs/architecture/blocks/`, and `docs/requirements/owner-decision-baseline.md`.
- Confirmed the overview defines 17 logical capabilities, not 17 mandatory network services.
- Confirmed the MVP direction is a Python/FastAPI modular monolith with separate Python RAG and ingestion workers; Rust remains benchmark-gated and is not an approved migration.
- Confirmed the trusted Core owns identity, authorization, administration, lifecycle and job coordination; workers cannot grant access; authorization is fail-closed with explicit deny precedence.
- Confirmed ADR-0001 through ADR-0005 were reviewed and explicitly approved by the Project Owner on 2026-11-10; the overview now records the approved MVP architecture baseline.
- Confirmed the overview's 12 architecture decision rows map to the decision register, including unresolved `DEC-001` through `DEC-014` references.
- Confirmed the 17 block documents describe ownership, trust boundaries, handoff tests and alignment with the overview without requiring a scope expansion.
- No production deployment, secret use, cloud provisioning or code changes were performed.

## Security implications

- Preserve backend-enforced RBAC + department membership + document ACL with default deny and explicit deny winning over allow.
- Do not allow the LLM, browser, vector index, queue payload, cache or retrieved text to make authorization decisions.
- Recheck tenant, ACL, policy version and document version at job acceptance/resume, every retrieval branch, source/citation access and cache reuse.
- Preserve the explicit restriction that System Admin cannot read user conversation bodies by default.

## Major decisions still pending Project Owner approval

The following must not be changed to `APPROVED` by an agent:

- `DEC-001`, `DEC-002`, `DEC-003`, `DEC-004`, `DEC-005`, `DEC-006`, `DEC-007`, `DEC-008`, `DEC-009`, `DEC-010`, `DEC-011`, `DEC-012`, `DEC-013`, `DEC-014`.
- In particular: final backend/runtime migration scope, cloud/provider/region, LLM providers and retention terms, data stores, worker trust transport, authorization precedence details, lifecycle safeguards, capacity/quality/RPO/RTO thresholds and repository migration.

## Acceptance state

- Architecture review: **complete for the approved MVP baseline**.
- ADR review: **complete; ADR-0001 through ADR-0005 are Accepted**.
- Project Owner sign-off: **recorded** for the architecture baseline and ADR-0001 through ADR-0005 on 2026-11-10.
- `ARCH-001` acceptance: **DONE** for the approved MVP architecture baseline. Unresolved `DEC-*` items remain scoped blockers for their affected tasks and are not silently approved here.
- `CONTRACT-001` may begin its review package; its own contract approval gate remains separate.

## Commands actually executed + exit status

- `sed`/`rg` source review commands: exit `0`.
- `python3 scripts/validate_harness.py`: run after this handoff; result recorded below.

## Integration steps

1. Project Owner reviewed and approved the overview and ADR-0001 through ADR-0005 in the conversation on 2026-11-10.
2. Main Agent recorded the approval in the relevant ADRs, handoff and task registry.
3. Unresolved decision-register items remain pending and continue to block only their affected work.
4. Activate `CONTRACT-001` for its independent review package.

## Known limitations / blockers with IDs

- `DEC-001`–`DEC-014`: unresolved owner decisions; see `docs/architecture/decisions/DECISION-REGISTER.md`.
- Architecture approval is recorded; the remaining decision-register items are not included in this approval.

## Suggested next READY task

- `CONTRACT-001` is now `READY` after the architecture approval evidence was recorded.

## Human approval required

No additional human approval is required to open `CONTRACT-001`; its contract review and approval package has its own gate.
