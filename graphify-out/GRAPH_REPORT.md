# Graph Report - enterprise-agentic-rag-harness  (2026-11-10)

## Corpus Check
- 169 files · ~153,514 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 68 file(s) not represented in the graph (top: (none) 53, .toml 9, .example 2)

## Summary
- 1878 nodes · 4364 edges · 98 communities (60 shown, 38 thin omitted)
- Extraction: 84% EXTRACTED · 16% INFERRED · 0% AMBIGUOUS · INFERRED: 695 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `dc632ed4`
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
- InMemoryIdentityStore
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
- InMemoryAuditSink
- E2EOperationalTests
- steps
- BehaviorComponentTests
- ContractIntegrationTests
- SecurityAdversarialTests
- rules
- subprocess
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
- AuthorizationDenied
- dependencies
- vitest
- scripts
- os
- KnowledgeContractIntegrationTests
- main.py
- load_validated_records
- service.py
- pytest
- EgressMode
- vite-env.d.ts
- sync_graph.sh
- migrate.sh
- enterprise-agentic-rag-backend
- model/test_e2e_operational.py
- pytest
- lifecycle.py
- test_identity.py
- ProviderPolicy
- ModelProviderError
- identity/models.py

## God Nodes (most connected - your core abstractions)
1. `new_service()` - 85 edges
2. `DataClassification` - 67 edges
3. `IngestionService` - 48 edges
4. `ModelGateway` - 46 edges
5. `ChunkMetadata` - 45 edges
6. `make_manifest()` - 43 edges
7. `section()` - 42 edges
8. `active()` - 36 edges
9. `AuthenticatedPrincipal` - 36 edges
10. `inherit_acl()` - 35 edges

## Surprising Connections (you probably didn't know these)
- `test_mvp_accepts_only_pdf_docx_and_xlsx()` --calls--> `make_manifest()`  [INFERRED]
  tests/qa/ingestion/test_contract_integration.py → backend/tests/_ingestion_fixtures.py
- `ScriptedEmbedding` --uses--> `ModelProviderError`  [INFERRED]
  tests/qa/model/_baseline.py → backend/app/integrations/model_gateway.py
- `ScriptedReranker` --uses--> `ModelProviderError`  [INFERRED]
  tests/qa/model/_baseline.py → backend/app/integrations/model_gateway.py
- `test_fallback_is_attempted_once()` --uses--> `ModelUnavailable`  [INFERRED]
  tests/qa/model/test_e2e_operational.py → backend/app/integrations/model_gateway.py
- `test_primary_attempts_are_bounded()` --uses--> `ModelUnavailable`  [INFERRED]
  tests/qa/model/test_e2e_operational.py → backend/app/integrations/model_gateway.py

## Import Cycles
- None detected.

## Communities (98 total, 38 thin omitted)

### Community 0 - "audit.py"
Cohesion: 0.09
Nodes (16): append_audit_event(), AuditEvent, AuditSink, AuditSinkUnavailable, InMemoryAuditSink, redact_metadata(), _safe_code(), _safe_identifier() (+8 more)

### Community 1 - "compose"
Cohesion: 0.05
Nodes (13): get_settings(), Settings, compose(), compose_config_result(), database(), handoff(), read(), tasks() (+5 more)

### Community 2 - "read"
Cohesion: 0.06
Nodes (7): migration_files(), migration_text(), read(), DatabaseBaselineBehaviorTests, DatabaseBaselineContractTests, DatabaseBaselineOperationalTests, DatabaseBaselineSecurityTests

### Community 3 - "read"
Cohesion: 0.06
Nodes (6): read(), task(), InfrastructureBehaviorTests, InfrastructureContractTests, InfrastructureOperationalTests, InfrastructureSecurityTests

### Community 4 - "read"
Cohesion: 0.05
Nodes (6): read(), task(), AuditBehaviorTests, AuditContractTests, AuditOperationalTests, AuditSecurityTests

### Community 5 - "section"
Cohesion: 0.10
Nodes (7): json_blocks(), require_all(), section(), BehaviorComponentTests, ContractIntegrationTests, E2EOperationalTests, SecurityAdversarialTests

### Community 6 - "read"
Cohesion: 0.06
Nodes (6): read(), task(), MonitoringBehaviorTests, MonitoringContractTests, MonitoringOperationalTests, MonitoringSecurityTests

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
Cohesion: 0.18
Nodes (10): _bearer_token(), current_identity(), _record(), _record_identity_error(), _request_context(), sign_in(), sign_out(), SignInRequest (+2 more)

### Community 14 - "AuthorizationEvaluator"
Cohesion: 0.12
Nodes (6): AccessGrant, AnonymousPrincipal, AuthorizationEvaluator, _normalize_action(), PolicyStore, AuthenticatedPrincipal

### Community 15 - "InMemoryIdentityStore"
Cohesion: 0.11
Nodes (6): IdentityRecord, normalize_roles(), hash_secret(), InMemoryIdentityStore, verify_secret(), test_noncanonical_role_cannot_create_identity()

### Community 16 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, networks (+12 more)

### Community 17 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, networks (+12 more)

### Community 18 - "authorization/test_behavior_component.py"
Cohesion: 0.38
Nodes (4): AuthorizationBehaviorTests, document(), evaluator(), principal()

### Community 19 - "package.json"
Cohesion: 0.13
Nodes (19): devDependencies, eslint@9.17.0, jsdom@25.0.1, @types/node@22.10.5, @types/react@18.3.18, @types/react-dom@18.3.5, typescript@5.7.2, engines (+11 more)

### Community 20 - "model/_baseline.py"
Cohesion: 0.14
Nodes (12): EmbeddingAdapter, EmbeddingRequest, EmbeddingResult, RerankerAdapter, RerankerRequest, RerankerResult, ModelRoute, test_embedding_request_rejects_blank_text() (+4 more)

### Community 21 - "InMemoryPolicyStore"
Cohesion: 0.30
Nodes (5): InMemoryPolicyStore, AuthorizationSecurityAdversarialTests, document(), evaluator(), principal()

### Community 22 - "ChunkMetadata"
Cohesion: 0.13
Nodes (12): ChunkMetadata, DocumentMetadata, _ImmutableModel, SourceSpan, test_active_chunk_requires_acl_metadata(), test_chunk_accepts_source_provenance(), test_chunk_rejects_reversed_pages(), test_chunk_rejects_self_parent() (+4 more)

### Community 23 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+10 more)

### Community 24 - "DocumentVersionMetadata"
Cohesion: 0.10
Nodes (8): DocumentVersionMetadata, test_document_version_identity_is_stable(), test_document_version_requires_private_source(), test_hashes_are_normalized(), test_version_contract_has_immutable_version_number(), test_version_contract_supports_publication_states(), make_document(), KnowledgeBehaviorTests

### Community 25 - "inherit_acl"
Cohesion: 0.29
Nodes (4): inherit_acl(), make_child(), make_parent(), KnowledgeSecurityAdversarialTests

### Community 26 - "json"
Cohesion: 0.10
Nodes (9): dfs(), test_dashboard_has_api_and_security_panels(), test_dashboard_is_valid_json(), tasks(), task(), tasks(), tasks(), tasks() (+1 more)

### Community 27 - "authorization/test_contract_integration.py"
Cohesion: 0.23
Nodes (5): DocumentResource, AuthorizationContractIntegrationTests, document(), evaluator(), principal()

### Community 28 - "PolicyEnforcementPoint"
Cohesion: 0.29
Nodes (5): PolicyEnforcementPoint, AuthorizationOperationalTests, document(), evaluator(), principal()

### Community 29 - "BackendBootstrapBehaviorTests"
Cohesion: 0.10
Nodes (9): assignment(), calls(), function(), literal(), pyproject(), route_calls(), route_path(), tree() (+1 more)

### Community 30 - "test_models.py"
Cohesion: 0.17
Nodes (41): ModelGateway, DataClassification, ModelTask, FakeEmbedding, policy(), provider(), route(), test_approved_local_fallback_can_handle_internal_data() (+33 more)

### Community 31 - "test_authorization.py"
Cohesion: 0.40
Nodes (15): document(), evaluator(), principal(), test_acl_can_assign_employee_and_explicit_deny_wins_for_chairman(), test_anonymous_is_public_only(), test_chairman_is_read_only(), test_conversation_body_is_owner_only(), test_conversation_requires_conversation_resource() (+7 more)

### Community 32 - "_evaluation_harness.py"
Cohesion: 0.31
Nodes (9): citation_accuracy(), evaluate_case(), mean_reciprocal_rank(), ndcg_at_k(), recall_at_k(), source_key(), validate_dataset(), validate_record() (+1 more)

### Community 33 - "GraphifyOperationalTests"
Cohesion: 0.14
Nodes (5): graph(), graphify_bin(), run_graphify(), GraphifyOperationalTests, run_graph_query()

### Community 34 - "InMemoryAuditSink"
Cohesion: 0.17
Nodes (7): test_healthz_is_local_liveness_only(), test_identity_requires_bearer_credentials(), _add_identity(), _request(), test_sign_in_denial_emits_no_credentials_or_body(), test_sign_in_emits_correlated_success_event(), test_sign_in_fails_closed_when_audit_sink_is_unavailable()

### Community 35 - "E2EOperationalTests"
Cohesion: 0.14
Nodes (4): answer_correctness(), no_answer_accuracy(), unauthorized_retrieval_rate(), E2EOperationalTests

### Community 36 - "steps"
Cohesion: 0.15
Nodes (12): jobs, validate, name, on, pull_request, workflow_dispatch, run, uses (+4 more)

### Community 40 - "rules"
Cohesion: 0.17
Nodes (11): runbook, summary, groups, name, rules, severity, alert, annotations (+3 more)

### Community 42 - "read"
Cohesion: 0.11
Nodes (6): backend_boot_task(), compile_sources_without_writes(), read(), task_packet(), BackendBootstrapContractTests, BackendBootstrapOperationalTests

### Community 43 - "read"
Cohesion: 0.05
Nodes (6): read(), task(), IdentityBehaviorTests, IdentityContractTests, IdentityOperationalTests, IdentitySecurityTests

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

### Community 53 - "AuthorizationDenied"
Cohesion: 0.15
Nodes (10): Action, AuthorizationDenied, deny(), Classification, ConversationResource, Decision, Effect, PolicyDecision (+2 more)

### Community 54 - "dependencies"
Cohesion: 0.29
Nodes (7): dependencies, react-dom@18.3.1, vite@6.3.5, @vitejs/plugin-react@4.6.0, react-dom, vite, @vitejs/plugin-react

### Community 55 - "vitest"
Cohesion: 0.25
Nodes (6): @testing-library/jest-dom@6.6.3, @testing-library/react@16.1.0, vitest@2.1.8, @testing-library/jest-dom, @testing-library/react, vitest

### Community 56 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, preview, test, test:watch, typecheck

### Community 61 - "service.py"
Cohesion: 0.13
Nodes (6): rate_limited(), SessionRecord, AuthenticationService, IdentityErrorPassthrough, now_utc(), IdentityStore

### Community 62 - "pytest"
Cohesion: 0.05
Nodes (106): ScanReport, UploadManifest, active(), Clock, make_chunks(), make_manifest(), new_service(), quarantine() (+98 more)

### Community 64 - "EgressMode"
Cohesion: 0.26
Nodes (17): ModelEgressDenied, EgressMode, provider(), test_external_internal_requires_dpa(), test_external_internal_requires_residency(), test_external_provider_requires_retention_policy(), test_external_unapproved_provider_is_denied(), test_provider_allowlist_is_required() (+9 more)

### Community 86 - "model/test_e2e_operational.py"
Cohesion: 0.14
Nodes (18): graph_labels(), policy(), route(), run_graph_query(), ScriptedEmbedding, task(), test_embedding_route_task_is_checked(), test_policy_version_is_required() (+10 more)

### Community 87 - "pytest"
Cohesion: 0.23
Nodes (13): ModelPolicy, test_mapping_loads_versioned_policy_without_credentials(), test_policy_rejects_credential_fields(), mapping(), test_access_token_field_is_rejected(), test_exact_api_key_field_is_rejected(), test_fallback_route_task_mismatch_is_rejected(), test_mapping_rejects_empty_model_revision() (+5 more)

### Community 91 - "lifecycle.py"
Cohesion: 0.07
Nodes (33): _acl_digest(), ApprovalBlocked, ApprovalRecord, _chunk_digest(), _chunk_state(), DerivedIndex, DerivedIndexFailure, DerivedIndexRecord (+25 more)

### Community 97 - "test_identity.py"
Cohesion: 0.19
Nodes (11): IdentityError, make_service(), test_expired_session_is_rejected(), test_invalid_password_is_safe_auth_error(), test_mfa_is_required_for_privileged_role(), test_principal_rejects_extra_client_claims(), test_revoked_session_is_rejected(), test_sign_in_normalizes_email_and_returns_server_principal() (+3 more)

### Community 99 - "ProviderPolicy"
Cohesion: 0.13
Nodes (6): route(), ProviderPolicy, ScriptedReranker, test_reranker_gateway_contract_passes_request_route_and_timeout(), test_reranker_result_keeps_selected_route(), test_reranker_happy_path_completes_once()

### Community 102 - "ModelProviderError"
Cohesion: 0.17
Nodes (5): ModelProviderError, ModelUnavailable, RankedDocument, FakeReranker, test_ranked_document_preserves_identifier_and_score()

## Knowledge Gaps
- **1 isolated node(s):** `enterprise-agentic-rag-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 572 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **38 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DataClassification` connect `test_models.py` to `EgressMode`, `ProviderPolicy`, `ModelProviderError`, `model/_baseline.py`, `model/test_e2e_operational.py`, `pytest`, `lifecycle.py`, `pytest`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `new_service()` (e.g. with `test_approval_expiry_blocks_processing()` and `test_empty_processing_input_is_rejected()`) actually correct?**
  _`new_service()` has 32 INFERRED edges - model-reasoned connections that need verification._
- **What connects `enterprise-agentic-rag-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `audit.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09291521486643438 - nodes in this community are weakly interconnected._
- **Why does `ChunkMetadata` connect `ChunkMetadata` to `unittest`, `test_knowledge_database.py`, `test_knowledge_security.py`, `to_qdrant_payload`, `DocumentVersionMetadata`, `inherit_acl`, `lifecycle.py`, `pytest`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Are the 47 inferred relationships involving `DataClassification` (e.g. with `ModelEgressDenied` and `ModelGateway`) actually correct?**
  _`DataClassification` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Should `compose` be split into smaller, more focused modules?**
  _Cohesion score 0.05478750640040963 - nodes in this community are weakly interconnected._