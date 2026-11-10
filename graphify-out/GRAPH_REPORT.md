# Graph Report - enterprise-agentic-rag-harness  (2026-11-11)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2905 nodes · 8291 edges · 136 communities (90 shown, 46 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 940 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ff43b065`
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
- env.py
- identity.py
- AuthenticatedPrincipal
- pytest
- postgres
- postgres
- active
- package.json
- hybrid.py
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
- eval_001_runner.py
- GraphifyOperationalTests
- auth
- _evaluation_harness.py
- steps
- BehaviorComponentTests
- ContractIntegrationTests
- SecurityAdversarialTests
- rules
- model/test_e2e_operational.py
- expand_parent_context
- read
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
- model/test_security_adversarial.py
- vite-env.d.ts
- sync_graph.sh
- migrate.sh
- inspect_untrusted_content
- enterprise-agentic-rag-backend
- answer_baseline/test_behavior_component.py
- ingestion/_baseline.py
- _make_case
- PromptContractIntegrationTests
- rag_hybrid/test_e2e_operational.py
- SecureContextBuilder
- lifecycle.py
- test_identity.py
- ModelPolicy
- new_service
- knowledge/models.py
- EvidenceRecord
- IngestionService
- InMemoryIdentityStore
- FrontendE2EOperationalTests
- identity/models.py
- ingestion/test_behavior_component.py
- ingestion/test_security_adversarial.py
- answer_baseline/test_contract_integration.py
- ProviderPolicy
- answer_baseline/test_e2e_operational.py
- answer.py
- guardrails/__init__.py
- answer_baseline/test_security_adversarial.py
- normalize_user_input
- AuthenticatedPrincipal
- E2EOperationalTests
- validate_output
- backend_boot/_baseline.py
- IdentityContractTests
- DirectAnswerPipeline
- run_local_guardrail_pipeline
- Citation
- Claim
- make_manifest
- InMemoryAuditSink
- PromptBehaviorComponentTests
- _ingestion_fixtures.py

## God Nodes (most connected - your core abstractions)
1. `IngestionService` - 116 edges
2. `DataClassification` - 93 edges
3. `auth()` - 87 edges
4. `request()` - 86 edges
5. `new_service()` - 85 edges
6. `_active_document()` - 78 edges
7. `AuthenticatedPrincipal` - 68 edges
8. `ChunkMetadata` - 65 edges
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

## Communities (136 total, 46 thin omitted)

### Community 0 - "audit.py"
Cohesion: 0.12
Nodes (10): append_audit_event(), AuditEvent, AuditSink, AuditSinkUnavailable, redact_metadata(), _safe_code(), _safe_identifier(), _utc_z() (+2 more)

### Community 1 - "compose"
Cohesion: 0.07
Nodes (11): compose(), compose_config_result(), database(), handoff(), read(), tasks(), testing(), DisposablePostgresBehaviorTests (+3 more)

### Community 2 - "read"
Cohesion: 0.06
Nodes (7): migration_files(), migration_text(), read(), DatabaseBaselineBehaviorTests, DatabaseBaselineContractTests, DatabaseBaselineOperationalTests, DatabaseBaselineSecurityTests

### Community 3 - "read"
Cohesion: 0.06
Nodes (6): read(), task(), InfrastructureBehaviorTests, InfrastructureContractTests, InfrastructureOperationalTests, InfrastructureSecurityTests

### Community 4 - "read"
Cohesion: 0.05
Nodes (7): read(), task(), tasks(), AuditBehaviorTests, AuditContractTests, AuditOperationalTests, AuditSecurityTests

### Community 5 - "section"
Cohesion: 0.10
Nodes (7): json_blocks(), require_all(), section(), BehaviorComponentTests, ContractIntegrationTests, E2EOperationalTests, SecurityAdversarialTests

### Community 6 - "read"
Cohesion: 0.06
Nodes (6): read(), task(), MonitoringBehaviorTests, MonitoringContractTests, MonitoringOperationalTests, MonitoringSecurityTests

### Community 7 - "read_frontend"
Cohesion: 0.09
Nodes (6): load_frontend_json(), read(), read_frontend(), FrontendBehaviorComponentTests, FrontendContractIntegrationTests, FrontendSecurityAdversarialTests

### Community 8 - "read"
Cohesion: 0.06
Nodes (7): read(), GraphifyBehaviorTests, GraphifyContractTests, GraphifySecurityTests, read(), task(), KnowledgeOperationalTests

### Community 9 - "otel-collector-config.yaml"
Cohesion: 0.06
Nodes (32): action, key, actions, send_batch_size, timeout, exporters, prometheus, endpoint (+24 more)

### Community 10 - "prometheus"
Cohesion: 0.06
Nodes (30): command, image, ports, read_only, security_opt, volumes, depends_on, image (+22 more)

### Community 11 - "env.py"
Cohesion: 0.09
Nodes (3): _database_url(), run_migrations_offline(), run_migrations_online()

### Community 13 - "identity.py"
Cohesion: 0.27
Nodes (9): _bearer_token(), current_identity(), _record(), _record_identity_error(), _request_context(), sign_in(), sign_out(), SignInRequest (+1 more)

### Community 14 - "AuthenticatedPrincipal"
Cohesion: 0.07
Nodes (20): Action, AnonymousPrincipal, AuthorizationDenied, AuthorizationEvaluator, deny(), Classification, ConversationResource, Decision (+12 more)

### Community 15 - "pytest"
Cohesion: 0.20
Nodes (17): UploadManifest, validated(), test_approval_expiry_blocks_publication(), test_doc_is_rejected(), test_internal_upload_requires_department(), test_manifest_checksum_mismatch_blocks_staging(), test_manifest_count_mismatch_blocks_staging(), test_non_private_source_is_rejected() (+9 more)

### Community 16 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, networks (+12 more)

### Community 17 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, networks (+12 more)

### Community 18 - "active"
Cohesion: 0.16
Nodes (18): active(), staged(), test_derived_cleanup_failure_still_denies_retrieval(), test_derived_index_cannot_authorize_non_active_version(), test_legal_hold_blocks_permanent_delete(), test_rejected_version_cannot_be_retrieved(), test_revoked_version_cannot_be_retrieved_from_derived_state(), test_root_chunk_without_acl_fails_closed() (+10 more)

### Community 19 - "package.json"
Cohesion: 0.13
Nodes (19): devDependencies, eslint@9.17.0, jsdom@25.0.1, @types/node@22.10.5, @types/react@18.3.18, @types/react-dom@18.3.5, typescript@5.7.2, engines (+11 more)

### Community 20 - "hybrid.py"
Cohesion: 0.08
Nodes (21): ModelProviderError, EmbeddingAdapter, EmbeddingRequest, EmbeddingResult, RankedDocument, RerankerAdapter, RerankerRequest, RerankerResult (+13 more)

### Community 21 - "InMemoryPolicyStore"
Cohesion: 0.21
Nodes (8): AccessGrant, InMemoryPolicyStore, AuthorizationSecurityAdversarialTests, document(), evaluator(), principal(), test_bm25_filters_unauthorized_high_frequency_candidates_before_scoring(), test_source_fetch_redacts_acl_denied_content_and_citation()

### Community 22 - "ChunkMetadata"
Cohesion: 0.10
Nodes (14): ChunkMetadata, DocumentMetadata, DOCXLocator, _ImmutableModel, XLSXLocator, test_malformed_locator_model_is_rejected(), test_active_chunk_requires_acl_metadata(), test_chunk_accepts_source_provenance() (+6 more)

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
Cohesion: 0.08
Nodes (10): dfs(), test_dashboard_has_api_and_security_panels(), test_dashboard_is_valid_json(), compose_config_result(), task(), tasks(), compose_config(), tasks() (+2 more)

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
Cohesion: 0.17
Nodes (39): ModelGateway, DataClassification, ModelTask, FakeEmbedding, policy(), provider(), route(), test_approved_local_fallback_can_handle_internal_data() (+31 more)

### Community 31 - "test_authorization.py"
Cohesion: 0.40
Nodes (15): document(), evaluator(), principal(), test_acl_can_assign_employee_and_explicit_deny_wins_for_chairman(), test_anonymous_is_public_only(), test_chairman_is_read_only(), test_conversation_body_is_owner_only(), test_conversation_requires_conversation_resource() (+7 more)

### Community 32 - "eval_001_runner.py"
Cohesion: 0.19
Nodes (10): _aggregate(), _AnswerModel, _Case, evaluate(), _mean(), _percentile(), _principal(), render_report() (+2 more)

### Community 33 - "GraphifyOperationalTests"
Cohesion: 0.11
Nodes (5): DatabaseMigrationSmokeTests, graph(), graphify_bin(), run_graphify(), GraphifyOperationalTests

### Community 34 - "auth"
Cohesion: 0.06
Nodes (102): ScanReport, ScanVerdict, add_user(), auth(), key(), prepare_review_two(), publish(), request() (+94 more)

### Community 35 - "_evaluation_harness.py"
Cohesion: 0.20
Nodes (20): _vectorize(), answer_correctness(), citation_accuracy(), evaluate_case(), load_records(), mean_reciprocal_rank(), ndcg_at_k(), no_answer_accuracy() (+12 more)

### Community 36 - "steps"
Cohesion: 0.15
Nodes (12): jobs, validate, name, on, pull_request, workflow_dispatch, run, uses (+4 more)

### Community 40 - "rules"
Cohesion: 0.17
Nodes (11): runbook, summary, groups, name, rules, severity, alert, annotations (+3 more)

### Community 41 - "model/test_e2e_operational.py"
Cohesion: 0.12
Nodes (20): ModelUnavailable, run_graph_query(), graph_labels(), policy(), run_graph_query(), ScriptedEmbedding, ScriptedReranker, task() (+12 more)

### Community 42 - "expand_parent_context"
Cohesion: 0.06
Nodes (64): _active(), ChildEvidence, _coerce_child(), _coerce_parent(), _construct(), expand_parent_context(), _identity(), _index_parents() (+56 more)

### Community 43 - "read"
Cohesion: 0.07
Nodes (6): read(), task(), tasks(), IdentityBehaviorTests, IdentityOperationalTests, IdentitySecurityTests

### Community 44 - "eslint.config.js"
Cohesion: 0.18
Nodes (10): @eslint/js@9.17.0, eslint-plugin-react-hooks@5.1.0, eslint-plugin-react-refresh@0.4.16, globals@15.14.0, typescript-eslint@8.18.0, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh (+2 more)

### Community 45 - "route"
Cohesion: 0.18
Nodes (10): global, resolve_timeout, receivers, name, route, group_by, group_interval, group_wait (+2 more)

### Community 46 - "rag_v4_citation/test_e2e_operational.py"
Cohesion: 0.18
Nodes (16): _allow(), _answer(), _locator(), _Model, _principal(), _StaticRetriever, test_answer_workflow_consumes_parent_context_without_ranking_parent(), test_audience_and_expiry_survive_citation_delivery() (+8 more)

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
Cohesion: 0.19
Nodes (17): CitationRecord, SourceSpan, _authorization_matches(), allow_active(), citation(), test_authorization_callback_error_fails_closed(), test_current_active_version_is_required_by_authorization_attestation(), test_negation_mismatch_is_conflicting_not_supported() (+9 more)

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
Cohesion: 0.15
Nodes (5): build_secure_context(), RetrievedEvidence, PromptOperationalTests, PromptSecurityAdversarialTests, test_secure_context_escapes_parent_prompt_injection_as_untrusted_content()

### Community 58 - "admin.py"
Cohesion: 0.15
Nodes (47): AccessGrantRequest, AccessRequest, activate_user(), AdminApiState, approve_document_version(), _body(), _bump_policy_epoch(), create_department() (+39 more)

### Community 59 - "main.py"
Cohesion: 0.10
Nodes (4): get_settings(), Settings, healthz(), identity_error_handler()

### Community 60 - "dataclasses"
Cohesion: 0.11
Nodes (5): default_prompt_registry(), _freeze(), PromptDefinition, PromptRegistry, PromptRegistryTests

### Community 61 - "AuthenticationService"
Cohesion: 0.10
Nodes (5): rate_limited(), IdentityRecord, SessionRecord, utc_z(), IdentityStore

### Community 62 - "orchestration/context.py"
Cohesion: 0.19
Nodes (7): AssembledContext, ContextLimitError, estimate_tokens(), PromptMessage, _render_evidence(), _safe_text(), _safe_value()

### Community 64 - "model/test_security_adversarial.py"
Cohesion: 0.19
Nodes (22): ModelEgressDenied, EgressMode, provider(), route(), test_embedding_route_task_is_checked(), test_external_internal_requires_dpa(), test_external_internal_requires_residency(), test_external_provider_requires_retention_policy() (+14 more)

### Community 86 - "answer_baseline/test_behavior_component.py"
Cohesion: 0.08
Nodes (27): AnswerResult, AnswerStatus, DirectAnswerPipeline, HybridEvidence, HybridRetrievalResult, _DenseAsHybrid, _RrfOnly, _authorization() (+19 more)

### Community 87 - "ingestion/_baseline.py"
Cohesion: 0.15
Nodes (12): graph_labels(), read(), task(), test_task_and_handoff_keep_ingestion_provider_neutral(), test_audit_event_is_structured_without_source_checksum(), test_changed_checksum_cannot_enter_retry(), test_cleanup_failure_blocks_maintenance_recovery_then_recovery_succeeds(), test_end_to_end_clean_upload_becomes_retrievable_only_after_publish() (+4 more)

### Community 91 - "_make_case"
Cohesion: 0.22
Nodes (15): evaluation_snapshot(), _make_case(), authorize(), load_validated_records(), test_all_golden_cases_run_through_v1_v3(), test_allowed_answer_has_no_unauthorized_retrieval_marker(), test_answered_case_keeps_citation_version_and_tenant_binding(), test_dataset_contains_permission_negative_and_cross_tenant_cases() (+7 more)

### Community 94 - "rag_hybrid/test_e2e_operational.py"
Cohesion: 0.07
Nodes (60): PolicyEnforcementPoint, DenseRetriever, DeterministicEmbeddingAdapter, InMemoryDenseVectorIndex, HybridRetrievalConfig, HybridRetriever, InMemoryBM25Index, reciprocal_rank_fusion() (+52 more)

### Community 95 - "SecureContextBuilder"
Cohesion: 0.20
Nodes (3): SecureContextBuilder, SecureContextBuilderTests, test_verifier_requires_a_server_supplied_authorization_callback()

### Community 96 - "lifecycle.py"
Cohesion: 0.06
Nodes (32): _acl_digest(), ApprovalBlocked, ApprovalRecord, _chunk_digest(), _chunk_state(), DerivedIndex, DerivedIndexFailure, DerivedIndexRecord (+24 more)

### Community 97 - "test_identity.py"
Cohesion: 0.19
Nodes (12): IdentityError, AuthenticationService, make_service(), test_expired_session_is_rejected(), test_invalid_password_is_safe_auth_error(), test_mfa_is_required_for_privileged_role(), test_principal_rejects_extra_client_claims(), test_revoked_session_is_rejected() (+4 more)

### Community 98 - "ModelPolicy"
Cohesion: 0.23
Nodes (13): ModelPolicy, test_mapping_loads_versioned_policy_without_credentials(), test_policy_rejects_credential_fields(), mapping(), test_access_token_field_is_rejected(), test_exact_api_key_field_is_rejected(), test_fallback_route_task_mismatch_is_rejected(), test_mapping_rejects_empty_model_revision() (+5 more)

### Community 99 - "new_service"
Cohesion: 0.14
Nodes (26): new_service(), quarantine(), test_acknowledged_index_is_still_not_active(), test_clean_review_one_allows_processing(), test_processing_inherits_parent_acl(), test_publishing_new_version_supersedes_previous_version(), test_rejected_scan_is_terminal_and_not_retrievable(), test_review_one_requires_clean_scan() (+18 more)

### Community 100 - "knowledge/models.py"
Cohesion: 0.14
Nodes (15): PDFLocator, SourceSpan, Citation, _AnswerModel, _pipeline(), allow(), _principal(), _StaticRetriever (+7 more)

### Community 102 - "EvidenceRecord"
Cohesion: 0.10
Nodes (33): ClaimVerification, EvidenceRecord, EvidenceVerifier, _is_negative(), _numeric_conflict(), _numeric_terms(), _relation(), _terms() (+25 more)

### Community 103 - "IngestionService"
Cohesion: 0.13
Nodes (21): IngestionService, _active_document(), _principal(), _retriever(), test_dense_retrieval_returns_authorized_current_chunk_only(), test_explicit_deny_candidates_are_not_exposed(), test_forbidden_source_fetch_is_redacted_without_content_or_citation(), test_active_retrieval_to_evidence_verification_succeeds() (+13 more)

### Community 104 - "InMemoryIdentityStore"
Cohesion: 0.14
Nodes (4): DepartmentRecord, normalize_roles(), InMemoryIdentityStore, test_noncanonical_role_cannot_create_identity()

### Community 106 - "identity/models.py"
Cohesion: 0.13
Nodes (8): IdentityErrorPassthrough, now_utc(), hash_secret(), verify_secret(), _header(), _new_traceparent(), _valid_traceparent(), test_correlation_context_preserves_valid_headers_and_creates_child()

### Community 107 - "ingestion/test_behavior_component.py"
Cohesion: 0.14
Nodes (13): make_chunks(), test_child_acl_broadening_is_denied(), test_approval_expiry_blocks_processing(), test_empty_processing_input_is_rejected(), test_malware_scan_is_terminal(), test_new_active_version_supersedes_previous_version(), test_publish_activates_authoritative_version_and_chunks(), test_review_one_and_processing_require_parent_acl() (+5 more)

### Community 113 - "ingestion/test_security_adversarial.py"
Cohesion: 0.16
Nodes (10): RuntimeFailureOnRemove, service_with_index(), test_cleanup_backend_error_is_wrapped_without_secret_leakage(), test_cross_tenant_document_lookup_is_denied(), test_cross_tenant_job_lookup_is_denied(), test_cross_tenant_version_lookup_is_denied(), test_derived_staging_state_cannot_authorize_retrieval(), test_legal_hold_blocks_permanent_delete() (+2 more)

### Community 114 - "answer_baseline/test_contract_integration.py"
Cohesion: 0.19
Nodes (15): _allow(), RecordingModel, RecordingRetriever, _setup(), test_citation_authorization_rejects_document_mismatch(), test_citation_authorization_rejects_non_active_status(), test_citation_authorization_rejects_non_current_version(), test_citation_authorization_rejects_revoked_source() (+7 more)

### Community 115 - "ProviderPolicy"
Cohesion: 0.18
Nodes (3): route(), ProviderPolicy, test_reranker_gateway_contract_passes_request_route_and_timeout()

### Community 116 - "answer_baseline/test_e2e_operational.py"
Cohesion: 0.17
Nodes (16): _allow(), FailingEmbedder, FailingReranker, FakeAnswerGateway, _setup(), test_operational_abstention_is_insufficient_evidence(), test_operational_conflicting_evidence_is_not_harmonized(), test_operational_denied_content_never_appears_in_failure_result() (+8 more)

### Community 117 - "answer.py"
Cohesion: 0.15
Nodes (7): _answer_citation(), AnswerCitation, AnswerModelGateway, _expired(), _utc_z(), _valid_locator(), test_answer_citation_serializes_typed_locator_and_bindings()

### Community 119 - "guardrails/__init__.py"
Cohesion: 0.15
Nodes (6): _luhn_valid(), redact_sensitive_data(), redact_card(), RedactionResult, ToolDecision, validate_tool_request()

### Community 120 - "answer_baseline/test_security_adversarial.py"
Cohesion: 0.11
Nodes (24): GeneratedAnswer, _authorization(), FakeModelGateway, _pipeline(), test_direct_answer_returns_insufficient_without_calling_model_when_no_match(), test_direct_answer_returns_partial_for_mixed_claims(), test_direct_answer_returns_supported_answer_and_authorized_citation(), test_guardrail_failure_fails_closed_before_model_call() (+16 more)

### Community 121 - "normalize_user_input"
Cohesion: 0.17
Nodes (3): normalize_user_input(), GuardrailBehaviorTests, GuardrailSecurityAdversarialTests

### Community 122 - "AuthenticatedPrincipal"
Cohesion: 0.10
Nodes (12): AuthenticatedPrincipal, _citation(), _cosine(), DenseEvidence, DenseRetrievalResult, SourceFetchResult, _uuid(), _valid_locator() (+4 more)

### Community 124 - "validate_output"
Cohesion: 0.26
Nodes (8): _citation(), detect_prompt_injection(), GuardrailResult, _inspect_text(), _normalize_text(), _sensitive_terms(), _terms(), validate_output()

### Community 125 - "backend_boot/_baseline.py"
Cohesion: 0.06
Nodes (11): backend_boot_task(), compile_sources_without_writes(), pyproject(), read(), route_calls(), route_path(), task_packet(), tree() (+3 more)

### Community 127 - "DirectAnswerPipeline"
Cohesion: 0.29
Nodes (6): _CapturingModel, _Model, test_direct_answer_context_includes_authorized_parent_runtime(), authorize(), test_real_hybrid_path_propagates_pdf_schema_end_to_end(), authorize()

### Community 130 - "Claim"
Cohesion: 0.15
Nodes (25): AuthorizationDecision, Claim, allow_active(), citation(), test_authorizer_must_attest_active_current_and_not_revoked(), revoked(), test_citation_and_source_span_are_immutable(), test_conflicting_numeric_source_spans_are_disclosed() (+17 more)

### Community 131 - "make_manifest"
Cohesion: 0.33
Nodes (8): make_manifest(), test_failed_new_publication_preserves_previous_active_version(), test_job_contract_keeps_attempt_and_tenant_scope(), test_legacy_doc_and_xls_are_rejected(), test_mime_and_magic_boundaries_are_checked(), test_mvp_accepts_only_pdf_docx_and_xlsx(), test_private_object_storage_uri_is_required(), test_upload_size_limit_is_enforced_before_processing()

### Community 132 - "InMemoryAuditSink"
Cohesion: 0.29
Nodes (8): InMemoryAuditSink, test_audit_sink_is_append_only_and_structured(), test_unavailable_sink_does_not_accept_an_event(), _add_identity(), _request(), test_sign_in_denial_emits_no_credentials_or_body(), test_sign_in_emits_correlated_success_event(), test_sign_in_fails_closed_when_audit_sink_is_unavailable()

## Knowledge Gaps
- **1 isolated node(s):** `enterprise-agentic-rag-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 736 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **46 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AuthenticatedPrincipal` connect `AuthenticatedPrincipal` to `identity.py`, `AuthenticatedPrincipal`, `hybrid.py`, `InMemoryPolicyStore`, `ChunkMetadata`, `authorization/test_contract_integration.py`, `PolicyEnforcementPoint`, `test_authorization.py`, `eval_001_runner.py`, `expand_parent_context`, `rag_v4_citation/test_e2e_operational.py`, `admin.py`, `AuthenticationService`, `answer_baseline/test_behavior_component.py`, `rag_hybrid/test_e2e_operational.py`, `test_identity.py`, `knowledge/models.py`, `IngestionService`, `identity/models.py`, `answer.py`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Are the 45 inferred relationships involving `IngestionService` (e.g. with `reset_state()` and `test_active_retrieval_to_evidence_verification_succeeds()`) actually correct?**
  _`IngestionService` has 45 INFERRED edges - model-reasoned connections that need verification._
- **What connects `enterprise-agentic-rag-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `audit.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11612903225806452 - nodes in this community are weakly interconnected._
- **Why does `DataClassification` connect `test_models.py` to `make_manifest`, `.__init__`, `pytest`, `hybrid.py`, `eval_001_runner.py`, `model/test_e2e_operational.py`, `expand_parent_context`, `rag_v4_citation/test_e2e_operational.py`, `admin.py`, `model/test_security_adversarial.py`, `answer_baseline/test_behavior_component.py`, `rag_hybrid/test_e2e_operational.py`, `lifecycle.py`, `ModelPolicy`, `knowledge/models.py`, `IngestionService`, `answer_baseline/test_contract_integration.py`, `ProviderPolicy`, `answer_baseline/test_e2e_operational.py`, `answer.py`, `answer_baseline/test_security_adversarial.py`, `AuthenticatedPrincipal`, `DirectAnswerPipeline`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Are the 47 inferred relationships involving `DataClassification` (e.g. with `ModelEgressDenied` and `ModelGateway`) actually correct?**
  _`DataClassification` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Should `compose` be split into smaller, more focused modules?**
  _Cohesion score 0.06778476589797344 - nodes in this community are weakly interconnected._