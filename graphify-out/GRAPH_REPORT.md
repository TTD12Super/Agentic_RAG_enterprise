# Graph Report - enterprise-agentic-rag-harness  (2026-11-12)

## Corpus Check
- 294 files · ~257,663 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 68 file(s) not represented in the graph (top: (none) 53, .toml 9, .example 2)

## Summary
- 4135 nodes · 12588 edges · 208 communities (127 shown, 81 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 865 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7a9ccdc2`
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
- InMemoryScopedCache
- EgressMode
- QueryJob
- app/rag/__init__.py
- postgres
- postgres
- PromptDefinition
- package.json
- InMemoryIdentityStore
- evaluator
- core/chat.py
- compilerOptions
- InMemoryConversationMemory
- ModelProviderError
- api/chat.py
- _common.py
- AuthorizationEvaluator
- chat_api/test_contract_integration.py
- DataClassification
- chat_api/test_behavior_component.py
- _make_retriever
- GraphifyOperationalTests
- key
- chat_api/test_security_adversarial.py
- steps
- rag/runtime.py
- ContractIntegrationTests
- SecurityAdversarialTests
- rules
- identity/service.py
- BackendBootstrapBehaviorTests
- ToolResult
- Icon
- route
- feedback/service.py
- test_knowledge_database.py
- chat_api/test_e2e_operational.py
- admin_api/test_behavior_component.py
- App.tsx
- datasources
- monitoring/prometheus.yml
- lifecycle.py
- client.ts
- CitationArtifact
- ProviderPolicy
- request
- admin.py
- upload
- pathlib
- tests/test_chat_api.py
- auth
- orchestration/context.py
- vite-env.d.ts
- sync_graph.sh
- migrate.sh
- inspect_untrusted_content
- enterprise-agentic-rag-backend
- answer_baseline/test_behavior_component.py
- orchestration_langgraph/test_security_adversarial.py
- unittest
- active
- test_chat_stream.py
- inherit_acl
- knowledge/_baseline.py
- FrontendE2EOperationalTests
- test_tool_gateway.py
- AnswerDraft
- identity.py
- _make_case
- IngestionService
- authorization/test_behavior_component.py
- IdentityError
- test_sample_documents.py
- ToolResult
- backend_boot/_baseline.py
- test_authorization.py
- read
- reset
- to_qdrant_payload
- AuthorizationDecision
- answer_baseline/test_contract_integration.py
- BoundedOrchestrator
- answer_baseline/test_e2e_operational.py
- read_frontend
- eval_001_runner.py
- PromptContractIntegrationTests
- cache_memory/test_security_adversarial.py
- App.test.tsx
- cache_memory/test_contract_integration.py
- orchestration_langgraph/test_contract_integration.py
- Claim
- test_customer_api_e2e.py
- new_service
- run_local_guardrail_pipeline
- quarantine
- manifest.json
- evidence/test_contract_integration.py
- orchestration_langgraph/test_behavior_component.py
- KnowledgeOperationalTests
- ConversationMessage
- AuthorizationOperationalTests
- ingestion/_baseline.py
- test_knowledge_security.py
- ndcg_at_k
- tree
- ChatService
- test_cache_memory.py
- InfrastructureSecurityTests
- PromptBehaviorComponentTests
- BackendBootstrapContractTests
- read
- build_secure_context
- expand_parent_context
- AnswerCitation
- SecureContextBuilder
- app/evidence/__init__.py
- InMemoryScopedCache
- answer_baseline/test_security_adversarial.py
- validate_output
- vercel.json
- db/runtime.py
- ChunkMetadata
- App
- BehaviorComponentTests
- pytest
- admin_api/test_contract_integration.py
- auth
- test_customer_frontend_static.py
- AnswerModelGateway
- test_answer_citation_schema.py
- hashlib
- _RequestModel
- json
- tests/test_dashboard_api.py
- UsersView
- env.py

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
  tests/integration/test_answer_baseline.py → backend/app/evidence/verifier.py
- `authorize()` --calls--> `AuthorizationDecision`  [INFERRED]
  tests/integration/test_answer_citation_schema.py → backend/app/evidence/verifier.py
- `authorize()` --calls--> `AuthorizationDecision`  [INFERRED]
  tests/qa/answer_baseline/test_contract_integration.py → backend/app/evidence/verifier.py
- `authorize()` --calls--> `AuthorizationDecision`  [INFERRED]
  tests/qa/answer_baseline/test_e2e_operational.py → backend/app/evidence/verifier.py
- `deny()` --calls--> `AuthorizationDecision`  [INFERRED]
  tests/qa/answer_baseline/test_e2e_operational.py → backend/app/evidence/verifier.py

## Import Cycles
- 2-file cycle: `backend/app/api/admin.py -> backend/app/api/identity.py -> backend/app/api/admin.py`
- 2-file cycle: `backend/app/api/admin.py -> backend/app/api/chat.py -> backend/app/api/admin.py`
- 2-file cycle: `backend/app/api/chat.py -> backend/app/api/identity.py -> backend/app/api/chat.py`
- 3-file cycle: `backend/app/api/admin.py -> backend/app/api/identity.py -> backend/app/api/chat.py -> backend/app/api/admin.py`
- 3-file cycle: `backend/app/api/admin.py -> backend/app/api/chat.py -> backend/app/api/identity.py -> backend/app/api/admin.py`

## Communities (208 total, 81 thin omitted)

### Community 0 - "audit.py"
Cohesion: 0.06
Nodes (30): reset_state(), _maintenance_probe(), reset_state(), identity_error_handler(), append_audit_event(), AuditEvent, AuditSink, AuditSinkUnavailable (+22 more)

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
Cohesion: 0.10
Nodes (6): require_all(), section(), BehaviorComponentTests, ContractIntegrationTests, E2EOperationalTests, SecurityAdversarialTests

### Community 6 - "read"
Cohesion: 0.06
Nodes (7): dashboard(), read(), task(), MonitoringBehaviorTests, MonitoringContractTests, MonitoringOperationalTests, MonitoringSecurityTests

### Community 7 - "ModelPolicy"
Cohesion: 0.19
Nodes (15): ModelPolicy, test_mapping_loads_versioned_policy_without_credentials(), test_policy_rejects_credential_fields(), mapping(), test_embedding_route_task_is_checked(), test_policy_version_is_required(), test_access_token_field_is_rejected(), test_exact_api_key_field_is_rejected() (+7 more)

### Community 8 - "read"
Cohesion: 0.08
Nodes (5): graph(), read(), GraphifyBehaviorTests, GraphifyContractTests, GraphifySecurityTests

### Community 9 - "otel-collector-config.yaml"
Cohesion: 0.06
Nodes (32): action, key, actions, send_batch_size, timeout, exporters, prometheus, endpoint (+24 more)

### Community 10 - "prometheus"
Cohesion: 0.06
Nodes (30): command, image, ports, read_only, security_opt, volumes, depends_on, image (+22 more)

### Community 12 - "InMemoryScopedCache"
Cohesion: 0.09
Nodes (7): _CacheEntry, _component(), ScopedCacheAdapter, ScopedCacheKey, _serialized_size(), FakeProvider, test_provider_neutral_fake_preserves_exact_scope_checks()

### Community 13 - "EgressMode"
Cohesion: 0.12
Nodes (34): ModelEgressDenied, EgressMode, graph_labels(), policy(), provider(), route(), run_graph_query(), ScriptedEmbedding (+26 more)

### Community 14 - "QueryJob"
Cohesion: 0.15
Nodes (5): CacheScope, InMemoryChatRepository, JobCheckpoint, QueryJob, QueryJobRepository

### Community 15 - "app/rag/__init__.py"
Cohesion: 0.07
Nodes (39): PDFLocator, SourceSpan, PreparedAnswer, Citation, DenseEvidence, DenseRetrievalResult, HybridEvidence, HybridRetrievalResult (+31 more)

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

### Community 20 - "InMemoryIdentityStore"
Cohesion: 0.11
Nodes (6): DepartmentRecord, IdentityRecord, normalize_roles(), Role, InMemoryIdentityStore, test_noncanonical_role_cannot_create_identity()

### Community 21 - "evaluator"
Cohesion: 0.41
Nodes (4): AuthorizationSecurityAdversarialTests, document(), evaluator(), principal()

### Community 22 - "core/chat.py"
Cohesion: 0.08
Nodes (14): ActorKind, AnonymousSession, CheckpointRepository, _citation_expired(), ConversationRecord, ConversationRepository, ConversationSummary, ConversationView (+6 more)

### Community 23 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+10 more)

### Community 24 - "InMemoryConversationMemory"
Cohesion: 0.10
Nodes (4): InvalidationEvent, ConversationMemoryRepository, InMemoryConversationMemory, FakeMemoryRepository

### Community 25 - "ModelProviderError"
Cohesion: 0.14
Nodes (5): ModelProviderError, RankedDocument, FakeReranker, test_ranked_document_preserves_identifier_and_score(), ScriptedReranker

### Community 26 - "api/chat.py"
Cohesion: 0.17
Nodes (20): _anonymous_token(), _body(), _context(), create_conversation(), download_citation(), FeedbackRequest, get_conversation(), get_query_completion() (+12 more)

### Community 27 - "_common.py"
Cohesion: 0.21
Nodes (3): load_frontend_json(), read(), FrontendContractIntegrationTests

### Community 28 - "AuthorizationEvaluator"
Cohesion: 0.07
Nodes (19): Action, AuthorizationDenied, AuthorizationEvaluator, deny(), Classification, Decision, DocumentResource, Effect (+11 more)

### Community 29 - "chat_api/test_contract_integration.py"
Cohesion: 0.11
Nodes (20): job_payload(), JobState, anonymous_conversation(), authenticated_conversation(), Clock, Executor, Maintenance, make_service() (+12 more)

### Community 30 - "DataClassification"
Cohesion: 0.12
Nodes (47): ModelGateway, ModelUnavailable, DataClassification, route(), ModelTask, FakeEmbedding, policy(), provider() (+39 more)

### Community 31 - "chat_api/test_behavior_component.py"
Cohesion: 0.15
Nodes (19): AnswerState, anonymous_conversation(), authenticated_conversation(), Clock, Executor, Maintenance, make_service(), principal() (+11 more)

### Community 32 - "_make_retriever"
Cohesion: 0.05
Nodes (59): _citation(), InMemoryDenseVectorIndex, _uuid(), _valid_locator(), _VectorRecord, HybridRetrievalConfig, HybridRetriever, InMemoryBM25Index (+51 more)

### Community 33 - "GraphifyOperationalTests"
Cohesion: 0.16
Nodes (4): graphify_bin(), run_graphify(), GraphifyOperationalTests, run_graph_query()

### Community 34 - "key"
Cohesion: 0.10
Nodes (38): ScanVerdict, key(), prepare_review_two(), publish(), test_manager_activates_provisioned_account(), test_manager_completes_two_review_publication(), test_manager_provisions_inactive_employee(), test_manager_uploads_into_quarantine() (+30 more)

### Community 35 - "chat_api/test_security_adversarial.py"
Cohesion: 0.15
Nodes (20): QueryCompletion, anonymous_conversation(), authenticated_conversation(), Clock, Executor, Maintenance, make_service(), principal() (+12 more)

### Community 36 - "steps"
Cohesion: 0.15
Nodes (12): jobs, validate, name, on, pull_request, workflow_dispatch, run, uses (+4 more)

### Community 37 - "rag/runtime.py"
Cohesion: 0.09
Nodes (17): DOCXLocator, _ImmutableModel, XLSXLocator, EmbeddingAdapter, EmbeddingRequest, EmbeddingResult, RerankerAdapter, RerankerResult (+9 more)

### Community 40 - "rules"
Cohesion: 0.17
Nodes (11): runbook, summary, groups, name, rules, severity, alert, annotations (+3 more)

### Community 41 - "identity/service.py"
Cohesion: 0.11
Nodes (3): SessionRecord, utc_z(), IdentityStore

### Community 42 - "BackendBootstrapBehaviorTests"
Cohesion: 0.19
Nodes (4): calls(), function(), literal(), BackendBootstrapBehaviorTests

### Community 43 - "ToolResult"
Cohesion: 0.08
Nodes (16): _evidence_from_result(), GetDocumentMetadataArguments, PrincipalResolver, ReadAuthorizedChunkArguments, _safe_tool_result(), ScopeResolver, SearchDocumentsArguments, ToolBackend (+8 more)

### Community 44 - "Icon"
Cohesion: 0.13
Nodes (23): getAuditEvents(), getFeedback(), setAccessToken(), signIn(), submitAccessRequest(), AdminGuardView(), AuditView(), load() (+15 more)

### Community 45 - "route"
Cohesion: 0.18
Nodes (10): global, resolve_timeout, receivers, name, route, group_by, group_interval, group_wait (+2 more)

### Community 46 - "feedback/service.py"
Cohesion: 0.15
Nodes (7): FeedbackRecord, FeedbackRepository, FeedbackReview, FeedbackService, InMemoryFeedbackRepository, test_feedback_replay_is_idempotent_but_tenant_bound(), test_feedback_review_projection_has_no_actor_comment_or_body()

### Community 47 - "test_knowledge_database.py"
Cohesion: 0.26
Nodes (11): migration_text(), test_existing_db_contract_has_active_index_guard(), test_existing_db_contract_has_chunks_table(), test_existing_db_contract_has_composite_parent_fk(), test_existing_db_contract_has_document_versions_table(), test_existing_db_contract_has_documents_table(), test_existing_db_contract_has_immutable_version_uniqueness(), test_existing_db_contract_has_private_source_constraint() (+3 more)

### Community 48 - "chat_api/test_e2e_operational.py"
Cohesion: 0.23
Nodes (15): anonymous_conversation(), HttpExecutor, request(), sign_in(), test_http_anonymous_lifecycle_and_session_isolation(), test_http_authenticated_history_and_job_are_owner_only(), test_http_citation_preview_and_download_reauthorize_after_revocation(), test_http_deadline_failure_is_safe_and_has_no_answer() (+7 more)

### Community 49 - "admin_api/test_behavior_component.py"
Cohesion: 0.16
Nodes (11): clean_state(), _prepare_review_two_without_index_ack(), test_manager_activates_provisioned_account(), test_manager_completes_two_review_publication(), test_manager_provisions_inactive_employee(), test_manager_uploads_into_quarantine(), test_publish_requires_acknowledged_index(), test_quarantined_document_is_not_readable() (+3 more)

### Community 50 - "App.tsx"
Cohesion: 0.10
Nodes (23): ApprovalRecord, ConversationSummary, getDashboard(), AnswerDetails(), AnswerDetailsBody(), AnswerDetailsProps, AuthMode, canAdmin() (+15 more)

### Community 51 - "datasources"
Cohesion: 0.22
Nodes (8): apiVersion, datasources, access, editable, isDefault, name, type, url

### Community 52 - "monitoring/prometheus.yml"
Cohesion: 0.22
Nodes (8): global, evaluation_interval, scrape_interval, rule_files, scrape_configs, job_name, static_configs, targets

### Community 53 - "lifecycle.py"
Cohesion: 0.06
Nodes (34): _acl_digest(), ApprovalBlocked, ApprovalRecord, _chunk_digest(), _chunk_state(), DerivedIndex, DerivedIndexFailure, DerivedIndexRecord (+26 more)

### Community 54 - "client.ts"
Cohesion: 0.08
Nodes (31): AccessGrant, AccessRequestResponse, answerFromStream(), ApiError, AuditRecord, Conversation, ConversationMessage, Dashboard (+23 more)

### Community 56 - "ProviderPolicy"
Cohesion: 0.11
Nodes (13): RerankerRequest, ProviderPolicy, _BM25Record, _citation(), DeterministicRerankerAdapter, _tokens(), test_reranker_request_rejects_blank_document_fields(), test_reranker_request_requires_documents() (+5 more)

### Community 57 - "request"
Cohesion: 0.14
Nodes (26): deleteDocument(), getApprovals(), getCurrentIdentity(), getDocument(), getDocuments(), getDocumentVersions(), getIngestionJob(), mutationHeaders() (+18 more)

### Community 58 - "admin.py"
Cohesion: 0.15
Nodes (48): activate_user(), AdminApiState, approve_document_version(), _body(), _bump_policy_epoch(), _counts(), create_department(), create_user() (+40 more)

### Community 59 - "upload"
Cohesion: 0.12
Nodes (22): add_user(), upload(), test_acl_explicit_deny_overrides_employee_read_allow(), test_anonymous_cannot_upload(), test_chairman_cannot_approve(), test_chairman_cannot_upload(), test_cross_tenant_document_is_not_revealed(), test_employee_cannot_provision_accounts() (+14 more)

### Community 61 - "tests/test_chat_api.py"
Cohesion: 0.23
Nodes (13): anonymous_conversation(), authenticated_headers(), request(), StubExecutor, test_anonymous_submit_status_completion_and_history_are_session_scoped(), test_authenticated_history_is_owner_only_and_revocation_denies_reuse(), test_citation_preview_and_download_are_separate_fresh_authorization_checks(), test_cross_origin_anonymous_cookie_is_usable_by_vercel_fetch() (+5 more)

### Community 62 - "auth"
Cohesion: 0.18
Nodes (21): auth(), test_account_response_does_not_return_password(), test_approval_schema_requires_explicit_stage(), test_existing_sign_in_contract_remains_under_auth_prefix(), test_job_status_contains_redacted_progress_only(), test_mutating_post_requires_idempotency_key(), test_upload_accepts_docx_mime_inference(), test_upload_accepts_xlsx_mime_inference() (+13 more)

### Community 64 - "orchestration/context.py"
Cohesion: 0.15
Nodes (7): AssembledContext, ContextLimitError, estimate_tokens(), PromptMessage, _render_evidence(), _safe_text(), _safe_value()

### Community 86 - "answer_baseline/test_behavior_component.py"
Cohesion: 0.11
Nodes (24): AnswerResult, _authorization_matches(), DirectAnswerPipeline, _expired(), _authorization(), authorize(), FakeModelGateway, _pipeline() (+16 more)

### Community 87 - "orchestration_langgraph/test_security_adversarial.py"
Cohesion: 0.13
Nodes (20): Answerer, Backend, call(), Clock, gateway(), Policy, principal(), request() (+12 more)

### Community 91 - "unittest"
Cohesion: 0.09
Nodes (8): Citation, inspect_untrusted_content(), normalize_user_input(), ToolDecision, validate_tool_request(), GuardrailBehaviorTests, GuardrailSecurityAdversarialTests, GuardrailTests

### Community 93 - "active"
Cohesion: 0.18
Nodes (15): active(), test_acknowledged_index_is_still_not_active(), test_publishing_new_version_supersedes_previous_version(), test_review_one_requires_clean_scan(), test_revoke_active_version_removes_retrieval(), test_second_review_and_publish_make_version_active(), test_soft_delete_isolates_all_versions(), test_upload_starts_quarantined_and_not_retrievable() (+7 more)

### Community 94 - "test_chat_stream.py"
Cohesion: 0.08
Nodes (23): AnonymousPrincipal, GeminiProviderError, GeminiStreamProvider, _http_error_code(), _text_parts(), LocalRagExecutor, anonymous_conversation(), _FakeGemini (+15 more)

### Community 95 - "inherit_acl"
Cohesion: 0.26
Nodes (4): inherit_acl(), make_child(), make_parent(), KnowledgeSecurityAdversarialTests

### Community 96 - "knowledge/_baseline.py"
Cohesion: 0.17
Nodes (4): make_document(), make_version(), KnowledgeBehaviorTests, KnowledgeContractIntegrationTests

### Community 98 - "test_tool_gateway.py"
Cohesion: 0.16
Nodes (21): _Backend, _call(), _Clock, _gateway(), _Policy, _principal(), _Resolvers, test_backend_exception_is_unavailable_without_raw_error() (+13 more)

### Community 99 - "AnswerDraft"
Cohesion: 0.26
Nodes (20): AnswerDraft, _Answerer, _Clock, _evidence(), _orchestrator(), _request(), test_answerer_error_is_returned_as_safe_error(), test_complex_route_splits_subqueries_and_preserves_bound() (+12 more)

### Community 100 - "identity.py"
Cohesion: 0.18
Nodes (11): create_access_request(), _bearer_token(), current_identity(), _record(), _record_identity_error(), _request_context(), sign_in(), sign_out() (+3 more)

### Community 102 - "_make_case"
Cohesion: 0.22
Nodes (13): evaluation_snapshot(), load_validated_records(), test_all_golden_cases_run_through_v1_v3(), test_allowed_answer_has_no_unauthorized_retrieval_marker(), test_answered_case_keeps_citation_version_and_tenant_binding(), test_dataset_contains_permission_negative_and_cross_tenant_cases(), test_empty_query_is_denied_before_retrieval(), test_model_failure_returns_error_without_source_or_answer() (+5 more)

### Community 103 - "IngestionService"
Cohesion: 0.11
Nodes (30): AccessGrant, IngestionService, _cosine(), DenseRetriever, DeterministicEmbeddingAdapter, _active_document(), _gateway(), _principal() (+22 more)

### Community 104 - "authorization/test_behavior_component.py"
Cohesion: 0.32
Nodes (5): ConversationResource, AuthorizationBehaviorTests, document(), evaluator(), principal()

### Community 105 - "IdentityError"
Cohesion: 0.19
Nodes (12): IdentityError, rate_limited(), AuthenticationService, make_service(), test_expired_session_is_rejected(), test_invalid_password_is_safe_auth_error(), test_mfa_is_required_for_privileged_role(), test_revoked_session_is_rejected() (+4 more)

### Community 106 - "test_sample_documents.py"
Cohesion: 0.31
Nodes (7): _authorize(), _Corpus, _GroundedSampleAnswer, _manifest(), test_no_answer_is_safe_when_sample_corpus_is_outside_tenant_scope(), test_sample_manifest_is_synthetic_hash_bound_and_private(), test_sample_query_returns_evidence_and_typed_citation()

### Community 107 - "ToolResult"
Cohesion: 0.32
Nodes (16): Answerer, Clock, evidence(), request(), run(), test_answer_provider_failure_returns_error_without_exception_to_user(), test_deadline_timeout_is_a_visible_insufficient_outcome(), test_second_retrieval_round_recovers_a_temporarily_insufficient_answer() (+8 more)

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
Cohesion: 0.09
Nodes (13): reset(), clean_state(), clean_state(), clean_state(), test_audit_catalog_is_metadata_only(), test_document_and_approval_catalogs_are_real_api_shapes(), clean_state(), test_dashboard_integration_reports_authorized_document_and_ingestion_aggregates() (+5 more)

### Community 112 - "to_qdrant_payload"
Cohesion: 0.35
Nodes (11): to_qdrant_payload(), make_child(), make_parent(), test_acl_inheritance_populates_child_reference(), test_parent_child_contract_keeps_same_scope(), test_qdrant_projection_contains_index_state(), test_qdrant_projection_contains_scope_keys(), test_qdrant_projection_does_not_store_chunk_text() (+3 more)

### Community 113 - "AuthorizationDecision"
Cohesion: 0.18
Nodes (25): AuthorizationDecision, EvidenceVerifier, VerificationRequest, allow(), authorize(), revoked(), authorize(), verify_retrieved() (+17 more)

### Community 114 - "answer_baseline/test_contract_integration.py"
Cohesion: 0.17
Nodes (16): _allow(), authorize(), RecordingModel, RecordingRetriever, _setup(), test_citation_authorization_rejects_document_mismatch(), test_citation_authorization_rejects_non_active_status(), test_citation_authorization_rejects_non_current_version() (+8 more)

### Community 115 - "BoundedOrchestrator"
Cohesion: 0.09
Nodes (10): AnswerSynthesizer, BoundedOrchestrator, _GraphState, OrchestrationOutcome, OrchestrationRequest, OrchestrationStatus, QueryRoute, _route() (+2 more)

### Community 116 - "answer_baseline/test_e2e_operational.py"
Cohesion: 0.14
Nodes (19): _allow(), authorize(), FailingEmbedder, FailingReranker, FakeAnswerGateway, _setup(), test_operational_abstention_is_insufficient_evidence(), test_operational_conflicting_evidence_is_not_harmonized() (+11 more)

### Community 117 - "read_frontend"
Cohesion: 0.15
Nodes (3): read_frontend(), FrontendBehaviorComponentTests, FrontendSecurityAdversarialTests

### Community 118 - "eval_001_runner.py"
Cohesion: 0.16
Nodes (11): _aggregate(), _AnswerModel, _Case, _DenseAsHybrid, evaluate(), _mean(), _percentile(), _principal() (+3 more)

### Community 120 - "cache_memory/test_security_adversarial.py"
Cohesion: 0.38
Nodes (11): make_key(), make_scope(), test_anonymous_revocation_isolated_to_one_session_and_fails_closed(), test_broad_scope_cannot_replay_after_a_narrow_document_change(), test_cache_key_excludes_queries_model_inputs_and_conversation_identifiers(), test_changed_document_version_cannot_repopulate_an_old_cache_entry(), test_cross_principal_cache_read_is_a_fail_closed_miss(), test_cross_scope_conversation_read_cannot_be_recovered_by_matching_id() (+3 more)

### Community 121 - "App.test.tsx"
Cohesion: 0.29
Nodes (4): adminPrincipal, conversationResponse(), json(), principal

### Community 122 - "cache_memory/test_contract_integration.py"
Cohesion: 0.18
Nodes (13): _digest(), _identifier(), InvalidationReason, make_key(), make_scope(), test_contract_acl_change_can_target_one_principal_and_version(), test_contract_delete_event_invalidates_matching_scope_without_cross_tenant_reach(), test_contract_document_change_invalidates_broad_scope_and_selected_version() (+5 more)

### Community 123 - "orchestration_langgraph/test_contract_integration.py"
Cohesion: 0.16
Nodes (17): AuthorizedScope, Backend, call(), Clock, gateway(), Policy, principal(), Resolvers (+9 more)

### Community 124 - "Claim"
Cohesion: 0.14
Nodes (33): CitationRecord, Claim, EvidenceRecord, SourceSpan, allow_active(), citation(), test_authorizer_must_attest_active_current_and_not_revoked(), revoked() (+25 more)

### Community 125 - "test_customer_api_e2e.py"
Cohesion: 0.06
Nodes (17): get_settings(), Settings, healthz(), test_healthz_is_local_liveness_only(), test_identity_requires_bearer_credentials(), test_vercel_origin_can_use_cookie_authenticated_api(), anonymous_conversation(), parse_sse() (+9 more)

### Community 127 - "new_service"
Cohesion: 0.14
Nodes (24): ScanReport, new_service(), test_rejected_scan_is_terminal_and_not_retrievable(), test_cross_tenant_version_lookup_is_denied(), test_derived_cleanup_failure_still_denies_retrieval(), test_derived_index_cannot_authorize_non_active_version(), test_legal_hold_blocks_permanent_delete(), test_rejected_version_cannot_be_retrieved() (+16 more)

### Community 129 - "quarantine"
Cohesion: 0.11
Nodes (19): make_chunks(), quarantine(), test_non_retryable_failure_is_terminal(), test_retry_is_bounded_and_preserves_checksum(), test_retry_with_changed_checksum_is_denied(), test_watchdog_expiry_does_not_auto_approve(), test_child_acl_broadening_is_denied(), test_tenant_scope_isolation_is_fail_closed() (+11 more)

### Community 130 - "manifest.json"
Cohesion: 0.15
Nodes (12): corpus_id, documents, provenance, external_sources, kind, owner, source, queries (+4 more)

### Community 131 - "evidence/test_contract_integration.py"
Cohesion: 0.23
Nodes (6): allow_active(), citation(), test_chat_001_owns_preview_download_reauthorization_recheck(), test_duplicate_evidence_ids_are_a_malformed_fail_closed_result(), authorize(), test_supported_result_round_trips_tenant_document_version_and_span()

### Community 132 - "orchestration_langgraph/test_behavior_component.py"
Cohesion: 0.27
Nodes (15): Answerer, Clock, evidence(), request(), run(), test_compiles_a_state_graph_with_expected_nodes(), test_complex_loop_caps_subqueries_and_tool_calls_at_four(), test_complex_query_splits_into_distinct_subqueries() (+7 more)

### Community 133 - "KnowledgeOperationalTests"
Cohesion: 0.17
Nodes (3): read(), task(), KnowledgeOperationalTests

### Community 134 - "ConversationMessage"
Cohesion: 0.14
Nodes (18): ConversationMemory, ConversationMessage, test_contract_fake_repository_implements_provider_neutral_memory_boundary(), Clock, FakeInvalidationBus, FakeMemoryRepository, make_key(), make_scope() (+10 more)

### Community 135 - "AuthorizationOperationalTests"
Cohesion: 0.17
Nodes (6): InMemoryPolicyStore, PolicyEnforcementPoint, AuthorizationOperationalTests, document(), evaluator(), principal()

### Community 136 - "ingestion/_baseline.py"
Cohesion: 0.10
Nodes (15): Clock, graph_labels(), read(), RuntimeFailureOnRemove, service_with_index(), task(), test_task_and_handoff_keep_ingestion_provider_neutral(), test_cleanup_backend_error_is_wrapped_without_secret_leakage() (+7 more)

### Community 137 - "test_knowledge_security.py"
Cohesion: 0.38
Nodes (12): make_child(), make_parent(), test_conflicting_child_acl_is_denied(), test_document_mismatch_is_denied(), test_matching_child_acl_is_preserved(), test_missing_child_acl_is_inherited(), test_qdrant_projection_does_not_claim_authority(), test_qdrant_projection_keeps_tenant_boundary() (+4 more)

### Community 138 - "ndcg_at_k"
Cohesion: 0.15
Nodes (16): answer_correctness(), citation_accuracy(), evaluate_case(), mean_reciprocal_rank(), ndcg_at_k(), no_answer_accuracy(), recall_at_k(), source_key() (+8 more)

### Community 140 - "ChatService"
Cohesion: 0.19
Nodes (5): ChatActor, ChatService, _error(), _fingerprint(), test_http_chat_reaches_local_rag_and_returns_verified_citation()

### Community 141 - "test_cache_memory.py"
Cohesion: 0.29
Nodes (11): Clock, response_key(), scope(), test_cache_delete_is_explicit(), test_cache_expires_and_rejects_unbounded_ttl_or_value(), test_cache_key_contains_security_scope_but_not_raw_query(), test_cache_requires_exact_current_scope_and_isolates_tenant_and_principal(), test_conversation_delete_removes_body_and_blocks_recreation_in_old_scope() (+3 more)

### Community 145 - "read"
Cohesion: 0.05
Nodes (7): read(), task(), tasks(), IdentityBehaviorTests, IdentityContractTests, IdentityOperationalTests, IdentitySecurityTests

### Community 146 - "build_secure_context"
Cohesion: 0.14
Nodes (6): build_secure_context(), RetrievedEvidence, SecureContextBuilderTests, PromptOperationalTests, PromptSecurityAdversarialTests, test_secure_context_escapes_parent_prompt_injection_as_untrusted_content()

### Community 147 - "expand_parent_context"
Cohesion: 0.06
Nodes (62): _active(), ChildEvidence, _coerce_child(), _coerce_parent(), _construct(), expand_parent_context(), _identity(), _index_parents() (+54 more)

### Community 148 - "AnswerCitation"
Cohesion: 0.31
Nodes (5): _answer_citation(), AnswerCitation, _utc_z(), _valid_locator(), test_answer_citation_serializes_typed_locator_and_bindings()

### Community 151 - "app/evidence/__init__.py"
Cohesion: 0.20
Nodes (8): ClaimVerification, _is_negative(), _numeric_conflict(), _numeric_terms(), _relation(), _terms(), VerificationOutcome, VerificationResult

### Community 152 - "InMemoryScopedCache"
Cohesion: 0.20
Nodes (17): InMemoryScopedCache, test_cache_invalidation_hooks_remove_only_matching_scope(), test_policy_invalidation_is_fail_closed_for_old_epoch_but_allows_new_epoch(), Clock, make_key(), make_scope(), test_broad_acl_invalidation_removes_all_versions_in_one_tenant(), test_cache_expires_at_the_exact_ttl_deadline() (+9 more)

### Community 153 - "answer_baseline/test_security_adversarial.py"
Cohesion: 0.09
Nodes (26): GeneratedAnswer, _LocalAnswerModel, _authorization(), authorize(), FakeModelGateway, _pipeline(), test_direct_answer_returns_insufficient_without_calling_model_when_no_match(), test_direct_answer_returns_partial_for_mixed_claims() (+18 more)

### Community 154 - "validate_output"
Cohesion: 0.16
Nodes (12): _citation(), detect_prompt_injection(), GuardrailResult, _inspect_text(), _luhn_valid(), _normalize_text(), redact_sensitive_data(), redact_card() (+4 more)

### Community 156 - "db/runtime.py"
Cohesion: 0.10
Nodes (18): StaleScopeError, _answer_status(), _as_utc(), _department_uuid(), _jsonb(), _membership_uuid(), normalize_database_url(), _parse_uuid() (+10 more)

### Community 157 - "ChunkMetadata"
Cohesion: 0.07
Nodes (15): DocumentMetadata, DocumentVersionMetadata, test_active_chunk_requires_acl_metadata(), test_chunk_accepts_source_provenance(), test_chunk_rejects_reversed_pages(), test_chunk_rejects_self_parent(), test_document_metadata_is_tenant_scoped(), test_document_version_identity_is_stable() (+7 more)

### Community 161 - "App"
Cohesion: 0.12
Nodes (29): clearAccessToken(), createConversation(), getConversation(), getConversations(), previewCitation(), signOut(), submitFeedback(), App() (+21 more)

### Community 172 - "pytest"
Cohesion: 0.12
Nodes (33): UploadManifest, make_manifest(), staged(), validated(), test_clean_review_one_allows_processing(), test_processing_inherits_parent_acl(), test_approval_expiry_blocks_publication(), test_doc_is_rejected() (+25 more)

### Community 173 - "admin_api/test_contract_integration.py"
Cohesion: 0.16
Nodes (12): clean_state(), test_account_response_does_not_return_password(), test_approval_schema_requires_explicit_stage(), test_job_status_contains_redacted_progress_only(), test_mutating_post_requires_idempotency_key(), test_upload_accepts_docx_mime_inference(), test_upload_accepts_xlsx_mime_inference(), test_upload_idempotency_rejects_a_different_fingerprint() (+4 more)

### Community 175 - "auth"
Cohesion: 0.13
Nodes (29): request(), test_anonymous_is_denied_without_a_management_data_or_existence_leak(), test_chairman_is_denied_the_management_boundary(), test_dashboard_metrics_aggregate_only_the_current_tenant_snapshot(), test_employee_is_denied_the_management_boundary(), test_system_admin_can_read_dashboard_through_the_real_pep(), test_website_manager_can_read_feedback_through_the_real_pep(), _feedback() (+21 more)

### Community 186 - "test_customer_frontend_static.py"
Cohesion: 0.15
Nodes (6): test_chat_controls_have_keyboard_labels_and_live_status_semantics(), test_mobile_375x812_contract_keeps_chat_controls_within_the_viewport(), test_reload_contract_restores_conversation_and_requests_history(), test_responsive_layout_has_mobile_breakpoints_and_no_horizontal_body_overflow(), test_retryable_backend_error_has_a_user_recovery_action(), test_stop_control_is_available_only_during_a_live_stream()

### Community 197 - "test_answer_citation_schema.py"
Cohesion: 0.29
Nodes (6): _CapturingModel, _Model, test_direct_answer_context_includes_authorized_parent_runtime(), authorize(), test_real_hybrid_path_propagates_pdf_schema_end_to_end(), authorize()

### Community 198 - "hashlib"
Cohesion: 0.21
Nodes (4): IdentityErrorPassthrough, now_utc(), hash_secret(), verify_secret()

### Community 200 - "_RequestModel"
Cohesion: 0.20
Nodes (10): AccessGrantRequest, AccessRequest, DepartmentRequest, EmployeeAccessRequest, PermanentDeleteRequest, _RequestModel, ReviewRequest, UploadRequest (+2 more)

### Community 201 - "json"
Cohesion: 0.15
Nodes (7): load_records(), _span(), _spans(), test_rag_002_regression_metrics_on_tiny_in_memory_corpus(), test_dashboard_has_api_and_security_panels(), test_dashboard_is_valid_json(), test_rag002_task_registry_keeps_retrieval_validation_and_scope()

### Community 204 - "tests/test_dashboard_api.py"
Cohesion: 0.25
Nodes (6): clean_state(), test_anonymous_is_denied_dashboard_and_feedback(), test_feedback_review_is_private_bounded_and_replay_does_not_duplicate(), test_management_roles_can_read_empty_dashboard_and_feedback(), test_non_management_roles_are_denied_dashboard_and_feedback(), test_policy_outage_fails_closed_for_both_management_reads()

### Community 205 - "UsersView"
Cohesion: 0.35
Nodes (11): activateUser(), createDepartment(), createUser(), getDepartments(), getUsers(), updateUser(), UsersView(), load() (+3 more)

### Community 207 - "env.py"
Cohesion: 0.19
Nodes (4): _database_url(), run_migrations_offline(), run_migrations_online(), DatabaseMigrationSmokeTests

## Knowledge Gaps
- **1 isolated node(s):** `enterprise-agentic-rag-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 1021 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **81 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AuthenticatedPrincipal` connect `AuthorizationEvaluator` to `AuthorizationOperationalTests`, `ChatService`, `app/rag/__init__.py`, `expand_parent_context`, `InMemoryIdentityStore`, `evaluator`, `core/chat.py`, `api/chat.py`, `ChunkMetadata`, `chat_api/test_contract_integration.py`, `chat_api/test_behavior_component.py`, `_make_retriever`, `chat_api/test_security_adversarial.py`, `rag/runtime.py`, `identity/service.py`, `ToolResult`, `lifecycle.py`, `ProviderPolicy`, `admin.py`, `hashlib`, `answer_baseline/test_behavior_component.py`, `orchestration_langgraph/test_security_adversarial.py`, `test_chat_stream.py`, `test_tool_gateway.py`, `identity.py`, `IngestionService`, `authorization/test_behavior_component.py`, `IdentityError`, `test_sample_documents.py`, `test_authorization.py`, `eval_001_runner.py`, `orchestration_langgraph/test_contract_integration.py`, `test_customer_api_e2e.py`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Are the 46 inferred relationships involving `IngestionService` (e.g. with `reset_state()` and `test_active_retrieval_to_evidence_verification_succeeds()`) actually correct?**
  _`IngestionService` has 46 INFERRED edges - model-reasoned connections that need verification._
- **What connects `enterprise-agentic-rag-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `audit.py` be split into smaller, more focused modules?**
  _Cohesion score 0.056535504296698326 - nodes in this community are weakly interconnected._
- **Why does `DataClassification` connect `DataClassification` to `ModelPolicy`, `EgressMode`, `app/rag/__init__.py`, `expand_parent_context`, `answer_baseline/test_security_adversarial.py`, `ModelProviderError`, `_make_retriever`, `rag/runtime.py`, `pytest`, `lifecycle.py`, `ProviderPolicy`, `admin.py`, `AnswerModelGateway`, `test_answer_citation_schema.py`, `answer_baseline/test_behavior_component.py`, `IngestionService`, `test_sample_documents.py`, `answer_baseline/test_contract_integration.py`, `answer_baseline/test_e2e_operational.py`, `eval_001_runner.py`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Are the 47 inferred relationships involving `DataClassification` (e.g. with `ModelEgressDenied` and `ModelGateway`) actually correct?**
  _`DataClassification` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Should `compose` be split into smaller, more focused modules?**
  _Cohesion score 0.07017543859649122 - nodes in this community are weakly interconnected._