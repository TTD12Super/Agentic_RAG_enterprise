# Enterprise Git Branches, Worktrees & Delivery Governance

## 1. Purpose

This document defines mandatory Git governance rules for the Enterprise Agentic RAG repository.

All coding agents, including the Main Agent and specialized Subagents, must follow these rules.

The objectives are to:

- Maintain clean, traceable Git history.
- Prevent unauthorized Git operations.
- Support safe parallel development.
- Protect confidential and personal information.
- Ensure commits contain meaningful technical information.
- Prevent accidental changes to shared components.
- Require explicit Project Owner approval for controlled operations.
- Maintain enterprise-grade code review and delivery standards.

This document complements:

- `AGENTS.md`
- `docs/agent-collaboration.md`
- `docs/file-ownership.md`
- `harness/tasks/tasks.json`
- `.github/ISSUE_TEMPLATE/task.md`
- `.github/PULL_REQUEST_TEMPLATE.md`

Repository governance and approved task scope take precedence over agent convenience.

---

## 2. Git Governance Principles

### 2.1 Mandatory Rules

All agents must:

1. Work only on assigned tasks.
2. Respect repository ownership boundaries.
3. Use dedicated branches for independent development tasks.
4. Use separate worktrees when concurrent coding requires isolation.
5. Keep changes limited to the assigned task.
6. Review all modified and staged files.
7. Verify relevant tests before proposing a commit.
8. Inspect outgoing commit history before proposing a push.
9. Protect personal, confidential, and proprietary information.
10. Obtain explicit Project Owner approval before committing, pushing, merging, or deploying.

### 2.2 Prohibited Actions

Without explicit authorization, agents must never:

- Create Git commits.
- Push commits to remote repositories.
- Merge branches or pull requests.
- Rewrite Git history.
- Execute force pushes.
- Reset or discard unrelated changes.
- Delete branches containing unmerged work.
- Modify protected branches directly.
- Change Git author or committer identity.
- Upload sensitive or unauthorized information.
- Bypass required security checks.
- Bypass branch protection rules.

Read-only Git inspection commands are permitted.

Creating, deleting, or modifying branches and worktrees must follow task authorization and repository coordination rules.

---

## 3. Roles & Responsibilities

### 3.1 Project Owner

The Project Owner is responsible for:

- Approving controlled Git operations.
- Authorizing commit creation.
- Authorizing remote pushes.
- Approving merges.
- Approving protected branch modifications.
- Reviewing exceptions to established Git policies.
- Approving destructive or history-rewriting operations when justified.

Approval must be explicit and associated with the intended operation.

### 3.2 Main Agent / Tech Lead

The Main Agent is responsible for:

- Coordinating Git branches and worktrees.
- Assigning task ownership.
- Preventing concurrent file modification conflicts.
- Reviewing Subagent implementation reports.
- Reviewing Git diffs and commit proposals.
- Checking dependency and contract compatibility.
- Coordinating integration.
- Presenting approval requests to the Project Owner.

The Main Agent must not interpret its coordination role as permission to commit, push, or merge.

### 3.3 Specialized Subagents

Each Subagent is responsible for:

- Working within its assigned branch or worktree.
- Respecting allowed directories and files.
- Avoiding unrelated modifications.
- Running relevant tests.
- Reviewing its changes.
- Preparing commit information.
- Reporting blockers.
- Providing handoff evidence.

Subagents must not perform controlled Git operations without explicit authorization.

---

## 4. Branch Management

### 4.1 Branch Naming Convention

Use task-oriented branch names.

Recommended format:

```text
<type>/<TASK-ID>-<short-description>
```

Examples:

```text
feature/AUTH-001-policy-enforcement
feature/RAG-001-dense-retrieval
feature/ING-001-document-ingestion
feature/UI-001-chat-interface

fix/AUTH-001-permission-validation
test/RAG-002-retrieval-regression
docs/CONTRACT-001-interface-documentation
```

Branch names must:

- Identify the purpose of the change.
- Reference the relevant task where applicable.
- Avoid personal information.
- Avoid confidential project details.
- Avoid names of AI coding tools.
- Remain concise and understandable.

### 4.2 Protected Branches

Protected branches must not be modified directly.

Agents must not:

- Commit directly to protected branches.
- Push directly to protected branches.
- Bypass required pull requests.
- Override branch protection.
- Force push to protected branches.

All integration changes must follow the approved review process.

### 4.3 Task Isolation

Each independent task should use a dedicated branch.

Do not combine unrelated tasks in one branch without authorization.

Do not reuse an active branch assigned to another agent.

Before implementation, verify:

- Current branch.
- Working tree status.
- Assigned task.
- Branch ownership.
- Existing uncommitted changes.
- Relevant upstream dependencies.

---

## 5. Git Worktrees for Parallel Agents

### 5.1 Worktree Policy

Use separate Git worktrees when multiple coding agents modify the repository concurrently.

Worktrees provide separate working directories while sharing the underlying Git repository.

Worktrees do not automatically enforce file ownership or security restrictions.

Agents must still follow:

- `AGENTS.md`
- `docs/file-ownership.md`
- `docs/agent-collaboration.md`
- Assigned task boundaries.

### 5.2 Example Worktree Setup

The following commands are examples only.

Do not execute without authorization.

```bash
git worktree add ../rag-security \
  -b feature/AUTH-001-policy-enforcement

git worktree add ../rag-retrieval \
  -b feature/RAG-001-dense-retrieval
```

Example structure:

```text
workspace/
|
├── enterprise-agentic-rag/
│   └── Main Agent workspace
│
├── rag-security/
│   └── Security Agent workspace
│
└── rag-retrieval/
    └── RAG Engineer workspace
```

Each agent works within its assigned directory.

### 5.3 Worktree Isolation Rules

- Never modify another agent's active worktree.
- Never assume separate worktrees eliminate merge conflicts.
- Never concurrently edit shared files without coordination.
- Never reset another agent's branch.
- Never delete another agent's worktree without authorization.
- Never modify shared Git configuration without authorization.
- Never use destructive cleanup commands on unrelated work.

### 5.4 Shared Files

The following categories require special coordination:

- Database migrations.
- Shared API contracts.
- Authorization policies.
- Architectural decision records.
- Shared configuration files.
- Dependency lockfiles.
- Project-wide build configurations.
- Task-state management files.

Shared components must have a designated owner for each change.

If multiple agents require changes to the same shared file, the Main Agent must coordinate ownership and execution order.

### 5.5 Dependency Synchronization

Before starting dependent tasks:

1. Verify upstream task completion.
2. Confirm required contracts are accepted.
3. Confirm the integration base is appropriate.
4. Check relevant branch history.
5. Ensure no conflicting shared-file changes are active.

Do not assume a dependency is complete because another agent reports that implementation has started.

---

## 6. Pre-Implementation Git Inspection

Before editing code, inspect repository state.

Recommended commands:

```bash
git status --short

git branch --show-current

git log -5 --oneline

git worktree list
```

Inspect relevant files and existing implementation before making changes.

Do not modify unrelated uncommitted work.

If unexpected changes are present:

- Identify the affected files.
- Determine whether they belong to another task.
- Report the conflict.
- Do not overwrite or discard them.
- Request coordination when necessary.

---

## 7. Commit Standards

### 7.1 Conventional Commits

All commits must follow the repository's approved Conventional Commits convention.

Recommended format:

```text
<type>(<scope>): <short description>
```

Supported types include:

```text
feat
fix
refactor
test
docs
chore
perf
ci
build
```

Examples:

```text
feat(auth): implement policy enforcement

fix(retrieval): prevent unauthorized source access

test(ingestion): cover document version isolation

refactor(api): simplify request validation

docs(security): document authorization boundaries
```

Commit messages must accurately describe the changes.

### 7.2 Commit Subject Requirements

Commit subjects must:

- Describe a meaningful technical change.
- Use clear and professional language.
- Avoid vague descriptions.
- Avoid unnecessary personal information.
- Avoid confidential information.
- Avoid AI coding tool names.
- Avoid unsupported claims.

Prohibited examples:

```text
update code

fix stuff

Codex generated this implementation

AI automatically implemented security

misc changes
```

### 7.3 Commit Body Requirements

For meaningful implementation changes, the commit body should explain:

- What changed.
- Why the change was necessary.
- Relevant implementation considerations.
- Related task ID.
- Relevant testing evidence or references.
- Important compatibility or migration implications.

Recommended format:

```text
feat(auth): implement authorization enforcement

Implement centralized authorization enforcement for
protected document access operations.

Changes:
- Add policy evaluation integration.
- Enforce authorization before protected operations.
- Handle denied requests consistently.

Validation:
- Authorization unit tests passed.
- Denied-access scenarios verified.
- Contract compatibility checked.

Impact:
- No approved API contract changes.

Task: AUTH-001
```

Only report tests that were actually executed.

Do not invent passing results.

### 7.4 AI Tool Attribution Policy

Commit messages must not contain unnecessary AI-tool branding or automated attribution.

Do not add:

```text
Generated by Codex
Created with ChatGPT
Implemented by AI
AI-assisted commit
Co-Authored-By: Codex
```

Do not automatically add AI-tool attribution trailers.

Do not insert tool names into commit subjects or bodies unless the tool itself is genuinely relevant to the technical change.

This policy does not authorize falsifying Git metadata.

Preserve legitimate human authorship and contributor attribution.

Do not remove legally or contractually required disclosures.

Never impersonate another contributor or modify author identity to conceal who performed an operation.

### 7.5 Commit Scope

A commit should represent one coherent, reviewable change.

Avoid combining:

- Unrelated feature implementations.
- Unrelated refactoring.
- Formatting changes across unrelated modules.
- Unrelated database migrations.
- Unrelated documentation changes.
- Changes belonging to different task owners.

Focused commits improve traceability and review quality.

---

## 8. Pre-Commit Review

Before requesting commit approval, the agent must inspect the changes.

Recommended commands:

```bash
git status --short

git diff --stat

git diff

git diff --check
```

Review:

- Modified files.
- New files.
- Deleted files.
- Generated artifacts.
- Untracked files.
- Unrelated modifications.
- Sensitive information.
- API and schema changes.
- Security implications.

### 8.1 Staging Rules

Only stage files belonging to the approved task.

Prefer explicit file paths:

```bash
git add path/to/approved-file
```

Avoid broad staging commands in multi-agent workspaces:

```bash
git add .
git add -A
```

Broad staging can accidentally include unrelated or sensitive files.

After staging, inspect:

```bash
git diff --cached --stat

git diff --cached

git diff --cached --check

git diff --cached --name-only
```

Staging files does not constitute authorization to commit.

### 8.2 Sensitive Data Review

The staged changes must not include unauthorized:

- Passwords.
- API keys.
- Access tokens.
- Refresh tokens.
- Private keys.
- Credentials.
- Personal information.
- Customer records.
- Employee records.
- Confidential company documents.
- Proprietary source documents.
- Database dumps.
- Sensitive logs.
- Local environment files.
- Unapproved datasets.
- Private configuration.
- Internal infrastructure secrets.

Use approved secret-scanning and data-protection checks.

Do not print discovered secrets or personal information into logs or approval requests.

If sensitive data is discovered:

1. Stop the Git operation.
2. Prevent publication.
3. Report the incident without reproducing the sensitive values.
4. Follow the approved incident-response procedure.
5. Obtain authorization before any history remediation.
6. Rotate or revoke exposed credentials when required by incident-response policy.

Removing sensitive content from the latest working tree does not guarantee that it has been removed from Git history.

---

## 9. Commit Approval Gate

### 9.1 Mandatory Approval

Agents must obtain explicit Project Owner approval before creating a commit.

A completed implementation does not authorize a commit.

Passing tests does not authorize a commit.

A task assignment does not authorize a commit.

### 9.2 Required Commit Proposal

Before committing, present:

```text
COMMIT APPROVAL REQUEST

Task ID:
Repository:
Working branch:

Proposed commit subject:
Proposed commit body:

Files to include:

Summary of changes:

Reason for change:

Contracts affected:

Tests actually executed:
Test results:

Security checks:
Sensitive data findings:

Known risks:

Approval status: PENDING
```

The Project Owner must be able to review the exact proposed commit scope.

### 9.3 Approval Scope

Approval must identify the intended operation.

A generic instruction such as "continue development" must not be interpreted as commit authorization.

Authorization must be limited to the reviewed changes.

If the staged content or commit message materially changes after approval, obtain renewed approval.

### 9.4 Commit Execution

Only after explicit approval may the authorized agent execute the commit.

The agent must verify the staged changes still match the approved scope.

After committing, record:

- Full commit SHA.
- Commit subject.
- Commit body.
- Author and committer metadata.
- Files included.
- Associated task ID.
- Actual validation status.

Commit approval does not imply push approval.

---

## 10. Push Approval Gate

### 10.1 Mandatory Approval

No agent may push code without explicit Project Owner approval.

The following actions require authorization:

```bash
git push

git push origin <branch>

git push --set-upstream origin <branch>
```

No push operation is implicitly authorized by:

- Task assignment.
- Commit approval.
- Passing tests.
- Successful local implementation.
- PR preparation.
- Main Agent recommendation.

### 10.2 Outgoing Commit Verification

Before requesting push approval, inspect all commits that would be published.

Verify:

- Remote repository.
- Current branch.
- Target remote branch.
- Outgoing commit SHAs.
- Commit subjects.
- Full commit messages.
- Files introduced by outgoing commits.
- Existing remote history.
- Security scan results.
- Relevant tests.

For a branch with an existing remote tracking branch, the following commands can help inspect outgoing commits:

```bash
git status

git branch -vv

git log --format=fuller

git diff --stat
```

After verifying the correct remote reference and ensuring it is current, inspect the outgoing range:

```bash
git log --reverse --format=fuller <remote-ref>..HEAD

git diff --stat <remote-ref>..HEAD

git diff --name-status <remote-ref>..HEAD
```

For a new remote branch, determine the intended target and compare against the approved integration base.

Do not assume the outgoing commit set contains only the latest commit.

A push may publish multiple local commits.

### 10.3 Historical Data Protection

Security checks must consider the complete outgoing commit history.

Do not rely exclusively on the current working tree.

A secret or personal record removed in a later commit may still exist in an earlier commit that is about to be pushed.

The agent must evaluate:

- Outgoing commit messages.
- Added and modified content.
- Historical blobs introduced by outgoing commits.
- Sensitive files included in intermediate commits.
- Potential unauthorized data exposure.

Use approved repository scanning tools when available.

If the complete outgoing commit history cannot be inspected adequately, report the limitation and do not claim the scan passed.

### 10.4 Required Push Approval Report

Before pushing, present:

```text
GIT PUSH APPROVAL REQUEST

Task ID:

Repository:
Remote:
Source branch:
Target remote branch:

OUTGOING COMMITS

Commit 1:
Full SHA:
Subject:
Body:
Files:
Purpose:

Commit 2:
Full SHA:
Subject:
Body:
Files:
Purpose:

TOTAL OUTGOING COMMITS:

VALIDATION

Tests executed:
Test outcomes:
Contract checks:
Security checks:
Secret scanning:
PII scanning:
Outgoing history review:

RISK ASSESSMENT

Breaking changes:
Database impact:
Security impact:
Known limitations:

APPROVAL

Commit approval reference:
Push approval status: PENDING

REQUEST

Approve pushing the exact listed commits
to the specified remote branch?
```

The Project Owner must explicitly approve the exact outgoing commit set and destination.

### 10.5 Push Execution

Only after approval may the authorized push be executed.

Before execution, verify:

- The outgoing commit set has not changed.
- The destination has not changed.
- Required checks remain valid.
- The approval still applies.

If the outgoing commit set or destination changes, request renewed approval.

After pushing, verify:

- Push command result.
- Remote branch.
- Remote commit SHA.
- Published commit inventory.

Report failures accurately.

### 10.6 Force Push

Force pushing is prohibited by default.

Never execute:

```bash
git push --force
```

History rewriting and exceptional force pushes require a separately approved recovery procedure.

Approval must identify:

- The affected repository.
- The affected branch.
- The reason for rewriting history.
- The expected impact.
- Recovery and coordination requirements.

Do not overwrite remote work belonging to another contributor.

---

## 11. Pull Request Governance

Every implementation PR must use:

```text
.github/PULL_REQUEST_TEMPLATE.md
```

The PR must include:

- Task ID.
- Implementation summary.
- Changed files.
- Accepted contract references.
- Dependency impact.
- Complete commit inventory.
- Relevant test evidence.
- Security and privacy review.
- Migration considerations.
- Rollback considerations.
- Known limitations.
- Human approval status.

Do not claim that a PR has passed review when reviews are pending.

Do not treat a successful push as PR approval.

Do not bypass required CI checks.

---

## 12. Merge Approval Gate

Merging requires separate explicit Project Owner authorization.

Commit approval does not authorize merging.

Push approval does not authorize merging.

A successful CI run does not authorize merging.

Before proposing a merge:

1. Verify the PR commit inventory.
2. Verify required reviewer approvals.
3. Verify required CI checks.
4. Verify security checks.
5. Verify contract compatibility.
6. Verify dependency readiness.
7. Verify integration evidence.
8. Verify the intended merge strategy.
9. Verify the source and target branches.

Do not merge if required checks are incomplete.

### 12.1 Protected Branch Policy

Never bypass protected branch rules.

Never directly update protected branches to avoid PR review.

Never rewrite protected branch history.

### 12.2 Integration Responsibility

The Main Agent coordinates integration review.

Only an explicitly authorized actor may perform the merge.

A Subagent must not independently integrate its own work.

---

## 13. Prohibited Sensitive Information

The repository must not contain unauthorized sensitive information.

This applies to:

- Source files.
- Git commits.
- Commit messages.
- Branch names.
- Pull request descriptions.
- Issue descriptions.
- CI logs.
- Test reports.
- Screenshots.
- Generated artifacts.
- Git history.

### 13.1 Personal Data

Do not publish personal information unless explicitly permitted by applicable policy and authorization.

Examples include:

- Personal email addresses.
- Private phone numbers.
- Home addresses.
- Personal identification numbers.
- Employee records.
- Customer records.
- Personal financial information.
- Sensitive personal identifiers.

Use synthetic or appropriately anonymized test data.

### 13.2 Enterprise Data

Do not publish unauthorized:

- Internal company documents.
- Confidential customer documents.
- Proprietary business information.
- Internal credentials.
- Private infrastructure configurations.
- Sensitive architectural information.
- Confidential operational records.

### 13.3 Secrets

Never publish:

- API keys.
- Passwords.
- Authentication tokens.
- Database credentials.
- SSH private keys.
- Private certificates.
- Production environment secrets.

Use approved secret-management mechanisms.

Local environment files must remain excluded from version control.

---

## 14. Multi-Agent Conflict Management

Before assigning parallel work, the Main Agent must verify:

- Tasks are independently executable.
- Required dependencies are satisfied.
- Contracts are accepted.
- File ownership is clear.
- Shared files have designated owners.
- Worktree assignments are documented.
- No active file-editing conflicts exist.

If conflicts occur:

1. Stop conflicting modifications.
2. Preserve all existing work.
3. Identify affected files and owners.
4. Report the conflict.
5. Determine an approved integration strategy.
6. Resume only within authorized scope.

Never resolve conflicts by silently discarding another agent's changes.

Never use destructive Git commands as a shortcut.

---

## 15. Git Operation Restrictions

The following operations require explicit authorization:

| Operation | Requirement |
|---|---|
| Read Git status/history/diff | Allowed |
| Create or delete branch | Authorized task or explicit approval |
| Create or remove worktree | Authorized task or explicit approval |
| Stage task-scoped files | Allowed for approved task preparation |
| Create commit | Explicit Project Owner approval |
| Push commits | Separate explicit Project Owner approval |
| Open PR | Follow repository task authorization and PR policy |
| Merge PR | Separate explicit Project Owner approval |
| Force push | Exceptional, separately approved procedure |
| Rewrite history | Exceptional, separately approved procedure |
| Reset/discard unrelated changes | Prohibited without explicit authorization |
| Delete project data | Explicit Project Owner approval |
| Deploy | Separate explicit Project Owner approval |

Approval must be specific to the operation and affected scope.

Do not infer approval from unrelated instructions.

---

## 16. Required Git Delivery Report

At the end of each task, report:

```text
GIT DELIVERY REPORT

Task ID:
Task owner:

Repository:
Working branch:
Worktree:

IMPLEMENTATION

Summary:
Files changed:
Contracts affected:
Dependencies affected:

VALIDATION

Tests executed:
Test outcomes:
Security checks:
Known risks:

COMMIT

Commit created: YES / NO
Commit approval:
Commit SHA(s):
Commit message(s):

PUSH

Push performed: YES / NO
Push approval:
Remote:
Target branch:
Push result:
Remote verification:

PULL REQUEST

PR created: YES / NO
PR reference:
Review status:

MERGE

Merge performed: YES / NO
Merge approval:
Integration status:

REMAINING WORK

Blockers:
Unverified requirements:
Next steps:
```

Never fabricate Git metadata, approvals, testing evidence, or remote operation results.

---

## 17. Definition of Done

A task must not be marked DONE merely because its code has been written, committed, or pushed.

Completion requires:

- Accepted task scope satisfied.
- Relevant tests executed.
- Required quality gates passed.
- Security checks completed.
- Accepted contracts preserved.
- Required integration evidence available.
- Required human approvals recorded.
- Task-state updates performed according to repository governance.

A task may be implementation-complete while integration remains blocked.

Do not automatically mark a task DONE based on Git activity.

---

## 18. Final Enforcement Rules

All agents must follow these principles:

**Inspect before editing.**

**Review before staging.**

**Validate before requesting a commit.**

**Request approval before committing.**

**Inspect complete outgoing history before requesting a push.**

**Request separate approval before pushing.**

**Require review and approval before merging.**

**Never publish unauthorized personal, confidential, or proprietary information.**

**Never falsify authorship, test results, approvals, or delivery evidence.**

**Never override another agent's work without authorization.**

When blocked, preserve the current work and use the approved handoff process.

The Project Owner retains final control over Git delivery and integration.