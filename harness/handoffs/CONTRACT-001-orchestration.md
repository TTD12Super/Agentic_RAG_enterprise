# CONTRACT-001 Orchestration Compatibility Review

- Task: `CONTRACT-001`
- Review role: Orchestration Compatibility Reviewer (`orchestration`)
- Contract reviewed: `docs/contracts/v1-baseline.md`, v1.0
- Review date: 2026-11-10
- Decision: `FINAL RECHECK: IMPLEMENTATION_DEFERRED`
- Approval: not granted; this is an independent compatibility review for the Main Agent
- Scope: tool manifest, scope binding, loop caps, deadlines, retries, maintenance pause/resume, idempotency, prompt-injection boundary and privacy

## Sources inspected

- `backend/app/orchestration/AGENTS.md`
- `docs/architecture/blocks/05-agent-orchestration.md`
- `docs/contracts/v1-baseline.md`
- `docs/contracts/agent-tools.md`
- `docs/contracts/chat-and-jobs.md`
- `docs/rag/retrieval-design.md`
- `docs/prompts/README.md`
- `docs/prompts/system-v1.md`
- `docs/prompts/planner-v1.md`
- `docs/prompts/answer-v1.md`
- `docs/security/prompt-injection-defense.md`
- `docs/database/database.md`

## Summary

The baseline is directionally compatible with the orchestration role: it keeps authorization outside LangGraph, restricts the runtime to three read-only tools, requires typed planner/tool outputs, treats retrieved content as untrusted, and defines bounded rounds/subqueries/tool calls plus token budgets. The validator also passes.

The contract is not yet fully machine-implementable for orchestration. The main gaps are an explicit workflow deadline, a single total interpretation of replanning caps, machine-readable tool/scope binding, orchestration retry/idempotency semantics, checkpoint privacy, and a precise maintenance boundary. These are compatibility findings, not silent contract changes.

## Findings

### ORCH-001 — Workflow deadline and deadline propagation are missing

- Severity: `HIGH`
- Type: missing invariant
- Evidence: `backend/app/orchestration/AGENTS.md:3` requires max rounds/time/tokens; `docs/architecture/blocks/05-agent-orchestration.md:20` requires round/time/token limits; `docs/contracts/agent-tools.md:20-21` requires a deadline; `docs/rag/retrieval-design.md:13-15` says timeout/token limits are to be decided by environment and measurement. The baseline defines message/scope expiry at `docs/contracts/v1-baseline.md:30-37`, but no end-to-end orchestration deadline, remaining-time calculation, or tool-call deadline field.
- Compatibility: `MISMATCH` with the orchestration instructions and tool contract. `expires_at` is not equivalent to a workflow deadline: it does not define the deadline budget, propagation, or behavior when remaining time is exhausted.
- Risk: a LangGraph run can exceed the intended request/job deadline while each individual message remains formally unexpired; this can cause queue starvation, late results and inconsistent pause/retry behavior.
- Recommendation: define one server-owned workflow deadline/deadline budget in the job or orchestration context; propagate remaining time to every planner, model and Tool Gateway call; fail with a safe timeout outcome without starting another branch when the budget is exhausted. Do not infer the value from prompt text or the LLM.

### ORCH-002 — Tool manifest is named but not machine-checkable

- Severity: `HIGH`
- Type: missing invariant / identifier mismatch
- Evidence: the baseline says the manifest is exactly three tools and calls receive `AuthorizedScope` (`docs/contracts/v1-baseline.md:133-135`); `docs/contracts/agent-tools.md:5-6` requires typed schemas, budgets, timeout and audit ID. However, `docs/contracts/agent-tools.md:8-12` uses `request_context_ref` and `trace_id`, while the baseline uses `scope_ref`/`traceparent` (`v1-baseline.md:17-25`, `58-77`) and `docs/contracts/retrieval.md:7-9` uses `authorized_scope_ref` and `trace_id`. No tool manifest version, exact request/response schemas, argument bounds, output classification or required binding fields are defined.
- Compatibility: `MISMATCH` between the normative baseline and the tool/retrieval examples; the allowlist itself is compatible.
- Risk: different agents may implement different scope identifiers and correlation fields, or accept an LLM-provided context reference. That can break gateway enforcement and make replay/privacy controls non-testable.
- Recommendation: publish one versioned, machine-readable manifest for the three tools. Specify exact request fields, server-injected principal/scope fields, `job_id`/`attempt_id`, deadline, policy epoch, correlation fields, argument limits, output classification and non-disclosing error mapping. Explicitly reject client/LLM-supplied scope or principal fields.

### ORCH-003 — Replanning caps do not state whether limits are global or per round

- Severity: `HIGH`
- Type: missing invariant
- Evidence: `docs/architecture/blocks/05-agent-orchestration.md:35-37` and `docs/rag/retrieval-design.md:24-25` set two rounds, four subqueries and eight tool calls. `docs/prompts/planner-v1.md:3` says “at most four subqueries initially,” which can be read as per planning round. No global counter semantics or transition table is stated.
- Compatibility: `MISMATCH` in wording; the intended bounded design is clear but the enforceable total is not.
- Risk: an implementation could issue four subqueries in each of two rounds, or eight calls per round, while claiming compliance. This defeats the intended cost and prompt-injection blast-radius limits.
- Recommendation: define counters as job-wide totals for the complete orchestration run: `retrieval_rounds <= 2`, `subqueries <= 4`, `tool_calls <= 8`; increment atomically before admission and reject/abstain when the next action would exceed a cap. State whether classifier/model calls are included in the token/deadline budget.

### ORCH-004 — Retry semantics for orchestration and Tool Gateway calls are incomplete

- Severity: `MEDIUM`
- Type: missing invariant
- Evidence: `docs/contracts/v1-baseline.md:119-125` defines queue delivery, worker lease, bounded ingestion/provider retry and duplicate completion. It does not define retries for tool `TIMEOUT`/`UNAVAILABLE`, planner/model failures, or a replan after a failed tool call. `docs/contracts/agent-tools.md:17-18` lists error outcomes but no retryability matrix.
- Compatibility: `MISSING`; no direct conflict with the bounded workflow.
- Risk: agents may retry non-retryable authorization/schema failures, consume all loop caps on transient errors, or duplicate provider work without a deterministic attempt policy.
- Recommendation: add a small retry matrix: retry only explicitly retryable transport/provider failures; never retry `DENIED`, invalid arguments, expired scope, unsupported schema or prompt-injection refusal; charge every attempt against deadline and global tool caps; preserve `attempt_id` and idempotency semantics across redelivery.

### ORCH-005 — Tool-call idempotency and replay binding are not explicit

- Severity: `MEDIUM`
- Type: missing invariant
- Evidence: the baseline covers mutating POSTs and worker completion/checkpoint writes (`docs/contracts/v1-baseline.md:85-91`), while the runtime tools are read-only (`v1-baseline.md:133-135`). The tool example has no `message_id`, `attempt_id`, `idempotency_key` or `expires_at` (`docs/contracts/agent-tools.md:8-12`), and no rule binds a repeated tool result to one job/attempt/scope.
- Compatibility: `MISSING`; read-only tools reduce impact but do not remove replay/cross-job correlation requirements.
- Risk: a late or duplicated result can be attached to the wrong LangGraph state, especially after retry or resume, or can consume budget twice.
- Recommendation: bind each Tool Gateway request/result to `job_id`, `attempt_id`, `scope_ref`, `policy_epoch`, a unique call ID and expiry. Define duplicate-result handling as safe replay of the same typed result or rejection; never accept a result from another job/attempt/tenant.

### ORCH-006 — Maintenance pause/resume boundary is underspecified for an active graph

- Severity: `HIGH`
- Type: missing invariant
- Evidence: `docs/contracts/v1-baseline.md:115-125` separates maintenance from `job_state`, blocks new chat admission and checkpoints existing jobs at safe boundaries. `docs/contracts/chat-and-jobs.md:18-22` repeats this. Neither specifies what happens when maintenance starts during planning, between tool calls, during model generation, or after a tool result but before state persistence; checkpoint schema/ownership and the safe-boundary definition are absent.
- Compatibility: `MISSING`; the high-level pause model is compatible with `AGENTS.md`, but not sufficient to implement deterministically.
- Risk: a graph may issue a tool call after maintenance begins, lose unpersisted evidence/state, or resume with a stale plan/scope. An in-flight provider call is explicitly not assumed to pause, so the post-call handling must be defined.
- Recommendation: define admission checks before every external call and state write; define safe boundaries as persisted graph state with no uncommitted tool result; on maintenance activation, stop scheduling new calls, persist only metadata-safe checkpoint state, and mark the job according to the shared state machine. On resume, reauthorize before replaying any tool call and discard stale results.

### ORCH-007 — Checkpoint privacy and state-retention rules are incomplete

- Severity: `HIGH`
- Type: missing invariant
- Evidence: `backend/app/orchestration/AGENTS.md:3` requires user-scoped state; the baseline excludes bodies/prompts/answers/source text from traces/logs/events (`docs/contracts/v1-baseline.md:90-91`, `133-137`). But the baseline does not say whether LangGraph checkpoints may contain user questions, prompts, retrieved chunks, tool outputs, answer drafts or citation text, nor how checkpoint access is authorized/retained/deleted.
- Compatibility: `MISSING`; privacy intent is compatible, but operational state can still become an alternate conversation store.
- Risk: System Admin or an operational dashboard could expose another user's conversation through checkpoint inspection, or a restored checkpoint could replay sensitive evidence after revocation.
- Recommendation: specify checkpoint field classes and access: keep raw source text, raw prompts and answer bodies out of operational checkpoints unless they are the authorized conversation/result store; use opaque references and redacted metadata where possible. Apply conversation ownership/privacy policy, retention/deletion, encryption and fresh authorization on read/resume/recovery.

### ORCH-008 — Prompt-injection boundary is conceptually compatible but lacks a schema-level invariant

- Severity: `MEDIUM`
- Type: missing invariant
- Evidence: prompts treat document/tool output as untrusted (`docs/prompts/system-v1.md:3-5`, `docs/prompts/answer-v1.md:3`, `docs/security/prompt-injection-defense.md:7-15`); planner/tool output must validate dedicated JSON Schemas (`docs/prompts/README.md:9`). The baseline only states the tool allowlist and server-resolved authorization (`docs/contracts/v1-baseline.md:133-137`), without defining message roles/fields that separate instructions from quoted evidence or the rejection behavior for malformed planner/router output.
- Compatibility: `COMPATIBLE` in principle, `MISSING` for implementation evidence.
- Risk: an implementation can concatenate retrieved text into a high-priority prompt or trust free-form planner output even while claiming to follow the prompt documents.
- Recommendation: define the orchestration input model with separate trusted instruction fields and untrusted evidence/tool-result fields; require schema validation before routing/tool execution/answering; reject malformed or instruction-bearing control output and return a safe abstention/error. The backend, not the prompt, remains the authorization boundary.

### ORCH-009 — Privacy-safe output handling is not bound to the orchestration result

- Severity: `MEDIUM`
- Type: missing invariant
- Evidence: `docs/security/prompt-injection-defense.md:13` requires secret/PII scanning and safe refusal/abstention. The baseline privacy event rules prohibit raw content (`docs/contracts/v1-baseline.md:137`), and the answer prompt requires structured results (`docs/prompts/answer-v1.md:7-9`), but v1.0 does not require an output scan/redaction decision before persisting or delivering an answer/citation result.
- Compatibility: `MISSING`; no direct contradiction.
- Risk: a model can repeat a secret or unauthorized source fragment in the answer even when retrieval authorization was correct, and the result may then enter the durable conversation store.
- Recommendation: define the final orchestration gate: validate answer schema, verify citations/claim grounding, run configured secret/PII/policy checks, then persist/deliver; on failure return a safe bounded refusal or redacted result. Do not log the rejected raw output.

## Positive compatibility evidence

1. `backend/app/orchestration/AGENTS.md:3` explicitly keeps LangGraph out of authorization and requires typed inputs, user-scoped state, bounded rounds/time/tokens and abstention/error paths.
2. `docs/architecture/blocks/05-agent-orchestration.md:12-17` matches the single-agent bounded LangGraph architecture and does not imply development subagents are runtime product agents.
3. `docs/contracts/v1-baseline.md:45-60, 77, 133-135` makes principal and scope server-resolved and keeps the exact three-tool read-only allowlist.
4. `docs/prompts/system-v1.md:3-12`, `docs/prompts/planner-v1.md:1-10` and `docs/security/prompt-injection-defense.md:7-21` consistently treat retrieved/tool content as untrusted and keep authorization external to prompts.
5. `docs/contracts/v1-baseline.md:95-103` requires reauthorization at retrieval branches, parent expansion, citation and source delivery.
6. `docs/contracts/v1-baseline.md:119-125` provides useful durable job/lease/checkpoint/retry guardrails, subject to the orchestration-specific gaps above.

## Validation and runtime scope

Command executed:

```text
python3 scripts/validate_harness.py
```

Exit status: `0`

Output:

```text
HARNESS VALID: 17 blocks, 8 agents, 31 tasks; no dependency cycles
```

The validator checks harness scaffolding only. No application runtime, provider/API key, cloud resource, or production data was accessed. No code, contract, prompt or task file was modified by this review.

## Re-check after v1.0 hardening

Re-review date: 2026-11-10. The current contract and focused contracts were inspected again. The results below are pass/fail against the original `ORCH-001` through `ORCH-009` findings; this handoff remains independent and does not approve the contract.

| Finding | Result | Current evidence | Remaining issue / reason |
|---|---|---|---|
| `ORCH-001` Workflow deadline and propagation | **FAIL** | `docs/contracts/agent-tools.md:20-21` now requires a server deadline per tool call; `docs/contracts/v1-baseline.md:141` requires every call to have one. | No job-wide orchestration deadline, remaining-time calculation, or deadline behavior for planner/model/replanning is defined. `docs/rag/retrieval-design.md:13-15` still says timeout limits are decided by environment/measurement. A per-call `deadline_at` does not prove an end-to-end workflow deadline. |
| `ORCH-002` Machine-checkable tool manifest/scope | **FAIL** | `docs/contracts/agent-tools.md:10-12` now uses `authorized_scope_ref`, `tool_call_id`, `traceparent` and `deadline_at`; `docs/contracts/v1-baseline.md:141` fixes the three-tool allowlist and server-resolved scope. | The contract still has no versioned machine-readable manifest, exact per-tool request/response schemas, argument bounds or output classification. The example is more consistent, but remains an example rather than a schema enforceable by the gateway. |
| `ORCH-003` Global replanning caps | **PASS** | `docs/contracts/agent-tools.md:20-21` says the limits are job-wide and total; `docs/contracts/v1-baseline.md:141` repeats two rounds, four subqueries and eight calls total; `docs/prompts/planner-v1.md:9` retains the same limits. | Original ambiguity is resolved. Implementation must still expose counters in tests, but no contract blocker remains for this finding. |
| `ORCH-004` Retry semantics | **FAIL** | `docs/contracts/v1-baseline.md:123-125` still defines queue/lease/provider retry bounds; `docs/contracts/agent-tools.md:17-18` still lists outcomes. | There is still no retryability matrix for tool `TIMEOUT`/`UNAVAILABLE`, planner/model failures, or replan-after-tool-failure, and no explicit rule that failed attempts consume the job-wide tool/deadline budget. |
| `ORCH-005` Tool-call idempotency/replay binding | **FAIL** | `docs/contracts/v1-baseline.md:92-93` now requires durable idempotency, `tool_call_id` and canonical argument fingerprint; `v1-baseline.md:141` requires a unique idempotent call ID and result state. | The focused tool request still does not explicitly bind the call/result to `job_id` and `attempt_id`, nor define late-result handling across graph resume/retry. The idempotency improvement is material but does not fully close the original replay-to-wrong-graph-state concern. |
| `ORCH-006` Maintenance pause/resume boundary | **FAIL** | `docs/contracts/v1-baseline.md:126-129` clarifies `MAINTENANCE_ACTIVE`, `PAUSED`, checkpointing and fresh authorization; `docs/contracts/chat-and-jobs.md:20-22` repeats the separate system-mode/UI semantics. | It still does not define safe boundaries for planning, between tool calls, model generation, or an unpersisted tool result; nor the required post-call behavior when maintenance starts. Checkpoint ownership/schema and “stop scheduling” semantics remain unspecified. |
| `ORCH-007` Checkpoint privacy/retention | **FAIL** | `docs/contracts/v1-baseline.md:143` now separates conversation-body storage/query paths and prevents privileged views from selecting another user's body; `v1-baseline.md:95` keeps payloads out of traces/events by default. | The contract still does not classify LangGraph checkpoint fields or say whether raw question, prompt, evidence, tool output, draft answer or citation text may be persisted there. Checkpoint-specific retention, deletion, encryption and read authorization remain absent. |
| `ORCH-008` Prompt-injection schema boundary | **FAIL** | `docs/prompts/README.md:9-10` requires dedicated JSON Schemas; `docs/security/prompt-injection-defense.md:10-15` and `docs/prompts/system-v1.md:3-12` preserve untrusted evidence and external authorization. | No current contract section defines the trusted/untrusted orchestration message fields or the fail-safe behavior for malformed planner/router output. Prompt guidance plus a general schema requirement is not yet a machine-checkable control boundary. |
| `ORCH-009` Output privacy/safety gate | **FAIL** | `docs/security/prompt-injection-defense.md:13` requires secret/PII scanning; `docs/prompts/answer-v1.md:7-9` requires structured results; `docs/contracts/v1-baseline.md:143` forbids raw content in audit/metadata paths. | v1.0 still does not require a final answer schema/grounding/secret-PII scan decision before durable answer persistence or delivery, nor define the safe result when that scan fails. |

### Re-check conclusion

- Passed: `ORCH-003`.
- Failed: `ORCH-001`, `ORCH-002`, `ORCH-004`, `ORCH-005`, `ORCH-006`, `ORCH-007`, `ORCH-008`, `ORCH-009`.
- Remaining implementation blockers from the orchestration role: workflow deadline semantics, machine-checkable tool schemas, retry policy, graph-bound tool replay, maintenance/checkpoint protocol, checkpoint privacy classification and final output safety gate.

## Recommendation to Main Agent

The recommendation above records the pre-final-recheck state. It is superseded by the final result below.

## FINAL RECHECK

Re-review date: 2026-11-10. This pass used only the current contract, focused contracts, orchestration guidance and database mapping. Runtime code is absent by design at this stage and is treated as downstream implementation evidence, not as a contract-text failure.

| Previous finding | Result | Current normative evidence and database mapping |
|---|---|---|
| `ORCH-001` Workflow deadline and propagation | **PASS — IMPLEMENTATION_DEFERRED** | `docs/contracts/v1-baseline.md:167` requires immutable `workflow_deadline_at` plus per-node deadlines and forbids extension; `docs/database/database.md:264-287, 538-547` maps the immutable job deadline to `QUERY_JOBS.workflow_deadline_at`. Timeout behavior is also normative. The remaining work is runtime enforcement and tests. |
| `ORCH-002` Machine-checkable tool manifest/scope | **PASS — IMPLEMENTATION_DEFERRED** | `docs/contracts/v1-baseline.md:163, 171-179` defines the exact three-tool manifest, manifest version, schema IDs, action, byte limits and timeout values; `v1-baseline.md:61-78, 183` keeps scope/principal server-resolved and separates trusted from untrusted fields. Runtime schema files/gateway validation remain downstream work. |
| `ORCH-003` Global replanning caps | **PASS — IMPLEMENTATION_DEFERRED** | `docs/contracts/v1-baseline.md:163`, `docs/contracts/agent-tools.md:20-21` explicitly define job-wide totals: two retrieval rounds, four subqueries and eight tool calls. This remains a runtime counter/test obligation only. |
| `ORCH-004` Retry semantics | **PASS — IMPLEMENTATION_DEFERRED** | `docs/contracts/v1-baseline.md:143, 181` defines bounded provider/worker retry and exactly one retry for tool `TIMEOUT`/`UNAVAILABLE`; the second failure returns safe insufficient evidence and cannot trigger unbounded replanning. `docs/database/database.md:289-303, 549-554` maps execution steps, attempt numbers and safe retry metadata. |
| `ORCH-005` Tool-call idempotency/replay binding | **PASS — IMPLEMENTATION_DEFERRED** | `docs/contracts/v1-baseline.md:97, 163, 181` requires durable fingerprinted `tool_call_id`, same-ID retry, `job_id`/`attempt_id` binding and stale-result rejection. `docs/database/database.md:264-303, 376-386, 538-554` maps query jobs, execution steps and durable idempotency records. Runtime implementation must choose the corresponding `operation/resource_key` representation without weakening the invariant. |
| `ORCH-006` Maintenance pause/resume boundary | **PASS — IMPLEMENTATION_DEFERRED** | `docs/contracts/v1-baseline.md:144-147` defines separate maintenance mode, pause/resume authorization and safe checkpointing; `docs/database/database.md:760-787` defines `RUNNING → PAUSED` only after a safe checkpoint, pause request as a control flag, lease/revision checks and stale-checkpoint rejection. Runtime scheduling and provider-call handling remain downstream work. |
| `ORCH-007` Checkpoint privacy/retention | **PASS — IMPLEMENTATION_DEFERRED** | `docs/contracts/v1-baseline.md:145, 169` makes checkpoints metadata-only, excludes raw question/prompt/evidence/tool output/answer/source/secrets, requires encryption, owner/authorized-worker access and seven-day purge. `docs/database/database.md:276-287, 538-547` maps versioned `QUERY_JOBS.checkpoint`, schema version, revision and safe metadata; runtime enforcement and retention jobs remain downstream work. |
| `ORCH-008` Prompt-injection schema boundary | **PASS — IMPLEMENTATION_DEFERRED** | `docs/contracts/v1-baseline.md:183` explicitly separates trusted orchestration fields from untrusted query/evidence/tool output and rejects malformed planner/router output without selecting a tool. This aligns with `docs/prompts/README.md:9-10` and `docs/security/prompt-injection-defense.md:10-15`. Schema validation and context assembly are downstream implementation work. |
| `ORCH-009` Output privacy/safety gate | **PASS — IMPLEMENTATION_DEFERRED** | `docs/contracts/v1-baseline.md:167, 183` requires output safety checks before persistence, including schema, grounding, authorization, secret/PII leakage and unsupported claims; failure is `SAFE_OUTPUT_BLOCKED` with no raw delivery/persistence. `docs/database/database.md:531-547, 853-857` maps final answer/citation persistence to one idempotent transaction. Runtime scanner/gate tests remain downstream work. |

### Final conclusion

- Contract-level result: **PASS** for all previous orchestration findings; no true contradiction or serious residual orchestration security gap was found in the current normative documents.
- Overall handoff status: **FINAL RECHECK: IMPLEMENTATION_DEFERRED** because application code, schema artifacts and runtime enforcement are not yet implemented. This is not a contract failure.
- Main implementation obligations: enforce the specified deadlines, counters, retry rules, trusted/untrusted field separation, stale-result fencing, checkpoint restrictions and final output safety gate; then run the required tests.
- This handoff does not approve `CONTRACT-001` or change any task state.
