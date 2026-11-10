# SECURITY — Reporting and rules

This repository initially contains scaffolding only. Never check in real credentials or proprietary documents.

- Report security findings privately to the repository owner; do not include secrets in issues.
- Authorization errors deny access; no fallback to unrestricted search.
- Treat all uploaded files and retrieved chunks as untrusted.
- No tool can obtain more privileges than the authenticated principal and service policy allow.
- Sensitive logging, cache segregation, key rotation, backups, and retention must be defined before production.

References: `docs/security/threat-model.md`, `docs/security/authorization-matrix.md`, `docs/security/prompt-injection-defense.md`.
