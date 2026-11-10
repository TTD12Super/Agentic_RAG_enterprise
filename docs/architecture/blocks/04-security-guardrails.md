# 04 — Security & Guardrails

## Trách nhiệm
input, file, context, tool and output inspection/DLP.

## Đầu vào
Untrusted input/document/tool result + security policy.

## Đầu ra / contract
Pass/block/flag/approval decision.

## ARCH-OVERVIEW alignment

- Request and policy controls sit in the Python/FastAPI Core MVP; file, context, tool-result and output safeguards run in Python workers.
- Guardrails are defense-in-depth and cannot replace backend authorization.
- MVP tools are allowlisted and read-only; external model calls pass the approved Python gateway and egress policy.
- Do not treat documents, retrieved chunks or tool output as executable instructions.

## Ranh giới bảo mật
Classifier cannot replace authn/authz; document text never instructions.

## Kiểm thử bàn giao
Direct/indirect injection, exfiltration, secrets and unsafe tools.

## Tích hợp
Các module ứng dụng phải tuân thủ contract tương ứng trong `docs/contracts/`; thay đổi giao diện chung phải theo `docs/contracts/CHANGE-PROCESS.md`. Khối này không được tự ý vượt quyền hoặc quyết định trạng thái tài liệu ngoài quyền sở hữu.

## Definition of Done
- API/schema được phê duyệt; có tests kiểm chứng ít nhất một happy path, denial path và lỗi phụ thuộc.
- Log/trace không tiết lộ dữ liệu nhạy cảm.
- Tech Lead nhận được handoff và kết quả CI thực tế.

## Owner-provided baseline

- MVP product classification is `PUBLIC`/`INTERNAL`; unknown data denies and future higher-sensitivity egress is stricter.
- Tool registry is read-only and limited to three approved tools. Tool output and document text remain untrusted data.
- Upload guardrails enforce the 200 MB byte limit, magic bytes, checksum, malware scan, parser resource limits and OCR quality checks.
