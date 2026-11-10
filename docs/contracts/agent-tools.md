# Agent Tool Gateway contract (v1.0)

The normative tool manifest, scope binding, replay and privacy rules are defined in [`v1-baseline.md`](v1-baseline.md).

## Principle
The LLM proposes tool name/arguments; **backend validates and executes**. All tools have typed schema, explicit actions, rate budgets, timeout and audit ID.

## Read tool example
```json
{"tool":"search_documents","arguments":{"query":"refund policy"},"authorized_scope_ref":"server-issued-scope","tool_call_id":"tool-call-uuid","traceparent":"00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01","deadline_at":"2026-11-10T10:00:10Z"}
```
The Tool Gateway resolves current principal itself and checks `tool:execute`, then retrieval applies document-level ACL independently.

## MVP allowlist
`search_documents`, `read_authorized_chunk`, `get_document_metadata` (all read-only and scoped). Do not add `send_email`, `delete_document`, shell or HTTP fetch tool until approved and audited.

## Responses
`SUCCESS` with typed payload, `DENIED`, `UNAVAILABLE`, `INVALID_ARGUMENTS`, `TIMEOUT`, `NEEDS_APPROVAL`. Never expose secrets, raw SQL errors or private server paths.

## Loop caps
The v1 job-wide limits are at most two retrieval rounds, four subqueries and eight tool calls total. Every call has a server deadline, bounded output and a unique idempotent `tool_call_id`; measured adjustments require a versioned contract change.

## Owner-provided MVP allowlist

The MVP allowlist is exactly:

- `search_documents`
- `read_authorized_chunk`
- `get_document_metadata`

No upload, edit, delete, permission-change, SQL, shell, HTTP-fetch or autonomous email tool is registered. Source preview is a separately authorized backend API, not an agent tool. Initial limits are two retrieval rounds, four subqueries and eight tool calls.
