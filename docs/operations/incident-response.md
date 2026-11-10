# Incident response — initial template

## Triggers
Unauthorized retrieval, exfiltration suspicion, leaked token, malicious upload, incorrect ACL/index state, unusable model API.

## Steps
1. Contain: disable affected tool, tenant, index or provider route while preserving evidence.
2. Rotate compromised credentials; revoke sessions if needed.
3. Identify affected document/version, users, trace IDs and cache keys.
4. Remove ACTIVE access and invalidate derivatives and caches.
5. Investigate with redacted audit records, record timeline and owner notifications.
6. Remediate, re-run security suite and owner-approved restoration.

Never publish sensitive raw logs during incident triage.

## Owner-provided severity baseline

- **P0:** cross-tenant or unauthorized-content disclosure, or severe compromise. Alert Security Incident Owner and System Admin on-call immediately, 24/7.
- **P1:** broad outage or inability to serve questions. Alert Technical Owner and System Admin on-call immediately, 24/7.
- **P2:** degraded service, mass ingestion failure or significant latency increase. Email during working hours and show on dashboard.
- **P3:** minor or self-recovered failure. Dashboard/reporting only unless the approved alert policy says otherwise.

Containment must include cache/index invalidation, ACL and ACTIVE-version revocation, checkpoint staleness checks and tombstone replay after restore. Raw prompts, outputs and conversation bodies are not exposed by default. Actual recipient addresses remain a production prerequisite.
