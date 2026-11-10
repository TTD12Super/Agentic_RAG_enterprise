# PROMPTS — Copy/paste tasks for Codex

## Start with architecture and readiness (recommended)

```text
You are the Tech Lead for this repository. Read AGENTS.md, GOALS.md, PLANS.md,
docs/architecture/overview.md, docs/contracts/README.md, and harness/tasks/tasks.json.
Validate the harness with python3 scripts/validate_harness.py.
Inspect available custom agents in .codex/agents/.
Do not write application code, commit, push, or merge.
Identify READY tasks, blocked dependencies, contract gaps and parallel-safe subagent tasks.
Report a proposal for Phase 0 and ask approval before implementation.
```

## Begin an approved phase

```text
Read AGENTS.md, the phase checklist, applicable contracts, and tasks.json.
Implement only the approved READY task IDs. Delegate independent research or scoped
implementation to matching custom subagents. Never let two agents edit a shared file.
Review deliverables, run tests, create handoffs, and propose task status updates.
Do not commit, push, merge or deploy without my approval.
```

## Review a blocked task

```text
Review BLOCKED task <ID>. Identify the missing dependency and its exact contract.
Do not fabricate missing implementations or change shared APIs. Prepare a handoff,
find parallel-safe READY work, and propose the next action for the Tech Lead.
```

## Security review

```text
Use the security and qa agents to review document authorization, tool authorization,
prompt injection boundaries, tenant isolation and cache invalidation. Provide concrete
attack cases, relevant files, executed tests and residual risks. Do not modify code.
```
