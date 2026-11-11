# Graph Report - enterprise-agentic-rag-harness  (2026-11-11)

## Corpus Check
- 274 files · ~232,115 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 68 file(s) not represented in the graph (top: (none) 53, .toml 9, .example 2)

## Summary
- 3875 nodes · 11724 edges · 194 communities (128 shown, 66 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 1179 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `141b4f3e`
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
- read_frontend
- read
- otel-collector-config.yaml
- prometheus
- identity.py
- dense.py
- model/_baseline.py
- postgres
- postgres
- env.py
- package.json
- models/policy.py
- InMemoryPolicyStore
- rag_v4_citation/test_contract_integration.py
- compilerOptions
- InMemoryConversationMemory
- expand_parent_context
- IdentityRecord
- DocumentResource
- auth
- chat_api/test_contract_integration.py
- DataClassification
- chat_api/test_behavior_component.py
- _evaluation_harness.py
- GraphifyOperationalTests
- key
- chat_api/test_security_adversarial.py
- steps
- pytest
- ContractIntegrationTests
- SecurityAdversarialTests
- rules
- knowledge/_baseline.py
- admin_api/test_behavior_component.py
- ToolResult
- lifecycle.py
- route
- CacheScope
- test_knowledge_database.py
- chat_api/test_e2e_operational.py
- active
- App.tsx
- datasources
- monitoring/prometheus.yml
- AuthorizationDecision
- dependencies
- App.test.tsx
- scripts
- ErrorNotice
- admin.py
- PromptDefinition
- tests/test_chat_api.py
- answer_baseline/test_security_adversarial.py
- orchestrator.py
- vite-env.d.ts
- sync_graph.sh
- migrate.sh
- inspect_untrusted_content
- enterprise-agentic-rag-backend
- answer_baseline/test_behavior_component.py
- orchestration_langgraph/test_security_adversarial.py
- AnswerCitation
- test_answer_citation_schema.py
- _make_retriever
- ModelPolicy
- inherit_acl
- IdentityError
- test_tool_gateway.py
- AnswerDraft
- AuthenticatedPrincipal
- load_validated_records
- IngestionService
- ModelProviderError
- FrontendE2EOperationalTests
- InMemoryIdentityStore
- ToolResult
- ingestion/_baseline.py
- IdentityBehaviorTests
- backend_boot/_baseline.py
- reset
- rag_v4_citation/test_e2e_operational.py
- EvidenceVerifier
- answer_baseline/test_contract_integration.py
- Claim
- answer_baseline/test_e2e_operational.py
- to_qdrant_payload
- test_knowledge_security.py
- guardrails/__init__.py
- test_answer_baseline.py
- normalize_user_input
- ScopedCacheKey
- orchestration_langgraph/test_contract_integration.py
- validate_output
- DocumentVersionMetadata
- knowledge/models.py
- make_manifest
- run_local_guardrail_pipeline
- Citation
- orchestration/context.py
- evidence/test_behavior_component.py
- orchestration_langgraph/test_behavior_component.py
- KnowledgeOperationalTests
- cache_memory/test_e2e_operational.py
- cache_memory/test_security_adversarial.py
- PromptContractIntegrationTests
- rag_v4_citation/test_security_adversarial.py
- main.py
- ingestion/test_security_adversarial.py
- ChatService
- test_cache_memory.py
- InMemoryScopedCache
- test_authorization.py
- eval_001_runner.py
- IdentityContractTests
- build_secure_context
- evidence/__init__.py
- admin_api/test_security_adversarial.py
- json
- AuditContractTests
- cache_memory/test_contract_integration.py
- evidence/test_contract_integration.py
- UUID
- InfrastructureSecurityTests
- db/runtime.py
- feedback/service.py
- model/test_security_adversarial.py
- ingestion/test_behavior_component.py
- App
- ModelRoute
- BehaviorComponentTests
- AuditSecurityTests
- key
- new_service
- request
- IdentityContractTests
- DurableChatRepository
- ndcg_at_k
- E2EOperationalTests
- GraphifyBehaviorTests
- PromptBehaviorComponentTests
- observability/context.py
- DashboardView
- signIn

## God Nodes (most connected - your core abstractions)
1. `request()` - 140 edges
2. `auth()` - 138 edges
3. `IngestionService` - 118 edges
4. `DataClassification` - 95 edges
5. `AuthenticatedPrincipal` - 88 edges
6. `new_service()` - 85 edges
7. `CacheScope` - 82 edges
8. `_active_document()` - 78 edges
9. `ModelGateway` - 66 edges
10. `ChunkMetadata` - 65 edges

## Surprising Connections (you probably didn't know these)
- `authorize()` --calls--> `AuthorizationDecision`  [INFERRED]
  tests/integration/test_answer_baseline.py → backend/app/evidence/verifier.py
- `reset_api_state()` --calls--> `InMemoryAuditSink`  [INFERRED]
  tests/qa/chat_api/test_contract_integration.py → backend/app/observability/audit.py
- `reset_api_state()` --calls--> `InMemoryAuditSink`  [INFERRED]
  tests/qa/chat_api/test_e2e_operational.py → backend/app/observability/audit.py
- `AuthorizationSecurityAdversarialTests` --uses--> `AuthenticatedPrincipal`  [INFERRED]
  tests/qa/authorization/test_security_adversarial.py → backend/app/identity/models.py
- `test_unknown_classification_and_noncanonical_principal_are_denied()` --uses--> `AuthenticatedPrincipal`  [INFERRED]
  tests/security/test_authorization.py → backend/app/identity/models.py

## Import Cycles
- 2-file cycle: `backend/app/api/admin.py -> backend/app/api/identity.py -> backend/app/api/admin.py`
- 2-file cycle: `backend/app/api/admin.py -> backend/app/api/chat.py -> backend/app/api/admin.py`
- 2-file cycle: `backend/app/api/chat.py -> backend/app/api/identity.py -> backend/app/api/chat.py`
- 3-file cycle: `backend/app/api/admin.py -> backend/app/api/identity.py -> backend/app/api/chat.py -> backend/app/api/admin.py`
- 3-file cycle: `backend/app/api/admin.py -> backend/app/api/chat.py -> backend/app/api/identity.py -> backend/app/api/admin.py`

## Communities (194 total, 66 thin omitted)

### Community 0 - "audit.py"
Cohesion: 0.11
Nodes (17): append_audit_event(), AuditEvent, AuditSink, AuditSinkUnavailable, InMemoryAuditSink, redact_metadata(), _safe_code(), _safe_identifier() (+9 more)

### Community 1 - "compose"
Cohesion: 0.07
Nodes (11): compose(), compose_config_result(), database(), handoff(), read(), tasks(), testing(), DisposablePostgresBehaviorTests (+3 more)

### Community 2 - "read"
Cohesion: 0.06
Nodes (7): migration_files(), migration_text(), read(), DatabaseBaselineBehaviorTests, DatabaseBaselineContractTests, DatabaseBaselineOperationalTests, DatabaseBaselineSecurityTests

### Community 3 - "read"
Cohesion: 0.07
Nodes (7): compose_config(), read(), task(), tasks(), InfrastructureBehaviorTests, InfrastructureContractTests, InfrastructureOperationalTests

### Community 4 - "read"
Cohesion: 0.12
Nodes (5): read(), task(), tasks(), AuditBehaviorTests, AuditOperationalTests

### Community 5 - "section"
Cohesion: 0.11
Nodes (6): require_all(), section(), BehaviorComponentTests, ContractIntegrationTests, E2EOperationalTests, SecurityAdversarialTests

### Community 6 - "read"
Cohesion: 0.06
Nodes (7): dashboard(), read(), task(), MonitoringBehaviorTests, MonitoringContractTests, MonitoringOperationalTests, MonitoringSecurityTests

### Community 7 - "read_frontend"
Cohesion: 0.09
Nodes (6): load_frontend_json(), read(), read_frontend(), FrontendBehaviorComponentTests, FrontendContractIntegrationTests, FrontendSecurityAdversarialTests

### Community 8 - "read"
Cohesion: 0.16
Nodes (3): read(), GraphifyContractTests, GraphifySecurityTests

### Community 9 - "otel-collector-config.yaml"
Cohesion: 0.06
Nodes (32): action, key, actions, send_batch_size, timeout, exporters, prometheus, endpoint (+24 more)

### Community 10 - "prometheus"
Cohesion: 0.06
Nodes (30): command, image, ports, read_only, security_opt, volumes, depends_on, image (+22 more)

### Community 13 - "identity.py"
Cohesion: 0.19
Nodes (10): _bearer_token(), current_identity(), _record(), _record_identity_error(), _request_context(), sign_in(), sign_out(), SignInRequest (+2 more)

### Community 14 - "dense.py"
Cohesion: 0.07
Nodes (20): AccessGrant, Action, AnonymousPrincipal, AuthorizationDenied, deny(), Classification, ConversationResource, Decision (+12 more)

### Community 15 - "model/_baseline.py"
Cohesion: 0.12
Nodes (19): run_graph_query(), graph_labels(), policy(), run_graph_query(), ScriptedEmbedding, task(), test_primary_retries_cannot_exceed_two(), test_timeout_cannot_exceed_sixty_seconds() (+11 more)

### Community 16 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, networks (+12 more)

### Community 17 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, networks (+12 more)

### Community 18 - "env.py"
Cohesion: 0.19
Nodes (4): _database_url(), run_migrations_offline(), run_migrations_online(), DatabaseMigrationSmokeTests

### Community 19 - "package.json"
Cohesion: 0.08
Nodes (35): devDependencies, eslint@9.17.0, @eslint/js@9.17.0, eslint-plugin-react-hooks@5.1.0, eslint-plugin-react-refresh@0.4.16, globals@15.14.0, jsdom@25.0.1, @testing-library/jest-dom@6.6.3 (+27 more)

### Community 20 - "models/policy.py"
Cohesion: 0.15
Nodes (12): EmbeddingAdapter, EmbeddingRequest, EmbeddingResult, RerankerAdapter, ModelTask, test_embedding_request_rejects_blank_text(), test_embedding_request_requires_texts(), test_embedding_result_requires_consistent_dimensions() (+4 more)

### Community 21 - "InMemoryPolicyStore"
Cohesion: 0.41
Nodes (4): AuthorizationSecurityAdversarialTests, document(), evaluator(), principal()

### Community 22 - "rag_v4_citation/test_contract_integration.py"
Cohesion: 0.11
Nodes (24): HybridEvidence, _active(), ChildEvidence, _coerce_child(), _coerce_parent(), _construct(), _identity(), _index_parents() (+16 more)

### Community 23 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+10 more)

### Community 24 - "InMemoryConversationMemory"
Cohesion: 0.11
Nodes (4): InvalidationEvent, ConversationMemoryRepository, InMemoryConversationMemory, FakeMemoryRepository

### Community 25 - "expand_parent_context"
Cohesion: 0.19
Nodes (25): expand_parent_context(), child(), parent(), test_callback_failure_fails_closed_for_parent_only(), test_cross_tenant_parent_is_never_authorized_or_returned(), test_denied_parent_does_not_change_child_result(), test_duplicate_children_and_parents_are_deduplicated_with_all_provenance(), test_expands_authorized_parent_and_preserves_child_citation() (+17 more)

### Community 26 - "IdentityRecord"
Cohesion: 0.12
Nodes (3): IdentityRecord, utc_z(), IdentityStore

### Community 27 - "DocumentResource"
Cohesion: 0.14
Nodes (9): DocumentResource, AuthorizationContractIntegrationTests, document(), evaluator(), principal(), AuthorizationOperationalTests, document(), evaluator() (+1 more)

### Community 28 - "auth"
Cohesion: 0.18
Nodes (23): auth(), _feedback(), test_completed_chat_query_flows_into_the_usage_aggregate(), test_denied_operational_read_is_a_safe_problem_with_correlation(), test_document_upload_flows_into_dashboard_document_and_ingestion_counts(), test_feedback_filter_and_page_walk_are_operationally_bounded(), test_feedback_replay_is_operationally_idempotent_and_review_has_one_item(), test_feedback_review_records_operational_correlation_metadata() (+15 more)

### Community 29 - "chat_api/test_contract_integration.py"
Cohesion: 0.11
Nodes (20): job_payload(), JobState, anonymous_conversation(), authenticated_conversation(), Clock, Executor, Maintenance, make_service() (+12 more)

### Community 30 - "DataClassification"
Cohesion: 0.16
Nodes (39): ModelGateway, DataClassification, EgressMode, FakeEmbedding, policy(), provider(), route(), test_approved_local_fallback_can_handle_internal_data() (+31 more)

### Community 31 - "chat_api/test_behavior_component.py"
Cohesion: 0.13
Nodes (20): AnswerState, QueryCompletion, anonymous_conversation(), authenticated_conversation(), Clock, Executor, Maintenance, make_service() (+12 more)

### Community 32 - "_evaluation_harness.py"
Cohesion: 0.22
Nodes (13): _Case, evaluate(), render_report(), _run_version(), answer_correctness(), citation_accuracy(), evaluate_case(), load_records() (+5 more)

### Community 33 - "GraphifyOperationalTests"
Cohesion: 0.17
Nodes (4): graph(), graphify_bin(), run_graphify(), GraphifyOperationalTests

### Community 34 - "key"
Cohesion: 0.11
Nodes (25): ScanVerdict, prepare_review_two(), publish(), clean_state(), test_manager_activates_provisioned_account(), test_manager_completes_two_review_publication(), test_manager_provisions_inactive_employee(), test_manager_uploads_into_quarantine() (+17 more)

### Community 35 - "chat_api/test_security_adversarial.py"
Cohesion: 0.16
Nodes (18): anonymous_conversation(), authenticated_conversation(), Clock, Executor, Maintenance, make_service(), principal(), public_document() (+10 more)

### Community 36 - "steps"
Cohesion: 0.15
Nodes (12): jobs, validate, name, on, pull_request, workflow_dispatch, run, uses (+4 more)

### Community 37 - "pytest"
Cohesion: 0.13
Nodes (17): validated(), test_clean_review_one_allows_processing(), test_processing_inherits_parent_acl(), test_approval_expiry_blocks_publication(), test_doc_is_rejected(), test_internal_upload_requires_department(), test_manifest_checksum_mismatch_blocks_staging(), test_manifest_count_mismatch_blocks_staging() (+9 more)

### Community 40 - "rules"
Cohesion: 0.17
Nodes (11): runbook, summary, groups, name, rules, severity, alert, annotations (+3 more)

### Community 41 - "knowledge/_baseline.py"
Cohesion: 0.13
Nodes (6): make_document(), make_version(), read(), task(), KnowledgeBehaviorTests, KnowledgeContractIntegrationTests

### Community 42 - "admin_api/test_behavior_component.py"
Cohesion: 0.16
Nodes (11): clean_state(), _prepare_review_two_without_index_ack(), test_manager_activates_provisioned_account(), test_manager_completes_two_review_publication(), test_manager_provisions_inactive_employee(), test_manager_uploads_into_quarantine(), test_publish_requires_acknowledged_index(), test_quarantined_document_is_not_readable() (+3 more)

### Community 43 - "ToolResult"
Cohesion: 0.10
Nodes (12): AuthorizedScope, GetDocumentMetadataArguments, PrincipalResolver, ReadAuthorizedChunkArguments, _safe_tool_result(), ScopeResolver, SearchDocumentsArguments, ToolBackend (+4 more)

### Community 44 - "lifecycle.py"
Cohesion: 0.06
Nodes (34): _acl_digest(), ApprovalBlocked, ApprovalRecord, _chunk_digest(), _chunk_state(), DerivedIndex, DerivedIndexFailure, DerivedIndexRecord (+26 more)

### Community 45 - "route"
Cohesion: 0.18
Nodes (10): global, resolve_timeout, receivers, name, route, group_by, group_interval, group_wait (+2 more)

### Community 46 - "CacheScope"
Cohesion: 0.12
Nodes (8): CacheScope, StaleScopeError, InMemoryChatRepository, JobCheckpoint, MessageRecord, _now(), QueryJob, QueryJobRepository

### Community 47 - "test_knowledge_database.py"
Cohesion: 0.26
Nodes (11): migration_text(), test_existing_db_contract_has_active_index_guard(), test_existing_db_contract_has_chunks_table(), test_existing_db_contract_has_composite_parent_fk(), test_existing_db_contract_has_document_versions_table(), test_existing_db_contract_has_documents_table(), test_existing_db_contract_has_immutable_version_uniqueness(), test_existing_db_contract_has_private_source_constraint() (+3 more)

### Community 48 - "chat_api/test_e2e_operational.py"
Cohesion: 0.15
Nodes (16): CitationArtifact, anonymous_conversation(), HttpExecutor, request(), sign_in(), test_http_anonymous_lifecycle_and_session_isolation(), test_http_authenticated_history_and_job_are_owner_only(), test_http_citation_preview_and_download_reauthorize_after_revocation() (+8 more)

### Community 49 - "active"
Cohesion: 0.19
Nodes (17): active(), staged(), test_acknowledged_index_is_still_not_active(), test_publishing_new_version_supersedes_previous_version(), test_review_one_requires_clean_scan(), test_revoke_active_version_removes_retrieval(), test_second_review_and_publish_make_version_active(), test_soft_delete_isolates_all_versions() (+9 more)

### Community 50 - "App.tsx"
Cohesion: 0.11
Nodes (29): ApiError, ApprovalRecord, AuditRecord, Conversation, ConversationMessage, Dashboard, DashboardMetric, DepartmentRecord (+21 more)

### Community 51 - "datasources"
Cohesion: 0.22
Nodes (8): apiVersion, datasources, access, editable, isDefault, name, type, url

### Community 52 - "monitoring/prometheus.yml"
Cohesion: 0.22
Nodes (8): global, evaluation_interval, scrape_interval, rule_files, scrape_configs, job_name, static_configs, targets

### Community 53 - "AuthorizationDecision"
Cohesion: 0.11
Nodes (18): AuthorizationDecision, allow(), authorize(), revoked(), revoked(), current_v2(), authorize(), authorize() (+10 more)

### Community 54 - "dependencies"
Cohesion: 0.22
Nodes (9): dependencies, react@18.3.1, react-dom@18.3.1, vite@6.3.5, @vitejs/plugin-react@4.6.0, react, react-dom, vite (+1 more)

### Community 55 - "App.test.tsx"
Cohesion: 0.40
Nodes (4): adminPrincipal, conversationResponse(), json(), principal

### Community 56 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, preview, test, test:watch, typecheck

### Community 57 - "ErrorNotice"
Cohesion: 0.18
Nodes (17): getApprovals(), getAuditEvents(), getDocuments(), AnswerDetails(), ApprovalsView(), load(), AuditView(), load() (+9 more)

### Community 58 - "admin.py"
Cohesion: 0.09
Nodes (75): AccessGrantRequest, AccessRequest, activate_user(), AdminApiState, approve_document_version(), _body(), _bump_policy_epoch(), _counts() (+67 more)

### Community 60 - "PromptDefinition"
Cohesion: 0.11
Nodes (6): SecureContextBuilder, default_prompt_registry(), _freeze(), PromptDefinition, PromptRegistry, PromptRegistryTests

### Community 61 - "tests/test_chat_api.py"
Cohesion: 0.14
Nodes (16): test_healthz_is_local_liveness_only(), test_identity_requires_bearer_credentials(), test_vercel_origin_can_use_cookie_authenticated_api(), anonymous_conversation(), authenticated_headers(), request(), StubExecutor, test_anonymous_submit_status_completion_and_history_are_session_scoped() (+8 more)

### Community 62 - "answer_baseline/test_security_adversarial.py"
Cohesion: 0.20
Nodes (15): _allow(), FakeModelGateway, _pipeline(), test_cross_tenant_evidence_is_absent_from_dense_bm25_and_answer(), test_direct_prompt_injection_is_denied_before_retrieval_and_model(), test_duplicate_and_unknown_citation_ids_do_not_duplicate_or_leak_metadata(), test_indirect_prompt_injection_is_removed_before_model_context(), test_malformed_model_output_fails_closed_without_denied_source_content() (+7 more)

### Community 64 - "orchestrator.py"
Cohesion: 0.08
Nodes (12): NoopQueryExecutor, AnswerSynthesizer, BoundedOrchestrator, _evidence_from_result(), _GraphState, OrchestrationOutcome, OrchestrationStatus, QueryRoute (+4 more)

### Community 86 - "answer_baseline/test_behavior_component.py"
Cohesion: 0.08
Nodes (27): AnswerModelGateway, AnswerResult, AnswerStatus, _authorization_matches(), DirectAnswerPipeline, _expired(), GeneratedAnswer, _LocalAnswerModel (+19 more)

### Community 87 - "orchestration_langgraph/test_security_adversarial.py"
Cohesion: 0.13
Nodes (20): Answerer, Backend, call(), Clock, gateway(), Policy, principal(), request() (+12 more)

### Community 91 - "AnswerCitation"
Cohesion: 0.43
Nodes (3): AnswerCitation, _utc_z(), test_answer_citation_serializes_typed_locator_and_bindings()

### Community 93 - "test_answer_citation_schema.py"
Cohesion: 0.33
Nodes (5): _CapturingModel, _Model, test_direct_answer_context_includes_authorized_parent_runtime(), test_real_hybrid_path_propagates_pdf_schema_end_to_end(), authorize()

### Community 94 - "_make_retriever"
Cohesion: 0.06
Nodes (58): AuthorizationEvaluator, InMemoryPolicyStore, PolicyEnforcementPoint, DenseRetriever, InMemoryDenseVectorIndex, HybridRetrievalConfig, InMemoryBM25Index, reciprocal_rank_fusion() (+50 more)

### Community 95 - "ModelPolicy"
Cohesion: 0.24
Nodes (14): ModelPolicy, test_mapping_loads_versioned_policy_without_credentials(), test_policy_rejects_credential_fields(), test_route_task_mismatch_is_rejected_by_policy(), mapping(), test_access_token_field_is_rejected(), test_exact_api_key_field_is_rejected(), test_fallback_route_task_mismatch_is_rejected() (+6 more)

### Community 96 - "inherit_acl"
Cohesion: 0.27
Nodes (4): inherit_acl(), make_child(), make_parent(), KnowledgeSecurityAdversarialTests

### Community 97 - "IdentityError"
Cohesion: 0.12
Nodes (15): IdentityError, rate_limited(), AuthenticationService, IdentityErrorPassthrough, now_utc(), make_service(), test_expired_session_is_rejected(), test_invalid_password_is_safe_auth_error() (+7 more)

### Community 98 - "test_tool_gateway.py"
Cohesion: 0.16
Nodes (21): _Backend, _call(), _Clock, _gateway(), _Policy, _principal(), _Resolvers, test_backend_exception_is_unavailable_without_raw_error() (+13 more)

### Community 99 - "AnswerDraft"
Cohesion: 0.27
Nodes (19): _Answerer, _Clock, _evidence(), _orchestrator(), _request(), test_answerer_error_is_returned_as_safe_error(), test_complex_route_splits_subqueries_and_preserves_bound(), test_custom_limits_cannot_weaken_contract_caps() (+11 more)

### Community 100 - "AuthenticatedPrincipal"
Cohesion: 0.08
Nodes (17): AuthenticatedPrincipal, _answer_citation(), _citation(), _cosine(), DenseEvidence, DenseRetrievalResult, SourceFetchResult, _uuid() (+9 more)

### Community 102 - "load_validated_records"
Cohesion: 0.20
Nodes (13): evaluation_snapshot(), load_validated_records(), test_all_golden_cases_run_through_v1_v3(), test_allowed_answer_has_no_unauthorized_retrieval_marker(), test_answered_case_keeps_citation_version_and_tenant_binding(), test_dataset_contains_permission_negative_and_cross_tenant_cases(), test_empty_query_is_denied_before_retrieval(), test_model_failure_returns_error_without_source_or_answer() (+5 more)

### Community 103 - "IngestionService"
Cohesion: 0.11
Nodes (21): IngestionService, _active_document(), _principal(), _retriever(), test_dense_retrieval_returns_authorized_current_chunk_only(), test_explicit_deny_candidates_are_not_exposed(), test_forbidden_source_fetch_is_redacted_without_content_or_citation(), test_active_retrieval_to_evidence_verification_succeeds() (+13 more)

### Community 104 - "ModelProviderError"
Cohesion: 0.15
Nodes (9): ModelProviderError, RankedDocument, RerankerResult, FakeReranker, test_ranked_document_preserves_identifier_and_score(), test_reranker_result_requires_ranked_documents(), ScriptedReranker, test_reranker_gateway_contract_passes_request_route_and_timeout() (+1 more)

### Community 106 - "InMemoryIdentityStore"
Cohesion: 0.09
Nodes (8): DepartmentRecord, normalize_roles(), Role, SessionRecord, hash_secret(), InMemoryIdentityStore, verify_secret(), test_noncanonical_role_cannot_create_identity()

### Community 107 - "ToolResult"
Cohesion: 0.20
Nodes (19): OrchestrationRequest, ToolResult, test_tool_result_does_not_accept_unsafe_error_code(), Answerer, Clock, evidence(), request(), run() (+11 more)

### Community 108 - "ingestion/_baseline.py"
Cohesion: 0.15
Nodes (13): graph_labels(), read(), task(), test_task_and_handoff_keep_ingestion_provider_neutral(), test_audit_event_is_structured_without_source_checksum(), test_changed_checksum_cannot_enter_retry(), test_cleanup_failure_blocks_maintenance_recovery_then_recovery_succeeds(), test_end_to_end_clean_upload_becomes_retrievable_only_after_publish() (+5 more)

### Community 110 - "backend_boot/_baseline.py"
Cohesion: 0.05
Nodes (16): assignment(), backend_boot_task(), calls(), compile_sources_without_writes(), function(), literal(), pyproject(), read() (+8 more)

### Community 111 - "reset"
Cohesion: 0.06
Nodes (23): reset_state(), reset_state(), reset(), clean_state(), clean_state(), clean_state(), test_anonymous_is_denied_dashboard_and_feedback(), test_feedback_review_is_private_bounded_and_replay_does_not_duplicate() (+15 more)

### Community 112 - "rag_v4_citation/test_e2e_operational.py"
Cohesion: 0.16
Nodes (20): _make_parent_child_retriever(), test_hybrid_runtime_expands_authorized_parent_after_reranking(), test_runtime_parent_is_added_after_child_rerank(), test_policy_epoch_is_propagated_to_ranked_and_expanded_citations(), test_runtime_parent_context_is_separate_from_ranked_evidence(), _allow(), _answer(), _locator() (+12 more)

### Community 113 - "EvidenceVerifier"
Cohesion: 0.22
Nodes (18): EvidenceVerifier, VerificationRequest, allow_active(), citation(), test_authorization_callback_exception_fails_closed(), test_cross_tenant_evidence_is_denied_before_authorizer_invocation(), unexpected(), test_denied_result_does_not_leak_source_text() (+10 more)

### Community 114 - "answer_baseline/test_contract_integration.py"
Cohesion: 0.19
Nodes (15): _allow(), RecordingModel, RecordingRetriever, _setup(), test_citation_authorization_rejects_document_mismatch(), test_citation_authorization_rejects_non_active_status(), test_citation_authorization_rejects_non_current_version(), test_citation_authorization_rejects_revoked_source() (+7 more)

### Community 115 - "Claim"
Cohesion: 0.35
Nodes (13): Claim, allow_active(), citation(), test_authorizer_must_attest_active_current_and_not_revoked(), test_citation_and_source_span_are_immutable(), test_conflicting_numeric_source_spans_are_disclosed(), test_denial_result_does_not_leak_source_text(), test_stale_version_is_denied_even_when_text_matches() (+5 more)

### Community 116 - "answer_baseline/test_e2e_operational.py"
Cohesion: 0.17
Nodes (16): _allow(), FailingEmbedder, FailingReranker, FakeAnswerGateway, _setup(), test_operational_abstention_is_insufficient_evidence(), test_operational_conflicting_evidence_is_not_harmonized(), test_operational_denied_content_never_appears_in_failure_result() (+8 more)

### Community 117 - "to_qdrant_payload"
Cohesion: 0.35
Nodes (11): to_qdrant_payload(), make_child(), make_parent(), test_acl_inheritance_populates_child_reference(), test_parent_child_contract_keeps_same_scope(), test_qdrant_projection_contains_index_state(), test_qdrant_projection_contains_scope_keys(), test_qdrant_projection_does_not_store_chunk_text() (+3 more)

### Community 118 - "test_knowledge_security.py"
Cohesion: 0.38
Nodes (12): make_child(), make_parent(), test_conflicting_child_acl_is_denied(), test_document_mismatch_is_denied(), test_matching_child_acl_is_preserved(), test_missing_child_acl_is_inherited(), test_qdrant_projection_does_not_claim_authority(), test_qdrant_projection_keeps_tenant_boundary() (+4 more)

### Community 119 - "guardrails/__init__.py"
Cohesion: 0.15
Nodes (6): _luhn_valid(), redact_sensitive_data(), redact_card(), RedactionResult, ToolDecision, validate_tool_request()

### Community 120 - "test_answer_baseline.py"
Cohesion: 0.32
Nodes (10): _authorization(), authorize(), FakeModelGateway, _pipeline(), test_direct_answer_returns_insufficient_without_calling_model_when_no_match(), test_direct_answer_returns_partial_for_mixed_claims(), test_direct_answer_returns_supported_answer_and_authorized_citation(), test_guardrail_failure_fails_closed_before_model_call() (+2 more)

### Community 121 - "normalize_user_input"
Cohesion: 0.17
Nodes (3): normalize_user_input(), GuardrailBehaviorTests, GuardrailSecurityAdversarialTests

### Community 122 - "ScopedCacheKey"
Cohesion: 0.07
Nodes (10): _CacheEntry, _component(), _digest(), _identifier(), InvalidationReason, ScopedCacheAdapter, ScopedCacheKey, _serialized_size() (+2 more)

### Community 123 - "orchestration_langgraph/test_contract_integration.py"
Cohesion: 0.18
Nodes (16): Backend, call(), Clock, gateway(), Policy, principal(), Resolvers, test_chunk_read_contract_accepts_only_chunk_id_shape() (+8 more)

### Community 124 - "validate_output"
Cohesion: 0.26
Nodes (8): _citation(), detect_prompt_injection(), GuardrailResult, _inspect_text(), _normalize_text(), _sensitive_terms(), _terms(), validate_output()

### Community 125 - "DocumentVersionMetadata"
Cohesion: 0.10
Nodes (15): DocumentMetadata, DocumentVersionMetadata, test_active_chunk_requires_acl_metadata(), test_chunk_accepts_source_provenance(), test_chunk_rejects_reversed_pages(), test_chunk_rejects_self_parent(), test_document_metadata_is_tenant_scoped(), test_document_version_identity_is_stable() (+7 more)

### Community 126 - "knowledge/models.py"
Cohesion: 0.08
Nodes (19): DOCXLocator, _ImmutableModel, PDFLocator, SourceSpan, XLSXLocator, _valid_locator(), Citation, _AnswerModel (+11 more)

### Community 127 - "make_manifest"
Cohesion: 0.19
Nodes (14): ScanReport, make_manifest(), test_rejected_scan_is_terminal_and_not_retrievable(), test_rejected_version_cannot_be_retrieved(), test_scan_rejection_is_not_retryable(), test_malware_scan_is_terminal(), test_failed_new_publication_preserves_previous_active_version(), test_job_contract_keeps_attempt_and_tenant_scope() (+6 more)

### Community 130 - "orchestration/context.py"
Cohesion: 0.17
Nodes (7): AssembledContext, ContextLimitError, estimate_tokens(), PromptMessage, _render_evidence(), _safe_text(), _safe_value()

### Community 131 - "evidence/test_behavior_component.py"
Cohesion: 0.27
Nodes (14): EvidenceRecord, SourceSpan, citation(), test_authorization_callback_error_fails_closed(), test_current_active_version_is_required_by_authorization_attestation(), test_negation_mismatch_is_conflicting_not_supported(), test_numeric_mismatch_is_conflicting_not_supported(), test_repeated_verification_is_deterministic() (+6 more)

### Community 132 - "orchestration_langgraph/test_behavior_component.py"
Cohesion: 0.25
Nodes (16): AnswerDraft, Answerer, Clock, evidence(), request(), run(), test_compiles_a_state_graph_with_expected_nodes(), test_complex_loop_caps_subqueries_and_tool_calls_at_four() (+8 more)

### Community 134 - "cache_memory/test_e2e_operational.py"
Cohesion: 0.13
Nodes (18): ConversationMemory, ConversationMessage, test_contract_fake_repository_implements_provider_neutral_memory_boundary(), Clock, FakeInvalidationBus, FakeMemoryRepository, make_key(), make_scope() (+10 more)

### Community 135 - "cache_memory/test_security_adversarial.py"
Cohesion: 0.36
Nodes (12): make_key(), make_scope(), test_anonymous_revocation_isolated_to_one_session_and_fails_closed(), test_broad_scope_cannot_replay_after_a_narrow_document_change(), test_cache_key_excludes_queries_model_inputs_and_conversation_identifiers(), test_changed_document_version_cannot_repopulate_an_old_cache_entry(), test_cross_principal_cache_read_is_a_fail_closed_miss(), test_cross_scope_conversation_read_cannot_be_recovered_by_matching_id() (+4 more)

### Community 137 - "rag_v4_citation/test_security_adversarial.py"
Cohesion: 0.33
Nodes (11): _child(), _parent(), _principal(), test_cross_document_parent_is_not_expanded(), test_cross_tenant_parent_is_not_even_sent_to_authorizer(), test_cross_version_parent_is_not_expanded(), test_explicit_parent_deny_does_not_remove_authorized_child(), test_inactive_parent_status_is_not_expanded() (+3 more)

### Community 138 - "main.py"
Cohesion: 0.08
Nodes (7): get_settings(), Settings, RuntimeDatabaseUnavailable, healthz(), identity_error_handler(), runtime_database_error_handler(), test_http_chat_reaches_local_rag_and_returns_verified_citation()

### Community 139 - "ingestion/test_security_adversarial.py"
Cohesion: 0.13
Nodes (17): make_chunks(), quarantine(), test_child_acl_broadening_is_denied(), test_tenant_scope_isolation_is_fail_closed(), RuntimeFailureOnRemove, service_with_index(), test_approval_expiry_blocks_processing(), test_review_one_and_processing_require_parent_acl() (+9 more)

### Community 140 - "ChatService"
Cohesion: 0.18
Nodes (9): ActorKind, AnonymousSession, ChatActor, ChatService, ConversationRecord, ConversationRepository, ConversationView, _error() (+1 more)

### Community 141 - "test_cache_memory.py"
Cohesion: 0.28
Nodes (12): Clock, response_key(), scope(), test_cache_delete_is_explicit(), test_cache_expires_and_rejects_unbounded_ttl_or_value(), test_cache_key_contains_security_scope_but_not_raw_query(), test_cache_requires_exact_current_scope_and_isolates_tenant_and_principal(), test_conversation_delete_removes_body_and_blocks_recreation_in_old_scope() (+4 more)

### Community 142 - "InMemoryScopedCache"
Cohesion: 0.22
Nodes (14): InMemoryScopedCache, test_cache_invalidation_hooks_remove_only_matching_scope(), Clock, make_key(), make_scope(), test_broad_acl_invalidation_removes_all_versions_in_one_tenant(), test_cache_expires_at_the_exact_ttl_deadline(), test_cache_rejects_invalid_ttl_and_oversize_values() (+6 more)

### Community 143 - "test_authorization.py"
Cohesion: 0.40
Nodes (15): document(), evaluator(), principal(), test_acl_can_assign_employee_and_explicit_deny_wins_for_chairman(), test_anonymous_is_public_only(), test_chairman_is_read_only(), test_conversation_body_is_owner_only(), test_conversation_requires_conversation_resource() (+7 more)

### Community 144 - "eval_001_runner.py"
Cohesion: 0.11
Nodes (10): HybridRetrievalResult, _aggregate(), _AnswerModel, _DenseAsHybrid, _mean(), _percentile(), _principal(), _RrfOnly (+2 more)

### Community 145 - "IdentityContractTests"
Cohesion: 0.10
Nodes (5): read(), task(), tasks(), IdentityOperationalTests, IdentitySecurityTests

### Community 146 - "build_secure_context"
Cohesion: 0.14
Nodes (6): build_secure_context(), RetrievedEvidence, SecureContextBuilderTests, PromptOperationalTests, PromptSecurityAdversarialTests, test_secure_context_escapes_parent_prompt_injection_as_untrusted_content()

### Community 147 - "evidence/__init__.py"
Cohesion: 0.16
Nodes (10): CitationRecord, ClaimVerification, _is_negative(), _numeric_conflict(), _numeric_terms(), _relation(), _terms(), VerificationOutcome (+2 more)

### Community 148 - "admin_api/test_security_adversarial.py"
Cohesion: 0.14
Nodes (13): add_user(), test_acl_explicit_deny_overrides_employee_read_allow(), clean_state(), test_acl_explicit_deny_overrides_employee_read_allow(), test_admin_results_do_not_expose_conversation_or_password_fields(), test_anonymous_cannot_upload(), test_chairman_cannot_approve(), test_chairman_cannot_upload() (+5 more)

### Community 149 - "json"
Cohesion: 0.09
Nodes (8): dfs(), json_blocks(), test_dashboard_has_api_and_security_panels(), test_dashboard_is_valid_json(), compose_config_result(), task(), tasks(), test_rag002_task_registry_keeps_retrieval_validation_and_scope()

### Community 152 - "cache_memory/test_contract_integration.py"
Cohesion: 0.32
Nodes (11): make_key(), make_scope(), test_contract_acl_change_can_target_one_principal_and_version(), test_contract_delete_event_invalidates_matching_scope_without_cross_tenant_reach(), test_contract_document_change_invalidates_broad_scope_and_selected_version(), test_contract_invalid_event_shapes_fail_closed_at_the_boundary(), test_contract_memory_read_requires_the_authoritative_current_scope(), test_contract_policy_epoch_change_requires_a_new_scope_for_reuse() (+3 more)

### Community 153 - "evidence/test_contract_integration.py"
Cohesion: 0.20
Nodes (7): allow_active(), citation(), test_chat_001_owns_preview_download_reauthorization_recheck(), test_duplicate_evidence_ids_are_a_malformed_fail_closed_result(), authorize(), test_supported_result_round_trips_tenant_document_version_and_span(), test_verifier_requires_a_server_supplied_authorization_callback()

### Community 156 - "db/runtime.py"
Cohesion: 0.11
Nodes (16): _utc_z(), _answer_status(), _as_utc(), _department_uuid(), _jsonb(), _membership_uuid(), normalize_database_url(), _parse_uuid() (+8 more)

### Community 158 - "feedback/service.py"
Cohesion: 0.15
Nodes (7): FeedbackRecord, FeedbackRepository, FeedbackReview, FeedbackService, InMemoryFeedbackRepository, test_feedback_replay_is_idempotent_but_tenant_bound(), test_feedback_review_projection_has_no_actor_comment_or_body()

### Community 159 - "model/test_security_adversarial.py"
Cohesion: 0.16
Nodes (13): ModelEgressDenied, ModelUnavailable, provider(), test_provider_allowlist_is_required(), test_provider_id_is_required(), gateway_for(), test_denied_primary_cannot_use_denied_fallback(), test_egress_denial_does_not_echo_input() (+5 more)

### Community 160 - "ingestion/test_behavior_component.py"
Cohesion: 0.22
Nodes (7): test_empty_processing_input_is_rejected(), test_new_active_version_supersedes_previous_version(), test_publish_activates_authoritative_version_and_chunks(), test_review_one_requires_clean_scan(), test_second_review_is_required_after_index_ack(), test_staging_is_not_retrievable_before_ack_and_publish(), test_upload_is_quarantined_and_invisible()

### Community 161 - "App"
Cohesion: 0.24
Nodes (16): clearAccessToken(), createConversation(), signOut(), waitForQueryCompletion(), App(), handleFeedback(), handlePreview(), handleSignOut() (+8 more)

### Community 162 - "ModelRoute"
Cohesion: 0.13
Nodes (14): RerankerRequest, route(), ModelRoute, ProviderPolicy, DeterministicEmbeddingAdapter, DeterministicRerankerAdapter, _gateway(), _gateway() (+6 more)

### Community 170 - "key"
Cohesion: 0.10
Nodes (33): key(), upload(), test_account_response_does_not_return_password(), test_approval_schema_requires_explicit_stage(), test_existing_sign_in_contract_remains_under_auth_prefix(), test_job_status_contains_redacted_progress_only(), test_mutating_post_requires_idempotency_key(), test_problem_response_uses_safe_media_type_for_anonymous_admin_call() (+25 more)

### Community 172 - "new_service"
Cohesion: 0.18
Nodes (19): new_service(), test_audit_sink_receives_lifecycle_events_without_content(), test_failed_maintenance_can_be_recovered_after_cleanup(), test_non_retryable_failure_is_terminal(), test_only_one_maintenance_window_is_active(), test_publication_failure_keeps_previous_active_version(), test_retry_is_bounded_and_preserves_checksum(), test_retry_with_changed_checksum_is_denied() (+11 more)

### Community 175 - "request"
Cohesion: 0.12
Nodes (28): request(), test_acl_update_advances_policy_epoch(), test_activation_allows_follow_up_sign_in(), test_admin_mutations_emit_privacy_safe_audit_events(), test_anonymous_is_denied_management_api(), test_chairman_is_denied_management_api(), test_employee_is_denied_management_api(), test_manager_completes_http_lifecycle_with_worker_boundary() (+20 more)

### Community 177 - "DurableChatRepository"
Cohesion: 0.20
Nodes (3): CheckpointRepository, DurableChatRepository, QueryExecutor

### Community 178 - "ndcg_at_k"
Cohesion: 0.42
Nodes (10): mean_reciprocal_rank(), ndcg_at_k(), recall_at_k(), source_key(), _span(), _spans(), test_rag_002_regression_metrics_on_tiny_in_memory_corpus(), metrics() (+2 more)

### Community 182 - "observability/context.py"
Cohesion: 0.38
Nodes (4): _header(), _new_traceparent(), _valid_traceparent(), test_correlation_context_preserves_valid_headers_and_creates_child()

### Community 183 - "DashboardView"
Cohesion: 0.67
Nodes (4): getDashboard(), DashboardView(), load(), metricValue()

### Community 186 - "signIn"
Cohesion: 0.67
Nodes (4): setAccessToken(), signIn(), AuthView(), submit()

## Knowledge Gaps
- **1 isolated node(s):** `enterprise-agentic-rag-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 935 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **66 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AuthenticatedPrincipal` connect `AuthenticatedPrincipal` to `rag_v4_citation/test_security_adversarial.py`, `ChatService`, `identity.py`, `dense.py`, `test_authorization.py`, `eval_001_runner.py`, `InMemoryPolicyStore`, `rag_v4_citation/test_contract_integration.py`, `IdentityRecord`, `DocumentResource`, `chat_api/test_contract_integration.py`, `chat_api/test_behavior_component.py`, `chat_api/test_security_adversarial.py`, `admin.py`, `answer_baseline/test_behavior_component.py`, `orchestration_langgraph/test_security_adversarial.py`, `_make_retriever`, `IdentityError`, `test_tool_gateway.py`, `IngestionService`, `InMemoryIdentityStore`, `rag_v4_citation/test_e2e_operational.py`, `orchestration_langgraph/test_contract_integration.py`, `knowledge/models.py`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Are the 45 inferred relationships involving `IngestionService` (e.g. with `reset_state()` and `test_active_retrieval_to_evidence_verification_succeeds()`) actually correct?**
  _`IngestionService` has 45 INFERRED edges - model-reasoned connections that need verification._
- **What connects `enterprise-agentic-rag-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `audit.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10931174089068826 - nodes in this community are weakly interconnected._
- **Why does `IngestionService` connect `IngestionService` to `AuthenticatedPrincipal`, `pytest`, `ingestion/test_security_adversarial.py`, `lifecycle.py`, `new_service`, `reset`, `rag_v4_citation/test_e2e_operational.py`, `active`, `eval_001_runner.py`, `answer_baseline/test_security_adversarial.py`, `_make_retriever`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Are the 47 inferred relationships involving `DataClassification` (e.g. with `ModelEgressDenied` and `ModelGateway`) actually correct?**
  _`DataClassification` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Should `compose` be split into smaller, more focused modules?**
  _Cohesion score 0.06599326599326599 - nodes in this community are weakly interconnected._