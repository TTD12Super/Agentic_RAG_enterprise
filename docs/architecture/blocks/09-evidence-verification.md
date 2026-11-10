# 09 — Evidence Verification

## Trách nhiệm
claim verification, citation/source/version checks.

## Đầu vào
Draft answer + authorized source spans.

## Đầu ra / contract
Verified claims, citations, revise/abstain.

## ARCH-OVERVIEW alignment

- Python workers verify claim-to-evidence support and provenance.
- The Python/FastAPI Core reauthorizes citation and original-source access.
- Evidence is insufficient when no authorized support exists; partial answers and disclosed conflicts are valid outcomes.
- Verification does not promise zero hallucinations or replace authorization.

## Ranh giới bảo mật
Never assert a hallucination detector guarantees correctness.

## Kiểm thử bàn giao
Fabricated citation, unsupported claim, conflicting versions.

## Tích hợp
Các module ứng dụng phải tuân thủ contract tương ứng trong `docs/contracts/`; thay đổi giao diện chung phải theo `docs/contracts/CHANGE-PROCESS.md`. Khối này không được tự ý vượt quyền hoặc quyết định trạng thái tài liệu ngoài quyền sở hữu.

## Definition of Done
- API/schema được phê duyệt; có tests kiểm chứng ít nhất một happy path, denial path và lỗi phụ thuộc.
- Log/trace không tiết lộ dữ liệu nhạy cảm.
- Tech Lead nhận được handoff và kết quả CI thực tế.

## Owner-provided baseline

- Answer in the user's language unless explicitly requested otherwise.
- Partial evidence is allowed only with an explicit unsupported portion; no evidence returns `INSUFFICIENT_EVIDENCE`.
- Conflicting approved sources are disclosed rather than silently harmonized.
- Citation preview/download rechecks current authorization and source version.
