# Document & chunk schema (proposal)

## Document
```json
{"document_id":"doc-42","tenant_id":"tenant-a","owner_department":"sales","classification":"INTERNAL","status":"ACTIVE","current_version_id":"v-2","created_by":"u-123"}
```

## DocumentVersion
```json
{"version_id":"v-2","document_id":"doc-42","sha256":"hex-of-checksum","source_uri":"private://documents/doc-42/v-2","effective_at":"2026-11-08T00:00:00Z","status":"ACTIVE","approval_id":"apr-12"}
```
Version status: `UPLOADED` → `QUARANTINED` → `REVIEW_1_APPROVED` → `PROCESSING` → `PROCESS_VALIDATED` → `PENDING_REVIEW_2` → `ACTIVE` → `SUPERSEDED`/`REVOKED`/`SOFT_DELETED`. Rejected, failed and cancelled versions are non-searchable terminal outcomes. A version must never skip either review gate.

The transition from `PENDING_REVIEW_2` to `ACTIVE` requires a recorded, authorized review-2 approval and all publication checks; approval alone does not publish a version.

## ChildChunk
```json
{"chunk_id":"chunk-77","document_id":"doc-42","version_id":"v-2","tenant_id":"tenant-a","parent_chunk_id":"parent-9","page_start":4,"page_end":4,"source_span":{"start":101,"end":412},"acl_policy_ref":"policy-7","text_hash":"hex","index_state":"ACTIVE"}
```
Parent child ACL cannot become broader than source; enforce permission again when expanding parent. Qdrant payload is an index projection; PostgreSQL/policy store is authoritative.

## Owner-provided upload and lifecycle baseline

- MVP accepts `.pdf`, `.docx` and `.xlsx`; `.doc` and `.xls` are rejected.
- Maximum upload size is 200,000,000 bytes. PDF supports text and Vietnamese/English OCR up to 2,000 pages; DOCX and XLSX have bounded extracted-content/resource limits.
- File upload validates actual bytes, MIME/magic bytes, checksum and malware status before processing.
- Citation preview requires `READ`; original-file download requires a separate `DOWNLOAD` decision and short-lived signed URL.
- The same administrator may perform both reviews. Approval expires after 30 minutes; rejection creates a new review request rather than an automatic retry.
- Retry is limited to three attempts for an unchanged version. A failed version never replaces the prior ACTIVE version.
- Soft delete immediately removes retrieval/preview access and invalidates derived indexes; permanent deletion is controlled by retention and legal hold.
