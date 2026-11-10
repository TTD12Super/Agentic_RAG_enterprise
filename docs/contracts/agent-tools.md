# Agent Tool Gateway contract (proposal)

## Principle
The LLM proposes tool name/arguments; **backend validates and executes**. All tools have typed schema, explicit actions, rate budgets, timeout and audit ID.

## Read tool example
```json
{"tool":"search_documents","arguments":{"query":"refund policy"},"request_context_ref":"server-issued-context","trace_id":"trace-1"}
```
The Tool Gateway resolves current principal itself and checks `tool:execute`, then retrieval applies document-level ACL independently.

## MVP allowlist
`search_documents`, `read_authorized_chunk`, `get_document_metadata` (all read-only and scoped). Do not add `send_email`, `delete_document`, shell or HTTP fetch tool until approved and audited.

## Responses
`SUCCESS` with typed payload, `DENIED`, `UNAVAILABLE`, `INVALID_ARGUMENTS`, `TIMEOUT`, `NEEDS_APPROVAL`. Never expose secrets, raw SQL errors or private server paths.

## Loop caps
Define initial policy limits in `docs/rag/retrieval-design.md`: max tool calls, max retrieval rounds, deadline and token budget; measured adjustments only after tests.

## Owner-provided MVP allowlist

The MVP allowlist is exactly:

- `search_documents`
- `read_authorized_chunk`
- `get_document_metadata`

No upload, edit, delete, permission-change, SQL, shell, HTTP-fetch or autonomous email tool is registered. Source preview is a separately authorized backend API, not an agent tool. Initial limits are two retrieval rounds, four subqueries and eight tool calls.
