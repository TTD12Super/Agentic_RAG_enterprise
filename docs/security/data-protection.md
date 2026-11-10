# Data protection / DLP / privacy

- MVP product data classes: PUBLIC and INTERNAL. CONFIDENTIAL/RESTRICTED are reserved future egress-policy tiers, not additional MVP classification UI values.
- Egress: define which classes may be sent to external LLM/embedding/reranker providers; redact or route locally for disallowed classes.
- Storage: encrypt in transit/at rest; secret manager rather than `.env` for production.
- Logs/traces: structured identifiers, no raw restricted content by default.
- Retention: source, index, backup, audit and conversation memory have separate policies.
- Deletion/revocation: invalidate retrieval/response caches and derived artifacts; honor retention/legal hold before permanent removal.
- Test exfiltration routes through model output, tool calls, citation downloads and caches.

## Owner-provided retention and egress baseline

- MVP UI classification is `PUBLIC`/`INTERNAL`. Unknown classification denies; future `CONFIDENTIAL`/`RESTRICTED` handling is stricter than INTERNAL.
- PUBLIC may use an approved external provider. INTERNAL requires an approved provider, data-processing contract, appropriate residency and minimal excerpts. Fallback cannot bypass policy.
- Proposed retention: authenticated conversations 180 days, anonymous sessions 30 minutes idle/24 hours maximum, anonymous conversations 7 days, superseded versions 365 days, soft delete 30 days, audit 2 years, application logs 30 days and backups 30 days.
- Permanent deletion removes online DB, vector, object and cache data under control. Immutable backups may retain data until expiry; restore must replay revocation/tombstones before serving.
- Provider training on enterprise data is prohibited by contract; provider request retention remains pending and should be zero or the lowest available setting.
