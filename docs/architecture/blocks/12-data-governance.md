# 12 — Data Governance

## Trách nhiệm
classification, ownership, lineage, retention and data egress.

## Đầu vào
Document owner and policy requirements.

## Đầu ra / contract
Authoritative governance metadata/policies.

## ARCH-OVERVIEW alignment

- The Python/FastAPI Core owns classification, department/owner metadata, retention and provider-egress policy in the MVP.
- MVP product classification is PUBLIC or INTERNAL; additional sensitivity and provider rules require an approved policy decision.
- Unknown classification, missing owner or disallowed provider must fail closed.
- Governance decisions must be available to retrieval, model egress, logging, deletion and audit paths.

## Ranh giới bảo mật
Data classification and allowed provider before external calls.

## Kiểm thử bàn giao
Unknown classification denied, retention and revocation tested.

## Tích hợp
Các module ứng dụng phải tuân thủ contract tương ứng trong `docs/contracts/`; thay đổi giao diện chung phải theo `docs/contracts/CHANGE-PROCESS.md`. Khối này không được tự ý vượt quyền hoặc quyết định trạng thái tài liệu ngoài quyền sở hữu.

## Definition of Done
- API/schema được phê duyệt; có tests kiểm chứng ít nhất một happy path, denial path và lỗi phụ thuộc.
- Log/trace không tiết lộ dữ liệu nhạy cảm.
- Tech Lead nhận được handoff và kết quả CI thực tế.

## Owner-provided baseline

- Product classification is `PUBLIC`/`INTERNAL` for MVP. Unknown classification denies; future higher-sensitivity provider egress remains stricter.
- Proposed retention: conversations 180 days, anonymous sessions 30 minutes idle/24 hours max, anonymous conversations 7 days, superseded versions 365 days, soft-deleted documents 30 days, audit 2 years, application logs 30 days and backups 30 days.
- Legal hold overrides ordinary deletion. Restores must replay revocations/tombstones before retrieval is enabled.
