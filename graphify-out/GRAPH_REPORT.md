# Graph Report - enterprise-agentic-rag-harness  (2026-11-12)

## Corpus Check
- 299 files · ~263,218 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 68 file(s) not represented in the graph (top: (none) 53, .toml 9, .example 2)

## Summary
- 4221 nodes · 13271 edges · 181 communities (124 shown, 57 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 1027 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7cb40169`
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
- db/runtime.py
- core/chat.py
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
- model/test_e2e_operational.py
- api/chat.py
- _make_retriever
- AuthorizationEvaluator
- chat_api/test_contract_integration.py
- admin.py
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
- IdentityRecord
- AuthenticatedPrincipal
- ToolResult
- App.tsx
- route
- gemini.py
- test_knowledge_database.py
- chat_api/test_e2e_operational.py
- expand_parent_context
- contracts/_baseline.py
- datasources
- monitoring/prometheus.yml
- authorization/test_behavior_component.py
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
- _evaluation_harness.py
- test_authorization.py
- normalize_user_input
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
- IdentityContractTests
- cache_memory/test_security_adversarial.py
- App.test.tsx
- cache_memory/test_contract_integration.py
- orchestration_langgraph/test_contract_integration.py
- SecureContextBuilder
- test_customer_api_e2e.py
- KnowledgeOperationalTests
- admin_api/test_contract_integration.py
- run_local_guardrail_pipeline
- ChunkMetadata
- manifest.json
- main.py
- orchestration_langgraph/test_behavior_component.py
- test_sample_documents.py
- ConversationMessage
- ingestion/test_security_adversarial.py
- AuthorizationDecision
- IdentitySecurityTests
- ndcg_at_k
- tree
- ChatService
- test_cache_memory.py
- DocumentsView
- UUID
- IdentityBehaviorTests
- read
- build_secure_context
- BackendBootstrapContractTests
- rag_v4_citation/test_e2e_operational.py
- PromptBehaviorComponentTests
- observability/context.py
- app/evidence/__init__.py
- InMemoryScopedCache
- ingestion/test_behavior_component.py
- ConversationMemoryRepository
- vercel.json
- db/runtime.py
- UUID
- App
- pathlib
- package.json
- BackendBootstrapBehaviorTests
- BehaviorComponentTests
- test_access_request_review.py
- authorization/test_e2e_operational.py
- test_customer_frontend_static.py
- make_manifest
- json

## God Nodes (most connected - your core abstractions)
1. `auth()` - 151 edges
2. `request()` - 151 edges
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
- `test_revoked_document_fails_current_version_policy_check()` --uses--> `Decision`  [INFERRED]
  tests/qa/admin_api/test_security_adversarial.py → backend/app/authorization/policy.py
- `test_acl_explicit_deny_overrides_employee_read_allow()` --uses--> `Action`  [INFERRED]
  tests/qa/admin_api/test_security_adversarial.py → backend/app/authorization/policy.py
- `test_revoked_document_fails_current_version_policy_check()` --uses--> `Action`  [INFERRED]
  tests/qa/admin_api/test_security_adversarial.py → backend/app/authorization/policy.py
- `test_source_download_is_rechecked_after_read_retrieval()` --uses--> `Action`  [INFERRED]
  tests/qa/evidence/test_e2e_operational.py → backend/app/authorization/policy.py

## Import Cycles
- 2-file cycle: `backend/app/api/admin.py -> backend/app/api/chat.py -> backend/app/api/admin.py`
- 2-file cycle: `backend/app/api/admin.py -> backend/app/api/identity.py -> backend/app/api/admin.py`
- 2-file cycle: `backend/app/api/chat.py -> backend/app/api/identity.py -> backend/app/api/chat.py`
- 3-file cycle: `backend/app/api/admin.py -> backend/app/api/chat.py -> backend/app/api/identity.py -> backend/app/api/admin.py`
- 3-file cycle: `backend/app/api/admin.py -> backend/app/api/identity.py -> backend/app/api/chat.py -> backend/app/api/admin.py`

## Communities (181 total, 57 thin omitted)

### Community 0 - "audit.py"
Cohesion: 0.10
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
Cohesion: 0.13
Nodes (5): require_all(), section(), BehaviorComponentTests, E2EOperationalTests, SecurityAdversarialTests

### Community 6 - "read"
Cohesion: 0.06
Nodes (7): dashboard(), read(), task(), MonitoringBehaviorTests, MonitoringContractTests, MonitoringOperationalTests, MonitoringSecurityTests

### Community 7 - "InMemoryDerivedIndex"
Cohesion: 0.09
Nodes (15): _acl_digest(), _chunk_digest(), _chunk_state(), DerivedIndex, DerivedIndexFailure, DerivedIndexRecord, IndexManifest, IndexPublicationStatus (+7 more)

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
Cohesion: 0.07
Nodes (10): _CacheEntry, _component(), _digest(), _identifier(), InvalidationReason, ScopedCacheAdapter, ScopedCacheKey, _serialized_size() (+2 more)

### Community 13 - "db/runtime.py"
Cohesion: 0.08
Nodes (12): _payload(), _department_uuid(), _membership_uuid(), normalize_database_url(), _PostgresAdapter, stable_uuid(), _tenant_slug(), user_uuid() (+4 more)

### Community 14 - "core/chat.py"
Cohesion: 0.07
Nodes (16): CacheScope, StaleScopeError, ActorKind, AnonymousSession, CheckpointRepository, _citation_expired(), ConversationRepository, ConversationSummary (+8 more)

### Community 15 - "ModelGateway"
Cohesion: 0.17
Nodes (38): DataClassification, ModelTask, FakeEmbedding, policy(), provider(), route(), test_approved_local_fallback_can_handle_internal_data(), test_approved_local_provider_can_process_internal_data() (+30 more)

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
Nodes (52): dependencies, react@18.3.1, react-dom@18.3.1, vite@6.3.5, @vitejs/plugin-react@4.6.0, devDependencies, eslint@9.17.0, @eslint/js@9.17.0 (+44 more)

### Community 20 - "answer_baseline/test_security_adversarial.py"
Cohesion: 0.12
Nodes (17): GeneratedAnswer, _LocalAnswerModel, _allow(), FakeModelGateway, _pipeline(), test_cross_tenant_evidence_is_absent_from_dense_bm25_and_answer(), test_direct_prompt_injection_is_denied_before_retrieval_and_model(), test_duplicate_and_unknown_citation_ids_do_not_duplicate_or_leak_metadata() (+9 more)

### Community 21 - "AuthorizationContractIntegrationTests"
Cohesion: 0.27
Nodes (4): AuthorizationContractIntegrationTests, document(), evaluator(), principal()

### Community 22 - "orchestration/context.py"
Cohesion: 0.20
Nodes (6): ContextLimitError, estimate_tokens(), PromptMessage, _render_evidence(), _safe_text(), _safe_value()

### Community 23 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+10 more)

### Community 24 - "InMemoryConversationMemory"
Cohesion: 0.12
Nodes (3): InvalidationEvent, InMemoryConversationMemory, FakeMemoryRepository

### Community 25 - "model/test_e2e_operational.py"
Cohesion: 0.10
Nodes (21): ModelGateway, ModelUnavailable, graph_labels(), policy(), run_graph_query(), ScriptedEmbedding, ScriptedReranker, task() (+13 more)

### Community 26 - "api/chat.py"
Cohesion: 0.09
Nodes (28): _anonymous_token(), _body(), _context(), create_conversation(), download_citation(), FeedbackRequest, get_conversation(), get_query_completion() (+20 more)

### Community 27 - "_make_retriever"
Cohesion: 0.09
Nodes (50): AccessGrant, Action, Effect, PolicyEnforcementPoint, DenseRetriever, InMemoryDenseVectorIndex, HybridRetrievalConfig, InMemoryBM25Index (+42 more)

### Community 28 - "AuthorizationEvaluator"
Cohesion: 0.07
Nodes (12): AuthorizationDenied, AuthorizationEvaluator, deny(), Classification, DocumentResource, _normalize_action(), PolicyDecision, PolicyStore (+4 more)

### Community 29 - "chat_api/test_contract_integration.py"
Cohesion: 0.12
Nodes (18): job_payload(), anonymous_conversation(), authenticated_conversation(), Clock, Executor, Maintenance, make_service(), principal() (+10 more)

### Community 30 - "admin.py"
Cohesion: 0.09
Nodes (25): _access_request_payload(), AccessGrantRequest, AccessRequest, AccessRequestReview, AdminApiState, _counts(), _dashboard_metric(), _dashboard_metrics() (+17 more)

### Community 31 - "chat_api/test_behavior_component.py"
Cohesion: 0.14
Nodes (21): AnswerState, JobState, _answer_status(), anonymous_conversation(), authenticated_conversation(), Clock, Executor, Maintenance (+13 more)

### Community 32 - "make_manifest"
Cohesion: 0.18
Nodes (13): make_manifest(), test_pdf_is_accepted(), graph_labels(), read(), task(), test_failed_new_publication_preserves_previous_active_version(), test_job_contract_keeps_attempt_and_tenant_scope(), test_legacy_doc_and_xls_are_rejected() (+5 more)

### Community 33 - "GraphifyOperationalTests"
Cohesion: 0.10
Nodes (5): DatabaseMigrationSmokeTests, graphify_bin(), run_graphify(), GraphifyOperationalTests, run_graph_query()

### Community 34 - "key"
Cohesion: 0.11
Nodes (39): ScanVerdict, key(), prepare_review_two(), publish(), test_manager_activates_provisioned_account(), test_manager_completes_two_review_publication(), test_manager_provisions_inactive_employee(), test_manager_uploads_into_quarantine() (+31 more)

### Community 35 - "chat_api/test_security_adversarial.py"
Cohesion: 0.12
Nodes (22): QueryCompletion, RuntimeDatabaseUnavailable, IdentityError, anonymous_conversation(), authenticated_conversation(), Clock, Executor, Maintenance (+14 more)

### Community 36 - "steps"
Cohesion: 0.15
Nodes (12): jobs, validate, name, on, pull_request, workflow_dispatch, run, uses (+4 more)

### Community 37 - "hybrid.py"
Cohesion: 0.10
Nodes (12): ModelProviderError, EmbeddingAdapter, EmbeddingRequest, EmbeddingResult, RankedDocument, RerankerAdapter, RerankerResult, ModelRoute (+4 more)

### Community 40 - "rules"
Cohesion: 0.17
Nodes (11): runbook, summary, groups, name, rules, severity, alert, annotations (+3 more)

### Community 41 - "IdentityRecord"
Cohesion: 0.05
Nodes (22): rate_limited(), IdentityRecord, SessionRecord, utc_z(), AuthenticationService, IdentityErrorPassthrough, now_utc(), hash_secret() (+14 more)

### Community 42 - "AuthenticatedPrincipal"
Cohesion: 0.12
Nodes (11): AuthenticatedPrincipal, _citation(), _cosine(), DenseEvidence, DenseRetrievalResult, SourceFetchResult, _uuid(), _valid_locator() (+3 more)

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
Cohesion: 0.07
Nodes (25): AnonymousPrincipal, GeminiProviderError, GeminiStreamProvider, _http_error_code(), _text_parts(), LocalRagExecutor, anonymous_conversation(), clean_state() (+17 more)

### Community 47 - "test_knowledge_database.py"
Cohesion: 0.26
Nodes (11): migration_text(), test_existing_db_contract_has_active_index_guard(), test_existing_db_contract_has_chunks_table(), test_existing_db_contract_has_composite_parent_fk(), test_existing_db_contract_has_document_versions_table(), test_existing_db_contract_has_documents_table(), test_existing_db_contract_has_immutable_version_uniqueness(), test_existing_db_contract_has_private_source_constraint() (+3 more)

### Community 48 - "chat_api/test_e2e_operational.py"
Cohesion: 0.13
Nodes (18): test_healthz_is_local_liveness_only(), test_identity_requires_bearer_credentials(), test_vercel_origin_can_use_cookie_authenticated_api(), anonymous_conversation(), HttpExecutor, request(), sign_in(), test_http_anonymous_lifecycle_and_session_isolation() (+10 more)

### Community 49 - "expand_parent_context"
Cohesion: 0.08
Nodes (54): _active(), ChildEvidence, _coerce_child(), _coerce_parent(), _construct(), expand_parent_context(), _identity(), _index_parents() (+46 more)

### Community 51 - "datasources"
Cohesion: 0.22
Nodes (8): apiVersion, datasources, access, editable, isDefault, name, type, url

### Community 52 - "monitoring/prometheus.yml"
Cohesion: 0.22
Nodes (8): global, evaluation_interval, scrape_interval, rule_files, scrape_configs, job_name, static_configs, targets

### Community 53 - "authorization/test_behavior_component.py"
Cohesion: 0.32
Nodes (5): ConversationResource, AuthorizationBehaviorTests, document(), evaluator(), principal()

### Community 54 - "client.ts"
Cohesion: 0.07
Nodes (35): AccessGrant, AccessRequestMetadata, AccessRequestResponse, answerFromStream(), ApiError, ApprovalRecord, AuditRecord, Conversation (+27 more)

### Community 56 - "AuthenticatedPrincipal"
Cohesion: 0.07
Nodes (33): PDFLocator, AnswerCitation, Citation, _citation(), _FusedCandidate, HybridEvidence, HybridRetrievalResult, _AnswerModel (+25 more)

### Community 57 - "request"
Cohesion: 0.11
Nodes (37): activateUser(), createDepartment(), createUser(), deleteDocument(), getAccessRequests(), getApprovals(), getConversations(), getCurrentIdentity() (+29 more)

### Community 58 - "_resolve"
Cohesion: 0.22
Nodes (37): activate_user(), approve_document_version(), _body(), _bump_policy_epoch(), create_department(), create_user(), delete_document(), _department_payload() (+29 more)

### Community 59 - "upload"
Cohesion: 0.15
Nodes (20): Decision, add_user(), upload(), test_acl_explicit_deny_overrides_employee_read_allow(), test_anonymous_cannot_upload(), test_chairman_cannot_approve(), test_chairman_cannot_upload(), test_cross_tenant_document_is_not_revealed() (+12 more)

### Community 60 - "admin_api/test_behavior_component.py"
Cohesion: 0.16
Nodes (11): clean_state(), _prepare_review_two_without_index_ack(), test_manager_activates_provisioned_account(), test_manager_completes_two_review_publication(), test_manager_provisions_inactive_employee(), test_manager_uploads_into_quarantine(), test_publish_requires_acknowledged_index(), test_quarantined_document_is_not_readable() (+3 more)

### Community 61 - "tests/test_chat_api.py"
Cohesion: 0.20
Nodes (13): anonymous_conversation(), authenticated_headers(), request(), StubExecutor, test_anonymous_submit_status_completion_and_history_are_session_scoped(), test_authenticated_history_is_owner_only_and_revocation_denies_reuse(), test_citation_preview_and_download_are_separate_fresh_authorization_checks(), test_cross_origin_anonymous_cookie_is_usable_by_vercel_fetch() (+5 more)

### Community 62 - "request"
Cohesion: 0.09
Nodes (56): auth(), request(), test_account_response_does_not_return_password(), test_approval_schema_requires_explicit_stage(), test_existing_sign_in_contract_remains_under_auth_prefix(), test_job_status_contains_redacted_progress_only(), test_mutating_post_requires_idempotency_key(), test_problem_response_uses_safe_media_type_for_anonymous_admin_call() (+48 more)

### Community 86 - "answer_baseline/test_behavior_component.py"
Cohesion: 0.09
Nodes (23): AnswerModelGateway, AnswerResult, AnswerStatus, DirectAnswerPipeline, PreparedAnswer, _authorization(), FakeModelGateway, _pipeline() (+15 more)

### Community 87 - "orchestration_langgraph/test_security_adversarial.py"
Cohesion: 0.13
Nodes (20): Answerer, Backend, call(), Clock, gateway(), Policy, principal(), request() (+12 more)

### Community 88 - "model/test_contract_integration.py"
Cohesion: 0.23
Nodes (13): ModelPolicy, test_mapping_loads_versioned_policy_without_credentials(), test_policy_rejects_credential_fields(), mapping(), test_access_token_field_is_rejected(), test_exact_api_key_field_is_rejected(), test_fallback_route_task_mismatch_is_rejected(), test_mapping_rejects_empty_model_revision() (+5 more)

### Community 89 - "_evaluation_harness.py"
Cohesion: 0.21
Nodes (7): _vectorize(), load_records(), load_validated_records(), unauthorized_retrieval_rate(), validate_dataset(), validate_record(), _validate_span()

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
Cohesion: 0.48
Nodes (4): _answer_covers_evidence(), _answer_has_term(), _claim_terms(), _relevant_evidence()

### Community 95 - "evaluator"
Cohesion: 0.27
Nodes (5): InMemoryPolicyStore, AuthorizationSecurityAdversarialTests, document(), evaluator(), principal()

### Community 96 - "inherit_acl"
Cohesion: 0.13
Nodes (18): inherit_acl(), make_child(), make_parent(), test_conflicting_child_acl_is_denied(), test_document_mismatch_is_denied(), test_matching_child_acl_is_preserved(), test_missing_child_acl_is_inherited(), test_qdrant_projection_does_not_claim_authority() (+10 more)

### Community 97 - "env.py"
Cohesion: 0.38
Nodes (3): _database_url(), run_migrations_offline(), run_migrations_online()

### Community 98 - "test_tool_gateway.py"
Cohesion: 0.15
Nodes (22): _Backend, _call(), _Clock, _gateway(), _Policy, _principal(), _Resolvers, test_backend_exception_is_unavailable_without_raw_error() (+14 more)

### Community 99 - "AnswerDraft"
Cohesion: 0.26
Nodes (20): AnswerDraft, _Answerer, _Clock, _evidence(), _orchestrator(), _request(), test_answerer_error_is_returned_as_safe_error(), test_complex_route_splits_subqueries_and_preserves_bound() (+12 more)

### Community 100 - "test_answer_baseline.py"
Cohesion: 0.32
Nodes (10): _authorization(), authorize(), FakeModelGateway, _pipeline(), test_direct_answer_returns_insufficient_without_calling_model_when_no_match(), test_direct_answer_returns_partial_for_mixed_claims(), test_direct_answer_returns_supported_answer_and_authorized_citation(), test_guardrail_failure_fails_closed_before_model_call() (+2 more)

### Community 102 - "eval_001_runner.py"
Cohesion: 0.10
Nodes (26): _aggregate(), _AnswerModel, _Case, _DenseAsHybrid, evaluate(), evaluation_snapshot(), _make_case(), authorize() (+18 more)

### Community 103 - "IngestionService"
Cohesion: 0.13
Nodes (19): IngestionService, _active_document(), _principal(), _retriever(), test_dense_retrieval_returns_authorized_current_chunk_only(), test_active_retrieval_to_evidence_verification_succeeds(), test_cross_tenant_retrieval_is_empty_and_cannot_be_verified(), test_policy_store_failure_denies_search_and_source_fetch() (+11 more)

### Community 104 - "Claim"
Cohesion: 0.13
Nodes (31): Claim, EvidenceRecord, SourceSpan, citation(), test_authorizer_must_attest_active_current_and_not_revoked(), test_citation_and_source_span_are_immutable(), test_conflicting_numeric_source_spans_are_disclosed(), test_denial_result_does_not_leak_source_text() (+23 more)

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
Cohesion: 0.20
Nodes (22): ModelEgressDenied, EgressMode, provider(), route(), test_embedding_route_task_is_checked(), test_external_internal_requires_dpa(), test_external_internal_requires_residency(), test_external_provider_requires_retention_policy() (+14 more)

### Community 110 - "read"
Cohesion: 0.16
Nodes (5): backend_boot_task(), compile_sources_without_writes(), read(), task_packet(), BackendBootstrapOperationalTests

### Community 111 - "reset"
Cohesion: 0.06
Nodes (21): reset_state(), reset_state(), reset(), clean_state(), clean_state(), clean_state(), clean_state(), clean_state() (+13 more)

### Community 112 - "quarantine"
Cohesion: 0.15
Nodes (24): new_service(), quarantine(), test_publishing_new_version_supersedes_previous_version(), test_rejected_scan_is_terminal_and_not_retrievable(), test_review_one_requires_clean_scan(), test_revoke_active_version_removes_retrieval(), test_second_review_and_publish_make_version_active(), test_soft_delete_isolates_all_versions() (+16 more)

### Community 113 - "AuthorizationDecision"
Cohesion: 0.16
Nodes (20): ClaimVerification, EvidenceVerifier, VerificationRequest, VerificationResult, allow_active(), citation(), test_authorization_callback_exception_fails_closed(), test_cross_tenant_evidence_is_denied_before_authorizer_invocation() (+12 more)

### Community 114 - "answer_baseline/test_contract_integration.py"
Cohesion: 0.19
Nodes (15): _allow(), RecordingModel, RecordingRetriever, _setup(), test_citation_authorization_rejects_document_mismatch(), test_citation_authorization_rejects_non_active_status(), test_citation_authorization_rejects_non_current_version(), test_citation_authorization_rejects_revoked_source() (+7 more)

### Community 115 - "BoundedOrchestrator"
Cohesion: 0.08
Nodes (13): NoopQueryExecutor, AssembledContext, AnswerSynthesizer, BoundedOrchestrator, _evidence_from_result(), _GraphState, OrchestrationOutcome, OrchestrationRequest (+5 more)

### Community 116 - "answer_baseline/test_e2e_operational.py"
Cohesion: 0.18
Nodes (14): FailingEmbedder, FailingReranker, FakeAnswerGateway, _setup(), test_operational_abstention_is_insufficient_evidence(), test_operational_conflicting_evidence_is_not_harmonized(), test_operational_denied_content_never_appears_in_failure_result(), test_operational_embedding_failure_does_not_fallback_to_bm25() (+6 more)

### Community 117 - "read_frontend"
Cohesion: 0.13
Nodes (3): read_frontend(), FrontendBehaviorComponentTests, FrontendSecurityAdversarialTests

### Community 120 - "cache_memory/test_security_adversarial.py"
Cohesion: 0.36
Nodes (12): make_key(), make_scope(), test_anonymous_revocation_isolated_to_one_session_and_fails_closed(), test_broad_scope_cannot_replay_after_a_narrow_document_change(), test_cache_key_excludes_queries_model_inputs_and_conversation_identifiers(), test_changed_document_version_cannot_repopulate_an_old_cache_entry(), test_cross_principal_cache_read_is_a_fail_closed_miss(), test_cross_scope_conversation_read_cannot_be_recovered_by_matching_id() (+4 more)

### Community 121 - "App.test.tsx"
Cohesion: 0.20
Nodes (7): clearAccessToken(), signOut(), handleSignOut(), adminPrincipal, conversationResponse(), json(), principal

### Community 122 - "cache_memory/test_contract_integration.py"
Cohesion: 0.36
Nodes (11): make_key(), make_scope(), test_contract_acl_change_can_target_one_principal_and_version(), test_contract_delete_event_invalidates_matching_scope_without_cross_tenant_reach(), test_contract_document_change_invalidates_broad_scope_and_selected_version(), test_contract_invalid_event_shapes_fail_closed_at_the_boundary(), test_contract_memory_read_requires_the_authoritative_current_scope(), test_contract_policy_epoch_change_requires_a_new_scope_for_reuse() (+3 more)

### Community 123 - "orchestration_langgraph/test_contract_integration.py"
Cohesion: 0.18
Nodes (16): Backend, call(), Clock, gateway(), Policy, principal(), Resolvers, test_chunk_read_contract_accepts_only_chunk_id_shape() (+8 more)

### Community 125 - "test_customer_api_e2e.py"
Cohesion: 0.07
Nodes (16): _durable_access_request_store(), get_settings(), Settings, healthz(), test_settings_accept_platform_database_url(), anonymous_conversation(), parse_sse(), request() (+8 more)

### Community 126 - "KnowledgeOperationalTests"
Cohesion: 0.17
Nodes (3): read(), task(), KnowledgeOperationalTests

### Community 127 - "admin_api/test_contract_integration.py"
Cohesion: 0.16
Nodes (12): clean_state(), test_account_response_does_not_return_password(), test_approval_schema_requires_explicit_stage(), test_job_status_contains_redacted_progress_only(), test_mutating_post_requires_idempotency_key(), test_upload_accepts_docx_mime_inference(), test_upload_accepts_xlsx_mime_inference(), test_upload_idempotency_rejects_a_different_fingerprint() (+4 more)

### Community 129 - "ChunkMetadata"
Cohesion: 0.07
Nodes (30): ChunkMetadata, DocumentMetadata, DocumentVersionMetadata, _ImmutableModel, SourceSpan, to_qdrant_payload(), test_active_chunk_requires_acl_metadata(), test_chunk_accepts_source_provenance() (+22 more)

### Community 130 - "manifest.json"
Cohesion: 0.15
Nodes (12): corpus_id, documents, provenance, external_sources, kind, owner, source, queries (+4 more)

### Community 131 - "main.py"
Cohesion: 0.16
Nodes (13): create_access_request(), _bearer_token(), _clear_session_cookie(), current_identity(), _record(), _record_identity_error(), _request_context(), _set_session_cookie() (+5 more)

### Community 132 - "orchestration_langgraph/test_behavior_component.py"
Cohesion: 0.25
Nodes (15): Answerer, Clock, evidence(), request(), run(), test_compiles_a_state_graph_with_expected_nodes(), test_complex_loop_caps_subqueries_and_tool_calls_at_four(), test_complex_query_splits_into_distinct_subqueries() (+7 more)

### Community 133 - "test_sample_documents.py"
Cohesion: 0.06
Nodes (34): RerankerRequest, route(), ProviderPolicy, DeterministicEmbeddingAdapter, DeterministicRerankerAdapter, reciprocal_rank_fusion(), _tokens(), _gateway() (+26 more)

### Community 134 - "ConversationMessage"
Cohesion: 0.13
Nodes (18): ConversationMemory, ConversationMessage, test_contract_fake_repository_implements_provider_neutral_memory_boundary(), Clock, FakeInvalidationBus, FakeMemoryRepository, make_key(), make_scope() (+10 more)

### Community 135 - "ingestion/test_security_adversarial.py"
Cohesion: 0.16
Nodes (10): RuntimeFailureOnRemove, service_with_index(), test_cleanup_backend_error_is_wrapped_without_secret_leakage(), test_cross_tenant_document_lookup_is_denied(), test_cross_tenant_job_lookup_is_denied(), test_cross_tenant_version_lookup_is_denied(), test_derived_staging_state_cannot_authorize_retrieval(), test_legal_hold_blocks_permanent_delete() (+2 more)

### Community 136 - "AuthorizationDecision"
Cohesion: 0.11
Nodes (21): AuthorizationDecision, revoked(), current_v2(), _CapturingModel, _Model, test_direct_answer_context_includes_authorized_parent_runtime(), authorize(), test_real_hybrid_path_propagates_pdf_schema_end_to_end() (+13 more)

### Community 138 - "ndcg_at_k"
Cohesion: 0.15
Nodes (15): answer_correctness(), citation_accuracy(), evaluate_case(), mean_reciprocal_rank(), ndcg_at_k(), no_answer_accuracy(), recall_at_k(), source_key() (+7 more)

### Community 140 - "ChatService"
Cohesion: 0.22
Nodes (5): ChatActor, ChatService, ConversationRecord, _error(), _fingerprint()

### Community 141 - "test_cache_memory.py"
Cohesion: 0.28
Nodes (12): Clock, response_key(), scope(), test_cache_delete_is_explicit(), test_cache_expires_and_rejects_unbounded_ttl_or_value(), test_cache_key_contains_security_scope_but_not_raw_query(), test_cache_requires_exact_current_scope_and_isolates_tenant_and_principal(), test_conversation_delete_removes_body_and_blocks_recreation_in_old_scope() (+4 more)

### Community 142 - "DocumentsView"
Cohesion: 0.31
Nodes (10): getAuditEvents(), getDocuments(), getFeedback(), uploadMetadataDocument(), AuditView(), load(), DataViewEmpty(), DocumentsView() (+2 more)

### Community 145 - "read"
Cohesion: 0.18
Nodes (4): read(), task(), tasks(), IdentityOperationalTests

### Community 146 - "build_secure_context"
Cohesion: 0.16
Nodes (5): build_secure_context(), RetrievedEvidence, PromptOperationalTests, PromptSecurityAdversarialTests, test_secure_context_escapes_parent_prompt_injection_as_untrusted_content()

### Community 148 - "rag_v4_citation/test_e2e_operational.py"
Cohesion: 0.11
Nodes (20): DOCXLocator, XLSXLocator, test_malformed_locator_model_is_rejected(), _locator(), _allow(), _answer(), _locator(), _Model (+12 more)

### Community 150 - "observability/context.py"
Cohesion: 0.19
Nodes (5): identity_error_handler(), _header(), _new_traceparent(), _valid_traceparent(), test_correlation_context_preserves_valid_headers_and_creates_child()

### Community 151 - "app/evidence/__init__.py"
Cohesion: 0.13
Nodes (15): CitationRecord, _is_negative(), _numeric_conflict(), _numeric_terms(), _relation(), _terms(), VerificationOutcome, _answer_citation() (+7 more)

### Community 152 - "InMemoryScopedCache"
Cohesion: 0.20
Nodes (14): InMemoryScopedCache, test_cache_invalidation_hooks_remove_only_matching_scope(), Clock, make_key(), make_scope(), test_broad_acl_invalidation_removes_all_versions_in_one_tenant(), test_cache_expires_at_the_exact_ttl_deadline(), test_cache_rejects_invalid_ttl_and_oversize_values() (+6 more)

### Community 153 - "ingestion/test_behavior_component.py"
Cohesion: 0.22
Nodes (6): test_empty_processing_input_is_rejected(), test_malware_scan_is_terminal(), test_new_active_version_supersedes_previous_version(), test_publish_activates_authoritative_version_and_chunks(), test_review_one_requires_clean_scan(), test_staging_is_not_retrievable_before_ack_and_publish()

### Community 156 - "db/runtime.py"
Cohesion: 0.13
Nodes (11): JobCheckpoint, MessageRecord, PostgresAccessRequestStore, _utc_z(), _as_utc(), _jsonb(), _parse_uuid(), PostgresAuditSink (+3 more)

### Community 159 - "UUID"
Cohesion: 0.10
Nodes (18): ApprovalBlocked, ApprovalRecord, DocumentRecord, IdempotencyConflict, IndexPublication, IngestionError, IngestionJob, InvalidInput (+10 more)

### Community 161 - "App"
Cohesion: 0.09
Nodes (37): createConversation(), getConversation(), previewCitation(), submitFeedback(), AdminGuardView(), App(), closeAuth(), completeAuthentication() (+29 more)

### Community 162 - "pathlib"
Cohesion: 0.17
Nodes (4): dfs(), load_frontend_json(), read(), FrontendContractIntegrationTests

### Community 164 - "package.json"
Cohesion: 0.38
Nodes (5): dependencies, @neon/config@^1.14.0, @neon/env@^2.1.3, @neon/config, @neon/env

### Community 166 - "BackendBootstrapBehaviorTests"
Cohesion: 0.19
Nodes (4): calls(), function(), literal(), BackendBootstrapBehaviorTests

### Community 171 - "test_access_request_review.py"
Cohesion: 0.21
Nodes (10): clean_state(), create_request(), test_anonymous_request_uses_server_configured_tenant(), test_approve_is_idempotent_and_does_not_grant_access(), test_http_only_session_cookie_restores_identity_after_reload(), test_manager_cannot_list_or_review_another_tenant_request(), test_manager_lists_same_tenant_pending_requests_as_safe_metadata_only(), test_only_managers_can_review_access_requests() (+2 more)

### Community 183 - "authorization/test_e2e_operational.py"
Cohesion: 0.32
Nodes (4): AuthorizationOperationalTests, document(), evaluator(), principal()

### Community 186 - "test_customer_frontend_static.py"
Cohesion: 0.15
Nodes (6): test_chat_controls_have_keyboard_labels_and_live_status_semantics(), test_mobile_375x812_contract_keeps_chat_controls_within_the_viewport(), test_reload_contract_restores_conversation_and_requests_history(), test_responsive_layout_has_mobile_breakpoints_and_no_horizontal_body_overflow(), test_retryable_backend_error_has_a_user_recovery_action(), test_stop_control_is_available_only_during_a_live_stream()

### Community 197 - "make_manifest"
Cohesion: 0.15
Nodes (24): UploadManifest, make_chunks(), validated(), test_clean_review_one_allows_processing(), test_processing_inherits_parent_acl(), test_approval_expiry_blocks_publication(), test_doc_is_rejected(), test_internal_upload_requires_department() (+16 more)

### Community 201 - "json"
Cohesion: 0.18
Nodes (3): test_dashboard_has_api_and_security_panels(), test_dashboard_is_valid_json(), test_rag002_task_registry_keeps_retrieval_validation_and_scope()

## Knowledge Gaps
- **1 isolated node(s):** `enterprise-agentic-rag-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 1034 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **57 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AuthenticatedPrincipal` connect `AuthenticatedPrincipal` to `main.py`, `test_sample_documents.py`, `ChatService`, `core/chat.py`, `rag_v4_citation/test_e2e_operational.py`, `AuthorizationContractIntegrationTests`, `app/evidence/__init__.py`, `api/chat.py`, `_make_retriever`, `AuthorizationEvaluator`, `chat_api/test_contract_integration.py`, `admin.py`, `chat_api/test_behavior_component.py`, `chat_api/test_security_adversarial.py`, `hybrid.py`, `IdentityRecord`, `ToolResult`, `gemini.py`, `expand_parent_context`, `authorization/test_behavior_component.py`, `authorization/test_e2e_operational.py`, `AuthenticatedPrincipal`, `_resolve`, `answer_baseline/test_behavior_component.py`, `orchestration_langgraph/test_security_adversarial.py`, `test_authorization.py`, `rag/runtime.py`, `evaluator`, `test_tool_gateway.py`, `eval_001_runner.py`, `IngestionService`, `orchestration_langgraph/test_contract_integration.py`, `test_customer_api_e2e.py`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Are the 88 inferred relationships involving `DataClassification` (e.g. with `_require_manager()` and `UploadRequest`) actually correct?**
  _`DataClassification` has 88 INFERRED edges - model-reasoned connections that need verification._
- **What connects `enterprise-agentic-rag-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `audit.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10241820768136557 - nodes in this community are weakly interconnected._
- **Why does `DataClassification` connect `ModelGateway` to `test_sample_documents.py`, `InMemoryDerivedIndex`, `AuthorizationDecision`, `answer_baseline/test_security_adversarial.py`, `rag_v4_citation/test_e2e_operational.py`, `app/evidence/__init__.py`, `model/test_e2e_operational.py`, `_make_retriever`, `.__init__`, `admin.py`, `UUID`, `make_manifest`, `hybrid.py`, `AuthenticatedPrincipal`, `gemini.py`, `expand_parent_context`, `AuthenticatedPrincipal`, `_resolve`, `make_manifest`, `answer_baseline/test_behavior_component.py`, `model/test_contract_integration.py`, `rag/runtime.py`, `test_answer_baseline.py`, `eval_001_runner.py`, `IngestionService`, `EgressMode`, `answer_baseline/test_contract_integration.py`, `answer_baseline/test_e2e_operational.py`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Are the 55 inferred relationships involving `IngestionService` (e.g. with `reset_state()` and `ChunkMetadata`) actually correct?**
  _`IngestionService` has 55 INFERRED edges - model-reasoned connections that need verification._
- **Should `compose` be split into smaller, more focused modules?**
  _Cohesion score 0.07017543859649122 - nodes in this community are weakly interconnected._