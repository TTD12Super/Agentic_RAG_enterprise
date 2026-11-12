# Graph Report - enterprise-agentic-rag-harness  (2026-11-12)

## Corpus Check
- 299 files · ~262,937 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 68 file(s) not represented in the graph (top: (none) 53, .toml 9, .example 2)

## Summary
- 4211 nodes · 12858 edges · 193 communities (120 shown, 73 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 858 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4496b66a`
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
- CacheScope
- request
- postgres
- postgres
- PromptDefinition
- package.json
- Claim
- AuthorizationContractIntegrationTests
- orchestration/context.py
- compilerOptions
- InMemoryConversationMemory
- normalize_user_input
- api/chat.py
- _make_retriever
- AuthorizationEvaluator
- chat_api/test_contract_integration.py
- DataClassification
- chat_api/test_behavior_component.py
- GraphifyOperationalTests
- key
- chat_api/test_security_adversarial.py
- steps
- DataClassification
- ContractIntegrationTests
- SecurityAdversarialTests
- rules
- hashlib
- validate_output
- ToolResult
- App.tsx
- route
- feedback/service.py
- test_knowledge_database.py
- chat_api/test_e2e_operational.py
- expand_parent_context
- _evaluation_harness.py
- datasources
- monitoring/prometheus.yml
- lifecycle.py
- client.ts
- PromptContractIntegrationTests
- dense.py
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
- app/guardrails/__init__.py
- make_manifest
- test_chat_stream.py
- evaluator
- inherit_acl
- env.py
- test_tool_gateway.py
- AnswerDraft
- main.py
- load_validated_records
- IngestionService
- EvidenceRecord
- Citation
- AuditContractTests
- ToolResult
- new_service
- quarantine
- read
- reset
- ChatView
- AuthorizationDecision
- answer_baseline/test_contract_integration.py
- BoundedOrchestrator
- answer_baseline/test_e2e_operational.py
- read_frontend
- AuditSecurityTests
- AuthorizationDecision
- cache_memory/test_security_adversarial.py
- App.test.tsx
- cache_memory/test_contract_integration.py
- orchestration_langgraph/test_contract_integration.py
- SecureContextBuilder
- test_customer_api_e2e.py
- AuditBehaviorTests
- admin_api/test_contract_integration.py
- run_local_guardrail_pipeline
- make_document
- manifest.json
- main.py
- orchestration_langgraph/test_behavior_component.py
- KnowledgeOperationalTests
- ConversationMessage
- ingestion/test_security_adversarial.py
- lifecycle.py
- inherit_acl
- ndcg_at_k
- tree
- ChatService
- test_cache_memory.py
- DocumentsView
- read
- build_secure_context
- test_sample_documents.py
- PromptBehaviorComponentTests
- app/evidence/__init__.py
- InMemoryScopedCache
- vercel.json
- db/runtime.py
- ChunkMetadata
- to_qdrant_payload
- ._now
- ApprovalsView
- App
- sys
- package.json
- DenseRetrievalContractIntegrationTests
- backend_boot/_baseline.py
- BehaviorComponentTests
- test_access_request_review.py
- authorization/test_e2e_operational.py
- test_customer_frontend_static.py
- pytest
- json
- admin.py

## God Nodes (most connected - your core abstractions)
1. `auth()` - 151 edges
2. `request()` - 150 edges
3. `IngestionService` - 119 edges
4. `DataClassification` - 98 edges
5. `AuthenticatedPrincipal` - 95 edges
6. `CacheScope` - 85 edges
7. `new_service()` - 85 edges
8. `_active_document()` - 78 edges
9. `key()` - 72 edges
10. `ModelGateway` - 68 edges

## Surprising Connections (you probably didn't know these)
- `literal()` --references--> `expr`  [EXTRACTED]
  tests/qa/backend_boot/_baseline.py → infra/monitoring/alerts.yml
- `reset_api_state()` --calls--> `InMemoryAuditSink`  [INFERRED]
  tests/qa/chat_api/test_contract_integration.py → backend/app/observability/audit.py
- `reset_api_state()` --calls--> `InMemoryAuditSink`  [INFERRED]
  tests/qa/chat_api/test_e2e_operational.py → backend/app/observability/audit.py
- `isolated_local_runtime()` --calls--> `InMemoryAuditSink`  [INFERRED]
  tests/qa/customer_experience/test_customer_api_e2e.py → backend/app/observability/audit.py
- `_build_corpus()` --calls--> `IngestionService`  [INFERRED]
  tests/qa/rag/test_sample_documents.py → backend/app/ingestion/lifecycle.py

## Import Cycles
- 2-file cycle: `backend/app/api/admin.py -> backend/app/api/identity.py -> backend/app/api/admin.py`
- 2-file cycle: `backend/app/api/admin.py -> backend/app/api/chat.py -> backend/app/api/admin.py`
- 2-file cycle: `backend/app/api/chat.py -> backend/app/api/identity.py -> backend/app/api/chat.py`
- 3-file cycle: `backend/app/api/admin.py -> backend/app/api/identity.py -> backend/app/api/chat.py -> backend/app/api/admin.py`
- 3-file cycle: `backend/app/api/admin.py -> backend/app/api/chat.py -> backend/app/api/identity.py -> backend/app/api/admin.py`

## Communities (193 total, 73 thin omitted)

### Community 0 - "audit.py"
Cohesion: 0.09
Nodes (21): append_audit_event(), AuditEvent, AuditSink, AuditSinkUnavailable, InMemoryAuditSink, redact_metadata(), _safe_code(), _safe_identifier() (+13 more)

### Community 1 - "compose"
Cohesion: 0.07
Nodes (11): compose(), compose_config_result(), database(), handoff(), read(), tasks(), testing(), DisposablePostgresBehaviorTests (+3 more)

### Community 2 - "read"
Cohesion: 0.05
Nodes (10): compose_config_result(), migration_files(), migration_text(), read(), task(), tasks(), DatabaseBaselineBehaviorTests, DatabaseBaselineContractTests (+2 more)

### Community 3 - "read"
Cohesion: 0.05
Nodes (8): compose_config(), read(), task(), tasks(), InfrastructureBehaviorTests, InfrastructureContractTests, InfrastructureOperationalTests, InfrastructureSecurityTests

### Community 4 - "read"
Cohesion: 0.18
Nodes (4): read(), task(), tasks(), AuditOperationalTests

### Community 5 - "section"
Cohesion: 0.08
Nodes (7): json_blocks(), require_all(), section(), BehaviorComponentTests, ContractIntegrationTests, E2EOperationalTests, SecurityAdversarialTests

### Community 6 - "read"
Cohesion: 0.06
Nodes (7): dashboard(), read(), task(), MonitoringBehaviorTests, MonitoringContractTests, MonitoringOperationalTests, MonitoringSecurityTests

### Community 7 - "InMemoryDerivedIndex"
Cohesion: 0.14
Nodes (6): _chunk_state(), DerivedIndex, DerivedIndexFailure, DerivedIndexRecord, IndexPublication, InMemoryDerivedIndex

### Community 8 - "read"
Cohesion: 0.09
Nodes (5): graph(), read(), GraphifyBehaviorTests, GraphifyContractTests, GraphifySecurityTests

### Community 9 - "otel-collector-config.yaml"
Cohesion: 0.06
Nodes (32): action, key, actions, send_batch_size, timeout, exporters, prometheus, endpoint (+24 more)

### Community 10 - "prometheus"
Cohesion: 0.06
Nodes (30): command, image, ports, read_only, security_opt, volumes, depends_on, image (+22 more)

### Community 12 - "InMemoryScopedCache"
Cohesion: 0.06
Nodes (11): _CacheEntry, _component(), _digest(), _identifier(), InvalidationReason, ScopedCacheAdapter, ScopedCacheKey, _serialized_size() (+3 more)

### Community 13 - "PostgresIdentityStore"
Cohesion: 0.08
Nodes (14): _answer_status(), _department_uuid(), _membership_uuid(), normalize_database_url(), _PostgresAdapter, PostgresAuditSink, RuntimeDatabaseUnavailable, stable_uuid() (+6 more)

### Community 14 - "CacheScope"
Cohesion: 0.07
Nodes (18): CacheScope, StaleScopeError, ActorKind, AnonymousSession, CheckpointRepository, _citation_expired(), ConversationRecord, ConversationRepository (+10 more)

### Community 15 - "request"
Cohesion: 0.12
Nodes (28): request(), test_acl_update_advances_policy_epoch(), test_activation_allows_follow_up_sign_in(), test_admin_mutations_emit_privacy_safe_audit_events(), test_anonymous_is_denied_management_api(), test_chairman_is_denied_management_api(), test_employee_is_denied_management_api(), test_manager_completes_http_lifecycle_with_worker_boundary() (+20 more)

### Community 16 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, networks (+12 more)

### Community 17 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, networks (+12 more)

### Community 18 - "PromptDefinition"
Cohesion: 0.12
Nodes (5): default_prompt_registry(), _freeze(), PromptDefinition, PromptRegistry, PromptRegistryTests

### Community 19 - "package.json"
Cohesion: 0.05
Nodes (51): dependencies, react@18.3.1, react-dom@18.3.1, vite@6.3.5, @vitejs/plugin-react@4.6.0, devDependencies, eslint@9.17.0, @eslint/js@9.17.0 (+43 more)

### Community 20 - "Claim"
Cohesion: 0.09
Nodes (25): Claim, GeneratedAnswer, _AnswerModel, _AnswerModel, _authorization(), FakeModelGateway, _pipeline(), test_direct_answer_returns_insufficient_without_calling_model_when_no_match() (+17 more)

### Community 21 - "AuthorizationContractIntegrationTests"
Cohesion: 0.26
Nodes (4): AuthorizationContractIntegrationTests, document(), evaluator(), principal()

### Community 22 - "orchestration/context.py"
Cohesion: 0.20
Nodes (6): ContextLimitError, estimate_tokens(), PromptMessage, _render_evidence(), _safe_text(), _safe_value()

### Community 23 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+10 more)

### Community 25 - "normalize_user_input"
Cohesion: 0.17
Nodes (3): normalize_user_input(), GuardrailBehaviorTests, GuardrailSecurityAdversarialTests

### Community 26 - "api/chat.py"
Cohesion: 0.17
Nodes (21): _anonymous_token(), _body(), _context(), create_conversation(), download_citation(), FeedbackRequest, get_conversation(), get_query_completion() (+13 more)

### Community 27 - "_make_retriever"
Cohesion: 0.05
Nodes (65): Action, InMemoryPolicyStore, PolicyEnforcementPoint, RerankerRequest, ProviderPolicy, DenseRetriever, DeterministicEmbeddingAdapter, InMemoryDenseVectorIndex (+57 more)

### Community 28 - "AuthorizationEvaluator"
Cohesion: 0.06
Nodes (26): AccessGrant, AuthorizationDenied, AuthorizationEvaluator, deny(), Classification, ConversationResource, Decision, DocumentResource (+18 more)

### Community 29 - "chat_api/test_contract_integration.py"
Cohesion: 0.11
Nodes (20): job_payload(), JobState, anonymous_conversation(), authenticated_conversation(), Clock, Executor, Maintenance, make_service() (+12 more)

### Community 30 - "DataClassification"
Cohesion: 0.14
Nodes (36): FakeEmbedding, policy(), provider(), route(), test_approved_local_fallback_can_handle_internal_data(), test_approved_local_provider_can_process_internal_data(), test_denial_error_does_not_echo_model_input(), test_embedding_result_requires_consistent_dimensions() (+28 more)

### Community 31 - "chat_api/test_behavior_component.py"
Cohesion: 0.15
Nodes (19): AnswerState, anonymous_conversation(), authenticated_conversation(), Clock, Executor, Maintenance, make_service(), principal() (+11 more)

### Community 33 - "GraphifyOperationalTests"
Cohesion: 0.11
Nodes (7): DatabaseMigrationSmokeTests, graphify_bin(), run_graphify(), GraphifyOperationalTests, run_graph_query(), run_graph_query(), test_graphify_query_finds_model_gateway()

### Community 34 - "key"
Cohesion: 0.14
Nodes (28): ScanVerdict, key(), prepare_review_two(), publish(), test_manager_activates_provisioned_account(), test_manager_completes_two_review_publication(), test_manager_provisions_inactive_employee(), test_manager_uploads_into_quarantine() (+20 more)

### Community 35 - "chat_api/test_security_adversarial.py"
Cohesion: 0.15
Nodes (20): QueryCompletion, anonymous_conversation(), authenticated_conversation(), Clock, Executor, Maintenance, make_service(), principal() (+12 more)

### Community 36 - "steps"
Cohesion: 0.15
Nodes (12): jobs, validate, name, on, pull_request, workflow_dispatch, run, uses (+4 more)

### Community 37 - "DataClassification"
Cohesion: 0.06
Nodes (67): ModelEgressDenied, ModelGateway, ModelProviderError, ModelUnavailable, EmbeddingAdapter, EmbeddingRequest, EmbeddingResult, RankedDocument (+59 more)

### Community 40 - "rules"
Cohesion: 0.17
Nodes (11): runbook, summary, groups, name, rules, severity, alert, annotations (+3 more)

### Community 41 - "hashlib"
Cohesion: 0.05
Nodes (24): IdentityError, rate_limited(), DepartmentRecord, Role, SessionRecord, utc_z(), AuthenticationService, IdentityErrorPassthrough (+16 more)

### Community 42 - "validate_output"
Cohesion: 0.26
Nodes (8): _citation(), detect_prompt_injection(), GuardrailResult, _inspect_text(), _normalize_text(), _sensitive_terms(), _terms(), validate_output()

### Community 43 - "ToolResult"
Cohesion: 0.11
Nodes (12): GetDocumentMetadataArguments, PrincipalResolver, ReadAuthorizedChunkArguments, _safe_tool_result(), ScopeResolver, SearchDocumentsArguments, ToolBackend, ToolCall (+4 more)

### Community 44 - "App.tsx"
Cohesion: 0.09
Nodes (35): ApprovalRecord, getDashboard(), setAccessToken(), signIn(), submitAccessRequest(), UserRecord, AdminGuardView(), AnswerDetails() (+27 more)

### Community 45 - "route"
Cohesion: 0.18
Nodes (10): global, resolve_timeout, receivers, name, route, group_by, group_interval, group_wait (+2 more)

### Community 46 - "feedback/service.py"
Cohesion: 0.16
Nodes (7): FeedbackRecord, FeedbackRepository, FeedbackReview, FeedbackService, InMemoryFeedbackRepository, test_feedback_replay_is_idempotent_but_tenant_bound(), test_feedback_review_projection_has_no_actor_comment_or_body()

### Community 47 - "test_knowledge_database.py"
Cohesion: 0.26
Nodes (11): migration_text(), test_existing_db_contract_has_active_index_guard(), test_existing_db_contract_has_chunks_table(), test_existing_db_contract_has_composite_parent_fk(), test_existing_db_contract_has_document_versions_table(), test_existing_db_contract_has_documents_table(), test_existing_db_contract_has_immutable_version_uniqueness(), test_existing_db_contract_has_private_source_constraint() (+3 more)

### Community 48 - "chat_api/test_e2e_operational.py"
Cohesion: 0.23
Nodes (15): anonymous_conversation(), HttpExecutor, request(), sign_in(), test_http_anonymous_lifecycle_and_session_isolation(), test_http_authenticated_history_and_job_are_owner_only(), test_http_citation_preview_and_download_reauthorize_after_revocation(), test_http_deadline_failure_is_safe_and_has_no_answer() (+7 more)

### Community 49 - "expand_parent_context"
Cohesion: 0.09
Nodes (46): _active(), _coerce_child(), _coerce_parent(), _construct(), expand_parent_context(), _identity(), _index_parents(), ParentEvidence (+38 more)

### Community 50 - "_evaluation_harness.py"
Cohesion: 0.24
Nodes (12): _aggregate(), evaluate(), _mean(), _percentile(), _run_version(), citation_accuracy(), load_records(), source_key() (+4 more)

### Community 51 - "datasources"
Cohesion: 0.22
Nodes (8): apiVersion, datasources, access, editable, isDefault, name, type, url

### Community 52 - "monitoring/prometheus.yml"
Cohesion: 0.22
Nodes (8): global, evaluation_interval, scrape_interval, rule_files, scrape_configs, job_name, static_configs, targets

### Community 53 - "lifecycle.py"
Cohesion: 0.11
Nodes (15): ApprovalBlocked, ApprovalRecord, DocumentRecord, IdempotencyConflict, IngestionError, IngestionJob, InvalidInput, InvalidTransition (+7 more)

### Community 54 - "client.ts"
Cohesion: 0.08
Nodes (32): AccessGrant, AccessRequestMetadata, AccessRequestResponse, answerFromStream(), ApiError, AuditRecord, Conversation, ConversationMessage (+24 more)

### Community 56 - "dense.py"
Cohesion: 0.05
Nodes (54): DOCXLocator, _ImmutableModel, PDFLocator, SourceSpan, XLSXLocator, Citation, _citation(), _cosine() (+46 more)

### Community 57 - "request"
Cohesion: 0.13
Nodes (30): activateUser(), createDepartment(), createUser(), deleteDocument(), getAccessRequests(), getConversations(), getCurrentIdentity(), getDepartments() (+22 more)

### Community 58 - "_resolve"
Cohesion: 0.21
Nodes (37): activate_user(), approve_document_version(), _body(), _bump_policy_epoch(), create_department(), create_user(), delete_document(), _department_payload() (+29 more)

### Community 59 - "upload"
Cohesion: 0.14
Nodes (20): add_user(), upload(), test_acl_explicit_deny_overrides_employee_read_allow(), test_anonymous_cannot_upload(), test_chairman_cannot_approve(), test_chairman_cannot_upload(), test_cross_tenant_document_is_not_revealed(), test_employee_cannot_provision_accounts() (+12 more)

### Community 60 - "admin_api/test_behavior_component.py"
Cohesion: 0.15
Nodes (12): clean_state(), _prepare_review_two_without_index_ack(), test_manager_activates_provisioned_account(), test_manager_completes_two_review_publication(), test_manager_provisions_inactive_employee(), test_manager_uploads_into_quarantine(), test_publish_requires_acknowledged_index(), test_quarantined_document_is_not_readable() (+4 more)

### Community 61 - "tests/test_chat_api.py"
Cohesion: 0.23
Nodes (13): anonymous_conversation(), authenticated_headers(), request(), StubExecutor, test_anonymous_submit_status_completion_and_history_are_session_scoped(), test_authenticated_history_is_owner_only_and_revocation_denies_reuse(), test_citation_preview_and_download_are_separate_fresh_authorization_checks(), test_cross_origin_anonymous_cookie_is_usable_by_vercel_fetch() (+5 more)

### Community 62 - "request"
Cohesion: 0.12
Nodes (32): auth(), test_account_response_does_not_return_password(), test_approval_schema_requires_explicit_stage(), test_existing_sign_in_contract_remains_under_auth_prefix(), test_job_status_contains_redacted_progress_only(), test_mutating_post_requires_idempotency_key(), test_upload_accepts_docx_mime_inference(), test_upload_accepts_xlsx_mime_inference() (+24 more)

### Community 86 - "answer_baseline/test_behavior_component.py"
Cohesion: 0.15
Nodes (19): _authorization(), authorize(), FakeModelGateway, _pipeline(), RaisingRetriever, RaisingVerifier, StaticRetriever, test_constructor_rejects_non_positive_top_k() (+11 more)

### Community 87 - "orchestration_langgraph/test_security_adversarial.py"
Cohesion: 0.12
Nodes (21): AuthorizedScope, Answerer, Backend, call(), Clock, gateway(), Policy, principal() (+13 more)

### Community 91 - "app/guardrails/__init__.py"
Cohesion: 0.15
Nodes (6): _luhn_valid(), redact_sensitive_data(), redact_card(), RedactionResult, ToolDecision, validate_tool_request()

### Community 93 - "make_manifest"
Cohesion: 0.14
Nodes (19): make_manifest(), staged(), test_pdf_is_accepted(), test_cross_tenant_version_lookup_is_denied(), test_derived_index_cannot_authorize_non_active_version(), test_rejected_version_cannot_be_retrieved(), test_root_chunk_without_acl_fails_closed(), test_staging_index_cannot_be_retrieved() (+11 more)

### Community 94 - "test_chat_stream.py"
Cohesion: 0.06
Nodes (43): AnonymousPrincipal, GeminiProviderError, GeminiStreamProvider, _http_error_code(), _text_parts(), LocalRagExecutor, anonymous_conversation(), clean_state() (+35 more)

### Community 95 - "evaluator"
Cohesion: 0.43
Nodes (4): AuthorizationSecurityAdversarialTests, document(), evaluator(), principal()

### Community 96 - "inherit_acl"
Cohesion: 0.29
Nodes (4): inherit_acl(), make_child(), make_parent(), KnowledgeSecurityAdversarialTests

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
Cohesion: 0.20
Nodes (13): evaluation_snapshot(), load_validated_records(), test_all_golden_cases_run_through_v1_v3(), test_allowed_answer_has_no_unauthorized_retrieval_marker(), test_answered_case_keeps_citation_version_and_tenant_binding(), test_dataset_contains_permission_negative_and_cross_tenant_cases(), test_empty_query_is_denied_before_retrieval(), test_model_failure_returns_error_without_source_or_answer() (+5 more)

### Community 103 - "IngestionService"
Cohesion: 0.14
Nodes (20): IngestionService, _active_document(), _principal(), _retriever(), test_dense_retrieval_returns_authorized_current_chunk_only(), test_explicit_deny_candidates_are_not_exposed(), test_forbidden_source_fetch_is_redacted_without_content_or_citation(), test_active_retrieval_to_evidence_verification_succeeds() (+12 more)

### Community 104 - "EvidenceRecord"
Cohesion: 0.27
Nodes (13): SourceSpan, citation(), test_authorization_callback_error_fails_closed(), test_current_active_version_is_required_by_authorization_attestation(), test_negation_mismatch_is_conflicting_not_supported(), test_numeric_mismatch_is_conflicting_not_supported(), test_repeated_verification_is_deterministic(), test_source_span_and_citation_metadata_are_immutable() (+5 more)

### Community 107 - "ToolResult"
Cohesion: 0.30
Nodes (16): Answerer, Clock, evidence(), request(), run(), test_answer_provider_failure_returns_error_without_exception_to_user(), test_deadline_timeout_is_a_visible_insufficient_outcome(), test_second_retrieval_round_recovers_a_temporarily_insufficient_answer() (+8 more)

### Community 108 - "new_service"
Cohesion: 0.11
Nodes (36): active(), new_service(), test_acknowledged_index_is_still_not_active(), test_clean_review_one_allows_processing(), test_processing_inherits_parent_acl(), test_publishing_new_version_supersedes_previous_version(), test_rejected_scan_is_terminal_and_not_retrievable(), test_review_one_requires_clean_scan() (+28 more)

### Community 109 - "quarantine"
Cohesion: 0.13
Nodes (17): quarantine(), test_audit_sink_receives_lifecycle_events_without_content(), test_failed_maintenance_can_be_recovered_after_cleanup(), test_non_retryable_failure_is_terminal(), test_only_one_maintenance_window_is_active(), test_publication_failure_keeps_previous_active_version(), test_retry_is_bounded_and_preserves_checksum(), test_retry_with_changed_checksum_is_denied() (+9 more)

### Community 110 - "read"
Cohesion: 0.11
Nodes (6): backend_boot_task(), compile_sources_without_writes(), read(), task_packet(), BackendBootstrapContractTests, BackendBootstrapOperationalTests

### Community 111 - "reset"
Cohesion: 0.06
Nodes (21): reset_state(), reset_state(), reset(), clean_state(), clean_state(), clean_state(), clean_state(), clean_state() (+13 more)

### Community 112 - "ChatView"
Cohesion: 0.27
Nodes (11): getAuditEvents(), getFeedback(), AuditView(), load(), ChatView(), closeHistory(), handleKeyDown(), newChat() (+3 more)

### Community 113 - "AuthorizationDecision"
Cohesion: 0.13
Nodes (25): EvidenceRecord, EvidenceVerifier, VerificationRequest, allow_active(), citation(), test_chat_001_owns_preview_download_reauthorization_recheck(), test_duplicate_evidence_ids_are_a_malformed_fail_closed_result(), authorize() (+17 more)

### Community 114 - "answer_baseline/test_contract_integration.py"
Cohesion: 0.19
Nodes (15): _allow(), RecordingModel, RecordingRetriever, _setup(), test_citation_authorization_rejects_document_mismatch(), test_citation_authorization_rejects_non_active_status(), test_citation_authorization_rejects_non_current_version(), test_citation_authorization_rejects_revoked_source() (+7 more)

### Community 115 - "BoundedOrchestrator"
Cohesion: 0.08
Nodes (14): NoopQueryExecutor, AssembledContext, AnswerSynthesizer, BoundedOrchestrator, _evidence_from_result(), _GraphState, OrchestrationOutcome, OrchestrationRequest (+6 more)

### Community 116 - "answer_baseline/test_e2e_operational.py"
Cohesion: 0.17
Nodes (16): _allow(), FailingEmbedder, FailingReranker, FakeAnswerGateway, _setup(), test_operational_abstention_is_insufficient_evidence(), test_operational_conflicting_evidence_is_not_harmonized(), test_operational_denied_content_never_appears_in_failure_result() (+8 more)

### Community 117 - "read_frontend"
Cohesion: 0.07
Nodes (8): load_frontend_json(), read(), read_frontend(), run_frontend(), FrontendBehaviorComponentTests, FrontendContractIntegrationTests, FrontendE2EOperationalTests, FrontendSecurityAdversarialTests

### Community 119 - "AuthorizationDecision"
Cohesion: 0.11
Nodes (30): AuthorizationDecision, CitationRecord, _authorization_matches(), allow_active(), citation(), test_authorizer_must_attest_active_current_and_not_revoked(), revoked(), test_citation_and_source_span_are_immutable() (+22 more)

### Community 120 - "cache_memory/test_security_adversarial.py"
Cohesion: 0.28
Nodes (11): make_key(), make_scope(), test_anonymous_revocation_isolated_to_one_session_and_fails_closed(), test_broad_scope_cannot_replay_after_a_narrow_document_change(), test_cache_key_excludes_queries_model_inputs_and_conversation_identifiers(), test_changed_document_version_cannot_repopulate_an_old_cache_entry(), test_cross_principal_cache_read_is_a_fail_closed_miss(), test_cross_tenant_cache_read_is_a_fail_closed_miss() (+3 more)

### Community 121 - "App.test.tsx"
Cohesion: 0.29
Nodes (4): adminPrincipal, conversationResponse(), json(), principal

### Community 122 - "cache_memory/test_contract_integration.py"
Cohesion: 0.25
Nodes (11): FakeMemoryRepository, make_key(), make_scope(), test_contract_delete_event_invalidates_matching_scope_without_cross_tenant_reach(), test_contract_document_change_invalidates_broad_scope_and_selected_version(), test_contract_fake_repository_implements_provider_neutral_memory_boundary(), test_contract_invalid_event_shapes_fail_closed_at_the_boundary(), test_contract_policy_epoch_change_requires_a_new_scope_for_reuse() (+3 more)

### Community 123 - "orchestration_langgraph/test_contract_integration.py"
Cohesion: 0.18
Nodes (16): Backend, call(), Clock, gateway(), Policy, principal(), Resolvers, test_chunk_read_contract_accepts_only_chunk_id_shape() (+8 more)

### Community 124 - "SecureContextBuilder"
Cohesion: 0.20
Nodes (3): SecureContextBuilder, SecureContextBuilderTests, test_verifier_requires_a_server_supplied_authorization_callback()

### Community 125 - "test_customer_api_e2e.py"
Cohesion: 0.10
Nodes (14): test_healthz_is_local_liveness_only(), test_identity_requires_bearer_credentials(), test_vercel_origin_can_use_cookie_authenticated_api(), anonymous_conversation(), parse_sse(), request(), stream_public_question(), test_access_request_idempotency_returns_the_original_request() (+6 more)

### Community 127 - "admin_api/test_contract_integration.py"
Cohesion: 0.16
Nodes (12): clean_state(), test_account_response_does_not_return_password(), test_approval_schema_requires_explicit_stage(), test_job_status_contains_redacted_progress_only(), test_mutating_post_requires_idempotency_key(), test_upload_accepts_docx_mime_inference(), test_upload_accepts_xlsx_mime_inference(), test_upload_idempotency_rejects_a_different_fingerprint() (+4 more)

### Community 129 - "make_document"
Cohesion: 0.10
Nodes (10): DocumentVersionMetadata, test_document_version_identity_is_stable(), test_document_version_requires_private_source(), test_hashes_are_normalized(), test_version_contract_has_immutable_version_number(), test_version_contract_supports_publication_states(), make_document(), make_version() (+2 more)

### Community 130 - "manifest.json"
Cohesion: 0.15
Nodes (12): corpus_id, documents, provenance, external_sources, kind, owner, source, queries (+4 more)

### Community 131 - "main.py"
Cohesion: 0.10
Nodes (15): create_access_request(), _durable_access_request_store(), _bearer_token(), current_identity(), _record(), _record_identity_error(), _request_context(), sign_in() (+7 more)

### Community 132 - "orchestration_langgraph/test_behavior_component.py"
Cohesion: 0.23
Nodes (16): AnswerDraft, Answerer, Clock, evidence(), request(), run(), test_compiles_a_state_graph_with_expected_nodes(), test_complex_loop_caps_subqueries_and_tool_calls_at_four() (+8 more)

### Community 133 - "KnowledgeOperationalTests"
Cohesion: 0.22
Nodes (3): read(), task(), KnowledgeOperationalTests

### Community 134 - "ConversationMessage"
Cohesion: 0.13
Nodes (20): ConversationMemory, ConversationMessage, test_conversation_memory_is_scoped_bounded_and_repr_redacts_body(), test_contract_memory_read_requires_the_authoritative_current_scope(), Clock, FakeInvalidationBus, FakeMemoryRepository, make_key() (+12 more)

### Community 135 - "ingestion/test_security_adversarial.py"
Cohesion: 0.12
Nodes (11): Clock, RuntimeFailureOnRemove, service_with_index(), test_cleanup_backend_error_is_wrapped_without_secret_leakage(), test_cross_tenant_document_lookup_is_denied(), test_cross_tenant_job_lookup_is_denied(), test_cross_tenant_version_lookup_is_denied(), test_derived_staging_state_cannot_authorize_retrieval() (+3 more)

### Community 136 - "lifecycle.py"
Cohesion: 0.08
Nodes (22): _acl_digest(), _chunk_digest(), IndexPublicationStatus, JobStage, JobState, MaintenanceStatus, ProcessingStatus, PublicationStatus (+14 more)

### Community 137 - "inherit_acl"
Cohesion: 0.38
Nodes (12): make_child(), make_parent(), test_conflicting_child_acl_is_denied(), test_document_mismatch_is_denied(), test_matching_child_acl_is_preserved(), test_missing_child_acl_is_inherited(), test_qdrant_projection_does_not_claim_authority(), test_qdrant_projection_keeps_tenant_boundary() (+4 more)

### Community 138 - "ndcg_at_k"
Cohesion: 0.16
Nodes (13): answer_correctness(), evaluate_case(), mean_reciprocal_rank(), ndcg_at_k(), no_answer_accuracy(), recall_at_k(), E2EOperationalTests, _span() (+5 more)

### Community 140 - "ChatService"
Cohesion: 0.19
Nodes (5): ChatActor, ChatService, _error(), _fingerprint(), test_http_chat_reaches_local_rag_and_returns_verified_citation()

### Community 141 - "test_cache_memory.py"
Cohesion: 0.24
Nodes (11): Clock, response_key(), scope(), test_cache_delete_is_explicit(), test_cache_expires_and_rejects_unbounded_ttl_or_value(), test_cache_key_contains_security_scope_but_not_raw_query(), test_cache_requires_exact_current_scope_and_isolates_tenant_and_principal(), test_conversation_delete_removes_body_and_blocks_recreation_in_old_scope() (+3 more)

### Community 142 - "DocumentsView"
Cohesion: 0.70
Nodes (5): getDocuments(), uploadMetadataDocument(), DocumentsView(), load(), upload()

### Community 145 - "read"
Cohesion: 0.05
Nodes (7): read(), task(), tasks(), IdentityBehaviorTests, IdentityContractTests, IdentityOperationalTests, IdentitySecurityTests

### Community 146 - "build_secure_context"
Cohesion: 0.16
Nodes (5): build_secure_context(), RetrievedEvidence, PromptOperationalTests, PromptSecurityAdversarialTests, test_secure_context_escapes_parent_prompt_injection_as_untrusted_content()

### Community 148 - "test_sample_documents.py"
Cohesion: 0.07
Nodes (36): AnswerModelGateway, AnswerResult, DirectAnswerPipeline, _make_parent_child_retriever(), test_hybrid_runtime_expands_authorized_parent_after_reranking(), _CapturingModel, _Model, test_direct_answer_context_includes_authorized_parent_runtime() (+28 more)

### Community 151 - "app/evidence/__init__.py"
Cohesion: 0.21
Nodes (8): ClaimVerification, _is_negative(), _numeric_conflict(), _numeric_terms(), _relation(), _terms(), VerificationOutcome, VerificationResult

### Community 152 - "InMemoryScopedCache"
Cohesion: 0.21
Nodes (15): InMemoryScopedCache, test_cache_invalidation_hooks_remove_only_matching_scope(), Clock, make_key(), make_scope(), test_broad_acl_invalidation_removes_all_versions_in_one_tenant(), test_cache_expires_at_the_exact_ttl_deadline(), test_cache_rejects_invalid_ttl_and_oversize_values() (+7 more)

### Community 156 - "db/runtime.py"
Cohesion: 0.12
Nodes (10): JobCheckpoint, _payload(), PostgresAccessRequestStore, _utc_z(), _as_utc(), _jsonb(), _parse_uuid(), PostgresChatRepository (+2 more)

### Community 157 - "ChunkMetadata"
Cohesion: 0.16
Nodes (10): ChunkMetadata, DocumentMetadata, test_active_chunk_requires_acl_metadata(), test_chunk_accepts_source_provenance(), test_chunk_rejects_reversed_pages(), test_chunk_rejects_self_parent(), test_document_metadata_is_tenant_scoped(), test_root_chunk_can_have_no_parent() (+2 more)

### Community 158 - "to_qdrant_payload"
Cohesion: 0.39
Nodes (10): to_qdrant_payload(), make_child(), make_parent(), test_acl_inheritance_populates_child_reference(), test_parent_child_contract_keeps_same_scope(), test_qdrant_projection_contains_index_state(), test_qdrant_projection_contains_scope_keys(), test_qdrant_projection_does_not_store_chunk_text() (+2 more)

### Community 160 - "ApprovalsView"
Cohesion: 0.70
Nodes (5): getApprovals(), reviewDocumentVersion(), ApprovalsView(), approve(), load()

### Community 161 - "App"
Cohesion: 0.12
Nodes (29): clearAccessToken(), createConversation(), getConversation(), previewCitation(), signOut(), submitFeedback(), App(), closeAuth() (+21 more)

### Community 164 - "package.json"
Cohesion: 0.38
Nodes (5): dependencies, @neon/config@^1.14.0, @neon/env@^2.1.3, @neon/config, @neon/env

### Community 166 - "backend_boot/_baseline.py"
Cohesion: 0.10
Nodes (9): assignment(), calls(), function(), literal(), pyproject(), route_calls(), route_path(), tree() (+1 more)

### Community 171 - "test_access_request_review.py"
Cohesion: 0.13
Nodes (14): clean_state(), create_request(), test_anonymous_request_uses_server_configured_tenant(), test_approve_is_idempotent_and_does_not_grant_access(), test_manager_cannot_list_or_review_another_tenant_request(), test_manager_lists_same_tenant_pending_requests_as_safe_metadata_only(), test_only_managers_can_review_access_requests(), test_review_rejects_key_reuse_and_conflicting_decision() (+6 more)

### Community 183 - "authorization/test_e2e_operational.py"
Cohesion: 0.33
Nodes (4): AuthorizationOperationalTests, document(), evaluator(), principal()

### Community 186 - "test_customer_frontend_static.py"
Cohesion: 0.15
Nodes (6): test_chat_controls_have_keyboard_labels_and_live_status_semantics(), test_mobile_375x812_contract_keeps_chat_controls_within_the_viewport(), test_reload_contract_restores_conversation_and_requests_history(), test_responsive_layout_has_mobile_breakpoints_and_no_horizontal_body_overflow(), test_retryable_backend_error_has_a_user_recovery_action(), test_stop_control_is_available_only_during_a_live_stream()

### Community 197 - "pytest"
Cohesion: 0.12
Nodes (28): IndexManifest, UploadManifest, make_chunks(), validated(), test_approval_expiry_blocks_publication(), test_doc_is_rejected(), test_internal_upload_requires_department(), test_manifest_checksum_mismatch_blocks_staging() (+20 more)

### Community 201 - "json"
Cohesion: 0.18
Nodes (3): test_dashboard_has_api_and_security_panels(), test_dashboard_is_valid_json(), test_rag002_task_registry_keeps_retrieval_validation_and_scope()

### Community 209 - "admin.py"
Cohesion: 0.09
Nodes (25): _access_request_payload(), AccessGrantRequest, AccessRequest, AccessRequestReview, AdminApiState, _counts(), _dashboard_metric(), _dashboard_metrics() (+17 more)

## Knowledge Gaps
- **1 isolated node(s):** `enterprise-agentic-rag-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 1028 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **73 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AuthenticatedPrincipal` connect `AuthorizationEvaluator` to `main.py`, `lifecycle.py`, `ChatService`, `CacheScope`, `test_sample_documents.py`, `AuthorizationContractIntegrationTests`, `api/chat.py`, `_make_retriever`, `chat_api/test_contract_integration.py`, `chat_api/test_behavior_component.py`, `field_validator`, `chat_api/test_security_adversarial.py`, `hashlib`, `ToolResult`, `authorization/test_e2e_operational.py`, `dense.py`, `_resolve`, `admin.py`, `orchestration_langgraph/test_security_adversarial.py`, `test_chat_stream.py`, `evaluator`, `test_tool_gateway.py`, `IngestionService`, `orchestration_langgraph/test_contract_integration.py`, `test_customer_api_e2e.py`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Are the 46 inferred relationships involving `IngestionService` (e.g. with `reset_state()` and `test_active_retrieval_to_evidence_verification_succeeds()`) actually correct?**
  _`IngestionService` has 46 INFERRED edges - model-reasoned connections that need verification._
- **What connects `enterprise-agentic-rag-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `audit.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08599290780141844 - nodes in this community are weakly interconnected._
- **Why does `DataClassification` connect `DataClassification` to `pytest`, `IngestionService`, `lifecycle.py`, `admin.py`, `answer_baseline/test_contract_integration.py`, `test_sample_documents.py`, `lifecycle.py`, `Claim`, `answer_baseline/test_behavior_component.py`, `dense.py`, `answer_baseline/test_e2e_operational.py`, `_make_retriever`, `AuthorizationEvaluator`, `make_manifest`, `DataClassification`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Are the 47 inferred relationships involving `DataClassification` (e.g. with `ModelEgressDenied` and `ModelGateway`) actually correct?**
  _`DataClassification` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Should `compose` be split into smaller, more focused modules?**
  _Cohesion score 0.07017543859649122 - nodes in this community are weakly interconnected._