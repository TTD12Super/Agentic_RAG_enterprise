# Ingestion API & job contract (proposal)

## Commands
- `POST /api/v1/documents`: multipart upload; requires `document:create`. Returns `202` + `job_id`, never immediately ACTIVE.
- `GET /api/v1/ingestion-jobs/{job_id}`: status, redacted progress, error codes.
- `POST /api/v1/documents/{id}/approve`: independent `document:approve` permission.
- `POST /api/v1/documents/{id}/publish`: independent `document:publish` permission.
- `DELETE /api/v1/documents/{id}`: `document:delete` plus retention/legal-hold policy.

## Job event
```json
{"job_id":"job-1","tenant_id":"tenant-a","document_id":"doc-42","version_id":"v-2","job_state":"COMPLETED","document_version_state":"PROCESS_VALIDATED","attempt":1,"error_code":null}
```
`job_state` follows the shared job lifecycle; `document_version_state` follows the document publication lifecycle. Use an idempotency key per upload event; retry only safe stages; quarantine files with parse errors. Atomic publication and cache invalidation are mandatory gates.

## Owner-provided ingestion limits

- Uploads stream to private object storage and return `413 PAYLOAD_TOO_LARGE` over 200,000,000 bytes.
- PDF scans require Vietnamese/English OCR; `.docx` is bounded to two million extracted words; `.xlsx` is bounded to 50 sheets, 200,000 populated rows per workbook and 200 columns per sheet.
- Macros, scripts and executable formulas are not run.
- Each retry has a unique attempt ID and is limited to three attempts per unchanged document version.
- Approval expires after 30 minutes; maintenance has a configurable 60-minute watchdog and never auto-approves.
- A failed or rejected version leaves the previous ACTIVE version available; failure cleanup releases maintenance and resumes paused query jobs only after authorization/version rechecks.
