# Development Harness — Enterprise Agentic RAG

## 1. Overview

The Development Harness coordinates task execution, dependency tracking, agent handoffs, implementation evidence, and quality gates across the Enterprise Agentic RAG repository.

It supports controlled multi-agent development under Main Agent / Tech Lead supervision.

**Task execution is manually coordinated, not automatically scheduled.**

The Project Owner retains final approval authority.

## 2. Core Responsibilities

- Task assignment and dependency tracking.
- Development phase management.
- Multi-agent coordination.
- Implementation progress tracking.
- Agent handoff management.
- Review and validation evidence.
- Quality gate verification.
- Integration readiness tracking.
- Development activity logging.

The Harness does not implement application business logic.

## 3. Project Structure

```text
harness/
├── tasks/
│   ├── tasks.json          # Authoritative task state
│   ├── DEPENDENCIES.md     # Task dependency graph
│   └── README.md           # Task management guide
│
├── checklists/             # Phase 0–7 quality gates
│
├── handoffs/
│   ├── TEMPLATE.md        # Standard agent handoff
│   └── README.md
│
├── reviews/                # Task and integration reviews
├── context/                # Development context references
├── build/                  # Build-related documentation
│
├── build-log.md            # Development activity log
├── file-manifest.json      # Repository file inventory
└── README.md
```

## 4. Task Management

`tasks/tasks.json` is the single source of truth for task status and dependencies.

Each task defines:

- Task ID and phase.
- Assigned owner.
- Current status.
- Dependencies.
- Expected deliverables.
- Acceptance criteria.

### Task Execution Rules

1. Main Agent identifies eligible tasks.
2. Verify all required dependencies are DONE.
3. Assign a scoped task to the appropriate Subagent.
4. Provide relevant contracts and ownership boundaries.
5. Subagent implements and validates its assigned work.
6. Subagent reports actual results and remaining risks.
7. Main Agent reviews the evidence.
8. Update task state only according to approved governance.

Do not mark tasks DONE without required acceptance and integration evidence.

`DEPENDENCIES.md` is descriptive and must remain synchronized with `tasks.json`.

## 5. Multi-Agent Coordination

The Main Agent coordinates the development process.

Subagents are responsible for their assigned implementation tasks.

### Coordination Principles

- Respect task ownership.
- Respect file ownership.
- Avoid concurrent modification of shared files.
- Follow accepted contracts and ADRs.
- Preserve task dependency order.
- Coordinate shared interfaces.
- Do not invent completed dependencies.
- Do not silently expand task scope.

Follow `../docs/agent-collaboration.md`.

## 6. Handoff & Review

When implementation is completed or blocked, Subagents must provide a structured handoff using:

`handoffs/TEMPLATE.md`

A handoff should identify:

- Task ID and owner.
- Implementation summary.
- Files changed.
- Contracts affected.
- Tests executed and results.
- Dependencies and blockers.
- Known risks.
- Integration readiness.

The Main Agent reviews handoff evidence before coordinating integration.

Mock-based validation does not automatically establish successful integration.

## 7. Quality Gates

Phase completion follows the checklists in:

`checklists/`

Quality requirements are defined in:

`../docs/testing/quality-gates.md`

Before completing a task or phase:

- Verify acceptance criteria.
- Review relevant test evidence.
- Verify contract compatibility.
- Review applicable security requirements.
- Resolve blocking dependencies.
- Obtain required human approvals.

Implementation completion and integration completion are separate milestones.

## 8. Development Evidence

Use `build-log.md` to record relevant development activity.

Evidence must reflect actual execution.

Record:

- Task references.
- Implemented changes.
- Validation commands.
- Test outcomes.
- Integration findings.
- Relevant blockers and decisions.

Never fabricate test results, approvals, or completion evidence.

Do not store credentials, personal information, or confidential documents in Harness artifacts.

## 9. Validation

The repository provides a Harness validation script:

```bash
python3 scripts/validate_harness.py
```

Run this command from the repository root.

The validator is intended to check repository Harness consistency, including task dependencies, contracts, configuration, and structural requirements.

Validation results must be reported accurately.

Passing Harness validation does not prove application implementation or integration correctness.

## 10. Git & Approval Governance

All Git operations must follow:

`../docs/git-worktrees.md`

- Commit requires explicit Project Owner approval.
- Push requires separate explicit approval.
- Merge requires separate explicit approval.
- Never publish unauthorized confidential or personal information.
- Never falsify Git metadata or approval evidence.

Task completion does not automatically authorize Git operations.

## 11. References

- `../AGENTS.md` — Repository governance.
- `../PLANS.md` — Project roadmap.
- `../docs/agent-collaboration.md` — Agent coordination.
- `../docs/file-ownership.md` — File ownership.
- `../docs/contracts/README.md` — Contract governance.
- `../docs/testing/quality-gates.md` — Quality gates.
- `../docs/git-worktrees.md` — Git governance.
- `tasks/README.md` — Task management.
- `handoffs/README.md` — Handoff procedures.