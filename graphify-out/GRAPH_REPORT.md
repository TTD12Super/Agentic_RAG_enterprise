# Graph Report - enterprise-agentic-rag-harness  (2026-11-11)

## Corpus Check
- 251 files · ~208,350 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 68 file(s) not represented in the graph (top: (none) 53, .toml 9, .example 2)

## Summary
- 3350 nodes · 9880 edges · 158 communities (102 shown, 56 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 1100 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `54069b6c`
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
- CacheScope
- postgres
- postgres
- pytest
- package.json
- models/policy.py
- InMemoryPolicyStore
- ChunkMetadata
- compilerOptions
- DocumentVersionMetadata
- inherit_acl
- json
- authorization/test_contract_integration.py
- PolicyEnforcementPoint
- BackendBootstrapBehaviorTests
- test_models.py
- test_authorization.py
- _evaluation_harness.py
- GraphifyOperationalTests
- auth
- _evaluation_harness.py
- steps
- BehaviorComponentTests
- ContractIntegrationTests
- SecurityAdversarialTests
- rules
- ModelGateway
- EgressMode
- gateway.py
- eslint.config.js
- route
- model/_baseline.py
- test_knowledge_database.py
- test_knowledge_security.py
- to_qdrant_payload
- App.tsx
- datasources
- monitoring/prometheus.yml
- Claim
- dependencies
- vitest
- scripts
- build_secure_context
- admin.py
- main.py
- dataclasses
- InMemoryAuditSink
- orchestration/context.py
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
- rag_hybrid/test_e2e_operational.py
- SecureContextBuilder
- lifecycle.py
- test_identity.py
- test_tool_gateway.py
- AnswerDraft
- knowledge/models.py
- evidence/__init__.py
- IngestionService
- ModelPolicy
- FrontendE2EOperationalTests
- service.py
- ToolResult
- KnowledgeOperationalTests
- answer_baseline/test_contract_integration.py
- eval_001_runner.py
- answer_baseline/test_e2e_operational.py
- AnswerModelGateway
- expand_parent_context
- guardrails/__init__.py
- Claim
- normalize_user_input
- dense.py
- orchestration_langgraph/test_contract_integration.py
- validate_output
- backend_boot/_baseline.py
- IdentityContractTests
- DirectAnswerPipeline
- run_local_guardrail_pipeline
- Citation
- Claim
- EvidenceVerifier
- orchestration_langgraph/test_behavior_component.py
- test_dense_retrieval.py
- cache_memory/test_e2e_operational.py
- InMemoryConversationMemory
- test_cache_memory.py
- authorization/test_behavior_component.py
- env.py
- DatabaseBaselineContractTests
- BackendBootstrapSecurityTests
- cache_memory/test_behavior_component.py
- observability/context.py
- DatabaseBaselineSecurityTests
- read
- PromptBehaviorComponentTests
- KnowledgeContractIntegrationTests
- InMemoryIdentityStore
- cache_memory/test_contract_integration.py
- _DenseAsHybrid
- ModelProviderError
- lifecycle.py
- cache_memory/test_security_adversarial.py
- ScopedCacheKey

## God Nodes (most connected - your core abstractions)
1. `IngestionService` - 116 edges
2. `DataClassification` - 93 edges
3. `auth()` - 87 edges
4. `request()` - 86 edges
5. `new_service()` - 85 edges
6. `_active_document()` - 78 edges
7. `AuthenticatedPrincipal` - 75 edges
8. `ChunkMetadata` - 67 edges
9. `_principal()` - 65 edges
10. `ModelGateway` - 64 edges

## Surprising Connections (you probably didn't know these)
- `authorize()` --calls--> `AuthorizationDecision`  [INFERRED]
  tests/evaluation/eval_001_runner.py → backend/app/evidence/verifier.py
- `authorize()` --calls--> `AuthorizationDecision`  [INFERRED]
  tests/integration/test_answer_citation_schema.py → backend/app/evidence/verifier.py
- `authorize()` --calls--> `AuthorizationDecision`  [INFERRED]
  tests/qa/answer_baseline/test_security_adversarial.py → backend/app/evidence/verifier.py
- `KnowledgeBehaviorTests` --uses--> `SourceSpan`  [INFERRED]
  tests/qa/knowledge/test_behavior_component.py → backend/app/knowledge/models.py
- `DenseRetrievalBehaviorTests` --uses--> `DenseRetriever`  [INFERRED]
  tests/qa/rag/test_behavior_component.py → backend/app/rag/dense.py

## Import Cycles
- 2-file cycle: `backend/app/api/admin.py -> backend/app/api/identity.py -> backend/app/api/admin.py`

## Communities (158 total, 56 thin omitted)

### Community 0 - "audit.py"
Cohesion: 0.11
Nodes (10): append_audit_event(), AuditEvent, AuditSink, AuditSinkUnavailable, redact_metadata(), _safe_code(), _safe_identifier(), _utc_z() (+2 more)

### Community 1 - "compose"
Cohesion: 0.07
Nodes (11): compose(), compose_config_result(), database(), handoff(), read(), tasks(), testing(), DisposablePostgresBehaviorTests (+3 more)

### Community 2 - "read"
Cohesion: 0.10
Nodes (8): compose_config_result(), migration_files(), migration_text(), read(), task(), tasks(), DatabaseBaselineBehaviorTests, DatabaseBaselineOperationalTests

### Community 3 - "read"
Cohesion: 0.06
Nodes (6): read(), task(), InfrastructureBehaviorTests, InfrastructureContractTests, InfrastructureOperationalTests, InfrastructureSecurityTests

### Community 4 - "read"
Cohesion: 0.05
Nodes (6): read(), task(), AuditBehaviorTests, AuditContractTests, AuditOperationalTests, AuditSecurityTests

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
Cohesion: 0.09
Nodes (12): Action, AnonymousPrincipal, AuthorizationDenied, deny(), Classification, Decision, Effect, _normalize_action() (+4 more)

### Community 15 - "CacheScope"
Cohesion: 0.08
Nodes (9): _CacheEntry, CacheScope, _component(), _digest(), _identifier(), InvalidationReason, _serialized_size(), StaleScopeError (+1 more)

### Community 16 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, networks (+12 more)

### Community 17 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, networks (+12 more)

### Community 18 - "pytest"
Cohesion: 0.05
Nodes (105): UploadManifest, active(), Clock, make_chunks(), make_manifest(), new_service(), quarantine(), staged() (+97 more)

### Community 19 - "package.json"
Cohesion: 0.13
Nodes (19): devDependencies, eslint@9.17.0, jsdom@25.0.1, @types/node@22.10.5, @types/react@18.3.18, @types/react-dom@18.3.5, typescript@5.7.2, engines (+11 more)

### Community 20 - "models/policy.py"
Cohesion: 0.13
Nodes (13): EmbeddingAdapter, EmbeddingRequest, EmbeddingResult, RerankerAdapter, RerankerRequest, RerankerResult, ModelRoute, test_embedding_request_rejects_blank_text() (+5 more)

### Community 21 - "InMemoryPolicyStore"
Cohesion: 0.43
Nodes (4): AuthorizationSecurityAdversarialTests, document(), evaluator(), principal()

### Community 22 - "ChunkMetadata"
Cohesion: 0.17
Nodes (10): ChunkMetadata, DocumentMetadata, test_active_chunk_requires_acl_metadata(), test_chunk_accepts_source_provenance(), test_chunk_rejects_reversed_pages(), test_chunk_rejects_self_parent(), test_document_metadata_is_tenant_scoped(), test_root_chunk_can_have_no_parent() (+2 more)

### Community 23 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+10 more)

### Community 24 - "DocumentVersionMetadata"
Cohesion: 0.13
Nodes (8): DocumentVersionMetadata, test_document_version_identity_is_stable(), test_document_version_requires_private_source(), test_hashes_are_normalized(), test_version_contract_has_immutable_version_number(), test_version_contract_supports_publication_states(), make_document(), KnowledgeBehaviorTests

### Community 25 - "inherit_acl"
Cohesion: 0.25
Nodes (4): inherit_acl(), make_child(), make_parent(), KnowledgeSecurityAdversarialTests

### Community 26 - "json"
Cohesion: 0.08
Nodes (10): dfs(), json_blocks(), test_dashboard_has_api_and_security_panels(), test_dashboard_is_valid_json(), tasks(), graph(), graphify_bin(), compose_config() (+2 more)

### Community 27 - "authorization/test_contract_integration.py"
Cohesion: 0.27
Nodes (4): AuthorizationContractIntegrationTests, document(), evaluator(), principal()

### Community 28 - "PolicyEnforcementPoint"
Cohesion: 0.33
Nodes (4): AuthorizationOperationalTests, document(), evaluator(), principal()

### Community 29 - "BackendBootstrapBehaviorTests"
Cohesion: 0.15
Nodes (5): assignment(), calls(), function(), literal(), BackendBootstrapBehaviorTests

### Community 30 - "test_models.py"
Cohesion: 0.18
Nodes (34): DataClassification, ModelTask, FakeEmbedding, policy(), provider(), route(), test_approved_local_fallback_can_handle_internal_data(), test_approved_local_provider_can_process_internal_data() (+26 more)

### Community 31 - "test_authorization.py"
Cohesion: 0.31
Nodes (16): AuthenticatedPrincipal, document(), evaluator(), principal(), test_acl_can_assign_employee_and_explicit_deny_wins_for_chairman(), test_anonymous_is_public_only(), test_chairman_is_read_only(), test_conversation_body_is_owner_only() (+8 more)

### Community 32 - "_evaluation_harness.py"
Cohesion: 0.15
Nodes (12): _AnswerModel, evaluate(), render_report(), _run_version(), answer_correctness(), citation_accuracy(), evaluate_case(), no_answer_accuracy() (+4 more)

### Community 34 - "auth"
Cohesion: 0.06
Nodes (102): ScanReport, ScanVerdict, add_user(), auth(), key(), prepare_review_two(), publish(), request() (+94 more)

### Community 35 - "_evaluation_harness.py"
Cohesion: 0.18
Nodes (11): mean_reciprocal_rank(), ndcg_at_k(), recall_at_k(), source_key(), E2EOperationalTests, _span(), _spans(), test_rag_002_regression_metrics_on_tiny_in_memory_corpus() (+3 more)

### Community 36 - "steps"
Cohesion: 0.15
Nodes (12): jobs, validate, name, on, pull_request, workflow_dispatch, run, uses (+4 more)

### Community 40 - "rules"
Cohesion: 0.17
Nodes (11): runbook, summary, groups, name, rules, severity, alert, annotations (+3 more)

### Community 41 - "ModelGateway"
Cohesion: 0.13
Nodes (18): ModelGateway, ModelUnavailable, test_gateway_caps_primary_retries(), test_gateway_reports_missing_adapter(), test_gateway_reports_unavailable_without_fallback(), policy(), ScriptedEmbedding, test_primary_retries_cannot_exceed_two() (+10 more)

### Community 42 - "EgressMode"
Cohesion: 0.20
Nodes (21): ModelEgressDenied, EgressMode, provider(), route(), test_embedding_route_task_is_checked(), test_external_internal_requires_dpa(), test_external_internal_requires_residency(), test_external_provider_requires_retention_policy() (+13 more)

### Community 43 - "gateway.py"
Cohesion: 0.10
Nodes (13): AuthorizedScope, GetDocumentMetadataArguments, PrincipalResolver, ReadAuthorizedChunkArguments, _safe_tool_result(), ScopeResolver, SearchDocumentsArguments, ToolBackend (+5 more)

### Community 44 - "eslint.config.js"
Cohesion: 0.18
Nodes (10): @eslint/js@9.17.0, eslint-plugin-react-hooks@5.1.0, eslint-plugin-react-refresh@0.4.16, globals@15.14.0, typescript-eslint@8.18.0, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh (+2 more)

### Community 45 - "route"
Cohesion: 0.18
Nodes (10): global, resolve_timeout, receivers, name, route, group_by, group_interval, group_wait (+2 more)

### Community 46 - "model/_baseline.py"
Cohesion: 0.21
Nodes (7): run_graph_query(), graph_labels(), run_graph_query(), task(), test_graph_contains_model_symbols(), test_graphify_query_finds_model_gateway(), test_task_registry_keeps_model_acceptance_and_validation()

### Community 47 - "test_knowledge_database.py"
Cohesion: 0.26
Nodes (11): migration_text(), test_existing_db_contract_has_active_index_guard(), test_existing_db_contract_has_chunks_table(), test_existing_db_contract_has_composite_parent_fk(), test_existing_db_contract_has_document_versions_table(), test_existing_db_contract_has_documents_table(), test_existing_db_contract_has_immutable_version_uniqueness(), test_existing_db_contract_has_private_source_constraint() (+3 more)

### Community 48 - "test_knowledge_security.py"
Cohesion: 0.38
Nodes (12): make_child(), make_parent(), test_conflicting_child_acl_is_denied(), test_document_mismatch_is_denied(), test_matching_child_acl_is_preserved(), test_missing_child_acl_is_inherited(), test_qdrant_projection_does_not_claim_authority(), test_qdrant_projection_keeps_tenant_boundary() (+4 more)

### Community 49 - "to_qdrant_payload"
Cohesion: 0.35
Nodes (11): to_qdrant_payload(), make_child(), make_parent(), test_acl_inheritance_populates_child_reference(), test_parent_child_contract_keeps_same_scope(), test_qdrant_projection_contains_index_state(), test_qdrant_projection_contains_scope_keys(), test_qdrant_projection_does_not_store_chunk_text() (+3 more)

### Community 50 - "App.tsx"
Cohesion: 0.27
Nodes (5): react@18.3.1, App(), supportedRoles, appConfig, react

### Community 51 - "datasources"
Cohesion: 0.22
Nodes (8): apiVersion, datasources, access, editable, isDefault, name, type, url

### Community 52 - "monitoring/prometheus.yml"
Cohesion: 0.22
Nodes (8): global, evaluation_interval, scrape_interval, rule_files, scrape_configs, job_name, static_configs, targets

### Community 53 - "Claim"
Cohesion: 0.27
Nodes (13): SourceSpan, citation(), test_authorization_callback_error_fails_closed(), test_current_active_version_is_required_by_authorization_attestation(), test_negation_mismatch_is_conflicting_not_supported(), test_numeric_mismatch_is_conflicting_not_supported(), test_repeated_verification_is_deterministic(), test_source_span_and_citation_metadata_are_immutable() (+5 more)

### Community 54 - "dependencies"
Cohesion: 0.29
Nodes (7): dependencies, react-dom@18.3.1, vite@6.3.5, @vitejs/plugin-react@4.6.0, react-dom, vite, @vitejs/plugin-react

### Community 55 - "vitest"
Cohesion: 0.25
Nodes (6): @testing-library/jest-dom@6.6.3, @testing-library/react@16.1.0, vitest@2.1.8, @testing-library/jest-dom, @testing-library/react, vitest

### Community 56 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, preview, test, test:watch, typecheck

### Community 57 - "build_secure_context"
Cohesion: 0.16
Nodes (5): build_secure_context(), RetrievedEvidence, PromptOperationalTests, PromptSecurityAdversarialTests, test_secure_context_escapes_parent_prompt_injection_as_untrusted_content()

### Community 58 - "admin.py"
Cohesion: 0.15
Nodes (47): AccessGrantRequest, AccessRequest, activate_user(), AdminApiState, approve_document_version(), _body(), _bump_policy_epoch(), create_department() (+39 more)

### Community 59 - "main.py"
Cohesion: 0.14
Nodes (3): get_settings(), Settings, healthz()

### Community 60 - "dataclasses"
Cohesion: 0.12
Nodes (5): default_prompt_registry(), _freeze(), PromptDefinition, PromptRegistry, PromptRegistryTests

### Community 61 - "InMemoryAuditSink"
Cohesion: 0.29
Nodes (8): InMemoryAuditSink, test_audit_sink_is_append_only_and_structured(), test_unavailable_sink_does_not_accept_an_event(), _add_identity(), _request(), test_sign_in_denial_emits_no_credentials_or_body(), test_sign_in_emits_correlated_success_event(), test_sign_in_fails_closed_when_audit_sink_is_unavailable()

### Community 62 - "orchestration/context.py"
Cohesion: 0.20
Nodes (6): ContextLimitError, estimate_tokens(), PromptMessage, _render_evidence(), _safe_text(), _safe_value()

### Community 64 - "orchestrator.py"
Cohesion: 0.12
Nodes (8): BoundedOrchestrator, _evidence_from_result(), _GraphState, OrchestrationOutcome, _route(), _subqueries(), _utc_now(), ToolStatus

### Community 86 - "answer_baseline/test_behavior_component.py"
Cohesion: 0.10
Nodes (27): AnswerResult, AnswerStatus, _authorization_matches(), DirectAnswerPipeline, _expired(), _authorization(), FakeModelGateway, _pipeline() (+19 more)

### Community 87 - "orchestration_langgraph/test_security_adversarial.py"
Cohesion: 0.13
Nodes (20): Answerer, Backend, call(), Clock, gateway(), Policy, principal(), request() (+12 more)

### Community 91 - "_make_case"
Cohesion: 0.13
Nodes (20): _Case, evaluation_snapshot(), _make_case(), authorize(), _principal(), _RrfOnly, _uuid(), load_records() (+12 more)

### Community 94 - "rag_hybrid/test_e2e_operational.py"
Cohesion: 0.06
Nodes (56): SourceFetchResult, _BM25Record, _citation(), DeterministicRerankerAdapter, HybridRetrievalConfig, HybridRetriever, InMemoryBM25Index, reciprocal_rank_fusion() (+48 more)

### Community 96 - "lifecycle.py"
Cohesion: 0.13
Nodes (13): ApprovalBlocked, ApprovalRecord, DocumentRecord, IdempotencyConflict, IngestionJob, InvalidInput, InvalidTransition, MaintenanceBlocked (+5 more)

### Community 97 - "test_identity.py"
Cohesion: 0.12
Nodes (15): IdentityError, rate_limited(), AuthenticationService, IdentityErrorPassthrough, now_utc(), make_service(), test_expired_session_is_rejected(), test_invalid_password_is_safe_auth_error() (+7 more)

### Community 98 - "test_tool_gateway.py"
Cohesion: 0.15
Nodes (22): _Backend, _call(), _Clock, _gateway(), _Policy, _principal(), _Resolvers, test_backend_exception_is_unavailable_without_raw_error() (+14 more)

### Community 99 - "AnswerDraft"
Cohesion: 0.15
Nodes (25): AssembledContext, AnswerDraft, AnswerSynthesizer, OrchestrationRequest, OrchestrationStatus, QueryRoute, _Answerer, _Clock (+17 more)

### Community 100 - "knowledge/models.py"
Cohesion: 0.06
Nodes (42): DOCXLocator, _ImmutableModel, PDFLocator, SourceSpan, XLSXLocator, _answer_citation(), AnswerCitation, _utc_z() (+34 more)

### Community 102 - "evidence/__init__.py"
Cohesion: 0.23
Nodes (7): _is_negative(), _numeric_conflict(), _numeric_terms(), _relation(), _terms(), VerificationOutcome, VerificationResult

### Community 103 - "IngestionService"
Cohesion: 0.12
Nodes (22): AccessGrant, IngestionService, _active_document(), _principal(), _retriever(), test_dense_retrieval_returns_authorized_current_chunk_only(), test_explicit_deny_candidates_are_not_exposed(), test_forbidden_source_fetch_is_redacted_without_content_or_citation() (+14 more)

### Community 104 - "ModelPolicy"
Cohesion: 0.23
Nodes (13): ModelPolicy, test_mapping_loads_versioned_policy_without_credentials(), test_policy_rejects_credential_fields(), mapping(), test_access_token_field_is_rejected(), test_exact_api_key_field_is_rejected(), test_fallback_route_task_mismatch_is_rejected(), test_mapping_rejects_empty_model_revision() (+5 more)

### Community 106 - "service.py"
Cohesion: 0.09
Nodes (4): IdentityRecord, SessionRecord, utc_z(), IdentityStore

### Community 107 - "ToolResult"
Cohesion: 0.25
Nodes (17): ToolResult, Answerer, Clock, evidence(), request(), run(), test_answer_provider_failure_returns_error_without_exception_to_user(), test_deadline_timeout_is_a_visible_insufficient_outcome() (+9 more)

### Community 113 - "KnowledgeOperationalTests"
Cohesion: 0.22
Nodes (3): read(), task(), KnowledgeOperationalTests

### Community 114 - "answer_baseline/test_contract_integration.py"
Cohesion: 0.19
Nodes (15): _allow(), RecordingModel, RecordingRetriever, _setup(), test_citation_authorization_rejects_document_mismatch(), test_citation_authorization_rejects_non_active_status(), test_citation_authorization_rejects_non_current_version(), test_citation_authorization_rejects_revoked_source() (+7 more)

### Community 115 - "eval_001_runner.py"
Cohesion: 0.21
Nodes (6): route(), ProviderPolicy, _aggregate(), _gateway(), _mean(), _percentile()

### Community 116 - "answer_baseline/test_e2e_operational.py"
Cohesion: 0.17
Nodes (16): _allow(), FailingEmbedder, FailingReranker, FakeAnswerGateway, _setup(), test_operational_abstention_is_insufficient_evidence(), test_operational_conflicting_evidence_is_not_harmonized(), test_operational_denied_content_never_appears_in_failure_result() (+8 more)

### Community 118 - "expand_parent_context"
Cohesion: 0.06
Nodes (64): HybridRetrievalResult, _active(), ChildEvidence, _coerce_child(), _coerce_parent(), _construct(), expand_parent_context(), _identity() (+56 more)

### Community 119 - "guardrails/__init__.py"
Cohesion: 0.15
Nodes (6): _luhn_valid(), redact_sensitive_data(), redact_card(), RedactionResult, ToolDecision, validate_tool_request()

### Community 120 - "Claim"
Cohesion: 0.12
Nodes (23): Claim, GeneratedAnswer, _AnswerModel, _authorization(), FakeModelGateway, _pipeline(), test_direct_answer_returns_insufficient_without_calling_model_when_no_match(), test_direct_answer_returns_partial_for_mixed_claims() (+15 more)

### Community 121 - "normalize_user_input"
Cohesion: 0.17
Nodes (3): normalize_user_input(), GuardrailBehaviorTests, GuardrailSecurityAdversarialTests

### Community 122 - "dense.py"
Cohesion: 0.19
Nodes (7): _citation(), _cosine(), DenseEvidence, DenseRetrievalResult, _uuid(), _valid_locator(), _VectorRecord

### Community 123 - "orchestration_langgraph/test_contract_integration.py"
Cohesion: 0.18
Nodes (16): Backend, call(), Clock, gateway(), Policy, principal(), Resolvers, test_chunk_read_contract_accepts_only_chunk_id_shape() (+8 more)

### Community 124 - "validate_output"
Cohesion: 0.26
Nodes (8): _citation(), detect_prompt_injection(), GuardrailResult, _inspect_text(), _normalize_text(), _sensitive_terms(), _terms(), validate_output()

### Community 125 - "backend_boot/_baseline.py"
Cohesion: 0.08
Nodes (10): backend_boot_task(), compile_sources_without_writes(), pyproject(), read(), route_calls(), route_path(), task_packet(), tree() (+2 more)

### Community 127 - "DirectAnswerPipeline"
Cohesion: 0.29
Nodes (6): _CapturingModel, _Model, test_direct_answer_context_includes_authorized_parent_runtime(), authorize(), test_real_hybrid_path_propagates_pdf_schema_end_to_end(), authorize()

### Community 130 - "Claim"
Cohesion: 0.12
Nodes (27): AuthorizationDecision, CitationRecord, allow_active(), citation(), test_authorizer_must_attest_active_current_and_not_revoked(), revoked(), test_citation_and_source_span_are_immutable(), test_conflicting_numeric_source_spans_are_disclosed() (+19 more)

### Community 131 - "EvidenceVerifier"
Cohesion: 0.12
Nodes (27): ClaimVerification, EvidenceRecord, EvidenceVerifier, VerificationRequest, allow_active(), citation(), test_chat_001_owns_preview_download_reauthorization_recheck(), test_duplicate_evidence_ids_are_a_malformed_fail_closed_result() (+19 more)

### Community 132 - "orchestration_langgraph/test_behavior_component.py"
Cohesion: 0.25
Nodes (15): Answerer, Clock, evidence(), request(), run(), test_compiles_a_state_graph_with_expected_nodes(), test_complex_loop_caps_subqueries_and_tool_calls_at_four(), test_complex_query_splits_into_distinct_subqueries() (+7 more)

### Community 133 - "test_dense_retrieval.py"
Cohesion: 0.19
Nodes (16): AuthorizationEvaluator, DocumentResource, InMemoryPolicyStore, PolicyEnforcementPoint, DenseRetriever, DeterministicEmbeddingAdapter, InMemoryDenseVectorIndex, _gateway() (+8 more)

### Community 134 - "cache_memory/test_e2e_operational.py"
Cohesion: 0.12
Nodes (19): ConversationMemory, ConversationMessage, test_conversation_memory_is_scoped_bounded_and_repr_redacts_body(), Clock, FakeInvalidationBus, FakeMemoryRepository, make_key(), make_scope() (+11 more)

### Community 137 - "test_cache_memory.py"
Cohesion: 0.31
Nodes (10): Clock, response_key(), scope(), test_cache_delete_is_explicit(), test_cache_expires_and_rejects_unbounded_ttl_or_value(), test_cache_key_contains_security_scope_but_not_raw_query(), test_cache_requires_exact_current_scope_and_isolates_tenant_and_principal(), test_conversation_delete_removes_body_and_blocks_recreation_in_old_scope() (+2 more)

### Community 138 - "authorization/test_behavior_component.py"
Cohesion: 0.32
Nodes (5): ConversationResource, AuthorizationBehaviorTests, document(), evaluator(), principal()

### Community 139 - "env.py"
Cohesion: 0.19
Nodes (4): _database_url(), run_migrations_offline(), run_migrations_online(), DatabaseMigrationSmokeTests

### Community 142 - "cache_memory/test_behavior_component.py"
Cohesion: 0.21
Nodes (16): InMemoryScopedCache, test_cache_invalidation_hooks_remove_only_matching_scope(), test_document_change_invalidates_broad_corpus_cache_but_not_other_version(), Clock, make_key(), make_scope(), test_broad_acl_invalidation_removes_all_versions_in_one_tenant(), test_cache_expires_at_the_exact_ttl_deadline() (+8 more)

### Community 143 - "observability/context.py"
Cohesion: 0.18
Nodes (5): identity_error_handler(), _header(), _new_traceparent(), _valid_traceparent(), test_correlation_context_preserves_valid_headers_and_creates_child()

### Community 145 - "read"
Cohesion: 0.07
Nodes (6): read(), task(), tasks(), IdentityBehaviorTests, IdentityOperationalTests, IdentitySecurityTests

### Community 148 - "InMemoryIdentityStore"
Cohesion: 0.12
Nodes (8): DepartmentRecord, normalize_roles(), Role, hash_secret(), InMemoryIdentityStore, verify_secret(), _vectorize(), test_noncanonical_role_cannot_create_identity()

### Community 149 - "cache_memory/test_contract_integration.py"
Cohesion: 0.25
Nodes (12): FakeMemoryRepository, make_key(), make_scope(), test_contract_delete_event_invalidates_matching_scope_without_cross_tenant_reach(), test_contract_document_change_invalidates_broad_scope_and_selected_version(), test_contract_fake_repository_implements_provider_neutral_memory_boundary(), test_contract_invalid_event_shapes_fail_closed_at_the_boundary(), test_contract_memory_read_requires_the_authoritative_current_scope() (+4 more)

### Community 152 - "ModelProviderError"
Cohesion: 0.15
Nodes (6): ModelProviderError, RankedDocument, FakeReranker, test_gateway_reranker_happy_path(), test_ranked_document_preserves_identifier_and_score(), ScriptedReranker

### Community 153 - "lifecycle.py"
Cohesion: 0.08
Nodes (19): _acl_digest(), _chunk_digest(), _chunk_state(), DerivedIndex, DerivedIndexFailure, DerivedIndexRecord, IndexManifest, IndexPublication (+11 more)

### Community 154 - "cache_memory/test_security_adversarial.py"
Cohesion: 0.39
Nodes (11): make_key(), make_scope(), test_anonymous_revocation_isolated_to_one_session_and_fails_closed(), test_broad_scope_cannot_replay_after_a_narrow_document_change(), test_cache_key_excludes_queries_model_inputs_and_conversation_identifiers(), test_changed_document_version_cannot_repopulate_an_old_cache_entry(), test_cross_principal_cache_read_is_a_fail_closed_miss(), test_cross_tenant_cache_read_is_a_fail_closed_miss() (+3 more)

### Community 156 - "ScopedCacheKey"
Cohesion: 0.15
Nodes (4): ScopedCacheAdapter, ScopedCacheKey, FakeProvider, test_provider_neutral_fake_preserves_exact_scope_checks()

## Knowledge Gaps
- **1 isolated node(s):** `enterprise-agentic-rag-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 831 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **56 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AuthenticatedPrincipal` connect `test_authorization.py` to `test_dense_retrieval.py`, `field_validator`, `authorization/test_behavior_component.py`, `identity.py`, `AuthenticatedPrincipal`, `InMemoryIdentityStore`, `InMemoryPolicyStore`, `authorization/test_contract_integration.py`, `PolicyEnforcementPoint`, `gateway.py`, `admin.py`, `answer_baseline/test_behavior_component.py`, `orchestration_langgraph/test_security_adversarial.py`, `_make_case`, `rag_hybrid/test_e2e_operational.py`, `test_identity.py`, `test_tool_gateway.py`, `knowledge/models.py`, `IngestionService`, `service.py`, `eval_001_runner.py`, `expand_parent_context`, `dense.py`, `orchestration_langgraph/test_contract_integration.py`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Are the 45 inferred relationships involving `IngestionService` (e.g. with `reset_state()` and `test_active_retrieval_to_evidence_verification_succeeds()`) actually correct?**
  _`IngestionService` has 45 INFERRED edges - model-reasoned connections that need verification._
- **What connects `enterprise-agentic-rag-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `audit.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11290322580645161 - nodes in this community are weakly interconnected._
- **Why does `IngestionService` connect `IngestionService` to `lifecycle.py`, `audit.py`, `test_dense_retrieval.py`, `dense.py`, `_make_case`, `pytest`, `eval_001_runner.py`, `lifecycle.py`, `admin.py`, `.retrievable_chunks`, `rag_hybrid/test_e2e_operational.py`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Are the 47 inferred relationships involving `DataClassification` (e.g. with `ModelEgressDenied` and `ModelGateway`) actually correct?**
  _`DataClassification` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Should `compose` be split into smaller, more focused modules?**
  _Cohesion score 0.06778476589797344 - nodes in this community are weakly interconnected._