# Graph Report - enterprise-agentic-rag-harness  (2026-11-10)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2366 nodes · 6435 edges · 119 communities (67 shown, 52 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 799 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9b3febff`
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
- model/test_security_adversarial.py
- vite-env.d.ts
- sync_graph.sh
- migrate.sh
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
- pytest
- IdentityContractTests
- .rerank
- InMemoryIdentityStore
- DatabaseBaselineSecurityTests
- IdentityBehaviorTests
- IdentitySecurityTests
- DatabaseBaselineContractTests
- os
- DerivedIndex
- observability/context.py
- ndcg_at_k
- identity/_baseline.py

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
- `AuthorizationSecurityAdversarialTests` --uses--> `AuthenticatedPrincipal`  [INFERRED]
  tests/qa/authorization/test_security_adversarial.py → backend/app/identity/models.py
- `test_unknown_classification_and_noncanonical_principal_are_denied()` --uses--> `AuthenticatedPrincipal`  [INFERRED]
  tests/security/test_authorization.py → backend/app/identity/models.py
- `test_embedding_gateway_contract_passes_request_route_and_timeout()` --uses--> `EmbeddingRequest`  [INFERRED]
  tests/qa/model/test_contract_integration.py → backend/app/models/adapters.py
- `ScriptedEmbedding` --uses--> `EmbeddingResult`  [INFERRED]
  tests/qa/model/_baseline.py → backend/app/models/adapters.py
- `test_reranker_gateway_contract_passes_request_route_and_timeout()` --uses--> `RerankerRequest`  [INFERRED]
  tests/qa/model/test_contract_integration.py → backend/app/models/adapters.py

## Import Cycles
- 2-file cycle: `backend/app/api/admin.py -> backend/app/api/identity.py -> backend/app/api/admin.py`

## Communities (119 total, 52 thin omitted)

### Community 0 - "audit.py"
Cohesion: 0.10
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
Cohesion: 0.10
Nodes (7): json_blocks(), require_all(), section(), BehaviorComponentTests, ContractIntegrationTests, E2EOperationalTests, SecurityAdversarialTests

### Community 6 - "read"
Cohesion: 0.06
Nodes (7): dashboard(), read(), task(), MonitoringBehaviorTests, MonitoringContractTests, MonitoringOperationalTests, MonitoringSecurityTests

### Community 7 - "read_frontend"
Cohesion: 0.07
Nodes (8): load_frontend_json(), read(), read_frontend(), run_frontend(), FrontendBehaviorComponentTests, FrontendContractIntegrationTests, FrontendE2EOperationalTests, FrontendSecurityAdversarialTests

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
Cohesion: 0.19
Nodes (10): _bearer_token(), current_identity(), _record(), _record_identity_error(), _request_context(), sign_in(), sign_out(), SignInRequest (+2 more)

### Community 14 - "AuthenticatedPrincipal"
Cohesion: 0.08
Nodes (14): Action, AuthorizationDenied, AuthorizationEvaluator, deny(), Classification, ConversationResource, Decision, Effect (+6 more)

### Community 15 - "store.py"
Cohesion: 0.21
Nodes (4): IdentityErrorPassthrough, now_utc(), hash_secret(), verify_secret()

### Community 16 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, networks (+12 more)

### Community 17 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, networks (+12 more)

### Community 18 - "authorization/test_behavior_component.py"
Cohesion: 0.32
Nodes (5): AnonymousPrincipal, AuthorizationBehaviorTests, document(), evaluator(), principal()

### Community 19 - "package.json"
Cohesion: 0.13
Nodes (19): devDependencies, eslint@9.17.0, jsdom@25.0.1, @types/node@22.10.5, @types/react@18.3.18, @types/react-dom@18.3.5, typescript@5.7.2, engines (+11 more)

### Community 20 - "ModelRoute"
Cohesion: 0.10
Nodes (13): EmbeddingAdapter, EmbeddingRequest, EmbeddingResult, RerankerAdapter, RerankerRequest, RerankerResult, ModelRoute, ProviderPolicy (+5 more)

### Community 21 - "InMemoryPolicyStore"
Cohesion: 0.27
Nodes (5): InMemoryPolicyStore, AuthorizationSecurityAdversarialTests, document(), evaluator(), principal()

### Community 22 - "ChunkMetadata"
Cohesion: 0.12
Nodes (11): ChunkMetadata, DocumentMetadata, _ImmutableModel, test_active_chunk_requires_acl_metadata(), test_chunk_accepts_source_provenance(), test_chunk_rejects_reversed_pages(), test_chunk_rejects_self_parent(), test_document_metadata_is_tenant_scoped() (+3 more)

### Community 23 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+10 more)

### Community 24 - "DocumentVersionMetadata"
Cohesion: 0.09
Nodes (8): DocumentVersionMetadata, test_document_version_identity_is_stable(), test_document_version_requires_private_source(), test_hashes_are_normalized(), test_version_contract_has_immutable_version_number(), test_version_contract_supports_publication_states(), make_document(), KnowledgeBehaviorTests

### Community 25 - "inherit_acl"
Cohesion: 0.16
Nodes (5): make_child(), make_parent(), make_version(), KnowledgeContractIntegrationTests, KnowledgeSecurityAdversarialTests

### Community 26 - "json"
Cohesion: 0.12
Nodes (4): dfs(), test_dashboard_has_api_and_security_panels(), test_dashboard_is_valid_json(), test_rag002_task_registry_keeps_retrieval_validation_and_scope()

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
Cohesion: 0.15
Nodes (43): ModelGateway, DataClassification, EgressMode, route(), FakeEmbedding, policy(), provider(), route() (+35 more)

### Community 31 - "test_authorization.py"
Cohesion: 0.40
Nodes (15): document(), evaluator(), principal(), test_acl_can_assign_employee_and_explicit_deny_wins_for_chairman(), test_anonymous_is_public_only(), test_chairman_is_read_only(), test_conversation_body_is_owner_only(), test_conversation_requires_conversation_resource() (+7 more)

### Community 32 - "_evaluation_harness.py"
Cohesion: 0.23
Nodes (10): answer_correctness(), citation_accuracy(), evaluate_case(), load_records(), no_answer_accuracy(), source_key(), unauthorized_retrieval_rate(), validate_dataset() (+2 more)

### Community 33 - "GraphifyOperationalTests"
Cohesion: 0.15
Nodes (5): graph(), graphify_bin(), run_graphify(), GraphifyOperationalTests, run_graph_query()

### Community 34 - "auth"
Cohesion: 0.05
Nodes (103): ScanReport, ScanVerdict, SourceSpan, add_user(), auth(), key(), prepare_review_two(), publish() (+95 more)

### Community 36 - "steps"
Cohesion: 0.15
Nodes (12): jobs, validate, name, on, pull_request, workflow_dispatch, run, uses (+4 more)

### Community 40 - "rules"
Cohesion: 0.17
Nodes (11): runbook, summary, groups, name, rules, severity, alert, annotations (+3 more)

### Community 41 - "RerankerRequest"
Cohesion: 0.15
Nodes (5): ModelProviderError, RankedDocument, FakeReranker, test_ranked_document_preserves_identifier_and_score(), ScriptedReranker

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

### Community 53 - "_make_retriever"
Cohesion: 0.09
Nodes (34): DeterministicRerankerAdapter, HybridRetrievalConfig, InMemoryBM25Index, reciprocal_rank_fusion(), _gateway(), _make_retriever(), test_hybrid_retrieval_composes_bm25_rrf_and_local_reranker(), test_rrf_uses_each_branch_rank_and_deduplicates_within_a_branch() (+26 more)

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
Cohesion: 0.11
Nodes (6): build_secure_context(), estimate_tokens(), RetrievedEvidence, PromptBehaviorComponentTests, PromptOperationalTests, PromptSecurityAdversarialTests

### Community 58 - "admin.py"
Cohesion: 0.15
Nodes (47): AccessGrantRequest, AccessRequest, activate_user(), AdminApiState, approve_document_version(), _body(), _bump_policy_epoch(), create_department() (+39 more)

### Community 60 - "dataclasses"
Cohesion: 0.11
Nodes (5): default_prompt_registry(), _freeze(), PromptDefinition, PromptRegistry, PromptRegistryTests

### Community 61 - "AuthenticationService"
Cohesion: 0.11
Nodes (3): SessionRecord, utc_z(), IdentityStore

### Community 62 - "orchestration/context.py"
Cohesion: 0.22
Nodes (6): AssembledContext, ContextLimitError, PromptMessage, _render_evidence(), _safe_text(), _safe_value()

### Community 64 - "model/test_security_adversarial.py"
Cohesion: 0.44
Nodes (10): ModelEgressDenied, provider(), gateway_for(), test_denied_primary_cannot_use_denied_fallback(), test_egress_denial_does_not_echo_input(), test_external_internal_without_dpa_is_denied(), test_external_internal_without_residency_is_denied(), test_external_training_provider_is_denied() (+2 more)

### Community 86 - "model/test_e2e_operational.py"
Cohesion: 0.17
Nodes (12): ModelUnavailable, graph_labels(), run_graph_query(), ScriptedEmbedding, task(), test_embedding_happy_path_completes_once(), test_fallback_is_attempted_once(), test_graph_contains_model_symbols() (+4 more)

### Community 87 - "pytest"
Cohesion: 0.13
Nodes (28): ModelPolicy, ModelTask, test_mapping_loads_versioned_policy_without_credentials(), test_model_task_values_are_stable(), test_policy_rejects_credential_fields(), mapping(), policy(), route() (+20 more)

### Community 91 - "lifecycle.py"
Cohesion: 0.05
Nodes (41): _acl_digest(), ApprovalBlocked, ApprovalRecord, _chunk_digest(), _chunk_state(), DerivedIndexFailure, DerivedIndexRecord, DocumentRecord (+33 more)

### Community 94 - "hybrid.py"
Cohesion: 0.20
Nodes (9): Citation, SourceFetchResult, _BM25Record, _citation(), _FusedCandidate, HybridEvidence, HybridRetrievalResult, HybridRetriever (+1 more)

### Community 96 - "test_dense_retrieval.py"
Cohesion: 0.13
Nodes (18): DocumentResource, PolicyEnforcementPoint, _citation(), _cosine(), DenseEvidence, DenseRetrievalResult, DenseRetriever, DeterministicEmbeddingAdapter (+10 more)

### Community 97 - "test_identity.py"
Cohesion: 0.17
Nodes (13): IdentityError, rate_limited(), AuthenticationService, make_service(), test_expired_session_is_rejected(), test_invalid_password_is_safe_auth_error(), test_mfa_is_required_for_privileged_role(), test_principal_rejects_extra_client_claims() (+5 more)

### Community 98 - "rag_hybrid/test_security_adversarial.py"
Cohesion: 0.15
Nodes (16): AccessGrant, test_source_fetch_rechecks_download_authorization_and_redacts_content(), _catalog(), _FailingEmbeddingAdapter, _FailingRerankerAdapter, _gateway_with_failure(), test_acl_denied_candidates_are_absent_from_dense_and_bm25(), test_bm25_filters_unauthorized_high_frequency_candidates_before_scoring() (+8 more)

### Community 99 - "pytest"
Cohesion: 0.05
Nodes (105): UploadManifest, active(), Clock, make_chunks(), make_manifest(), new_service(), quarantine(), staged() (+97 more)

### Community 103 - "InMemoryIdentityStore"
Cohesion: 0.12
Nodes (6): DepartmentRecord, IdentityRecord, normalize_roles(), Role, InMemoryIdentityStore, test_noncanonical_role_cannot_create_identity()

### Community 116 - "observability/context.py"
Cohesion: 0.38
Nodes (4): _header(), _new_traceparent(), _valid_traceparent(), test_correlation_context_preserves_valid_headers_and_creates_child()

### Community 117 - "ndcg_at_k"
Cohesion: 0.44
Nodes (9): mean_reciprocal_rank(), ndcg_at_k(), recall_at_k(), _span(), _spans(), test_rag_002_regression_metrics_on_tiny_in_memory_corpus(), metrics(), _span() (+1 more)

## Knowledge Gaps
- **1 isolated node(s):** `enterprise-agentic-rag-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 648 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **52 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `section()` connect `section` to `json`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 35 inferred relationships involving `IngestionService` (e.g. with `reset_state()` and `.test_assigned_department_allows_internal_employee()`) actually correct?**
  _`IngestionService` has 35 INFERRED edges - model-reasoned connections that need verification._
- **What connects `enterprise-agentic-rag-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `audit.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0975609756097561 - nodes in this community are weakly interconnected._
- **Why does `AuthenticatedPrincipal` connect `AuthenticatedPrincipal` to `test_dense_retrieval.py`, `test_identity.py`, `rag_hybrid/test_security_adversarial.py`, `InMemoryIdentityStore`, `authorization/test_contract_integration.py`, `identity.py`, `store.py`, `authorization/test_behavior_component.py`, `InMemoryPolicyStore`, `DocumentVersionMetadata`, `admin.py`, `lifecycle.py`, `PolicyEnforcementPoint`, `AuthenticationService`, `hybrid.py`, `test_authorization.py`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `new_service()` (e.g. with `test_approval_expiry_blocks_processing()` and `test_empty_processing_input_is_rejected()`) actually correct?**
  _`new_service()` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Should `compose` be split into smaller, more focused modules?**
  _Cohesion score 0.05478750640040963 - nodes in this community are weakly interconnected._