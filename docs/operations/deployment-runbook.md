# Deployment runbook — template

1. Verify approved release, CI, migrations, image digest, secrets and tenant configuration.
2. Deploy private Postgres/Qdrant/Redis/object store networks and restricted service identities.
3. Run migrations, verify vector index version and healthy dependencies.
4. Execute auth/ACL, ingestion, retrieval, citation and injection smoke tests.
5. Enable monitored traffic, observe p95 latency, denied requests, tool calls, external egress and costs.
6. Rollback application or switch ACTIVE index/version if smoke tests fail. Never rollback in a way that re-grants revoked data.
7. Verify backups and restore drills; document recovery point/time targets once approved.

**Not executable yet:** docker manifests and deployment pipeline will be produced by Phase 1/5 tasks.

## Owner-provided operating baseline

- Dev, staging and production require separate secrets, databases and object-storage buckets. Production data must not be copied to development without approval and de-identification.
- MVP target stack is PostgreSQL 17, Qdrant, private S3-compatible object storage and optional Redis; PostgreSQL remains authoritative for jobs and checkpoints.
- PostgreSQL uses daily base backup plus continuous WAL/PITR. Object storage uses versioning/backup. Qdrant is recoverable by snapshot or rebuild from source data.
- Proposed recovery targets are RPO ≤1 hour and RTO ≤4 hours with quarterly restore drills; these are not claims until evidence exists.
- A valid upload is limited to 200,000,000 bytes and supported formats are `.pdf`, `.docx` and `.xlsx`. Maintenance has a configurable 60-minute watchdog and must never leave the chatbot locked after a safe abort.
- Peak load verification uses 500 active sessions, 30 queries/minute sustained and a 60 queries/minute five-minute burst. The exact cloud provider and region remain pending.

## Student/demo rollout

Use one of the following only for development, coursework or a controlled demo:

1. Vercel frontend + Azure for Students container runtime + Qdrant Cloud Free.
2. Vercel frontend + Oracle Always Free VM running Docker Compose for API, workers and development data services.

For either profile:

- Keep real enterprise data out unless retention, access and backup controls are explicitly approved.
- Store all LLM, database and Qdrant keys in a secret store or protected runtime variables; never expose them to the browser.
- Upload large files directly to private object storage using short-lived signed URLs.
- Export and verify PostgreSQL, document and Qdrant backups before any destructive test.
- Label the environment `DEMO`, disable production alert claims and set hard spending limits for external LLM calls.

Render Free may be used for a temporary API preview only; it must not hold durable production conversations, documents or audit records.
