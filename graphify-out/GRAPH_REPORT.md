# Graph Report - enterprise-agentic-rag-harness  (2026-11-10)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2737 nodes · 7683 edges · 135 communities (81 shown, 54 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 897 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e64016e5`
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
- dataclasses
- postgres
- postgres
- authorization/test_behavior_component.py
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
- model/test_security_adversarial.py
- vite-env.d.ts
- sync_graph.sh
- migrate.sh
- inspect_untrusted_content
- enterprise-agentic-rag-backend
- answer_baseline/test_behavior_component.py
- answer_baseline/test_security_adversarial.py
- _make_case
- PromptContractIntegrationTests
- rag_hybrid/test_e2e_operational.py
- SecureContextBuilder
- lifecycle.py
- test_identity.py
- ModelPolicy
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
- ProviderPolicy
- answer_baseline/test_e2e_operational.py
- env.py
- identity/_baseline.py
- guardrails/__init__.py
- evidence/__init__.py
- normalize_user_input
- dense.py
- test_answer_baseline.py
- validate_output
- read
- BackendBootstrapContractTests
- KnowledgeContractIntegrationTests
- run_local_guardrail_pipeline
- Citation
- pathlib
- compile_sources_without_writes
- _RrfOnly
- KnowledgeOperationalTests
- assignment

## God Nodes (most connected - your core abstractions)
1. `IngestionService` - 115 edges
2. `DataClassification` - 88 edges
3. `auth()` - 87 edges
4. `request()` - 86 edges
5. `new_service()` - 85 edges
6. `_active_document()` - 78 edges
7. `ModelGateway` - 64 edges
8. `_principal()` - 64 edges
9. `ChunkMetadata` - 63 edges
10. `_retriever()` - 63 edges

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

## Communities (135 total, 54 thin omitted)

### Community 0 - "audit.py"
Cohesion: 0.10
Nodes (17): append_audit_event(), AuditEvent, AuditSink, AuditSinkUnavailable, InMemoryAuditSink, redact_metadata(), _safe_code(), _safe_identifier() (+9 more)

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

### Community 13 - "identity.py"
Cohesion: 0.19
Nodes (10): _bearer_token(), current_identity(), _record(), _record_identity_error(), _request_context(), sign_in(), sign_out(), SignInRequest (+2 more)

### Community 14 - "AuthenticatedPrincipal"
Cohesion: 0.08
Nodes (19): AccessGrant, Action, AuthorizationDenied, AuthorizationEvaluator, deny(), Classification, Decision, DocumentResource (+11 more)

### Community 15 - "dataclasses"
Cohesion: 0.19
Nodes (6): hash_secret(), verify_secret(), _header(), _new_traceparent(), _valid_traceparent(), test_correlation_context_preserves_valid_headers_and_creates_child()

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

### Community 20 - "hybrid.py"
Cohesion: 0.10
Nodes (18): EmbeddingAdapter, EmbeddingRequest, EmbeddingResult, RankedDocument, RerankerAdapter, RerankerRequest, RerankerResult, ModelRoute (+10 more)

### Community 21 - "InMemoryPolicyStore"
Cohesion: 0.27
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
Cohesion: 0.16
Nodes (4): load_records(), test_dashboard_has_api_and_security_panels(), test_dashboard_is_valid_json(), test_rag002_task_registry_keeps_retrieval_validation_and_scope()

### Community 27 - "authorization/test_contract_integration.py"
Cohesion: 0.26
Nodes (4): AuthorizationContractIntegrationTests, document(), evaluator(), principal()

### Community 28 - "PolicyEnforcementPoint"
Cohesion: 0.32
Nodes (4): AuthorizationOperationalTests, document(), evaluator(), principal()

### Community 29 - "BackendBootstrapBehaviorTests"
Cohesion: 0.21
Nodes (4): calls(), function(), literal(), BackendBootstrapBehaviorTests

### Community 30 - "test_models.py"
Cohesion: 0.15
Nodes (42): ModelGateway, DataClassification, EgressMode, ModelTask, FakeEmbedding, policy(), provider(), route() (+34 more)

### Community 31 - "test_authorization.py"
Cohesion: 0.40
Nodes (15): document(), evaluator(), principal(), test_acl_can_assign_employee_and_explicit_deny_wins_for_chairman(), test_anonymous_is_public_only(), test_chairman_is_read_only(), test_conversation_body_is_owner_only(), test_conversation_requires_conversation_resource() (+7 more)

### Community 32 - "eval_001_runner.py"
Cohesion: 0.19
Nodes (13): _aggregate(), _AnswerModel, _Case, evaluate(), _mean(), _percentile(), _principal(), render_report() (+5 more)

### Community 33 - "GraphifyOperationalTests"
Cohesion: 0.15
Nodes (5): graph(), graphify_bin(), run_graphify(), GraphifyOperationalTests, run_graph_query()

### Community 34 - "auth"
Cohesion: 0.06
Nodes (102): ScanReport, ScanVerdict, add_user(), auth(), key(), prepare_review_two(), publish(), request() (+94 more)

### Community 35 - "_evaluation_harness.py"
Cohesion: 0.14
Nodes (17): _vectorize(), answer_correctness(), citation_accuracy(), evaluate_case(), mean_reciprocal_rank(), ndcg_at_k(), no_answer_accuracy(), recall_at_k() (+9 more)

### Community 36 - "steps"
Cohesion: 0.15
Nodes (12): jobs, validate, name, on, pull_request, workflow_dispatch, run, uses (+4 more)

### Community 40 - "rules"
Cohesion: 0.17
Nodes (11): runbook, summary, groups, name, rules, severity, alert, annotations (+3 more)

### Community 41 - "model/test_e2e_operational.py"
Cohesion: 0.10
Nodes (19): ModelProviderError, ModelUnavailable, graph_labels(), policy(), run_graph_query(), ScriptedEmbedding, ScriptedReranker, task() (+11 more)

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
Cohesion: 0.27
Nodes (14): Claim, SourceSpan, citation(), test_authorization_callback_error_fails_closed(), test_current_active_version_is_required_by_authorization_attestation(), test_negation_mismatch_is_conflicting_not_supported(), test_numeric_mismatch_is_conflicting_not_supported(), test_repeated_verification_is_deterministic() (+6 more)

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
Cohesion: 0.10
Nodes (6): rate_limited(), SessionRecord, AuthenticationService, IdentityErrorPassthrough, now_utc(), IdentityStore

### Community 62 - "orchestration/context.py"
Cohesion: 0.22
Nodes (6): AssembledContext, ContextLimitError, PromptMessage, _render_evidence(), _safe_text(), _safe_value()

### Community 64 - "model/test_security_adversarial.py"
Cohesion: 0.18
Nodes (20): ModelEgressDenied, provider(), route(), test_embedding_route_task_is_checked(), test_external_internal_requires_dpa(), test_external_internal_requires_residency(), test_external_provider_requires_retention_policy(), test_external_unapproved_provider_is_denied() (+12 more)

### Community 86 - "answer_baseline/test_behavior_component.py"
Cohesion: 0.09
Nodes (26): _answer_citation(), AnswerCitation, AnswerModelGateway, AnswerResult, AnswerStatus, _authorization_matches(), DirectAnswerPipeline, HybridRetrievalResult (+18 more)

### Community 87 - "answer_baseline/test_security_adversarial.py"
Cohesion: 0.20
Nodes (15): _allow(), FakeModelGateway, _pipeline(), test_cross_tenant_evidence_is_absent_from_dense_bm25_and_answer(), test_direct_prompt_injection_is_denied_before_retrieval_and_model(), test_duplicate_and_unknown_citation_ids_do_not_duplicate_or_leak_metadata(), test_indirect_prompt_injection_is_removed_before_model_context(), test_malformed_model_output_fails_closed_without_denied_source_content() (+7 more)

### Community 91 - "_make_case"
Cohesion: 0.17
Nodes (15): _DenseAsHybrid, evaluation_snapshot(), _make_case(), load_validated_records(), test_all_golden_cases_run_through_v1_v3(), test_allowed_answer_has_no_unauthorized_retrieval_marker(), test_answered_case_keeps_citation_version_and_tenant_binding(), test_dataset_contains_permission_negative_and_cross_tenant_cases() (+7 more)

### Community 94 - "rag_hybrid/test_e2e_operational.py"
Cohesion: 0.07
Nodes (54): PolicyEnforcementPoint, DenseRetriever, InMemoryDenseVectorIndex, HybridRetrievalConfig, HybridRetriever, InMemoryBM25Index, reciprocal_rank_fusion(), _resource() (+46 more)

### Community 95 - "SecureContextBuilder"
Cohesion: 0.20
Nodes (3): SecureContextBuilder, SecureContextBuilderTests, test_verifier_requires_a_server_supplied_authorization_callback()

### Community 96 - "lifecycle.py"
Cohesion: 0.06
Nodes (32): _acl_digest(), ApprovalBlocked, ApprovalRecord, _chunk_digest(), _chunk_state(), DerivedIndex, DerivedIndexFailure, DerivedIndexRecord (+24 more)

### Community 97 - "test_identity.py"
Cohesion: 0.21
Nodes (11): IdentityError, make_service(), test_expired_session_is_rejected(), test_invalid_password_is_safe_auth_error(), test_mfa_is_required_for_privileged_role(), test_principal_rejects_extra_client_claims(), test_revoked_session_is_rejected(), test_sign_in_normalizes_email_and_returns_server_principal() (+3 more)

### Community 98 - "ModelPolicy"
Cohesion: 0.23
Nodes (13): ModelPolicy, test_mapping_loads_versioned_policy_without_credentials(), test_policy_rejects_credential_fields(), mapping(), test_access_token_field_is_rejected(), test_exact_api_key_field_is_rejected(), test_fallback_route_task_mismatch_is_rejected(), test_mapping_rejects_empty_model_revision() (+5 more)

### Community 99 - "pytest"
Cohesion: 0.05
Nodes (105): UploadManifest, active(), Clock, make_chunks(), make_manifest(), new_service(), quarantine(), staged() (+97 more)

### Community 102 - "EvidenceVerifier"
Cohesion: 0.15
Nodes (25): EvidenceRecord, EvidenceVerifier, VerificationRequest, allow_active(), citation(), test_chat_001_owns_preview_download_reauthorization_recheck(), test_duplicate_evidence_ids_are_a_malformed_fail_closed_result(), authorize() (+17 more)

### Community 103 - "IngestionService"
Cohesion: 0.13
Nodes (21): IngestionService, _active_document(), _principal(), _retriever(), test_dense_retrieval_returns_authorized_current_chunk_only(), test_explicit_deny_candidates_are_not_exposed(), test_forbidden_source_fetch_is_redacted_without_content_or_citation(), test_active_retrieval_to_evidence_verification_succeeds() (+13 more)

### Community 104 - "InMemoryIdentityStore"
Cohesion: 0.09
Nodes (7): DepartmentRecord, IdentityRecord, normalize_roles(), Role, utc_z(), InMemoryIdentityStore, test_noncanonical_role_cannot_create_identity()

### Community 113 - "AuthorizationDecision"
Cohesion: 0.11
Nodes (29): AuthorizationDecision, CitationRecord, allow_active(), citation(), test_authorizer_must_attest_active_current_and_not_revoked(), revoked(), test_citation_and_source_span_are_immutable(), test_conflicting_numeric_source_spans_are_disclosed() (+21 more)

### Community 114 - "answer_baseline/test_contract_integration.py"
Cohesion: 0.19
Nodes (15): _allow(), RecordingModel, RecordingRetriever, _setup(), test_citation_authorization_rejects_document_mismatch(), test_citation_authorization_rejects_non_active_status(), test_citation_authorization_rejects_non_current_version(), test_citation_authorization_rejects_revoked_source() (+7 more)

### Community 115 - "ProviderPolicy"
Cohesion: 0.14
Nodes (5): route(), ProviderPolicy, FakeReranker, test_gateway_reranker_happy_path(), test_reranker_gateway_contract_passes_request_route_and_timeout()

### Community 116 - "answer_baseline/test_e2e_operational.py"
Cohesion: 0.15
Nodes (17): GeneratedAnswer, _allow(), FailingEmbedder, FailingReranker, FakeAnswerGateway, _setup(), test_operational_abstention_is_insufficient_evidence(), test_operational_conflicting_evidence_is_not_harmonized() (+9 more)

### Community 117 - "env.py"
Cohesion: 0.19
Nodes (4): _database_url(), run_migrations_offline(), run_migrations_online(), DatabaseMigrationSmokeTests

### Community 119 - "guardrails/__init__.py"
Cohesion: 0.15
Nodes (6): _luhn_valid(), redact_sensitive_data(), redact_card(), RedactionResult, ToolDecision, validate_tool_request()

### Community 120 - "evidence/__init__.py"
Cohesion: 0.19
Nodes (8): ClaimVerification, _is_negative(), _numeric_conflict(), _numeric_terms(), _relation(), _terms(), VerificationOutcome, VerificationResult

### Community 121 - "normalize_user_input"
Cohesion: 0.17
Nodes (3): normalize_user_input(), GuardrailBehaviorTests, GuardrailSecurityAdversarialTests

### Community 122 - "dense.py"
Cohesion: 0.13
Nodes (12): Citation, _citation(), _cosine(), DenseEvidence, DenseRetrievalResult, SourceFetchResult, _uuid(), _VectorRecord (+4 more)

### Community 123 - "test_answer_baseline.py"
Cohesion: 0.36
Nodes (9): _authorization(), FakeModelGateway, _pipeline(), test_direct_answer_returns_insufficient_without_calling_model_when_no_match(), test_direct_answer_returns_partial_for_mixed_claims(), test_direct_answer_returns_supported_answer_and_authorized_citation(), test_guardrail_failure_fails_closed_before_model_call(), test_model_egress_failure_fails_closed_without_answer_or_citation() (+1 more)

### Community 124 - "validate_output"
Cohesion: 0.26
Nodes (8): _citation(), detect_prompt_injection(), GuardrailResult, _inspect_text(), _normalize_text(), _sensitive_terms(), _terms(), validate_output()

### Community 125 - "read"
Cohesion: 0.27
Nodes (4): backend_boot_task(), read(), task_packet(), BackendBootstrapOperationalTests

### Community 133 - "KnowledgeOperationalTests"
Cohesion: 0.20
Nodes (3): read(), task(), KnowledgeOperationalTests

## Knowledge Gaps
- **1 isolated node(s):** `enterprise-agentic-rag-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 716 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **54 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AuthenticatedPrincipal` connect `AuthenticatedPrincipal` to `eval_001_runner.py`, `test_identity.py`, `dense.py`, `IngestionService`, `InMemoryIdentityStore`, `identity.py`, `authorization/test_behavior_component.py`, `hybrid.py`, `InMemoryPolicyStore`, `answer_baseline/test_behavior_component.py`, `DocumentVersionMetadata`, `admin.py`, `authorization/test_contract_integration.py`, `PolicyEnforcementPoint`, `AuthenticationService`, `rag_hybrid/test_e2e_operational.py`, `test_authorization.py`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 45 inferred relationships involving `IngestionService` (e.g. with `reset_state()` and `test_active_retrieval_to_evidence_verification_succeeds()`) actually correct?**
  _`IngestionService` has 45 INFERRED edges - model-reasoned connections that need verification._
- **What connects `enterprise-agentic-rag-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `audit.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10121951219512196 - nodes in this community are weakly interconnected._
- **Why does `ChunkMetadata` connect `ChunkMetadata` to `lifecycle.py`, `eval_001_runner.py`, `auth`, `pytest`, `IngestionService`, `AuthenticatedPrincipal`, `test_knowledge_database.py`, `test_knowledge_security.py`, `to_qdrant_payload`, `hybrid.py`, `DocumentVersionMetadata`, `inherit_acl`, `dense.py`, `_make_case`, `rag_hybrid/test_e2e_operational.py`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 47 inferred relationships involving `DataClassification` (e.g. with `ModelEgressDenied` and `ModelGateway`) actually correct?**
  _`DataClassification` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Should `compose` be split into smaller, more focused modules?**
  _Cohesion score 0.05478750640040963 - nodes in this community are weakly interconnected._