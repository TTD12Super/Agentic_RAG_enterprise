# 10 — Knowledge Management

## Trách nhiệm
taxonomy, structured metadata, parent-child references.

## Đầu vào
Parsed headings/entities/relationships.

## Đầu ra / contract
Searchable catalog and provenance graph/relations.

## ARCH-OVERVIEW alignment

- The Python/FastAPI Core owns document metadata, collections, departments, permissions and searchable catalog state in the MVP.
- Python ingestion workers produce parsed headings, tables, parent-child references and source provenance through versioned contracts.
- Metadata and relationship indexes are derived views; they cannot broaden the authoritative policy.
- Keep the logical capability in the modular monolith boundary; do not split it into a separate service without an approved ADR.

## Ranh giới bảo mật
Metadata inheriting access must not loosen ACL.

## Kiểm thử bàn giao
Parent-child integrity, taxonomy filter and source tracing.

## Tích hợp
Các module ứng dụng phải tuân thủ contract tương ứng trong `docs/contracts/`; thay đổi giao diện chung phải theo `docs/contracts/CHANGE-PROCESS.md`. Khối này không được tự ý vượt quyền hoặc quyết định trạng thái tài liệu ngoài quyền sở hữu.

## Definition of Done
- API/schema được phê duyệt; có tests kiểm chứng ít nhất một happy path, denial path và lỗi phụ thuộc.
- Log/trace không tiết lộ dữ liệu nhạy cảm.
- Tech Lead nhận được handoff và kết quả CI thực tế.
