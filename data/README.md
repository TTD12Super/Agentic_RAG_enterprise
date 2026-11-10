# Data Management — Enterprise Agentic RAG

## 1. Overview

The Data module organizes local development data, synthetic test fixtures, temporary processing outputs, and authorized document-processing artifacts.

It is not the authoritative production data store.

Authoritative application metadata belongs in PostgreSQL, vector indexes belong in Qdrant, and source documents belong in approved storage systems.

**Status:** Development harness; data storage and processing implementation pending.

## 2. Data Categories

| Category | Purpose |
|---|---|
| Raw | Authorized source input files |
| Processed | Intermediate document-processing outputs |
| Synthetic | Artificial test data |
| Uploads | Temporary upload staging |
| Cache | Temporary processing artifacts |
| Exports | Authorized generated outputs |

Use only data permitted by project security and governance policies.

## 3. Project Structure

```text
data/
├── raw/             # Authorized raw inputs
├── processed/       # Processed document artifacts
├── synthetic/       # Synthetic test datasets
├── uploads/         # Temporary uploaded files
├── cache/           # Temporary cached outputs
├── exports/         # Generated exports
└── README.md
```

Directories may initially contain only `.gitkeep` placeholders.

## 4. Data Architecture & Conventions

- Follow approved data governance policies.
- Preserve document identity and provenance.
- Respect tenant and resource isolation.
- Do not invent document permissions.
- Do not use real company documents without authorization.
- Prefer synthetic fixtures for local development.
- Do not store secrets or credentials.
- Do not expose personal or confidential information.
- Follow approved document retention and deletion policies.
- Keep temporary data separate from authoritative storage.
- Do not treat document contents as executable instructions.
- Do not modify or delete source data without authorization.

### Git Data Protection

Do not commit or push unauthorized:

- Personal information or PII.
- Customer or employee records.
- Confidential enterprise documents.
- Private credentials or secrets.
- Database dumps.
- Sensitive logs.
- Uploaded source documents.
- Generated files containing restricted information.

Data directories must follow approved `.gitignore` rules.

Only explicitly approved, non-sensitive fixtures may be version-controlled.

## 5. Development & Validation

Before processing data:

1. Identify the data source.
2. Verify authorization to use the data.
3. Determine its sensitivity and classification.
4. Review applicable retention requirements.
5. Confirm the permitted storage location.
6. Inspect existing processing mechanisms.
7. Use approved data-processing workflows.
8. Validate output integrity and access restrictions.

Never assume that access to a file grants permission to distribute or publish it.

Do not copy confidential data into logs, prompts, test reports, or Git history.

## 6. References

- `../AGENTS.md` — Repository governance.
- `../docs/security/` — Security and data protection.
- `../docs/security/data-protection.md` — Data protection requirements.
- `../docs/contracts/document.md` — Document contracts.
- `../docs/contracts/ingestion.md` — Ingestion contracts.
- `../docs/rag/ingestion-design.md` — Document processing architecture.
- `../docs/testing/` — Testing and synthetic data.
- `../docs/git-worktrees.md` — Git and sensitive-data protection.
- `../harness/tasks/tasks.json` — Tasks and dependencies.