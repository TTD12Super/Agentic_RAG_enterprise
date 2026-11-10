# Phase 2 — Ingestion & knowledge

- [x] Implement upload, quarantine, scanning and approval
- [ ] Parse structural sections and tables (parser/OCR remains a downstream production adapter)
- [x] Index versioned ACL-inheriting chunks
- [x] Validate publish/version/invalidations
- [x] Complete Backend administration APIs and role-denial integration tests

## Task mapping

`MODEL-001`, `KNOW-001`, `ING-001`, `ADMIN-API-001`

## Gate
- [x] Tests actually executed; command/result attached.
- [x] All phase blocking dependencies marked DONE.
- [x] Security and contract compatibility reviewed.
- [ ] Tech Lead and human owner sign off before moving to next phase.

## Evidence links
- Task IDs: `MODEL-001`, `KNOW-001`, `ING-001`, `ADMIN-API-001`
- Test reports: `harness/handoffs/ADMIN-QA-001.md`, `harness/reviews/ADMIN-API-001-main-review.md`
- ADRs: `docs/architecture/decisions/ADR-0001.md`–`ADR-0005.md`
- Reviewer/date: Main Agent / 2026-11-10

## Gate note

The provider-neutral Phase 2 foundation is implemented and task-level tests
pass. Phase transition remains open until the production parser/OCR adapter
and the explicit Project Owner sign-off are recorded; no production cloud or
API-key decision is inferred.
