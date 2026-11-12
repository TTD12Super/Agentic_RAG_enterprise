# Graph Report - enterprise-agentic-rag-harness  (2026-11-12)

## Corpus Check
- 299 files · ~263,218 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 68 file(s) not represented in the graph (top: (none) 53, .toml 9, .example 2)

## Summary
- 4227 nodes · 13242 edges · 197 communities (135 shown, 62 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 1000 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d5ca193e`
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
- db/runtime.py
- ModelGateway
- postgres
- postgres
- PromptDefinition
- package.json
- answer_baseline/test_security_adversarial.py
- AuthorizationContractIntegrationTests
- orchestration/context.py
- compilerOptions
- InMemoryConversationMemory
- ModelGateway
- api/chat.py
- test_dense_retrieval.py
- AuthenticatedPrincipal
- chat_api/test_contract_integration.py
- chat_api/test_behavior_component.py
- make_manifest
- GraphifyOperationalTests
- key
- chat_api/test_security_adversarial.py
- steps
- hybrid.py
- ContractIntegrationTests
- SecurityAdversarialTests
- rules
- IdentityStore
- test_hybrid_retrieval.py
- ToolResult
- App.tsx
- route
- gemini.py
- test_knowledge_database.py
- chat_api/test_e2e_operational.py
- expand_parent_context
- rag_v4_citation/test_contract_integration.py
- datasources
- monitoring/prometheus.yml
- feedback/service.py
- client.ts
- PromptContractIntegrationTests
- SourceSpan
- request
- admin.py
- upload
- LocalRagExecutor
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
- hybrid.py
- test_authorization.py
- app/guardrails/__init__.py
- backend_boot/_baseline.py
- rag/runtime.py
- evaluator
- inherit_acl
- env.py
- test_tool_gateway.py
- AnswerDraft
- test_answer_baseline.py
- eval_001_runner.py
- IngestionService
- Claim
- ingestion/test_e2e_operational.py
- FrontendE2EOperationalTests
- ToolResult
- new_service
- EgressMode
- read
- reset
- quarantine
- AuthorizationDecision
- answer_baseline/test_contract_integration.py
- BoundedOrchestrator
- answer_baseline/test_e2e_operational.py
- read_frontend
- InfrastructureSecurityTests
- test_evidence.py
- cache_memory/test_security_adversarial.py
- App.test.tsx
- CacheScope
- orchestration_langgraph/test_contract_integration.py
- identity/models.py
- test_customer_api_e2e.py
- KnowledgeOperationalTests
- admin_api/test_contract_integration.py
- run_local_guardrail_pipeline
- DocumentVersionMetadata
- manifest.json
- InMemoryIdentityStore
- orchestration_langgraph/test_behavior_component.py
- _make_retriever
- ConversationMessage
- ingestion/test_security_adversarial.py
- AuthorizationDecision
- identity/store.py
- ndcg_at_k
- tree
- ChatService
- test_cache_memory.py
- DocumentsView
- UUID
- normalize_user_input
- read
- build_secure_context
- BackendBootstrapContractTests
- rag_v4_citation/test_e2e_operational.py
- ChunkMetadata
- observability/context.py
- app/evidence/__init__.py
- InMemoryScopedCache
- ingestion/test_behavior_component.py
- validate_output
- vercel.json
- asyncio
- ModelProviderError
- IdentityRecord
- UUID
- InMemoryAuditSink
- App
- test_identity.py
- test_chat_stream.py
- package.json
- test_knowledge_security.py
- BackendBootstrapBehaviorTests
- rag_hybrid/test_security_adversarial.py
- BehaviorComponentTests
- rag_v4_citation/test_security_adversarial.py
- Citation
- test_access_request_review.py
- .answer
- test_sample_documents.py
- ._now
- tests/test_dashboard_api.py
- test_customer_frontend_static.py
- make_manifest
- json

## God Nodes (most connected - your core abstractions)
1. `request()` - 151 edges
2. `auth()` - 151 edges
3. `DataClassification` - 135 edges
4. `IngestionService` - 125 edges
5. `AuthenticatedPrincipal` - 101 edges
6. `CacheScope` - 90 edges
7. `new_service()` - 85 edges
8. `_active_document()` - 80 edges
9. `ChunkMetadata` - 79 edges
10. `Claim` - 75 edges

## Surprising Connections (you probably didn't know these)
- `pause_first_run()` --calls--> `_tenant_uuid()`  [EXTRACTED]
  tests/qa/chat_api/test_e2e_operational.py → backend/app/api/admin.py
- `FakeModelGateway` --uses--> `DataClassification`  [INFERRED]
  tests/integration/test_answer_baseline.py → backend/app/models/policy.py
- `_AnswerModel` --uses--> `DataClassification`  [INFERRED]
  tests/evaluation/eval_001_runner.py → backend/app/models/policy.py
- `_publish()` --uses--> `IngestionService`  [INFERRED]
  tests/evaluation/eval_001_runner.py → backend/app/ingestion/lifecycle.py
- `_build_corpus()` --calls--> `IngestionService`  [INFERRED]
  tests/qa/rag/test_sample_documents.py → backend/app/ingestion/lifecycle.py

## Import Cycles
- 2-file cycle: `backend/app/api/admin.py -> backend/app/api/chat.py -> backend/app/api/admin.py`
- 2-file cycle: `backend/app/api/admin.py -> backend/app/api/identity.py -> backend/app/api/admin.py`
- 2-file cycle: `backend/app/api/chat.py -> backend/app/api/identity.py -> backend/app/api/chat.py`
- 3-file cycle: `backend/app/api/admin.py -> backend/app/api/chat.py -> backend/app/api/identity.py -> backend/app/api/admin.py`
- 3-file cycle: `backend/app/api/admin.py -> backend/app/api/identity.py -> backend/app/api/chat.py -> backend/app/api/admin.py`

## Communities (197 total, 62 thin omitted)

### Community 0 - "audit.py"
Cohesion: 0.14
Nodes (9): append_audit_event(), AuditEvent, AuditSink, AuditSinkUnavailable, redact_metadata(), _safe_code(), _safe_identifier(), _utc_z() (+1 more)

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
Cohesion: 0.08
Nodes (7): json_blocks(), require_all(), section(), BehaviorComponentTests, ContractIntegrationTests, E2EOperationalTests, SecurityAdversarialTests

### Community 6 - "read"
Cohesion: 0.06
Nodes (7): dashboard(), read(), task(), MonitoringBehaviorTests, MonitoringContractTests, MonitoringOperationalTests, MonitoringSecurityTests

### Community 7 - "InMemoryDerivedIndex"
Cohesion: 0.09
Nodes (17): ApprovalBlocked, _chunk_state(), DerivedIndex, DerivedIndexFailure, DerivedIndexRecord, IdempotencyConflict, IndexPublication, IndexPublicationStatus (+9 more)

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
Nodes (10): _CacheEntry, _component(), _digest(), _identifier(), InvalidationReason, ScopedCacheAdapter, ScopedCacheKey, _serialized_size() (+2 more)

### Community 14 - "db/runtime.py"
Cohesion: 0.05
Nodes (26): StaleScopeError, ActorKind, AnonymousSession, ConversationRepository, ConversationSummary, ConversationView, InMemoryChatRepository, JobCheckpoint (+18 more)

### Community 15 - "ModelGateway"
Cohesion: 0.18
Nodes (39): DataClassification, EgressMode, route(), ModelTask, FakeEmbedding, policy(), provider(), route() (+31 more)

### Community 16 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, networks (+12 more)

### Community 17 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, networks (+12 more)

### Community 18 - "PromptDefinition"
Cohesion: 0.13
Nodes (5): default_prompt_registry(), _freeze(), PromptDefinition, PromptRegistry, PromptRegistryTests

### Community 19 - "package.json"
Cohesion: 0.05
Nodes (52): dependencies, react@18.3.1, react-dom@18.3.1, vite@6.3.5, @vitejs/plugin-react@4.6.0, devDependencies, eslint@9.17.0, @eslint/js@9.17.0 (+44 more)

### Community 20 - "answer_baseline/test_security_adversarial.py"
Cohesion: 0.19
Nodes (16): _allow(), authorize(), FakeModelGateway, _pipeline(), test_cross_tenant_evidence_is_absent_from_dense_bm25_and_answer(), test_direct_prompt_injection_is_denied_before_retrieval_and_model(), test_duplicate_and_unknown_citation_ids_do_not_duplicate_or_leak_metadata(), test_indirect_prompt_injection_is_removed_before_model_context() (+8 more)

### Community 21 - "AuthorizationContractIntegrationTests"
Cohesion: 0.27
Nodes (4): AuthorizationContractIntegrationTests, document(), evaluator(), principal()

### Community 22 - "orchestration/context.py"
Cohesion: 0.13
Nodes (6): ContextLimitError, estimate_tokens(), PromptMessage, _render_evidence(), _safe_text(), _safe_value()

### Community 23 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+10 more)

### Community 25 - "ModelGateway"
Cohesion: 0.33
Nodes (4): ModelGateway, test_gateway_reranker_happy_path(), test_reranker_gateway_contract_passes_request_route_and_timeout(), test_reranker_happy_path_completes_once()

### Community 26 - "api/chat.py"
Cohesion: 0.17
Nodes (21): _anonymous_token(), _body(), _context(), create_conversation(), download_citation(), FeedbackRequest, get_conversation(), get_query_completion() (+13 more)

### Community 27 - "test_dense_retrieval.py"
Cohesion: 0.12
Nodes (16): AccessGrant, Action, Effect, HybridRetrievalConfig, test_explicit_deny_candidates_are_not_exposed(), test_forbidden_source_fetch_is_redacted_without_content_or_citation(), test_bm25_config_rejects_invalid_parameters(), test_evidence_carries_version_page_and_source_span_contract_fields() (+8 more)

### Community 28 - "AuthenticatedPrincipal"
Cohesion: 0.06
Nodes (24): AuthorizationDenied, AuthorizationEvaluator, deny(), Classification, ConversationResource, DocumentResource, InMemoryPolicyStore, _normalize_action() (+16 more)

### Community 29 - "chat_api/test_contract_integration.py"
Cohesion: 0.14
Nodes (18): job_payload(), JobState, anonymous_conversation(), authenticated_conversation(), Clock, Executor, Maintenance, make_service() (+10 more)

### Community 31 - "chat_api/test_behavior_component.py"
Cohesion: 0.15
Nodes (19): AnswerState, anonymous_conversation(), authenticated_conversation(), Clock, Executor, Maintenance, make_service(), principal() (+11 more)

### Community 32 - "make_manifest"
Cohesion: 0.18
Nodes (13): make_manifest(), test_pdf_is_accepted(), graph_labels(), read(), task(), test_failed_new_publication_preserves_previous_active_version(), test_job_contract_keeps_attempt_and_tenant_scope(), test_legacy_doc_and_xls_are_rejected() (+5 more)

### Community 33 - "GraphifyOperationalTests"
Cohesion: 0.12
Nodes (5): graph(), graphify_bin(), run_graphify(), GraphifyOperationalTests, run_graph_query()

### Community 34 - "key"
Cohesion: 0.10
Nodes (39): ScanVerdict, key(), prepare_review_two(), publish(), test_manager_activates_provisioned_account(), test_manager_completes_two_review_publication(), test_manager_provisions_inactive_employee(), test_permanent_delete_honors_legal_hold() (+31 more)

### Community 35 - "chat_api/test_security_adversarial.py"
Cohesion: 0.12
Nodes (22): QueryCompletion, RuntimeDatabaseUnavailable, IdentityError, anonymous_conversation(), authenticated_conversation(), Clock, Executor, Maintenance (+14 more)

### Community 36 - "steps"
Cohesion: 0.15
Nodes (12): jobs, validate, name, on, pull_request, workflow_dispatch, run, uses (+4 more)

### Community 37 - "hybrid.py"
Cohesion: 0.09
Nodes (23): EmbeddingAdapter, EmbeddingRequest, EmbeddingResult, RerankerAdapter, RerankerRequest, RerankerResult, ModelRoute, ProviderPolicy (+15 more)

### Community 40 - "rules"
Cohesion: 0.17
Nodes (11): runbook, summary, groups, name, rules, severity, alert, annotations (+3 more)

### Community 41 - "IdentityStore"
Cohesion: 0.12
Nodes (5): SessionRecord, AuthenticationService, now_utc(), IdentityStore, test_store_failure_fails_closed()

### Community 42 - "test_hybrid_retrieval.py"
Cohesion: 0.13
Nodes (17): _citation(), DenseRetriever, InMemoryDenseVectorIndex, SourceFetchResult, _VectorRecord, HybridRetriever, InMemoryBM25Index, _resource() (+9 more)

### Community 43 - "ToolResult"
Cohesion: 0.10
Nodes (14): AuthorizedScope, GetDocumentMetadataArguments, PrincipalResolver, ReadAuthorizedChunkArguments, _safe_tool_result(), ScopeResolver, SearchDocumentsArguments, ToolBackend (+6 more)

### Community 44 - "App.tsx"
Cohesion: 0.10
Nodes (24): getDashboard(), AnswerDetails(), AnswerDetailsBody(), AnswerDetailsProps, AuthMode, submitSignIn(), canAdmin(), ChatViewProps (+16 more)

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
Cohesion: 0.18
Nodes (26): expand_parent_context(), child(), parent(), test_callback_failure_fails_closed_for_parent_only(), test_cross_tenant_parent_is_never_authorized_or_returned(), test_denied_parent_does_not_change_child_result(), test_duplicate_children_and_parents_are_deduplicated_with_all_provenance(), test_expands_authorized_parent_and_preserves_child_citation() (+18 more)

### Community 50 - "rag_v4_citation/test_contract_integration.py"
Cohesion: 0.10
Nodes (25): _active(), ChildEvidence, _coerce_child(), _coerce_parent(), _construct(), _identity(), _index_parents(), ParentEvidence (+17 more)

### Community 51 - "datasources"
Cohesion: 0.22
Nodes (8): apiVersion, datasources, access, editable, isDefault, name, type, url

### Community 52 - "monitoring/prometheus.yml"
Cohesion: 0.22
Nodes (8): global, evaluation_interval, scrape_interval, rule_files, scrape_configs, job_name, static_configs, targets

### Community 53 - "feedback/service.py"
Cohesion: 0.15
Nodes (7): FeedbackRecord, FeedbackRepository, FeedbackReview, FeedbackService, InMemoryFeedbackRepository, test_feedback_replay_is_idempotent_but_tenant_bound(), test_feedback_review_projection_has_no_actor_comment_or_body()

### Community 54 - "client.ts"
Cohesion: 0.07
Nodes (35): AccessGrant, AccessRequestMetadata, AccessRequestResponse, answerFromStream(), ApiError, ApprovalRecord, AuditRecord, Conversation (+27 more)

### Community 56 - "SourceSpan"
Cohesion: 0.09
Nodes (27): DocumentMetadata, DOCXLocator, _ImmutableModel, PDFLocator, SourceSpan, XLSXLocator, _valid_locator(), Citation (+19 more)

### Community 57 - "request"
Cohesion: 0.11
Nodes (37): activateUser(), createDepartment(), createUser(), deleteDocument(), getAccessRequests(), getApprovals(), getConversations(), getCurrentIdentity() (+29 more)

### Community 58 - "admin.py"
Cohesion: 0.06
Nodes (80): _access_request_payload(), AccessGrantRequest, AccessRequest, AccessRequestReview, activate_user(), AdminApiState, approve_document_version(), _body() (+72 more)

### Community 59 - "upload"
Cohesion: 0.09
Nodes (30): Decision, add_user(), upload(), test_manager_uploads_into_quarantine(), test_publish_requires_acknowledged_index(), test_review_one_requires_clean_scan(), test_acl_explicit_deny_overrides_employee_read_allow(), test_anonymous_cannot_upload() (+22 more)

### Community 60 - "LocalRagExecutor"
Cohesion: 0.21
Nodes (7): AnonymousPrincipal, LocalRagExecutor, test_local_runtime_answers_from_checked_in_public_sample_document(), test_local_runtime_applies_department_acl_to_internal_sample_document(), test_provider_incomplete_detailed_answer_abstains_before_token_delivery(), test_long_equipment_answer_contains_every_policy_condition(), test_public_and_internal_acl_are_enforced_by_local_rag()

### Community 61 - "tests/test_chat_api.py"
Cohesion: 0.23
Nodes (13): anonymous_conversation(), authenticated_headers(), request(), StubExecutor, test_anonymous_submit_status_completion_and_history_are_session_scoped(), test_authenticated_history_is_owner_only_and_revocation_denies_reuse(), test_citation_preview_and_download_are_separate_fresh_authorization_checks(), test_cross_origin_anonymous_cookie_is_usable_by_vercel_fetch() (+5 more)

### Community 62 - "request"
Cohesion: 0.10
Nodes (51): auth(), request(), test_account_response_does_not_return_password(), test_approval_schema_requires_explicit_stage(), test_existing_sign_in_contract_remains_under_auth_prefix(), test_job_status_contains_redacted_progress_only(), test_mutating_post_requires_idempotency_key(), test_problem_response_uses_safe_media_type_for_anonymous_admin_call() (+43 more)

### Community 64 - "CitationArtifact"
Cohesion: 0.09
Nodes (5): _document_state(), CheckpointRepository, CitationArtifact, DurableChatRepository, QueryExecutor

### Community 86 - "answer_baseline/test_behavior_component.py"
Cohesion: 0.15
Nodes (19): _authorization(), authorize(), FakeModelGateway, _pipeline(), RaisingRetriever, RaisingVerifier, StaticRetriever, test_constructor_rejects_non_positive_top_k() (+11 more)

### Community 87 - "orchestration_langgraph/test_security_adversarial.py"
Cohesion: 0.13
Nodes (20): Answerer, Backend, call(), Clock, gateway(), Policy, principal(), request() (+12 more)

### Community 88 - "model/test_contract_integration.py"
Cohesion: 0.21
Nodes (13): ModelPolicy, test_mapping_loads_versioned_policy_without_credentials(), test_policy_rejects_credential_fields(), mapping(), test_access_token_field_is_rejected(), test_exact_api_key_field_is_rejected(), test_fallback_route_task_mismatch_is_rejected(), test_mapping_rejects_empty_model_revision() (+5 more)

### Community 89 - "hybrid.py"
Cohesion: 0.17
Nodes (7): _BM25Record, _citation(), _FusedCandidate, HybridEvidence, HybridRetrievalResult, _tokens(), test_retrieval_result_keeps_backward_compatible_empty_parent_context()

### Community 90 - "test_authorization.py"
Cohesion: 0.36
Nodes (15): document(), evaluator(), principal(), test_acl_can_assign_employee_and_explicit_deny_wins_for_chairman(), test_anonymous_is_public_only(), test_chairman_is_read_only(), test_conversation_body_is_owner_only(), test_conversation_requires_conversation_resource() (+7 more)

### Community 91 - "app/guardrails/__init__.py"
Cohesion: 0.15
Nodes (6): _luhn_valid(), redact_sensitive_data(), redact_card(), RedactionResult, ToolDecision, validate_tool_request()

### Community 93 - "backend_boot/_baseline.py"
Cohesion: 0.22
Nodes (4): assignment(), pyproject(), route_calls(), route_path()

### Community 94 - "rag/runtime.py"
Cohesion: 0.10
Nodes (16): _answer_citation(), AnswerCitation, AnswerStatus, _expired(), PreparedAnswer, _utc_z(), _cosine(), DenseEvidence (+8 more)

### Community 95 - "evaluator"
Cohesion: 0.41
Nodes (4): AuthorizationSecurityAdversarialTests, document(), evaluator(), principal()

### Community 96 - "inherit_acl"
Cohesion: 0.13
Nodes (16): inherit_acl(), to_qdrant_payload(), make_child(), make_parent(), test_acl_inheritance_populates_child_reference(), test_parent_child_contract_keeps_same_scope(), test_qdrant_projection_contains_index_state(), test_qdrant_projection_contains_scope_keys() (+8 more)

### Community 97 - "env.py"
Cohesion: 0.19
Nodes (4): _database_url(), run_migrations_offline(), run_migrations_online(), DatabaseMigrationSmokeTests

### Community 98 - "test_tool_gateway.py"
Cohesion: 0.15
Nodes (22): _Backend, _call(), _Clock, _gateway(), _Policy, _principal(), _Resolvers, test_backend_exception_is_unavailable_without_raw_error() (+14 more)

### Community 99 - "AnswerDraft"
Cohesion: 0.26
Nodes (20): AnswerDraft, _Answerer, _Clock, _evidence(), _orchestrator(), _request(), test_answerer_error_is_returned_as_safe_error(), test_complex_route_splits_subqueries_and_preserves_bound() (+12 more)

### Community 100 - "test_answer_baseline.py"
Cohesion: 0.36
Nodes (9): _authorization(), FakeModelGateway, _pipeline(), test_direct_answer_returns_insufficient_without_calling_model_when_no_match(), test_direct_answer_returns_partial_for_mixed_claims(), test_direct_answer_returns_supported_answer_and_authorized_citation(), test_guardrail_failure_fails_closed_before_model_call(), test_model_egress_failure_fails_closed_without_answer_or_citation() (+1 more)

### Community 102 - "eval_001_runner.py"
Cohesion: 0.10
Nodes (26): _aggregate(), _AnswerModel, _Case, _DenseAsHybrid, evaluate(), evaluation_snapshot(), _make_case(), authorize() (+18 more)

### Community 103 - "IngestionService"
Cohesion: 0.15
Nodes (18): IngestionService, _active_document(), _principal(), _retriever(), test_dense_retrieval_returns_authorized_current_chunk_only(), test_active_retrieval_to_evidence_verification_succeeds(), test_cross_tenant_retrieval_is_empty_and_cannot_be_verified(), test_policy_store_failure_denies_search_and_source_fetch() (+10 more)

### Community 104 - "Claim"
Cohesion: 0.27
Nodes (14): Claim, SourceSpan, citation(), test_authorization_callback_error_fails_closed(), test_current_active_version_is_required_by_authorization_attestation(), test_negation_mismatch_is_conflicting_not_supported(), test_numeric_mismatch_is_conflicting_not_supported(), test_repeated_verification_is_deterministic() (+6 more)

### Community 105 - "ingestion/test_e2e_operational.py"
Cohesion: 0.22
Nodes (7): test_audit_event_is_structured_without_source_checksum(), test_changed_checksum_cannot_enter_retry(), test_cleanup_failure_blocks_maintenance_recovery_then_recovery_succeeds(), test_end_to_end_clean_upload_becomes_retrievable_only_after_publish(), test_invalid_scan_is_terminal_and_not_retryable(), test_only_one_maintenance_window_can_run_per_tenant(), test_permanent_delete_requires_retention_and_removes_document()

### Community 107 - "ToolResult"
Cohesion: 0.25
Nodes (17): ToolResult, Answerer, Clock, evidence(), request(), run(), test_answer_provider_failure_returns_error_without_exception_to_user(), test_deadline_timeout_is_a_visible_insufficient_outcome() (+9 more)

### Community 108 - "new_service"
Cohesion: 0.14
Nodes (20): active(), staged(), test_acknowledged_index_is_still_not_active(), test_derived_cleanup_failure_still_denies_retrieval(), test_derived_index_cannot_authorize_non_active_version(), test_legal_hold_blocks_permanent_delete(), test_rejected_version_cannot_be_retrieved(), test_revoked_version_cannot_be_retrieved_from_derived_state() (+12 more)

### Community 109 - "EgressMode"
Cohesion: 0.10
Nodes (36): ModelEgressDenied, ModelUnavailable, graph_labels(), policy(), provider(), route(), run_graph_query(), ScriptedEmbedding (+28 more)

### Community 110 - "read"
Cohesion: 0.16
Nodes (5): backend_boot_task(), compile_sources_without_writes(), read(), task_packet(), BackendBootstrapOperationalTests

### Community 111 - "reset"
Cohesion: 0.05
Nodes (23): reset_state(), reset_state(), normalize_database_url(), reset(), clean_state(), clean_state(), clean_state(), clean_state() (+15 more)

### Community 112 - "quarantine"
Cohesion: 0.15
Nodes (24): new_service(), quarantine(), test_publishing_new_version_supersedes_previous_version(), test_rejected_scan_is_terminal_and_not_retrievable(), test_review_one_requires_clean_scan(), test_revoke_active_version_removes_retrieval(), test_second_review_and_publish_make_version_active(), test_soft_delete_isolates_all_versions() (+16 more)

### Community 113 - "AuthorizationDecision"
Cohesion: 0.13
Nodes (24): EvidenceRecord, EvidenceVerifier, VerificationRequest, allow_active(), citation(), test_chat_001_owns_preview_download_reauthorization_recheck(), test_duplicate_evidence_ids_are_a_malformed_fail_closed_result(), authorize() (+16 more)

### Community 114 - "answer_baseline/test_contract_integration.py"
Cohesion: 0.19
Nodes (15): _allow(), RecordingModel, RecordingRetriever, _setup(), test_citation_authorization_rejects_document_mismatch(), test_citation_authorization_rejects_non_active_status(), test_citation_authorization_rejects_non_current_version(), test_citation_authorization_rejects_revoked_source() (+7 more)

### Community 115 - "BoundedOrchestrator"
Cohesion: 0.08
Nodes (13): NoopQueryExecutor, AssembledContext, AnswerSynthesizer, BoundedOrchestrator, _evidence_from_result(), _GraphState, OrchestrationOutcome, OrchestrationRequest (+5 more)

### Community 116 - "answer_baseline/test_e2e_operational.py"
Cohesion: 0.15
Nodes (15): GeneratedAnswer, _LocalAnswerModel, FailingEmbedder, FailingReranker, FakeAnswerGateway, _setup(), test_operational_abstention_is_insufficient_evidence(), test_operational_conflicting_evidence_is_not_harmonized() (+7 more)

### Community 117 - "read_frontend"
Cohesion: 0.09
Nodes (6): load_frontend_json(), read(), read_frontend(), FrontendBehaviorComponentTests, FrontendContractIntegrationTests, FrontendSecurityAdversarialTests

### Community 119 - "test_evidence.py"
Cohesion: 0.24
Nodes (15): CitationRecord, _authorization_matches(), allow_active(), citation(), test_authorizer_must_attest_active_current_and_not_revoked(), test_citation_and_source_span_are_immutable(), test_conflicting_numeric_source_spans_are_disclosed(), test_denial_result_does_not_leak_source_text() (+7 more)

### Community 120 - "cache_memory/test_security_adversarial.py"
Cohesion: 0.36
Nodes (12): make_key(), make_scope(), test_anonymous_revocation_isolated_to_one_session_and_fails_closed(), test_broad_scope_cannot_replay_after_a_narrow_document_change(), test_cache_key_excludes_queries_model_inputs_and_conversation_identifiers(), test_changed_document_version_cannot_repopulate_an_old_cache_entry(), test_cross_principal_cache_read_is_a_fail_closed_miss(), test_cross_scope_conversation_read_cannot_be_recovered_by_matching_id() (+4 more)

### Community 121 - "App.test.tsx"
Cohesion: 0.20
Nodes (7): clearAccessToken(), signOut(), handleSignOut(), adminPrincipal, conversationResponse(), json(), principal

### Community 122 - "CacheScope"
Cohesion: 0.11
Nodes (15): CacheScope, ConversationMemory, ConversationMemoryRepository, FakeMemoryRepository, make_key(), make_scope(), test_contract_delete_event_invalidates_matching_scope_without_cross_tenant_reach(), test_contract_document_change_invalidates_broad_scope_and_selected_version() (+7 more)

### Community 123 - "orchestration_langgraph/test_contract_integration.py"
Cohesion: 0.18
Nodes (16): Backend, call(), Clock, gateway(), Policy, principal(), Resolvers, test_chunk_read_contract_accepts_only_chunk_id_shape() (+8 more)

### Community 124 - "identity/models.py"
Cohesion: 0.14
Nodes (4): rate_limited(), Role, utc_z(), IdentityErrorPassthrough

### Community 125 - "test_customer_api_e2e.py"
Cohesion: 0.15
Nodes (11): anonymous_conversation(), parse_sse(), request(), stream_public_question(), test_access_request_idempotency_returns_the_original_request(), test_access_request_is_recorded_without_granting_access(), test_access_request_requires_consent(), test_backend_outage_exposes_retryable_problem_contract() (+3 more)

### Community 126 - "KnowledgeOperationalTests"
Cohesion: 0.20
Nodes (3): read(), task(), KnowledgeOperationalTests

### Community 127 - "admin_api/test_contract_integration.py"
Cohesion: 0.16
Nodes (12): clean_state(), test_account_response_does_not_return_password(), test_approval_schema_requires_explicit_stage(), test_job_status_contains_redacted_progress_only(), test_mutating_post_requires_idempotency_key(), test_upload_accepts_docx_mime_inference(), test_upload_accepts_xlsx_mime_inference(), test_upload_idempotency_rejects_a_different_fingerprint() (+4 more)

### Community 129 - "DocumentVersionMetadata"
Cohesion: 0.09
Nodes (8): DocumentVersionMetadata, test_document_version_identity_is_stable(), test_document_version_requires_private_source(), test_hashes_are_normalized(), test_version_contract_has_immutable_version_number(), test_version_contract_supports_publication_states(), make_document(), KnowledgeBehaviorTests

### Community 130 - "manifest.json"
Cohesion: 0.15
Nodes (12): corpus_id, documents, provenance, external_sources, kind, owner, source, queries (+4 more)

### Community 132 - "orchestration_langgraph/test_behavior_component.py"
Cohesion: 0.25
Nodes (15): Answerer, Clock, evidence(), request(), run(), test_compiles_a_state_graph_with_expected_nodes(), test_complex_loop_caps_subqueries_and_tool_calls_at_four(), test_complex_query_splits_into_distinct_subqueries() (+7 more)

### Community 133 - "_make_retriever"
Cohesion: 0.10
Nodes (27): reciprocal_rank_fusion(), _make_retriever(), test_hybrid_retrieval_composes_bm25_rrf_and_local_reranker(), test_rrf_uses_each_branch_rank_and_deduplicates_within_a_branch(), test_bm25_length_normalization_prefers_shorter_equal_match(), test_bm25_repeated_query_term_has_frequency_weight(), test_bm25_tokenization_casefolds_and_splits_punctuation(), test_hybrid_composition_preserves_rrf_and_rerank_scores() (+19 more)

### Community 134 - "ConversationMessage"
Cohesion: 0.17
Nodes (16): ConversationMessage, Clock, FakeInvalidationBus, FakeMemoryRepository, make_key(), make_scope(), test_anonymous_idle_retention_expires_at_boundary(), test_anonymous_max_age_caps_an_active_session() (+8 more)

### Community 135 - "ingestion/test_security_adversarial.py"
Cohesion: 0.16
Nodes (10): RuntimeFailureOnRemove, service_with_index(), test_cleanup_backend_error_is_wrapped_without_secret_leakage(), test_cross_tenant_document_lookup_is_denied(), test_cross_tenant_job_lookup_is_denied(), test_cross_tenant_version_lookup_is_denied(), test_derived_staging_state_cannot_authorize_retrieval(), test_legal_hold_blocks_permanent_delete() (+2 more)

### Community 136 - "AuthorizationDecision"
Cohesion: 0.11
Nodes (23): AuthorizationDecision, DirectAnswerPipeline, revoked(), current_v2(), authorize(), _CapturingModel, _Model, test_direct_answer_context_includes_authorized_parent_runtime() (+15 more)

### Community 137 - "identity/store.py"
Cohesion: 0.26
Nodes (7): _department_uuid(), _membership_uuid(), stable_uuid(), user_uuid(), normalize_roles(), hash_secret(), verify_secret()

### Community 138 - "ndcg_at_k"
Cohesion: 0.12
Nodes (20): answer_correctness(), citation_accuracy(), evaluate_case(), load_records(), load_validated_records(), mean_reciprocal_rank(), ndcg_at_k(), no_answer_accuracy() (+12 more)

### Community 140 - "ChatService"
Cohesion: 0.17
Nodes (7): ChatActor, ChatService, _citation_expired(), ConversationRecord, _error(), _fingerprint(), test_http_chat_reaches_local_rag_and_returns_verified_citation()

### Community 141 - "test_cache_memory.py"
Cohesion: 0.29
Nodes (11): Clock, response_key(), scope(), test_cache_delete_is_explicit(), test_cache_expires_and_rejects_unbounded_ttl_or_value(), test_cache_key_contains_security_scope_but_not_raw_query(), test_cache_requires_exact_current_scope_and_isolates_tenant_and_principal(), test_conversation_delete_removes_body_and_blocks_recreation_in_old_scope() (+3 more)

### Community 142 - "DocumentsView"
Cohesion: 0.31
Nodes (10): getAuditEvents(), getDocuments(), getFeedback(), uploadMetadataDocument(), AuditView(), load(), DataViewEmpty(), DocumentsView() (+2 more)

### Community 144 - "normalize_user_input"
Cohesion: 0.17
Nodes (3): normalize_user_input(), GuardrailBehaviorTests, GuardrailSecurityAdversarialTests

### Community 145 - "read"
Cohesion: 0.05
Nodes (7): read(), task(), tasks(), IdentityBehaviorTests, IdentityContractTests, IdentityOperationalTests, IdentitySecurityTests

### Community 146 - "build_secure_context"
Cohesion: 0.09
Nodes (9): build_secure_context(), RetrievedEvidence, SecureContextBuilder, SecureContextBuilderTests, test_verifier_requires_a_server_supplied_authorization_callback(), PromptBehaviorComponentTests, PromptOperationalTests, PromptSecurityAdversarialTests (+1 more)

### Community 148 - "rag_v4_citation/test_e2e_operational.py"
Cohesion: 0.19
Nodes (15): _allow(), _answer(), _locator(), _Model, _principal(), _StaticRetriever, test_answer_workflow_consumes_parent_context_without_ranking_parent(), test_audience_and_expiry_survive_citation_delivery() (+7 more)

### Community 149 - "ChunkMetadata"
Cohesion: 0.21
Nodes (11): _acl_digest(), _chunk_digest(), IndexManifest, StagedIndex, ChunkMetadata, test_active_chunk_requires_acl_metadata(), test_chunk_accepts_source_provenance(), test_chunk_rejects_reversed_pages() (+3 more)

### Community 150 - "observability/context.py"
Cohesion: 0.19
Nodes (5): identity_error_handler(), _header(), _new_traceparent(), _valid_traceparent(), test_correlation_context_preserves_valid_headers_and_creates_child()

### Community 151 - "app/evidence/__init__.py"
Cohesion: 0.21
Nodes (8): ClaimVerification, _is_negative(), _numeric_conflict(), _numeric_terms(), _relation(), _terms(), VerificationOutcome, VerificationResult

### Community 152 - "InMemoryScopedCache"
Cohesion: 0.20
Nodes (16): InMemoryScopedCache, test_cache_invalidation_hooks_remove_only_matching_scope(), test_document_change_invalidates_broad_corpus_cache_but_not_other_version(), Clock, make_key(), make_scope(), test_broad_acl_invalidation_removes_all_versions_in_one_tenant(), test_cache_expires_at_the_exact_ttl_deadline() (+8 more)

### Community 153 - "ingestion/test_behavior_component.py"
Cohesion: 0.22
Nodes (6): test_empty_processing_input_is_rejected(), test_malware_scan_is_terminal(), test_new_active_version_supersedes_previous_version(), test_publish_activates_authoritative_version_and_chunks(), test_review_one_requires_clean_scan(), test_staging_is_not_retrievable_before_ack_and_publish()

### Community 154 - "validate_output"
Cohesion: 0.26
Nodes (8): _citation(), detect_prompt_injection(), GuardrailResult, _inspect_text(), _normalize_text(), _sensitive_terms(), _terms(), validate_output()

### Community 156 - "asyncio"
Cohesion: 0.18
Nodes (5): test_healthz_is_local_liveness_only(), test_identity_requires_bearer_credentials(), test_vercel_origin_can_use_cookie_authenticated_api(), request(), test_contract_feedback_response_omits_comment_and_replays_safely()

### Community 157 - "ModelProviderError"
Cohesion: 0.13
Nodes (6): ModelProviderError, RankedDocument, FakeReranker, test_ranked_document_preserves_identifier_and_score(), ScriptedReranker, test_reranker_result_keeps_selected_route()

### Community 159 - "UUID"
Cohesion: 0.14
Nodes (10): ApprovalRecord, DocumentRecord, IngestionJob, InvalidInput, InvalidTransition, NotFound, ScanReport, _status() (+2 more)

### Community 160 - "InMemoryAuditSink"
Cohesion: 0.29
Nodes (8): InMemoryAuditSink, test_audit_sink_is_append_only_and_structured(), test_unavailable_sink_does_not_accept_an_event(), _add_identity(), _request(), test_sign_in_denial_emits_no_credentials_or_body(), test_sign_in_emits_correlated_success_event(), test_sign_in_fails_closed_when_audit_sink_is_unavailable()

### Community 161 - "App"
Cohesion: 0.09
Nodes (37): createConversation(), getConversation(), previewCitation(), submitFeedback(), AdminGuardView(), App(), closeAuth(), completeAuthentication() (+29 more)

### Community 162 - "test_identity.py"
Cohesion: 0.26
Nodes (10): make_service(), test_expired_session_is_rejected(), test_invalid_password_is_safe_auth_error(), test_mfa_is_required_for_privileged_role(), test_noncanonical_role_cannot_create_identity(), test_principal_rejects_extra_client_claims(), test_revoked_session_is_rejected(), test_sign_in_normalizes_email_and_returns_server_principal() (+2 more)

### Community 163 - "test_chat_stream.py"
Cohesion: 0.36
Nodes (9): anonymous_conversation(), parse_sse(), request(), test_configured_provider_error_never_falls_back_to_local_answer(), test_local_fallback_streams_incrementally_and_cancels_before_completion(), test_local_sample_citation_preview_returns_safe_metadata_after_fresh_authz(), test_new_conversation_recovers_from_a_stale_anonymous_session(), test_no_key_stream_runs_local_rag_and_persists_answer() (+1 more)

### Community 164 - "package.json"
Cohesion: 0.38
Nodes (5): dependencies, @neon/config@^1.14.0, @neon/env@^2.1.3, @neon/config, @neon/env

### Community 165 - "test_knowledge_security.py"
Cohesion: 0.38
Nodes (12): make_child(), make_parent(), test_conflicting_child_acl_is_denied(), test_document_mismatch_is_denied(), test_matching_child_acl_is_preserved(), test_missing_child_acl_is_inherited(), test_qdrant_projection_does_not_claim_authority(), test_qdrant_projection_keeps_tenant_boundary() (+4 more)

### Community 166 - "BackendBootstrapBehaviorTests"
Cohesion: 0.19
Nodes (4): calls(), function(), literal(), BackendBootstrapBehaviorTests

### Community 167 - "rag_hybrid/test_security_adversarial.py"
Cohesion: 0.21
Nodes (10): _catalog(), _FailingEmbeddingAdapter, _FailingRerankerAdapter, test_cross_tenant_candidates_are_absent_from_dense_and_bm25(), test_embedding_failure_fails_closed_without_bm25_fallback_leak(), test_policy_store_outage_fails_closed_without_candidate_metadata(), test_reranker_failure_returns_error_without_evidence(), test_staging_index_candidates_are_absent_from_dense_and_bm25() (+2 more)

### Community 169 - "rag_v4_citation/test_security_adversarial.py"
Cohesion: 0.33
Nodes (11): _child(), _parent(), _principal(), test_cross_document_parent_is_not_expanded(), test_cross_tenant_parent_is_not_even_sent_to_authorizer(), test_cross_version_parent_is_not_expanded(), test_explicit_parent_deny_does_not_remove_authorized_child(), test_inactive_parent_status_is_not_expanded() (+3 more)

### Community 171 - "test_access_request_review.py"
Cohesion: 0.21
Nodes (10): clean_state(), create_request(), test_anonymous_request_uses_server_configured_tenant(), test_approve_is_idempotent_and_does_not_grant_access(), test_http_only_session_cookie_restores_identity_after_reload(), test_manager_cannot_list_or_review_another_tenant_request(), test_manager_lists_same_tenant_pending_requests_as_safe_metadata_only(), test_only_managers_can_review_access_requests() (+2 more)

### Community 173 - "test_sample_documents.py"
Cohesion: 0.29
Nodes (6): _authorize(), _GroundedSampleAnswer, _manifest(), test_no_answer_is_safe_when_sample_corpus_is_outside_tenant_scope(), test_sample_manifest_is_synthetic_hash_bound_and_private(), test_sample_query_returns_evidence_and_typed_citation()

### Community 175 - "tests/test_dashboard_api.py"
Cohesion: 0.25
Nodes (6): clean_state(), test_anonymous_is_denied_dashboard_and_feedback(), test_feedback_review_is_private_bounded_and_replay_does_not_duplicate(), test_management_roles_can_read_empty_dashboard_and_feedback(), test_non_management_roles_are_denied_dashboard_and_feedback(), test_policy_outage_fails_closed_for_both_management_reads()

### Community 186 - "test_customer_frontend_static.py"
Cohesion: 0.15
Nodes (6): test_chat_controls_have_keyboard_labels_and_live_status_semantics(), test_mobile_375x812_contract_keeps_chat_controls_within_the_viewport(), test_reload_contract_restores_conversation_and_requests_history(), test_responsive_layout_has_mobile_breakpoints_and_no_horizontal_body_overflow(), test_retryable_backend_error_has_a_user_recovery_action(), test_stop_control_is_available_only_during_a_live_stream()

### Community 197 - "make_manifest"
Cohesion: 0.15
Nodes (24): UploadManifest, make_chunks(), validated(), test_clean_review_one_allows_processing(), test_processing_inherits_parent_acl(), test_approval_expiry_blocks_publication(), test_doc_is_rejected(), test_internal_upload_requires_department() (+16 more)

### Community 201 - "json"
Cohesion: 0.13
Nodes (3): dfs(), test_dashboard_has_api_and_security_panels(), test_dashboard_is_valid_json()

## Knowledge Gaps
- **1 isolated node(s):** `enterprise-agentic-rag-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 1042 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **62 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AuthenticatedPrincipal` connect `AuthenticatedPrincipal` to `AuthorizationDecision`, `ChatService`, `rag_v4_citation/test_e2e_operational.py`, `AuthorizationContractIntegrationTests`, `api/chat.py`, `test_dense_retrieval.py`, `chat_api/test_contract_integration.py`, `chat_api/test_behavior_component.py`, `test_identity.py`, `test_chat_stream.py`, `chat_api/test_security_adversarial.py`, `IdentityStore`, `test_hybrid_retrieval.py`, `ToolResult`, `.answer`, `test_sample_documents.py`, `rag_v4_citation/test_security_adversarial.py`, `rag_v4_citation/test_contract_integration.py`, `SourceSpan`, `admin.py`, `LocalRagExecutor`, `orchestration_langgraph/test_security_adversarial.py`, `hybrid.py`, `test_authorization.py`, `rag/runtime.py`, `evaluator`, `test_tool_gateway.py`, `eval_001_runner.py`, `IngestionService`, `orchestration_langgraph/test_contract_integration.py`, `identity/models.py`, `test_customer_api_e2e.py`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 86 inferred relationships involving `DataClassification` (e.g. with `DocumentRecord` and `UploadManifest`) actually correct?**
  _`DataClassification` has 86 INFERRED edges - model-reasoned connections that need verification._
- **What connects `enterprise-agentic-rag-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `audit.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14153846153846153 - nodes in this community are weakly interconnected._
- **Why does `DataClassification` connect `ModelGateway` to `_make_retriever`, `InMemoryDerivedIndex`, `AuthorizationDecision`, `answer_baseline/test_security_adversarial.py`, `rag_v4_citation/test_e2e_operational.py`, `ModelGateway`, `test_dense_retrieval.py`, `ModelProviderError`, `UUID`, `make_manifest`, `hybrid.py`, `rag_hybrid/test_security_adversarial.py`, `rag_v4_citation/test_security_adversarial.py`, `test_hybrid_retrieval.py`, `.answer`, `test_sample_documents.py`, `rag_v4_citation/test_contract_integration.py`, `SourceSpan`, `admin.py`, `LocalRagExecutor`, `make_manifest`, `answer_baseline/test_behavior_component.py`, `model/test_contract_integration.py`, `hybrid.py`, `rag/runtime.py`, `test_answer_baseline.py`, `eval_001_runner.py`, `IngestionService`, `EgressMode`, `answer_baseline/test_contract_integration.py`, `answer_baseline/test_e2e_operational.py`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Are the 55 inferred relationships involving `IngestionService` (e.g. with `reset_state()` and `ChunkMetadata`) actually correct?**
  _`IngestionService` has 55 INFERRED edges - model-reasoned connections that need verification._
- **Should `compose` be split into smaller, more focused modules?**
  _Cohesion score 0.07017543859649122 - nodes in this community are weakly interconnected._