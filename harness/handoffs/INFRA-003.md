# Handoff — INFRA-003

## Status

READY_FOR_MAIN_REVIEW — provider-neutral local monitoring baseline and config
smoke tests are complete. No production resource was provisioned.

## Delivered

- OpenTelemetry Collector OTLP gRPC/HTTP receiver with memory limiting,
  batching and allowlisted privacy deletion for user/resource/content/secret
  attributes.
- Prometheus scrape configuration and 30-day local retention setting.
- Synthetic P0/P1/P2/P3-compatible alert rules with incident runbook links.
- Private Grafana Prometheus datasource and minimal API/authorization dashboard.
- Local Alertmanager route with no external recipient configured.
- Loopback-only Docker Compose stack with read-only mounts and
  `no-new-privileges` for the four monitoring services.
- Deployment runbook commands and explicit provider/cloud/recipient boundary.

## Validation evidence

Executed from the repository root:

    docker compose -f infra/monitoring/compose.yml config --quiet
    PASS

    /tmp/erag-auth-venv/bin/python -m pytest -q tests/integration/test_monitoring_config.py tests/integration/test_audit_identity.py
    PASS — 13 passed

The integration tests validate config file presence, dashboard JSON, privacy
processor markers, Prometheus/alert wiring, loopback bindings, hardening flags,
dashboard panels and provider/recipient deferral. Identity audit integration
continues to pass against synthetic in-memory data.

## Boundaries and residual risks

- This is a local configuration baseline; the live images were not pulled or
  deployed, and no cloud account, alert recipient or API key was used.
- The current AUDIT-001 sink is process-local; OpenTelemetry export and durable
  audit/WORM persistence require a later application integration.
- Traces/log backend, production retention, private network policy, backups,
  dashboard access control and on-call recipients remain owner-approved release
  decisions.
- Queue, ingestion, provider and RAG metric signals are configured as future
  metric names and need live verification at RELEASE-001.

No commit or push was performed by this task.
