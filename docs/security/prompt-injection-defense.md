# Prompt injection defense-in-depth

## Sources
- Direct: user tries to override system instructions or impersonate admin.
- Indirect: PDF, spreadsheet, vector chunk, search result or tool output contains instructions addressed to the model.

## Defense chain
- Input: normalization, length and abuse checks; allow legitimate questions about attacks.
- Ingestion: scan suspicious content, quarantine uncertain files, preserve original provenance for review.
- Retrieval: only authorized sources; tool output treated untrusted.
- Context: separate system/developer instructions from quoted source data; no source content gains instruction priority.
- Tool: schema, allowlist, authorization, confirmation for side effects, budgets and egress restrictions.
- Output: source support checks, citation ACL, secret/PII scanning and safe refusal/abstention.

No detection model alone can guarantee injection prevention. Verify that bypassing the input detector still cannot grant unauthorized source access or tool execution.

## Owner-provided execution boundary

- The only MVP agent tools are `search_documents`, `read_authorized_chunk` and `get_document_metadata`.
- No upload, edit, delete, permission-change, SQL, shell, HTTP-fetch or autonomous-email tool is available to the agent.
- Tool limits are two retrieval rounds, four subqueries and eight tool calls. Backend authorization remains authoritative for every call.
