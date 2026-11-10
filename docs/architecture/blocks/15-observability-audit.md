# 15 — Observability & Audit

## Trách nhiệm
traces, metrics, security events and retention.

## Đầu vào
Request/job events and usage.

## Đầu ra / contract
Correlated traces, minimal audit trails, alerts.

## ARCH-OVERVIEW alignment

- Instrument the Python/FastAPI Core, queue, Python RAG workers, ingestion workers, model gateway and storage boundaries with shared correlation IDs.
- The Core owns authorized business-audit visibility; operational telemetry is separately access-controlled.
- Record queue wait, processing, maintenance wait, model/fallback, retrieval, citation and completion/error stages.
- Dashboard and system-generated alerts are allowed; the chatbot is not an autonomous email sender.

## Ranh giới bảo mật
Never log credentials or raw confidential content by default.

## Kiểm thử bàn giao
Trace correlation, audit tamper resistance, privacy checks.

## Tích hợp
Các module ứng dụng phải tuân thủ contract tương ứng trong `docs/contracts/`; thay đổi giao diện chung phải theo `docs/contracts/CHANGE-PROCESS.md`. Khối này không được tự ý vượt quyền hoặc quyết định trạng thái tài liệu ngoài quyền sở hữu.

## Definition of Done
- API/schema được phê duyệt; có tests kiểm chứng ít nhất một happy path, denial path và lỗi phụ thuộc.
- Log/trace không tiết lộ dữ liệu nhạy cảm.
- Tech Lead nhận được handoff và kết quả CI thực tế.

## Owner-provided baseline

- Audit is append-only, preferably immutable/WORM, with two-year retention. Ordinary application logs retain for 30 days.
- Do not log raw prompts, outputs or conversation bodies by default. Investigation access is time-limited, approved and audited.
- P0/P1 alerts are immediate for the security/technical on-call; P2/P3 follow dashboard and working-hours notification policy.

## Monitoring service architecture

The monitoring service is a separate operational plane. It observes the application and infrastructure but never becomes an authorization authority or a source of document content.

### Ownership boundary

- Backend owns `AUDIT-001` and application-side telemetry: event names, correlation IDs, append-only business audit events and redaction before telemetry leaves the application boundary.
- `INFRA-003` owns the monitoring platform: OpenTelemetry Collector configuration, exporters, Prometheus, Grafana, Alertmanager, retention settings and platform smoke tests.
- `AUDIT-001` must complete before `INFRA-003` is integrated so the platform consumes a stable application telemetry shape. Neither task grants permission to expose raw prompts, answers, document text or restricted conversation bodies.
- `AUDIT-001` verifies the real identity/API foundation. `RELEASE-001` verifies end-to-end request-to-policy-to-source telemetry after ingestion and RAG exist.

~~~mermaid
flowchart LR
    FE["Vercel Frontend"]
    API["FastAPI API"]
    RAG["RAG Worker"]
    ING["Ingestion Worker"]
    DB["PostgreSQL"]
    QD["Qdrant"]
    REDIS["Redis"]
    LLM["External LLM Provider"]

    API --> OTEL["OpenTelemetry SDK / Collector"]
    RAG --> OTEL
    ING --> OTEL
    FE -->|privacy-safe web vitals| OTEL
    DB --> EXP["DB / service exporters"]
    QD --> EXP
    REDIS --> EXP
    EXP --> OTEL

    OTEL --> PROM["Prometheus metrics store"]
    OTEL --> TRACE["Trace/log backend (provider TBD)"]
    PROM --> GRAF["Grafana dashboards"]
    PROM --> ALERT["Alertmanager"]
    ALERT --> NOTIFY["Approved email/on-call channels"]

    API --> DB
    RAG --> DB
    ING --> DB
    RAG --> QD
    RAG --> LLM
    API --> REDIS
~~~

### Components and responsibilities

| Component | Responsibility | MVP status |
|---|---|---|
| OpenTelemetry SDK | Emit traces, metrics and structured events from API/workers | `AUDIT-001` |
| OpenTelemetry Collector | Receive OTLP, apply platform routing/filtering and route telemetry | `INFRA-003` |
| Prometheus | Store/query time-series metrics and evaluate alert expressions | Proposed |
| Grafana | Operations dashboards with role-limited access | Proposed |
| Alertmanager | Deduplicate, group and route P0–P3 alerts | Proposed |
| Trace/log backend | Store traces and redacted operational logs | Provider/backend pending |
| Exporters | Expose PostgreSQL, Qdrant, Redis and runtime health metrics | `INFRA-003` |

### Required metric groups

- **API:** request count, status code, latency, timeout, rate-limit and maintenance responses.
- **Queue:** queued jobs, queue age, claim latency, lease expiry, retries, pauses, cancellations and saturation.
- **RAG:** retrieval rounds, candidate counts, reranker latency, evidence sufficiency, citation verification, LLM latency, token usage and fallback count.
- **Ingestion:** upload bytes, parse/OCR duration, pages/sheets/rows, chunk count, embedding/index duration, retry and failure codes.
- **Dependencies:** PostgreSQL, Qdrant, Redis, object storage and external LLM health/latency/error rate.
- **Security:** denied requests, policy failures, cross-tenant test failures, suspicious tool attempts and secret/configuration errors.

### Data and security rules

- Never emit API keys, tokens, passwords, signed URLs, raw prompts, full answers, document text or restricted conversation bodies.
- Use tenant-safe aggregated labels; do not use raw user IDs, document IDs or query text as unbounded metric labels.
- Keep business audit events separate from high-volume operational metrics.
- Retention target: operational application logs 30 days; audit events 2 years; exact trace retention depends on the selected backend and privacy policy.
- Prometheus/Grafana access is private and role-limited. The monitoring plane cannot grant or revoke application access.
- Alert payloads contain a redacted summary, severity, service, metric, trace ID and runbook link—not sensitive content.

### Initial alert rules

- **P0:** unauthorized/cross-tenant disclosure signal, policy bypass signal or credential compromise.
- **P1:** API unavailable, database unavailable, queue unable to claim work, or widespread LLM failure.
- **P2:** ingestion failure spike, sustained latency degradation, queue age breach, Qdrant/Redis degradation or repeated fallback.
- **P3:** isolated retryable failure, exporter missing data or non-user-impacting capacity warning.

P0/P1 alerts route immediately to the approved security/technical on-call. P2 alerts route during working hours. P3 alerts remain dashboard/reporting unless the approved alert policy says otherwise. Actual recipients and trace/log backend remain pending.

### Deployment boundaries

- Local development may run Prometheus, Grafana and exporters through Docker Compose after `INFRA-001`.
- Student/demo deployments may use a managed monitoring service or a small self-managed stack, but must not claim production retention or availability.
- Production monitoring must run in a private network or protected control plane with separate credentials, backup/restore and configuration validation.
- `AUDIT-001` owns application telemetry and audit instrumentation; `INFRA-003` owns implementation of the monitoring platform baseline. No production monitoring resource is created by documenting either task.
