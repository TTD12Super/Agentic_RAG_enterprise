# 06 — Model Management

## Trách nhiệm
model gateway for LLM, embedding, reranker, budget/fallback.

## Đầu vào
Model task request + data classification.

## Đầu ra / contract
Model output, embedding, rank scores, usage.

## ARCH-OVERVIEW alignment

- Python model gateway is the only approved runtime path to external LLM, embedding and reranking providers.
- It owns approved routing, timeout, bounded retry, fallback, token limits and usage accounting.
- Egress is checked before every provider call using data classification and provider policy.
- Provider, model and cloud choices remain proposed until their ADR and contracts are approved.

## Ranh giới bảo mật
Sensitive data egress policy before external providers.

## Kiểm thử bàn giao
Model errors, timeouts, deterministic schema parsing, budget checks.

## Tích hợp
Các module ứng dụng phải tuân thủ contract tương ứng trong `docs/contracts/`; thay đổi giao diện chung phải theo `docs/contracts/CHANGE-PROCESS.md`. Khối này không được tự ý vượt quyền hoặc quyết định trạng thái tài liệu ngoài quyền sở hữu.

## Definition of Done
- API/schema được phê duyệt; có tests kiểm chứng ít nhất một happy path, denial path và lỗi phụ thuộc.
- Log/trace không tiết lộ dữ liệu nhạy cảm.
- Tech Lead nhận được handoff và kết quả CI thực tế.

## Owner-provided baseline

- Embedding baseline: `BAAI/bge-m3`; reranker baseline: `BAAI/bge-reranker-v2-m3`.
- Primary and fallback LLM providers remain pending selection and data-processing review.
- Retry primary at most twice for transient failures, then use an approved fallback that satisfies the same egress policy.
- A single LLM call has a 60-second timeout; no fallback may broaden tenant, ACL or classification scope.
