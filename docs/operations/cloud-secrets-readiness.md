# Cloud deployment and secrets readiness — INFRA-002

**Task:** `INFRA-002`  
**Status:** `READY_FOR_INTEGRATION`  
**Scope:** readiness evidence only; no account creation, provisioning, secret handling or deployment was performed.

## 1. Executive result

The repository is ready to collect owner-provided cloud and secret inputs, but it is not production-deployable yet. The following decisions remain `PENDING` in the decision register:

- `DEC-001`: primary/fallback LLM, embedding and reranker providers/models;
- `DEC-002`: cloud provider, region, topology and managed-service profile;
- `DEC-003`/`DEC-004`: trace backend and alert recipients;
- `DEC-005`: final retention, deletion and legal-hold policy;
- `DEC-006`/`DEC-013`: capacity, cost, quality, RPO/RTO and alert thresholds.

The smallest low-risk path for a student/demo is **Profile A: Vercel frontend + Azure for Students container runtime + Qdrant Cloud Free**, with a separate development database/object-storage choice. Profile B, **Vercel + Oracle Always Free VM**, is a lower-cash-cost fallback but puts patching, backup, restore and availability on the operator. Neither profile is evidence for production availability, compliance, 500-session capacity or enterprise data handling.

For production, the recommendation is conditional: choose a managed private network with managed PostgreSQL, private versioned object storage, a production Qdrant tier or approved private deployment, a provider secret manager, and isolated dev/staging/prod resources. The provider and region must be selected and approved by the Project Owner first.

## 2. Current evidence

Already documented:

- FastAPI/Python API, separate RAG and ingestion workers, PostgreSQL 17, Qdrant, private S3-compatible object storage and optional Redis.
- PostgreSQL is authoritative for durable jobs/checkpoints; Qdrant is rebuildable from source data; Redis is non-authoritative.
- Dev, staging and production require separate secrets, databases and buckets.
- Production requires private networks, encryption in transit/at rest, least-privilege identities, managed secrets, backups, restore drills, rollback and redacted telemetry.
- Proposed backup baseline: daily PostgreSQL base backup plus WAL/PITR, versioned object storage and rebuildable Qdrant; proposed RPO/RTO are targets until restore evidence exists.
- Vercel is the planned frontend host. The backend/worker host and region remain undecided.
- `INFRA-003` owns the monitoring platform; `AUDIT-001` owns application telemetry. This task does not implement monitoring.

Not yet evidenced:

- No cloud account, subscription, project, tenant, region, quota or billing setup was inspected or created.
- No secret manager, API key, DNS/TLS certificate, private network, database, bucket, Qdrant cluster or deployment pipeline exists in this task.
- No provider key, model key, database password or connection string was received or tested.
- No capacity, backup/restore, network-isolation, rotation or production smoke test was run.

## 3. Profiles and provider terms

### Student/demo recommendation — Profile A

| Component | Proposed choice | Boundary |
|---|---|---|
| Frontend | Vercel Free | Public UI only; never put backend/LLM/database secrets in browser-exposed variables |
| API/workers | Azure for Students container runtime | Demo/coursework only; service availability, quotas and credit must be verified by owner |
| Vector search | Qdrant Cloud Free | Prototype/test only; single node, 1 GB RAM and 4 GB disk, no production SLA |
| Database/object storage | Separate development-tier managed services or approved self-managed disposable services | Must be isolated from production and use synthetic data unless policy is approved |
| LLM/embedding/reranker | Separately approved provider account | Cloud student credit does not pay for external model usage |

Azure's official offer states that eligible students receive USD 100 credit for the first 12 months, subject to eligibility, availability and offer terms; exhausting the credit disables the subscription unless the owner separately upgrades it. See [Azure for Students offer](https://azure.microsoft.com/en-us/pricing/offers/ms-azr-0170p).

Qdrant documents its Free cluster as a prototype/test tier with 0.5 vCPU, 1 GB RAM, 4 GB disk and one node; unused clusters can be suspended/deleted under the documented inactivity policy. See [Qdrant Cloud cluster tiers](https://qdrant.tech/documentation/cloud/create-cluster/) and [Qdrant Managed Cloud](https://qdrant.tech/documentation/cloud/).

### Self-managed fallback — Profile B

Vercel Free plus an Oracle Always Free VM running Docker containers can minimize cash cost, but creates a single-VM failure boundary. The owner/operator must patch the VM, restrict network ingress, configure backups, verify restores and monitor capacity. Oracle documents Always Free resources as home-region resources subject to shape availability and quotas; an out-of-host-capacity error can prevent provisioning. See [Oracle Always Free resources](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm).

### Production boundary

Do not use Qdrant Free, Oracle Always Free or student credits as production evidence. Production requires an approved cloud/region and a review of residency, provider data processing, private connectivity, quotas, backup/restore, availability, cost and incident ownership. `DEC-002` remains `PENDING`.

## 4. Redacted configuration inventory

These are names only. Values must be entered by the Project Owner or an authorized operator in the approved secret/configuration stores.

| Class | Variable names | Secret? | Environments |
|---|---|---:|---|
| Runtime | `APP_ENV`, `LOG_LEVEL`, `PUBLIC_API_BASE_URL`, `CORS_ALLOWED_ORIGINS` | No, except private origins if policy requires | dev/staging/prod, separately |
| Auth/crypto | `JWT_SIGNING_KEY`, `SESSION_ENCRYPTION_KEY`, `COOKIE_SIGNING_KEY`, `MFA_ISSUER` | Yes for keys | dev/staging/prod, separately |
| PostgreSQL | `DATABASE_URL` or `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_SSL_MODE` | Password/URL yes | dev/staging/prod, separately |
| Qdrant | `QDRANT_URL`, `QDRANT_API_KEY`, `QDRANT_COLLECTION_PREFIX` | API key yes | dev/staging/prod, separately |
| Object storage | `OBJECT_STORAGE_ENDPOINT`, `OBJECT_STORAGE_REGION`, `OBJECT_STORAGE_BUCKET`, `OBJECT_STORAGE_ACCESS_KEY_ID`, `OBJECT_STORAGE_SECRET_ACCESS_KEY` | Access/secret keys yes | separate bucket and credentials per environment |
| Redis (optional) | `REDIS_URL`, `REDIS_PASSWORD`, `REDIS_TLS` | Password/URL yes | dev/staging/prod, separately |
| Model gateway | `BACKEND_GEMINI_API_KEY`, `BACKEND_GEMINI_MODEL` for the current Gemini adapter; future provider-neutral names remain pending `DEC-001` | API keys yes | only after `DEC-001` approval |
| Embedding/reranker | `EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`, `EMBEDDING_API_KEY`, `RERANKER_PROVIDER`, `RERANKER_MODEL`, `RERANKER_API_KEY` | API keys yes | only after `DEC-001` approval |
| Observability | `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_EXPORTER_OTLP_HEADERS`, `PROMETHEUS_REMOTE_WRITE_URL`, `PROMETHEUS_REMOTE_WRITE_TOKEN` | Headers/tokens yes | only after `DEC-003` approval |
| Deployment/CI | `REGISTRY_URL`, `REGISTRY_USERNAME`, `REGISTRY_PASSWORD`, `CLOUD_SUBSCRIPTION_ID`, `CLOUD_PROJECT_ID`, `CLOUD_TENANCY_ID` | Credentials/tokens yes | owner/CI scope only; never runtime-wide |
| Notifications | `ALERT_WEBHOOK_URL` or provider-specific notification credentials | Yes | only after `DEC-004` approval |

The exact variable names are an infrastructure handoff inventory, not a backend contract. Backend must confirm names when its configuration surface exists. No `.env`, `.env.local`, key file or real value may be committed.

## 5. Environment and access matrix

| Environment | Data | Credentials | Exposure | Required controls |
|---|---|---|---|---|
| Local/dev | Synthetic fixtures only by default | Developer-local disposable values | Localhost/private network | `.env.example` names only; no production export |
| Demo | Synthetic or explicitly approved low-sensitivity data | Demo-only credentials | Public frontend, private API/data plane | `DEMO` label, hard LLM spend cap, backups before destructive tests |
| Staging | Sanitized data only | Staging-only identities and keys | Private data plane; restricted UI | Same auth/ACL/egress policy as production; redacted telemetry |
| Production | Approved enterprise data | Separate least-privilege identities and secret versions | Private DB/object/vector networks; HTTPS edge | MFA, rotation, audit, backup/restore, alerts, incident owner, release gate |

Vercel documents environment-specific variables and supports unreadable Secret-type values for Preview/Production; only non-sensitive public configuration may be exposed with a public framework prefix. See [Vercel environment variables](https://vercel.com/docs/environment-variables) and [Vercel sensitive environment variables](https://vercel.com/docs/environment-variables/sensitive-environment-variables).

## 6. Least privilege, rotation and budget controls

- Use separate identities for API, RAG worker, ingestion worker, migration job, backup job and CI/CD. Runtime identities must not be owner/admin identities.
- Database credentials are scoped to the application database/schema; migration credentials are short-lived or isolated from normal runtime credentials.
- Object storage separates read/write prefixes and bucket permissions; signed upload/download URLs are short-lived. Buckets remain private.
- Qdrant keys are scoped to the required collection permissions where supported; never ship them to the browser.
- LLM keys are server-side only, provider-specific, restricted to the required model/project, and limited by provider budget/rate controls where available.
- Rotate bootstrap, CI, database, storage, Qdrant, model and observability credentials before first production data and after any suspected exposure. Verify revocation, restart/reload behavior and audit evidence.
- Set a hard monthly spend cap/alert for each external model provider and cloud account, plus per-request token/time limits already proposed in the RAG policy. Cloud student credits are not an LLM budget.
- Alert recipients and escalation channels remain `PENDING` under `DEC-004`; do not configure real recipients in this task.

## 7. Project Owner action checklist

1. Choose and explicitly approve `DEC-002`: provider(s), region(s), data residency, topology and production service tiers.
2. For demo only, choose Profile A or B and confirm that all data is synthetic or approved low-sensitivity data.
3. Create/verify the owner accounts and billing/credit controls for Vercel, selected backend cloud, Qdrant and the LLM provider. Do not send credentials in chat or Git.
4. Provide the approved secret-store path and access method; provide names/metadata only to the Main Agent, never secret values.
5. Approve `DEC-001` with primary/fallback model names, versions, training prohibition, retention, residency and egress terms.
6. Approve `DEC-003`/`DEC-004` for trace backend, retention, alert recipients and notification channels.
7. Confirm dev/staging/prod separation, domain/DNS ownership, TLS ownership and whether preview deployments may call any non-public API.
8. Define provider/cloud quotas, spend caps, rate limits and who receives budget alerts.
9. After Backend exposes its configuration contract, reconcile the variable names above with the actual `.env.example`/runtime configuration without adding values here.
10. Supply test-only credentials through the approved secret store for the next authorized infrastructure task; DevOps then verifies connectivity without recording values.

## 8. Risk and go/no-go

Current result: **READY_FOR_INTEGRATION, not production-ready and not a deployment authorization.**

Blocking risks are unresolved provider/region/residency, LLM data-processing terms, alert ownership, final retention policy, capacity definition and restore evidence. A production release is **NO-GO** until those decisions are approved and the release gate supplies real tests for secret rotation, private networking, backup/restore, ACL/revocation, monitoring and rollback.

