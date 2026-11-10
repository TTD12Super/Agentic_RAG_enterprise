# Task registry protocol

`tasks.json` is the canonical tracker; `PLANS.md` documents phases. Each task has stable `id`, `owner`, `phase`, `depends_on`, `status`, `deliverables`, `acceptance`, and an execution packet:

- `scope.read_paths`: documents and directories the agent must inspect.
- `scope.write_paths`: directories the agent may change for this task.
- `scope.forbidden_paths`: paths the agent must not change or use for task data.
- `architecture_blocks`: logical blocks covered by the task, using the `01`–`17` IDs.
- `requirements`: functional/non-functional requirement IDs covered by the task.
- `contracts`: shared contract files that must be reviewed before implementation.
- `validation`: checks or test targets that must be executed and recorded in the handoff.
- `handoff`: expected handoff file path under `harness/handoffs/`.
- `decision_authority` (when present): explicit reviewer, editor and approver for a high-risk task.

The task packet narrows the broader directory ownership in `docs/file-ownership.md`; it does not grant permission to change approved contracts, architecture, security policy, Git state or deployment settings.

For shared contracts, the Security Agent reviews and proposes, the Main Agent edits after affected-agent review, and the Project Owner approves. A reviewer must not mark a shared contract `APPROVED`.

The top-level `decision_policy` defines approval authority:

- `minor_decisions: main_agent`: local, non-breaking implementation and integration choices are reviewed by the Main Agent.
- `major_decisions: project_owner`: architecture, shared contracts, security/data policy, major dependencies, scope, deployment and Git delivery require Project Owner approval.
- `record`: decisions and evidence are recorded in the task handoff.
- `escalate_when`: no approved option exists, the trade-offs are material, or the decision changes shared behavior/MVP scope; the affected task becomes `BLOCKED` until the Project Owner decides.

The top-level `agent_role_map` maps non-specialist task owners to runtime roles. `tech_lead` is an alias for the Main Agent and is not a separate `.codex/agents/*.toml` sub-agent. All other task owners must match a specialist profile in `.codex/agents/`.

The top-level `concurrency_policy` sets a maximum of 10 active agents and separate context windows. `task_concurrency[TASK-ID].requested_agents` is the number activated for that task; it may be 1, 3 or 10 as needed. The Main Agent must still check dependencies and write-path conflicts before activation. Agents share repository artifacts and handoffs, not conversation memory.

Statuses: `PLANNED`, `READY`, `IN_PROGRESS`, `BLOCKED`, `READY_FOR_INTEGRATION`, `DONE`, `FAILED`.

- READY only if all `depends_on` are DONE. The current task schema has no contract-only exception.
- READY_FOR_INTEGRATION is local implementation complete, not proof of overall completion.
- DONE requires integration checks reviewed by Tech Lead.
- Main Agent updates registry after human/contract-gate verification; no automatic scheduler exists solely because this file is present.
- If dependency missing, use `harness/handoffs/TEMPLATE.md` and schedule another READY task, never fabricate upstream results.
- Later migration requests become new Backend-owned tasks with explicit dependencies, not edits by Ingestion or silent changes to an already DONE DB-001. Update the task registry, dependency graph and phase checklist together; keep affected work BLOCKED until the migration is reviewed and DONE.
