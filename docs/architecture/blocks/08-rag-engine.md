# 08 — RAG Engine

## Trách nhiệm
dense + BM25 + RRF + rerank + parent-child context.

## Đầu vào
Authorized query + scope + index version.

## Đầu ra / contract
Chunk evidence with provenance metadata.

## ARCH-OVERVIEW alignment

- Python workers perform permission-aware dense and lexical retrieval, RRF, optional reranking and bounded parent expansion.
- Tenant, ACTIVE-version and ACL filters run in every retrieval branch before results return.
- The authoritative policy store is separate from Qdrant/search projections.
- Recheck permission before returning chunks and again before parent or original-source access.

## Ranh giới bảo mật
ACL filter at query in every retrieval branch and recheck parent.

## Kiểm thử bàn giao
Recall@k, nDCG, no unauthorized IDs at any retrieval step.

## Tích hợp
Các module ứng dụng phải tuân thủ contract tương ứng trong `docs/contracts/`; thay đổi giao diện chung phải theo `docs/contracts/CHANGE-PROCESS.md`. Khối này không được tự ý vượt quyền hoặc quyết định trạng thái tài liệu ngoài quyền sở hữu.

## Definition of Done
- API/schema được phê duyệt; có tests kiểm chứng ít nhất một happy path, denial path và lỗi phụ thuộc.
- Log/trace không tiết lộ dữ liệu nhạy cảm.
- Tech Lead nhận được handoff và kết quả CI thực tế.

## Owner-provided baseline

- Qdrant supplies dense and sparse/BM25 retrieval with RRF fusion; OpenSearch/Elasticsearch are deferred.
- Reranking is enabled by default. Parent expansion is conditional on evidence need and token budget.
- Child chunks target 500–800 tokens with 10–15% overlap; parent sections target 2,000 tokens.
- Two retrieval rounds, four subqueries and eight tool calls are the initial caps.
