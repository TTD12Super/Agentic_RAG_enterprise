# Testing — Enterprise Agentic RAG

## 1. Overview

The Testing module validates the correctness, security, reliability, and integration quality of Enterprise Agentic RAG.

Testing must provide reproducible evidence against accepted contracts, task acceptance criteria, and approved quality gates.

**Status:** Development harness; test implementations pending.

## 2. Technology Stack

- Backend Testing: Python testing framework (verify approved configuration)
- Frontend Testing: Approved React/TypeScript testing tools
- API Testing: Contract-based API validation
- Integration Testing: Approved service test environments
- E2E Testing: Approved browser testing framework
- Security Testing: Authorization and security regression tests
- RAG Evaluation: Approved evaluation metrics and golden datasets
- CI: GitHub Actions

Specific frameworks and versions must follow approved project decisions.

## 3. Project Structure

```text
tests/
├── unit/           # Individual component tests
├── integration/    # Cross-module and service integration tests
├── contracts/      # API and interface contract tests
├── e2e/            # End-to-end workflows
├── security/       # Security and authorization tests
├── evaluation/     # RAG quality evaluation
├── AGENTS.md
└── README.md
```

Directories represent planned testing categories.

## 4. Testing Architecture & Conventions

- Follow approved testing standards.
- Align tests with accepted contracts.
- Keep tests deterministic and reproducible.
- Reuse existing fixtures and utilities.
- Test successful and failure scenarios.
- Verify unauthorized access is denied.
- Preserve tenant and document isolation.
- Avoid testing against real confidential data.
- Use approved synthetic test data.
- Maintain regression coverage.
- Do not weaken tests to obtain passing results.
- Do not invent evaluation metrics or thresholds.

### Test Responsibilities

| Category | Responsibility |
|---|---|
| Unit | Individual functions and components |
| Integration | Communication between modules and services |
| Contract | API and shared interface compatibility |
| E2E | Complete application workflows |
| Security | Access control and security boundaries |
| Evaluation | Retrieval, evidence, and RAG answer quality |

## 5. Development & Validation

Before creating or modifying tests:

1. Read the assigned task and acceptance criteria.
2. Inspect relevant implementation.
3. Read applicable contracts.
4. Identify existing test coverage.
5. Reuse existing fixtures.
6. Implement required test scenarios.
7. Execute relevant tests.
8. Record actual results and failures.

Test reports must distinguish:

- PASS — Executed successfully.
- FAIL — Executed and failed.
- BLOCKED — Could not execute due to a dependency or environment issue.
- NOT RUN — Not executed.
- N/A — Not applicable, with justification.

Never claim tests passed without execution evidence.

Use test commands defined by the actual project configuration.

## 6. References

- `../AGENTS.md` — Repository governance.
- `AGENTS.md` — Testing-specific instructions.
- `../docs/testing/README.md` — Testing strategy.
- `../docs/testing/quality-gates.md` — Quality gates.
- `../docs/testing/golden-dataset-schema.md` — Evaluation dataset specifications.
- `../docs/security/security-test-cases.md` — Security test scenarios.
- `../docs/rag/evaluation-plan.md` — RAG evaluation.
- `../docs/contracts/` — Contract specifications.
- `../docs/git-worktrees.md` — Git governance.
- `../harness/tasks/tasks.json` — Tasks and dependencies.