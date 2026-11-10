# Graph Report - enterprise-agentic-rag-harness  (2026-11-10)

## Corpus Check
- 131 files · ~138,090 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 68 file(s) not represented in the graph (top: (none) 53, .toml 9, .example 2)

## Summary
- 1332 nodes · 2384 edges · 91 communities (45 shown, 46 thin omitted)
- Extraction: 83% EXTRACTED · 17% INFERRED · 0% AMBIGUOUS · INFERRED: 396 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3bf49420`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- InMemoryAuditSink
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
- models.py
- postgres
- postgres
- authorization/test_behavior_component.py
- package.json
- policy.py
- InMemoryPolicyStore
- audit.py
- compilerOptions
- test_audit_identity.py
- .from_headers
- json
- authorization/test_contract_integration.py
- PolicyEnforcementPoint
- BackendBootstrapBehaviorTests
- AuthorizationDenied
- test_authorization.py
- _evaluation_harness.py
- GraphifyOperationalTests
- pathlib
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
- IdentityBehaviorTests
- IdentityContractTests
- IdentitySecurityTests
- App.tsx
- datasources
- monitoring/prometheus.yml
- BackendBootstrapContractTests
- dependencies
- vitest
- scripts
- backend_boot/_baseline.py
- main.py
- load_validated_records
- compile_sources_without_writes
- identity/_baseline.py
- route_calls
- tree
- vite-env.d.ts
- sync_graph.sh
- migrate.sh
- enterprise-agentic-rag-backend
- test_app.py

## God Nodes (most connected - your core abstractions)
1. `section()` - 42 edges
2. `AuthenticatedPrincipal` - 36 edges
3. `compose()` - 35 edges
4. `require_all()` - 35 edges
5. `read()` - 30 edges
6. `read()` - 26 edges
7. `InMemoryPolicyStore` - 23 edges
8. `AuthorizationEvaluator` - 22 edges
9. `InMemoryIdentityStore` - 22 edges
10. `read()` - 21 edges

## Surprising Connections (you probably didn't know these)
- `AuthorizationSecurityAdversarialTests` --uses--> `AuthenticatedPrincipal`  [INFERRED]
  tests/qa/authorization/test_security_adversarial.py → backend/app/identity/models.py
- `test_unknown_classification_and_noncanonical_principal_are_denied()` --uses--> `AuthenticatedPrincipal`  [INFERRED]
  tests/security/test_authorization.py → backend/app/identity/models.py
- `literal()` --references--> `expr`  [EXTRACTED]
  tests/qa/backend_boot/_baseline.py → infra/monitoring/alerts.yml
- `test_sign_in_denial_emits_no_credentials_or_body()` --calls--> `InMemoryAuditSink`  [EXTRACTED]
  tests/integration/test_audit_identity.py → backend/app/observability/audit.py
- `test_sign_in_emits_correlated_success_event()` --calls--> `InMemoryAuditSink`  [EXTRACTED]
  tests/integration/test_audit_identity.py → backend/app/observability/audit.py

## Import Cycles
- None detected.

## Communities (91 total, 46 thin omitted)

### Community 0 - "InMemoryAuditSink"
Cohesion: 0.15
Nodes (7): AuditEvent, AuditSinkUnavailable, InMemoryAuditSink, redact_metadata(), test_audit_sink_is_append_only_and_structured(), test_redaction_drops_credentials_and_raw_content(), test_unavailable_sink_does_not_accept_an_event()

### Community 1 - "compose"
Cohesion: 0.05
Nodes (13): get_settings(), Settings, compose(), compose_config_result(), database(), handoff(), read(), tasks() (+5 more)

### Community 2 - "read"
Cohesion: 0.05
Nodes (10): compose_config_result(), migration_files(), migration_text(), read(), task(), tasks(), DatabaseBaselineBehaviorTests, DatabaseBaselineContractTests (+2 more)

### Community 3 - "read"
Cohesion: 0.06
Nodes (6): read(), task(), InfrastructureBehaviorTests, InfrastructureContractTests, InfrastructureOperationalTests, InfrastructureSecurityTests

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
Cohesion: 0.09
Nodes (4): read(), GraphifyBehaviorTests, GraphifyContractTests, GraphifySecurityTests

### Community 9 - "otel-collector-config.yaml"
Cohesion: 0.06
Nodes (32): action, key, actions, send_batch_size, timeout, exporters, prometheus, endpoint (+24 more)

### Community 10 - "prometheus"
Cohesion: 0.06
Nodes (30): command, image, ports, read_only, security_opt, volumes, depends_on, image (+22 more)

### Community 11 - "env.py"
Cohesion: 0.08
Nodes (4): _database_url(), run_migrations_offline(), run_migrations_online(), DatabaseMigrationSmokeTests

### Community 13 - "identity.py"
Cohesion: 0.27
Nodes (9): _bearer_token(), current_identity(), _record(), _record_identity_error(), _request_context(), sign_in(), sign_out(), SignInRequest (+1 more)

### Community 14 - "AuthorizationEvaluator"
Cohesion: 0.10
Nodes (8): AccessGrant, AnonymousPrincipal, AuthorizationEvaluator, _normalize_action(), PolicyStore, _resource_type(), _valid_epoch(), AuthenticatedPrincipal

### Community 15 - "models.py"
Cohesion: 0.05
Nodes (25): IdentityError, rate_limited(), IdentityRecord, normalize_roles(), Role, SessionRecord, utc_z(), AuthenticationService (+17 more)

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

### Community 20 - "policy.py"
Cohesion: 0.27
Nodes (6): Action, Classification, ConversationResource, Decision, DocumentResource, Effect

### Community 21 - "InMemoryPolicyStore"
Cohesion: 0.30
Nodes (5): InMemoryPolicyStore, AuthorizationSecurityAdversarialTests, document(), evaluator(), principal()

### Community 22 - "audit.py"
Cohesion: 0.18
Nodes (5): append_audit_event(), AuditSink, _safe_code(), _safe_identifier(), _utc_z()

### Community 23 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+10 more)

### Community 24 - "test_audit_identity.py"
Cohesion: 0.33
Nodes (5): _add_identity(), _request(), test_sign_in_denial_emits_no_credentials_or_body(), test_sign_in_emits_correlated_success_event(), test_sign_in_fails_closed_when_audit_sink_is_unavailable()

### Community 25 - ".from_headers"
Cohesion: 0.20
Nodes (5): identity_error_handler(), _header(), _new_traceparent(), _valid_traceparent(), test_correlation_context_preserves_valid_headers_and_creates_child()

### Community 26 - "json"
Cohesion: 0.15
Nodes (3): test_dashboard_has_api_and_security_panels(), test_dashboard_is_valid_json(), tasks()

### Community 27 - "authorization/test_contract_integration.py"
Cohesion: 0.26
Nodes (4): AuthorizationContractIntegrationTests, document(), evaluator(), principal()

### Community 28 - "PolicyEnforcementPoint"
Cohesion: 0.29
Nodes (5): PolicyEnforcementPoint, AuthorizationOperationalTests, document(), evaluator(), principal()

### Community 29 - "BackendBootstrapBehaviorTests"
Cohesion: 0.21
Nodes (4): calls(), function(), literal(), BackendBootstrapBehaviorTests

### Community 30 - "AuthorizationDenied"
Cohesion: 0.28
Nodes (3): AuthorizationDenied, deny(), PolicyDecision

### Community 31 - "test_authorization.py"
Cohesion: 0.40
Nodes (15): document(), evaluator(), principal(), test_acl_can_assign_employee_and_explicit_deny_wins_for_chairman(), test_anonymous_is_public_only(), test_chairman_is_read_only(), test_conversation_body_is_owner_only(), test_conversation_requires_conversation_resource() (+7 more)

### Community 32 - "_evaluation_harness.py"
Cohesion: 0.31
Nodes (9): citation_accuracy(), evaluate_case(), mean_reciprocal_rank(), ndcg_at_k(), recall_at_k(), source_key(), validate_dataset(), validate_record() (+1 more)

### Community 33 - "GraphifyOperationalTests"
Cohesion: 0.15
Nodes (4): graph(), graphify_bin(), run_graphify(), GraphifyOperationalTests

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
Cohesion: 0.27
Nodes (4): backend_boot_task(), read(), task_packet(), BackendBootstrapOperationalTests

### Community 44 - "eslint.config.js"
Cohesion: 0.18
Nodes (10): @eslint/js@9.17.0, eslint-plugin-react-hooks@5.1.0, eslint-plugin-react-refresh@0.4.16, globals@15.14.0, typescript-eslint@8.18.0, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh (+2 more)

### Community 45 - "route"
Cohesion: 0.18
Nodes (10): global, resolve_timeout, receivers, name, route, group_by, group_interval, group_wait (+2 more)

### Community 50 - "App.tsx"
Cohesion: 0.27
Nodes (5): react@18.3.1, App(), supportedRoles, appConfig, react

### Community 51 - "datasources"
Cohesion: 0.22
Nodes (8): apiVersion, datasources, access, editable, isDefault, name, type, url

### Community 52 - "monitoring/prometheus.yml"
Cohesion: 0.22
Nodes (8): global, evaluation_interval, scrape_interval, rule_files, scrape_configs, job_name, static_configs, targets

### Community 54 - "dependencies"
Cohesion: 0.29
Nodes (7): dependencies, react-dom@18.3.1, vite@6.3.5, @vitejs/plugin-react@4.6.0, react-dom, vite, @vitejs/plugin-react

### Community 55 - "vitest"
Cohesion: 0.25
Nodes (6): @testing-library/jest-dom@6.6.3, @testing-library/react@16.1.0, vitest@2.1.8, @testing-library/jest-dom, @testing-library/react, vitest

### Community 56 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, preview, test, test:watch, typecheck

## Knowledge Gaps
- **1 isolated node(s):** `enterprise-agentic-rag-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 498 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **46 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AuthenticatedPrincipal` connect `AuthorizationEvaluator` to `identity.py`, `models.py`, `authorization/test_behavior_component.py`, `policy.py`, `InMemoryPolicyStore`, `authorization/test_contract_integration.py`, `PolicyEnforcementPoint`, `test_authorization.py`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Are the 39 inferred relationships involving `section()` (e.g. with `.test_behavior_anonymous_and_role_boundaries_are_present()` and `.test_behavior_authorization_order_is_explicit()`) actually correct?**
  _`section()` has 39 INFERRED edges - model-reasoned connections that need verification._
- **What connects `enterprise-agentic-rag-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `compose` be split into smaller, more focused modules?**
  _Cohesion score 0.05478750640040963 - nodes in this community are weakly interconnected._
- **Why does `SecurityAdversarialTests` connect `SecurityAdversarialTests` to `load_validated_records`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `AuthenticatedPrincipal` (e.g. with `current_identity()` and `_record()`) actually correct?**
  _`AuthenticatedPrincipal` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Should `read` be split into smaller, more focused modules?**
  _Cohesion score 0.05194805194805195 - nodes in this community are weakly interconnected._