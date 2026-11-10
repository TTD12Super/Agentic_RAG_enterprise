# Security release cases

| ID | Scenario | Expected |
|---|---|---|
| SEC-01 | User lies about being administrator in prompt | No role change; tool/doc denied |
| SEC-02 | Chairman without create permission uses upload API | 403; no ingestion job |
| SEC-03 | Employee asks strategy document not in ACL | No chunk in search/context/response |
| SEC-04 | Cross-tenant dense + sparse searches | Zero foreign tenant IDs |
| SEC-05 | Parent expansion crosses ACL boundary | Parent content denied |
| SEC-06 | ACL revoked after caching | No stale content exposed |
| SEC-07 | Document carries tool-exfiltration instruction | Tool invocation blocked |
| SEC-08 | Policy service timeout | Fail closed |
| SEC-09 | Citation endpoint accessed by unprivileged user | Denied without existence leak |
| SEC-10 | Unapproved document exists in vector index | Cannot be served |
| SEC-11 | Restricted content enters raw logs | Redaction/missing sensitive payload |
| SEC-12 | LLM suggests deletion tool | Not registered/denied by gateway |

| SEC-13 | Upload exceeds 200,000,000 bytes | `413 PAYLOAD_TOO_LARGE`; no job or searchable artifact |
| SEC-14 | `.doc` or `.xls` upload | Rejected; no parser execution or ingestion job |
| SEC-15 | Scanned PDF contains Vietnamese/English OCR content | OCR runs within limits; provenance and OCR quality are recorded |
| SEC-16 | Same version is retried after transient failure | At most three idempotent attempts; prior ACTIVE version remains served |
| SEC-17 | Maintenance checkpoint resumes after ACL revocation | Checkpoint is stale; retrieval and citation access are denied/recomputed |
| SEC-18 | System Admin requests another user's conversation body, including during an incident | Denied; diagnostic metadata is handled separately without exposing conversation bodies |
| SEC-19 | Restore brings back soft-deleted content | Tombstone/revocation replay prevents retrieval before service resumes |
| SEC-20 | Provider fallback receives higher-sensitivity evidence | Egress policy blocks fallback; no classification bypass |
