# 16 — Evaluation & Feedback

## Trách nhiệm
golden dataset, security/regression eval, feedback labels.

## Đầu vào
Queries, expected sources, actual execution traces.

## Đầu ra / contract
Recall/nDCG/grounding/security report and release gates.

## ARCH-OVERVIEW alignment

- Python evaluation covers dense-only, Hybrid RAG, reranking, parent-child retrieval and bounded single-agent improvements.
- The initial corpus target is about 100 documents; the 500-user capacity target requires a defined workload and load-test evidence.
- The Python/FastAPI Core exposes authorized feedback and dashboard data without exposing private model reasoning or restricted content.
- No release claim is valid without reproducible Golden Dataset, security-negative and latency/cost evidence.

## Ranh giới bảo mật
No production release based on anecdotal answers.

## Kiểm thử bàn giao
Adversarial and role-matrix regression tests.

## Tích hợp
Các module ứng dụng phải tuân thủ contract tương ứng trong `docs/contracts/`; thay đổi giao diện chung phải theo `docs/contracts/CHANGE-PROCESS.md`. Khối này không được tự ý vượt quyền hoặc quyết định trạng thái tài liệu ngoài quyền sở hữu.

## Definition of Done
- API/schema được phê duyệt; có tests kiểm chứng ít nhất một happy path, denial path và lỗi phụ thuộc.
- Log/trace không tiết lộ dữ liệu nhạy cảm.
- Tech Lead nhận được handoff và kết quả CI thực tế.

## Owner-provided baseline

- Initial Golden Dataset target is at least 200 cases, 70% Vietnamese/30% English, 70% simple/30% complex, with at least 50 permission-negative and 30 unanswerable cases.
- Proposed gates: Recall@10 ≥90%, citation accuracy ≥95%, answer correctness ≥90%, no-answer accuracy ≥90%, zero unauthorized retrieval and p95 simple/complex ≤30/90 seconds at the load profile.
- These are targets pending benchmark and Project Owner approval, not demonstrated capabilities.
