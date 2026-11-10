# Graph Report - enterprise-agentic-rag-harness  (2026-11-11)

## Corpus Check
- 233 files · ~195,911 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 68 file(s) not represented in the graph (top: (none) 53, .toml 9, .example 2)

## Summary
- 2905 nodes · 8329 edges · 151 communities (98 shown, 53 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 949 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ac4bfe8a`
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
- make_manifest
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
- _AnswerModel
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
- active
- _make_case
- PromptContractIntegrationTests
- rag_hybrid/test_e2e_operational.py
- SecureContextBuilder
- lifecycle.py
- test_identity.py
- ModelPolicy
- validated
- knowledge/models.py
- EvidenceVerifier
- IngestionService
- rag_v4_citation/test_contract_integration.py
- FrontendE2EOperationalTests
- identity/models.py
- ingestion/test_behavior_component.py
- ingestion/test_security_adversarial.py
- answer_baseline/test_contract_integration.py
- eval_001_runner.py
- answer_baseline/test_e2e_operational.py
- answer.py
- rag/__init__.py
- guardrails/__init__.py
- answer_baseline/test_security_adversarial.py
- normalize_user_input
- AuthenticatedPrincipal
- recall_at_k
- validate_output
- backend_boot/_baseline.py
- IdentityContractTests
- DirectAnswerPipeline
- run_local_guardrail_pipeline
- Citation
- Claim
- Claim
- authorization/test_behavior_component.py
- PromptBehaviorComponentTests
- ingestion/_baseline.py
- ModelProviderError
- KnowledgeOperationalTests
- rag_v4_citation/test_security_adversarial.py
- test_dense_retrieval.py
- env.py
- test_answer_baseline.py
- BackendBootstrapSecurityTests
- evidence/test_contract_integration.py
- observability/context.py
- pathlib
- IdentityBehaviorTests
- IdentitySecurityTests
- AnswerModelGateway
- identity/_baseline.py

## God Nodes (most connected - your core abstractions)
1. `IngestionService` - 116 edges
2. `DataClassification` - 93 edges
3. `auth()` - 87 edges
4. `request()` - 86 edges
5. `new_service()` - 85 edges
6. `_active_document()` - 78 edges
7. `AuthenticatedPrincipal` - 68 edges
8. `ChunkMetadata` - 67 edges
9. `_principal()` - 65 edges
10. `_make_retriever()` - 64 edges

## Surprising Connections (you probably didn't know these)
- `authorize()` --calls--> `AuthorizationDecision`  [INFERRED]
  tests/integration/test_answer_citation_schema.py → backend/app/evidence/verifier.py
- `authorize()` --calls--> `AuthorizationDecision`  [INFERRED]
  tests/evaluation/eval_001_runner.py → backend/app/evidence/verifier.py
- `authorize()` --calls--> `AuthorizationDecision`  [INFERRED]
  tests/integration/test_answer_baseline.py → backend/app/evidence/verifier.py
- `authorize()` --calls--> `AuthorizationDecision`  [INFERRED]
  tests/qa/answer_baseline/test_security_adversarial.py → backend/app/evidence/verifier.py
- `KnowledgeBehaviorTests` --uses--> `SourceSpan`  [INFERRED]
  tests/qa/knowledge/test_behavior_component.py → backend/app/knowledge/models.py

## Import Cycles
- 2-file cycle: `backend/app/api/admin.py -> backend/app/api/identity.py -> backend/app/api/admin.py`

## Communities (151 total, 53 thin omitted)

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
Cohesion: 0.18
Nodes (10): _bearer_token(), current_identity(), _record(), _record_identity_error(), _request_context(), sign_in(), sign_out(), SignInRequest (+2 more)

### Community 14 - "AuthenticatedPrincipal"
Cohesion: 0.07
Nodes (15): Action, AuthorizationDenied, AuthorizationEvaluator, deny(), Classification, ConversationResource, Decision, Effect (+7 more)

### Community 15 - "make_manifest"
Cohesion: 0.15
Nodes (17): UploadManifest, make_manifest(), test_rejected_scan_is_terminal_and_not_retrievable(), test_doc_is_rejected(), test_internal_upload_requires_department(), test_non_private_source_is_rejected(), test_pdf_is_accepted(), test_sha256_must_be_a_digest() (+9 more)

### Community 16 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, networks (+12 more)

### Community 17 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, networks (+12 more)

### Community 18 - "active"
Cohesion: 0.12
Nodes (32): new_service(), staged(), test_acknowledged_index_is_still_not_active(), test_approval_expiry_blocks_publication(), test_audit_sink_receives_lifecycle_events_without_content(), test_failed_maintenance_can_be_recovered_after_cleanup(), test_non_retryable_failure_is_terminal(), test_only_one_maintenance_window_is_active() (+24 more)

### Community 19 - "package.json"
Cohesion: 0.13
Nodes (19): devDependencies, eslint@9.17.0, jsdom@25.0.1, @types/node@22.10.5, @types/react@18.3.18, @types/react-dom@18.3.5, typescript@5.7.2, engines (+11 more)

### Community 20 - "hybrid.py"
Cohesion: 0.14
Nodes (9): EmbeddingAdapter, EmbeddingRequest, EmbeddingResult, RerankerAdapter, RerankerResult, ModelRoute, _cosine(), _uuid() (+1 more)

### Community 21 - "InMemoryPolicyStore"
Cohesion: 0.43
Nodes (4): AuthorizationSecurityAdversarialTests, document(), evaluator(), principal()

### Community 22 - "ChunkMetadata"
Cohesion: 0.14
Nodes (11): ChunkMetadata, DocumentMetadata, SourceSpan, test_active_chunk_requires_acl_metadata(), test_chunk_accepts_source_provenance(), test_chunk_rejects_reversed_pages(), test_chunk_rejects_self_parent(), test_document_metadata_is_tenant_scoped() (+3 more)

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
Cohesion: 0.16
Nodes (4): load_records(), test_dashboard_has_api_and_security_panels(), test_dashboard_is_valid_json(), test_rag002_task_registry_keeps_retrieval_validation_and_scope()

### Community 27 - "authorization/test_contract_integration.py"
Cohesion: 0.26
Nodes (4): AuthorizationContractIntegrationTests, document(), evaluator(), principal()

### Community 28 - "PolicyEnforcementPoint"
Cohesion: 0.33
Nodes (4): AuthorizationOperationalTests, document(), evaluator(), principal()

### Community 29 - "BackendBootstrapBehaviorTests"
Cohesion: 0.15
Nodes (5): assignment(), calls(), function(), literal(), BackendBootstrapBehaviorTests

### Community 30 - "test_models.py"
Cohesion: 0.14
Nodes (41): ModelGateway, ModelUnavailable, DataClassification, EgressMode, ModelTask, FakeEmbedding, policy(), provider() (+33 more)

### Community 31 - "test_authorization.py"
Cohesion: 0.27
Nodes (16): InMemoryPolicyStore, document(), evaluator(), principal(), test_acl_can_assign_employee_and_explicit_deny_wins_for_chairman(), test_anonymous_is_public_only(), test_chairman_is_read_only(), test_conversation_body_is_owner_only() (+8 more)

### Community 33 - "GraphifyOperationalTests"
Cohesion: 0.15
Nodes (5): graph(), graphify_bin(), run_graphify(), GraphifyOperationalTests, run_graph_query()

### Community 34 - "auth"
Cohesion: 0.06
Nodes (102): ScanReport, ScanVerdict, add_user(), auth(), key(), prepare_review_two(), publish(), request() (+94 more)

### Community 35 - "_evaluation_harness.py"
Cohesion: 0.15
Nodes (15): _Case, evaluate(), render_report(), _run_version(), answer_correctness(), citation_accuracy(), evaluate_case(), ndcg_at_k() (+7 more)

### Community 36 - "steps"
Cohesion: 0.15
Nodes (12): jobs, validate, name, on, pull_request, workflow_dispatch, run, uses (+4 more)

### Community 40 - "rules"
Cohesion: 0.17
Nodes (11): runbook, summary, groups, name, rules, severity, alert, annotations (+3 more)

### Community 41 - "model/test_e2e_operational.py"
Cohesion: 0.14
Nodes (18): graph_labels(), policy(), route(), run_graph_query(), ScriptedEmbedding, ScriptedReranker, task(), test_embedding_result_keeps_selected_route() (+10 more)

### Community 42 - "expand_parent_context"
Cohesion: 0.18
Nodes (26): expand_parent_context(), child(), parent(), test_callback_failure_fails_closed_for_parent_only(), test_cross_tenant_parent_is_never_authorized_or_returned(), test_denied_parent_does_not_change_child_result(), test_duplicate_children_and_parents_are_deduplicated_with_all_provenance(), test_expands_authorized_parent_and_preserves_child_citation() (+18 more)

### Community 44 - "eslint.config.js"
Cohesion: 0.18
Nodes (10): @eslint/js@9.17.0, eslint-plugin-react-hooks@5.1.0, eslint-plugin-react-refresh@0.4.16, globals@15.14.0, typescript-eslint@8.18.0, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh (+2 more)

### Community 45 - "route"
Cohesion: 0.18
Nodes (10): global, resolve_timeout, receivers, name, route, group_by, group_interval, group_wait (+2 more)

### Community 46 - "rag_v4_citation/test_e2e_operational.py"
Cohesion: 0.14
Nodes (21): DOCXLocator, _ImmutableModel, XLSXLocator, _valid_locator(), test_malformed_locator_model_is_rejected(), _allow(), _answer(), _locator() (+13 more)

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
Cohesion: 0.26
Nodes (15): EvidenceRecord, SourceSpan, citation(), test_authorization_callback_error_fails_closed(), test_current_active_version_is_required_by_authorization_attestation(), test_negation_mismatch_is_conflicting_not_supported(), test_numeric_mismatch_is_conflicting_not_supported(), test_repeated_verification_is_deterministic() (+7 more)

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
Cohesion: 0.14
Nodes (3): get_settings(), Settings, healthz()

### Community 60 - "dataclasses"
Cohesion: 0.11
Nodes (5): default_prompt_registry(), _freeze(), PromptDefinition, PromptRegistry, PromptRegistryTests

### Community 61 - "AuthenticationService"
Cohesion: 0.08
Nodes (7): DepartmentRecord, IdentityRecord, normalize_roles(), SessionRecord, IdentityStore, InMemoryIdentityStore, test_noncanonical_role_cannot_create_identity()

### Community 62 - "orchestration/context.py"
Cohesion: 0.19
Nodes (7): AssembledContext, ContextLimitError, estimate_tokens(), PromptMessage, _render_evidence(), _safe_text(), _safe_value()

### Community 64 - "model/test_security_adversarial.py"
Cohesion: 0.20
Nodes (17): ModelEgressDenied, provider(), test_external_internal_requires_dpa(), test_external_internal_requires_residency(), test_external_provider_requires_retention_policy(), test_external_unapproved_provider_is_denied(), test_primary_retries_cannot_exceed_two(), test_provider_allowlist_is_required() (+9 more)

### Community 86 - "answer_baseline/test_behavior_component.py"
Cohesion: 0.14
Nodes (22): AnswerResult, AnswerStatus, DirectAnswerPipeline, _authorization(), FakeModelGateway, _pipeline(), RaisingRetriever, RaisingVerifier (+14 more)

### Community 87 - "active"
Cohesion: 0.15
Nodes (18): active(), quarantine(), test_publishing_new_version_supersedes_previous_version(), test_review_one_requires_clean_scan(), test_revoke_active_version_removes_retrieval(), test_second_review_and_publish_make_version_active(), test_soft_delete_isolates_all_versions(), test_upload_starts_quarantined_and_not_retrievable() (+10 more)

### Community 91 - "_make_case"
Cohesion: 0.19
Nodes (17): evaluation_snapshot(), _make_case(), authorize(), _principal(), _uuid(), load_validated_records(), test_all_golden_cases_run_through_v1_v3(), test_allowed_answer_has_no_unauthorized_retrieval_marker() (+9 more)

### Community 94 - "rag_hybrid/test_e2e_operational.py"
Cohesion: 0.07
Nodes (53): AccessGrant, InMemoryDenseVectorIndex, HybridRetrievalConfig, HybridRetriever, InMemoryBM25Index, reciprocal_rank_fusion(), _gateway(), _make_parent_child_retriever() (+45 more)

### Community 95 - "SecureContextBuilder"
Cohesion: 0.20
Nodes (3): SecureContextBuilder, SecureContextBuilderTests, test_verifier_requires_a_server_supplied_authorization_callback()

### Community 96 - "lifecycle.py"
Cohesion: 0.06
Nodes (31): _acl_digest(), ApprovalBlocked, ApprovalRecord, _chunk_digest(), _chunk_state(), DerivedIndex, DerivedIndexFailure, DerivedIndexRecord (+23 more)

### Community 97 - "test_identity.py"
Cohesion: 0.17
Nodes (13): IdentityError, rate_limited(), AuthenticationService, make_service(), test_expired_session_is_rejected(), test_invalid_password_is_safe_auth_error(), test_mfa_is_required_for_privileged_role(), test_principal_rejects_extra_client_claims() (+5 more)

### Community 98 - "ModelPolicy"
Cohesion: 0.19
Nodes (18): ModelPolicy, test_embedding_request_rejects_blank_text(), test_embedding_request_requires_texts(), test_mapping_loads_versioned_policy_without_credentials(), test_policy_rejects_credential_fields(), test_route_task_mismatch_is_rejected_by_policy(), mapping(), test_embedding_route_task_is_checked() (+10 more)

### Community 99 - "validated"
Cohesion: 0.26
Nodes (11): IndexManifest, validated(), test_clean_review_one_allows_processing(), test_processing_inherits_parent_acl(), test_manifest_checksum_mismatch_blocks_staging(), test_manifest_count_mismatch_blocks_staging(), test_publication_requires_index_ack(), test_index_ack_is_a_publication_gate() (+3 more)

### Community 100 - "knowledge/models.py"
Cohesion: 0.14
Nodes (15): PDFLocator, Citation, _FusedCandidate, _AnswerModel, _pipeline(), allow(), _principal(), _StaticRetriever (+7 more)

### Community 102 - "EvidenceVerifier"
Cohesion: 0.19
Nodes (9): ClaimVerification, EvidenceVerifier, _is_negative(), _numeric_conflict(), _numeric_terms(), _relation(), _terms(), VerificationOutcome (+1 more)

### Community 103 - "IngestionService"
Cohesion: 0.12
Nodes (21): IngestionService, _active_document(), _principal(), _retriever(), test_dense_retrieval_returns_authorized_current_chunk_only(), test_explicit_deny_candidates_are_not_exposed(), test_forbidden_source_fetch_is_redacted_without_content_or_citation(), test_active_retrieval_to_evidence_verification_succeeds() (+13 more)

### Community 104 - "rag_v4_citation/test_contract_integration.py"
Cohesion: 0.10
Nodes (18): HybridRetrievalResult, _active(), ParentRecord, _DenseAsHybrid, _RrfOnly, _allow(), _CapturingModel, _citation() (+10 more)

### Community 106 - "identity/models.py"
Cohesion: 0.16
Nodes (5): utc_z(), IdentityErrorPassthrough, now_utc(), hash_secret(), verify_secret()

### Community 107 - "ingestion/test_behavior_component.py"
Cohesion: 0.14
Nodes (13): make_chunks(), test_child_acl_broadening_is_denied(), test_approval_expiry_blocks_processing(), test_empty_processing_input_is_rejected(), test_malware_scan_is_terminal(), test_new_active_version_supersedes_previous_version(), test_publish_activates_authoritative_version_and_chunks(), test_review_one_and_processing_require_parent_acl() (+5 more)

### Community 113 - "ingestion/test_security_adversarial.py"
Cohesion: 0.16
Nodes (10): RuntimeFailureOnRemove, service_with_index(), test_cleanup_backend_error_is_wrapped_without_secret_leakage(), test_cross_tenant_document_lookup_is_denied(), test_cross_tenant_job_lookup_is_denied(), test_cross_tenant_version_lookup_is_denied(), test_derived_staging_state_cannot_authorize_retrieval(), test_legal_hold_blocks_permanent_delete() (+2 more)

### Community 114 - "answer_baseline/test_contract_integration.py"
Cohesion: 0.19
Nodes (15): _allow(), RecordingModel, RecordingRetriever, _setup(), test_citation_authorization_rejects_document_mismatch(), test_citation_authorization_rejects_non_active_status(), test_citation_authorization_rejects_non_current_version(), test_citation_authorization_rejects_revoked_source() (+7 more)

### Community 115 - "eval_001_runner.py"
Cohesion: 0.11
Nodes (15): RerankerRequest, route(), ProviderPolicy, DeterministicRerankerAdapter, _tokens(), test_reranker_request_rejects_blank_document_fields(), test_reranker_request_requires_documents(), test_reranker_request_requires_query() (+7 more)

### Community 116 - "answer_baseline/test_e2e_operational.py"
Cohesion: 0.14
Nodes (17): GeneratedAnswer, _allow(), FailingEmbedder, FailingReranker, FakeAnswerGateway, _setup(), test_operational_abstention_is_insufficient_evidence(), test_operational_conflicting_evidence_is_not_harmonized() (+9 more)

### Community 117 - "answer.py"
Cohesion: 0.22
Nodes (8): _answer_citation(), AnswerCitation, _authorization_matches(), _expired(), _utc_z(), _valid_locator(), HybridEvidence, test_answer_citation_serializes_typed_locator_and_bindings()

### Community 118 - "rag/__init__.py"
Cohesion: 0.16
Nodes (14): DenseEvidence, DenseRetrievalResult, ChildEvidence, _coerce_child(), _coerce_parent(), _construct(), _identity(), _index_parents() (+6 more)

### Community 119 - "guardrails/__init__.py"
Cohesion: 0.15
Nodes (6): _luhn_valid(), redact_sensitive_data(), redact_card(), RedactionResult, ToolDecision, validate_tool_request()

### Community 120 - "answer_baseline/test_security_adversarial.py"
Cohesion: 0.19
Nodes (15): _allow(), authorize(), FakeModelGateway, _pipeline(), test_cross_tenant_evidence_is_absent_from_dense_bm25_and_answer(), test_direct_prompt_injection_is_denied_before_retrieval_and_model(), test_duplicate_and_unknown_citation_ids_do_not_duplicate_or_leak_metadata(), test_indirect_prompt_injection_is_removed_before_model_context() (+7 more)

### Community 121 - "normalize_user_input"
Cohesion: 0.17
Nodes (3): normalize_user_input(), GuardrailBehaviorTests, GuardrailSecurityAdversarialTests

### Community 122 - "AuthenticatedPrincipal"
Cohesion: 0.13
Nodes (7): AuthenticatedPrincipal, _citation(), DenseRetriever, SourceFetchResult, _VectorRecord, _BM25Record, _citation()

### Community 123 - "recall_at_k"
Cohesion: 0.29
Nodes (8): mean_reciprocal_rank(), recall_at_k(), _span(), _spans(), test_rag_002_regression_metrics_on_tiny_in_memory_corpus(), metrics(), _span(), test_hybrid_metrics_regressions_remain_at_perfect_tiny_corpus_baseline()

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
Cohesion: 0.13
Nodes (25): AuthorizationDecision, CitationRecord, allow_active(), citation(), test_authorizer_must_attest_active_current_and_not_revoked(), revoked(), test_citation_and_source_span_are_immutable(), test_conflicting_numeric_source_spans_are_disclosed() (+17 more)

### Community 131 - "Claim"
Cohesion: 0.26
Nodes (18): Claim, VerificationRequest, allow_active(), citation(), test_authorization_callback_exception_fails_closed(), test_cross_tenant_evidence_is_denied_before_authorizer_invocation(), unexpected(), test_denied_result_does_not_leak_source_text() (+10 more)

### Community 132 - "authorization/test_behavior_component.py"
Cohesion: 0.32
Nodes (5): AnonymousPrincipal, AuthorizationBehaviorTests, document(), evaluator(), principal()

### Community 134 - "ingestion/_baseline.py"
Cohesion: 0.19
Nodes (5): Clock, graph_labels(), read(), task(), test_task_and_handoff_keep_ingestion_provider_neutral()

### Community 135 - "ModelProviderError"
Cohesion: 0.18
Nodes (5): ModelProviderError, RankedDocument, FakeReranker, test_gateway_reranker_happy_path(), test_ranked_document_preserves_identifier_and_score()

### Community 136 - "KnowledgeOperationalTests"
Cohesion: 0.20
Nodes (3): read(), task(), KnowledgeOperationalTests

### Community 137 - "rag_v4_citation/test_security_adversarial.py"
Cohesion: 0.29
Nodes (13): _child(), _locator(), _parent(), _principal(), test_answer_rejects_cross_tenant_citation_before_authorizer(), test_cross_document_parent_is_not_expanded(), test_cross_tenant_parent_is_not_even_sent_to_authorizer(), test_cross_version_parent_is_not_expanded() (+5 more)

### Community 138 - "test_dense_retrieval.py"
Cohesion: 0.33
Nodes (7): DocumentResource, DeterministicEmbeddingAdapter, _gateway(), _resource(), test_cross_tenant_candidates_are_not_exposed(), test_stale_policy_and_non_active_version_fail_closed(), _multi_retriever()

### Community 139 - "env.py"
Cohesion: 0.19
Nodes (4): _database_url(), run_migrations_offline(), run_migrations_online(), DatabaseMigrationSmokeTests

### Community 140 - "test_answer_baseline.py"
Cohesion: 0.32
Nodes (10): _authorization(), authorize(), FakeModelGateway, _pipeline(), test_direct_answer_returns_insufficient_without_calling_model_when_no_match(), test_direct_answer_returns_partial_for_mixed_claims(), test_direct_answer_returns_supported_answer_and_authorized_citation(), test_guardrail_failure_fails_closed_before_model_call() (+2 more)

### Community 142 - "evidence/test_contract_integration.py"
Cohesion: 0.23
Nodes (6): allow_active(), citation(), test_chat_001_owns_preview_download_reauthorization_recheck(), test_duplicate_evidence_ids_are_a_malformed_fail_closed_result(), authorize(), test_supported_result_round_trips_tenant_document_version_and_span()

### Community 143 - "observability/context.py"
Cohesion: 0.20
Nodes (5): identity_error_handler(), _header(), _new_traceparent(), _valid_traceparent(), test_correlation_context_preserves_valid_headers_and_creates_child()

## Knowledge Gaps
- **1 isolated node(s):** `enterprise-agentic-rag-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 736 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **53 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AuthenticatedPrincipal` connect `AuthenticatedPrincipal` to `authorization/test_behavior_component.py`, `rag_v4_citation/test_security_adversarial.py`, `test_dense_retrieval.py`, `identity.py`, `AuthenticatedPrincipal`, `field_validator`, `hybrid.py`, `InMemoryPolicyStore`, `authorization/test_contract_integration.py`, `PolicyEnforcementPoint`, `test_authorization.py`, `rag_v4_citation/test_e2e_operational.py`, `admin.py`, `AuthenticationService`, `answer_baseline/test_behavior_component.py`, `_make_case`, `rag_hybrid/test_e2e_operational.py`, `test_identity.py`, `knowledge/models.py`, `IngestionService`, `rag_v4_citation/test_contract_integration.py`, `identity/models.py`, `eval_001_runner.py`, `answer.py`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Are the 45 inferred relationships involving `IngestionService` (e.g. with `reset_state()` and `test_active_retrieval_to_evidence_verification_succeeds()`) actually correct?**
  _`IngestionService` has 45 INFERRED edges - model-reasoned connections that need verification._
- **What connects `enterprise-agentic-rag-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `audit.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10121951219512196 - nodes in this community are weakly interconnected._
- **Why does `DataClassification` connect `test_models.py` to `ModelProviderError`, `rag_v4_citation/test_security_adversarial.py`, `test_dense_retrieval.py`, `test_answer_baseline.py`, `make_manifest`, `hybrid.py`, `AnswerModelGateway`, `_AnswerModel`, `model/test_e2e_operational.py`, `rag_v4_citation/test_e2e_operational.py`, `admin.py`, `model/test_security_adversarial.py`, `answer_baseline/test_behavior_component.py`, `rag_hybrid/test_e2e_operational.py`, `lifecycle.py`, `ModelPolicy`, `knowledge/models.py`, `IngestionService`, `rag_v4_citation/test_contract_integration.py`, `answer_baseline/test_contract_integration.py`, `eval_001_runner.py`, `answer_baseline/test_e2e_operational.py`, `answer.py`, `answer_baseline/test_security_adversarial.py`, `DirectAnswerPipeline`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Are the 47 inferred relationships involving `DataClassification` (e.g. with `ModelEgressDenied` and `ModelGateway`) actually correct?**
  _`DataClassification` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Should `compose` be split into smaller, more focused modules?**
  _Cohesion score 0.06778476589797344 - nodes in this community are weakly interconnected._