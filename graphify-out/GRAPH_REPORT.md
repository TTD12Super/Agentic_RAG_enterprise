# Graph Report - enterprise-agentic-rag-harness  (2026-11-11)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 3159 nodes · 9159 edges · 147 communities (97 shown, 50 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 966 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4f7b79a3`
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
- _publish
- postgres
- postgres
- pytest
- package.json
- eval_001_runner.py
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
- _AnswerModel
- GraphifyOperationalTests
- auth
- _evaluation_harness.py
- steps
- BehaviorComponentTests
- ContractIntegrationTests
- SecurityAdversarialTests
- rules
- DataClassification
- expand_parent_context
- gateway.py
- eslint.config.js
- route
- rag_v4_citation/test_e2e_operational.py
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
- AuthenticationService
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
- AuthenticatedPrincipal
- FrontendE2EOperationalTests
- service.py
- ToolResult
- UUID
- answer_baseline/test_contract_integration.py
- RerankerRequest
- answer_baseline/test_e2e_operational.py
- knowledge/models.py
- rag_v4_citation/test_contract_integration.py
- guardrails/__init__.py
- Claim
- normalize_user_input
- AuthenticatedPrincipal
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
- PromptBehaviorComponentTests
- DenseRetrievalContractIntegrationTests
- inspect_untrusted_content
- KnowledgeOperationalTests
- rag_v4_citation/test_security_adversarial.py
- _aggregate
- env.py
- BackendBootstrapSecurityTests
- evidence/test_contract_integration.py
- observability/context.py
- pathlib
- read
- IdentitySecurityTests

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
  tests/qa/answer_baseline/test_security_adversarial.py → backend/app/evidence/verifier.py
- `KnowledgeBehaviorTests` --uses--> `SourceSpan`  [INFERRED]
  tests/qa/knowledge/test_behavior_component.py → backend/app/knowledge/models.py
- `_make_case()` --calls--> `AccessGrant`  [INFERRED]
  tests/evaluation/eval_001_runner.py → backend/app/authorization/policy.py
- `DenseRetrievalBehaviorTests` --uses--> `DenseRetriever`  [INFERRED]
  tests/qa/rag/test_behavior_component.py → backend/app/rag/dense.py

## Import Cycles
- 2-file cycle: `backend/app/api/admin.py -> backend/app/api/identity.py -> backend/app/api/admin.py`

## Communities (147 total, 50 thin omitted)

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
Cohesion: 0.19
Nodes (10): _bearer_token(), current_identity(), _record(), _record_identity_error(), _request_context(), sign_in(), sign_out(), SignInRequest (+2 more)

### Community 14 - "AuthenticatedPrincipal"
Cohesion: 0.08
Nodes (14): Action, AuthorizationDenied, deny(), Classification, ConversationResource, Decision, DocumentResource, Effect (+6 more)

### Community 15 - "_publish"
Cohesion: 0.19
Nodes (7): ApprovalBlocked, ApprovalRecord, IdempotencyConflict, InvalidInput, _status(), VersionRecord, _publish()

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

### Community 20 - "eval_001_runner.py"
Cohesion: 0.07
Nodes (35): ModelProviderError, EmbeddingAdapter, EmbeddingRequest, EmbeddingResult, RankedDocument, RerankerAdapter, RerankerResult, ModelPolicy (+27 more)

### Community 21 - "InMemoryPolicyStore"
Cohesion: 0.41
Nodes (4): AuthorizationSecurityAdversarialTests, document(), evaluator(), principal()

### Community 22 - "ChunkMetadata"
Cohesion: 0.17
Nodes (10): ChunkMetadata, DocumentMetadata, test_active_chunk_requires_acl_metadata(), test_chunk_accepts_source_provenance(), test_chunk_rejects_reversed_pages(), test_chunk_rejects_self_parent(), test_document_metadata_is_tenant_scoped(), test_root_chunk_can_have_no_parent() (+2 more)

### Community 23 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+10 more)

### Community 24 - "DocumentVersionMetadata"
Cohesion: 0.10
Nodes (9): DocumentVersionMetadata, test_document_version_identity_is_stable(), test_document_version_requires_private_source(), test_hashes_are_normalized(), test_version_contract_has_immutable_version_number(), test_version_contract_supports_publication_states(), make_document(), make_version() (+1 more)

### Community 25 - "inherit_acl"
Cohesion: 0.21
Nodes (4): make_child(), make_parent(), KnowledgeContractIntegrationTests, KnowledgeSecurityAdversarialTests

### Community 26 - "json"
Cohesion: 0.18
Nodes (3): test_dashboard_has_api_and_security_panels(), test_dashboard_is_valid_json(), test_rag002_task_registry_keeps_retrieval_validation_and_scope()

### Community 27 - "authorization/test_contract_integration.py"
Cohesion: 0.26
Nodes (4): AuthorizationContractIntegrationTests, document(), evaluator(), principal()

### Community 28 - "PolicyEnforcementPoint"
Cohesion: 0.33
Nodes (4): AuthorizationOperationalTests, document(), evaluator(), principal()

### Community 29 - "BackendBootstrapBehaviorTests"
Cohesion: 0.16
Nodes (5): assignment(), calls(), function(), literal(), BackendBootstrapBehaviorTests

### Community 30 - "test_models.py"
Cohesion: 0.15
Nodes (35): ModelGateway, FakeEmbedding, policy(), provider(), route(), test_approved_local_fallback_can_handle_internal_data(), test_approved_local_provider_can_process_internal_data(), test_denial_error_does_not_echo_model_input() (+27 more)

### Community 31 - "test_authorization.py"
Cohesion: 0.16
Nodes (20): AnonymousPrincipal, AuthorizationBehaviorTests, document(), evaluator(), principal(), document(), evaluator(), principal() (+12 more)

### Community 33 - "GraphifyOperationalTests"
Cohesion: 0.15
Nodes (5): graph(), graphify_bin(), run_graphify(), GraphifyOperationalTests, run_graph_query()

### Community 34 - "auth"
Cohesion: 0.06
Nodes (102): ScanReport, ScanVerdict, add_user(), auth(), key(), prepare_review_two(), publish(), request() (+94 more)

### Community 35 - "_evaluation_harness.py"
Cohesion: 0.14
Nodes (21): _run_version(), answer_correctness(), citation_accuracy(), evaluate_case(), load_records(), mean_reciprocal_rank(), ndcg_at_k(), no_answer_accuracy() (+13 more)

### Community 36 - "steps"
Cohesion: 0.15
Nodes (12): jobs, validate, name, on, pull_request, workflow_dispatch, run, uses (+4 more)

### Community 40 - "rules"
Cohesion: 0.17
Nodes (11): runbook, summary, groups, name, rules, severity, alert, annotations (+3 more)

### Community 41 - "DataClassification"
Cohesion: 0.08
Nodes (40): ModelEgressDenied, ModelUnavailable, DataClassification, EgressMode, route(), test_model_egress_denial_returns_error_with_no_answer_or_citation(), graph_labels(), policy() (+32 more)

### Community 42 - "expand_parent_context"
Cohesion: 0.18
Nodes (26): expand_parent_context(), child(), parent(), test_callback_failure_fails_closed_for_parent_only(), test_cross_tenant_parent_is_never_authorized_or_returned(), test_denied_parent_does_not_change_child_result(), test_duplicate_children_and_parents_are_deduplicated_with_all_provenance(), test_expands_authorized_parent_and_preserves_child_citation() (+18 more)

### Community 43 - "gateway.py"
Cohesion: 0.09
Nodes (14): AuthorizedScope, GetDocumentMetadataArguments, PrincipalResolver, ReadAuthorizedChunkArguments, _safe_tool_result(), ScopeResolver, SearchDocumentsArguments, ToolBackend (+6 more)

### Community 44 - "eslint.config.js"
Cohesion: 0.18
Nodes (10): @eslint/js@9.17.0, eslint-plugin-react-hooks@5.1.0, eslint-plugin-react-refresh@0.4.16, globals@15.14.0, typescript-eslint@8.18.0, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh (+2 more)

### Community 45 - "route"
Cohesion: 0.18
Nodes (10): global, resolve_timeout, receivers, name, route, group_by, group_interval, group_wait (+2 more)

### Community 46 - "rag_v4_citation/test_e2e_operational.py"
Cohesion: 0.21
Nodes (15): _allow(), _answer(), _locator(), _Model, _principal(), _StaticRetriever, test_answer_workflow_consumes_parent_context_without_ranking_parent(), test_audience_and_expiry_survive_citation_delivery() (+7 more)

### Community 47 - "test_knowledge_database.py"
Cohesion: 0.26
Nodes (11): migration_text(), test_existing_db_contract_has_active_index_guard(), test_existing_db_contract_has_chunks_table(), test_existing_db_contract_has_composite_parent_fk(), test_existing_db_contract_has_document_versions_table(), test_existing_db_contract_has_documents_table(), test_existing_db_contract_has_immutable_version_uniqueness(), test_existing_db_contract_has_private_source_constraint() (+3 more)

### Community 48 - "test_knowledge_security.py"
Cohesion: 0.37
Nodes (13): inherit_acl(), make_child(), make_parent(), test_conflicting_child_acl_is_denied(), test_document_mismatch_is_denied(), test_matching_child_acl_is_preserved(), test_missing_child_acl_is_inherited(), test_qdrant_projection_does_not_claim_authority() (+5 more)

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
Nodes (14): EvidenceRecord, SourceSpan, citation(), test_authorization_callback_error_fails_closed(), test_current_active_version_is_required_by_authorization_attestation(), test_negation_mismatch_is_conflicting_not_supported(), test_numeric_mismatch_is_conflicting_not_supported(), test_repeated_verification_is_deterministic() (+6 more)

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

### Community 61 - "AuthenticationService"
Cohesion: 0.09
Nodes (7): DepartmentRecord, normalize_roles(), Role, hash_secret(), InMemoryIdentityStore, verify_secret(), test_noncanonical_role_cannot_create_identity()

### Community 62 - "orchestration/context.py"
Cohesion: 0.20
Nodes (6): ContextLimitError, estimate_tokens(), PromptMessage, _render_evidence(), _safe_text(), _safe_value()

### Community 64 - "orchestrator.py"
Cohesion: 0.09
Nodes (11): AssembledContext, AnswerSynthesizer, BoundedOrchestrator, _GraphState, OrchestrationOutcome, OrchestrationRequest, OrchestrationStatus, QueryRoute (+3 more)

### Community 86 - "answer_baseline/test_behavior_component.py"
Cohesion: 0.12
Nodes (22): AnswerResult, DirectAnswerPipeline, _authorization(), FakeModelGateway, _pipeline(), RaisingRetriever, RaisingVerifier, StaticRetriever (+14 more)

### Community 87 - "orchestration_langgraph/test_security_adversarial.py"
Cohesion: 0.13
Nodes (20): Answerer, Backend, call(), Clock, gateway(), Policy, principal(), request() (+12 more)

### Community 91 - "_make_case"
Cohesion: 0.14
Nodes (20): _Case, evaluate(), evaluation_snapshot(), _make_case(), authorize(), _principal(), render_report(), _uuid() (+12 more)

### Community 94 - "rag_hybrid/test_e2e_operational.py"
Cohesion: 0.06
Nodes (67): AuthorizationEvaluator, InMemoryPolicyStore, PolicyEnforcementPoint, DenseRetriever, DeterministicEmbeddingAdapter, InMemoryDenseVectorIndex, DeterministicRerankerAdapter, HybridRetrievalConfig (+59 more)

### Community 95 - "SecureContextBuilder"
Cohesion: 0.20
Nodes (3): SecureContextBuilder, SecureContextBuilderTests, test_verifier_requires_a_server_supplied_authorization_callback()

### Community 96 - "lifecycle.py"
Cohesion: 0.08
Nodes (19): _acl_digest(), _chunk_digest(), _chunk_state(), DerivedIndex, DerivedIndexFailure, DerivedIndexRecord, IndexManifest, IndexPublication (+11 more)

### Community 97 - "test_identity.py"
Cohesion: 0.24
Nodes (10): IdentityError, make_service(), test_expired_session_is_rejected(), test_invalid_password_is_safe_auth_error(), test_mfa_is_required_for_privileged_role(), test_principal_rejects_extra_client_claims(), test_revoked_session_is_rejected(), test_sign_in_normalizes_email_and_returns_server_principal() (+2 more)

### Community 98 - "test_tool_gateway.py"
Cohesion: 0.15
Nodes (21): _Backend, _call(), _Clock, _gateway(), _Policy, _principal(), _Resolvers, test_backend_exception_is_unavailable_without_raw_error() (+13 more)

### Community 99 - "AnswerDraft"
Cohesion: 0.26
Nodes (20): AnswerDraft, _Answerer, _Clock, _evidence(), _orchestrator(), _request(), test_answerer_error_is_returned_as_safe_error(), test_complex_route_splits_subqueries_and_preserves_bound() (+12 more)

### Community 100 - "knowledge/models.py"
Cohesion: 0.14
Nodes (18): PDFLocator, SourceSpan, Citation, _FusedCandidate, _AnswerModel, _pipeline(), allow(), _principal() (+10 more)

### Community 102 - "evidence/__init__.py"
Cohesion: 0.19
Nodes (8): ClaimVerification, _is_negative(), _numeric_conflict(), _numeric_terms(), _relation(), _terms(), VerificationOutcome, VerificationResult

### Community 103 - "IngestionService"
Cohesion: 0.14
Nodes (21): AccessGrant, IngestionService, _active_document(), _principal(), _retriever(), test_dense_retrieval_returns_authorized_current_chunk_only(), test_explicit_deny_candidates_are_not_exposed(), test_forbidden_source_fetch_is_redacted_without_content_or_citation() (+13 more)

### Community 104 - "AuthenticatedPrincipal"
Cohesion: 0.13
Nodes (7): AuthenticatedPrincipal, HybridEvidence, HybridRetrievalResult, _DenseAsHybrid, _RrfOnly, test_retrieval_result_keeps_backward_compatible_empty_parent_context(), _principal()

### Community 106 - "service.py"
Cohesion: 0.09
Nodes (9): rate_limited(), IdentityRecord, SessionRecord, utc_z(), AuthenticationService, IdentityErrorPassthrough, now_utc(), IdentityStore (+1 more)

### Community 107 - "ToolResult"
Cohesion: 0.22
Nodes (18): ToolResult, test_tool_result_does_not_accept_unsafe_error_code(), Answerer, Clock, evidence(), request(), run(), test_answer_provider_failure_returns_error_without_exception_to_user() (+10 more)

### Community 113 - "UUID"
Cohesion: 0.19
Nodes (6): DocumentRecord, IngestionJob, InvalidTransition, MaintenanceBlocked, MaintenanceWindow, NotFound

### Community 114 - "answer_baseline/test_contract_integration.py"
Cohesion: 0.19
Nodes (15): _allow(), RecordingModel, RecordingRetriever, _setup(), test_citation_authorization_rejects_document_mismatch(), test_citation_authorization_rejects_non_active_status(), test_citation_authorization_rejects_non_current_version(), test_citation_authorization_rejects_revoked_source() (+7 more)

### Community 115 - "RerankerRequest"
Cohesion: 0.33
Nodes (5): RerankerRequest, test_reranker_request_rejects_blank_document_fields(), test_reranker_request_requires_documents(), test_reranker_request_requires_query(), test_deterministic_reranker_orders_equal_scores_by_id()

### Community 116 - "answer_baseline/test_e2e_operational.py"
Cohesion: 0.16
Nodes (17): AnswerStatus, _allow(), FailingEmbedder, FailingReranker, FakeAnswerGateway, _setup(), test_operational_abstention_is_insufficient_evidence(), test_operational_conflicting_evidence_is_not_harmonized() (+9 more)

### Community 117 - "knowledge/models.py"
Cohesion: 0.12
Nodes (11): DOCXLocator, _ImmutableModel, XLSXLocator, _answer_citation(), AnswerCitation, _expired(), _utc_z(), _valid_locator() (+3 more)

### Community 118 - "rag_v4_citation/test_contract_integration.py"
Cohesion: 0.10
Nodes (25): _active(), ChildEvidence, _coerce_child(), _coerce_parent(), _construct(), _identity(), _index_parents(), ParentEvidence (+17 more)

### Community 119 - "guardrails/__init__.py"
Cohesion: 0.15
Nodes (6): _luhn_valid(), redact_sensitive_data(), redact_card(), RedactionResult, ToolDecision, validate_tool_request()

### Community 120 - "Claim"
Cohesion: 0.12
Nodes (23): Claim, GeneratedAnswer, _authorization(), FakeModelGateway, _pipeline(), test_direct_answer_returns_insufficient_without_calling_model_when_no_match(), test_direct_answer_returns_partial_for_mixed_claims(), test_direct_answer_returns_supported_answer_and_authorized_citation() (+15 more)

### Community 121 - "normalize_user_input"
Cohesion: 0.17
Nodes (3): normalize_user_input(), GuardrailBehaviorTests, GuardrailSecurityAdversarialTests

### Community 122 - "AuthenticatedPrincipal"
Cohesion: 0.09
Nodes (12): AnswerModelGateway, _citation(), _cosine(), DenseEvidence, DenseRetrievalResult, SourceFetchResult, _uuid(), _vectorize() (+4 more)

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
Cohesion: 0.43
Nodes (5): _CapturingModel, _Model, test_direct_answer_context_includes_authorized_parent_runtime(), test_real_hybrid_path_propagates_pdf_schema_end_to_end(), authorize()

### Community 130 - "Claim"
Cohesion: 0.12
Nodes (28): AuthorizationDecision, CitationRecord, _authorization_matches(), allow_active(), citation(), test_authorizer_must_attest_active_current_and_not_revoked(), revoked(), test_citation_and_source_span_are_immutable() (+20 more)

### Community 131 - "EvidenceVerifier"
Cohesion: 0.22
Nodes (18): EvidenceVerifier, VerificationRequest, allow_active(), citation(), test_authorization_callback_exception_fails_closed(), test_cross_tenant_evidence_is_denied_before_authorizer_invocation(), unexpected(), test_denied_result_does_not_leak_source_text() (+10 more)

### Community 132 - "orchestration_langgraph/test_behavior_component.py"
Cohesion: 0.27
Nodes (15): Answerer, Clock, evidence(), request(), run(), test_compiles_a_state_graph_with_expected_nodes(), test_complex_loop_caps_subqueries_and_tool_calls_at_four(), test_complex_query_splits_into_distinct_subqueries() (+7 more)

### Community 136 - "KnowledgeOperationalTests"
Cohesion: 0.20
Nodes (3): read(), task(), KnowledgeOperationalTests

### Community 137 - "rag_v4_citation/test_security_adversarial.py"
Cohesion: 0.38
Nodes (10): _child(), _parent(), test_cross_document_parent_is_not_expanded(), test_cross_tenant_parent_is_not_even_sent_to_authorizer(), test_cross_version_parent_is_not_expanded(), test_explicit_parent_deny_does_not_remove_authorized_child(), test_inactive_parent_status_is_not_expanded(), test_parent_policy_callback_outage_does_not_leak_text() (+2 more)

### Community 138 - "_aggregate"
Cohesion: 0.67
Nodes (3): _aggregate(), _mean(), _percentile()

### Community 139 - "env.py"
Cohesion: 0.19
Nodes (4): _database_url(), run_migrations_offline(), run_migrations_online(), DatabaseMigrationSmokeTests

### Community 142 - "evidence/test_contract_integration.py"
Cohesion: 0.23
Nodes (6): allow_active(), citation(), test_chat_001_owns_preview_download_reauthorization_recheck(), test_duplicate_evidence_ids_are_a_malformed_fail_closed_result(), authorize(), test_supported_result_round_trips_tenant_document_version_and_span()

### Community 143 - "observability/context.py"
Cohesion: 0.18
Nodes (5): identity_error_handler(), _header(), _new_traceparent(), _valid_traceparent(), test_correlation_context_preserves_valid_headers_and_creates_child()

### Community 145 - "read"
Cohesion: 0.11
Nodes (5): read(), task(), tasks(), IdentityBehaviorTests, IdentityOperationalTests

## Knowledge Gaps
- **1 isolated node(s):** `enterprise-agentic-rag-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 802 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **50 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AuthenticatedPrincipal` connect `AuthenticatedPrincipal` to `rag_v4_citation/test_security_adversarial.py`, `identity.py`, `AuthenticatedPrincipal`, `eval_001_runner.py`, `InMemoryPolicyStore`, `authorization/test_contract_integration.py`, `PolicyEnforcementPoint`, `test_authorization.py`, `gateway.py`, `rag_v4_citation/test_e2e_operational.py`, `admin.py`, `AuthenticationService`, `answer_baseline/test_behavior_component.py`, `orchestration_langgraph/test_security_adversarial.py`, `_make_case`, `rag_hybrid/test_e2e_operational.py`, `test_identity.py`, `test_tool_gateway.py`, `knowledge/models.py`, `IngestionService`, `service.py`, `knowledge/models.py`, `rag_v4_citation/test_contract_integration.py`, `AuthenticatedPrincipal`, `orchestration_langgraph/test_contract_integration.py`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Are the 45 inferred relationships involving `IngestionService` (e.g. with `reset_state()` and `test_active_retrieval_to_evidence_verification_succeeds()`) actually correct?**
  _`IngestionService` has 45 INFERRED edges - model-reasoned connections that need verification._
- **What connects `enterprise-agentic-rag-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `audit.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10121951219512196 - nodes in this community are weakly interconnected._
- **Why does `DataClassification` connect `DataClassification` to `rag_v4_citation/test_security_adversarial.py`, `_publish`, `pytest`, `eval_001_runner.py`, `test_models.py`, `_AnswerModel`, `rag_v4_citation/test_e2e_operational.py`, `admin.py`, `answer_baseline/test_behavior_component.py`, `rag_hybrid/test_e2e_operational.py`, `lifecycle.py`, `knowledge/models.py`, `IngestionService`, `answer_baseline/test_contract_integration.py`, `answer_baseline/test_e2e_operational.py`, `knowledge/models.py`, `rag_v4_citation/test_contract_integration.py`, `Claim`, `AuthenticatedPrincipal`, `DirectAnswerPipeline`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Are the 47 inferred relationships involving `DataClassification` (e.g. with `ModelEgressDenied` and `ModelGateway`) actually correct?**
  _`DataClassification` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Should `compose` be split into smaller, more focused modules?**
  _Cohesion score 0.06778476589797344 - nodes in this community are weakly interconnected._