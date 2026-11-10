# Graph Report - enterprise-agentic-rag-harness  (2026-11-10)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2570 nodes · 7088 edges · 129 communities (74 shown, 55 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 831 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `71866f89`
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
- ModelProviderError
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
- rag_hybrid/test_e2e_operational.py
- SecureContextBuilder
- UUID
- test_identity.py
- _make_retriever
- pytest
- IdentityContractTests
- DataClassification
- IngestionService
- InMemoryIdentityStore
- FrontendE2EOperationalTests
- IdentityBehaviorTests
- IdentitySecurityTests
- read
- os
- ._now
- BackendBootstrapContractTests
- ndcg_at_k
- identity/_baseline.py
- guardrails/__init__.py
- compile_sources_without_writes
- normalize_user_input
- assignment
- validate_output
- run_local_guardrail_pipeline
- Citation
- pathlib
- KnowledgeOperationalTests

## God Nodes (most connected - your core abstractions)
1. `IngestionService` - 110 edges
2. `auth()` - 87 edges
3. `request()` - 86 edges
4. `new_service()` - 85 edges
5. `DataClassification` - 78 edges
6. `_active_document()` - 76 edges
7. `_retriever()` - 63 edges
8. `_principal()` - 62 edges
9. `key()` - 62 edges
10. `ModelGateway` - 61 edges

## Surprising Connections (you probably didn't know these)
- `provider()` --uses--> `DataClassification`  [INFERRED]
  tests/qa/model/_baseline.py → backend/app/models/policy.py
- `test_external_internal_requires_dpa()` --uses--> `DataClassification`  [INFERRED]
  tests/qa/model/test_behavior_component.py → backend/app/models/policy.py
- `test_external_internal_requires_residency()` --uses--> `DataClassification`  [INFERRED]
  tests/qa/model/test_behavior_component.py → backend/app/models/policy.py
- `test_external_provider_requires_retention_policy()` --uses--> `DataClassification`  [INFERRED]
  tests/qa/model/test_behavior_component.py → backend/app/models/policy.py
- `test_external_unapproved_provider_is_denied()` --uses--> `DataClassification`  [INFERRED]
  tests/qa/model/test_behavior_component.py → backend/app/models/policy.py

## Import Cycles
- 2-file cycle: `backend/app/api/admin.py -> backend/app/api/identity.py -> backend/app/api/admin.py`

## Communities (129 total, 55 thin omitted)

### Community 0 - "audit.py"
Cohesion: 0.09
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

### Community 11 - "env.py"
Cohesion: 0.09
Nodes (3): _database_url(), run_migrations_offline(), run_migrations_online()

### Community 13 - "identity.py"
Cohesion: 0.27
Nodes (9): _bearer_token(), current_identity(), _record(), _record_identity_error(), _request_context(), sign_in(), sign_out(), SignInRequest (+1 more)

### Community 14 - "AuthenticatedPrincipal"
Cohesion: 0.08
Nodes (14): Action, AuthorizationDenied, AuthorizationEvaluator, deny(), Classification, ConversationResource, Decision, DocumentResource (+6 more)

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
Nodes (12): _ImmutableModel, EmbeddingAdapter, RankedDocument, RerankerAdapter, RerankerRequest, RerankerResult, ModelRoute, ProviderPolicy (+4 more)

### Community 21 - "InMemoryPolicyStore"
Cohesion: 0.27
Nodes (5): InMemoryPolicyStore, AuthorizationSecurityAdversarialTests, document(), evaluator(), principal()

### Community 22 - "ChunkMetadata"
Cohesion: 0.15
Nodes (10): ChunkMetadata, DocumentMetadata, test_active_chunk_requires_acl_metadata(), test_chunk_accepts_source_provenance(), test_chunk_rejects_reversed_pages(), test_chunk_rejects_self_parent(), test_document_metadata_is_tenant_scoped(), test_root_chunk_can_have_no_parent() (+2 more)

### Community 23 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+10 more)

### Community 24 - "DocumentVersionMetadata"
Cohesion: 0.08
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
Cohesion: 0.21
Nodes (4): calls(), function(), literal(), BackendBootstrapBehaviorTests

### Community 30 - "test_models.py"
Cohesion: 0.11
Nodes (46): ModelGateway, EmbeddingRequest, EmbeddingResult, ModelTask, FakeEmbedding, policy(), provider(), route() (+38 more)

### Community 31 - "test_authorization.py"
Cohesion: 0.31
Nodes (16): AuthenticatedPrincipal, document(), evaluator(), principal(), test_acl_can_assign_employee_and_explicit_deny_wins_for_chairman(), test_anonymous_is_public_only(), test_chairman_is_read_only(), test_conversation_body_is_owner_only() (+8 more)

### Community 32 - "_evaluation_harness.py"
Cohesion: 0.32
Nodes (9): answer_correctness(), citation_accuracy(), evaluate_case(), load_records(), no_answer_accuracy(), unauthorized_retrieval_rate(), validate_dataset(), validate_record() (+1 more)

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

### Community 42 - "backend_boot/_baseline.py"
Cohesion: 0.21
Nodes (4): pyproject(), route_calls(), route_path(), tree()

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

### Community 53 - "Claim"
Cohesion: 0.07
Nodes (68): AuthorizationDecision, CitationRecord, Claim, ClaimVerification, EvidenceRecord, EvidenceVerifier, _is_negative(), _numeric_conflict() (+60 more)

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

### Community 59 - "main.py"
Cohesion: 0.09
Nodes (9): get_settings(), Settings, healthz(), identity_error_handler(), _add_identity(), _request(), test_sign_in_denial_emits_no_credentials_or_body(), test_sign_in_emits_correlated_success_event() (+1 more)

### Community 60 - "dataclasses"
Cohesion: 0.11
Nodes (5): default_prompt_registry(), _freeze(), PromptDefinition, PromptRegistry, PromptRegistryTests

### Community 61 - "AuthenticationService"
Cohesion: 0.10
Nodes (3): SessionRecord, utc_z(), IdentityStore

### Community 62 - "orchestration/context.py"
Cohesion: 0.22
Nodes (6): AssembledContext, ContextLimitError, PromptMessage, _render_evidence(), _safe_text(), _safe_value()

### Community 64 - "EgressMode"
Cohesion: 0.20
Nodes (21): ModelEgressDenied, EgressMode, provider(), test_embedding_route_task_is_checked(), test_external_internal_requires_dpa(), test_external_internal_requires_residency(), test_external_provider_requires_retention_policy(), test_external_unapproved_provider_is_denied() (+13 more)

### Community 86 - "model/test_e2e_operational.py"
Cohesion: 0.18
Nodes (15): graph_labels(), policy(), route(), run_graph_query(), ScriptedEmbedding, task(), test_embedding_result_keeps_selected_route(), test_approved_fallback_runs_after_primary_failure() (+7 more)

### Community 87 - "pytest"
Cohesion: 0.23
Nodes (13): ModelPolicy, test_mapping_loads_versioned_policy_without_credentials(), test_policy_rejects_credential_fields(), mapping(), test_access_token_field_is_rejected(), test_exact_api_key_field_is_rejected(), test_fallback_route_task_mismatch_is_rejected(), test_mapping_rejects_empty_model_revision() (+5 more)

### Community 91 - "lifecycle.py"
Cohesion: 0.08
Nodes (19): _acl_digest(), _chunk_digest(), _chunk_state(), DerivedIndex, DerivedIndexFailure, DerivedIndexRecord, IndexManifest, IndexPublication (+11 more)

### Community 94 - "rag_hybrid/test_e2e_operational.py"
Cohesion: 0.07
Nodes (34): PolicyEnforcementPoint, Citation, _citation(), _cosine(), DenseEvidence, DenseRetrievalResult, DenseRetriever, InMemoryDenseVectorIndex (+26 more)

### Community 95 - "SecureContextBuilder"
Cohesion: 0.20
Nodes (3): SecureContextBuilder, SecureContextBuilderTests, test_verifier_requires_a_server_supplied_authorization_callback()

### Community 96 - "UUID"
Cohesion: 0.15
Nodes (10): ApprovalBlocked, ApprovalRecord, DocumentRecord, IdempotencyConflict, IngestionJob, InvalidInput, InvalidTransition, NotFound (+2 more)

### Community 97 - "test_identity.py"
Cohesion: 0.18
Nodes (13): IdentityError, rate_limited(), AuthenticationService, make_service(), test_expired_session_is_rejected(), test_invalid_password_is_safe_auth_error(), test_mfa_is_required_for_privileged_role(), test_principal_rejects_extra_client_claims() (+5 more)

### Community 98 - "_make_retriever"
Cohesion: 0.08
Nodes (39): AccessGrant, DeterministicRerankerAdapter, HybridRetrievalConfig, reciprocal_rank_fusion(), _gateway(), _make_retriever(), test_hybrid_retrieval_composes_bm25_rrf_and_local_reranker(), test_rrf_uses_each_branch_rank_and_deduplicates_within_a_branch() (+31 more)

### Community 99 - "pytest"
Cohesion: 0.05
Nodes (105): UploadManifest, active(), Clock, make_chunks(), make_manifest(), new_service(), quarantine(), staged() (+97 more)

### Community 102 - "DataClassification"
Cohesion: 0.17
Nodes (7): DataClassification, route(), test_gateway_reranker_happy_path(), ScriptedReranker, test_reranker_gateway_contract_passes_request_route_and_timeout(), test_reranker_result_keeps_selected_route(), test_reranker_happy_path_completes_once()

### Community 103 - "IngestionService"
Cohesion: 0.12
Nodes (21): IngestionService, _active_document(), _principal(), _retriever(), test_dense_retrieval_returns_authorized_current_chunk_only(), test_explicit_deny_candidates_are_not_exposed(), test_forbidden_source_fetch_is_redacted_without_content_or_citation(), test_active_retrieval_to_evidence_verification_succeeds() (+13 more)

### Community 104 - "InMemoryIdentityStore"
Cohesion: 0.12
Nodes (6): DepartmentRecord, IdentityRecord, normalize_roles(), Role, InMemoryIdentityStore, test_noncanonical_role_cannot_create_identity()

### Community 113 - "read"
Cohesion: 0.27
Nodes (4): backend_boot_task(), read(), task_packet(), BackendBootstrapOperationalTests

### Community 117 - "ndcg_at_k"
Cohesion: 0.42
Nodes (10): mean_reciprocal_rank(), ndcg_at_k(), recall_at_k(), source_key(), _span(), _spans(), test_rag_002_regression_metrics_on_tiny_in_memory_corpus(), metrics() (+2 more)

### Community 119 - "guardrails/__init__.py"
Cohesion: 0.15
Nodes (6): _luhn_valid(), redact_sensitive_data(), redact_card(), RedactionResult, ToolDecision, validate_tool_request()

### Community 121 - "normalize_user_input"
Cohesion: 0.17
Nodes (3): normalize_user_input(), GuardrailBehaviorTests, GuardrailSecurityAdversarialTests

### Community 124 - "validate_output"
Cohesion: 0.26
Nodes (8): _citation(), detect_prompt_injection(), GuardrailResult, _inspect_text(), _normalize_text(), _sensitive_terms(), _terms(), validate_output()

### Community 133 - "KnowledgeOperationalTests"
Cohesion: 0.20
Nodes (3): read(), task(), KnowledgeOperationalTests

## Knowledge Gaps
- **1 isolated node(s):** `enterprise-agentic-rag-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 688 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **55 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AuthenticatedPrincipal` connect `test_authorization.py` to `test_identity.py`, `_make_retriever`, `IngestionService`, `InMemoryIdentityStore`, `identity.py`, `AuthenticatedPrincipal`, `store.py`, `authorization/test_behavior_component.py`, `ModelRoute`, `InMemoryPolicyStore`, `DocumentVersionMetadata`, `admin.py`, `authorization/test_contract_integration.py`, `PolicyEnforcementPoint`, `AuthenticationService`, `rag_hybrid/test_e2e_operational.py`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Are the 45 inferred relationships involving `IngestionService` (e.g. with `reset_state()` and `test_active_retrieval_to_evidence_verification_succeeds()`) actually correct?**
  _`IngestionService` has 45 INFERRED edges - model-reasoned connections that need verification._
- **What connects `enterprise-agentic-rag-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `audit.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08686868686868687 - nodes in this community are weakly interconnected._
- **Why does `DataClassification` connect `DataClassification` to `EgressMode`, `_make_retriever`, `pytest`, `IngestionService`, `ModelProviderError`, `ModelRoute`, `model/test_e2e_operational.py`, `pytest`, `rag_hybrid/test_e2e_operational.py`, `admin.py`, `lifecycle.py`, `test_models.py`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `new_service()` (e.g. with `test_approval_expiry_blocks_processing()` and `test_empty_processing_input_is_rejected()`) actually correct?**
  _`new_service()` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Should `compose` be split into smaller, more focused modules?**
  _Cohesion score 0.06778476589797344 - nodes in this community are weakly interconnected._