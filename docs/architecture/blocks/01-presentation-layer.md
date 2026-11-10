# 01 — Presentation Layer

## Trách nhiệm
web UI for chat/admin/citation/approval.

## Đầu vào
User action + session context.

## Đầu ra / contract
Validated API request; rendered answer and source link.

## ARCH-OVERVIEW alignment

- React + TypeScript client; anonymous, employee, Chairman and admin views.
- Display QUEUED, PROCESSING, MAINTENANCE, final and controlled failure states.
- MVP returns a complete answer without token streaming.
- Source expansion and original-document opening always go back through the Core authorization boundary.

## Ranh giới bảo mật
Frontend hiding controls is not a security boundary.

## Kiểm thử bàn giao
Frontend smoke/E2E role views and citation behavior.

## Tích hợp
Các module ứng dụng phải tuân thủ contract tương ứng trong `docs/contracts/`; thay đổi giao diện chung phải theo `docs/contracts/CHANGE-PROCESS.md`. Khối này không được tự ý vượt quyền hoặc quyết định trạng thái tài liệu ngoài quyền sở hữu.

## Definition of Done
- API/schema được phê duyệt; có tests kiểm chứng ít nhất một happy path, denial path và lỗi phụ thuộc.
- Log/trace không tiết lộ dữ liệu nhạy cảm.
- Tech Lead nhận được handoff và kết quả CI thực tế.

## Owner-provided behavior baseline

- The UI must show `QUEUED`, `PROCESSING`, `PAUSED`, `MAINTENANCE`, completed and controlled failure states without token streaming.
- Citation details are collapsed by default but a visible source indicator remains available. Preview and original download use separate backend authorization checks.
- Queue saturation shows `503`/`Retry-After`; rate limiting shows `429`; maintenance shows `503 MAINTENANCE_ACTIVE`.
- Exact layout, components and interaction design remain governed by the Project Owner's Figma files.
