# Graph Report - enterprise-agentic-rag-harness  (2026-11-10)

## Corpus Check
- 155 files · ~145,610 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 68 file(s) not represented in the graph (top: (none) 53, .toml 9, .example 2)

## Summary
- 1646 nodes · 3499 edges · 104 communities (58 shown, 46 thin omitted)
- Extraction: 83% EXTRACTED · 17% INFERRED · 0% AMBIGUOUS · INFERRED: 609 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e615ce87`
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
- context.py
- DataClassification
- vite-env.d.ts
- sync_graph.sh
- migrate.sh
- enterprise-agentic-rag-backend
- model/test_e2e_operational.py
- pytest
- pathlib
- IdentityBehaviorTests
- IdentityContractTests
- IdentitySecurityTests
- BackendBootstrapContractTests
- backend_boot/_baseline.py
- test_identity.py
- identity/_baseline.py
- ProviderPolicy
- route_calls
- ModelProviderError
- identity/models.py

## God Nodes (most connected - your core abstractions)
1. `DataClassification` - 63 edges
2. `ModelGateway` - 46 edges
3. `section()` - 42 edges
4. `AuthenticatedPrincipal` - 36 edges
5. `compose()` - 35 edges
6. `require_all()` - 35 edges
7. `EgressMode` - 31 edges
8. `ChunkMetadata` - 30 edges
9. `read()` - 30 edges
10. `inherit_acl()` - 29 edges

## Surprising Connections (you probably didn't know these)
- `ScriptedEmbedding` --uses--> `ModelProviderError`  [INFERRED]
  tests/qa/model/_baseline.py → backend/app/integrations/model_gateway.py
- `test_runtime_provider_failure_does_not_leak_raw_payload()` --uses--> `ModelUnavailable`  [INFERRED]
  tests/qa/model/test_security_adversarial.py → backend/app/integrations/model_gateway.py
- `KnowledgeBehaviorTests` --uses--> `SourceSpan`  [INFERRED]
  tests/qa/knowledge/test_behavior_component.py → backend/app/knowledge/models.py
- `KnowledgeSecurityAdversarialTests` --uses--> `ChunkMetadata`  [INFERRED]
  tests/qa/knowledge/test_security_adversarial.py → backend/app/knowledge/models.py
- `test_embedding_gateway_contract_passes_request_route_and_timeout()` --uses--> `EmbeddingRequest`  [INFERRED]
  tests/qa/model/test_contract_integration.py → backend/app/models/adapters.py

## Import Cycles
- None detected.

## Communities (104 total, 46 thin omitted)

### Community 0 - "audit.py"
Cohesion: 0.12
Nodes (12): append_audit_event(), AuditEvent, AuditSink, AuditSinkUnavailable, InMemoryAuditSink, redact_metadata(), _safe_code(), _safe_identifier() (+4 more)

### Community 1 - "compose"
Cohesion: 0.05
Nodes (13): get_settings(), Settings, compose(), compose_config_result(), database(), handoff(), read(), tasks() (+5 more)

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

### Community 13 - "identity.py"
Cohesion: 0.18
Nodes (10): _bearer_token(), current_identity(), _record(), _record_identity_error(), _request_context(), sign_in(), sign_out(), SignInRequest (+2 more)

### Community 14 - "AuthorizationEvaluator"
Cohesion: 0.11
Nodes (9): AccessGrant, AnonymousPrincipal, AuthorizationEvaluator, DocumentResource, _normalize_action(), PolicyStore, _resource_type(), _valid_epoch() (+1 more)

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
Cohesion: 0.32
Nodes (5): ConversationResource, AuthorizationBehaviorTests, document(), evaluator(), principal()

### Community 19 - "package.json"
Cohesion: 0.13
Nodes (19): devDependencies, eslint@9.17.0, jsdom@25.0.1, @types/node@22.10.5, @types/react@18.3.18, @types/react-dom@18.3.5, typescript@5.7.2, engines (+11 more)

### Community 20 - "model/_baseline.py"
Cohesion: 0.15
Nodes (12): EmbeddingAdapter, EmbeddingRequest, EmbeddingResult, RerankerAdapter, RerankerRequest, RerankerResult, ModelRoute, test_embedding_request_rejects_blank_text() (+4 more)

### Community 21 - "InMemoryPolicyStore"
Cohesion: 0.30
Nodes (5): InMemoryPolicyStore, AuthorizationSecurityAdversarialTests, document(), evaluator(), principal()

### Community 22 - "ChunkMetadata"
Cohesion: 0.12
Nodes (12): ChunkMetadata, DocumentMetadata, _ImmutableModel, SourceSpan, test_active_chunk_requires_acl_metadata(), test_chunk_accepts_source_provenance(), test_chunk_rejects_reversed_pages(), test_chunk_rejects_self_parent() (+4 more)

### Community 23 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+10 more)

### Community 24 - "DocumentVersionMetadata"
Cohesion: 0.11
Nodes (8): DocumentVersionMetadata, test_document_version_identity_is_stable(), test_document_version_requires_private_source(), test_hashes_are_normalized(), test_version_contract_has_immutable_version_number(), test_version_contract_supports_publication_states(), make_document(), KnowledgeBehaviorTests

### Community 25 - "inherit_acl"
Cohesion: 0.29
Nodes (4): inherit_acl(), make_child(), make_parent(), KnowledgeSecurityAdversarialTests

### Community 26 - "json"
Cohesion: 0.18
Nodes (3): test_dashboard_has_api_and_security_panels(), test_dashboard_is_valid_json(), graph()

### Community 27 - "authorization/test_contract_integration.py"
Cohesion: 0.27
Nodes (4): AuthorizationContractIntegrationTests, document(), evaluator(), principal()

### Community 28 - "PolicyEnforcementPoint"
Cohesion: 0.24
Nodes (5): PolicyEnforcementPoint, AuthorizationOperationalTests, document(), evaluator(), principal()

### Community 29 - "BackendBootstrapBehaviorTests"
Cohesion: 0.15
Nodes (5): assignment(), calls(), function(), literal(), BackendBootstrapBehaviorTests

### Community 30 - "test_models.py"
Cohesion: 0.14
Nodes (41): ModelGateway, DataClassification, route(), FakeEmbedding, policy(), provider(), route(), test_approved_local_fallback_can_handle_internal_data() (+33 more)

### Community 31 - "test_authorization.py"
Cohesion: 0.40
Nodes (15): document(), evaluator(), principal(), test_acl_can_assign_employee_and_explicit_deny_wins_for_chairman(), test_anonymous_is_public_only(), test_chairman_is_read_only(), test_conversation_body_is_owner_only(), test_conversation_requires_conversation_resource() (+7 more)

### Community 32 - "_evaluation_harness.py"
Cohesion: 0.31
Nodes (9): citation_accuracy(), evaluate_case(), mean_reciprocal_rank(), ndcg_at_k(), recall_at_k(), source_key(), validate_dataset(), validate_record() (+1 more)

### Community 33 - "GraphifyOperationalTests"
Cohesion: 0.14
Nodes (5): graphify_bin(), run_graphify(), GraphifyOperationalTests, run_graph_query(), test_graphify_query_finds_model_gateway()

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
Cohesion: 0.18
Nodes (4): compile_sources_without_writes(), read(), tree(), BackendBootstrapOperationalTests

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
Cohesion: 0.17
Nodes (7): Action, AuthorizationDenied, deny(), Classification, Decision, Effect, PolicyDecision

### Community 54 - "dependencies"
Cohesion: 0.29
Nodes (7): dependencies, react-dom@18.3.1, vite@6.3.5, @vitejs/plugin-react@4.6.0, react-dom, vite, @vitejs/plugin-react

### Community 55 - "vitest"
Cohesion: 0.25
Nodes (6): @testing-library/jest-dom@6.6.3, @testing-library/react@16.1.0, vitest@2.1.8, @testing-library/jest-dom, @testing-library/react, vitest

### Community 56 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, preview, test, test:watch, typecheck

### Community 57 - "os"
Cohesion: 0.16
Nodes (4): _database_url(), run_migrations_offline(), run_migrations_online(), DatabaseMigrationSmokeTests

### Community 61 - "service.py"
Cohesion: 0.13
Nodes (6): rate_limited(), SessionRecord, AuthenticationService, IdentityErrorPassthrough, now_utc(), IdentityStore

### Community 62 - "context.py"
Cohesion: 0.31
Nodes (4): _header(), _new_traceparent(), _valid_traceparent(), test_correlation_context_preserves_valid_headers_and_creates_child()

### Community 64 - "DataClassification"
Cohesion: 0.19
Nodes (21): ModelEgressDenied, EgressMode, ModelTask, provider(), route(), test_embedding_route_task_is_checked(), test_external_internal_requires_dpa(), test_external_internal_requires_residency() (+13 more)

### Community 86 - "model/test_e2e_operational.py"
Cohesion: 0.16
Nodes (16): ModelUnavailable, graph_labels(), policy(), ScriptedEmbedding, task(), test_primary_retries_cannot_exceed_two(), test_timeout_cannot_exceed_sixty_seconds(), test_embedding_gateway_contract_passes_request_route_and_timeout() (+8 more)

### Community 87 - "pytest"
Cohesion: 0.25
Nodes (13): ModelPolicy, test_mapping_loads_versioned_policy_without_credentials(), test_policy_rejects_credential_fields(), mapping(), test_access_token_field_is_rejected(), test_exact_api_key_field_is_rejected(), test_fallback_route_task_mismatch_is_rejected(), test_mapping_rejects_empty_model_revision() (+5 more)

### Community 96 - "backend_boot/_baseline.py"
Cohesion: 0.32
Nodes (3): backend_boot_task(), pyproject(), task_packet()

### Community 97 - "test_identity.py"
Cohesion: 0.24
Nodes (11): IdentityError, make_service(), test_expired_session_is_rejected(), test_invalid_password_is_safe_auth_error(), test_mfa_is_required_for_privileged_role(), test_principal_rejects_extra_client_claims(), test_revoked_session_is_rejected(), test_sign_in_normalizes_email_and_returns_server_principal() (+3 more)

### Community 102 - "ModelProviderError"
Cohesion: 0.13
Nodes (6): ModelProviderError, RankedDocument, FakeReranker, test_ranked_document_preserves_identifier_and_score(), ScriptedReranker, test_reranker_result_keeps_selected_route()

## Knowledge Gaps
- **1 isolated node(s):** `enterprise-agentic-rag-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 547 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **46 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AuthenticatedPrincipal` connect `AuthorizationEvaluator` to `test_identity.py`, `identity/models.py`, `identity.py`, `authorization/test_behavior_component.py`, `InMemoryPolicyStore`, `DocumentVersionMetadata`, `authorization/test_contract_integration.py`, `PolicyEnforcementPoint`, `service.py`, `test_authorization.py`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Are the 47 inferred relationships involving `DataClassification` (e.g. with `ModelEgressDenied` and `ModelGateway`) actually correct?**
  _`DataClassification` has 47 INFERRED edges - model-reasoned connections that need verification._
- **What connects `enterprise-agentic-rag-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `audit.py` be split into smaller, more focused modules?**
  _Cohesion score 0.125 - nodes in this community are weakly interconnected._
- **Why does `section()` connect `section` to `pathlib`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `ModelGateway` (e.g. with `EmbeddingAdapter` and `EmbeddingRequest`) actually correct?**
  _`ModelGateway` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Should `compose` be split into smaller, more focused modules?**
  _Cohesion score 0.05478750640040963 - nodes in this community are weakly interconnected._