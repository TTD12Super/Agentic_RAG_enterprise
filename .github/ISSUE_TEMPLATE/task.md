---
name: Development task
about: Scoped engineering task with dependencies, contracts, security controls and Git approval requirements
title: "[TASK-ID] "
labels: enhancement
---

# Development Task

## 1. Task Information

- **Task ID:**
- **Phase:**
- **Assigned owner / subagent:**
- **Priority:**
- **Current status:**
- **Related issues:**

Task status must remain consistent with `harness/tasks/tasks.json`.

## 2. Problem & Objectives

### Problem Statement

Describe the problem and why the change is required.

### Expected Outcome

Describe the expected behavior after implementation.

### Acceptance Criteria

- [ ] Requirements are clearly defined.
- [ ] Expected behavior is documented.
- [ ] Failure and edge cases are identified.
- [ ] Acceptance criteria are measurable.
- [ ] Security requirements are identified.

## 3. Dependencies

### Upstream Dependencies

List all prerequisite task IDs.

### Downstream Dependencies

List tasks or components affected by this implementation.

### Dependency Verification

- [ ] Required upstream tasks are DONE.
- [ ] Required contracts are approved.
- [ ] No unresolved blocking dependencies.
- [ ] Cross-agent dependencies are identified.

Do not implement blocked dependencies without explicit authorization.

## 4. Architecture & Contracts

### Relevant Documentation

- Root `AGENTS.md`:
- Scoped `AGENTS.md`:
- Module `README.md`:
- Architecture references:
- Accepted contracts:
- Relevant ADRs:

### Contract Impact

- [ ] No public contract changes.
- [ ] Contract changes are required and explicitly approved.
- [ ] Backward compatibility has been evaluated.
- [ ] Security and authorization impacts are reviewed.

Unapproved contract changes must not be implemented.

## 5. Scope & File Ownership

### Allowed Directories

List directories explicitly authorized for modification.

### Expected Files

List files expected to be created or modified.

### Restricted Files

List files or modules that must remain unchanged.

### Ownership Verification

- [ ] File ownership has been checked.
- [ ] No concurrent modification conflicts exist.
- [ ] Existing implementations have been inspected.
- [ ] Reusable components have been identified.
- [ ] Changes are limited to assigned task scope.

## 6. Implementation Plan

Describe the intended implementation approach.

### Planned Changes

1.
2.
3.

### Compatibility Considerations

Describe possible effects on existing functionality.

### Database / Migration Impact

- [ ] No database changes.
- [ ] Database migration required.
- [ ] Migration and rollback requirements reviewed.

## 7. Testing & Quality Requirements

### Required Tests

- [ ] Unit tests.
- [ ] Integration tests.
- [ ] Contract tests.
- [ ] Security tests.
- [ ] Regression tests.
- [ ] End-to-end tests, if applicable.

Mark non-applicable categories as N/A with justification.

### Quality Checks

- [ ] Relevant existing tests pass.
- [ ] New behavior is covered by tests.
- [ ] Error and failure paths are tested.
- [ ] Unauthorized access paths are tested where applicable.
- [ ] Static analysis and linting pass.
- [ ] Type checks pass where applicable.
- [ ] No unrelated functionality is broken.

### Test Evidence

Record actual commands, outcomes and relevant evidence references.

Never fabricate or estimate test results.

## 8. Security & Data Protection

### Data Classification

Identify the data classes affected:

- [ ] Public data.
- [ ] Approved internal development data.
- [ ] Confidential or proprietary data.
- [ ] Personal data / PII.
- [ ] Credentials or secrets.
- [ ] No data handling changes.

### Mandatory Security Checks

- [ ] No passwords, API keys, tokens or credentials are included.
- [ ] No `.env` files or private configuration are included.
- [ ] No private keys, certificates or sensitive authentication files are included.
- [ ] No personal or customer data is exposed.
- [ ] No unauthorized proprietary documents are included.
- [ ] No sensitive logs, exports, database dumps or generated artifacts are included.
- [ ] No unauthorized external data transfer is introduced.
- [ ] Authorization and tenant isolation are preserved.
- [ ] Relevant secret-scanning checks are completed.

Security evidence must not expose the sensitive information being checked.

Sensitive data must not be copied into issues, commit messages, PR descriptions or test evidence.

## 9. Git Branch Strategy

### Branch Information

- **Base branch:**
- **Working branch:**
- **Branch naming convention:**
- **Related task ID:**

### Branch Requirements

- [ ] Branch follows repository naming conventions.
- [ ] Changes are isolated from unrelated tasks.
- [ ] Protected branches are not modified directly.
- [ ] No unrelated commits are included.
- [ ] Concurrent agent work is isolated appropriately.
- [ ] No force push or history rewriting is planned.

Follow `docs/git-worktrees.md` and repository governance.

## 10. Commit Preparation & Approval

### Proposed Commit

- **Commit type:** feat / fix / refactor / test / docs / chore / perf / ci
- **Commit scope:**
- **Proposed commit subject:**
- **Proposed commit body:**
- **Files included:**
- **Reason for change:**
- **Expected impact:**
- **Tests performed:**

### Commit Requirements

- [ ] Commit uses Conventional Commits.
- [ ] Commit describes the actual changes.
- [ ] Commit includes the relevant task reference.
- [ ] Commit contains no unrelated changes.
- [ ] Commit message contains no AI-tool branding, attribution or generated-by markers.
- [ ] No tool-specific co-author or attribution trailers are added.
- [ ] Git author and committer identities are valid and not falsified.
- [ ] No personal or confidential data is exposed.
- [ ] Staged changes have been reviewed.
- [ ] Commit message has been presented to the Project Owner.

### Commit Authorization

- **Approval status:** PENDING / APPROVED / REJECTED
- **Approver:** Authorized Project Owner
- **Approval reference:**
- **Approved scope:**

**No commit may be created before explicit approval.**

Approval must cover the actual proposed changes and commit message.

Any material change after approval requires renewed authorization.

## 11. Push Preparation & Approval

### Push Destination

- **Remote:**
- **Source branch:**
- **Target remote branch:**
- **Commit SHA(s) to push:**
- **Number of commits:**
- **Expected remote changes:**

### Pre-Push Verification

- [ ] Every outgoing commit has been reviewed.
- [ ] Commit SHAs and messages are recorded.
- [ ] Remote and destination branch have been verified.
- [ ] No unrelated commits will be pushed.
- [ ] No secrets, PII or unauthorized proprietary data are present in outgoing commit history.
- [ ] Required tests and checks are complete.
- [ ] No unresolved blocking security findings exist.
- [ ] No force push is required.
- [ ] Branch protection requirements are respected.

### Push Authorization

- **Approval status:** PENDING / APPROVED / REJECTED
- **Approver:** Authorized Project Owner
- **Approval reference:**
- **Approved commit SHA(s):**
- **Approved destination:**

**Commit approval does not imply push approval.**

The Project Owner must explicitly approve the exact commits and destination before pushing.

Any change to the outgoing commit set or destination requires renewed approval.

## 12. Pull Request & Merge Controls

- [ ] Pull request references this task.
- [ ] PR includes the complete commit inventory.
- [ ] PR describes implementation and risks.
- [ ] Required checks pass.
- [ ] Required reviewers have approved.
- [ ] No unresolved blocking review comments.
- [ ] No security or privacy violations.
- [ ] Merge strategy follows repository policy.

**Never merge automatically.**

Merge requires separate explicit authorization from the Project Owner.

## 13. Handoff & Blockers

### Current Blockers

Describe blockers and unresolved dependencies.

### Required Cross-Agent Work

Identify other agents and required changes.

### Handoff Reference

Use `harness/handoffs/TEMPLATE.md`.

### Remaining Risks

Document known limitations and unresolved risks.

## 14. Completion Evidence

- **Implemented functionality:**
- **Files changed:**
- **Tests executed:**
- **Test outcomes:**
- **Security verification:**
- **Commit SHA(s):**
- **Commit approval reference:**
- **Push approval reference:**
- **Remote branch:**
- **Push result:**
- **PR reference:**
- **Integration status:**

Do not mark the task DONE solely because code has been committed or pushed.

Task completion requires the accepted project quality gates and integration evidence.