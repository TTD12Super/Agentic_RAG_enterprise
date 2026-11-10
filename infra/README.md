# Infrastructure — Enterprise Agentic RAG

## 1. Overview

The Infrastructure module provides development environments, containerization, service configuration, monitoring, and deployment infrastructure for Enterprise Agentic RAG.

It supports reproducible environments, operational reliability, and secure service integration.

**Status:** Development-service and migration-runner baseline implemented; production infrastructure and monitoring remain pending.

## 2. Technology Stack

- Containerization: Docker
- Service Orchestration: Docker Compose (development)
- Backend Runtime: Python / FastAPI
- Primary Database: PostgreSQL
- Vector Database: Qdrant
- Cache: Redis (optional)
- Frontend Runtime: Node.js
- CI/CD: GitHub Actions
- Production Infrastructure: Pending approved architecture decisions
- Monitoring: Follow approved observability architecture

### Monitoring service baseline

- Backend owns `AUDIT-001`: application-side OpenTelemetry instrumentation, event names, correlation IDs and redaction before export.
- `INFRA-003` owns the OpenTelemetry Collector, exporters, Prometheus metrics, Grafana dashboards and Alertmanager routing.
- Prometheus stores/query metrics; Grafana provides private dashboards; Alertmanager routes P0–P3 notifications.
- A trace/log backend remains provider-dependent and must receive only redacted telemetry.
- The monitoring plane is operational only; it cannot make authorization decisions or receive raw document/conversation content.
- Platform implementation is tracked by `INFRA-003`; application telemetry implementation is tracked by `AUDIT-001`; `infra/monitoring/` currently contains placeholders only.

## 2.1 Student and production profiles

### Student/demo profile A — managed

- Vercel hosts the frontend.
- Azure for Students hosts containerized FastAPI, RAG and ingestion services where the student subscription/credit permits.
- Qdrant Cloud Free is used only for development/test vectors.
- External LLM API keys are stored in a provider secret store and spending-capped separately from cloud credits.

### Student/demo profile B — self-managed

- Vercel hosts the frontend.
- An Oracle Always Free VM runs Docker containers for the FastAPI API, RAG worker, ingestion worker and development data services.
- Manual backup/export and restore verification are mandatory; this profile is not production-ready.

### Production profile

Cloud provider, region, private network, managed PostgreSQL, object storage, Qdrant tier, secret manager and monitoring remain pending approval. Free student tiers must not be used as evidence of production capacity, availability, backup or security.

## 3. Project Structure

```text
infra/
├── docker/          # Container and service configurations
├── monitoring/      # Monitoring and observability configuration
├── scripts/         # Infrastructure automation utilities
├── AGENTS.md
└── README.md
```

Directories represent planned infrastructure boundaries and may contain placeholders.

The local development baseline is `infra/docker/development.compose.yml`. It
starts only a disposable PostgreSQL service on loopback port 55433. The
Backend-owned Alembic chain is executed through `infra/scripts/migrate.sh`;
DevOps owns service startup, upgrade/rollback orchestration and cleanup, not
schema definitions.

## 4. Architecture & Conventions

- Follow approved infrastructure architecture.
- Backend owns PostgreSQL schema and migration definitions through `DB-001`; DevOps owns only database runtime infrastructure, migration execution and rollback orchestration.
- Maintain reproducible development environments.
- Keep environment configurations isolated.
- Reuse existing infrastructure definitions.
- Avoid unnecessary services and dependencies.
- Follow approved networking and storage requirements.
- Preserve application data integrity.
- Keep secrets outside source control.
- Use approved secret-management mechanisms.
- Do not modify production infrastructure without authorization.
- Maintain compatibility with Backend and Frontend requirements.

## 5. Development & Validation

Before implementation:

1. Inspect existing infrastructure configurations.
2. Read the assigned task and acceptance criteria.
3. Verify service dependencies.
4. Identify affected environments.
5. Review approved security requirements.
6. Implement only authorized infrastructure changes.
7. Validate configurations and service compatibility.
8. Report actual validation results and operational risks.

Use commands defined by the existing infrastructure configuration.

Do not assume services are available without verification.

## 6. References

- `../AGENTS.md` — Repository governance.
- `AGENTS.md` — Infrastructure-specific instructions.
- `../docs/architecture/` — System architecture.
- `../docs/architecture/blocks/17-infrastructure-llmops.md` — Infrastructure architecture.
- `../docs/operations/` — Deployment and operational procedures.
- `../docs/security/` — Security requirements.
- `../docs/testing/` — Validation standards.
- `../docs/git-worktrees.md` — Git governance.
- `../harness/tasks/tasks.json` — Tasks and dependencies.
