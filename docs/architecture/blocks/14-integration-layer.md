# 14 — Integration Layer

## Trách nhiệm
connectors, adapters, MCP and external tool results.

## Đầu vào
Authorized structured tool requests.

## Đầu ra / contract
Validated, attributed responses from external systems.

## ARCH-OVERVIEW alignment

- The primary MVP integration boundary is typed Python/FastAPI Core ↔ Python worker jobs/results, policy checks, lifecycle events, pause/resume, errors and usage records. A future Rust trial must preserve this boundary.
- External connectors and MCP-style adapters remain read-only and allowlisted; side effects require separate approval.
- Workers and external systems do not import internal modules across the Core/worker boundary.
- Every request and result is versioned, authenticated, traceable and safe to retry or reject.

## Ranh giới bảo mật
Read-only MVP; side effects require explicit approval.

## Kiểm thử bàn giao
Tool schema, owner identity, cross-tenant and timeout.

## Tích hợp
Các module ứng dụng phải tuân thủ contract tương ứng trong `docs/contracts/`; thay đổi giao diện chung phải theo `docs/contracts/CHANGE-PROCESS.md`. Khối này không được tự ý vượt quyền hoặc quyết định trạng thái tài liệu ngoài quyền sở hữu.

## Definition of Done
- API/schema được phê duyệt; có tests kiểm chứng ít nhất một happy path, denial path và lỗi phụ thuộc.
- Log/trace không tiết lộ dữ liệu nhạy cảm.
- Tech Lead nhận được handoff và kết quả CI thực tế.

## Owner-provided baseline

- Public APIs use REST/HTTP JSON and OpenAPI 3.1 under `/api/v1`; worker payloads use JSON Schema with `schema_version`.
- Background work uses the PostgreSQL durable queue; service identities are short-lived and least-privileged.
- Every payload carries idempotency, request/correlation and trace metadata. Safe errors use a code/message/request-ID envelope.
- The queue and worker boundary rechecks tenant, ACL, policy version and document version on execution and resume.
