# Graph Report - enterprise-agentic-rag-harness  (2026-11-10)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2166 nodes · 5747 edges · 118 communities (68 shown, 50 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 773 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `63481434`
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
- AuthorizationEvaluator
- AuthenticatedPrincipal
- postgres
- postgres
- authorization/test_behavior_component.py
- package.json
- model/_baseline.py
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
- ProviderPolicy
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
- IngestionService
- dependencies
- vitest
- scripts
- ingestion/_baseline.py
- admin.py
- main.py
- load_validated_records
- AuthenticationService
- staged
- pytest
- vite-env.d.ts
- sync_graph.sh
- migrate.sh
- enterprise-agentic-rag-backend
- model/test_e2e_operational.py
- pytest
- lifecycle.py
- new_service
- CorrelationContext
- make_manifest
- test_dense_retrieval.py
- test_identity.py
- IdentityBehaviorTests
- active
- IdentityContractTests
- IdentitySecurityTests
- InMemoryIdentityStore
- identity/_baseline.py
- FrontendE2EOperationalTests
- ingestion/test_behavior_component.py
- KnowledgeOperationalTests
- DatabaseBaselineContractTests
- DatabaseBaselineSecurityTests
- test_ingestion_behavior.py
- ProviderPolicy
- ndcg_at_k

## God Nodes (most connected - your core abstractions)
1. `IngestionService` - 93 edges
2. `auth()` - 87 edges
3. `request()` - 86 edges
4. `new_service()` - 85 edges
5. `DataClassification` - 74 edges
6. `key()` - 62 edges
7. `_active_document()` - 58 edges
8. `ChunkMetadata` - 57 edges
9. `ModelGateway` - 55 edges
10. `_retriever()` - 52 edges

## Surprising Connections (you probably didn't know these)
- `policy()` --uses--> `ProviderPolicy`  [INFERRED]
  tests/qa/model/_baseline.py → backend/app/models/policy.py
- `route()` --uses--> `ProviderPolicy`  [INFERRED]
  tests/qa/model/_baseline.py → backend/app/models/policy.py
- `AuthorizationSecurityAdversarialTests` --uses--> `AuthenticatedPrincipal`  [INFERRED]
  tests/qa/authorization/test_security_adversarial.py → backend/app/identity/models.py
- `test_unknown_classification_and_noncanonical_principal_are_denied()` --uses--> `AuthenticatedPrincipal`  [INFERRED]
  tests/security/test_authorization.py → backend/app/identity/models.py
- `ScriptedEmbedding` --uses--> `ModelProviderError`  [INFERRED]
  tests/qa/model/_baseline.py → backend/app/integrations/model_gateway.py

## Import Cycles
- 2-file cycle: `backend/app/api/admin.py -> backend/app/api/identity.py -> backend/app/api/admin.py`

## Communities (118 total, 50 thin omitted)

### Community 0 - "audit.py"
Cohesion: 0.11
Nodes (17): append_audit_event(), AuditEvent, AuditSink, AuditSinkUnavailable, InMemoryAuditSink, redact_metadata(), _safe_code(), _safe_identifier() (+9 more)

### Community 1 - "compose"
Cohesion: 0.05
Nodes (13): get_settings(), Settings, compose(), compose_config_result(), database(), handoff(), read(), tasks() (+5 more)

### Community 2 - "read"
Cohesion: 0.10
Nodes (8): compose_config_result(), migration_files(), migration_text(), read(), task(), tasks(), DatabaseBaselineBehaviorTests, DatabaseBaselineOperationalTests

### Community 3 - "read"
Cohesion: 0.05
Nodes (8): compose_config(), read(), task(), tasks(), InfrastructureBehaviorTests, InfrastructureContractTests, InfrastructureOperationalTests, InfrastructureSecurityTests

### Community 4 - "read"
Cohesion: 0.05
Nodes (7): read(), task(), tasks(), AuditBehaviorTests, AuditContractTests, AuditOperationalTests, AuditSecurityTests

### Community 5 - "section"
Cohesion: 0.09
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

### Community 11 - "env.py"
Cohesion: 0.09
Nodes (3): _database_url(), run_migrations_offline(), run_migrations_online()

### Community 13 - "identity.py"
Cohesion: 0.21
Nodes (11): _bearer_token(), current_identity(), _record(), _record_identity_error(), _request_context(), sign_in(), sign_out(), SignInRequest (+3 more)

### Community 14 - "AuthorizationEvaluator"
Cohesion: 0.11
Nodes (10): AccessGrant, Action, AuthorizationEvaluator, Classification, Decision, Effect, _normalize_action(), PolicyStore (+2 more)

### Community 15 - "AuthenticatedPrincipal"
Cohesion: 0.15
Nodes (10): hash_secret(), verify_secret(), _acl_digest(), _chunk_digest(), IndexPublicationStatus, JobStage, JobState, MaintenanceStatus (+2 more)

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

### Community 20 - "model/_baseline.py"
Cohesion: 0.10
Nodes (13): ModelProviderError, ModelUnavailable, EmbeddingAdapter, EmbeddingRequest, EmbeddingResult, RankedDocument, RerankerAdapter, RerankerResult (+5 more)

### Community 21 - "InMemoryPolicyStore"
Cohesion: 0.41
Nodes (4): AuthorizationSecurityAdversarialTests, document(), evaluator(), principal()

### Community 22 - "ChunkMetadata"
Cohesion: 0.11
Nodes (11): ChunkMetadata, DocumentMetadata, _ImmutableModel, test_active_chunk_requires_acl_metadata(), test_chunk_accepts_source_provenance(), test_chunk_rejects_reversed_pages(), test_chunk_rejects_self_parent(), test_document_metadata_is_tenant_scoped() (+3 more)

### Community 23 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+10 more)

### Community 24 - "DocumentVersionMetadata"
Cohesion: 0.09
Nodes (9): DocumentVersionMetadata, test_document_version_identity_is_stable(), test_document_version_requires_private_source(), test_hashes_are_normalized(), test_version_contract_has_immutable_version_number(), test_version_contract_supports_publication_states(), make_document(), make_version() (+1 more)

### Community 25 - "inherit_acl"
Cohesion: 0.22
Nodes (4): make_child(), make_parent(), KnowledgeContractIntegrationTests, KnowledgeSecurityAdversarialTests

### Community 26 - "json"
Cohesion: 0.13
Nodes (3): dfs(), test_dashboard_has_api_and_security_panels(), test_dashboard_is_valid_json()

### Community 27 - "authorization/test_contract_integration.py"
Cohesion: 0.27
Nodes (4): AuthorizationContractIntegrationTests, document(), evaluator(), principal()

### Community 28 - "PolicyEnforcementPoint"
Cohesion: 0.15
Nodes (8): AuthorizationDenied, deny(), PolicyDecision, PolicyEnforcementPoint, AuthorizationOperationalTests, document(), evaluator(), principal()

### Community 29 - "BackendBootstrapBehaviorTests"
Cohesion: 0.16
Nodes (5): assignment(), calls(), function(), literal(), BackendBootstrapBehaviorTests

### Community 30 - "test_models.py"
Cohesion: 0.16
Nodes (43): ModelGateway, DataClassification, EgressMode, ModelTask, FakeEmbedding, policy(), provider(), route() (+35 more)

### Community 31 - "test_authorization.py"
Cohesion: 0.27
Nodes (16): InMemoryPolicyStore, document(), evaluator(), principal(), test_acl_can_assign_employee_and_explicit_deny_wins_for_chairman(), test_anonymous_is_public_only(), test_chairman_is_read_only(), test_conversation_body_is_owner_only() (+8 more)

### Community 32 - "_evaluation_harness.py"
Cohesion: 0.34
Nodes (11): answer_correctness(), citation_accuracy(), evaluate_case(), load_records(), mean_reciprocal_rank(), recall_at_k(), source_key(), unauthorized_retrieval_rate() (+3 more)

### Community 33 - "GraphifyOperationalTests"
Cohesion: 0.10
Nodes (6): DatabaseMigrationSmokeTests, graph(), graphify_bin(), run_graphify(), GraphifyOperationalTests, run_graph_query()

### Community 34 - "auth"
Cohesion: 0.05
Nodes (102): ScanVerdict, SourceSpan, add_user(), auth(), key(), prepare_review_two(), publish(), request() (+94 more)

### Community 36 - "steps"
Cohesion: 0.15
Nodes (12): jobs, validate, name, on, pull_request, workflow_dispatch, run, uses (+4 more)

### Community 40 - "rules"
Cohesion: 0.17
Nodes (11): runbook, summary, groups, name, rules, severity, alert, annotations (+3 more)

### Community 41 - "ProviderPolicy"
Cohesion: 0.20
Nodes (6): RerankerRequest, test_reranker_request_rejects_blank_document_fields(), test_reranker_request_requires_documents(), test_reranker_request_requires_query(), test_reranker_gateway_contract_passes_request_route_and_timeout(), test_reranker_happy_path_completes_once()

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
Cohesion: 0.37
Nodes (13): inherit_acl(), make_child(), make_parent(), test_conflicting_child_acl_is_denied(), test_document_mismatch_is_denied(), test_matching_child_acl_is_preserved(), test_missing_child_acl_is_inherited(), test_qdrant_projection_does_not_claim_authority() (+5 more)

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

### Community 53 - "IngestionService"
Cohesion: 0.13
Nodes (11): IngestionService, _active_document(), _principal(), _retriever(), test_dense_retrieval_returns_authorized_current_chunk_only(), test_explicit_deny_candidates_are_not_exposed(), test_forbidden_source_fetch_is_redacted_without_content_or_citation(), DenseRetrievalBehaviorTests (+3 more)

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
Cohesion: 0.10
Nodes (15): Clock, graph_labels(), read(), RuntimeFailureOnRemove, service_with_index(), task(), test_task_and_handoff_keep_ingestion_provider_neutral(), test_cleanup_backend_error_is_wrapped_without_secret_leakage() (+7 more)

### Community 58 - "admin.py"
Cohesion: 0.15
Nodes (47): AccessGrantRequest, AccessRequest, activate_user(), AdminApiState, approve_document_version(), _body(), _bump_policy_epoch(), create_department() (+39 more)

### Community 61 - "AuthenticationService"
Cohesion: 0.10
Nodes (7): rate_limited(), IdentityRecord, SessionRecord, AuthenticationService, IdentityErrorPassthrough, now_utc(), IdentityStore

### Community 62 - "staged"
Cohesion: 0.14
Nodes (20): IndexManifest, UploadManifest, staged(), validated(), test_approval_expiry_blocks_publication(), test_doc_is_rejected(), test_internal_upload_requires_department(), test_manifest_checksum_mismatch_blocks_staging() (+12 more)

### Community 64 - "pytest"
Cohesion: 0.19
Nodes (25): ModelEgressDenied, policy(), provider(), route(), test_embedding_route_task_is_checked(), test_external_internal_requires_dpa(), test_external_internal_requires_residency(), test_external_provider_requires_retention_policy() (+17 more)

### Community 86 - "model/test_e2e_operational.py"
Cohesion: 0.17
Nodes (10): graph_labels(), run_graph_query(), ScriptedEmbedding, task(), test_embedding_result_keeps_selected_route(), test_graph_contains_model_symbols(), test_graphify_query_finds_model_gateway(), test_primary_attempts_are_bounded() (+2 more)

### Community 87 - "pytest"
Cohesion: 0.23
Nodes (13): ModelPolicy, test_mapping_loads_versioned_policy_without_credentials(), test_policy_rejects_credential_fields(), mapping(), test_access_token_field_is_rejected(), test_exact_api_key_field_is_rejected(), test_fallback_route_task_mismatch_is_rejected(), test_mapping_rejects_empty_model_revision() (+5 more)

### Community 91 - "lifecycle.py"
Cohesion: 0.08
Nodes (21): ApprovalBlocked, ApprovalRecord, _chunk_state(), DerivedIndexFailure, DerivedIndexRecord, DocumentRecord, IdempotencyConflict, IndexPublication (+13 more)

### Community 93 - "new_service"
Cohesion: 0.17
Nodes (22): new_service(), quarantine(), test_audit_sink_receives_lifecycle_events_without_content(), test_failed_maintenance_can_be_recovered_after_cleanup(), test_non_retryable_failure_is_terminal(), test_only_one_maintenance_window_is_active(), test_publication_failure_keeps_previous_active_version(), test_retry_is_bounded_and_preserves_checksum() (+14 more)

### Community 94 - "CorrelationContext"
Cohesion: 0.11
Nodes (6): DerivedIndex, CorrelationContext, _header(), _new_traceparent(), _valid_traceparent(), test_correlation_context_preserves_valid_headers_and_creates_child()

### Community 95 - "make_manifest"
Cohesion: 0.19
Nodes (14): ScanReport, make_manifest(), test_rejected_scan_is_terminal_and_not_retrievable(), test_rejected_version_cannot_be_retrieved(), test_scan_rejection_is_not_retryable(), test_malware_scan_is_terminal(), test_failed_new_publication_preserves_previous_active_version(), test_job_contract_keeps_attempt_and_tenant_scope() (+6 more)

### Community 96 - "test_dense_retrieval.py"
Cohesion: 0.14
Nodes (17): DocumentResource, Citation, _citation(), _cosine(), DenseEvidence, DenseRetrievalResult, DenseRetriever, DeterministicEmbeddingAdapter (+9 more)

### Community 97 - "test_identity.py"
Cohesion: 0.27
Nodes (10): IdentityError, make_service(), test_expired_session_is_rejected(), test_invalid_password_is_safe_auth_error(), test_mfa_is_required_for_privileged_role(), test_revoked_session_is_rejected(), test_sign_in_normalizes_email_and_returns_server_principal(), test_store_failure_fails_closed() (+2 more)

### Community 99 - "active"
Cohesion: 0.18
Nodes (15): active(), test_cross_tenant_version_lookup_is_denied(), test_derived_cleanup_failure_still_denies_retrieval(), test_derived_index_cannot_authorize_non_active_version(), test_legal_hold_blocks_permanent_delete(), test_revoked_version_cannot_be_retrieved_from_derived_state(), test_root_chunk_without_acl_fails_closed(), test_staging_index_cannot_be_retrieved() (+7 more)

### Community 103 - "InMemoryIdentityStore"
Cohesion: 0.09
Nodes (6): DepartmentRecord, normalize_roles(), Role, utc_z(), InMemoryIdentityStore, test_noncanonical_role_cannot_create_identity()

### Community 106 - "ingestion/test_behavior_component.py"
Cohesion: 0.15
Nodes (12): make_chunks(), test_child_acl_broadening_is_denied(), test_approval_expiry_blocks_processing(), test_empty_processing_input_is_rejected(), test_new_active_version_supersedes_previous_version(), test_publish_activates_authoritative_version_and_chunks(), test_review_one_and_processing_require_parent_acl(), test_review_one_requires_clean_scan() (+4 more)

### Community 107 - "KnowledgeOperationalTests"
Cohesion: 0.22
Nodes (3): read(), task(), KnowledgeOperationalTests

### Community 115 - "test_ingestion_behavior.py"
Cohesion: 0.20
Nodes (9): test_acknowledged_index_is_still_not_active(), test_clean_review_one_allows_processing(), test_processing_inherits_parent_acl(), test_publishing_new_version_supersedes_previous_version(), test_review_one_requires_clean_scan(), test_revoke_active_version_removes_retrieval(), test_second_review_and_publish_make_version_active(), test_soft_delete_isolates_all_versions() (+1 more)

## Knowledge Gaps
- **1 isolated node(s):** `enterprise-agentic-rag-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 604 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **50 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ChunkMetadata` connect `ChunkMetadata` to `test_dense_retrieval.py`, `auth`, `active`, `ingestion/test_behavior_component.py`, `AuthenticatedPrincipal`, `test_knowledge_security.py`, `to_qdrant_payload`, `test_knowledge_database.py`, `IngestionService`, `inherit_acl`, `DocumentVersionMetadata`, `ingestion/_baseline.py`, `lifecycle.py`, `staged`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Are the 35 inferred relationships involving `IngestionService` (e.g. with `reset_state()` and `.test_assigned_department_allows_internal_employee()`) actually correct?**
  _`IngestionService` has 35 INFERRED edges - model-reasoned connections that need verification._
- **What connects `enterprise-agentic-rag-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `audit.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10512820512820513 - nodes in this community are weakly interconnected._
- **Why does `AuthenticatedPrincipal` connect `identity.py` to `test_dense_retrieval.py`, `test_identity.py`, `InMemoryIdentityStore`, `AuthorizationEvaluator`, `authorization/test_behavior_component.py`, `IngestionService`, `InMemoryPolicyStore`, `DocumentVersionMetadata`, `admin.py`, `authorization/test_contract_integration.py`, `PolicyEnforcementPoint`, `AuthenticationService`, `test_authorization.py`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `new_service()` (e.g. with `test_approval_expiry_blocks_processing()` and `test_empty_processing_input_is_rejected()`) actually correct?**
  _`new_service()` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Should `compose` be split into smaller, more focused modules?**
  _Cohesion score 0.05478750640040963 - nodes in this community are weakly interconnected._