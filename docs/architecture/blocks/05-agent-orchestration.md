# 05 — Agent Orchestration

## Trách nhiệm
LangGraph state + planner + router + bounded replanning.

## Đầu vào
Authenticated question + allowed tool registry.

## Đầu ra / contract
Tool requests, plan state, synthesized draft.

## ARCH-OVERVIEW alignment

- Python RAG workers run a bounded single-agent LangGraph workflow.
- Simple questions use the direct Hybrid RAG path; complex or insufficient-evidence cases may replan within limits.
- The Python/FastAPI Core creates/authenticates jobs and receives versioned results; the Tool Gateway validates every call.
- Development subagents do not imply a runtime multi-agent product architecture.

## Ranh giới bảo mật
Tool Gateway validates calls; limit rounds/time/tokens.

## Kiểm thử bàn giao
Branch selection, bounded loops, blocked tool, insufficient evidence.

## Tích hợp
Các module ứng dụng phải tuân thủ contract tương ứng trong `docs/contracts/`; thay đổi giao diện chung phải theo `docs/contracts/CHANGE-PROCESS.md`. Khối này không được tự ý vượt quyền hoặc quyết định trạng thái tài liệu ngoài quyền sở hữu.

## Definition of Done
- API/schema được phê duyệt; có tests kiểm chứng ít nhất một happy path, denial path và lỗi phụ thuộc.
- Log/trace không tiết lộ dữ liệu nhạy cảm.
- Tech Lead nhận được handoff và kết quả CI thực tế.

## Owner-provided baseline

- Route rule-first; use an LLM classifier only when simple/complex classification is ambiguous.
- Complex means multi-source synthesis/comparison, dependent subquestions or insufficient first-pass evidence.
- Maximum two retrieval rounds, four subqueries and eight tool calls. Simple budget is 16k/2k input/output tokens; complex is 32k/4k.
- The only runtime tools are `search_documents`, `read_authorized_chunk` and `get_document_metadata`.
