# Graph Report - enterprise-agentic-rag-harness  (2026-11-11)

## Corpus Check
- 267 files · ~222,307 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 68 file(s) not represented in the graph (top: (none) 53, .toml 9, .example 2)

## Summary
- 3708 nodes · 11120 edges · 175 communities (115 shown, 60 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 1168 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fae63670`
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
- AuthenticatedPrincipal
- InvalidationEvent
- postgres
- postgres
- new_service
- package.json
- hybrid.py
- InMemoryPolicyStore
- CacheScope
- compilerOptions
- ChunkMetadata
- inherit_acl
- expand_parent_context
- authorization/test_contract_integration.py
- request
- chat_api/test_contract_integration.py
- DataClassification
- chat_api/test_behavior_component.py
- _evaluation_harness.py
- GraphifyOperationalTests
- key
- chat_api/test_security_adversarial.py
- steps
- ModelGateway
- ContractIntegrationTests
- SecurityAdversarialTests
- rules
- RerankerRequest
- ProviderPolicy
- ToolResult
- eslint.config.js
- route
- CacheScope
- test_knowledge_database.py
- chat_api/test_e2e_operational.py
- rag_v4_citation/test_e2e_operational.py
- App.tsx
- datasources
- monitoring/prometheus.yml
- AuthorizationDecision
- dependencies
- vitest
- scripts
- rag_v4_citation/test_security_adversarial.py
- admin.py
- api/chat.py
- PromptDefinition
- tests/test_chat_api.py
- dense.py
- orchestrator.py
- vite-env.d.ts
- sync_graph.sh
- migrate.sh
- inspect_untrusted_content
- enterprise-agentic-rag-backend
- answer_baseline/test_behavior_component.py
- orchestration_langgraph/test_security_adversarial.py
- _make_case
- PromptContractIntegrationTests
- _make_retriever
- AuthenticatedPrincipal
- test_identity.py
- test_tool_gateway.py
- AnswerDraft
- SourceSpan
- lifecycle.py
- IngestionService
- ModelPolicy
- FrontendE2EOperationalTests
- InMemoryIdentityStore
- ToolResult
- InfrastructureSecurityTests
- IdentityBehaviorTests
- IdentitySecurityTests
- reset
- EvidenceVerifier
- answer_baseline/test_contract_integration.py
- ingestion/_baseline.py
- answer_baseline/test_e2e_operational.py
- CitationArtifact
- guardrails/__init__.py
- GeneratedAnswer
- normalize_user_input
- identity/_baseline.py
- orchestration_langgraph/test_contract_integration.py
- validate_output
- backend_boot/_baseline.py
- BackendBootstrapBehaviorTests
- rag_hybrid/test_security_adversarial.py
- run_local_guardrail_pipeline
- Citation
- dataclasses
- Claim
- orchestration_langgraph/test_behavior_component.py
- cache_memory/test_e2e_operational.py
- test_cache_memory.py
- authorization/test_behavior_component.py
- ChatService
- cache_memory/test_behavior_component.py
- test_authorization.py
- eval_001_runner.py
- read
- build_secure_context
- evidence/__init__.py
- upload
- json
- rag_v4_citation/test_contract_integration.py
- make_manifest
- SecureContextBuilder
- IdentityContractTests
- ScopedCacheKey
- feedback/service.py
- EgressMode
- active
- env.py
- PromptBehaviorComponentTests
- ingestion/test_behavior_component.py
- BehaviorComponentTests
- admin_api/test_contract_integration.py
- test_admin_api_contract.py
- admin_api/test_behavior_component.py
- UUID
- validated
- test_ingestion_behavior.py
- _ingestion_fixtures.py
- AnswerModelGateway
- _RrfOnly

## God Nodes (most connected - your core abstractions)
1. `request()` - 137 edges
2. `auth()` - 135 edges
3. `IngestionService` - 116 edges
4. `DataClassification` - 93 edges
5. `AuthenticatedPrincipal` - 87 edges
6. `new_service()` - 85 edges
7. `_active_document()` - 78 edges
8. `CacheScope` - 68 edges
9. `ChunkMetadata` - 67 edges
10. `_principal()` - 65 edges

## Surprising Connections (you probably didn't know these)
- `authorize()` --calls--> `AuthorizationDecision`  [INFERRED]
  tests/evaluation/eval_001_runner.py → backend/app/evidence/verifier.py
- `authorize()` --calls--> `AuthorizationDecision`  [INFERRED]
  tests/integration/test_answer_citation_schema.py → backend/app/evidence/verifier.py
- `authorize()` --calls--> `AuthorizationDecision`  [INFERRED]
  tests/qa/answer_baseline/test_security_adversarial.py → backend/app/evidence/verifier.py
- `pause_first_run()` --calls--> `_tenant_uuid()`  [EXTRACTED]
  tests/qa/chat_api/test_e2e_operational.py → backend/app/api/admin.py
- `reset_api_state()` --calls--> `InMemoryAuditSink`  [INFERRED]
  tests/qa/chat_api/test_contract_integration.py → backend/app/observability/audit.py

## Import Cycles
- 2-file cycle: `backend/app/api/admin.py -> backend/app/api/chat.py -> backend/app/api/admin.py`
- 2-file cycle: `backend/app/api/admin.py -> backend/app/api/identity.py -> backend/app/api/admin.py`
- 2-file cycle: `backend/app/api/chat.py -> backend/app/api/identity.py -> backend/app/api/chat.py`
- 3-file cycle: `backend/app/api/admin.py -> backend/app/api/chat.py -> backend/app/api/identity.py -> backend/app/api/admin.py`
- 3-file cycle: `backend/app/api/admin.py -> backend/app/api/identity.py -> backend/app/api/chat.py -> backend/app/api/admin.py`

## Communities (175 total, 60 thin omitted)

### Community 0 - "audit.py"
Cohesion: 0.08
Nodes (21): append_audit_event(), AuditEvent, AuditSink, AuditSinkUnavailable, InMemoryAuditSink, redact_metadata(), _safe_code(), _safe_identifier() (+13 more)

### Community 1 - "compose"
Cohesion: 0.05
Nodes (13): get_settings(), Settings, compose(), compose_config_result(), database(), handoff(), read(), tasks() (+5 more)

### Community 2 - "read"
Cohesion: 0.05
Nodes (10): compose_config_result(), migration_files(), migration_text(), read(), task(), tasks(), DatabaseBaselineBehaviorTests, DatabaseBaselineContractTests (+2 more)

### Community 3 - "read"
Cohesion: 0.07
Nodes (7): compose_config(), read(), task(), tasks(), InfrastructureBehaviorTests, InfrastructureContractTests, InfrastructureOperationalTests

### Community 4 - "read"
Cohesion: 0.05
Nodes (7): read(), task(), tasks(), AuditBehaviorTests, AuditContractTests, AuditOperationalTests, AuditSecurityTests

### Community 5 - "section"
Cohesion: 0.10
Nodes (7): json_blocks(), require_all(), section(), BehaviorComponentTests, ContractIntegrationTests, E2EOperationalTests, SecurityAdversarialTests

### Community 6 - "read"
Cohesion: 0.06
Nodes (7): dashboard(), read(), task(), MonitoringBehaviorTests, MonitoringContractTests, MonitoringOperationalTests, MonitoringSecurityTests

### Community 7 - "read_frontend"
Cohesion: 0.08
Nodes (7): dfs(), load_frontend_json(), read(), read_frontend(), FrontendBehaviorComponentTests, FrontendContractIntegrationTests, FrontendSecurityAdversarialTests

### Community 8 - "read"
Cohesion: 0.06
Nodes (7): read(), GraphifyBehaviorTests, GraphifyContractTests, GraphifySecurityTests, read(), task(), KnowledgeOperationalTests

### Community 9 - "otel-collector-config.yaml"
Cohesion: 0.06
Nodes (32): action, key, actions, send_batch_size, timeout, exporters, prometheus, endpoint (+24 more)

### Community 10 - "prometheus"
Cohesion: 0.06
Nodes (30): command, image, ports, read_only, security_opt, volumes, depends_on, image (+22 more)

### Community 13 - "identity.py"
Cohesion: 0.13
Nodes (11): _bearer_token(), current_identity(), _record(), _record_identity_error(), _request_context(), sign_in(), sign_out(), SignInRequest (+3 more)

### Community 14 - "AuthenticatedPrincipal"
Cohesion: 0.08
Nodes (12): AuthorizationDenied, AuthorizationEvaluator, deny(), PolicyDecision, PolicyEnforcementPoint, PolicyStore, _resource_type(), _valid_epoch() (+4 more)

### Community 15 - "InvalidationEvent"
Cohesion: 0.10
Nodes (7): _CacheEntry, _digest(), _identifier(), InvalidationEvent, InvalidationReason, _serialized_size(), test_contract_invalid_event_shapes_fail_closed_at_the_boundary()

### Community 16 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, networks (+12 more)

### Community 17 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, networks (+12 more)

### Community 18 - "new_service"
Cohesion: 0.16
Nodes (24): new_service(), quarantine(), test_upload_starts_quarantined_and_not_retrievable(), test_audit_sink_receives_lifecycle_events_without_content(), test_failed_maintenance_can_be_recovered_after_cleanup(), test_non_retryable_failure_is_terminal(), test_only_one_maintenance_window_is_active(), test_publication_failure_keeps_previous_active_version() (+16 more)

### Community 19 - "package.json"
Cohesion: 0.13
Nodes (19): devDependencies, eslint@9.17.0, jsdom@25.0.1, @types/node@22.10.5, @types/react@18.3.18, @types/react-dom@18.3.5, typescript@5.7.2, engines (+11 more)

### Community 20 - "hybrid.py"
Cohesion: 0.10
Nodes (13): ModelProviderError, EmbeddingAdapter, EmbeddingRequest, EmbeddingResult, RankedDocument, RerankerAdapter, RerankerResult, ModelRoute (+5 more)

### Community 21 - "InMemoryPolicyStore"
Cohesion: 0.27
Nodes (5): InMemoryPolicyStore, AuthorizationSecurityAdversarialTests, document(), evaluator(), principal()

### Community 22 - "CacheScope"
Cohesion: 0.11
Nodes (13): CacheScope, ConversationMemory, ConversationMemoryRepository, FakeMemoryRepository, make_key(), make_scope(), test_contract_delete_event_invalidates_matching_scope_without_cross_tenant_reach(), test_contract_document_change_invalidates_broad_scope_and_selected_version() (+5 more)

### Community 23 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+10 more)

### Community 24 - "ChunkMetadata"
Cohesion: 0.06
Nodes (18): ChunkMetadata, DocumentMetadata, DocumentVersionMetadata, test_active_chunk_requires_acl_metadata(), test_chunk_accepts_source_provenance(), test_chunk_rejects_reversed_pages(), test_chunk_rejects_self_parent(), test_document_metadata_is_tenant_scoped() (+10 more)

### Community 25 - "inherit_acl"
Cohesion: 0.10
Nodes (28): inherit_acl(), to_qdrant_payload(), make_child(), make_parent(), test_acl_inheritance_populates_child_reference(), test_parent_child_contract_keeps_same_scope(), test_qdrant_projection_contains_index_state(), test_qdrant_projection_contains_scope_keys() (+20 more)

### Community 26 - "expand_parent_context"
Cohesion: 0.10
Nodes (44): _active(), ChildEvidence, _coerce_child(), _coerce_parent(), _construct(), expand_parent_context(), _identity(), _index_parents() (+36 more)

### Community 27 - "authorization/test_contract_integration.py"
Cohesion: 0.27
Nodes (4): AuthorizationContractIntegrationTests, document(), evaluator(), principal()

### Community 28 - "request"
Cohesion: 0.10
Nodes (51): auth(), request(), test_acl_update_advances_policy_epoch(), test_activation_allows_follow_up_sign_in(), test_admin_mutations_emit_privacy_safe_audit_events(), test_anonymous_is_denied_management_api(), test_chairman_is_denied_management_api(), test_employee_is_denied_management_api() (+43 more)

### Community 29 - "chat_api/test_contract_integration.py"
Cohesion: 0.11
Nodes (20): job_payload(), JobState, anonymous_conversation(), authenticated_conversation(), Clock, Executor, Maintenance, make_service() (+12 more)

### Community 30 - "DataClassification"
Cohesion: 0.17
Nodes (37): DataClassification, ModelTask, FakeEmbedding, policy(), provider(), route(), test_approved_local_fallback_can_handle_internal_data(), test_approved_local_provider_can_process_internal_data() (+29 more)

### Community 31 - "chat_api/test_behavior_component.py"
Cohesion: 0.14
Nodes (20): AnswerState, QueryCompletion, anonymous_conversation(), authenticated_conversation(), Clock, Executor, Maintenance, make_service() (+12 more)

### Community 32 - "_evaluation_harness.py"
Cohesion: 0.14
Nodes (16): answer_correctness(), citation_accuracy(), evaluate_case(), mean_reciprocal_rank(), ndcg_at_k(), no_answer_accuracy(), recall_at_k(), source_key() (+8 more)

### Community 33 - "GraphifyOperationalTests"
Cohesion: 0.15
Nodes (5): graph(), graphify_bin(), run_graphify(), GraphifyOperationalTests, run_graph_query()

### Community 34 - "key"
Cohesion: 0.12
Nodes (34): _document_resource(), ScanVerdict, StagedIndex, add_user(), key(), prepare_review_two(), publish(), test_manager_activates_provisioned_account() (+26 more)

### Community 35 - "chat_api/test_security_adversarial.py"
Cohesion: 0.16
Nodes (18): anonymous_conversation(), authenticated_conversation(), Clock, Executor, Maintenance, make_service(), principal(), public_document() (+10 more)

### Community 36 - "steps"
Cohesion: 0.15
Nodes (12): jobs, validate, name, on, pull_request, workflow_dispatch, run, uses (+4 more)

### Community 37 - "ModelGateway"
Cohesion: 0.12
Nodes (20): ModelGateway, test_gateway_reranker_happy_path(), graph_labels(), policy(), run_graph_query(), ScriptedEmbedding, task(), test_embedding_gateway_contract_passes_request_route_and_timeout() (+12 more)

### Community 40 - "rules"
Cohesion: 0.17
Nodes (11): runbook, summary, groups, name, rules, severity, alert, annotations (+3 more)

### Community 41 - "RerankerRequest"
Cohesion: 0.21
Nodes (9): RerankerRequest, DeterministicRerankerAdapter, _tokens(), test_reranker_request_rejects_blank_document_fields(), test_reranker_request_requires_documents(), test_reranker_request_requires_query(), _gateway(), test_deterministic_reranker_counts_query_and_document_overlap() (+1 more)

### Community 43 - "ToolResult"
Cohesion: 0.09
Nodes (15): AuthorizedScope, GetDocumentMetadataArguments, PrincipalResolver, ReadAuthorizedChunkArguments, _safe_tool_result(), ScopeResolver, SearchDocumentsArguments, ToolBackend (+7 more)

### Community 44 - "eslint.config.js"
Cohesion: 0.18
Nodes (10): @eslint/js@9.17.0, eslint-plugin-react-hooks@5.1.0, eslint-plugin-react-refresh@0.4.16, globals@15.14.0, typescript-eslint@8.18.0, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh (+2 more)

### Community 45 - "route"
Cohesion: 0.18
Nodes (10): global, resolve_timeout, receivers, name, route, group_by, group_interval, group_wait (+2 more)

### Community 46 - "CacheScope"
Cohesion: 0.08
Nodes (15): StaleScopeError, ActorKind, AnonymousSession, CheckpointRepository, ConversationRecord, ConversationRepository, ConversationView, InMemoryChatRepository (+7 more)

### Community 47 - "test_knowledge_database.py"
Cohesion: 0.26
Nodes (11): migration_text(), test_existing_db_contract_has_active_index_guard(), test_existing_db_contract_has_chunks_table(), test_existing_db_contract_has_composite_parent_fk(), test_existing_db_contract_has_document_versions_table(), test_existing_db_contract_has_documents_table(), test_existing_db_contract_has_immutable_version_uniqueness(), test_existing_db_contract_has_private_source_constraint() (+3 more)

### Community 48 - "chat_api/test_e2e_operational.py"
Cohesion: 0.23
Nodes (15): anonymous_conversation(), HttpExecutor, request(), sign_in(), test_http_anonymous_lifecycle_and_session_isolation(), test_http_authenticated_history_and_job_are_owner_only(), test_http_citation_preview_and_download_reauthorize_after_revocation(), test_http_deadline_failure_is_safe_and_has_no_answer() (+7 more)

### Community 49 - "rag_v4_citation/test_e2e_operational.py"
Cohesion: 0.16
Nodes (18): HybridEvidence, HybridRetrievalResult, _allow(), _answer(), _locator(), _Model, _principal(), _StaticRetriever (+10 more)

### Community 50 - "App.tsx"
Cohesion: 0.27
Nodes (5): react@18.3.1, App(), supportedRoles, appConfig, react

### Community 51 - "datasources"
Cohesion: 0.22
Nodes (8): apiVersion, datasources, access, editable, isDefault, name, type, url

### Community 52 - "monitoring/prometheus.yml"
Cohesion: 0.22
Nodes (8): global, evaluation_interval, scrape_interval, rule_files, scrape_configs, job_name, static_configs, targets

### Community 53 - "AuthorizationDecision"
Cohesion: 0.13
Nodes (26): AuthorizationDecision, CitationRecord, allow_active(), citation(), test_authorizer_must_attest_active_current_and_not_revoked(), revoked(), test_citation_and_source_span_are_immutable(), test_conflicting_numeric_source_spans_are_disclosed() (+18 more)

### Community 54 - "dependencies"
Cohesion: 0.29
Nodes (7): dependencies, react-dom@18.3.1, vite@6.3.5, @vitejs/plugin-react@4.6.0, react-dom, vite, @vitejs/plugin-react

### Community 55 - "vitest"
Cohesion: 0.25
Nodes (6): @testing-library/jest-dom@6.6.3, @testing-library/react@16.1.0, vitest@2.1.8, @testing-library/jest-dom, @testing-library/react, vitest

### Community 56 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, preview, test, test:watch, typecheck

### Community 57 - "rag_v4_citation/test_security_adversarial.py"
Cohesion: 0.29
Nodes (13): _child(), _locator(), _parent(), _principal(), test_answer_rejects_cross_tenant_citation_before_authorizer(), test_cross_document_parent_is_not_expanded(), test_cross_tenant_parent_is_not_even_sent_to_authorizer(), test_cross_version_parent_is_not_expanded() (+5 more)

### Community 58 - "admin.py"
Cohesion: 0.14
Nodes (53): AccessGrantRequest, AccessRequest, activate_user(), AdminApiState, approve_document_version(), _body(), _bump_policy_epoch(), _counts() (+45 more)

### Community 59 - "api/chat.py"
Cohesion: 0.27
Nodes (17): _anonymous_token(), _body(), _context(), create_conversation(), download_citation(), FeedbackRequest, get_conversation(), get_query_completion() (+9 more)

### Community 60 - "PromptDefinition"
Cohesion: 0.12
Nodes (5): default_prompt_registry(), _freeze(), PromptDefinition, PromptRegistry, PromptRegistryTests

### Community 61 - "tests/test_chat_api.py"
Cohesion: 0.15
Nodes (14): test_healthz_is_local_liveness_only(), test_identity_requires_bearer_credentials(), anonymous_conversation(), authenticated_headers(), request(), StubExecutor, test_anonymous_submit_status_completion_and_history_are_session_scoped(), test_authenticated_history_is_owner_only_and_revocation_denies_reuse() (+6 more)

### Community 62 - "dense.py"
Cohesion: 0.16
Nodes (12): Action, Classification, Decision, DocumentResource, Effect, _cosine(), DenseEvidence, DenseRetrievalResult (+4 more)

### Community 64 - "orchestrator.py"
Cohesion: 0.09
Nodes (10): NoopQueryExecutor, AnswerSynthesizer, BoundedOrchestrator, _evidence_from_result(), _GraphState, OrchestrationOutcome, _route(), _subqueries() (+2 more)

### Community 86 - "answer_baseline/test_behavior_component.py"
Cohesion: 0.09
Nodes (28): AnswerResult, AnswerStatus, DirectAnswerPipeline, _CapturingModel, _Model, test_direct_answer_context_includes_authorized_parent_runtime(), authorize(), test_real_hybrid_path_propagates_pdf_schema_end_to_end() (+20 more)

### Community 87 - "orchestration_langgraph/test_security_adversarial.py"
Cohesion: 0.13
Nodes (20): Answerer, Backend, call(), Clock, gateway(), Policy, principal(), request() (+12 more)

### Community 91 - "_make_case"
Cohesion: 0.16
Nodes (16): _DenseAsHybrid, evaluation_snapshot(), _make_case(), authorize(), load_validated_records(), test_all_golden_cases_run_through_v1_v3(), test_allowed_answer_has_no_unauthorized_retrieval_marker(), test_answered_case_keeps_citation_version_and_tenant_binding() (+8 more)

### Community 94 - "_make_retriever"
Cohesion: 0.08
Nodes (43): DenseRetriever, InMemoryDenseVectorIndex, _VectorRecord, HybridRetrievalConfig, InMemoryBM25Index, reciprocal_rank_fusion(), _resource(), test_cross_tenant_candidates_are_not_exposed() (+35 more)

### Community 95 - "AuthenticatedPrincipal"
Cohesion: 0.13
Nodes (7): AnonymousPrincipal, AuthenticatedPrincipal, _citation(), SourceFetchResult, _valid_locator(), _BM25Record, HybridRetriever

### Community 97 - "test_identity.py"
Cohesion: 0.15
Nodes (12): IdentityError, identity_error_handler(), make_service(), test_expired_session_is_rejected(), test_invalid_password_is_safe_auth_error(), test_mfa_is_required_for_privileged_role(), test_principal_rejects_extra_client_claims(), test_revoked_session_is_rejected() (+4 more)

### Community 98 - "test_tool_gateway.py"
Cohesion: 0.16
Nodes (21): _Backend, _call(), _Clock, _gateway(), _Policy, _principal(), _Resolvers, test_backend_exception_is_unavailable_without_raw_error() (+13 more)

### Community 99 - "AnswerDraft"
Cohesion: 0.26
Nodes (20): AnswerDraft, _Answerer, _Clock, _evidence(), _orchestrator(), _request(), test_answerer_error_is_returned_as_safe_error(), test_complex_route_splits_subqueries_and_preserves_bound() (+12 more)

### Community 100 - "SourceSpan"
Cohesion: 0.15
Nodes (17): SourceSpan, Citation, _citation(), _FusedCandidate, _AnswerModel, _pipeline(), allow(), _principal() (+9 more)

### Community 102 - "lifecycle.py"
Cohesion: 0.07
Nodes (30): _acl_digest(), ApprovalBlocked, ApprovalRecord, _chunk_digest(), _chunk_state(), DerivedIndex, DerivedIndexFailure, DerivedIndexRecord (+22 more)

### Community 103 - "IngestionService"
Cohesion: 0.12
Nodes (21): IngestionService, _active_document(), _principal(), _retriever(), test_dense_retrieval_returns_authorized_current_chunk_only(), test_explicit_deny_candidates_are_not_exposed(), test_forbidden_source_fetch_is_redacted_without_content_or_citation(), test_active_retrieval_to_evidence_verification_succeeds() (+13 more)

### Community 104 - "ModelPolicy"
Cohesion: 0.22
Nodes (16): ModelPolicy, test_mapping_loads_versioned_policy_without_credentials(), test_policy_rejects_credential_fields(), mapping(), route(), test_embedding_route_task_is_checked(), test_policy_version_is_required(), test_access_token_field_is_rejected() (+8 more)

### Community 106 - "InMemoryIdentityStore"
Cohesion: 0.05
Nodes (16): rate_limited(), DepartmentRecord, IdentityRecord, normalize_roles(), Role, SessionRecord, utc_z(), AuthenticationService (+8 more)

### Community 107 - "ToolResult"
Cohesion: 0.23
Nodes (19): OrchestrationRequest, OrchestrationStatus, QueryRoute, Answerer, Clock, evidence(), request(), run() (+11 more)

### Community 111 - "reset"
Cohesion: 0.07
Nodes (18): reset_state(), reset_state(), reset(), clean_state(), clean_state(), clean_state(), clean_state(), clean_state() (+10 more)

### Community 113 - "EvidenceVerifier"
Cohesion: 0.26
Nodes (18): EvidenceVerifier, VerificationRequest, allow_active(), citation(), test_authorization_callback_exception_fails_closed(), test_cross_tenant_evidence_is_denied_before_authorizer_invocation(), unexpected(), test_denied_result_does_not_leak_source_text() (+10 more)

### Community 114 - "answer_baseline/test_contract_integration.py"
Cohesion: 0.19
Nodes (15): _allow(), RecordingModel, RecordingRetriever, _setup(), test_citation_authorization_rejects_document_mismatch(), test_citation_authorization_rejects_non_active_status(), test_citation_authorization_rejects_non_current_version(), test_citation_authorization_rejects_revoked_source() (+7 more)

### Community 115 - "ingestion/_baseline.py"
Cohesion: 0.13
Nodes (14): graph_labels(), read(), RuntimeFailureOnRemove, service_with_index(), task(), test_task_and_handoff_keep_ingestion_provider_neutral(), test_cleanup_backend_error_is_wrapped_without_secret_leakage(), test_cross_tenant_document_lookup_is_denied() (+6 more)

### Community 116 - "answer_baseline/test_e2e_operational.py"
Cohesion: 0.17
Nodes (16): _allow(), FailingEmbedder, FailingReranker, FakeAnswerGateway, _setup(), test_operational_abstention_is_insufficient_evidence(), test_operational_conflicting_evidence_is_not_harmonized(), test_operational_denied_content_never_appears_in_failure_result() (+8 more)

### Community 117 - "CitationArtifact"
Cohesion: 0.15
Nodes (3): _document_state(), CitationArtifact, DurableChatRepository

### Community 119 - "guardrails/__init__.py"
Cohesion: 0.15
Nodes (6): _luhn_valid(), redact_sensitive_data(), redact_card(), RedactionResult, ToolDecision, validate_tool_request()

### Community 120 - "GeneratedAnswer"
Cohesion: 0.10
Nodes (25): GeneratedAnswer, _authorization(), FakeModelGateway, _pipeline(), test_direct_answer_returns_insufficient_without_calling_model_when_no_match(), test_direct_answer_returns_partial_for_mixed_claims(), test_direct_answer_returns_supported_answer_and_authorized_citation(), test_guardrail_failure_fails_closed_before_model_call() (+17 more)

### Community 121 - "normalize_user_input"
Cohesion: 0.17
Nodes (3): normalize_user_input(), GuardrailBehaviorTests, GuardrailSecurityAdversarialTests

### Community 123 - "orchestration_langgraph/test_contract_integration.py"
Cohesion: 0.18
Nodes (16): Backend, call(), Clock, gateway(), Policy, principal(), Resolvers, test_chunk_read_contract_accepts_only_chunk_id_shape() (+8 more)

### Community 124 - "validate_output"
Cohesion: 0.26
Nodes (8): _citation(), detect_prompt_injection(), GuardrailResult, _inspect_text(), _normalize_text(), _sensitive_terms(), _terms(), validate_output()

### Community 125 - "backend_boot/_baseline.py"
Cohesion: 0.06
Nodes (8): backend_boot_task(), compile_sources_without_writes(), read(), task_packet(), tree(), BackendBootstrapContractTests, BackendBootstrapOperationalTests, BackendBootstrapSecurityTests

### Community 126 - "BackendBootstrapBehaviorTests"
Cohesion: 0.12
Nodes (8): assignment(), calls(), function(), literal(), pyproject(), route_calls(), route_path(), BackendBootstrapBehaviorTests

### Community 127 - "rag_hybrid/test_security_adversarial.py"
Cohesion: 0.15
Nodes (16): AccessGrant, _normalize_action(), _catalog(), _FailingEmbeddingAdapter, _FailingRerankerAdapter, _gateway_with_failure(), test_acl_denied_candidates_are_absent_from_dense_and_bm25(), test_bm25_filters_unauthorized_high_frequency_candidates_before_scoring() (+8 more)

### Community 130 - "dataclasses"
Cohesion: 0.14
Nodes (7): AssembledContext, ContextLimitError, estimate_tokens(), PromptMessage, _render_evidence(), _safe_text(), _safe_value()

### Community 131 - "Claim"
Cohesion: 0.15
Nodes (21): Claim, EvidenceRecord, SourceSpan, citation(), test_authorization_callback_error_fails_closed(), test_current_active_version_is_required_by_authorization_attestation(), test_negation_mismatch_is_conflicting_not_supported(), test_numeric_mismatch_is_conflicting_not_supported() (+13 more)

### Community 132 - "orchestration_langgraph/test_behavior_component.py"
Cohesion: 0.25
Nodes (15): Answerer, Clock, evidence(), request(), run(), test_compiles_a_state_graph_with_expected_nodes(), test_complex_loop_caps_subqueries_and_tool_calls_at_four(), test_complex_query_splits_into_distinct_subqueries() (+7 more)

### Community 134 - "cache_memory/test_e2e_operational.py"
Cohesion: 0.13
Nodes (25): ConversationMessage, InMemoryConversationMemory, test_conversation_delete_removes_body_and_blocks_recreation_in_old_scope(), test_conversation_memory_expires_anonymous_sessions_and_revocation_is_fail_closed(), test_conversation_memory_is_scoped_bounded_and_repr_redacts_body(), test_contract_memory_read_requires_the_authoritative_current_scope(), Clock, FakeInvalidationBus (+17 more)

### Community 137 - "test_cache_memory.py"
Cohesion: 0.33
Nodes (9): Clock, response_key(), scope(), test_cache_delete_is_explicit(), test_cache_expires_and_rejects_unbounded_ttl_or_value(), test_cache_key_contains_security_scope_but_not_raw_query(), test_cache_requires_exact_current_scope_and_isolates_tenant_and_principal(), test_document_change_invalidates_broad_corpus_cache_but_not_other_version() (+1 more)

### Community 138 - "authorization/test_behavior_component.py"
Cohesion: 0.32
Nodes (5): ConversationResource, AuthorizationBehaviorTests, document(), evaluator(), principal()

### Community 140 - "ChatService"
Cohesion: 0.35
Nodes (4): ChatActor, ChatService, _error(), _fingerprint()

### Community 142 - "cache_memory/test_behavior_component.py"
Cohesion: 0.18
Nodes (23): InMemoryScopedCache, test_cache_invalidation_hooks_remove_only_matching_scope(), Clock, make_key(), make_scope(), test_broad_acl_invalidation_removes_all_versions_in_one_tenant(), test_cache_expires_at_the_exact_ttl_deadline(), test_cache_rejects_invalid_ttl_and_oversize_values() (+15 more)

### Community 143 - "test_authorization.py"
Cohesion: 0.40
Nodes (15): document(), evaluator(), principal(), test_acl_can_assign_employee_and_explicit_deny_wins_for_chairman(), test_anonymous_is_public_only(), test_chairman_is_read_only(), test_conversation_body_is_owner_only(), test_conversation_requires_conversation_resource() (+7 more)

### Community 144 - "eval_001_runner.py"
Cohesion: 0.19
Nodes (13): _aggregate(), _AnswerModel, _Case, evaluate(), _mean(), _percentile(), _principal(), render_report() (+5 more)

### Community 146 - "build_secure_context"
Cohesion: 0.16
Nodes (5): build_secure_context(), RetrievedEvidence, PromptOperationalTests, PromptSecurityAdversarialTests, test_secure_context_escapes_parent_prompt_injection_as_untrusted_content()

### Community 147 - "evidence/__init__.py"
Cohesion: 0.19
Nodes (8): ClaimVerification, _is_negative(), _numeric_conflict(), _numeric_terms(), _relation(), _terms(), VerificationOutcome, VerificationResult

### Community 148 - "upload"
Cohesion: 0.18
Nodes (15): upload(), test_anonymous_cannot_upload(), test_chairman_cannot_approve(), test_chairman_cannot_upload(), test_cross_tenant_document_is_not_revealed(), test_employee_cannot_provision_accounts(), test_employee_cannot_upload(), test_policy_store_outage_denies_admin_action() (+7 more)

### Community 149 - "json"
Cohesion: 0.16
Nodes (4): load_records(), test_dashboard_has_api_and_security_panels(), test_dashboard_is_valid_json(), test_rag002_task_registry_keeps_retrieval_validation_and_scope()

### Community 151 - "rag_v4_citation/test_contract_integration.py"
Cohesion: 0.10
Nodes (21): DOCXLocator, _ImmutableModel, PDFLocator, XLSXLocator, _answer_citation(), AnswerCitation, _authorization_matches(), _expired() (+13 more)

### Community 153 - "make_manifest"
Cohesion: 0.11
Nodes (23): ScanReport, UploadManifest, make_manifest(), test_rejected_scan_is_terminal_and_not_retrievable(), test_approval_expiry_blocks_publication(), test_doc_is_rejected(), test_internal_upload_requires_department(), test_non_private_source_is_rejected() (+15 more)

### Community 156 - "ScopedCacheKey"
Cohesion: 0.12
Nodes (5): _component(), ScopedCacheAdapter, ScopedCacheKey, FakeProvider, test_provider_neutral_fake_preserves_exact_scope_checks()

### Community 158 - "feedback/service.py"
Cohesion: 0.16
Nodes (7): FeedbackRecord, FeedbackRepository, FeedbackReview, FeedbackService, InMemoryFeedbackRepository, test_feedback_replay_is_idempotent_but_tenant_bound(), test_feedback_review_projection_has_no_actor_comment_or_body()

### Community 159 - "EgressMode"
Cohesion: 0.16
Nodes (20): ModelEgressDenied, ModelUnavailable, EgressMode, provider(), test_external_internal_requires_dpa(), test_external_internal_requires_residency(), test_external_provider_requires_retention_policy(), test_external_unapproved_provider_is_denied() (+12 more)

### Community 160 - "active"
Cohesion: 0.21
Nodes (16): active(), staged(), test_derived_cleanup_failure_still_denies_retrieval(), test_derived_index_cannot_authorize_non_active_version(), test_legal_hold_blocks_permanent_delete(), test_revoked_version_cannot_be_retrieved_from_derived_state(), test_root_chunk_without_acl_fails_closed(), test_staging_index_cannot_be_retrieved() (+8 more)

### Community 161 - "env.py"
Cohesion: 0.19
Nodes (4): _database_url(), run_migrations_offline(), run_migrations_online(), DatabaseMigrationSmokeTests

### Community 165 - "ingestion/test_behavior_component.py"
Cohesion: 0.15
Nodes (12): make_chunks(), test_child_acl_broadening_is_denied(), test_approval_expiry_blocks_processing(), test_empty_processing_input_is_rejected(), test_new_active_version_supersedes_previous_version(), test_publish_activates_authoritative_version_and_chunks(), test_review_one_and_processing_require_parent_acl(), test_review_one_requires_clean_scan() (+4 more)

### Community 169 - "admin_api/test_contract_integration.py"
Cohesion: 0.16
Nodes (12): clean_state(), test_account_response_does_not_return_password(), test_approval_schema_requires_explicit_stage(), test_job_status_contains_redacted_progress_only(), test_mutating_post_requires_idempotency_key(), test_upload_accepts_docx_mime_inference(), test_upload_accepts_xlsx_mime_inference(), test_upload_idempotency_rejects_a_different_fingerprint() (+4 more)

### Community 170 - "test_admin_api_contract.py"
Cohesion: 0.15
Nodes (11): clean_state(), test_account_response_does_not_return_password(), test_approval_schema_requires_explicit_stage(), test_existing_sign_in_contract_remains_under_auth_prefix(), test_job_status_contains_redacted_progress_only(), test_mutating_post_requires_idempotency_key(), test_problem_response_uses_safe_media_type_for_anonymous_admin_call(), test_upload_accepts_docx_mime_inference() (+3 more)

### Community 171 - "admin_api/test_behavior_component.py"
Cohesion: 0.20
Nodes (10): _prepare_review_two_without_index_ack(), test_manager_activates_provisioned_account(), test_manager_completes_two_review_publication(), test_manager_provisions_inactive_employee(), test_manager_uploads_into_quarantine(), test_publish_requires_acknowledged_index(), test_quarantined_document_is_not_readable(), test_review_one_requires_clean_scan() (+2 more)

### Community 175 - "UUID"
Cohesion: 0.22
Nodes (5): test_anonymous_is_denied_dashboard_and_feedback(), test_feedback_review_is_private_bounded_and_replay_does_not_duplicate(), test_management_roles_can_read_empty_dashboard_and_feedback(), test_non_management_roles_are_denied_dashboard_and_feedback(), test_policy_outage_fails_closed_for_both_management_reads()

### Community 176 - "validated"
Cohesion: 0.33
Nodes (9): IndexManifest, validated(), test_manifest_checksum_mismatch_blocks_staging(), test_manifest_count_mismatch_blocks_staging(), test_publication_requires_index_ack(), test_index_ack_is_a_publication_gate(), test_second_review_is_required_after_index_ack(), test_index_ack_is_required_before_publication() (+1 more)

### Community 177 - "test_ingestion_behavior.py"
Cohesion: 0.22
Nodes (8): test_acknowledged_index_is_still_not_active(), test_clean_review_one_allows_processing(), test_processing_inherits_parent_acl(), test_publishing_new_version_supersedes_previous_version(), test_review_one_requires_clean_scan(), test_revoke_active_version_removes_retrieval(), test_second_review_and_publish_make_version_active(), test_soft_delete_isolates_all_versions()

## Knowledge Gaps
- **1 isolated node(s):** `enterprise-agentic-rag-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 887 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **60 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AuthenticatedPrincipal` connect `AuthenticatedPrincipal` to `authorization/test_behavior_component.py`, `ChatService`, `identity.py`, `AuthenticatedPrincipal`, `test_authorization.py`, `eval_001_runner.py`, `hybrid.py`, `InMemoryPolicyStore`, `rag_v4_citation/test_contract_integration.py`, `ChunkMetadata`, `authorization/test_contract_integration.py`, `chat_api/test_contract_integration.py`, `chat_api/test_behavior_component.py`, `key`, `chat_api/test_security_adversarial.py`, `ToolResult`, `CacheScope`, `rag_v4_citation/test_e2e_operational.py`, `rag_v4_citation/test_security_adversarial.py`, `admin.py`, `api/chat.py`, `dense.py`, `answer_baseline/test_behavior_component.py`, `orchestration_langgraph/test_security_adversarial.py`, `_make_retriever`, `test_identity.py`, `test_tool_gateway.py`, `SourceSpan`, `IngestionService`, `InMemoryIdentityStore`, `orchestration_langgraph/test_contract_integration.py`, `rag_hybrid/test_security_adversarial.py`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Are the 45 inferred relationships involving `IngestionService` (e.g. with `reset_state()` and `test_active_retrieval_to_evidence_verification_succeeds()`) actually correct?**
  _`IngestionService` has 45 INFERRED edges - model-reasoned connections that need verification._
- **What connects `enterprise-agentic-rag-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `audit.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08333333333333333 - nodes in this community are weakly interconnected._
- **Why does `IngestionService` connect `IngestionService` to `active`, `make_manifest`, `lifecycle.py`, `reset`, `validated`, `eval_001_runner.py`, `new_service`, `ingestion/_baseline.py`, `_make_retriever`, `_make_case`, `dense.py`, `rag_hybrid/test_security_adversarial.py`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Are the 47 inferred relationships involving `DataClassification` (e.g. with `ModelEgressDenied` and `ModelGateway`) actually correct?**
  _`DataClassification` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Should `compose` be split into smaller, more focused modules?**
  _Cohesion score 0.05478750640040963 - nodes in this community are weakly interconnected._