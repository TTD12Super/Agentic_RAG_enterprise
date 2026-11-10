# Graph Report - enterprise-agentic-rag-harness  (2026-11-10)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2457 nodes · 6648 edges · 135 communities (80 shown, 55 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 802 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fc872435`
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
- identity/models.py
- postgres
- postgres
- authorization/test_behavior_component.py
- package.json
- ModelRoute
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
- E2EOperationalTests
- steps
- BehaviorComponentTests
- ContractIntegrationTests
- SecurityAdversarialTests
- rules
- backend_boot/_baseline.py
- read
- eslint.config.js
- route
- BackendBootstrapSecurityTests
- test_knowledge_database.py
- test_knowledge_security.py
- to_qdrant_payload
- App.tsx
- datasources
- monitoring/prometheus.yml
- _make_retriever
- dependencies
- vitest
- scripts
- build_secure_context
- admin.py
- main.py
- dataclasses
- AuthenticationService
- orchestration/context.py
- EgressMode
- vite-env.d.ts
- sync_graph.sh
- migrate.sh
- inspect_untrusted_content
- enterprise-agentic-rag-backend
- model/test_e2e_operational.py
- pytest
- lifecycle.py
- PromptContractIntegrationTests
- hybrid.py
- SecureContextBuilder
- test_dense_retrieval.py
- test_identity.py
- rag_hybrid/test_security_adversarial.py
- new_service
- IdentityContractTests
- ProviderPolicy
- IngestionService
- admin.py
- FrontendE2EOperationalTests
- IdentityBehaviorTests
- IdentitySecurityTests
- active
- env.py
- make_manifest
- observability/context.py
- ndcg_at_k
- identity/_baseline.py
- guardrails/__init__.py
- RetrievedEvidence
- normalize_user_input
- DenseRetriever
- InMemoryAuditSink
- validate_output
- ingestion/_baseline.py
- ingestion/test_behavior_component.py
- ingestion/test_security_adversarial.py
- run_local_guardrail_pipeline
- Citation
- pathlib
- validated
- quarantine
- KnowledgeContractIntegrationTests
- rag/test_contract_integration.py

## God Nodes (most connected - your core abstractions)
1. `IngestionService` - 100 edges
2. `auth()` - 87 edges
3. `request()` - 86 edges
4. `new_service()` - 85 edges
5. `DataClassification` - 78 edges
6. `_active_document()` - 65 edges
7. `key()` - 62 edges
8. `ModelGateway` - 61 edges
9. `ChunkMetadata` - 60 edges
10. `AuthenticatedPrincipal` - 55 edges

## Surprising Connections (you probably didn't know these)
- `policy()` --uses--> `ProviderPolicy`  [INFERRED]
  tests/qa/model/_baseline.py → backend/app/models/policy.py
- `route()` --uses--> `ProviderPolicy`  [INFERRED]
  tests/qa/model/_baseline.py → backend/app/models/policy.py
- `DenseRetrievalBehaviorTests` --uses--> `DenseRetriever`  [INFERRED]
  tests/qa/rag/test_behavior_component.py → backend/app/rag/dense.py
- `DenseRetrievalBehaviorTests` --uses--> `DeterministicEmbeddingAdapter`  [INFERRED]
  tests/qa/rag/test_behavior_component.py → backend/app/rag/dense.py
- `DenseRetrievalOperationalTests` --uses--> `DenseRetriever`  [INFERRED]
  tests/qa/rag/test_e2e_operational.py → backend/app/rag/dense.py

## Import Cycles
- 2-file cycle: `backend/app/api/admin.py -> backend/app/api/identity.py -> backend/app/api/admin.py`

## Communities (135 total, 55 thin omitted)

### Community 0 - "audit.py"
Cohesion: 0.12
Nodes (9): append_audit_event(), AuditEvent, AuditSink, AuditSinkUnavailable, redact_metadata(), _safe_code(), _safe_identifier(), _utc_z() (+1 more)

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
Cohesion: 0.07
Nodes (7): read(), GraphifyBehaviorTests, GraphifyContractTests, GraphifySecurityTests, read(), task(), KnowledgeOperationalTests

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
Nodes (12): Action, AuthorizationDenied, AuthorizationEvaluator, deny(), Classification, Decision, Effect, _normalize_action() (+4 more)

### Community 15 - "identity/models.py"
Cohesion: 0.11
Nodes (8): DepartmentRecord, normalize_roles(), Role, utc_z(), IdentityErrorPassthrough, now_utc(), hash_secret(), verify_secret()

### Community 16 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, networks (+12 more)

### Community 17 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, networks (+12 more)

### Community 18 - "authorization/test_behavior_component.py"
Cohesion: 0.26
Nodes (6): AnonymousPrincipal, ConversationResource, AuthorizationBehaviorTests, document(), evaluator(), principal()

### Community 19 - "package.json"
Cohesion: 0.13
Nodes (19): devDependencies, eslint@9.17.0, jsdom@25.0.1, @types/node@22.10.5, @types/react@18.3.18, @types/react-dom@18.3.5, typescript@5.7.2, engines (+11 more)

### Community 20 - "ModelRoute"
Cohesion: 0.08
Nodes (20): ModelProviderError, EmbeddingAdapter, EmbeddingRequest, EmbeddingResult, RankedDocument, RerankerAdapter, RerankerResult, ModelRoute (+12 more)

### Community 21 - "InMemoryPolicyStore"
Cohesion: 0.27
Nodes (5): InMemoryPolicyStore, AuthorizationSecurityAdversarialTests, document(), evaluator(), principal()

### Community 22 - "ChunkMetadata"
Cohesion: 0.11
Nodes (12): ChunkMetadata, DocumentMetadata, _ImmutableModel, test_root_chunk_without_acl_fails_closed(), test_active_chunk_requires_acl_metadata(), test_chunk_accepts_source_provenance(), test_chunk_rejects_reversed_pages(), test_chunk_rejects_self_parent() (+4 more)

### Community 23 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+10 more)

### Community 24 - "DocumentVersionMetadata"
Cohesion: 0.10
Nodes (8): DocumentVersionMetadata, test_document_version_identity_is_stable(), test_document_version_requires_private_source(), test_hashes_are_normalized(), test_version_contract_has_immutable_version_number(), test_version_contract_supports_publication_states(), make_document(), KnowledgeBehaviorTests

### Community 25 - "inherit_acl"
Cohesion: 0.29
Nodes (4): inherit_acl(), make_child(), make_parent(), KnowledgeSecurityAdversarialTests

### Community 27 - "authorization/test_contract_integration.py"
Cohesion: 0.27
Nodes (4): AuthorizationContractIntegrationTests, document(), evaluator(), principal()

### Community 28 - "PolicyEnforcementPoint"
Cohesion: 0.32
Nodes (4): AuthorizationOperationalTests, document(), evaluator(), principal()

### Community 29 - "BackendBootstrapBehaviorTests"
Cohesion: 0.13
Nodes (5): assignment(), calls(), function(), literal(), BackendBootstrapBehaviorTests

### Community 30 - "test_models.py"
Cohesion: 0.17
Nodes (38): DataClassification, ModelTask, FakeEmbedding, policy(), provider(), route(), test_approved_local_fallback_can_handle_internal_data(), test_approved_local_provider_can_process_internal_data() (+30 more)

### Community 31 - "test_authorization.py"
Cohesion: 0.40
Nodes (15): document(), evaluator(), principal(), test_acl_can_assign_employee_and_explicit_deny_wins_for_chairman(), test_anonymous_is_public_only(), test_chairman_is_read_only(), test_conversation_body_is_owner_only(), test_conversation_requires_conversation_resource() (+7 more)

### Community 32 - "_evaluation_harness.py"
Cohesion: 0.32
Nodes (9): answer_correctness(), citation_accuracy(), evaluate_case(), load_records(), no_answer_accuracy(), unauthorized_retrieval_rate(), validate_dataset(), validate_record() (+1 more)

### Community 33 - "GraphifyOperationalTests"
Cohesion: 0.17
Nodes (4): graph(), graphify_bin(), run_graphify(), GraphifyOperationalTests

### Community 34 - "auth"
Cohesion: 0.05
Nodes (102): ScanVerdict, SourceSpan, add_user(), auth(), key(), prepare_review_two(), publish(), request() (+94 more)

### Community 36 - "steps"
Cohesion: 0.15
Nodes (12): jobs, validate, name, on, pull_request, workflow_dispatch, run, uses (+4 more)

### Community 40 - "rules"
Cohesion: 0.17
Nodes (11): runbook, summary, groups, name, rules, severity, alert, annotations (+3 more)

### Community 42 - "backend_boot/_baseline.py"
Cohesion: 0.08
Nodes (10): backend_boot_task(), compile_sources_without_writes(), pyproject(), read(), route_calls(), route_path(), task_packet(), tree() (+2 more)

### Community 44 - "eslint.config.js"
Cohesion: 0.18
Nodes (10): @eslint/js@9.17.0, eslint-plugin-react-hooks@5.1.0, eslint-plugin-react-refresh@0.4.16, globals@15.14.0, typescript-eslint@8.18.0, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh (+2 more)

### Community 45 - "route"
Cohesion: 0.18
Nodes (10): global, resolve_timeout, receivers, name, route, group_by, group_interval, group_wait (+2 more)

### Community 47 - "test_knowledge_database.py"
Cohesion: 0.26
Nodes (11): migration_text(), test_existing_db_contract_has_active_index_guard(), test_existing_db_contract_has_chunks_table(), test_existing_db_contract_has_composite_parent_fk(), test_existing_db_contract_has_document_versions_table(), test_existing_db_contract_has_documents_table(), test_existing_db_contract_has_immutable_version_uniqueness(), test_existing_db_contract_has_private_source_constraint() (+3 more)

### Community 48 - "test_knowledge_security.py"
Cohesion: 0.38
Nodes (12): make_child(), make_parent(), test_conflicting_child_acl_is_denied(), test_document_mismatch_is_denied(), test_matching_child_acl_is_preserved(), test_missing_child_acl_is_inherited(), test_qdrant_projection_does_not_claim_authority(), test_qdrant_projection_keeps_tenant_boundary() (+4 more)

### Community 49 - "to_qdrant_payload"
Cohesion: 0.39
Nodes (10): to_qdrant_payload(), make_child(), make_parent(), test_acl_inheritance_populates_child_reference(), test_parent_child_contract_keeps_same_scope(), test_qdrant_projection_contains_index_state(), test_qdrant_projection_contains_scope_keys(), test_qdrant_projection_does_not_store_chunk_text() (+2 more)

### Community 50 - "App.tsx"
Cohesion: 0.27
Nodes (5): react@18.3.1, App(), supportedRoles, appConfig, react

### Community 51 - "datasources"
Cohesion: 0.22
Nodes (8): apiVersion, datasources, access, editable, isDefault, name, type, url

### Community 52 - "monitoring/prometheus.yml"
Cohesion: 0.22
Nodes (8): global, evaluation_interval, scrape_interval, rule_files, scrape_configs, job_name, static_configs, targets

### Community 53 - "_make_retriever"
Cohesion: 0.13
Nodes (23): reciprocal_rank_fusion(), _make_retriever(), test_hybrid_retrieval_composes_bm25_rrf_and_local_reranker(), test_bm25_length_normalization_prefers_shorter_equal_match(), test_bm25_repeated_query_term_has_frequency_weight(), test_bm25_tokenization_casefolds_and_splits_punctuation(), test_hybrid_composition_preserves_rrf_and_rerank_scores(), test_hybrid_fusion_deduplicates_a_chunk_shared_by_dense_and_bm25() (+15 more)

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
Cohesion: 0.14
Nodes (3): build_secure_context(), PromptBehaviorComponentTests, PromptOperationalTests

### Community 58 - "admin.py"
Cohesion: 0.28
Nodes (29): activate_user(), approve_document_version(), _body(), _bump_policy_epoch(), create_department(), create_user(), delete_document(), _department_payload() (+21 more)

### Community 59 - "main.py"
Cohesion: 0.10
Nodes (4): get_settings(), Settings, healthz(), identity_error_handler()

### Community 60 - "dataclasses"
Cohesion: 0.12
Nodes (5): default_prompt_registry(), _freeze(), PromptDefinition, PromptRegistry, PromptRegistryTests

### Community 61 - "AuthenticationService"
Cohesion: 0.09
Nodes (6): IdentityRecord, SessionRecord, AuthenticationService, IdentityStore, InMemoryIdentityStore, test_store_failure_fails_closed()

### Community 62 - "orchestration/context.py"
Cohesion: 0.17
Nodes (7): AssembledContext, ContextLimitError, estimate_tokens(), PromptMessage, _render_evidence(), _safe_text(), _safe_value()

### Community 64 - "EgressMode"
Cohesion: 0.23
Nodes (20): ModelEgressDenied, EgressMode, provider(), route(), test_embedding_route_task_is_checked(), test_external_internal_requires_dpa(), test_external_internal_requires_residency(), test_external_provider_requires_retention_policy() (+12 more)

### Community 86 - "model/test_e2e_operational.py"
Cohesion: 0.11
Nodes (20): ModelGateway, ModelUnavailable, run_graph_query(), graph_labels(), policy(), run_graph_query(), ScriptedEmbedding, task() (+12 more)

### Community 87 - "pytest"
Cohesion: 0.12
Nodes (25): ModelPolicy, HybridRetrievalConfig, test_rrf_uses_each_branch_rank_and_deduplicates_within_a_branch(), test_mapping_loads_versioned_policy_without_credentials(), test_policy_rejects_credential_fields(), mapping(), test_primary_retries_cannot_exceed_two(), test_timeout_cannot_exceed_sixty_seconds() (+17 more)

### Community 91 - "lifecycle.py"
Cohesion: 0.06
Nodes (30): _acl_digest(), ApprovalBlocked, ApprovalRecord, _chunk_digest(), _chunk_state(), DerivedIndex, DerivedIndexFailure, DerivedIndexRecord (+22 more)

### Community 94 - "hybrid.py"
Cohesion: 0.19
Nodes (7): Citation, _BM25Record, _citation(), _FusedCandidate, HybridRetriever, InMemoryBM25Index, test_bm25_branch_filters_tenant_acl_active_and_policy_before_scoring()

### Community 96 - "test_dense_retrieval.py"
Cohesion: 0.27
Nodes (8): DocumentResource, PolicyEnforcementPoint, InMemoryDenseVectorIndex, _gateway(), _resource(), test_cross_tenant_candidates_are_not_exposed(), test_stale_policy_and_non_active_version_fail_closed(), _multi_retriever()

### Community 97 - "test_identity.py"
Cohesion: 0.20
Nodes (11): IdentityError, rate_limited(), make_service(), test_expired_session_is_rejected(), test_invalid_password_is_safe_auth_error(), test_mfa_is_required_for_privileged_role(), test_noncanonical_role_cannot_create_identity(), test_revoked_session_is_rejected() (+3 more)

### Community 98 - "rag_hybrid/test_security_adversarial.py"
Cohesion: 0.18
Nodes (14): AccessGrant, _catalog(), _FailingEmbeddingAdapter, _FailingRerankerAdapter, _gateway_with_failure(), test_acl_denied_candidates_are_absent_from_dense_and_bm25(), test_bm25_filters_unauthorized_high_frequency_candidates_before_scoring(), test_cross_tenant_candidates_are_absent_from_dense_and_bm25() (+6 more)

### Community 99 - "new_service"
Cohesion: 0.13
Nodes (24): ScanReport, new_service(), test_clean_review_one_allows_processing(), test_processing_inherits_parent_acl(), test_publishing_new_version_supersedes_previous_version(), test_rejected_scan_is_terminal_and_not_retrievable(), test_review_one_requires_clean_scan(), test_revoke_active_version_removes_retrieval() (+16 more)

### Community 102 - "ProviderPolicy"
Cohesion: 0.14
Nodes (12): RerankerRequest, route(), ProviderPolicy, DeterministicRerankerAdapter, _tokens(), _gateway(), test_reranker_request_rejects_blank_document_fields(), test_reranker_request_requires_documents() (+4 more)

### Community 103 - "IngestionService"
Cohesion: 0.17
Nodes (10): IngestionService, _active_document(), _principal(), _retriever(), test_dense_retrieval_returns_authorized_current_chunk_only(), test_explicit_deny_candidates_are_not_exposed(), test_forbidden_source_fetch_is_redacted_without_content_or_citation(), DenseRetrievalBehaviorTests (+2 more)

### Community 104 - "admin.py"
Cohesion: 0.11
Nodes (20): AccessGrantRequest, AccessRequest, AdminApiState, DepartmentRequest, _document_payload(), _document_resource(), _enforce_document(), _grant_payload() (+12 more)

### Community 113 - "active"
Cohesion: 0.16
Nodes (20): active(), staged(), test_acknowledged_index_is_still_not_active(), test_audit_sink_receives_lifecycle_events_without_content(), test_publication_failure_keeps_previous_active_version(), test_cross_tenant_version_lookup_is_denied(), test_derived_cleanup_failure_still_denies_retrieval(), test_derived_index_cannot_authorize_non_active_version() (+12 more)

### Community 114 - "env.py"
Cohesion: 0.19
Nodes (4): _database_url(), run_migrations_offline(), run_migrations_online(), DatabaseMigrationSmokeTests

### Community 115 - "make_manifest"
Cohesion: 0.16
Nodes (17): UploadManifest, make_manifest(), test_approval_expiry_blocks_publication(), test_doc_is_rejected(), test_internal_upload_requires_department(), test_non_private_source_is_rejected(), test_pdf_is_accepted(), test_sha256_must_be_a_digest() (+9 more)

### Community 116 - "observability/context.py"
Cohesion: 0.21
Nodes (5): CorrelationContext, _header(), _new_traceparent(), _valid_traceparent(), test_correlation_context_preserves_valid_headers_and_creates_child()

### Community 117 - "ndcg_at_k"
Cohesion: 0.49
Nodes (9): mean_reciprocal_rank(), ndcg_at_k(), recall_at_k(), source_key(), _span(), _spans(), test_rag_002_regression_metrics_on_tiny_in_memory_corpus(), metrics() (+1 more)

### Community 119 - "guardrails/__init__.py"
Cohesion: 0.15
Nodes (6): _luhn_valid(), redact_sensitive_data(), redact_card(), RedactionResult, ToolDecision, validate_tool_request()

### Community 121 - "normalize_user_input"
Cohesion: 0.17
Nodes (3): normalize_user_input(), GuardrailBehaviorTests, GuardrailSecurityAdversarialTests

### Community 122 - "DenseRetriever"
Cohesion: 0.20
Nodes (5): _citation(), _cosine(), DenseRetriever, _uuid(), _VectorRecord

### Community 123 - "InMemoryAuditSink"
Cohesion: 0.25
Nodes (8): InMemoryAuditSink, test_audit_sink_is_append_only_and_structured(), test_unavailable_sink_does_not_accept_an_event(), _add_identity(), _request(), test_sign_in_denial_emits_no_credentials_or_body(), test_sign_in_emits_correlated_success_event(), test_sign_in_fails_closed_when_audit_sink_is_unavailable()

### Community 124 - "validate_output"
Cohesion: 0.26
Nodes (8): _citation(), detect_prompt_injection(), GuardrailResult, _inspect_text(), _normalize_text(), _sensitive_terms(), _terms(), validate_output()

### Community 125 - "ingestion/_baseline.py"
Cohesion: 0.19
Nodes (5): Clock, graph_labels(), read(), task(), test_task_and_handoff_keep_ingestion_provider_neutral()

### Community 126 - "ingestion/test_behavior_component.py"
Cohesion: 0.15
Nodes (12): make_chunks(), test_child_acl_broadening_is_denied(), test_approval_expiry_blocks_processing(), test_empty_processing_input_is_rejected(), test_new_active_version_supersedes_previous_version(), test_publish_activates_authoritative_version_and_chunks(), test_review_one_and_processing_require_parent_acl(), test_review_one_requires_clean_scan() (+4 more)

### Community 127 - "ingestion/test_security_adversarial.py"
Cohesion: 0.16
Nodes (10): RuntimeFailureOnRemove, service_with_index(), test_cleanup_backend_error_is_wrapped_without_secret_leakage(), test_cross_tenant_document_lookup_is_denied(), test_cross_tenant_job_lookup_is_denied(), test_cross_tenant_version_lookup_is_denied(), test_derived_staging_state_cannot_authorize_retrieval(), test_legal_hold_blocks_permanent_delete() (+2 more)

### Community 131 - "validated"
Cohesion: 0.33
Nodes (9): IndexManifest, validated(), test_manifest_checksum_mismatch_blocks_staging(), test_manifest_count_mismatch_blocks_staging(), test_publication_requires_index_ack(), test_index_ack_is_a_publication_gate(), test_second_review_is_required_after_index_ack(), test_index_ack_is_required_before_publication() (+1 more)

### Community 132 - "quarantine"
Cohesion: 0.29
Nodes (9): quarantine(), test_failed_maintenance_can_be_recovered_after_cleanup(), test_non_retryable_failure_is_terminal(), test_only_one_maintenance_window_is_active(), test_retry_is_bounded_and_preserves_checksum(), test_retry_with_changed_checksum_is_denied(), test_upload_idempotency_conflict_is_rejected(), test_upload_idempotency_replays_same_job() (+1 more)

## Knowledge Gaps
- **1 isolated node(s):** `enterprise-agentic-rag-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 667 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **55 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AuthenticatedPrincipal` connect `admin.py` to `test_dense_retrieval.py`, `test_identity.py`, `rag_hybrid/test_security_adversarial.py`, `DenseRetriever`, `IngestionService`, `identity.py`, `AuthenticatedPrincipal`, `identity/models.py`, `authorization/test_behavior_component.py`, `ModelRoute`, `InMemoryPolicyStore`, `DocumentVersionMetadata`, `admin.py`, `authorization/test_contract_integration.py`, `PolicyEnforcementPoint`, `AuthenticationService`, `hybrid.py`, `test_authorization.py`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Are the 35 inferred relationships involving `IngestionService` (e.g. with `reset_state()` and `.test_assigned_department_allows_internal_employee()`) actually correct?**
  _`IngestionService` has 35 INFERRED edges - model-reasoned connections that need verification._
- **What connects `enterprise-agentic-rag-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `audit.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1225071225071225 - nodes in this community are weakly interconnected._
- **Why does `DataClassification` connect `test_models.py` to `EgressMode`, `test_dense_retrieval.py`, `rag_hybrid/test_security_adversarial.py`, `ProviderPolicy`, `IngestionService`, `admin.py`, `.__init__`, `make_manifest`, `ModelRoute`, `_make_retriever`, `model/test_e2e_operational.py`, `pytest`, `lifecycle.py`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `new_service()` (e.g. with `test_approval_expiry_blocks_processing()` and `test_empty_processing_input_is_rejected()`) actually correct?**
  _`new_service()` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Should `compose` be split into smaller, more focused modules?**
  _Cohesion score 0.06778476589797344 - nodes in this community are weakly interconnected._