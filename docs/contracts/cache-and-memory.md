# Memory & cache isolation contract (proposal)

## Memory
- Owned by `tenant_id`, `user_id`, `conversation_id` and context policy.
- Conversation read requires `conversation:read`; a Chairman cannot read an employee's conversation solely by role.
- Summaries referencing protected sources must preserve source references and be reauthorized on reuse.

## Cache
- Prompt caching: provider-level model-prefix optimization; do not assume it caches answers or enforces ACL.
- Embedding cache: keyed by normalized text + model/version; no raw personal data stored unless approved.
- Retrieval/response cache: scoped by tenant, principal/entitlements, policy_version, corpus/index_version, query, model configuration.
- Invalidate on document active-version changes, ACL/role revocation, classification changes and deletion.
- Avoid response caching for restricted material until isolation/revocation tests pass.

## Owner-provided lifecycle baseline

- Authenticated conversations are retained for 180 days from last activity; anonymous sessions expire after 30 minutes idle and at most 24 hours; anonymous conversations are retained for 7 days.
- Soft delete invalidates retrieval/answer caches immediately. Restore and resume paths must replay tombstones/revocations before serving data.
- Redis may hold cache, rate-limit and short-lived state but never the only durable checkpoint.
