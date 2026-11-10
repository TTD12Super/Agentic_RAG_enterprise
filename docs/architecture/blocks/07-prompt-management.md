# 07 — Prompt Management

## Trách nhiệm
versioned system/task prompts, context assembler.

## Đầu vào
Instructions + validated user query + authorized evidence.

## Đầu ra / contract
Structured model messages + prompt version.

## ARCH-OVERVIEW alignment

- Python workers assemble versioned system, planner and answer prompts.
- Authorized evidence is quoted as untrusted data and cannot override higher-priority instructions.
- Prompt text never grants roles, scope, tool permission or document access.
- Prompt version and assembly metadata feed regression evaluation and privacy-safe audit.

## Ranh giới bảo mật
Keep untrusted evidence separate from high-priority instructions.

## Kiểm thử bàn giao
Prompt injection boundaries and version regression.

## Tích hợp
Các module ứng dụng phải tuân thủ contract tương ứng trong `docs/contracts/`; thay đổi giao diện chung phải theo `docs/contracts/CHANGE-PROCESS.md`. Khối này không được tự ý vượt quyền hoặc quyết định trạng thái tài liệu ngoài quyền sở hữu.

## Definition of Done
- API/schema được phê duyệt; có tests kiểm chứng ít nhất một happy path, denial path và lỗi phụ thuộc.
- Log/trace không tiết lộ dữ liệu nhạy cảm.
- Tech Lead nhận được handoff và kết quả CI thực tế.

## Owner-provided baseline

- Git is the prompt source of truth; the database stores active prompt metadata and audit references.
- Planner/router/tool outputs validate JSON Schemas. Answers record prompt, model, retrieval-config and policy versions.
- Prompt promotion requires an authorized reviewer and Golden Dataset, citation, security and prompt-injection regression tests.
