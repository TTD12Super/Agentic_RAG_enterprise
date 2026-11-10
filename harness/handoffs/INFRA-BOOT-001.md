# Handoff — INFRA-BOOT-001

## Task

- **Owner:** DevOps
- **Scope:** Isolated disposable PostgreSQL for migration tests
- **Status:** READY_FOR_INTEGRATION
- **Inputs read:** `AGENTS.md`, `infra/AGENTS.md`, `infra/README.md`, `docs/database/database.md`, `docs/contracts/v1-baseline.md`, `docs/operations/multi-agent-production-workflow.md`, `docs/testing/README.md`, and the `INFRA-BOOT-001` task definition in `harness/tasks/tasks.json`.

## Changed files

- `infra/docker/postgres-test.compose.yml`
- `harness/handoffs/INFRA-BOOT-001.md`

No backend, frontend, database documentation, contract, task registry, `.env`, data directory or production resource was changed.

## Service definition

- Image: `postgres:17-alpine`.
- Compose project used for validation: `enterprise-rag-pg-test`.
- Database/user: `enterprise_rag_test`.
- Password: `synthetic_only_not_secret` (disposable fixture value, not a secret).
- Host port: `127.0.0.1:55432` only; it is not bound to a public interface.
- Storage: PostgreSQL data directory is a container `tmpfs`; no named or bind volume is declared.
- Network: Compose creates a project-scoped bridge network; the only host access is the explicit loopback port mapping. Docker Desktop did not publish the host port when `internal: true` was used, so that flag is intentionally omitted.
- Restart policy: disabled.
- Healthcheck: `pg_isready` against the synthetic database and user.

Synthetic connection settings for DB-001 local migration tests:

```text
DB_HOST=127.0.0.1
DB_PORT=55432
DB_NAME=enterprise_rag_test
DB_USER=enterprise_rag_test
DB_PASSWORD=synthetic_only_not_secret
DATABASE_URL=postgresql://enterprise_rag_test:synthetic_only_not_secret@127.0.0.1:55432/enterprise_rag_test
```

These values are intentionally disposable and must never be used for staging or production.

## Exact startup and validation commands

Run from the repository root:

```sh
docker compose -f infra/docker/postgres-test.compose.yml -p enterprise-rag-pg-test config --quiet
docker compose -f infra/docker/postgres-test.compose.yml -p enterprise-rag-pg-test up -d --wait
docker compose -f infra/docker/postgres-test.compose.yml -p enterprise-rag-pg-test ps
docker compose -f infra/docker/postgres-test.compose.yml -p enterprise-rag-pg-test exec -T postgres pg_isready -U enterprise_rag_test -d enterprise_rag_test
docker compose -f infra/docker/postgres-test.compose.yml -p enterprise-rag-pg-test exec -T postgres psql -v ON_ERROR_STOP=1 -U enterprise_rag_test -d enterprise_rag_test -Atc "SELECT current_database() || '|' || current_user || '|' || current_setting('server_version_num')"
```

The final query is a synthetic connection check only; it does not create or read project data.

## Validation evidence

Executed on 2026-11-10 with Docker Engine 29.4.1 and Docker Compose v5.1.3:

| Check | Result |
|---|---|
| `docker compose ... config --quiet` | PASS, exit 0 |
| `docker compose ... up -d --wait` | PASS, exit 0 |
| `docker compose ... ps` | PASS, service healthy, port `127.0.0.1:55432->5432/tcp` |
| `pg_isready` inside container | PASS, accepting connections |
| Synthetic `psql` query inside service | PASS, returned `enterprise_rag_test|enterprise_rag_test|170011` |
| Synthetic `psql` query through published host port | PASS, returned `enterprise_rag_test|enterprise_rag_test|170011` |
| `docker inspect` isolation check | PASS, restart `no`, port binding loopback-only, `/var/lib/postgresql/data` mounted as tmpfs, no persistent volume |
| Real credentials/cloud/paid resource use | NOT USED |
| Migration execution | NOT RUN; owned by DB-001 |

## Isolation and cleanup

Isolation properties are declarative and were inspected in the Compose config:

- Only one PostgreSQL service is defined.
- The host bind is loopback-only.
- The network is project-scoped to the Compose project; no other service is defined.
- The database directory is `tmpfs`; no persistent volume is created.
- Credentials and database names are synthetic fixture values.

Cleanup targets only the named Compose project and its network/container:

```sh
docker compose -f infra/docker/postgres-test.compose.yml -p enterprise-rag-pg-test down --remove-orphans
```

After cleanup, verify the targeted project is absent and the host port is closed:

```sh
docker compose -f infra/docker/postgres-test.compose.yml -p enterprise-rag-pg-test ps
docker ps -a --filter name=enterprise-rag-pg-test-postgres-1 --format '{{.Names}}'
docker network ls --filter name=enterprise-rag-pg-test_postgres_test --format '{{.Name}}'
docker volume ls --filter label=com.docker.compose.project=enterprise-rag-pg-test --format '{{.Name}}'
nc -z 127.0.0.1 55432  # expected to fail after cleanup
```

Observed cleanup: Compose reported container/network removal; the targeted `docker ps`, network and volume filters returned no rows; `nc` reported `port-closed`. Do not run broad `docker system prune`, delete unrelated containers, or remove host data. No persistent database volume is mounted for this service.

## Integration boundary and next task

`DB-001` owns Alembic migrations, schema definitions, migration tests and rollback behavior. It may use the synthetic settings above and must run migrations against a freshly started instance. `INFRA-001` may later reuse this pattern when wiring reproducible development services, but must not turn this disposable profile into a production database.

The required four-family/40-case implementation test package remains a QA/Main Agent gate. This task provides the infrastructure smoke/config evidence only; it does not alter shared test directories.

## Unresolved decisions and risks

- Cloud provider, production PostgreSQL topology, secret manager and network policy remain pending decisions and are intentionally out of scope.
- This profile is disposable and has no backup/restore durability; it is unsuitable for staging or production.
- The validation proves container startup and a synthetic connection, not DB-001 migration correctness.

## Commit/push

Not performed, per task instruction. Main Agent owns phase integration and the phase commit/push gate.
