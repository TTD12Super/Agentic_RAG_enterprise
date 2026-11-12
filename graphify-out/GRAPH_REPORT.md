# Graph Report - enterprise-agentic-rag-harness  (2026-11-12)

## Corpus Check
- 299 files · ~263,030 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 68 file(s) not represented in the graph (top: (none) 53, .toml 9, .example 2)

## Summary
- 4215 nodes · 13249 edges · 183 communities (128 shown, 55 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 1027 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ad6235ee`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- audit.py
- compose
- read
- read
- read
- section
- read
- InMemoryDerivedIndex
- read
- otel-collector-config.yaml
- prometheus
- InMemoryScopedCache
- PostgresIdentityStore
- core/chat.py
- CacheScope
- postgres
- postgres
- PromptDefinition
- package.json
- answer_baseline/test_security_adversarial.py
- AuthorizationContractIntegrationTests
- orchestration/context.py
- compilerOptions
- InMemoryConversationMemory
- model/test_e2e_operational.py
- api/chat.py
- _make_retriever
- AuthorizationEvaluator
- chat_api/test_contract_integration.py
- InMemoryIdentityStore
- chat_api/test_behavior_component.py
- DocumentVersionMetadata
- GraphifyOperationalTests
- key
- chat_api/test_security_adversarial.py
- steps
- DataClassification
- ContractIntegrationTests
- SecurityAdversarialTests
- rules
- hashlib
- dense.py
- ToolResult
- App.tsx
- route
- gemini.py
- test_knowledge_database.py
- chat_api/test_e2e_operational.py
- expand_parent_context
- eval_001_runner.py
- datasources
- monitoring/prometheus.yml
- lifecycle.py
- client.ts
- PromptContractIntegrationTests
- AuthenticatedPrincipal
- request
- _resolve
- upload
- admin_api/test_behavior_component.py
- tests/test_chat_api.py
- request
- CitationArtifact
- vite-env.d.ts
- sync_graph.sh
- migrate.sh
- inspect_untrusted_content
- enterprise-agentic-rag-backend
- answer_baseline/test_behavior_component.py
- orchestration_langgraph/test_security_adversarial.py
- model/test_contract_integration.py
- _common.py
- test_authorization.py
- normalize_user_input
- backend_boot/_baseline.py
- rag/runtime.py
- evaluator
- inherit_acl
- env.py
- test_tool_gateway.py
- AnswerDraft
- main.py
- load_validated_records
- IngestionService
- EvidenceRecord
- evaluator
- FrontendE2EOperationalTests
- ToolResult
- new_service
- test_answer_baseline.py
- read
- reset
- ChatView
- AuthorizationDecision
- answer_baseline/test_contract_integration.py
- BoundedOrchestrator
- answer_baseline/test_e2e_operational.py
- read_frontend
- evidence/test_contract_integration.py
- Claim
- cache_memory/test_security_adversarial.py
- App.test.tsx
- cache_memory/test_contract_integration.py
- orchestration_langgraph/test_contract_integration.py
- SecureContextBuilder
- test_customer_api_e2e.py
- InfrastructureSecurityTests
- admin_api/test_contract_integration.py
- run_local_guardrail_pipeline
- KnowledgeBehaviorTests
- manifest.json
- main.py
- orchestration_langgraph/test_behavior_component.py
- test_chat_stream.py
- ConversationMessage
- ingestion/test_security_adversarial.py
- ChunkMetadata
- inherit_acl
- ndcg_at_k
- tree
- ChatService
- test_cache_memory.py
- DocumentsView
- FakeMemoryRepository
- tests/test_dashboard_api.py
- read
- build_secure_context
- BackendBootstrapContractTests
- _Model
- PromptBehaviorComponentTests
- observability/context.py
- app/evidence/__init__.py
- InMemoryScopedCache
- ingestion/test_behavior_component.py
- test_rag_002_metrics.py
- vercel.json
- db/runtime.py
- DocumentMetadata
- to_qdrant_payload
- UUID
- ApprovalsView
- App
- package.json
- DenseRetrievalContractIntegrationTests
- BackendBootstrapBehaviorTests
- BehaviorComponentTests
- test_access_request_review.py
- authorization/test_e2e_operational.py
- test_customer_frontend_static.py
- pytest
- json

## God Nodes (most connected - your core abstractions)
1. `auth()` - 151 edges
2. `request()` - 150 edges
3. `DataClassification` - 137 edges
4. `IngestionService` - 125 edges
5. `AuthenticatedPrincipal` - 103 edges
6. `CacheScope` - 90 edges
7. `new_service()` - 85 edges
8. `_active_document()` - 80 edges
9. `ChunkMetadata` - 79 edges
10. `Claim` - 75 edges

## Surprising Connections (you probably didn't know these)
- `pause_first_run()` --calls--> `_tenant_uuid()`  [EXTRACTED]
  tests/qa/chat_api/test_e2e_operational.py → backend/app/api/admin.py
- `test_acl_explicit_deny_overrides_employee_read_allow()` --uses--> `Action`  [INFERRED]
  tests/qa/admin_api/test_security_adversarial.py → backend/app/authorization/policy.py
- `test_revoked_document_fails_current_version_policy_check()` --uses--> `Action`  [INFERRED]
  tests/qa/admin_api/test_security_adversarial.py → backend/app/authorization/policy.py
- `test_source_download_is_rechecked_after_read_retrieval()` --uses--> `Action`  [INFERRED]
  tests/qa/evidence/test_e2e_operational.py → backend/app/authorization/policy.py
- `DenseRetrievalBehaviorTests` --uses--> `Action`  [INFERRED]
  tests/qa/rag/test_behavior_component.py → backend/app/authorization/policy.py

## Import Cycles
- 2-file cycle: `backend/app/api/admin.py -> backend/app/api/chat.py -> backend/app/api/admin.py`
- 2-file cycle: `backend/app/api/admin.py -> backend/app/api/identity.py -> backend/app/api/admin.py`
- 2-file cycle: `backend/app/api/chat.py -> backend/app/api/identity.py -> backend/app/api/chat.py`
- 3-file cycle: `backend/app/api/admin.py -> backend/app/api/chat.py -> backend/app/api/identity.py -> backend/app/api/admin.py`
- 3-file cycle: `backend/app/api/admin.py -> backend/app/api/identity.py -> backend/app/api/chat.py -> backend/app/api/admin.py`

## Communities (183 total, 55 thin omitted)

### Community 0 - "audit.py"
Cohesion: 0.11
Nodes (17): append_audit_event(), AuditEvent, AuditSink, AuditSinkUnavailable, InMemoryAuditSink, redact_metadata(), _safe_code(), _safe_identifier() (+9 more)

### Community 1 - "compose"
Cohesion: 0.07
Nodes (11): compose(), compose_config_result(), database(), handoff(), read(), tasks(), testing(), DisposablePostgresBehaviorTests (+3 more)

### Community 2 - "read"
Cohesion: 0.05
Nodes (10): compose_config_result(), migration_files(), migration_text(), read(), task(), tasks(), DatabaseBaselineBehaviorTests, DatabaseBaselineContractTests (+2 more)

### Community 3 - "read"
Cohesion: 0.08
Nodes (7): compose_config(), read(), task(), tasks(), InfrastructureBehaviorTests, InfrastructureContractTests, InfrastructureOperationalTests

### Community 4 - "read"
Cohesion: 0.05
Nodes (7): read(), task(), tasks(), AuditBehaviorTests, AuditContractTests, AuditOperationalTests, AuditSecurityTests

### Community 5 - "section"
Cohesion: 0.05
Nodes (11): dfs(), json_blocks(), require_all(), section(), BehaviorComponentTests, ContractIntegrationTests, E2EOperationalTests, SecurityAdversarialTests (+3 more)

### Community 6 - "read"
Cohesion: 0.06
Nodes (7): dashboard(), read(), task(), MonitoringBehaviorTests, MonitoringContractTests, MonitoringOperationalTests, MonitoringSecurityTests

### Community 7 - "InMemoryDerivedIndex"
Cohesion: 0.14
Nodes (4): _chunk_state(), DerivedIndex, DerivedIndexFailure, InMemoryDerivedIndex

### Community 8 - "read"
Cohesion: 0.09
Nodes (4): read(), GraphifyBehaviorTests, GraphifyContractTests, GraphifySecurityTests

### Community 9 - "otel-collector-config.yaml"
Cohesion: 0.06
Nodes (32): action, key, actions, send_batch_size, timeout, exporters, prometheus, endpoint (+24 more)

### Community 10 - "prometheus"
Cohesion: 0.06
Nodes (30): command, image, ports, read_only, security_opt, volumes, depends_on, image (+22 more)

### Community 12 - "InMemoryScopedCache"
Cohesion: 0.07
Nodes (9): _CacheEntry, _component(), _digest(), _identifier(), InvalidationReason, ScopedCacheAdapter, ScopedCacheKey, _serialized_size() (+1 more)

### Community 13 - "PostgresIdentityStore"
Cohesion: 0.12
Nodes (4): _department_uuid(), IdentityRecord, normalize_roles(), PostgresIdentityStore

### Community 14 - "core/chat.py"
Cohesion: 0.07
Nodes (13): ActorKind, AnonymousSession, CheckpointRepository, _citation_expired(), ConversationRepository, ConversationSummary, ConversationView, DurableChatRepository (+5 more)

### Community 15 - "CacheScope"
Cohesion: 0.12
Nodes (8): CacheScope, StaleScopeError, InMemoryChatRepository, JobCheckpoint, MessageRecord, QueryJob, QueryJobRepository, _jsonb()

### Community 16 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, networks (+12 more)

### Community 17 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, networks (+12 more)

### Community 18 - "PromptDefinition"
Cohesion: 0.11
Nodes (5): default_prompt_registry(), _freeze(), PromptDefinition, PromptRegistry, PromptRegistryTests

### Community 19 - "package.json"
Cohesion: 0.05
Nodes (51): dependencies, react@18.3.1, react-dom@18.3.1, vite@6.3.5, @vitejs/plugin-react@4.6.0, devDependencies, eslint@9.17.0, @eslint/js@9.17.0 (+43 more)

### Community 20 - "answer_baseline/test_security_adversarial.py"
Cohesion: 0.10
Nodes (19): AnswerModelGateway, GeneratedAnswer, _AnswerModel, _allow(), FakeModelGateway, _pipeline(), test_cross_tenant_evidence_is_absent_from_dense_bm25_and_answer(), test_direct_prompt_injection_is_denied_before_retrieval_and_model() (+11 more)

### Community 21 - "AuthorizationContractIntegrationTests"
Cohesion: 0.26
Nodes (4): AuthorizationContractIntegrationTests, document(), evaluator(), principal()

### Community 22 - "orchestration/context.py"
Cohesion: 0.20
Nodes (6): ContextLimitError, estimate_tokens(), PromptMessage, _render_evidence(), _safe_text(), _safe_value()

### Community 23 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+10 more)

### Community 24 - "InMemoryConversationMemory"
Cohesion: 0.13
Nodes (3): InvalidationEvent, ConversationMemoryRepository, InMemoryConversationMemory

### Community 25 - "model/test_e2e_operational.py"
Cohesion: 0.09
Nodes (35): graph_labels(), policy(), provider(), route(), run_graph_query(), ScriptedEmbedding, task(), test_embedding_route_task_is_checked() (+27 more)

### Community 26 - "api/chat.py"
Cohesion: 0.09
Nodes (28): _anonymous_token(), _body(), _context(), create_conversation(), download_citation(), FeedbackRequest, get_conversation(), get_query_completion() (+20 more)

### Community 27 - "_make_retriever"
Cohesion: 0.06
Nodes (62): AuthorizationEvaluator, InMemoryPolicyStore, PolicyEnforcementPoint, DenseRetriever, InMemoryDenseVectorIndex, HybridRetrievalConfig, HybridRetriever, InMemoryBM25Index (+54 more)

### Community 28 - "AuthorizationEvaluator"
Cohesion: 0.07
Nodes (18): AccessGrant, Action, AuthorizationDenied, deny(), Classification, ConversationResource, DocumentResource, Effect (+10 more)

### Community 29 - "chat_api/test_contract_integration.py"
Cohesion: 0.12
Nodes (19): job_payload(), JobState, anonymous_conversation(), authenticated_conversation(), Clock, Executor, Maintenance, make_service() (+11 more)

### Community 30 - "InMemoryIdentityStore"
Cohesion: 0.10
Nodes (6): DepartmentRecord, Role, hash_secret(), InMemoryIdentityStore, verify_secret(), test_noncanonical_role_cannot_create_identity()

### Community 31 - "chat_api/test_behavior_component.py"
Cohesion: 0.15
Nodes (19): AnswerState, anonymous_conversation(), authenticated_conversation(), Clock, Executor, Maintenance, make_service(), principal() (+11 more)

### Community 32 - "DocumentVersionMetadata"
Cohesion: 0.11
Nodes (11): DocumentVersionMetadata, test_active_chunk_requires_acl_metadata(), test_chunk_rejects_reversed_pages(), test_chunk_rejects_self_parent(), test_document_version_identity_is_stable(), test_document_version_requires_private_source(), test_hashes_are_normalized(), test_root_chunk_can_have_no_parent() (+3 more)

### Community 33 - "GraphifyOperationalTests"
Cohesion: 0.11
Nodes (5): DatabaseMigrationSmokeTests, graph(), graphify_bin(), run_graphify(), GraphifyOperationalTests

### Community 34 - "key"
Cohesion: 0.11
Nodes (36): ScanVerdict, key(), prepare_review_two(), publish(), test_manager_activates_provisioned_account(), test_manager_completes_two_review_publication(), test_manager_provisions_inactive_employee(), test_manager_uploads_into_quarantine() (+28 more)

### Community 35 - "chat_api/test_security_adversarial.py"
Cohesion: 0.17
Nodes (17): QueryCompletion, anonymous_conversation(), authenticated_conversation(), Clock, Executor, Maintenance, make_service(), principal() (+9 more)

### Community 36 - "steps"
Cohesion: 0.15
Nodes (12): jobs, validate, name, on, pull_request, workflow_dispatch, run, uses (+4 more)

### Community 37 - "DataClassification"
Cohesion: 0.06
Nodes (72): ModelEgressDenied, ModelGateway, ModelProviderError, ModelUnavailable, EmbeddingAdapter, EmbeddingRequest, EmbeddingResult, RankedDocument (+64 more)

### Community 40 - "rules"
Cohesion: 0.17
Nodes (11): runbook, summary, groups, name, rules, severity, alert, annotations (+3 more)

### Community 41 - "hashlib"
Cohesion: 0.07
Nodes (18): IdentityError, rate_limited(), SessionRecord, utc_z(), AuthenticationService, IdentityErrorPassthrough, now_utc(), IdentityStore (+10 more)

### Community 42 - "dense.py"
Cohesion: 0.14
Nodes (9): _citation(), _cosine(), DenseEvidence, DenseRetrievalResult, SourceFetchResult, _uuid(), _valid_locator(), _vectorize() (+1 more)

### Community 43 - "ToolResult"
Cohesion: 0.10
Nodes (14): AuthorizedScope, GetDocumentMetadataArguments, PrincipalResolver, ReadAuthorizedChunkArguments, _safe_tool_result(), ScopeResolver, SearchDocumentsArguments, ToolBackend (+6 more)

### Community 44 - "App.tsx"
Cohesion: 0.09
Nodes (35): ApprovalRecord, getDashboard(), setAccessToken(), signIn(), submitAccessRequest(), UserRecord, AdminGuardView(), AnswerDetails() (+27 more)

### Community 45 - "route"
Cohesion: 0.18
Nodes (10): global, resolve_timeout, receivers, name, route, group_by, group_interval, group_wait (+2 more)

### Community 46 - "gemini.py"
Cohesion: 0.12
Nodes (7): GeminiProviderError, GeminiStreamProvider, _http_error_code(), _text_parts(), _FakeGemini, test_gemini_adapter_uses_server_header_and_parses_sse_without_echoing_key(), close()

### Community 47 - "test_knowledge_database.py"
Cohesion: 0.26
Nodes (11): migration_text(), test_existing_db_contract_has_active_index_guard(), test_existing_db_contract_has_chunks_table(), test_existing_db_contract_has_composite_parent_fk(), test_existing_db_contract_has_document_versions_table(), test_existing_db_contract_has_documents_table(), test_existing_db_contract_has_immutable_version_uniqueness(), test_existing_db_contract_has_private_source_constraint() (+3 more)

### Community 48 - "chat_api/test_e2e_operational.py"
Cohesion: 0.23
Nodes (15): anonymous_conversation(), HttpExecutor, request(), sign_in(), test_http_anonymous_lifecycle_and_session_isolation(), test_http_authenticated_history_and_job_are_owner_only(), test_http_citation_preview_and_download_reauthorize_after_revocation(), test_http_deadline_failure_is_safe_and_has_no_answer() (+7 more)

### Community 49 - "expand_parent_context"
Cohesion: 0.08
Nodes (53): _active(), ChildEvidence, _coerce_child(), _coerce_parent(), _construct(), expand_parent_context(), _identity(), _index_parents() (+45 more)

### Community 50 - "eval_001_runner.py"
Cohesion: 0.18
Nodes (12): _aggregate(), _AnswerModel, _Case, _DenseAsHybrid, evaluate(), _make_case(), _mean(), _percentile() (+4 more)

### Community 51 - "datasources"
Cohesion: 0.22
Nodes (8): apiVersion, datasources, access, editable, isDefault, name, type, url

### Community 52 - "monitoring/prometheus.yml"
Cohesion: 0.22
Nodes (8): global, evaluation_interval, scrape_interval, rule_files, scrape_configs, job_name, static_configs, targets

### Community 53 - "lifecycle.py"
Cohesion: 0.17
Nodes (9): ApprovalBlocked, ApprovalRecord, IdempotencyConflict, IndexPublication, InvalidInput, PublicationBlocked, _status(), VersionRecord (+1 more)

### Community 54 - "client.ts"
Cohesion: 0.08
Nodes (32): AccessGrant, AccessRequestMetadata, AccessRequestResponse, answerFromStream(), ApiError, AuditRecord, Conversation, ConversationMessage (+24 more)

### Community 56 - "AuthenticatedPrincipal"
Cohesion: 0.04
Nodes (61): AuthenticatedPrincipal, DOCXLocator, _ImmutableModel, PDFLocator, SourceSpan, XLSXLocator, _answer_citation(), AnswerCitation (+53 more)

### Community 57 - "request"
Cohesion: 0.13
Nodes (30): activateUser(), createDepartment(), createUser(), deleteDocument(), getAccessRequests(), getConversations(), getCurrentIdentity(), getDepartments() (+22 more)

### Community 58 - "_resolve"
Cohesion: 0.09
Nodes (67): _access_request_payload(), AccessGrantRequest, AccessRequest, AccessRequestReview, activate_user(), AdminApiState, approve_document_version(), _body() (+59 more)

### Community 59 - "upload"
Cohesion: 0.14
Nodes (22): Decision, add_user(), upload(), test_acl_explicit_deny_overrides_employee_read_allow(), test_anonymous_cannot_upload(), test_chairman_cannot_approve(), test_chairman_cannot_upload(), test_cross_tenant_document_is_not_revealed() (+14 more)

### Community 60 - "admin_api/test_behavior_component.py"
Cohesion: 0.15
Nodes (12): clean_state(), _prepare_review_two_without_index_ack(), test_manager_activates_provisioned_account(), test_manager_completes_two_review_publication(), test_manager_provisions_inactive_employee(), test_manager_uploads_into_quarantine(), test_publish_requires_acknowledged_index(), test_quarantined_document_is_not_readable() (+4 more)

### Community 61 - "tests/test_chat_api.py"
Cohesion: 0.20
Nodes (13): anonymous_conversation(), authenticated_headers(), request(), StubExecutor, test_anonymous_submit_status_completion_and_history_are_session_scoped(), test_authenticated_history_is_owner_only_and_revocation_denies_reuse(), test_citation_preview_and_download_are_separate_fresh_authorization_checks(), test_cross_origin_anonymous_cookie_is_usable_by_vercel_fetch() (+5 more)

### Community 62 - "request"
Cohesion: 0.10
Nodes (51): auth(), request(), test_account_response_does_not_return_password(), test_approval_schema_requires_explicit_stage(), test_existing_sign_in_contract_remains_under_auth_prefix(), test_job_status_contains_redacted_progress_only(), test_mutating_post_requires_idempotency_key(), test_problem_response_uses_safe_media_type_for_anonymous_admin_call() (+43 more)

### Community 86 - "answer_baseline/test_behavior_component.py"
Cohesion: 0.15
Nodes (19): _authorization(), authorize(), FakeModelGateway, _pipeline(), RaisingRetriever, RaisingVerifier, StaticRetriever, test_constructor_rejects_non_positive_top_k() (+11 more)

### Community 87 - "orchestration_langgraph/test_security_adversarial.py"
Cohesion: 0.13
Nodes (20): Answerer, Backend, call(), Clock, gateway(), Policy, principal(), request() (+12 more)

### Community 88 - "model/test_contract_integration.py"
Cohesion: 0.21
Nodes (12): test_mapping_loads_versioned_policy_without_credentials(), test_policy_rejects_credential_fields(), mapping(), test_access_token_field_is_rejected(), test_embedding_gateway_contract_passes_request_route_and_timeout(), test_exact_api_key_field_is_rejected(), test_mapping_rejects_empty_model_revision(), test_secret_key_field_is_rejected() (+4 more)

### Community 89 - "_common.py"
Cohesion: 0.20
Nodes (3): load_frontend_json(), read(), FrontendContractIntegrationTests

### Community 90 - "test_authorization.py"
Cohesion: 0.36
Nodes (15): document(), evaluator(), principal(), test_acl_can_assign_employee_and_explicit_deny_wins_for_chairman(), test_anonymous_is_public_only(), test_chairman_is_read_only(), test_conversation_body_is_owner_only(), test_conversation_requires_conversation_resource() (+7 more)

### Community 91 - "normalize_user_input"
Cohesion: 0.07
Nodes (20): Citation, _citation(), detect_prompt_injection(), GuardrailResult, _inspect_text(), inspect_untrusted_content(), _luhn_valid(), _normalize_text() (+12 more)

### Community 93 - "backend_boot/_baseline.py"
Cohesion: 0.22
Nodes (4): assignment(), pyproject(), route_calls(), route_path()

### Community 94 - "rag/runtime.py"
Cohesion: 0.11
Nodes (14): AnonymousPrincipal, AnswerStatus, _answer_covers_evidence(), _answer_has_term(), _claim_terms(), _LocalAnswerModel, LocalRagExecutor, _relevant_evidence() (+6 more)

### Community 95 - "evaluator"
Cohesion: 0.43
Nodes (4): AuthorizationSecurityAdversarialTests, document(), evaluator(), principal()

### Community 96 - "inherit_acl"
Cohesion: 0.17
Nodes (5): make_child(), make_parent(), make_version(), KnowledgeContractIntegrationTests, KnowledgeSecurityAdversarialTests

### Community 97 - "env.py"
Cohesion: 0.38
Nodes (3): _database_url(), run_migrations_offline(), run_migrations_online()

### Community 98 - "test_tool_gateway.py"
Cohesion: 0.15
Nodes (22): _Backend, _call(), _Clock, _gateway(), _Policy, _principal(), _Resolvers, test_backend_exception_is_unavailable_without_raw_error() (+14 more)

### Community 99 - "AnswerDraft"
Cohesion: 0.23
Nodes (20): ToolResult, _Answerer, _Clock, _evidence(), _orchestrator(), _request(), test_answerer_error_is_returned_as_safe_error(), test_complex_route_splits_subqueries_and_preserves_bound() (+12 more)

### Community 102 - "load_validated_records"
Cohesion: 0.22
Nodes (13): evaluation_snapshot(), load_validated_records(), test_all_golden_cases_run_through_v1_v3(), test_allowed_answer_has_no_unauthorized_retrieval_marker(), test_answered_case_keeps_citation_version_and_tenant_binding(), test_dataset_contains_permission_negative_and_cross_tenant_cases(), test_empty_query_is_denied_before_retrieval(), test_model_failure_returns_error_without_source_or_answer() (+5 more)

### Community 103 - "IngestionService"
Cohesion: 0.14
Nodes (20): IngestionService, _active_document(), _principal(), _retriever(), test_dense_retrieval_returns_authorized_current_chunk_only(), test_explicit_deny_candidates_are_not_exposed(), test_forbidden_source_fetch_is_redacted_without_content_or_citation(), test_active_retrieval_to_evidence_verification_succeeds() (+12 more)

### Community 104 - "EvidenceRecord"
Cohesion: 0.27
Nodes (13): SourceSpan, citation(), test_authorization_callback_error_fails_closed(), test_current_active_version_is_required_by_authorization_attestation(), test_negation_mismatch_is_conflicting_not_supported(), test_numeric_mismatch_is_conflicting_not_supported(), test_repeated_verification_is_deterministic(), test_source_span_and_citation_metadata_are_immutable() (+5 more)

### Community 105 - "evaluator"
Cohesion: 0.40
Nodes (4): AuthorizationBehaviorTests, document(), evaluator(), principal()

### Community 107 - "ToolResult"
Cohesion: 0.30
Nodes (16): Answerer, Clock, evidence(), request(), run(), test_answer_provider_failure_returns_error_without_exception_to_user(), test_deadline_timeout_is_a_visible_insufficient_outcome(), test_second_retrieval_round_recovers_a_temporarily_insufficient_answer() (+8 more)

### Community 108 - "new_service"
Cohesion: 0.08
Nodes (55): ScanReport, active(), new_service(), quarantine(), staged(), test_acknowledged_index_is_still_not_active(), test_clean_review_one_allows_processing(), test_processing_inherits_parent_acl() (+47 more)

### Community 109 - "test_answer_baseline.py"
Cohesion: 0.32
Nodes (10): _authorization(), authorize(), FakeModelGateway, _pipeline(), test_direct_answer_returns_insufficient_without_calling_model_when_no_match(), test_direct_answer_returns_partial_for_mixed_claims(), test_direct_answer_returns_supported_answer_and_authorized_citation(), test_guardrail_failure_fails_closed_before_model_call() (+2 more)

### Community 110 - "read"
Cohesion: 0.16
Nodes (5): backend_boot_task(), compile_sources_without_writes(), read(), task_packet(), BackendBootstrapOperationalTests

### Community 111 - "reset"
Cohesion: 0.06
Nodes (21): reset_state(), reset_state(), reset(), clean_state(), clean_state(), clean_state(), clean_state(), clean_state() (+13 more)

### Community 112 - "ChatView"
Cohesion: 0.27
Nodes (11): getAuditEvents(), getFeedback(), AuditView(), load(), ChatView(), closeHistory(), handleKeyDown(), newChat() (+3 more)

### Community 113 - "AuthorizationDecision"
Cohesion: 0.19
Nodes (22): EvidenceRecord, EvidenceVerifier, VerificationRequest, evidence_for(), verify_retrieved(), authorize(), allow_active(), citation() (+14 more)

### Community 114 - "answer_baseline/test_contract_integration.py"
Cohesion: 0.19
Nodes (15): _allow(), RecordingModel, RecordingRetriever, _setup(), test_citation_authorization_rejects_document_mismatch(), test_citation_authorization_rejects_non_active_status(), test_citation_authorization_rejects_non_current_version(), test_citation_authorization_rejects_revoked_source() (+7 more)

### Community 115 - "BoundedOrchestrator"
Cohesion: 0.10
Nodes (11): AssembledContext, AnswerSynthesizer, BoundedOrchestrator, _evidence_from_result(), _GraphState, OrchestrationOutcome, OrchestrationStatus, QueryRoute (+3 more)

### Community 116 - "answer_baseline/test_e2e_operational.py"
Cohesion: 0.09
Nodes (32): AuthorizationDecision, allow(), authorize(), revoked(), revoked(), current_v2(), authorize(), test_direct_answer_context_includes_authorized_parent_runtime() (+24 more)

### Community 117 - "read_frontend"
Cohesion: 0.14
Nodes (3): read_frontend(), FrontendBehaviorComponentTests, FrontendSecurityAdversarialTests

### Community 118 - "evidence/test_contract_integration.py"
Cohesion: 0.23
Nodes (6): allow_active(), citation(), test_chat_001_owns_preview_download_reauthorization_recheck(), test_duplicate_evidence_ids_are_a_malformed_fail_closed_result(), authorize(), test_supported_result_round_trips_tenant_document_version_and_span()

### Community 119 - "Claim"
Cohesion: 0.35
Nodes (13): Claim, allow_active(), citation(), test_authorizer_must_attest_active_current_and_not_revoked(), test_citation_and_source_span_are_immutable(), test_conflicting_numeric_source_spans_are_disclosed(), test_denial_result_does_not_leak_source_text(), test_stale_version_is_denied_even_when_text_matches() (+5 more)

### Community 120 - "cache_memory/test_security_adversarial.py"
Cohesion: 0.26
Nodes (12): make_key(), make_scope(), test_anonymous_revocation_isolated_to_one_session_and_fails_closed(), test_broad_scope_cannot_replay_after_a_narrow_document_change(), test_cache_key_excludes_queries_model_inputs_and_conversation_identifiers(), test_changed_document_version_cannot_repopulate_an_old_cache_entry(), test_cross_principal_cache_read_is_a_fail_closed_miss(), test_cross_scope_conversation_read_cannot_be_recovered_by_matching_id() (+4 more)

### Community 121 - "App.test.tsx"
Cohesion: 0.29
Nodes (4): adminPrincipal, conversationResponse(), json(), principal

### Community 122 - "cache_memory/test_contract_integration.py"
Cohesion: 0.36
Nodes (11): make_key(), make_scope(), test_contract_acl_change_can_target_one_principal_and_version(), test_contract_delete_event_invalidates_matching_scope_without_cross_tenant_reach(), test_contract_document_change_invalidates_broad_scope_and_selected_version(), test_contract_invalid_event_shapes_fail_closed_at_the_boundary(), test_contract_memory_read_requires_the_authoritative_current_scope(), test_contract_policy_epoch_change_requires_a_new_scope_for_reuse() (+3 more)

### Community 123 - "orchestration_langgraph/test_contract_integration.py"
Cohesion: 0.18
Nodes (16): Backend, call(), Clock, gateway(), Policy, principal(), Resolvers, test_chunk_read_contract_accepts_only_chunk_id_shape() (+8 more)

### Community 125 - "test_customer_api_e2e.py"
Cohesion: 0.10
Nodes (14): test_healthz_is_local_liveness_only(), test_identity_requires_bearer_credentials(), test_vercel_origin_can_use_cookie_authenticated_api(), anonymous_conversation(), parse_sse(), request(), stream_public_question(), test_access_request_idempotency_returns_the_original_request() (+6 more)

### Community 127 - "admin_api/test_contract_integration.py"
Cohesion: 0.16
Nodes (12): clean_state(), test_account_response_does_not_return_password(), test_approval_schema_requires_explicit_stage(), test_job_status_contains_redacted_progress_only(), test_mutating_post_requires_idempotency_key(), test_upload_accepts_docx_mime_inference(), test_upload_accepts_xlsx_mime_inference(), test_upload_idempotency_rejects_a_different_fingerprint() (+4 more)

### Community 130 - "manifest.json"
Cohesion: 0.15
Nodes (12): corpus_id, documents, provenance, external_sources, kind, owner, source, queries (+4 more)

### Community 131 - "main.py"
Cohesion: 0.19
Nodes (10): _bearer_token(), current_identity(), _record(), _record_identity_error(), _request_context(), sign_in(), sign_out(), SignInRequest (+2 more)

### Community 132 - "orchestration_langgraph/test_behavior_component.py"
Cohesion: 0.23
Nodes (16): AnswerDraft, Answerer, Clock, evidence(), request(), run(), test_compiles_a_state_graph_with_expected_nodes(), test_complex_loop_caps_subqueries_and_tool_calls_at_four() (+8 more)

### Community 133 - "test_chat_stream.py"
Cohesion: 0.41
Nodes (9): anonymous_conversation(), parse_sse(), request(), test_configured_provider_error_never_falls_back_to_local_answer(), test_local_fallback_streams_incrementally_and_cancels_before_completion(), test_local_sample_citation_preview_returns_safe_metadata_after_fresh_authz(), test_new_conversation_recovers_from_a_stale_anonymous_session(), test_no_key_stream_runs_local_rag_and_persists_answer() (+1 more)

### Community 134 - "ConversationMessage"
Cohesion: 0.14
Nodes (18): ConversationMemory, ConversationMessage, test_contract_fake_repository_implements_provider_neutral_memory_boundary(), Clock, FakeInvalidationBus, FakeMemoryRepository, make_key(), make_scope() (+10 more)

### Community 135 - "ingestion/test_security_adversarial.py"
Cohesion: 0.08
Nodes (16): Clock, graph_labels(), read(), run_graph_query(), RuntimeFailureOnRemove, service_with_index(), task(), test_task_and_handoff_keep_ingestion_provider_neutral() (+8 more)

### Community 136 - "ChunkMetadata"
Cohesion: 0.11
Nodes (19): _acl_digest(), _chunk_digest(), DerivedIndexRecord, IndexPublicationStatus, JobStage, JobState, MaintenanceStatus, ProcessingStatus (+11 more)

### Community 137 - "inherit_acl"
Cohesion: 0.37
Nodes (13): inherit_acl(), make_child(), make_parent(), test_conflicting_child_acl_is_denied(), test_document_mismatch_is_denied(), test_matching_child_acl_is_preserved(), test_missing_child_acl_is_inherited(), test_qdrant_projection_does_not_claim_authority() (+5 more)

### Community 138 - "ndcg_at_k"
Cohesion: 0.15
Nodes (16): answer_correctness(), citation_accuracy(), evaluate_case(), mean_reciprocal_rank(), ndcg_at_k(), no_answer_accuracy(), recall_at_k(), source_key() (+8 more)

### Community 140 - "ChatService"
Cohesion: 0.25
Nodes (5): ChatActor, ChatService, ConversationRecord, _error(), _fingerprint()

### Community 141 - "test_cache_memory.py"
Cohesion: 0.28
Nodes (12): Clock, response_key(), scope(), test_cache_delete_is_explicit(), test_cache_expires_and_rejects_unbounded_ttl_or_value(), test_cache_key_contains_security_scope_but_not_raw_query(), test_cache_requires_exact_current_scope_and_isolates_tenant_and_principal(), test_conversation_delete_removes_body_and_blocks_recreation_in_old_scope() (+4 more)

### Community 142 - "DocumentsView"
Cohesion: 0.70
Nodes (5): getDocuments(), uploadMetadataDocument(), DocumentsView(), load(), upload()

### Community 144 - "tests/test_dashboard_api.py"
Cohesion: 0.25
Nodes (6): clean_state(), test_anonymous_is_denied_dashboard_and_feedback(), test_feedback_review_is_private_bounded_and_replay_does_not_duplicate(), test_management_roles_can_read_empty_dashboard_and_feedback(), test_non_management_roles_are_denied_dashboard_and_feedback(), test_policy_outage_fails_closed_for_both_management_reads()

### Community 145 - "read"
Cohesion: 0.05
Nodes (7): read(), task(), tasks(), IdentityBehaviorTests, IdentityContractTests, IdentityOperationalTests, IdentitySecurityTests

### Community 146 - "build_secure_context"
Cohesion: 0.16
Nodes (5): build_secure_context(), RetrievedEvidence, PromptOperationalTests, PromptSecurityAdversarialTests, test_secure_context_escapes_parent_prompt_injection_as_untrusted_content()

### Community 150 - "observability/context.py"
Cohesion: 0.36
Nodes (4): _header(), _new_traceparent(), _valid_traceparent(), test_correlation_context_preserves_valid_headers_and_creates_child()

### Community 151 - "app/evidence/__init__.py"
Cohesion: 0.15
Nodes (11): CitationRecord, ClaimVerification, _is_negative(), _numeric_conflict(), _numeric_terms(), _relation(), _terms(), VerificationOutcome (+3 more)

### Community 152 - "InMemoryScopedCache"
Cohesion: 0.20
Nodes (15): InMemoryScopedCache, test_cache_invalidation_hooks_remove_only_matching_scope(), Clock, make_key(), make_scope(), test_broad_acl_invalidation_removes_all_versions_in_one_tenant(), test_cache_expires_at_the_exact_ttl_deadline(), test_cache_rejects_invalid_ttl_and_oversize_values() (+7 more)

### Community 153 - "ingestion/test_behavior_component.py"
Cohesion: 0.25
Nodes (6): test_empty_processing_input_is_rejected(), test_new_active_version_supersedes_previous_version(), test_publish_activates_authoritative_version_and_chunks(), test_review_one_requires_clean_scan(), test_staging_is_not_retrievable_before_ack_and_publish(), test_upload_is_quarantined_and_invisible()

### Community 154 - "test_rag_002_metrics.py"
Cohesion: 1.00
Nodes (3): _span(), _spans(), test_rag_002_regression_metrics_on_tiny_in_memory_corpus()

### Community 156 - "db/runtime.py"
Cohesion: 0.09
Nodes (18): _payload(), PostgresAccessRequestStore, _utc_z(), _answer_status(), _as_utc(), _membership_uuid(), normalize_database_url(), _parse_uuid() (+10 more)

### Community 157 - "DocumentMetadata"
Cohesion: 0.29
Nodes (3): DocumentMetadata, test_document_metadata_is_tenant_scoped(), test_document_metadata_contract_fields()

### Community 158 - "to_qdrant_payload"
Cohesion: 0.39
Nodes (10): to_qdrant_payload(), make_child(), make_parent(), test_acl_inheritance_populates_child_reference(), test_parent_child_contract_keeps_same_scope(), test_qdrant_projection_contains_index_state(), test_qdrant_projection_contains_scope_keys(), test_qdrant_projection_does_not_store_chunk_text() (+2 more)

### Community 159 - "UUID"
Cohesion: 0.15
Nodes (8): DocumentRecord, IngestionError, IngestionJob, InvalidTransition, MaintenanceBlocked, MaintenanceWindow, NotFound, RetentionBlocked

### Community 160 - "ApprovalsView"
Cohesion: 0.70
Nodes (5): getApprovals(), reviewDocumentVersion(), ApprovalsView(), approve(), load()

### Community 161 - "App"
Cohesion: 0.12
Nodes (29): clearAccessToken(), createConversation(), getConversation(), previewCitation(), signOut(), submitFeedback(), App(), closeAuth() (+21 more)

### Community 164 - "package.json"
Cohesion: 0.38
Nodes (5): dependencies, @neon/config@^1.14.0, @neon/env@^2.1.3, @neon/config, @neon/env

### Community 166 - "BackendBootstrapBehaviorTests"
Cohesion: 0.19
Nodes (4): calls(), function(), literal(), BackendBootstrapBehaviorTests

### Community 171 - "test_access_request_review.py"
Cohesion: 0.23
Nodes (9): clean_state(), create_request(), test_anonymous_request_uses_server_configured_tenant(), test_approve_is_idempotent_and_does_not_grant_access(), test_manager_cannot_list_or_review_another_tenant_request(), test_manager_lists_same_tenant_pending_requests_as_safe_metadata_only(), test_only_managers_can_review_access_requests(), test_review_rejects_key_reuse_and_conflicting_decision() (+1 more)

### Community 183 - "authorization/test_e2e_operational.py"
Cohesion: 0.33
Nodes (4): AuthorizationOperationalTests, document(), evaluator(), principal()

### Community 186 - "test_customer_frontend_static.py"
Cohesion: 0.15
Nodes (6): test_chat_controls_have_keyboard_labels_and_live_status_semantics(), test_mobile_375x812_contract_keeps_chat_controls_within_the_viewport(), test_reload_contract_restores_conversation_and_requests_history(), test_responsive_layout_has_mobile_breakpoints_and_no_horizontal_body_overflow(), test_retryable_backend_error_has_a_user_recovery_action(), test_stop_control_is_available_only_during_a_live_stream()

### Community 197 - "pytest"
Cohesion: 0.13
Nodes (31): IndexManifest, UploadManifest, make_chunks(), make_manifest(), validated(), test_doc_is_rejected(), test_internal_upload_requires_department(), test_manifest_checksum_mismatch_blocks_staging() (+23 more)

### Community 201 - "json"
Cohesion: 0.16
Nodes (4): load_records(), test_dashboard_has_api_and_security_panels(), test_dashboard_is_valid_json(), test_rag002_task_registry_keeps_retrieval_validation_and_scope()

## Knowledge Gaps
- **1 isolated node(s):** `enterprise-agentic-rag-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 1034 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **55 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AuthenticatedPrincipal` connect `AuthenticatedPrincipal` to `main.py`, `test_chat_stream.py`, `ChunkMetadata`, `ChatService`, `core/chat.py`, `AuthorizationContractIntegrationTests`, `api/chat.py`, `_make_retriever`, `AuthorizationEvaluator`, `chat_api/test_contract_integration.py`, `InMemoryIdentityStore`, `chat_api/test_behavior_component.py`, `chat_api/test_security_adversarial.py`, `DataClassification`, `hashlib`, `dense.py`, `ToolResult`, `eval_001_runner.py`, `authorization/test_e2e_operational.py`, `_resolve`, `orchestration_langgraph/test_security_adversarial.py`, `test_authorization.py`, `rag/runtime.py`, `evaluator`, `test_tool_gateway.py`, `IngestionService`, `evaluator`, `orchestration_langgraph/test_contract_integration.py`, `test_customer_api_e2e.py`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Are the 88 inferred relationships involving `DataClassification` (e.g. with `_require_manager()` and `UploadRequest`) actually correct?**
  _`DataClassification` has 88 INFERRED edges - model-reasoned connections that need verification._
- **What connects `enterprise-agentic-rag-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `audit.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10512820512820513 - nodes in this community are weakly interconnected._
- **Why does `IngestionService` connect `IngestionService` to `DocumentVersionMetadata`, `audit.py`, `main.py`, `pytest`, `DataClassification`, `InMemoryDerivedIndex`, `ChunkMetadata`, `ingestion/test_security_adversarial.py`, `dense.py`, `new_service`, `reset`, `eval_001_runner.py`, `answer_baseline/test_security_adversarial.py`, `lifecycle.py`, `_make_retriever`, `rag/runtime.py`, `UUID`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Are the 55 inferred relationships involving `IngestionService` (e.g. with `reset_state()` and `ChunkMetadata`) actually correct?**
  _`IngestionService` has 55 INFERRED edges - model-reasoned connections that need verification._
- **Should `compose` be split into smaller, more focused modules?**
  _Cohesion score 0.06838106370543542 - nodes in this community are weakly interconnected._