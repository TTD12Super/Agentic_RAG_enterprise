# Graph Report - enterprise-agentic-rag-harness  (2026-11-10)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2261 nodes · 6188 edges · 120 communities (75 shown, 45 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 781 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `252e5f34`
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
- AuthorizationEvaluator
- store.py
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
- RerankerRequest
- read
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
- ingestion/_baseline.py
- admin.py
- main.py
- AuthenticatedPrincipal
- AuthenticationService
- validated
- pytest
- vite-env.d.ts
- sync_graph.sh
- migrate.sh
- enterprise-agentic-rag-backend
- model/test_e2e_operational.py
- pytest
- lifecycle.py
- active
- hybrid.py
- make_manifest
- test_dense_retrieval.py
- test_identity.py
- rag_hybrid/test_security_adversarial.py
- new_service
- IdentityContractTests
- ModelGateway
- InMemoryIdentityStore
- backend_boot/_baseline.py
- FrontendE2EOperationalTests
- ingestion/test_behavior_component.py
- ingestion/_baseline.py
- DatabaseBaselineContractTests
- env.py
- AuditSecurityTests
- BackendBootstrapContractTests
- ndcg_at_k
- InfrastructureSecurityTests
- MonitoringBehaviorTests

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
- `test_fallback_is_attempted_once()` --uses--> `ModelUnavailable`  [INFERRED]
  tests/qa/model/test_e2e_operational.py → backend/app/integrations/model_gateway.py
- `test_runtime_provider_failure_does_not_leak_raw_payload()` --uses--> `ModelUnavailable`  [INFERRED]
  tests/qa/model/test_security_adversarial.py → backend/app/integrations/model_gateway.py
- `test_embedding_gateway_contract_passes_request_route_and_timeout()` --uses--> `EmbeddingRequest`  [INFERRED]
  tests/qa/model/test_contract_integration.py → backend/app/models/adapters.py
- `ScriptedEmbedding` --uses--> `EmbeddingResult`  [INFERRED]
  tests/qa/model/_baseline.py → backend/app/models/adapters.py
- `policy()` --uses--> `ModelRoute`  [INFERRED]
  tests/qa/model/_baseline.py → backend/app/models/policy.py

## Import Cycles
- 2-file cycle: `backend/app/api/admin.py -> backend/app/api/identity.py -> backend/app/api/admin.py`

## Communities (120 total, 45 thin omitted)

### Community 0 - "audit.py"
Cohesion: 0.05
Nodes (25): DerivedIndex, append_audit_event(), AuditEvent, AuditSink, AuditSinkUnavailable, InMemoryAuditSink, redact_metadata(), _safe_code() (+17 more)

### Community 1 - "compose"
Cohesion: 0.06
Nodes (11): compose(), compose_config_result(), database(), handoff(), read(), tasks(), testing(), DisposablePostgresBehaviorTests (+3 more)

### Community 2 - "read"
Cohesion: 0.07
Nodes (9): compose_config_result(), migration_files(), migration_text(), read(), task(), tasks(), DatabaseBaselineBehaviorTests, DatabaseBaselineOperationalTests (+1 more)

### Community 3 - "read"
Cohesion: 0.07
Nodes (7): compose_config(), read(), task(), tasks(), InfrastructureBehaviorTests, InfrastructureContractTests, InfrastructureOperationalTests

### Community 4 - "read"
Cohesion: 0.07
Nodes (6): read(), task(), tasks(), AuditBehaviorTests, AuditContractTests, AuditOperationalTests

### Community 5 - "section"
Cohesion: 0.10
Nodes (7): json_blocks(), require_all(), section(), BehaviorComponentTests, ContractIntegrationTests, E2EOperationalTests, SecurityAdversarialTests

### Community 6 - "read"
Cohesion: 0.09
Nodes (6): dashboard(), read(), task(), MonitoringContractTests, MonitoringOperationalTests, MonitoringSecurityTests

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

### Community 13 - "identity.py"
Cohesion: 0.27
Nodes (9): _bearer_token(), current_identity(), _record(), _record_identity_error(), _request_context(), sign_in(), sign_out(), SignInRequest (+1 more)

### Community 14 - "AuthorizationEvaluator"
Cohesion: 0.14
Nodes (5): AuthorizationEvaluator, _normalize_action(), PolicyStore, _resource_type(), _valid_epoch()

### Community 15 - "store.py"
Cohesion: 0.22
Nodes (3): IdentityErrorPassthrough, hash_secret(), verify_secret()

### Community 16 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, networks (+12 more)

### Community 17 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, networks (+12 more)

### Community 18 - "authorization/test_behavior_component.py"
Cohesion: 0.28
Nodes (6): AnonymousPrincipal, ConversationResource, AuthorizationBehaviorTests, document(), evaluator(), principal()

### Community 19 - "package.json"
Cohesion: 0.13
Nodes (19): devDependencies, eslint@9.17.0, jsdom@25.0.1, @types/node@22.10.5, @types/react@18.3.18, @types/react-dom@18.3.5, typescript@5.7.2, engines (+11 more)

### Community 20 - "ModelRoute"
Cohesion: 0.15
Nodes (7): EmbeddingAdapter, EmbeddingRequest, EmbeddingResult, RerankerAdapter, route(), ModelRoute, ProviderPolicy

### Community 21 - "InMemoryPolicyStore"
Cohesion: 0.30
Nodes (5): InMemoryPolicyStore, AuthorizationSecurityAdversarialTests, document(), evaluator(), principal()

### Community 22 - "ChunkMetadata"
Cohesion: 0.12
Nodes (11): ChunkMetadata, DocumentMetadata, _ImmutableModel, test_active_chunk_requires_acl_metadata(), test_chunk_accepts_source_provenance(), test_chunk_rejects_reversed_pages(), test_chunk_rejects_self_parent(), test_document_metadata_is_tenant_scoped() (+3 more)

### Community 23 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+10 more)

### Community 24 - "DocumentVersionMetadata"
Cohesion: 0.08
Nodes (9): DocumentVersionMetadata, test_document_version_identity_is_stable(), test_document_version_requires_private_source(), test_hashes_are_normalized(), test_version_contract_has_immutable_version_number(), test_version_contract_supports_publication_states(), make_document(), make_version() (+1 more)

### Community 25 - "inherit_acl"
Cohesion: 0.22
Nodes (5): to_qdrant_payload(), make_child(), make_parent(), KnowledgeContractIntegrationTests, KnowledgeSecurityAdversarialTests

### Community 27 - "authorization/test_contract_integration.py"
Cohesion: 0.26
Nodes (4): AuthorizationContractIntegrationTests, document(), evaluator(), principal()

### Community 28 - "PolicyEnforcementPoint"
Cohesion: 0.16
Nodes (8): AuthorizationDenied, deny(), PolicyDecision, PolicyEnforcementPoint, AuthorizationOperationalTests, document(), evaluator(), principal()

### Community 29 - "BackendBootstrapBehaviorTests"
Cohesion: 0.21
Nodes (4): calls(), function(), literal(), BackendBootstrapBehaviorTests

### Community 30 - "test_models.py"
Cohesion: 0.16
Nodes (38): DataClassification, EgressMode, ModelTask, FakeEmbedding, policy(), provider(), route(), test_approved_local_fallback_can_handle_internal_data() (+30 more)

### Community 31 - "test_authorization.py"
Cohesion: 0.40
Nodes (15): document(), evaluator(), principal(), test_acl_can_assign_employee_and_explicit_deny_wins_for_chairman(), test_anonymous_is_public_only(), test_chairman_is_read_only(), test_conversation_body_is_owner_only(), test_conversation_requires_conversation_resource() (+7 more)

### Community 32 - "_evaluation_harness.py"
Cohesion: 0.30
Nodes (7): load_records(), source_key(), unauthorized_retrieval_rate(), validate_dataset(), validate_record(), _validate_span(), test_rag002_task_registry_keeps_retrieval_validation_and_scope()

### Community 33 - "GraphifyOperationalTests"
Cohesion: 0.15
Nodes (5): graph(), graphify_bin(), run_graphify(), GraphifyOperationalTests, run_graph_query()

### Community 34 - "auth"
Cohesion: 0.06
Nodes (101): ScanReport, ScanVerdict, SourceSpan, add_user(), auth(), key(), prepare_review_two(), publish() (+93 more)

### Community 35 - "E2EOperationalTests"
Cohesion: 0.25
Nodes (6): answer_correctness(), citation_accuracy(), evaluate_case(), no_answer_accuracy(), recall_at_k(), E2EOperationalTests

### Community 36 - "steps"
Cohesion: 0.15
Nodes (12): jobs, validate, name, on, pull_request, workflow_dispatch, run, uses (+4 more)

### Community 40 - "rules"
Cohesion: 0.17
Nodes (11): runbook, summary, groups, name, rules, severity, alert, annotations (+3 more)

### Community 41 - "RerankerRequest"
Cohesion: 0.11
Nodes (14): ModelProviderError, RankedDocument, RerankerRequest, RerankerResult, FakeReranker, test_gateway_reranker_happy_path(), test_ranked_document_preserves_identifier_and_score(), test_reranker_request_rejects_blank_document_fields() (+6 more)

### Community 42 - "read"
Cohesion: 0.16
Nodes (4): compile_sources_without_writes(), read(), tree(), BackendBootstrapOperationalTests

### Community 43 - "read"
Cohesion: 0.06
Nodes (6): read(), task(), tasks(), IdentityBehaviorTests, IdentityOperationalTests, IdentitySecurityTests

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
Cohesion: 0.37
Nodes (13): inherit_acl(), make_child(), make_parent(), test_conflicting_child_acl_is_denied(), test_document_mismatch_is_denied(), test_matching_child_acl_is_preserved(), test_missing_child_acl_is_inherited(), test_qdrant_projection_does_not_claim_authority() (+5 more)

### Community 49 - "to_qdrant_payload"
Cohesion: 0.42
Nodes (9): make_child(), make_parent(), test_acl_inheritance_populates_child_reference(), test_parent_child_contract_keeps_same_scope(), test_qdrant_projection_contains_index_state(), test_qdrant_projection_contains_scope_keys(), test_qdrant_projection_does_not_store_chunk_text(), test_qdrant_projection_preserves_parent_reference() (+1 more)

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
Cohesion: 0.11
Nodes (28): DeterministicRerankerAdapter, HybridRetrievalConfig, _gateway(), _make_retriever(), test_hybrid_retrieval_composes_bm25_rrf_and_local_reranker(), test_bm25_length_normalization_prefers_shorter_equal_match(), test_bm25_repeated_query_term_has_frequency_weight(), test_bm25_tokenization_casefolds_and_splits_punctuation() (+20 more)

### Community 54 - "dependencies"
Cohesion: 0.29
Nodes (7): dependencies, react-dom@18.3.1, vite@6.3.5, @vitejs/plugin-react@4.6.0, react-dom, vite, @vitejs/plugin-react

### Community 55 - "vitest"
Cohesion: 0.25
Nodes (6): @testing-library/jest-dom@6.6.3, @testing-library/react@16.1.0, vitest@2.1.8, @testing-library/jest-dom, @testing-library/react, vitest

### Community 56 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, preview, test, test:watch, typecheck

### Community 57 - "ingestion/_baseline.py"
Cohesion: 0.16
Nodes (10): RuntimeFailureOnRemove, service_with_index(), test_cleanup_backend_error_is_wrapped_without_secret_leakage(), test_cross_tenant_document_lookup_is_denied(), test_cross_tenant_job_lookup_is_denied(), test_cross_tenant_version_lookup_is_denied(), test_derived_staging_state_cannot_authorize_retrieval(), test_legal_hold_blocks_permanent_delete() (+2 more)

### Community 58 - "admin.py"
Cohesion: 0.14
Nodes (48): AccessGrantRequest, AccessRequest, activate_user(), AdminApiState, approve_document_version(), _body(), _bump_policy_epoch(), create_department() (+40 more)

### Community 59 - "main.py"
Cohesion: 0.10
Nodes (4): get_settings(), Settings, healthz(), identity_error_handler()

### Community 60 - "AuthenticatedPrincipal"
Cohesion: 0.11
Nodes (11): Action, Classification, Decision, Effect, AuthenticatedPrincipal, _citation(), _cosine(), DenseEvidence (+3 more)

### Community 61 - "AuthenticationService"
Cohesion: 0.11
Nodes (5): IdentityRecord, utc_z(), AuthenticationService, now_utc(), IdentityStore

### Community 62 - "validated"
Cohesion: 0.26
Nodes (11): IndexManifest, validated(), test_clean_review_one_allows_processing(), test_processing_inherits_parent_acl(), test_manifest_checksum_mismatch_blocks_staging(), test_manifest_count_mismatch_blocks_staging(), test_publication_requires_index_ack(), test_index_ack_is_a_publication_gate() (+3 more)

### Community 64 - "pytest"
Cohesion: 0.19
Nodes (24): ModelEgressDenied, test_embedding_request_rejects_blank_text(), test_embedding_request_requires_texts(), policy(), provider(), route(), test_embedding_route_task_is_checked(), test_policy_version_is_required() (+16 more)

### Community 86 - "model/test_e2e_operational.py"
Cohesion: 0.18
Nodes (8): graph_labels(), run_graph_query(), ScriptedEmbedding, task(), test_graph_contains_model_symbols(), test_graphify_query_finds_model_gateway(), test_primary_retries_twice_then_succeeds(), test_task_registry_keeps_model_acceptance_and_validation()

### Community 87 - "pytest"
Cohesion: 0.24
Nodes (12): ModelPolicy, test_mapping_loads_versioned_policy_without_credentials(), test_policy_rejects_credential_fields(), mapping(), test_access_token_field_is_rejected(), test_exact_api_key_field_is_rejected(), test_mapping_rejects_empty_model_revision(), test_secret_key_field_is_rejected() (+4 more)

### Community 91 - "lifecycle.py"
Cohesion: 0.05
Nodes (40): _acl_digest(), ApprovalBlocked, ApprovalRecord, _chunk_digest(), _chunk_state(), DerivedIndexFailure, DerivedIndexRecord, DocumentRecord (+32 more)

### Community 93 - "active"
Cohesion: 0.15
Nodes (18): active(), quarantine(), test_publishing_new_version_supersedes_previous_version(), test_review_one_requires_clean_scan(), test_revoke_active_version_removes_retrieval(), test_second_review_and_publish_make_version_active(), test_soft_delete_isolates_all_versions(), test_upload_starts_quarantined_and_not_retrievable() (+10 more)

### Community 94 - "hybrid.py"
Cohesion: 0.12
Nodes (15): Citation, SourceFetchResult, _BM25Record, _citation(), _FusedCandidate, HybridEvidence, HybridRetrievalResult, HybridRetriever (+7 more)

### Community 95 - "make_manifest"
Cohesion: 0.15
Nodes (17): UploadManifest, make_manifest(), test_rejected_scan_is_terminal_and_not_retrievable(), test_doc_is_rejected(), test_internal_upload_requires_department(), test_non_private_source_is_rejected(), test_pdf_is_accepted(), test_sha256_must_be_a_digest() (+9 more)

### Community 96 - "test_dense_retrieval.py"
Cohesion: 0.25
Nodes (10): DocumentResource, DenseRetriever, DeterministicEmbeddingAdapter, InMemoryDenseVectorIndex, _gateway(), _resource(), test_cross_tenant_candidates_are_not_exposed(), test_stale_policy_and_non_active_version_fail_closed() (+2 more)

### Community 97 - "test_identity.py"
Cohesion: 0.20
Nodes (12): IdentityError, rate_limited(), make_service(), test_expired_session_is_rejected(), test_invalid_password_is_safe_auth_error(), test_mfa_is_required_for_privileged_role(), test_principal_rejects_extra_client_claims(), test_revoked_session_is_rejected() (+4 more)

### Community 98 - "rag_hybrid/test_security_adversarial.py"
Cohesion: 0.14
Nodes (16): AccessGrant, test_source_fetch_rechecks_download_authorization_and_redacts_content(), _catalog(), _FailingEmbeddingAdapter, _FailingRerankerAdapter, _gateway_with_failure(), test_acl_denied_candidates_are_absent_from_dense_and_bm25(), test_bm25_filters_unauthorized_high_frequency_candidates_before_scoring() (+8 more)

### Community 99 - "new_service"
Cohesion: 0.12
Nodes (32): new_service(), staged(), test_acknowledged_index_is_still_not_active(), test_approval_expiry_blocks_publication(), test_audit_sink_receives_lifecycle_events_without_content(), test_failed_maintenance_can_be_recovered_after_cleanup(), test_non_retryable_failure_is_terminal(), test_only_one_maintenance_window_is_active() (+24 more)

### Community 102 - "ModelGateway"
Cohesion: 0.21
Nodes (9): ModelGateway, ModelUnavailable, test_gateway_caps_primary_retries(), test_gateway_passes_bounded_timeout_to_adapter(), test_gateway_reports_missing_adapter(), test_gateway_reports_unavailable_without_fallback(), test_embedding_gateway_contract_passes_request_route_and_timeout(), test_embedding_happy_path_completes_once() (+1 more)

### Community 103 - "InMemoryIdentityStore"
Cohesion: 0.11
Nodes (5): DepartmentRecord, normalize_roles(), SessionRecord, InMemoryIdentityStore, test_noncanonical_role_cannot_create_identity()

### Community 104 - "backend_boot/_baseline.py"
Cohesion: 0.19
Nodes (4): assignment(), pyproject(), route_calls(), route_path()

### Community 106 - "ingestion/test_behavior_component.py"
Cohesion: 0.14
Nodes (13): make_chunks(), test_child_acl_broadening_is_denied(), test_approval_expiry_blocks_processing(), test_empty_processing_input_is_rejected(), test_malware_scan_is_terminal(), test_new_active_version_supersedes_previous_version(), test_publish_activates_authoritative_version_and_chunks(), test_review_one_and_processing_require_parent_acl() (+5 more)

### Community 107 - "ingestion/_baseline.py"
Cohesion: 0.19
Nodes (5): Clock, graph_labels(), read(), task(), test_task_and_handoff_keep_ingestion_provider_neutral()

### Community 114 - "env.py"
Cohesion: 0.19
Nodes (4): _database_url(), run_migrations_offline(), run_migrations_online(), DatabaseMigrationSmokeTests

### Community 116 - "BackendBootstrapContractTests"
Cohesion: 0.15
Nodes (3): backend_boot_task(), task_packet(), BackendBootstrapContractTests

### Community 117 - "ndcg_at_k"
Cohesion: 0.23
Nodes (9): _vectorize(), mean_reciprocal_rank(), ndcg_at_k(), _span(), _spans(), test_rag_002_regression_metrics_on_tiny_in_memory_corpus(), metrics(), _span() (+1 more)

## Knowledge Gaps
- **1 isolated node(s):** `enterprise-agentic-rag-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 617 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **45 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AuthenticatedPrincipal` connect `AuthenticatedPrincipal` to `test_dense_retrieval.py`, `test_identity.py`, `rag_hybrid/test_security_adversarial.py`, `authorization/test_contract_integration.py`, `identity.py`, `AuthorizationEvaluator`, `store.py`, `authorization/test_behavior_component.py`, `InMemoryPolicyStore`, `DocumentVersionMetadata`, `admin.py`, `lifecycle.py`, `PolicyEnforcementPoint`, `AuthenticationService`, `hybrid.py`, `test_authorization.py`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Are the 35 inferred relationships involving `IngestionService` (e.g. with `reset_state()` and `.test_assigned_department_allows_internal_employee()`) actually correct?**
  _`IngestionService` has 35 INFERRED edges - model-reasoned connections that need verification._
- **What connects `enterprise-agentic-rag-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `audit.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05341614906832298 - nodes in this community are weakly interconnected._
- **Why does `IngestionService` connect `lifecycle.py` to `audit.py`, `test_dense_retrieval.py`, `rag_hybrid/test_security_adversarial.py`, `new_service`, `_make_retriever`, `ingestion/_baseline.py`, `admin.py`, `AuthenticatedPrincipal`, `active`, `validated`, `make_manifest`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `new_service()` (e.g. with `test_approval_expiry_blocks_processing()` and `test_empty_processing_input_is_rejected()`) actually correct?**
  _`new_service()` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Should `compose` be split into smaller, more focused modules?**
  _Cohesion score 0.06110102843315184 - nodes in this community are weakly interconnected._