# Flow A: Admin/authorized document manager → document publish

This workflow crosses the Python/FastAPI Core MVP, the authenticated Python ingestion worker and the authoritative policy/data stores. A later Rust replacement would preserve the same contracts. It is a proposal until the lifecycle and maintenance ADRs are accepted.

1. Website Manager or System Admin authenticates; the Core validates identity, MFA and document-management permission.
2. The Core enables chatbot-wide maintenance, stops admitting new chat work and checkpoints or safely quiesces existing question jobs.
3. The Core creates an idempotent ingestion job, records checksum/audit metadata and stores the upload in restricted non-searchable quarantine.
4. Admin review #1 decides whether the file may be processed. Rejection leaves the former ACTIVE version untouched.
5. A Python ingestion worker validates type/signature/size, scans for malware, applies resource limits and parses PDF/Word/Excel content.
6. The worker extracts headings, tables, pages and source spans; chunks inherit immutable document, version, tenant and ACL metadata.
7. The worker creates dense and lexical staging indexes and reports parse fidelity, index counts, citation paths and permission-test results.
8. Admin review #2 approves or rejects the processed result. A failed or rejected result never becomes searchable.
9. On approval, the Core publishes the latest approved version ACTIVE atomically and supersedes the prior version.
10. The system invalidates affected retrieval/answer caches, records lifecycle/audit events and ends maintenance safely.
11. The Core rechecks identity and policy before resuming paused jobs. External LLM calls are not assumed to resume mid-token; replay only safe read-only checkpoints.
12. On failure or cancellation, preserve the previous ACTIVE version, expose a redacted failure state and release maintenance without publishing unapproved data.

## Invariants

- Only Website Manager and System Admin can initiate document administration.
- Review #1 precedes processing; Review #2 follows processing.
- Only an approved, current ACTIVE version may serve chatbot evidence.
- Staging, rejected, failed, superseded, revoked or deleted content is never returned through search, citation, cache or direct source access.
- Cache/index invalidation and audit events are part of publication, revocation and deletion gates.

## Acceptance examples

- An unauthorized Chairman or employee receives 403 before a job is created.
- A suspicious upload remains quarantined and cannot reach the parser without approved handling.
- An unapproved document is absent from dense, lexical, parent and citation paths.
- A revoked version cannot be served through a stale vector index, cache or resumed question job.
- An ingestion failure cannot leave chatbot maintenance locked indefinitely.

## Owner-provided operational parameters

- Accepted MVP files are `.pdf`, `.docx` and `.xlsx`, with a 200,000,000-byte limit. `.doc` and `.xls` are rejected.
- PDF supports text and Vietnamese/English OCR up to 2,000 pages; DOCX and XLSX enforce extracted-content/resource limits.
- Ingestion retries at most three times for an unchanged version; a changed file creates a new version.
- Review approval expires after 30 minutes. Maintenance has a configurable 60-minute watchdog and never auto-approves.
- A failed or rejected version leaves the prior ACTIVE version serving. Permanent deletion is subject to retention/legal hold and tombstone replay on restore.

