# 13 — Memory & Caching

## Trách nhiệm
per-conversation memory, summaries, prompt/retrieval cache.

## Đầu vào
Authorized conversation + policy version.

## Đầu ra / contract
Scoped memory and cache entries.

## ARCH-OVERVIEW alignment

- The Python/FastAPI Core and Python workers use approved interfaces for conversation state, cache and durable checkpoints.
- Memory and retrieval/answer caches are scoped by tenant, principal/entitlements, policy version, corpus/index version, query and model configuration.
- Invalidate or bypass entries on ACL, role, classification, ACTIVE-version, revocation or deletion changes.
- Semantic similarity answer caching and volatile-only critical checkpoints are outside the MVP.

## Ranh giới bảo mật
No cross-user leakage; ACL and version invalidation.

## Kiểm thử bàn giao
Revoked access, cache key isolation, memory deletion.

## Tích hợp
Các module ứng dụng phải tuân thủ contract tương ứng trong `docs/contracts/`; thay đổi giao diện chung phải theo `docs/contracts/CHANGE-PROCESS.md`. Khối này không được tự ý vượt quyền hoặc quyết định trạng thái tài liệu ngoài quyền sở hữu.

## Definition of Done
- API/schema được phê duyệt; có tests kiểm chứng ít nhất một happy path, denial path và lỗi phụ thuộc.
- Log/trace không tiết lộ dữ liệu nhạy cảm.
- Tech Lead nhận được handoff và kết quả CI thực tế.

## Owner-provided baseline

- Authenticated conversations retain for 180 days from last activity; anonymous sessions expire after 30 minutes idle and at most 24 hours; anonymous conversations retain for 7 days.
- Soft delete, ACL revocation, ACTIVE-version changes and policy changes invalidate/bypass retrieval and answer caches.
- Redis can hold cache/rate-limit/short-lived state, but PostgreSQL remains the durable checkpoint authority.
