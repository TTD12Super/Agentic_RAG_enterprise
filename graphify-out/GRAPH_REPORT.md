# Graph Report - enterprise-agentic-rag-harness  (2026-11-12)

## Corpus Check
- 294 files · ~257,663 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 68 file(s) not represented in the graph (top: (none) 53, .toml 9, .example 2)

## Summary
- 4146 nodes · 12619 edges · 202 communities (132 shown, 70 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 870 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `31e43ea7`
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
- ModelPolicy
- read
- otel-collector-config.yaml
- prometheus
- env.py
- InMemoryScopedCache
- DataClassification
- QueryJob
- knowledge/models.py
- postgres
- postgres
- PromptDefinition
- package.json
- identity.py
- evaluator
- core/chat.py
- compilerOptions
- InMemoryConversationMemory
- ModelProviderError
- api/chat.py
- _make_retriever
- AuthorizationEvaluator
- chat_api/test_contract_integration.py
- DataClassification
- chat_api/test_behavior_component.py
- rag/runtime.py
- GraphifyOperationalTests
- key
- chat_api/test_security_adversarial.py
- steps
- models/policy.py
- ContractIntegrationTests
- SecurityAdversarialTests
- rules
- lifecycle.py
- BackendBootstrapBehaviorTests
- ToolResult
- Icon
- route
- feedback/service.py
- test_knowledge_database.py
- chat_api/test_e2e_operational.py
- expand_parent_context
- App.tsx
- datasources
- monitoring/prometheus.yml
- UUID
- client.ts
- CitationArtifact
- AuthenticatedPrincipal
- request
- admin.py
- upload
- sys
- tests/test_chat_api.py
- request
- model/test_e2e_operational.py
- vite-env.d.ts
- sync_graph.sh
- migrate.sh
- inspect_untrusted_content
- enterprise-agentic-rag-backend
- answer_baseline/test_behavior_component.py
- orchestration_langgraph/test_security_adversarial.py
- unittest
- new_service
- gemini.py
- rag_v4_citation/test_e2e_operational.py
- inherit_acl
- FrontendE2EOperationalTests
- test_tool_gateway.py
- AnswerDraft
- identity.py
- _make_case
- IngestionService
- EvidenceRecord
- IdentityError
- test_sample_documents.py
- ToolResult
- backend_boot/_baseline.py
- test_authorization.py
- read
- reset
- LocalRagExecutor
- AuthorizationDecision
- answer_baseline/test_contract_integration.py
- BoundedOrchestrator
- answer_baseline/test_e2e_operational.py
- read_frontend
- eval_001_runner.py
- DocumentResource
- cache_memory/test_security_adversarial.py
- App.test.tsx
- cache_memory/test_contract_integration.py
- orchestration_langgraph/test_contract_integration.py
- AuthorizationDecision
- test_customer_api_e2e.py
- test_chat_stream.py
- ingestion/_baseline.py
- run_local_guardrail_pipeline
- ingestion/test_behavior_component.py
- manifest.json
- main.py
- orchestration_langgraph/test_behavior_component.py
- KnowledgeOperationalTests
- ConversationMessage
- AuthorizationOperationalTests
- quarantine
- test_knowledge_security.py
- ndcg_at_k
- tree
- ChatService
- test_cache_memory.py
- InfrastructureSecurityTests
- CacheScope
- BackendBootstrapContractTests
- read
- build_secure_context
- rag_v4_citation/test_contract_integration.py
- app/rag/__init__.py
- staged
- app/evidence/__init__.py
- InMemoryScopedCache
- test_answer_baseline.py
- AuditOperationalTests
- vercel.json
- db/runtime.py
- ChunkMetadata
- AuditContractTests
- AuditSecurityTests
- rag_v4_citation/test_security_adversarial.py
- App
- test_ingestion_security.py
- asyncio
- package.json
- clean_state
- BehaviorComponentTests
- _dashboard_metrics
- pytest
- dashboard_api/test_e2e_operational.py
- test_customer_frontend_static.py
- test_answer_citation_schema.py
- hashlib
- _RequestModel
- json
- UsersView

## God Nodes (most connected - your core abstractions)
1. `auth()` - 143 edges
2. `request()` - 141 edges
3. `IngestionService` - 119 edges
4. `DataClassification` - 98 edges
5. `AuthenticatedPrincipal` - 95 edges
6. `CacheScope` - 85 edges
7. `new_service()` - 85 edges
8. `_active_document()` - 78 edges
9. `ModelGateway` - 68 edges
10. `ChunkMetadata` - 67 edges

## Surprising Connections (you probably didn't know these)
- `authorize()` --calls--> `AuthorizationDecision`  [INFERRED]
  tests/evaluation/eval_001_runner.py → backend/app/evidence/verifier.py
- `authorize()` --calls--> `AuthorizationDecision`  [INFERRED]
  tests/integration/test_answer_citation_schema.py → backend/app/evidence/verifier.py
- `pause_first_run()` --calls--> `_tenant_uuid()`  [EXTRACTED]
  tests/qa/chat_api/test_e2e_operational.py → backend/app/api/admin.py
- `test_contract_maintenance_is_mode_not_a_job_state()` --uses--> `JobState`  [INFERRED]
  tests/qa/chat_api/test_contract_integration.py → backend/app/core/chat.py
- `test_contract_pause_resume_rejects_a_stale_policy_scope()` --uses--> `JobState`  [INFERRED]
  tests/qa/chat_api/test_contract_integration.py → backend/app/core/chat.py

## Import Cycles
- 2-file cycle: `backend/app/api/admin.py -> backend/app/api/chat.py -> backend/app/api/admin.py`
- 2-file cycle: `backend/app/api/admin.py -> backend/app/api/identity.py -> backend/app/api/admin.py`
- 2-file cycle: `backend/app/api/chat.py -> backend/app/api/identity.py -> backend/app/api/chat.py`
- 3-file cycle: `backend/app/api/admin.py -> backend/app/api/chat.py -> backend/app/api/identity.py -> backend/app/api/admin.py`
- 3-file cycle: `backend/app/api/admin.py -> backend/app/api/identity.py -> backend/app/api/chat.py -> backend/app/api/admin.py`

## Communities (202 total, 70 thin omitted)

### Community 0 - "audit.py"
Cohesion: 0.08
Nodes (22): identity_error_handler(), append_audit_event(), AuditEvent, AuditSink, AuditSinkUnavailable, InMemoryAuditSink, redact_metadata(), _safe_code() (+14 more)

### Community 1 - "compose"
Cohesion: 0.07
Nodes (11): compose(), compose_config_result(), database(), handoff(), read(), tasks(), testing(), DisposablePostgresBehaviorTests (+3 more)

### Community 2 - "read"
Cohesion: 0.05
Nodes (10): compose_config_result(), migration_files(), migration_text(), read(), task(), tasks(), DatabaseBaselineBehaviorTests, DatabaseBaselineContractTests (+2 more)

### Community 3 - "read"
Cohesion: 0.08
Nodes (7): compose_config(), read(), task(), tasks(), InfrastructureBehaviorTests, InfrastructureContractTests, InfrastructureOperationalTests

### Community 5 - "section"
Cohesion: 0.08
Nodes (7): json_blocks(), require_all(), section(), BehaviorComponentTests, ContractIntegrationTests, E2EOperationalTests, SecurityAdversarialTests

### Community 6 - "read"
Cohesion: 0.06
Nodes (7): dashboard(), read(), task(), MonitoringBehaviorTests, MonitoringContractTests, MonitoringOperationalTests, MonitoringSecurityTests

### Community 7 - "ModelPolicy"
Cohesion: 0.14
Nodes (25): ModelPolicy, ModelTask, test_mapping_loads_versioned_policy_without_credentials(), test_policy_rejects_credential_fields(), test_route_task_mismatch_is_rejected_by_policy(), mapping(), policy(), route() (+17 more)

### Community 8 - "read"
Cohesion: 0.09
Nodes (4): read(), GraphifyBehaviorTests, GraphifyContractTests, GraphifySecurityTests

### Community 9 - "otel-collector-config.yaml"
Cohesion: 0.06
Nodes (32): action, key, actions, send_batch_size, timeout, exporters, prometheus, endpoint (+24 more)

### Community 10 - "prometheus"
Cohesion: 0.06
Nodes (30): command, image, ports, read_only, security_opt, volumes, depends_on, image (+22 more)

### Community 11 - "env.py"
Cohesion: 0.09
Nodes (3): _database_url(), run_migrations_offline(), run_migrations_online()

### Community 12 - "InMemoryScopedCache"
Cohesion: 0.07
Nodes (9): _CacheEntry, _component(), _digest(), _identifier(), InvalidationReason, ScopedCacheAdapter, ScopedCacheKey, FakeProvider (+1 more)

### Community 13 - "DataClassification"
Cohesion: 0.24
Nodes (18): ModelEgressDenied, DataClassification, EgressMode, provider(), test_external_internal_requires_dpa(), test_external_internal_requires_residency(), test_external_provider_requires_retention_policy(), test_external_unapproved_provider_is_denied() (+10 more)

### Community 14 - "QueryJob"
Cohesion: 0.12
Nodes (6): StaleScopeError, InMemoryChatRepository, JobCheckpoint, QueryJob, QueryJobRepository, _jsonb()

### Community 15 - "knowledge/models.py"
Cohesion: 0.12
Nodes (19): DOCXLocator, _ImmutableModel, PDFLocator, SourceSpan, XLSXLocator, Citation, _AnswerModel, _pipeline() (+11 more)

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

### Community 20 - "identity.py"
Cohesion: 0.06
Nodes (14): rate_limited(), DepartmentRecord, IdentityRecord, normalize_roles(), Role, SessionRecord, AuthenticationService, IdentityErrorPassthrough (+6 more)

### Community 21 - "evaluator"
Cohesion: 0.30
Nodes (5): InMemoryPolicyStore, AuthorizationSecurityAdversarialTests, document(), evaluator(), principal()

### Community 22 - "core/chat.py"
Cohesion: 0.08
Nodes (11): AnonymousSession, CheckpointRepository, _citation_expired(), ConversationRepository, ConversationSummary, ConversationView, DurableChatRepository, NoopQueryExecutor (+3 more)

### Community 23 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+10 more)

### Community 25 - "ModelProviderError"
Cohesion: 0.14
Nodes (6): ModelProviderError, RankedDocument, FakeReranker, test_ranked_document_preserves_identifier_and_score(), ScriptedReranker, test_reranker_happy_path_completes_once()

### Community 26 - "api/chat.py"
Cohesion: 0.17
Nodes (21): _anonymous_token(), _body(), _context(), create_conversation(), download_citation(), FeedbackRequest, get_conversation(), get_query_completion() (+13 more)

### Community 27 - "_make_retriever"
Cohesion: 0.08
Nodes (33): AccessGrant, HybridRetrievalConfig, reciprocal_rank_fusion(), _make_retriever(), test_hybrid_retrieval_composes_bm25_rrf_and_local_reranker(), test_rrf_uses_each_branch_rank_and_deduplicates_within_a_branch(), test_bm25_length_normalization_prefers_shorter_equal_match(), test_bm25_repeated_query_term_has_frequency_weight() (+25 more)

### Community 28 - "AuthorizationEvaluator"
Cohesion: 0.07
Nodes (18): AnonymousPrincipal, AuthorizationDenied, AuthorizationEvaluator, deny(), Classification, ConversationResource, Decision, Effect (+10 more)

### Community 29 - "chat_api/test_contract_integration.py"
Cohesion: 0.11
Nodes (19): job_payload(), anonymous_conversation(), authenticated_conversation(), Clock, Executor, Maintenance, make_service(), principal() (+11 more)

### Community 30 - "DataClassification"
Cohesion: 0.16
Nodes (34): ModelGateway, FakeEmbedding, policy(), provider(), route(), test_approved_local_fallback_can_handle_internal_data(), test_approved_local_provider_can_process_internal_data(), test_denial_error_does_not_echo_model_input() (+26 more)

### Community 31 - "chat_api/test_behavior_component.py"
Cohesion: 0.14
Nodes (19): AnswerState, JobState, anonymous_conversation(), authenticated_conversation(), Clock, Executor, Maintenance, make_service() (+11 more)

### Community 32 - "rag/runtime.py"
Cohesion: 0.08
Nodes (44): Action, _cosine(), DenseEvidence, DenseRetrievalResult, DenseRetriever, DeterministicEmbeddingAdapter, InMemoryDenseVectorIndex, _uuid() (+36 more)

### Community 33 - "GraphifyOperationalTests"
Cohesion: 0.11
Nodes (5): DatabaseMigrationSmokeTests, graph(), graphify_bin(), run_graphify(), GraphifyOperationalTests

### Community 34 - "key"
Cohesion: 0.09
Nodes (46): ScanVerdict, key(), prepare_review_two(), publish(), test_manager_activates_provisioned_account(), test_manager_completes_two_review_publication(), test_manager_provisions_inactive_employee(), test_manager_uploads_into_quarantine() (+38 more)

### Community 35 - "chat_api/test_security_adversarial.py"
Cohesion: 0.15
Nodes (20): QueryCompletion, anonymous_conversation(), authenticated_conversation(), Clock, Executor, Maintenance, make_service(), principal() (+12 more)

### Community 36 - "steps"
Cohesion: 0.15
Nodes (12): jobs, validate, name, on, pull_request, workflow_dispatch, run, uses (+4 more)

### Community 37 - "models/policy.py"
Cohesion: 0.09
Nodes (19): EmbeddingAdapter, EmbeddingRequest, EmbeddingResult, RerankerAdapter, RerankerRequest, RerankerResult, route(), ModelRoute (+11 more)

### Community 40 - "rules"
Cohesion: 0.17
Nodes (11): runbook, summary, groups, name, rules, severity, alert, annotations (+3 more)

### Community 41 - "lifecycle.py"
Cohesion: 0.09
Nodes (14): _chunk_state(), DerivedIndex, DerivedIndexFailure, DerivedIndexRecord, IdempotencyConflict, IndexPublicationStatus, IngestionError, InMemoryDerivedIndex (+6 more)

### Community 42 - "BackendBootstrapBehaviorTests"
Cohesion: 0.19
Nodes (4): calls(), function(), literal(), BackendBootstrapBehaviorTests

### Community 43 - "ToolResult"
Cohesion: 0.10
Nodes (14): AuthorizedScope, GetDocumentMetadataArguments, PrincipalResolver, ReadAuthorizedChunkArguments, _safe_tool_result(), ScopeResolver, SearchDocumentsArguments, ToolBackend (+6 more)

### Community 44 - "Icon"
Cohesion: 0.13
Nodes (23): getAuditEvents(), getFeedback(), setAccessToken(), signIn(), submitAccessRequest(), AdminGuardView(), AuditView(), load() (+15 more)

### Community 45 - "route"
Cohesion: 0.18
Nodes (10): global, resolve_timeout, receivers, name, route, group_by, group_interval, group_wait (+2 more)

### Community 46 - "feedback/service.py"
Cohesion: 0.16
Nodes (8): FeedbackRecord, FeedbackRepository, FeedbackReview, FeedbackService, InMemoryFeedbackRepository, test_feedback_is_private_and_idempotent_per_actor(), test_feedback_replay_is_idempotent_but_tenant_bound(), test_feedback_review_projection_has_no_actor_comment_or_body()

### Community 47 - "test_knowledge_database.py"
Cohesion: 0.26
Nodes (11): migration_text(), test_existing_db_contract_has_active_index_guard(), test_existing_db_contract_has_chunks_table(), test_existing_db_contract_has_composite_parent_fk(), test_existing_db_contract_has_document_versions_table(), test_existing_db_contract_has_documents_table(), test_existing_db_contract_has_immutable_version_uniqueness(), test_existing_db_contract_has_private_source_constraint() (+3 more)

### Community 48 - "chat_api/test_e2e_operational.py"
Cohesion: 0.23
Nodes (15): anonymous_conversation(), HttpExecutor, request(), sign_in(), test_http_anonymous_lifecycle_and_session_isolation(), test_http_authenticated_history_and_job_are_owner_only(), test_http_citation_preview_and_download_reauthorize_after_revocation(), test_http_deadline_failure_is_safe_and_has_no_answer() (+7 more)

### Community 49 - "expand_parent_context"
Cohesion: 0.18
Nodes (26): expand_parent_context(), child(), parent(), test_callback_failure_fails_closed_for_parent_only(), test_cross_tenant_parent_is_never_authorized_or_returned(), test_denied_parent_does_not_change_child_result(), test_duplicate_children_and_parents_are_deduplicated_with_all_provenance(), test_expands_authorized_parent_and_preserves_child_citation() (+18 more)

### Community 50 - "App.tsx"
Cohesion: 0.10
Nodes (23): ApprovalRecord, ConversationSummary, getDashboard(), AnswerDetails(), AnswerDetailsBody(), AnswerDetailsProps, AuthMode, canAdmin() (+15 more)

### Community 51 - "datasources"
Cohesion: 0.22
Nodes (8): apiVersion, datasources, access, editable, isDefault, name, type, url

### Community 52 - "monitoring/prometheus.yml"
Cohesion: 0.22
Nodes (8): global, evaluation_interval, scrape_interval, rule_files, scrape_configs, job_name, static_configs, targets

### Community 53 - "UUID"
Cohesion: 0.16
Nodes (11): ApprovalBlocked, ApprovalRecord, DocumentRecord, IngestionJob, InvalidInput, InvalidTransition, MaintenanceBlocked, MaintenanceWindow (+3 more)

### Community 54 - "client.ts"
Cohesion: 0.08
Nodes (31): AccessGrant, AccessRequestResponse, answerFromStream(), ApiError, AuditRecord, Conversation, ConversationMessage, Dashboard (+23 more)

### Community 56 - "AuthenticatedPrincipal"
Cohesion: 0.07
Nodes (11): AuthenticatedPrincipal, _citation(), SourceFetchResult, _BM25Record, _citation(), _FusedCandidate, HybridEvidence, HybridRetrievalResult (+3 more)

### Community 57 - "request"
Cohesion: 0.14
Nodes (26): deleteDocument(), getApprovals(), getCurrentIdentity(), getDocument(), getDocuments(), getDocumentVersions(), getIngestionJob(), mutationHeaders() (+18 more)

### Community 58 - "admin.py"
Cohesion: 0.18
Nodes (41): activate_user(), AdminApiState, approve_document_version(), _body(), _bump_policy_epoch(), create_department(), create_user(), delete_document() (+33 more)

### Community 59 - "upload"
Cohesion: 0.11
Nodes (36): add_user(), auth(), upload(), test_upload_returns_async_job_envelope(), clean_state(), test_acl_explicit_deny_overrides_employee_read_allow(), test_anonymous_cannot_upload(), test_chairman_cannot_approve() (+28 more)

### Community 61 - "tests/test_chat_api.py"
Cohesion: 0.20
Nodes (13): anonymous_conversation(), authenticated_headers(), request(), StubExecutor, test_anonymous_submit_status_completion_and_history_are_session_scoped(), test_authenticated_history_is_owner_only_and_revocation_denies_reuse(), test_citation_preview_and_download_are_separate_fresh_authorization_checks(), test_cross_origin_anonymous_cookie_is_usable_by_vercel_fetch() (+5 more)

### Community 62 - "request"
Cohesion: 0.09
Nodes (38): request(), test_account_response_does_not_return_password(), test_approval_schema_requires_explicit_stage(), test_existing_sign_in_contract_remains_under_auth_prefix(), test_job_status_contains_redacted_progress_only(), test_mutating_post_requires_idempotency_key(), test_problem_response_uses_safe_media_type_for_anonymous_admin_call(), test_upload_accepts_docx_mime_inference() (+30 more)

### Community 64 - "model/test_e2e_operational.py"
Cohesion: 0.14
Nodes (14): ModelUnavailable, run_graph_query(), graph_labels(), run_graph_query(), ScriptedEmbedding, task(), test_approved_fallback_runs_after_primary_failure(), test_embedding_happy_path_completes_once() (+6 more)

### Community 86 - "answer_baseline/test_behavior_component.py"
Cohesion: 0.17
Nodes (18): _authorization(), FakeModelGateway, _pipeline(), RaisingRetriever, RaisingVerifier, StaticRetriever, test_constructor_rejects_non_positive_top_k(), test_denied_citation_returns_insufficient_without_context_or_answer() (+10 more)

### Community 87 - "orchestration_langgraph/test_security_adversarial.py"
Cohesion: 0.13
Nodes (20): Answerer, Backend, call(), Clock, gateway(), Policy, principal(), request() (+12 more)

### Community 91 - "unittest"
Cohesion: 0.07
Nodes (20): Citation, _citation(), detect_prompt_injection(), GuardrailResult, _inspect_text(), inspect_untrusted_content(), _luhn_valid(), _normalize_text() (+12 more)

### Community 93 - "new_service"
Cohesion: 0.14
Nodes (29): active(), new_service(), test_publishing_new_version_supersedes_previous_version(), test_revoke_active_version_removes_retrieval(), test_second_review_and_publish_make_version_active(), test_soft_delete_isolates_all_versions(), test_audit_sink_receives_lifecycle_events_without_content(), test_failed_maintenance_can_be_recovered_after_cleanup() (+21 more)

### Community 94 - "gemini.py"
Cohesion: 0.13
Nodes (7): GeminiProviderError, GeminiStreamProvider, _http_error_code(), _text_parts(), _FakeGemini, test_gemini_adapter_uses_server_header_and_parses_sse_without_echoing_key(), close()

### Community 95 - "rag_v4_citation/test_e2e_operational.py"
Cohesion: 0.18
Nodes (16): _allow(), _answer(), _locator(), _Model, _principal(), _StaticRetriever, test_answer_workflow_consumes_parent_context_without_ranking_parent(), test_audience_and_expiry_survive_citation_delivery() (+8 more)

### Community 96 - "inherit_acl"
Cohesion: 0.11
Nodes (8): inherit_acl(), make_child(), make_document(), make_parent(), make_version(), KnowledgeBehaviorTests, KnowledgeContractIntegrationTests, KnowledgeSecurityAdversarialTests

### Community 98 - "test_tool_gateway.py"
Cohesion: 0.15
Nodes (22): _Backend, _call(), _Clock, _gateway(), _Policy, _principal(), _Resolvers, test_backend_exception_is_unavailable_without_raw_error() (+14 more)

### Community 99 - "AnswerDraft"
Cohesion: 0.26
Nodes (20): AnswerDraft, _Answerer, _Clock, _evidence(), _orchestrator(), _request(), test_answerer_error_is_returned_as_safe_error(), test_complex_route_splits_subqueries_and_preserves_bound() (+12 more)

### Community 100 - "identity.py"
Cohesion: 0.16
Nodes (11): create_access_request(), _bearer_token(), current_identity(), _record(), _record_identity_error(), _request_context(), sign_in(), sign_out() (+3 more)

### Community 102 - "_make_case"
Cohesion: 0.17
Nodes (16): _DenseAsHybrid, evaluation_snapshot(), _make_case(), authorize(), load_validated_records(), test_all_golden_cases_run_through_v1_v3(), test_allowed_answer_has_no_unauthorized_retrieval_marker(), test_answered_case_keeps_citation_version_and_tenant_binding() (+8 more)

### Community 103 - "IngestionService"
Cohesion: 0.12
Nodes (21): IngestionService, _active_document(), _principal(), _retriever(), test_dense_retrieval_returns_authorized_current_chunk_only(), test_explicit_deny_candidates_are_not_exposed(), test_forbidden_source_fetch_is_redacted_without_content_or_citation(), test_active_retrieval_to_evidence_verification_succeeds() (+13 more)

### Community 104 - "EvidenceRecord"
Cohesion: 0.27
Nodes (14): EvidenceRecord, SourceSpan, citation(), test_authorization_callback_error_fails_closed(), test_current_active_version_is_required_by_authorization_attestation(), test_negation_mismatch_is_conflicting_not_supported(), test_numeric_mismatch_is_conflicting_not_supported(), test_repeated_verification_is_deterministic() (+6 more)

### Community 105 - "IdentityError"
Cohesion: 0.24
Nodes (11): IdentityError, make_service(), test_expired_session_is_rejected(), test_invalid_password_is_safe_auth_error(), test_mfa_is_required_for_privileged_role(), test_principal_rejects_extra_client_claims(), test_revoked_session_is_rejected(), test_sign_in_normalizes_email_and_returns_server_principal() (+3 more)

### Community 106 - "test_sample_documents.py"
Cohesion: 0.21
Nodes (9): utc_z(), _authorize(), _build_corpus(), _Corpus, _GroundedSampleAnswer, _manifest(), test_no_answer_is_safe_when_sample_corpus_is_outside_tenant_scope(), test_sample_manifest_is_synthetic_hash_bound_and_private() (+1 more)

### Community 107 - "ToolResult"
Cohesion: 0.26
Nodes (17): OrchestrationRequest, Answerer, Clock, evidence(), request(), run(), test_answer_provider_failure_returns_error_without_exception_to_user(), test_deadline_timeout_is_a_visible_insufficient_outcome() (+9 more)

### Community 108 - "backend_boot/_baseline.py"
Cohesion: 0.22
Nodes (4): assignment(), pyproject(), route_calls(), route_path()

### Community 109 - "test_authorization.py"
Cohesion: 0.40
Nodes (15): document(), evaluator(), principal(), test_acl_can_assign_employee_and_explicit_deny_wins_for_chairman(), test_anonymous_is_public_only(), test_chairman_is_read_only(), test_conversation_body_is_owner_only(), test_conversation_requires_conversation_resource() (+7 more)

### Community 110 - "read"
Cohesion: 0.16
Nodes (5): backend_boot_task(), compile_sources_without_writes(), read(), task_packet(), BackendBootstrapOperationalTests

### Community 111 - "reset"
Cohesion: 0.05
Nodes (27): reset_state(), reset_state(), reset(), clean_state(), clean_state(), clean_state(), clean_state(), test_anonymous_is_denied_dashboard_and_feedback() (+19 more)

### Community 112 - "LocalRagExecutor"
Cohesion: 0.23
Nodes (6): LocalRagExecutor, test_local_runtime_answers_from_checked_in_public_sample_document(), test_local_runtime_applies_department_acl_to_internal_sample_document(), test_provider_incomplete_detailed_answer_abstains_before_token_delivery(), test_long_equipment_answer_contains_every_policy_condition(), test_public_and_internal_acl_are_enforced_by_local_rag()

### Community 113 - "AuthorizationDecision"
Cohesion: 0.13
Nodes (24): EvidenceVerifier, VerificationRequest, allow_active(), citation(), test_chat_001_owns_preview_download_reauthorization_recheck(), test_duplicate_evidence_ids_are_a_malformed_fail_closed_result(), authorize(), test_supported_result_round_trips_tenant_document_version_and_span() (+16 more)

### Community 114 - "answer_baseline/test_contract_integration.py"
Cohesion: 0.19
Nodes (15): _allow(), RecordingModel, RecordingRetriever, _setup(), test_citation_authorization_rejects_document_mismatch(), test_citation_authorization_rejects_non_active_status(), test_citation_authorization_rejects_non_current_version(), test_citation_authorization_rejects_revoked_source() (+7 more)

### Community 115 - "BoundedOrchestrator"
Cohesion: 0.09
Nodes (10): AnswerSynthesizer, BoundedOrchestrator, _evidence_from_result(), _GraphState, OrchestrationOutcome, OrchestrationStatus, QueryRoute, _route() (+2 more)

### Community 116 - "answer_baseline/test_e2e_operational.py"
Cohesion: 0.09
Nodes (30): Claim, GeneratedAnswer, _LocalAnswerModel, _allow(), FailingEmbedder, FailingReranker, FakeAnswerGateway, _setup() (+22 more)

### Community 117 - "read_frontend"
Cohesion: 0.09
Nodes (6): load_frontend_json(), read(), read_frontend(), FrontendBehaviorComponentTests, FrontendContractIntegrationTests, FrontendSecurityAdversarialTests

### Community 118 - "eval_001_runner.py"
Cohesion: 0.16
Nodes (14): _aggregate(), _AnswerModel, _Case, evaluate(), _mean(), _percentile(), _principal(), render_report() (+6 more)

### Community 119 - "DocumentResource"
Cohesion: 0.23
Nodes (5): DocumentResource, AuthorizationContractIntegrationTests, document(), evaluator(), principal()

### Community 120 - "cache_memory/test_security_adversarial.py"
Cohesion: 0.36
Nodes (12): make_key(), make_scope(), test_anonymous_revocation_isolated_to_one_session_and_fails_closed(), test_broad_scope_cannot_replay_after_a_narrow_document_change(), test_cache_key_excludes_queries_model_inputs_and_conversation_identifiers(), test_changed_document_version_cannot_repopulate_an_old_cache_entry(), test_cross_principal_cache_read_is_a_fail_closed_miss(), test_cross_scope_conversation_read_cannot_be_recovered_by_matching_id() (+4 more)

### Community 121 - "App.test.tsx"
Cohesion: 0.29
Nodes (4): adminPrincipal, conversationResponse(), json(), principal

### Community 122 - "cache_memory/test_contract_integration.py"
Cohesion: 0.20
Nodes (12): ConversationMemoryRepository, make_key(), make_scope(), test_contract_acl_change_can_target_one_principal_and_version(), test_contract_delete_event_invalidates_matching_scope_without_cross_tenant_reach(), test_contract_document_change_invalidates_broad_scope_and_selected_version(), test_contract_invalid_event_shapes_fail_closed_at_the_boundary(), test_contract_memory_read_requires_the_authoritative_current_scope() (+4 more)

### Community 123 - "orchestration_langgraph/test_contract_integration.py"
Cohesion: 0.18
Nodes (16): Backend, call(), Clock, gateway(), Policy, principal(), Resolvers, test_chunk_read_contract_accepts_only_chunk_id_shape() (+8 more)

### Community 124 - "AuthorizationDecision"
Cohesion: 0.10
Nodes (32): AuthorizationDecision, CitationRecord, _authorization_matches(), allow(), authorize(), revoked(), allow_active(), citation() (+24 more)

### Community 125 - "test_customer_api_e2e.py"
Cohesion: 0.15
Nodes (11): anonymous_conversation(), parse_sse(), request(), stream_public_question(), test_access_request_idempotency_returns_the_original_request(), test_access_request_is_recorded_without_granting_access(), test_access_request_requires_consent(), test_backend_outage_exposes_retryable_problem_contract() (+3 more)

### Community 126 - "test_chat_stream.py"
Cohesion: 0.41
Nodes (9): anonymous_conversation(), parse_sse(), request(), test_configured_provider_error_never_falls_back_to_local_answer(), test_local_fallback_streams_incrementally_and_cancels_before_completion(), test_local_sample_citation_preview_returns_safe_metadata_after_fresh_authz(), test_new_conversation_recovers_from_a_stale_anonymous_session(), test_no_key_stream_runs_local_rag_and_persists_answer() (+1 more)

### Community 127 - "ingestion/_baseline.py"
Cohesion: 0.13
Nodes (14): graph_labels(), read(), task(), test_task_and_handoff_keep_ingestion_provider_neutral(), test_audit_event_is_structured_without_source_checksum(), test_changed_checksum_cannot_enter_retry(), test_cleanup_failure_blocks_maintenance_recovery_then_recovery_succeeds(), test_end_to_end_clean_upload_becomes_retrievable_only_after_publish() (+6 more)

### Community 129 - "ingestion/test_behavior_component.py"
Cohesion: 0.17
Nodes (10): test_approval_expiry_blocks_processing(), test_empty_processing_input_is_rejected(), test_malware_scan_is_terminal(), test_new_active_version_supersedes_previous_version(), test_publish_activates_authoritative_version_and_chunks(), test_review_one_and_processing_require_parent_acl(), test_review_one_requires_clean_scan(), test_second_review_is_required_after_index_ack() (+2 more)

### Community 130 - "manifest.json"
Cohesion: 0.15
Nodes (12): corpus_id, documents, provenance, external_sources, kind, owner, source, queries (+4 more)

### Community 131 - "main.py"
Cohesion: 0.13
Nodes (3): get_settings(), Settings, healthz()

### Community 132 - "orchestration_langgraph/test_behavior_component.py"
Cohesion: 0.21
Nodes (16): ToolResult, Answerer, Clock, evidence(), request(), run(), test_compiles_a_state_graph_with_expected_nodes(), test_complex_loop_caps_subqueries_and_tool_calls_at_four() (+8 more)

### Community 133 - "KnowledgeOperationalTests"
Cohesion: 0.20
Nodes (3): read(), task(), KnowledgeOperationalTests

### Community 134 - "ConversationMessage"
Cohesion: 0.16
Nodes (17): ConversationMessage, test_contract_fake_repository_implements_provider_neutral_memory_boundary(), Clock, FakeInvalidationBus, FakeMemoryRepository, make_key(), make_scope(), test_anonymous_idle_retention_expires_at_boundary() (+9 more)

### Community 135 - "AuthorizationOperationalTests"
Cohesion: 0.32
Nodes (4): AuthorizationOperationalTests, document(), evaluator(), principal()

### Community 136 - "quarantine"
Cohesion: 0.17
Nodes (11): quarantine(), test_upload_starts_quarantined_and_not_retrievable(), RuntimeFailureOnRemove, service_with_index(), test_child_acl_cannot_be_broader_than_parent(), test_cleanup_backend_error_is_wrapped_without_secret_leakage(), test_cross_tenant_chunk_scope_is_rejected(), test_cross_tenant_document_lookup_is_denied() (+3 more)

### Community 137 - "test_knowledge_security.py"
Cohesion: 0.38
Nodes (12): make_child(), make_parent(), test_conflicting_child_acl_is_denied(), test_document_mismatch_is_denied(), test_matching_child_acl_is_preserved(), test_missing_child_acl_is_inherited(), test_qdrant_projection_does_not_claim_authority(), test_qdrant_projection_keeps_tenant_boundary() (+4 more)

### Community 138 - "ndcg_at_k"
Cohesion: 0.14
Nodes (17): _vectorize(), answer_correctness(), citation_accuracy(), evaluate_case(), mean_reciprocal_rank(), ndcg_at_k(), no_answer_accuracy(), recall_at_k() (+9 more)

### Community 140 - "ChatService"
Cohesion: 0.19
Nodes (5): ChatActor, ChatService, _error(), _fingerprint(), test_http_chat_reaches_local_rag_and_returns_verified_citation()

### Community 141 - "test_cache_memory.py"
Cohesion: 0.29
Nodes (11): Clock, response_key(), scope(), test_cache_delete_is_explicit(), test_cache_expires_and_rejects_unbounded_ttl_or_value(), test_cache_key_contains_security_scope_but_not_raw_query(), test_cache_requires_exact_current_scope_and_isolates_tenant_and_principal(), test_conversation_delete_removes_body_and_blocks_recreation_in_old_scope() (+3 more)

### Community 143 - "CacheScope"
Cohesion: 0.21
Nodes (3): CacheScope, ConversationMemory, FakeMemoryRepository

### Community 145 - "read"
Cohesion: 0.05
Nodes (7): read(), task(), tasks(), IdentityBehaviorTests, IdentityContractTests, IdentityOperationalTests, IdentitySecurityTests

### Community 146 - "build_secure_context"
Cohesion: 0.05
Nodes (17): AssembledContext, build_secure_context(), ContextLimitError, estimate_tokens(), PromptMessage, _render_evidence(), RetrievedEvidence, _safe_text() (+9 more)

### Community 147 - "rag_v4_citation/test_contract_integration.py"
Cohesion: 0.10
Nodes (26): _active(), ChildEvidence, _coerce_child(), _coerce_parent(), _construct(), _identity(), _index_parents(), ParentEvidence (+18 more)

### Community 148 - "app/rag/__init__.py"
Cohesion: 0.13
Nodes (11): _answer_citation(), AnswerCitation, AnswerModelGateway, AnswerResult, AnswerStatus, DirectAnswerPipeline, _expired(), PreparedAnswer (+3 more)

### Community 149 - "staged"
Cohesion: 0.24
Nodes (8): UploadManifest, Clock, make_chunks(), staged(), validated(), test_acknowledged_index_is_still_not_active(), test_clean_review_one_allows_processing(), test_processing_inherits_parent_acl()

### Community 151 - "app/evidence/__init__.py"
Cohesion: 0.17
Nodes (8): ClaimVerification, _is_negative(), _numeric_conflict(), _numeric_terms(), _relation(), _terms(), VerificationOutcome, VerificationResult

### Community 152 - "InMemoryScopedCache"
Cohesion: 0.21
Nodes (15): InMemoryScopedCache, test_cache_invalidation_hooks_remove_only_matching_scope(), test_document_change_invalidates_broad_corpus_cache_but_not_other_version(), Clock, make_key(), make_scope(), test_broad_acl_invalidation_removes_all_versions_in_one_tenant(), test_cache_expires_at_the_exact_ttl_deadline() (+7 more)

### Community 153 - "test_answer_baseline.py"
Cohesion: 0.36
Nodes (9): _authorization(), FakeModelGateway, _pipeline(), test_direct_answer_returns_insufficient_without_calling_model_when_no_match(), test_direct_answer_returns_partial_for_mixed_claims(), test_direct_answer_returns_supported_answer_and_authorized_citation(), test_guardrail_failure_fails_closed_before_model_call(), test_model_egress_failure_fails_closed_without_answer_or_citation() (+1 more)

### Community 154 - "AuditOperationalTests"
Cohesion: 0.18
Nodes (3): task(), tasks(), AuditOperationalTests

### Community 156 - "db/runtime.py"
Cohesion: 0.10
Nodes (19): ActorKind, ConversationRecord, MessageRecord, _answer_status(), _as_utc(), _department_uuid(), _membership_uuid(), normalize_database_url() (+11 more)

### Community 157 - "ChunkMetadata"
Cohesion: 0.11
Nodes (27): ChunkMetadata, DocumentMetadata, DocumentVersionMetadata, to_qdrant_payload(), test_active_chunk_requires_acl_metadata(), test_chunk_accepts_source_provenance(), test_chunk_rejects_reversed_pages(), test_chunk_rejects_self_parent() (+19 more)

### Community 160 - "rag_v4_citation/test_security_adversarial.py"
Cohesion: 0.38
Nodes (10): _child(), _parent(), test_cross_document_parent_is_not_expanded(), test_cross_tenant_parent_is_not_even_sent_to_authorizer(), test_cross_version_parent_is_not_expanded(), test_explicit_parent_deny_does_not_remove_authorized_child(), test_inactive_parent_status_is_not_expanded(), test_parent_policy_callback_outage_does_not_leak_text() (+2 more)

### Community 161 - "App"
Cohesion: 0.12
Nodes (29): clearAccessToken(), createConversation(), getConversation(), getConversations(), previewCitation(), signOut(), submitFeedback(), App() (+21 more)

### Community 162 - "test_ingestion_security.py"
Cohesion: 0.18
Nodes (10): test_child_acl_broadening_is_denied(), test_cross_tenant_version_lookup_is_denied(), test_derived_cleanup_failure_still_denies_retrieval(), test_derived_index_cannot_authorize_non_active_version(), test_legal_hold_blocks_permanent_delete(), test_rejected_version_cannot_be_retrieved(), test_revoked_version_cannot_be_retrieved_from_derived_state(), test_root_chunk_without_acl_fails_closed() (+2 more)

### Community 163 - "asyncio"
Cohesion: 0.27
Nodes (3): test_healthz_is_local_liveness_only(), test_identity_requires_bearer_credentials(), test_vercel_origin_can_use_cookie_authenticated_api()

### Community 164 - "package.json"
Cohesion: 0.38
Nodes (5): dependencies, @neon/config@^1.14.0, @neon/env@^2.1.3, @neon/config, @neon/env

### Community 170 - "_dashboard_metrics"
Cohesion: 0.29
Nodes (7): _counts(), _dashboard_metric(), _dashboard_metrics(), _unavailable_metric(), _utc_z(), test_measured_metric_keeps_value_provenance_and_measurement_period(), test_unavailable_metric_is_explicitly_empty_and_not_an_estimate()

### Community 172 - "pytest"
Cohesion: 0.14
Nodes (23): make_manifest(), test_rejected_scan_is_terminal_and_not_retrievable(), test_review_one_requires_clean_scan(), test_approval_expiry_blocks_publication(), test_doc_is_rejected(), test_internal_upload_requires_department(), test_manifest_checksum_mismatch_blocks_staging(), test_manifest_count_mismatch_blocks_staging() (+15 more)

### Community 175 - "dashboard_api/test_e2e_operational.py"
Cohesion: 0.23
Nodes (11): _feedback(), test_completed_chat_query_flows_into_the_usage_aggregate(), test_denied_operational_read_is_a_safe_problem_with_correlation(), test_document_upload_flows_into_dashboard_document_and_ingestion_counts(), test_feedback_filter_and_page_walk_are_operationally_bounded(), test_feedback_replay_is_operationally_idempotent_and_review_has_one_item(), test_feedback_review_records_operational_correlation_metadata(), test_operational_dashboard_explains_unavailable_metrics_instead_of_inventing_values() (+3 more)

### Community 186 - "test_customer_frontend_static.py"
Cohesion: 0.15
Nodes (6): test_chat_controls_have_keyboard_labels_and_live_status_semantics(), test_mobile_375x812_contract_keeps_chat_controls_within_the_viewport(), test_reload_contract_restores_conversation_and_requests_history(), test_responsive_layout_has_mobile_breakpoints_and_no_horizontal_body_overflow(), test_retryable_backend_error_has_a_user_recovery_action(), test_stop_control_is_available_only_during_a_live_stream()

### Community 197 - "test_answer_citation_schema.py"
Cohesion: 0.29
Nodes (6): _CapturingModel, _Model, test_direct_answer_context_includes_authorized_parent_runtime(), authorize(), test_real_hybrid_path_propagates_pdf_schema_end_to_end(), authorize()

### Community 198 - "hashlib"
Cohesion: 0.17
Nodes (8): _acl_digest(), _chunk_digest(), IndexManifest, IndexPublication, PublicationBlocked, ScanReport, StagedIndex, _publish()

### Community 200 - "_RequestModel"
Cohesion: 0.18
Nodes (10): AccessGrantRequest, AccessRequest, DepartmentRequest, EmployeeAccessRequest, PermanentDeleteRequest, _RequestModel, ReviewRequest, UploadRequest (+2 more)

### Community 201 - "json"
Cohesion: 0.15
Nodes (5): _serialized_size(), load_records(), test_dashboard_has_api_and_security_panels(), test_dashboard_is_valid_json(), test_rag002_task_registry_keeps_retrieval_validation_and_scope()

### Community 205 - "UsersView"
Cohesion: 0.35
Nodes (11): activateUser(), createDepartment(), createUser(), getDepartments(), getUsers(), updateUser(), UsersView(), load() (+3 more)

## Knowledge Gaps
- **1 isolated node(s):** `enterprise-agentic-rag-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 1016 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **70 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AuthenticatedPrincipal` connect `AuthenticatedPrincipal` to `AuthorizationOperationalTests`, `ChatService`, `knowledge/models.py`, `rag_v4_citation/test_contract_integration.py`, `identity.py`, `app/rag/__init__.py`, `core/chat.py`, `evaluator`, `api/chat.py`, `_make_retriever`, `AuthorizationEvaluator`, `chat_api/test_contract_integration.py`, `chat_api/test_behavior_component.py`, `rag/runtime.py`, `rag_v4_citation/test_security_adversarial.py`, `chat_api/test_security_adversarial.py`, `_dashboard_metrics`, `ToolResult`, `admin.py`, `orchestration_langgraph/test_security_adversarial.py`, `rag_v4_citation/test_e2e_operational.py`, `test_tool_gateway.py`, `identity.py`, `IngestionService`, `IdentityError`, `test_sample_documents.py`, `test_authorization.py`, `LocalRagExecutor`, `eval_001_runner.py`, `DocumentResource`, `orchestration_langgraph/test_contract_integration.py`, `test_customer_api_e2e.py`, `test_chat_stream.py`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Are the 46 inferred relationships involving `IngestionService` (e.g. with `reset_state()` and `test_active_retrieval_to_evidence_verification_succeeds()`) actually correct?**
  _`IngestionService` has 46 INFERRED edges - model-reasoned connections that need verification._
- **What connects `enterprise-agentic-rag-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `audit.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07764705882352942 - nodes in this community are weakly interconnected._
- **Why does `IngestionService` connect `IngestionService` to `rag/runtime.py`, `hashlib`, `_make_case`, `quarantine`, `lifecycle.py`, `test_sample_documents.py`, `pytest`, `reset`, `UUID`, `staged`, `eval_001_runner.py`, `_make_retriever`, `AuthorizationEvaluator`, `new_service`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Are the 47 inferred relationships involving `DataClassification` (e.g. with `ModelEgressDenied` and `ModelGateway`) actually correct?**
  _`DataClassification` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Should `compose` be split into smaller, more focused modules?**
  _Cohesion score 0.07017543859649122 - nodes in this community are weakly interconnected._