# Threat model (initial)

## Assets
Source files, indexed chunks, PII, policies/ACLs, API tokens, audit records, LLM prompts and outputs, conversation memory.

## Trust boundaries
1. User/browser ↔ API; identity/role claims remain untrusted until verified.
2. Uploaded file ↔ parser/ingestion worker; isolate potentially malicious formats.
3. Qdrant/index ↔ policy store; index metadata can be stale.
4. Retrieved chunk/tool output ↔ LLM; content is data, not instructions.
5. LLM tool suggestion ↔ Tool Gateway; backend owns actions.
6. LLM provider ↔ sensitive internal data; egress governed by policy.
7. Response/citation/cache ↔ user; recheck current access.

## Threat scenarios and owner
| Threat | Control | Owner |
|---|---|---|
| Cross-tenant retrieval | tenant filter + PDP + negative tests | Security/RAG |
| Indirect prompt injection | context isolation + tool allowlist | Security/Orchestration |
| Unauthorized file upload | server-side document:create policy | Backend/Security |
| Stale ACL after revoke | source recheck + cache invalidation | Security/Cache |
| Malicious PDF parser exploit | quarantine, size limits, sandboxed processing | Ingestion/DevOps |
| Unsupported citation | source span + verifier | Evidence/QA |
| Excessive tool calls | deadline, budget, max rounds | Orchestration |
| Log disclosure | field redaction, restricted logs | DevOps/Security |

Update threat model when adding new connector, tool, model provider or modality.

## Owner-provided threat-model additions

- Tenant replacement/offboarding is an asset-lifecycle boundary: old users, indexes, caches, conversations and files must not become visible to a new tenant.
- A 200 MB upload is also a resource-exhaustion threat; enforce streaming, byte limits, page/row/word limits, parser isolation and watchdog cleanup.
- PostgreSQL queue/checkpoint state is trusted only while tenant, policy version, source version and lease are current; stale checkpoints must fail closed.
- Immutable backup restore is a revocation threat; replay tombstones before making any restored service available.
- Provider fallback and model routing must enforce the same classification/egress rules as the primary provider.
