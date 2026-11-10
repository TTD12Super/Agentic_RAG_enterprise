# Handoff — CONTRACT-TEST-001 / QA Test Agent

- Task ID: `CONTRACT-TEST-001`
- Agent owner: QA/Test Agent
- Status: `READY_FOR_INTEGRATION`
- Contract version(s) used: `docs/contracts/v1-baseline.md` v1.0
- Upstream dependencies checked: `ARCH-001` is recorded `DONE`; the v1 baseline is the normative static/schema source for this package.
- Changed files:
  - `tests/contracts/__init__.py`
  - `tests/contracts/_baseline.py`
  - `tests/contracts/test_behavior_component.py`
  - `tests/contracts/test_contract_integration.py`
  - `tests/contracts/test_security_adversarial.py`
  - `tests/contracts/test_e2e_operational.py`
  - `harness/handoffs/CONTRACT-TEST-001.md`
- Forbidden paths changed: none. No backend, frontend, infra, contract, or task-registry files were changed.
- New/updated tests: 40 deterministic static/schema tests; 10 in each required family.

## Scope and test model

This package validates the accepted v1 baseline as repository text and JSON examples using only Python standard library `unittest`. It does not create a mock API, policy service, database, queue, vector store, model provider, cloud resource or browser flow. Therefore a passing test proves that the normative baseline contains the checked invariant; it does not prove runtime behavior or production authorization.

The helper reads only `docs/contracts/v1-baseline.md`, parses its fenced JSON examples, extracts numbered sections and checks required normative statements. Fixtures are synthetic and no real company data, API key, cloud account or provider was used.

## Four-family coverage mapping

### Behavior/component — 10 cases

| ID | Test | Static/schema invariant |
|---|---|---|
| B-01 | `test_behavior_baseline_is_approved_mvp_profile` | v1 is the approved MVP compatibility profile and names public API scope |
| B-02 | `test_behavior_common_envelope_has_required_identity_fields` | Common JSON envelope contains required identity, version and payload fields |
| B-03 | `test_behavior_timestamps_use_utc_rfc3339_z` | Example timestamps and rule require UTC RFC 3339 `Z` |
| B-04 | `test_behavior_schema_evolution_is_additive_within_major_version` | Major-version breaking rule and additive/unknown-field semantics are present |
| B-05 | `test_behavior_problem_details_shape_is_safe` | Error envelope fields and sensitive-data exclusions are defined |
| B-06 | `test_behavior_authorization_order_is_explicit` | Six authorization stages appear in normative order |
| B-07 | `test_behavior_anonymous_and_role_boundaries_are_present` | Anonymous, Chairman and Website Manager boundaries are explicit |
| B-08 | `test_behavior_citation_locator_is_discriminated_by_file_type` | PDF, DOCX and XLSX citation locator kinds are all present |
| B-09 | `test_behavior_job_states_and_maintenance_are_separate` | Job state enum is distinct from `MAINTENANCE_ACTIVE` system mode |
| B-10 | `test_behavior_mvp_tool_allowlist_and_budgets_are_bounded` | Exact read-only tool allowlist and per-job limits are present |

### Contract/integration — 10 cases

| ID | Test | Static/schema invariant |
|---|---|---|
| C-01 | `test_contract_api_root_is_versioned_rest_json` | Public API uses REST/HTTP JSON under `/api/v1` |
| C-02 | `test_contract_worker_payload_identifies_schema_and_attempt` | Worker envelope includes schema/message/request/attempt/payload identity |
| C-03 | `test_contract_traceparent_and_request_id_have_distinct_roles` | W3C `traceparent` and application `request_id` semantics differ |
| C-04 | `test_contract_mutation_idempotency_scope_is_defined` | Mutation keys, fingerprints, replay TTL and tuple scope are defined |
| C-05 | `test_contract_read_and_delete_have_resource_semantics` | GET/DELETE are not incorrectly required to use mutation idempotency |
| C-06 | `test_contract_authorized_scope_schema_is_server_bound` | Scope schema has audience, tenant, epoch, expiry and revocation fields |
| C-07 | `test_contract_citation_reference_contains_reauthorization_claims` | Citation carries immutable version, evidence, epoch and separate download authorization |
| C-08 | `test_contract_cache_key_carries_all_authorization_epochs` | Cache dimensions include tenant, entitlement and corpus/index/policy freshness |
| C-09 | `test_contract_publication_requires_index_ack_before_pointer_flip` | Two-step publication order and former ACTIVE retention are explicit |
| C-10 | `test_contract_versioned_mutation_endpoints_are_explicit` | Access, approve/publish and feedback endpoints bind their resource identifiers |

### Security/adversarial — 10 cases

| ID | Test | Static/schema invariant |
|---|---|---|
| S-01 | `test_security_untrusted_clients_cannot_supply_principal_attributes` | Browser, LLM and retrieved text cannot supply principal attributes |
| S-02 | `test_security_explicit_deny_overrides_chairman_allow` | Explicit deny overrides broad Chairman read allow |
| S-03 | `test_security_scope_mismatch_denies_without_existence_leak` | Missing/expired/revoked/mismatched scope denies without existence leak |
| S-04 | `test_security_worker_jwt_replay_and_cross_tenant_checks_fail_closed` | Worker replay, binding and cross-tenant rejection are normative |
| S-05 | `test_security_scope_is_rechecked_at_each_content_boundary` | Admission, retrieval, parent, citation and download rechecks are listed |
| S-06 | `test_security_parent_denial_cannot_change_child_authorization` | Denied parent is omitted without broadening child authorization |
| S-07 | `test_security_stale_cache_is_fail_closed` | Stale/missing invalidation cannot serve restricted cached content |
| S-08 | `test_security_privacy_events_exclude_conversation_and_source_content` | Events exclude bodies, prompts, answers, source, secrets, tokens and unrestricted PII |
| S-09 | `test_security_agent_tool_surface_excludes_side_effect_tools` | Upload/edit/delete/permission/SQL/shell/HTTP/email tools are absent |
| S-10 | `test_security_output_and_provider_fallback_cannot_bypass_policy` | Output safety and approved-only fallback constraints are present |

### E2E/operational — 10 cases

| ID | Test | Static/schema invariant |
|---|---|---|
| E-01 | `test_e2e_anonymous_flow_has_public_only_boundary` | Anonymous flow is constrained to PUBLIC and current ACTIVE content |
| E-02 | `test_e2e_employee_flow_requires_department_acl_and_active_version` | Employee path requires department, ACL and current ACTIVE checks |
| E-03 | `test_e2e_upload_publication_retains_previous_active_version_until_verified` | Publication retains former ACTIVE until both steps verify |
| E-04 | `test_e2e_failed_publication_emits_repair_without_replacing_active` | Mismatch/timeout/stale writer preserves ACTIVE and emits repair |
| E-05 | `test_e2e_invalid_ingestion_is_terminal_without_retry` | Invalid input and review decisions are terminal/non-auto-retried |
| E-06 | `test_e2e_transient_ingestion_retry_is_bounded_and_checksum_bound` | Transient retries are bounded and tied to unchanged checksum/version |
| E-07 | `test_e2e_lease_expiry_allows_at_most_one_retryable_attempt` | Lease expiry uses CAS and fencing to prevent duplicate retry completion |
| E-08 | `test_e2e_maintenance_pause_resume_rechecks_fresh_security_context` | Maintenance admission and resume checkpoint/security rechecks are defined |
| E-09 | `test_e2e_restore_replays_tombstones_before_any_read` | Revocation tombstones replay before any restored read |
| E-10 | `test_e2e_deadline_timeout_and_model_fallback_remain_safe` | Workflow deadline, safe timeout result and approved bounded fallback are defined |

## Commands actually executed

### Required task command

```text
$ python -m unittest discover -s tests/contracts -p 'test_*.py'
zsh:1: command not found: python
exit 127
```

Result: `BLOCKED` by the local environment; no `python` executable/alias exists. This is not a test failure.

### Equivalent reproducible command available in this environment

```text
$ python3 -m unittest discover -s tests/contracts -p 'test_*.py'
........................................
----------------------------------------------------------------------
Ran 40 tests in 0.005s

OK
exit 0
```

Result: `PASS` — all 40 static/schema tests executed successfully.

### Harness validator

```text
$ python3 scripts/validate_harness.py
HARNESS INVALID
 - Dependency graph missing edge: ARCH-001 -> CONTRACT-TEST-001
 - Task CONTRACT-TEST-001 is missing from phase-0 checklist
exit 1
```

Result: `BLOCKED/FAIL` outside this task's write scope. The validator reports existing harness metadata inconsistencies; this agent did not edit `harness/tasks/tasks.json` or phase checklists because both are forbidden paths for `CONTRACT-TEST-001`. Main Agent must reconcile those files separately.

## Runtime status

The following are deliberately `NOT RUN`/`BLOCKED`, not mocked or claimed as proven:

| Surface | Status | Reason |
|---|---|---|
| FastAPI/API contract execution | `NOT RUN` | No backend runtime implementation exists in this task scope |
| PostgreSQL/Qdrant/object storage integration | `NOT RUN` | No services or runtime fixtures are available |
| Worker JWT/replay/lease behavior | `NOT RUN` | No worker implementation or key material; static claims only |
| Ingestion/publication/revocation E2E | `NOT RUN` | No ingestion/index/queue implementation exists |
| Browser/UI E2E and provider fallback | `NOT RUN` | No frontend/runtime/provider execution is in scope |
| Exact `python` acceptance command | `BLOCKED` | Interpreter alias is unavailable; `python3` equivalent passes |

## Findings for Main Agent

1. The v1 baseline is internally checkable for the 40 selected invariants; all 40 tests pass under `python3`.
2. The exact task command cannot execute until the repository environment exposes `python` or the task runner documents `python3` as the accepted interpreter. This QA agent did not change environment/configuration.
3. `scripts/validate_harness.py` currently reports a missing `ARCH-001 -> CONTRACT-TEST-001` dependency edge and a missing `CONTRACT-TEST-001` entry in the Phase 0 checklist. Fixing those requires Main Agent changes outside this task's allowed paths.
4. This package does not approve the contract and does not prove runtime security, API compatibility, database behavior or production readiness. It only reports static/schema evidence against the accepted v1 baseline.

## Security implications

- No real data, secrets, API keys, cloud accounts or external providers were accessed.
- Tests assert fail-closed, tenant, ACL, privacy, replay, cache and tool-boundary statements exist in the normative baseline.
- Static assertions can detect baseline drift but cannot detect an implementation bypass. Runtime negative tests remain required before integration/release.

## Main Agent action requested

- Review this handoff and the 40-case mapping.
- Decide whether the missing `python` alias is resolved by environment setup or recorded as an acceptance-environment issue.
- Reconcile the validator findings in the task/dependency/checklist metadata outside this task's scope.
- Do not mark the shared contract `APPROVED` based solely on this handoff; this is QA evidence, not contract approval.

## Human approval required

None for this QA package. Any change to the shared contract, task registry, phase checklist, runtime test environment, deployment, provider or release gate remains subject to Main Agent/Project Owner authority under the repository rules.
