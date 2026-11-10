# 02 — API & Identity

## Trách nhiệm
HTTP boundary, authn, token/session, rate limits.

## Đầu vào
HTTP request + bearer token.

## Đầu ra / contract
Authenticated principal + request_id.

## ARCH-OVERVIEW alignment

- Python/FastAPI Core is the MVP owner of API, identity, sessions and request coordination; Rust is a benchmark candidate only.
- The current repository layout remains authoritative until an approved migration plan exists.
- The API creates authenticated question and ingestion jobs for Python workers.
- Employee activation is admin-provisioned email/password; Website Manager and System Admin require MFA.

## Ranh giới bảo mật
Validate issuer/audience/expiry; never trust client role claims.

## Kiểm thử bàn giao
Invalid token, expired session, request validation, rate limits.

## Tích hợp
Các module ứng dụng phải tuân thủ contract tương ứng trong `docs/contracts/`; thay đổi giao diện chung phải theo `docs/contracts/CHANGE-PROCESS.md`. Khối này không được tự ý vượt quyền hoặc quyết định trạng thái tài liệu ngoài quyền sở hữu.

## Definition of Done
- API/schema được phê duyệt; có tests kiểm chứng ít nhất một happy path, denial path và lỗi phụ thuộc.
- Log/trace không tiết lộ dữ liệu nhạy cảm.
- Tech Lead nhận được handoff và kết quả CI thực tế.

## Owner-provided baseline

- MVP API remains Python/FastAPI. Employee accounts are request-based and require administrator approval before activation.
- Public API uses REST/HTTP JSON, OpenAPI 3.1 and `/api/v1`; timestamps are UTC/RFC 3339.
- Access tokens target 15 minutes, sessions target 8 hours with 30-minute idle timeout. Five failed logins in 15 minutes trigger a 15-minute lock/throttle.
- Chairman, Website Manager and System Admin require MFA. System Admin cannot read user conversation bodies by default.
