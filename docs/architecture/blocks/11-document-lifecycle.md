# 11 — Document Lifecycle

## Trách nhiệm
quarantine, approval, parse, version, index, publish, revoke.

## Đầu vào
Authorized upload + document governance policy.

## Đầu ra / contract
ACTIVE indexed version or FAILED job.

## ARCH-OVERVIEW alignment

- The Python/FastAPI Core owns document metadata, review decisions, publication, version pointers and maintenance coordination in the MVP.
- Independent Python ingestion workers validate, extract, chunk, embed and stage indexes.
- The flow is Review 1 → processing/validation → Review 2 → atomic ACTIVE publication.
- Upload maintenance must quiesce new chat work, preserve safe checkpoints, invalidate affected caches and release or fail safely.

## Ranh giới bảo mật
Never expose STAGING or denied files; clean derivative artifacts.

## Kiểm thử bàn giao
Malware, parsing failure, version publish and atomic swap.

## Tích hợp
Các module ứng dụng phải tuân thủ contract tương ứng trong `docs/contracts/`; thay đổi giao diện chung phải theo `docs/contracts/CHANGE-PROCESS.md`. Khối này không được tự ý vượt quyền hoặc quyết định trạng thái tài liệu ngoài quyền sở hữu.

## Definition of Done
- API/schema được phê duyệt; có tests kiểm chứng ít nhất một happy path, denial path và lỗi phụ thuộc.
- Log/trace không tiết lộ dữ liệu nhạy cảm.
- Tech Lead nhận được handoff và kết quả CI thực tế.

## Owner-provided baseline

- Supported files are `.pdf`, `.docx` and `.xlsx`, maximum 200,000,000 bytes; `.doc` and `.xls` are rejected.
- Same-admin double review is allowed. Approval expires after 30 minutes; maintenance watchdog is 60 minutes and never auto-approves.
- Retry is limited to three attempts for an unchanged version. Failed/rejected versions do not replace the prior ACTIVE version.
- Soft delete blocks retrieval immediately; permanent deletion respects retention/legal hold and restore tombstones.
