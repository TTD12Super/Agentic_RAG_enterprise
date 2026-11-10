# Graph Report - enterprise-agentic-rag-harness  (2026-11-10)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2695 nodes · 7513 edges · 133 communities (79 shown, 54 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 873 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2b170b77`
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
- CorrelationContext
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
- ModelPolicy
- vite-env.d.ts
- sync_graph.sh
- migrate.sh
- inspect_untrusted_content
- enterprise-agentic-rag-backend
- answer_baseline/test_behavior_component.py
- GeneratedAnswer
- lifecycle.py
- PromptContractIntegrationTests
- rag_hybrid/test_e2e_operational.py
- SecureContextBuilder
- UUID
- test_identity.py
- _gateway
- pytest
- IdentityContractTests
- EvidenceVerifier
- IngestionService
- InMemoryIdentityStore
- FrontendE2EOperationalTests
- IdentityBehaviorTests
- IdentitySecurityTests
- AuthorizationDecision
- answer_baseline/test_contract_integration.py
- ._now
- answer_baseline/test_e2e_operational.py
- ndcg_at_k
- identity/_baseline.py
- guardrails/__init__.py
- evidence/__init__.py
- normalize_user_input
- RetrievedEvidence
- validate_output
- app/authorization/__init__.py
- evidence/test_contract_integration.py
- KnowledgeContractIntegrationTests
- run_local_guardrail_pipeline
- Citation
- pathlib
- DerivedIndex
- KnowledgeOperationalTests

## God Nodes (most connected - your core abstractions)
1. `IngestionService` - 112 edges
2. `auth()` - 87 edges
3. `request()` - 86 edges
4. `DataClassification` - 85 edges
5. `new_service()` - 85 edges
6. `_active_document()` - 78 edges
7. `_principal()` - 64 edges
8. `_retriever()` - 63 edges
9. `ModelGateway` - 62 edges
10. `key()` - 62 edges

## Surprising Connections (you probably didn't know these)
- `DenseRetrievalBehaviorTests` --uses--> `DenseRetriever`  [INFERRED]
  tests/qa/rag/test_behavior_component.py → backend/app/rag/dense.py
- `DenseRetrievalBehaviorTests` --uses--> `DeterministicEmbeddingAdapter`  [INFERRED]
  tests/qa/rag/test_behavior_component.py → backend/app/rag/dense.py
- `DenseRetrievalContractIntegrationTests` --uses--> `DenseRetriever`  [INFERRED]
  tests/qa/rag/test_contract_integration.py → backend/app/rag/dense.py
- `DenseRetrievalOperationalTests` --uses--> `DenseRetriever`  [INFERRED]
  tests/qa/rag/test_e2e_operational.py → backend/app/rag/dense.py
- `DenseRetrievalSecurityAdversarialTests` --uses--> `DeterministicEmbeddingAdapter`  [INFERRED]
  tests/qa/rag/test_security_adversarial.py → backend/app/rag/dense.py

## Import Cycles
- 2-file cycle: `backend/app/api/admin.py -> backend/app/api/identity.py -> backend/app/api/admin.py`

## Communities (133 total, 54 thin omitted)

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

### Community 11 - "env.py"
Cohesion: 0.09
Nodes (3): _database_url(), run_migrations_offline(), run_migrations_online()

### Community 13 - "identity.py"
Cohesion: 0.25
Nodes (9): _bearer_token(), current_identity(), _record(), _record_identity_error(), _request_context(), sign_in(), sign_out(), SignInRequest (+1 more)

### Community 14 - "AuthenticatedPrincipal"
Cohesion: 0.12
Nodes (8): AccessGrant, AnonymousPrincipal, AuthorizationEvaluator, _normalize_action(), PolicyStore, _resource_type(), _valid_epoch(), AuthenticatedPrincipal

### Community 15 - "CorrelationContext"
Cohesion: 0.21
Nodes (5): CorrelationContext, _header(), _new_traceparent(), _valid_traceparent(), test_correlation_context_preserves_valid_headers_and_creates_child()

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

### Community 20 - "ModelRoute"
Cohesion: 0.10
Nodes (17): Action, Effect, EmbeddingAdapter, EmbeddingRequest, EmbeddingResult, RerankerAdapter, RerankerResult, ModelRoute (+9 more)

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
Nodes (3): test_dashboard_has_api_and_security_panels(), test_dashboard_is_valid_json(), test_rag002_task_registry_keeps_retrieval_validation_and_scope()

### Community 27 - "authorization/test_contract_integration.py"
Cohesion: 0.22
Nodes (4): AuthorizationContractIntegrationTests, document(), evaluator(), principal()

### Community 28 - "PolicyEnforcementPoint"
Cohesion: 0.21
Nodes (6): DocumentResource, PolicyEnforcementPoint, AuthorizationOperationalTests, document(), evaluator(), principal()

### Community 29 - "BackendBootstrapBehaviorTests"
Cohesion: 0.15
Nodes (5): assignment(), calls(), function(), literal(), BackendBootstrapBehaviorTests

### Community 30 - "test_models.py"
Cohesion: 0.14
Nodes (43): ModelGateway, ModelUnavailable, DataClassification, route(), ModelTask, FakeEmbedding, policy(), provider() (+35 more)

### Community 31 - "test_authorization.py"
Cohesion: 0.40
Nodes (15): document(), evaluator(), principal(), test_acl_can_assign_employee_and_explicit_deny_wins_for_chairman(), test_anonymous_is_public_only(), test_chairman_is_read_only(), test_conversation_body_is_owner_only(), test_conversation_requires_conversation_resource() (+7 more)

### Community 32 - "_evaluation_harness.py"
Cohesion: 0.32
Nodes (9): answer_correctness(), citation_accuracy(), evaluate_case(), load_records(), no_answer_accuracy(), unauthorized_retrieval_rate(), validate_dataset(), validate_record() (+1 more)

### Community 33 - "GraphifyOperationalTests"
Cohesion: 0.13
Nodes (7): graph(), graphify_bin(), run_graphify(), GraphifyOperationalTests, run_graph_query(), run_graph_query(), test_graphify_query_finds_model_gateway()

### Community 34 - "auth"
Cohesion: 0.06
Nodes (102): ScanReport, ScanVerdict, add_user(), auth(), key(), prepare_review_two(), publish(), request() (+94 more)

### Community 36 - "steps"
Cohesion: 0.15
Nodes (12): jobs, validate, name, on, pull_request, workflow_dispatch, run, uses (+4 more)

### Community 40 - "rules"
Cohesion: 0.17
Nodes (11): runbook, summary, groups, name, rules, severity, alert, annotations (+3 more)

### Community 41 - "ModelProviderError"
Cohesion: 0.13
Nodes (6): ModelProviderError, RankedDocument, FakeReranker, test_ranked_document_preserves_identifier_and_score(), ScriptedReranker, test_reranker_result_keeps_selected_route()

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

### Community 53 - "Claim"
Cohesion: 0.20
Nodes (25): Claim, EvidenceRecord, SourceSpan, citation(), test_authorizer_must_attest_active_current_and_not_revoked(), test_citation_and_source_span_are_immutable(), test_conflicting_numeric_source_spans_are_disclosed(), test_denial_result_does_not_leak_source_text() (+17 more)

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
Cohesion: 0.15
Nodes (47): AccessGrantRequest, AccessRequest, activate_user(), AdminApiState, approve_document_version(), _body(), _bump_policy_epoch(), create_department() (+39 more)

### Community 59 - "main.py"
Cohesion: 0.10
Nodes (4): get_settings(), Settings, healthz(), identity_error_handler()

### Community 60 - "dataclasses"
Cohesion: 0.12
Nodes (5): default_prompt_registry(), _freeze(), PromptDefinition, PromptRegistry, PromptRegistryTests

### Community 61 - "AuthenticationService"
Cohesion: 0.11
Nodes (3): SessionRecord, utc_z(), IdentityStore

### Community 62 - "orchestration/context.py"
Cohesion: 0.17
Nodes (7): AssembledContext, ContextLimitError, estimate_tokens(), PromptMessage, _render_evidence(), _safe_text(), _safe_value()

### Community 64 - "ModelPolicy"
Cohesion: 0.08
Nodes (48): ModelEgressDenied, EgressMode, ModelPolicy, test_mapping_loads_versioned_policy_without_credentials(), test_policy_rejects_credential_fields(), graph_labels(), mapping(), policy() (+40 more)

### Community 86 - "answer_baseline/test_behavior_component.py"
Cohesion: 0.13
Nodes (22): AnswerResult, AnswerStatus, DirectAnswerPipeline, _authorization(), FakeModelGateway, _pipeline(), RaisingRetriever, RaisingVerifier (+14 more)

### Community 87 - "GeneratedAnswer"
Cohesion: 0.11
Nodes (22): GeneratedAnswer, _authorization(), FakeModelGateway, _pipeline(), test_direct_answer_returns_insufficient_without_calling_model_when_no_match(), test_direct_answer_returns_partial_for_mixed_claims(), test_direct_answer_returns_supported_answer_and_authorized_citation(), test_guardrail_failure_fails_closed_before_model_call() (+14 more)

### Community 91 - "lifecycle.py"
Cohesion: 0.13
Nodes (16): _acl_digest(), _chunk_digest(), _chunk_state(), DerivedIndexFailure, DerivedIndexRecord, IndexManifest, IndexPublication, IndexPublicationStatus (+8 more)

### Community 94 - "rag_hybrid/test_e2e_operational.py"
Cohesion: 0.06
Nodes (54): Citation, _citation(), _cosine(), DenseEvidence, DenseRetrievalResult, DenseRetriever, InMemoryDenseVectorIndex, SourceFetchResult (+46 more)

### Community 96 - "UUID"
Cohesion: 0.13
Nodes (12): ApprovalBlocked, ApprovalRecord, DocumentRecord, IdempotencyConflict, IngestionError, IngestionJob, InvalidInput, InvalidTransition (+4 more)

### Community 97 - "test_identity.py"
Cohesion: 0.12
Nodes (15): IdentityError, rate_limited(), AuthenticationService, IdentityErrorPassthrough, now_utc(), make_service(), test_expired_session_is_rejected(), test_invalid_password_is_safe_auth_error() (+7 more)

### Community 98 - "_gateway"
Cohesion: 0.09
Nodes (23): RerankerRequest, DeterministicRerankerAdapter, reciprocal_rank_fusion(), _gateway(), test_rrf_uses_each_branch_rank_and_deduplicates_within_a_branch(), test_reranker_request_rejects_blank_document_fields(), test_reranker_request_requires_documents(), test_reranker_request_requires_query() (+15 more)

### Community 99 - "pytest"
Cohesion: 0.05
Nodes (105): UploadManifest, active(), Clock, make_chunks(), make_manifest(), new_service(), quarantine(), staged() (+97 more)

### Community 102 - "EvidenceVerifier"
Cohesion: 0.22
Nodes (18): EvidenceVerifier, VerificationRequest, allow_active(), citation(), test_authorization_callback_exception_fails_closed(), test_cross_tenant_evidence_is_denied_before_authorizer_invocation(), unexpected(), test_denied_result_does_not_leak_source_text() (+10 more)

### Community 103 - "IngestionService"
Cohesion: 0.13
Nodes (21): IngestionService, _active_document(), _principal(), _retriever(), test_dense_retrieval_returns_authorized_current_chunk_only(), test_explicit_deny_candidates_are_not_exposed(), test_forbidden_source_fetch_is_redacted_without_content_or_citation(), test_active_retrieval_to_evidence_verification_succeeds() (+13 more)

### Community 104 - "InMemoryIdentityStore"
Cohesion: 0.11
Nodes (8): DepartmentRecord, IdentityRecord, normalize_roles(), Role, hash_secret(), InMemoryIdentityStore, verify_secret(), test_noncanonical_role_cannot_create_identity()

### Community 113 - "AuthorizationDecision"
Cohesion: 0.10
Nodes (20): AuthorizationDecision, CitationRecord, _authorization_matches(), allow_active(), revoked(), current_v2(), unexpected(), authorize() (+12 more)

### Community 114 - "answer_baseline/test_contract_integration.py"
Cohesion: 0.19
Nodes (15): _allow(), RecordingModel, RecordingRetriever, _setup(), test_citation_authorization_rejects_document_mismatch(), test_citation_authorization_rejects_non_active_status(), test_citation_authorization_rejects_non_current_version(), test_citation_authorization_rejects_revoked_source() (+7 more)

### Community 116 - "answer_baseline/test_e2e_operational.py"
Cohesion: 0.17
Nodes (16): _allow(), FailingEmbedder, FailingReranker, FakeAnswerGateway, _setup(), test_operational_abstention_is_insufficient_evidence(), test_operational_conflicting_evidence_is_not_harmonized(), test_operational_denied_content_never_appears_in_failure_result() (+8 more)

### Community 117 - "ndcg_at_k"
Cohesion: 0.42
Nodes (10): mean_reciprocal_rank(), ndcg_at_k(), recall_at_k(), source_key(), _span(), _spans(), test_rag_002_regression_metrics_on_tiny_in_memory_corpus(), metrics() (+2 more)

### Community 119 - "guardrails/__init__.py"
Cohesion: 0.15
Nodes (6): _luhn_valid(), redact_sensitive_data(), redact_card(), RedactionResult, ToolDecision, validate_tool_request()

### Community 120 - "evidence/__init__.py"
Cohesion: 0.17
Nodes (8): ClaimVerification, _is_negative(), _numeric_conflict(), _numeric_terms(), _relation(), _terms(), VerificationOutcome, VerificationResult

### Community 121 - "normalize_user_input"
Cohesion: 0.17
Nodes (3): normalize_user_input(), GuardrailBehaviorTests, GuardrailSecurityAdversarialTests

### Community 124 - "validate_output"
Cohesion: 0.26
Nodes (8): _citation(), detect_prompt_injection(), GuardrailResult, _inspect_text(), _normalize_text(), _sensitive_terms(), _terms(), validate_output()

### Community 125 - "app/authorization/__init__.py"
Cohesion: 0.21
Nodes (5): AuthorizationDenied, deny(), Classification, Decision, PolicyDecision

### Community 126 - "evidence/test_contract_integration.py"
Cohesion: 0.23
Nodes (6): allow_active(), citation(), test_chat_001_owns_preview_download_reauthorization_recheck(), test_duplicate_evidence_ids_are_a_malformed_fail_closed_result(), authorize(), test_supported_result_round_trips_tenant_document_version_and_span()

### Community 133 - "KnowledgeOperationalTests"
Cohesion: 0.20
Nodes (3): read(), task(), KnowledgeOperationalTests

## Knowledge Gaps
- **1 isolated node(s):** `enterprise-agentic-rag-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 711 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **54 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AuthenticatedPrincipal` connect `AuthenticatedPrincipal` to `test_identity.py`, `IngestionService`, `InMemoryIdentityStore`, `identity.py`, `authorization/test_behavior_component.py`, `ModelRoute`, `InMemoryPolicyStore`, `answer_baseline/test_behavior_component.py`, `DocumentVersionMetadata`, `admin.py`, `authorization/test_contract_integration.py`, `PolicyEnforcementPoint`, `AuthenticationService`, `rag_hybrid/test_e2e_operational.py`, `test_authorization.py`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Are the 45 inferred relationships involving `IngestionService` (e.g. with `reset_state()` and `test_active_retrieval_to_evidence_verification_succeeds()`) actually correct?**
  _`IngestionService` has 45 INFERRED edges - model-reasoned connections that need verification._
- **What connects `enterprise-agentic-rag-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `audit.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09413067552602436 - nodes in this community are weakly interconnected._
- **Why does `ChunkMetadata` connect `ChunkMetadata` to `UUID`, `auth`, `pytest`, `DerivedIndex`, `IngestionService`, `test_knowledge_database.py`, `test_knowledge_security.py`, `to_qdrant_payload`, `ModelRoute`, `DocumentVersionMetadata`, `inherit_acl`, `.retrievable_chunks`, `lifecycle.py`, `rag_hybrid/test_e2e_operational.py`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 47 inferred relationships involving `DataClassification` (e.g. with `ModelEgressDenied` and `ModelGateway`) actually correct?**
  _`DataClassification` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Should `compose` be split into smaller, more focused modules?**
  _Cohesion score 0.06778476589797344 - nodes in this community are weakly interconnected._