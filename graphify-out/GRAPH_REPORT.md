# Graph Report - enterprise-agentic-rag-harness  (2026-11-11)

## Corpus Check
- 261 files · ~217,944 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 68 file(s) not represented in the graph (top: (none) 53, .toml 9, .example 2)

## Summary
- 3630 nodes · 10842 edges · 167 communities (116 shown, 51 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 1174 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8a8c2ee3`
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
- unittest
- identity.py
- AuthenticatedPrincipal
- InMemoryConversationMemory
- postgres
- postgres
- new_service
- package.json
- test_hybrid_retrieval.py
- InMemoryPolicyStore
- cache_memory/test_contract_integration.py
- compilerOptions
- DocumentVersionMetadata
- inherit_acl
- rag_v4_citation/test_contract_integration.py
- authorization/test_contract_integration.py
- PolicyEnforcementPoint
- chat_api/test_contract_integration.py
- test_models.py
- chat_api/test_behavior_component.py
- _evaluation_harness.py
- GraphifyOperationalTests
- auth
- chat_api/test_security_adversarial.py
- steps
- BehaviorComponentTests
- ContractIntegrationTests
- SecurityAdversarialTests
- rules
- rag_hybrid/test_security_adversarial.py
- ModelProviderError
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
- pytest
- dependencies
- vitest
- scripts
- identity/models.py
- admin.py
- api/chat.py
- PromptDefinition
- tests/test_chat_api.py
- make_manifest
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
- test_dense_retrieval.py
- ChunkMetadata
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
- main.py
- quarantine
- answer_baseline/test_contract_integration.py
- field_validator
- answer_baseline/test_e2e_operational.py
- CitationArtifact
- expand_parent_context
- guardrails/__init__.py
- answer_baseline/test_security_adversarial.py
- normalize_user_input
- ._authorized
- orchestration_langgraph/test_contract_integration.py
- validate_output
- backend_boot/_baseline.py
- BackendBootstrapBehaviorTests
- _make_retriever
- run_local_guardrail_pipeline
- Citation
- orchestration/context.py
- Claim
- orchestration_langgraph/test_behavior_component.py
- test_knowledge_security.py
- cache_memory/test_e2e_operational.py
- to_qdrant_payload
- env.py
- test_cache_memory.py
- authorization/test_behavior_component.py
- test_answer_citation_schema.py
- ChatService
- GeneratedAnswer
- cache_memory/test_behavior_component.py
- test_authorization.py
- ingestion/test_behavior_component.py
- read
- build_secure_context
- InMemoryAuditSink
- ingestion/test_security_adversarial.py
- json
- rag/__init__.py
- KnowledgeOperationalTests
- UUID
- SecureContextBuilder
- IdentityContractTests
- ScopedCacheKey
- feedback/service.py
- DataClassification
- InMemoryDerivedIndex
- cache_memory/test_security_adversarial.py
- PromptBehaviorComponentTests
- ._now
- DerivedIndex
- eval_001_runner.py

## God Nodes (most connected - your core abstractions)
1. `IngestionService` - 116 edges
2. `DataClassification` - 93 edges
3. `auth()` - 87 edges
4. `AuthenticatedPrincipal` - 86 edges
5. `request()` - 86 edges
6. `new_service()` - 85 edges
7. `_active_document()` - 78 edges
8. `CacheScope` - 68 edges
9. `ChunkMetadata` - 67 edges
10. `_principal()` - 65 edges

## Surprising Connections (you probably didn't know these)
- `authorize()` --calls--> `AuthorizationDecision`  [INFERRED]
  tests/evaluation/eval_001_runner.py → backend/app/evidence/verifier.py
- `authorize()` --calls--> `AuthorizationDecision`  [INFERRED]
  tests/integration/test_answer_baseline.py → backend/app/evidence/verifier.py
- `authorize()` --calls--> `AuthorizationDecision`  [INFERRED]
  tests/integration/test_answer_citation_schema.py → backend/app/evidence/verifier.py
- `authorize()` --calls--> `AuthorizationDecision`  [INFERRED]
  tests/qa/answer_baseline/test_contract_integration.py → backend/app/evidence/verifier.py
- `authorize()` --calls--> `AuthorizationDecision`  [INFERRED]
  tests/qa/answer_baseline/test_e2e_operational.py → backend/app/evidence/verifier.py

## Import Cycles
- 2-file cycle: `backend/app/api/admin.py -> backend/app/api/identity.py -> backend/app/api/admin.py`
- 2-file cycle: `backend/app/api/chat.py -> backend/app/api/identity.py -> backend/app/api/chat.py`
- 3-file cycle: `backend/app/api/admin.py -> backend/app/api/identity.py -> backend/app/api/chat.py -> backend/app/api/admin.py`

## Communities (167 total, 51 thin omitted)

### Community 0 - "audit.py"
Cohesion: 0.09
Nodes (14): append_audit_event(), AuditEvent, AuditSink, AuditSinkUnavailable, redact_metadata(), _safe_code(), _safe_identifier(), _utc_z() (+6 more)

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
Cohesion: 0.05
Nodes (7): read(), task(), tasks(), AuditBehaviorTests, AuditContractTests, AuditOperationalTests, AuditSecurityTests

### Community 5 - "section"
Cohesion: 0.10
Nodes (7): json_blocks(), require_all(), section(), BehaviorComponentTests, ContractIntegrationTests, E2EOperationalTests, SecurityAdversarialTests

### Community 6 - "read"
Cohesion: 0.06
Nodes (7): dashboard(), read(), task(), MonitoringBehaviorTests, MonitoringContractTests, MonitoringOperationalTests, MonitoringSecurityTests

### Community 7 - "read_frontend"
Cohesion: 0.09
Nodes (6): load_frontend_json(), read(), read_frontend(), FrontendBehaviorComponentTests, FrontendContractIntegrationTests, FrontendSecurityAdversarialTests

### Community 8 - "read"
Cohesion: 0.09
Nodes (4): read(), GraphifyBehaviorTests, GraphifyContractTests, GraphifySecurityTests

### Community 9 - "otel-collector-config.yaml"
Cohesion: 0.06
Nodes (32): action, key, actions, send_batch_size, timeout, exporters, prometheus, endpoint (+24 more)

### Community 10 - "prometheus"
Cohesion: 0.06
Nodes (30): command, image, ports, read_only, security_opt, volumes, depends_on, image (+22 more)

### Community 13 - "identity.py"
Cohesion: 0.27
Nodes (9): _bearer_token(), current_identity(), _record(), _record_identity_error(), _request_context(), sign_in(), sign_out(), SignInRequest (+1 more)

### Community 14 - "AuthenticatedPrincipal"
Cohesion: 0.08
Nodes (15): AccessGrant, AnonymousPrincipal, AuthorizationDenied, AuthorizationEvaluator, deny(), Classification, Decision, DocumentResource (+7 more)

### Community 15 - "InMemoryConversationMemory"
Cohesion: 0.14
Nodes (3): InvalidationEvent, InMemoryConversationMemory, FakeMemoryRepository

### Community 16 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, networks (+12 more)

### Community 17 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, networks (+12 more)

### Community 18 - "new_service"
Cohesion: 0.14
Nodes (30): active(), new_service(), staged(), test_acknowledged_index_is_still_not_active(), test_publishing_new_version_supersedes_previous_version(), test_rejected_scan_is_terminal_and_not_retrievable(), test_review_one_requires_clean_scan(), test_revoke_active_version_removes_retrieval() (+22 more)

### Community 19 - "package.json"
Cohesion: 0.13
Nodes (19): devDependencies, eslint@9.17.0, jsdom@25.0.1, @types/node@22.10.5, @types/react@18.3.18, @types/react-dom@18.3.5, typescript@5.7.2, engines (+11 more)

### Community 20 - "test_hybrid_retrieval.py"
Cohesion: 0.11
Nodes (15): Action, EmbeddingAdapter, EmbeddingRequest, EmbeddingResult, RerankerAdapter, RerankerResult, ModelRoute, ProviderPolicy (+7 more)

### Community 21 - "InMemoryPolicyStore"
Cohesion: 0.41
Nodes (4): AuthorizationSecurityAdversarialTests, document(), evaluator(), principal()

### Community 22 - "cache_memory/test_contract_integration.py"
Cohesion: 0.36
Nodes (8): make_key(), make_scope(), test_contract_delete_event_invalidates_matching_scope_without_cross_tenant_reach(), test_contract_document_change_invalidates_broad_scope_and_selected_version(), test_contract_invalid_event_shapes_fail_closed_at_the_boundary(), test_contract_memory_read_requires_the_authoritative_current_scope(), test_contract_request_fingerprint_changes_for_query_model_and_prompt(), test_contract_scope_carries_every_authorization_and_corpus_partition()

### Community 23 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+10 more)

### Community 24 - "DocumentVersionMetadata"
Cohesion: 0.11
Nodes (9): DocumentVersionMetadata, test_document_version_identity_is_stable(), test_document_version_requires_private_source(), test_hashes_are_normalized(), test_version_contract_has_immutable_version_number(), test_version_contract_supports_publication_states(), make_document(), make_version() (+1 more)

### Community 25 - "inherit_acl"
Cohesion: 0.22
Nodes (4): make_child(), make_parent(), KnowledgeContractIntegrationTests, KnowledgeSecurityAdversarialTests

### Community 26 - "rag_v4_citation/test_contract_integration.py"
Cohesion: 0.17
Nodes (10): _allow(), _CapturingModel, _principal(), _StaticRetriever, test_answer_pipeline_adds_authorized_parent_to_secure_context(), test_policy_epoch_is_propagated_to_ranked_and_expanded_citations(), test_qdrant_projection_contains_discriminated_source_locator(), test_retrieval_result_keeps_backward_compatible_empty_parent_context() (+2 more)

### Community 27 - "authorization/test_contract_integration.py"
Cohesion: 0.27
Nodes (4): AuthorizationContractIntegrationTests, document(), evaluator(), principal()

### Community 28 - "PolicyEnforcementPoint"
Cohesion: 0.32
Nodes (4): AuthorizationOperationalTests, document(), evaluator(), principal()

### Community 29 - "chat_api/test_contract_integration.py"
Cohesion: 0.12
Nodes (19): job_payload(), JobState, anonymous_conversation(), authenticated_conversation(), Clock, Executor, Maintenance, make_service() (+11 more)

### Community 30 - "test_models.py"
Cohesion: 0.13
Nodes (39): ModelGateway, ModelUnavailable, ModelTask, FakeEmbedding, policy(), provider(), route(), test_approved_local_fallback_can_handle_internal_data() (+31 more)

### Community 31 - "chat_api/test_behavior_component.py"
Cohesion: 0.14
Nodes (20): AnswerState, QueryCompletion, anonymous_conversation(), authenticated_conversation(), Clock, Executor, Maintenance, make_service() (+12 more)

### Community 32 - "_evaluation_harness.py"
Cohesion: 0.14
Nodes (19): answer_correctness(), citation_accuracy(), evaluate_case(), load_records(), mean_reciprocal_rank(), ndcg_at_k(), no_answer_accuracy(), recall_at_k() (+11 more)

### Community 33 - "GraphifyOperationalTests"
Cohesion: 0.15
Nodes (5): graph(), graphify_bin(), run_graphify(), GraphifyOperationalTests, run_graph_query()

### Community 34 - "auth"
Cohesion: 0.06
Nodes (100): ScanReport, ScanVerdict, add_user(), auth(), key(), prepare_review_two(), publish(), request() (+92 more)

### Community 35 - "chat_api/test_security_adversarial.py"
Cohesion: 0.16
Nodes (18): anonymous_conversation(), authenticated_conversation(), Clock, Executor, Maintenance, make_service(), principal(), public_document() (+10 more)

### Community 36 - "steps"
Cohesion: 0.15
Nodes (12): jobs, validate, name, on, pull_request, workflow_dispatch, run, uses (+4 more)

### Community 40 - "rules"
Cohesion: 0.17
Nodes (11): runbook, summary, groups, name, rules, severity, alert, annotations (+3 more)

### Community 41 - "rag_hybrid/test_security_adversarial.py"
Cohesion: 0.15
Nodes (15): RerankerRequest, DeterministicRerankerAdapter, _tokens(), _gateway(), test_reranker_request_rejects_blank_document_fields(), test_reranker_request_requires_documents(), test_reranker_request_requires_query(), test_reranker_gateway_contract_passes_request_route_and_timeout() (+7 more)

### Community 42 - "ModelProviderError"
Cohesion: 0.17
Nodes (6): ModelProviderError, RankedDocument, FakeReranker, test_ranked_document_preserves_identifier_and_score(), ScriptedReranker, test_reranker_result_keeps_selected_route()

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
Cohesion: 0.07
Nodes (18): CacheScope, StaleScopeError, ActorKind, AnonymousSession, CheckpointRepository, ConversationRecord, ConversationRepository, ConversationView (+10 more)

### Community 47 - "test_knowledge_database.py"
Cohesion: 0.26
Nodes (11): migration_text(), test_existing_db_contract_has_active_index_guard(), test_existing_db_contract_has_chunks_table(), test_existing_db_contract_has_composite_parent_fk(), test_existing_db_contract_has_document_versions_table(), test_existing_db_contract_has_documents_table(), test_existing_db_contract_has_immutable_version_uniqueness(), test_existing_db_contract_has_private_source_constraint() (+3 more)

### Community 48 - "chat_api/test_e2e_operational.py"
Cohesion: 0.23
Nodes (15): anonymous_conversation(), HttpExecutor, request(), sign_in(), test_http_anonymous_lifecycle_and_session_isolation(), test_http_authenticated_history_and_job_are_owner_only(), test_http_citation_preview_and_download_reauthorize_after_revocation(), test_http_deadline_failure_is_safe_and_has_no_answer() (+7 more)

### Community 49 - "rag_v4_citation/test_e2e_operational.py"
Cohesion: 0.19
Nodes (15): _allow(), _answer(), _locator(), _Model, _principal(), _StaticRetriever, test_answer_workflow_consumes_parent_context_without_ranking_parent(), test_audience_and_expiry_survive_citation_delivery() (+7 more)

### Community 50 - "App.tsx"
Cohesion: 0.27
Nodes (5): react@18.3.1, App(), supportedRoles, appConfig, react

### Community 51 - "datasources"
Cohesion: 0.22
Nodes (8): apiVersion, datasources, access, editable, isDefault, name, type, url

### Community 52 - "monitoring/prometheus.yml"
Cohesion: 0.22
Nodes (8): global, evaluation_interval, scrape_interval, rule_files, scrape_configs, job_name, static_configs, targets

### Community 53 - "pytest"
Cohesion: 0.11
Nodes (27): UploadManifest, HybridRetrievalConfig, validated(), test_clean_review_one_allows_processing(), test_processing_inherits_parent_acl(), test_doc_is_rejected(), test_internal_upload_requires_department(), test_manifest_checksum_mismatch_blocks_staging() (+19 more)

### Community 54 - "dependencies"
Cohesion: 0.29
Nodes (7): dependencies, react-dom@18.3.1, vite@6.3.5, @vitejs/plugin-react@4.6.0, react-dom, vite, @vitejs/plugin-react

### Community 55 - "vitest"
Cohesion: 0.25
Nodes (6): @testing-library/jest-dom@6.6.3, @testing-library/react@16.1.0, vitest@2.1.8, @testing-library/jest-dom, @testing-library/react, vitest

### Community 56 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, preview, test, test:watch, typecheck

### Community 57 - "identity/models.py"
Cohesion: 0.13
Nodes (6): Role, utc_z(), IdentityErrorPassthrough, now_utc(), hash_secret(), verify_secret()

### Community 58 - "admin.py"
Cohesion: 0.16
Nodes (46): AccessGrantRequest, AccessRequest, activate_user(), AdminApiState, approve_document_version(), _body(), _bump_policy_epoch(), create_department() (+38 more)

### Community 59 - "api/chat.py"
Cohesion: 0.29
Nodes (16): _anonymous_token(), _body(), _context(), create_conversation(), download_citation(), FeedbackRequest, get_conversation(), get_query_completion() (+8 more)

### Community 60 - "PromptDefinition"
Cohesion: 0.12
Nodes (5): default_prompt_registry(), _freeze(), PromptDefinition, PromptRegistry, PromptRegistryTests

### Community 61 - "tests/test_chat_api.py"
Cohesion: 0.10
Nodes (20): reset_state(), _maintenance_probe(), reset_state(), test_healthz_is_local_liveness_only(), test_identity_requires_bearer_credentials(), anonymous_conversation(), authenticated_headers(), clean_state() (+12 more)

### Community 62 - "make_manifest"
Cohesion: 0.14
Nodes (13): Clock, make_manifest(), graph_labels(), read(), task(), test_failed_new_publication_preserves_previous_active_version(), test_job_contract_keeps_attempt_and_tenant_scope(), test_legacy_doc_and_xls_are_rejected() (+5 more)

### Community 64 - "orchestrator.py"
Cohesion: 0.09
Nodes (13): AssembledContext, AnswerSynthesizer, BoundedOrchestrator, _evidence_from_result(), _GraphState, OrchestrationOutcome, OrchestrationRequest, OrchestrationStatus (+5 more)

### Community 86 - "answer_baseline/test_behavior_component.py"
Cohesion: 0.16
Nodes (19): DirectAnswerPipeline, _authorization(), FakeModelGateway, _pipeline(), RaisingRetriever, RaisingVerifier, StaticRetriever, test_constructor_rejects_non_positive_top_k() (+11 more)

### Community 87 - "orchestration_langgraph/test_security_adversarial.py"
Cohesion: 0.13
Nodes (20): Answerer, Backend, call(), Clock, gateway(), Policy, principal(), request() (+12 more)

### Community 91 - "_make_case"
Cohesion: 0.22
Nodes (15): evaluation_snapshot(), _make_case(), authorize(), load_validated_records(), test_all_golden_cases_run_through_v1_v3(), test_allowed_answer_has_no_unauthorized_retrieval_marker(), test_answered_case_keeps_citation_version_and_tenant_binding(), test_dataset_contains_permission_negative_and_cross_tenant_cases() (+7 more)

### Community 94 - "test_dense_retrieval.py"
Cohesion: 0.09
Nodes (31): InMemoryPolicyStore, PolicyEnforcementPoint, _cosine(), DenseRetriever, InMemoryDenseVectorIndex, InMemoryBM25Index, _resource(), test_cross_tenant_candidates_are_not_exposed() (+23 more)

### Community 96 - "ChunkMetadata"
Cohesion: 0.11
Nodes (13): ChunkMetadata, DocumentMetadata, DOCXLocator, _ImmutableModel, SourceSpan, test_active_chunk_requires_acl_metadata(), test_chunk_accepts_source_provenance(), test_chunk_rejects_reversed_pages() (+5 more)

### Community 97 - "test_identity.py"
Cohesion: 0.17
Nodes (13): IdentityError, rate_limited(), AuthenticationService, make_service(), test_expired_session_is_rejected(), test_invalid_password_is_safe_auth_error(), test_mfa_is_required_for_privileged_role(), test_principal_rejects_extra_client_claims() (+5 more)

### Community 98 - "test_tool_gateway.py"
Cohesion: 0.16
Nodes (21): _Backend, _call(), _Clock, _gateway(), _Policy, _principal(), _Resolvers, test_backend_exception_is_unavailable_without_raw_error() (+13 more)

### Community 99 - "AnswerDraft"
Cohesion: 0.26
Nodes (20): AnswerDraft, _Answerer, _Clock, _evidence(), _orchestrator(), _request(), test_answerer_error_is_returned_as_safe_error(), test_complex_route_splits_subqueries_and_preserves_bound() (+12 more)

### Community 100 - "SourceSpan"
Cohesion: 0.09
Nodes (22): PDFLocator, Citation, DenseEvidence, DenseRetrievalResult, _BM25Record, _citation(), _FusedCandidate, HybridEvidence (+14 more)

### Community 102 - "lifecycle.py"
Cohesion: 0.13
Nodes (15): _acl_digest(), ApprovalBlocked, _chunk_digest(), IndexManifest, IndexPublication, IndexPublicationStatus, IngestionError, JobStage (+7 more)

### Community 103 - "IngestionService"
Cohesion: 0.13
Nodes (21): IngestionService, _active_document(), _principal(), _retriever(), test_dense_retrieval_returns_authorized_current_chunk_only(), test_explicit_deny_candidates_are_not_exposed(), test_forbidden_source_fetch_is_redacted_without_content_or_citation(), test_active_retrieval_to_evidence_verification_succeeds() (+13 more)

### Community 104 - "ModelPolicy"
Cohesion: 0.16
Nodes (17): ModelPolicy, test_mapping_loads_versioned_policy_without_credentials(), test_policy_rejects_credential_fields(), mapping(), task(), test_embedding_route_task_is_checked(), test_policy_version_is_required(), test_access_token_field_is_rejected() (+9 more)

### Community 106 - "InMemoryIdentityStore"
Cohesion: 0.08
Nodes (7): DepartmentRecord, IdentityRecord, normalize_roles(), SessionRecord, IdentityStore, InMemoryIdentityStore, test_noncanonical_role_cannot_create_identity()

### Community 107 - "ToolResult"
Cohesion: 0.32
Nodes (16): Answerer, Clock, evidence(), request(), run(), test_answer_provider_failure_returns_error_without_exception_to_user(), test_deadline_timeout_is_a_visible_insufficient_outcome(), test_second_retrieval_round_recovers_a_temporarily_insufficient_answer() (+8 more)

### Community 112 - "main.py"
Cohesion: 0.10
Nodes (4): get_settings(), Settings, healthz(), identity_error_handler()

### Community 113 - "quarantine"
Cohesion: 0.10
Nodes (21): quarantine(), test_upload_starts_quarantined_and_not_retrievable(), test_audit_sink_receives_lifecycle_events_without_content(), test_failed_maintenance_can_be_recovered_after_cleanup(), test_non_retryable_failure_is_terminal(), test_only_one_maintenance_window_is_active(), test_retry_is_bounded_and_preserves_checksum(), test_retry_with_changed_checksum_is_denied() (+13 more)

### Community 114 - "answer_baseline/test_contract_integration.py"
Cohesion: 0.17
Nodes (16): _allow(), authorize(), RecordingModel, RecordingRetriever, _setup(), test_citation_authorization_rejects_document_mismatch(), test_citation_authorization_rejects_non_active_status(), test_citation_authorization_rejects_non_current_version() (+8 more)

### Community 116 - "answer_baseline/test_e2e_operational.py"
Cohesion: 0.14
Nodes (19): _allow(), authorize(), FailingEmbedder, FailingReranker, FakeAnswerGateway, _setup(), test_operational_abstention_is_insufficient_evidence(), test_operational_conflicting_evidence_is_not_harmonized() (+11 more)

### Community 118 - "expand_parent_context"
Cohesion: 0.08
Nodes (57): _active(), ChildEvidence, _coerce_child(), _coerce_parent(), _construct(), expand_parent_context(), _identity(), _index_parents() (+49 more)

### Community 119 - "guardrails/__init__.py"
Cohesion: 0.15
Nodes (6): _luhn_valid(), redact_sensitive_data(), redact_card(), RedactionResult, ToolDecision, validate_tool_request()

### Community 120 - "answer_baseline/test_security_adversarial.py"
Cohesion: 0.19
Nodes (16): _allow(), authorize(), FakeModelGateway, _pipeline(), test_cross_tenant_evidence_is_absent_from_dense_bm25_and_answer(), test_direct_prompt_injection_is_denied_before_retrieval_and_model(), test_duplicate_and_unknown_citation_ids_do_not_duplicate_or_leak_metadata(), test_indirect_prompt_injection_is_removed_before_model_context() (+8 more)

### Community 121 - "normalize_user_input"
Cohesion: 0.17
Nodes (3): normalize_user_input(), GuardrailBehaviorTests, GuardrailSecurityAdversarialTests

### Community 122 - "._authorized"
Cohesion: 0.17
Nodes (4): _citation(), _uuid(), _valid_locator(), _VectorRecord

### Community 123 - "orchestration_langgraph/test_contract_integration.py"
Cohesion: 0.18
Nodes (16): Backend, call(), Clock, gateway(), Policy, principal(), Resolvers, test_chunk_read_contract_accepts_only_chunk_id_shape() (+8 more)

### Community 124 - "validate_output"
Cohesion: 0.26
Nodes (8): _citation(), detect_prompt_injection(), GuardrailResult, _inspect_text(), _normalize_text(), _sensitive_terms(), _terms(), validate_output()

### Community 125 - "backend_boot/_baseline.py"
Cohesion: 0.06
Nodes (11): backend_boot_task(), compile_sources_without_writes(), pyproject(), read(), route_calls(), route_path(), task_packet(), tree() (+3 more)

### Community 126 - "BackendBootstrapBehaviorTests"
Cohesion: 0.14
Nodes (5): assignment(), calls(), function(), literal(), BackendBootstrapBehaviorTests

### Community 127 - "_make_retriever"
Cohesion: 0.15
Nodes (17): reciprocal_rank_fusion(), _make_retriever(), test_hybrid_retrieval_composes_bm25_rrf_and_local_reranker(), test_rrf_uses_each_branch_rank_and_deduplicates_within_a_branch(), test_bm25_length_normalization_prefers_shorter_equal_match(), test_bm25_repeated_query_term_has_frequency_weight(), test_bm25_tokenization_casefolds_and_splits_punctuation(), test_hybrid_composition_preserves_rrf_and_rerank_scores() (+9 more)

### Community 130 - "orchestration/context.py"
Cohesion: 0.20
Nodes (6): ContextLimitError, estimate_tokens(), PromptMessage, _render_evidence(), _safe_text(), _safe_value()

### Community 131 - "Claim"
Cohesion: 0.07
Nodes (69): AuthorizationDecision, CitationRecord, Claim, ClaimVerification, EvidenceRecord, EvidenceVerifier, _is_negative(), _numeric_conflict() (+61 more)

### Community 132 - "orchestration_langgraph/test_behavior_component.py"
Cohesion: 0.25
Nodes (15): Answerer, Clock, evidence(), request(), run(), test_compiles_a_state_graph_with_expected_nodes(), test_complex_loop_caps_subqueries_and_tool_calls_at_four(), test_complex_query_splits_into_distinct_subqueries() (+7 more)

### Community 133 - "test_knowledge_security.py"
Cohesion: 0.37
Nodes (13): inherit_acl(), make_child(), make_parent(), test_conflicting_child_acl_is_denied(), test_document_mismatch_is_denied(), test_matching_child_acl_is_preserved(), test_missing_child_acl_is_inherited(), test_qdrant_projection_does_not_claim_authority() (+5 more)

### Community 134 - "cache_memory/test_e2e_operational.py"
Cohesion: 0.12
Nodes (19): ConversationMemory, ConversationMemoryRepository, ConversationMessage, test_contract_fake_repository_implements_provider_neutral_memory_boundary(), Clock, FakeInvalidationBus, FakeMemoryRepository, make_key() (+11 more)

### Community 135 - "to_qdrant_payload"
Cohesion: 0.39
Nodes (10): to_qdrant_payload(), make_child(), make_parent(), test_acl_inheritance_populates_child_reference(), test_parent_child_contract_keeps_same_scope(), test_qdrant_projection_contains_index_state(), test_qdrant_projection_contains_scope_keys(), test_qdrant_projection_does_not_store_chunk_text() (+2 more)

### Community 136 - "env.py"
Cohesion: 0.19
Nodes (4): _database_url(), run_migrations_offline(), run_migrations_online(), DatabaseMigrationSmokeTests

### Community 137 - "test_cache_memory.py"
Cohesion: 0.33
Nodes (7): Clock, scope(), test_cache_expires_and_rejects_unbounded_ttl_or_value(), test_cache_key_contains_security_scope_but_not_raw_query(), test_conversation_delete_removes_body_and_blocks_recreation_in_old_scope(), test_conversation_memory_expires_anonymous_sessions_and_revocation_is_fail_closed(), test_conversation_memory_is_scoped_bounded_and_repr_redacts_body()

### Community 138 - "authorization/test_behavior_component.py"
Cohesion: 0.32
Nodes (5): ConversationResource, AuthorizationBehaviorTests, document(), evaluator(), principal()

### Community 139 - "test_answer_citation_schema.py"
Cohesion: 0.29
Nodes (6): _CapturingModel, _Model, test_direct_answer_context_includes_authorized_parent_runtime(), authorize(), test_real_hybrid_path_propagates_pdf_schema_end_to_end(), authorize()

### Community 140 - "ChatService"
Cohesion: 0.30
Nodes (4): ChatActor, ChatService, _error(), _fingerprint()

### Community 141 - "GeneratedAnswer"
Cohesion: 0.27
Nodes (11): GeneratedAnswer, _authorization(), authorize(), FakeModelGateway, _pipeline(), test_direct_answer_returns_insufficient_without_calling_model_when_no_match(), test_direct_answer_returns_partial_for_mixed_claims(), test_direct_answer_returns_supported_answer_and_authorized_citation() (+3 more)

### Community 142 - "cache_memory/test_behavior_component.py"
Cohesion: 0.17
Nodes (25): InMemoryScopedCache, response_key(), test_cache_delete_is_explicit(), test_cache_invalidation_hooks_remove_only_matching_scope(), test_cache_requires_exact_current_scope_and_isolates_tenant_and_principal(), test_document_change_invalidates_broad_corpus_cache_but_not_other_version(), test_policy_invalidation_is_fail_closed_for_old_epoch_but_allows_new_epoch(), Clock (+17 more)

### Community 143 - "test_authorization.py"
Cohesion: 0.40
Nodes (15): document(), evaluator(), principal(), test_acl_can_assign_employee_and_explicit_deny_wins_for_chairman(), test_anonymous_is_public_only(), test_chairman_is_read_only(), test_conversation_body_is_owner_only(), test_conversation_requires_conversation_resource() (+7 more)

### Community 144 - "ingestion/test_behavior_component.py"
Cohesion: 0.14
Nodes (13): make_chunks(), test_child_acl_broadening_is_denied(), test_approval_expiry_blocks_processing(), test_empty_processing_input_is_rejected(), test_malware_scan_is_terminal(), test_new_active_version_supersedes_previous_version(), test_publish_activates_authoritative_version_and_chunks(), test_review_one_and_processing_require_parent_acl() (+5 more)

### Community 145 - "read"
Cohesion: 0.07
Nodes (6): read(), task(), tasks(), IdentityBehaviorTests, IdentityOperationalTests, IdentitySecurityTests

### Community 146 - "build_secure_context"
Cohesion: 0.16
Nodes (5): build_secure_context(), RetrievedEvidence, PromptOperationalTests, PromptSecurityAdversarialTests, test_secure_context_escapes_parent_prompt_injection_as_untrusted_content()

### Community 147 - "InMemoryAuditSink"
Cohesion: 0.29
Nodes (8): InMemoryAuditSink, test_audit_sink_is_append_only_and_structured(), test_unavailable_sink_does_not_accept_an_event(), _add_identity(), _request(), test_sign_in_denial_emits_no_credentials_or_body(), test_sign_in_emits_correlated_success_event(), test_sign_in_fails_closed_when_audit_sink_is_unavailable()

### Community 148 - "ingestion/test_security_adversarial.py"
Cohesion: 0.16
Nodes (10): RuntimeFailureOnRemove, service_with_index(), test_cleanup_backend_error_is_wrapped_without_secret_leakage(), test_cross_tenant_document_lookup_is_denied(), test_cross_tenant_job_lookup_is_denied(), test_cross_tenant_version_lookup_is_denied(), test_derived_staging_state_cannot_authorize_retrieval(), test_legal_hold_blocks_permanent_delete() (+2 more)

### Community 151 - "rag/__init__.py"
Cohesion: 0.13
Nodes (10): _answer_citation(), AnswerCitation, AnswerModelGateway, AnswerResult, AnswerStatus, _authorization_matches(), _expired(), _utc_z() (+2 more)

### Community 152 - "KnowledgeOperationalTests"
Cohesion: 0.20
Nodes (3): read(), task(), KnowledgeOperationalTests

### Community 153 - "UUID"
Cohesion: 0.15
Nodes (10): ApprovalRecord, DocumentRecord, IdempotencyConflict, IngestionJob, InvalidInput, InvalidTransition, NotFound, _status() (+2 more)

### Community 154 - "SecureContextBuilder"
Cohesion: 0.20
Nodes (3): SecureContextBuilder, SecureContextBuilderTests, test_verifier_requires_a_server_supplied_authorization_callback()

### Community 156 - "ScopedCacheKey"
Cohesion: 0.07
Nodes (9): _CacheEntry, _component(), _digest(), _identifier(), InvalidationReason, ScopedCacheAdapter, ScopedCacheKey, _serialized_size() (+1 more)

### Community 158 - "feedback/service.py"
Cohesion: 0.19
Nodes (4): FeedbackRecord, FeedbackRepository, FeedbackService, InMemoryFeedbackRepository

### Community 159 - "DataClassification"
Cohesion: 0.13
Nodes (36): ModelEgressDenied, DataClassification, EgressMode, route(), graph_labels(), policy(), provider(), route() (+28 more)

### Community 160 - "InMemoryDerivedIndex"
Cohesion: 0.33
Nodes (4): _chunk_state(), DerivedIndexFailure, DerivedIndexRecord, InMemoryDerivedIndex

### Community 161 - "cache_memory/test_security_adversarial.py"
Cohesion: 0.40
Nodes (10): make_key(), make_scope(), test_anonymous_revocation_isolated_to_one_session_and_fails_closed(), test_broad_scope_cannot_replay_after_a_narrow_document_change(), test_cache_key_excludes_queries_model_inputs_and_conversation_identifiers(), test_cross_principal_cache_read_is_a_fail_closed_miss(), test_cross_scope_conversation_read_cannot_be_recovered_by_matching_id(), test_cross_tenant_cache_read_is_a_fail_closed_miss() (+2 more)

### Community 174 - "eval_001_runner.py"
Cohesion: 0.14
Nodes (12): _aggregate(), _AnswerModel, _Case, _DenseAsHybrid, evaluate(), _mean(), _percentile(), _principal() (+4 more)

## Knowledge Gaps
- **1 isolated node(s):** `enterprise-agentic-rag-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 878 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **51 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AuthenticatedPrincipal` connect `AuthenticatedPrincipal` to `authorization/test_behavior_component.py`, `ChatService`, `identity.py`, `test_authorization.py`, `test_hybrid_retrieval.py`, `InMemoryPolicyStore`, `rag/__init__.py`, `rag_v4_citation/test_contract_integration.py`, `authorization/test_contract_integration.py`, `PolicyEnforcementPoint`, `chat_api/test_contract_integration.py`, `chat_api/test_behavior_component.py`, `chat_api/test_security_adversarial.py`, `ToolResult`, `CacheScope`, `eval_001_runner.py`, `rag_v4_citation/test_e2e_operational.py`, `identity/models.py`, `admin.py`, `api/chat.py`, `orchestration_langgraph/test_security_adversarial.py`, `test_dense_retrieval.py`, `test_identity.py`, `test_tool_gateway.py`, `SourceSpan`, `IngestionService`, `InMemoryIdentityStore`, `field_validator`, `expand_parent_context`, `._authorized`, `orchestration_langgraph/test_contract_integration.py`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Are the 45 inferred relationships involving `IngestionService` (e.g. with `reset_state()` and `test_active_retrieval_to_evidence_verification_succeeds()`) actually correct?**
  _`IngestionService` has 45 INFERRED edges - model-reasoned connections that need verification._
- **What connects `enterprise-agentic-rag-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `audit.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0931174089068826 - nodes in this community are weakly interconnected._
- **Why does `IngestionService` connect `IngestionService` to `._now`, `DerivedIndex`, `lifecycle.py`, `rag_hybrid/test_security_adversarial.py`, `eval_001_runner.py`, `quarantine`, `new_service`, `test_hybrid_retrieval.py`, `pytest`, `ingestion/test_security_adversarial.py`, `answer_baseline/test_security_adversarial.py`, `UUID`, `._authorized`, `_make_case`, `tests/test_chat_api.py`, `test_dense_retrieval.py`, `_make_retriever`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Are the 47 inferred relationships involving `DataClassification` (e.g. with `ModelEgressDenied` and `ModelGateway`) actually correct?**
  _`DataClassification` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Should `compose` be split into smaller, more focused modules?**
  _Cohesion score 0.06778476589797344 - nodes in this community are weakly interconnected._