# 03 — Authorization

## Trách nhiệm
PDP+PEP for tenant, role, attributes, document ACL, tool actions.

## Đầu vào
Principal, action, resource, policy version.

## Đầu ra / contract
ALLOW/DENY plus eligible read scope.

## ARCH-OVERVIEW alignment

- The Python/FastAPI Core owns the trusted PDP and PEPs in the MVP; a Rust replacement must preserve the same policy contract.
- Python workers must recheck through an approved trust interface before retrieval, source access, cache reuse or job resume.
- Enforce policy at API, queue acceptance/resume, tool gateway, every retrieval branch, parent expansion, citation/source access and memory/cache reuse.
- Client claims, LLM output, queue payloads, vector indexes and retrieved text cannot grant permission.

## Ranh giới bảo mật
Deny by default; recheck on tool, retrieval and source fetch.

## Kiểm thử bàn giao
Cross-tenant, revocation, role vs action, outage fail-closed.

## Tích hợp
Các module ứng dụng phải tuân thủ contract tương ứng trong `docs/contracts/`; thay đổi giao diện chung phải theo `docs/contracts/CHANGE-PROCESS.md`. Khối này không được tự ý vượt quyền hoặc quyết định trạng thái tài liệu ngoài quyền sở hữu.

## Definition of Done
- API/schema được phê duyệt; có tests kiểm chứng ít nhất một happy path, denial path và lỗi phụ thuộc.
- Log/trace không tiết lộ dữ liệu nhạy cảm.
- Tech Lead nhận được handoff và kết quả CI thực tế.

## Owner-provided baseline

- Use RBAC + department membership + document ACL with default deny.
- Explicit deny wins over role allow. Chairman's broad read access cannot bypass an explicit deny.
- MVP product classification is `PUBLIC`/`INTERNAL`; unknown or stale policy denies.
- Every worker resume, retrieval branch, chunk expansion, citation and source download rechecks tenant, ACL, policy version and document version.
