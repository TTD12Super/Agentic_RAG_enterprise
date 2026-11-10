# Enterprise Agentic RAG — Shared System and 17-Block Diagrams

This file contains the downloadable Mermaid source for the overall system and all 17 logical architecture blocks. It mirrors `docs/architecture/blocks/` and does not introduce a new implementation decision. The block documents remain authoritative.

Figma/FigJam board: [Enterprise Agentic RAG diagrams](https://www.figma.com/board/QqEFDcGE0GcP2TeMVqHxLd?utm_source=chatgpt&utm_content=edit_in_figjam&oai_id=v1%2FsD6TKv5BuUkJELwfaGR7gCeEO01MG6CaibfNs4OFbrP7dyudUEojv3&request_id=190e3671-6b81-4029-8f9b-725a9884993c&architecture=true)

## Overall system

```mermaid
flowchart LR
    subgraph client ["Client"]
        webApp["Vercel Frontend"]
    end
    subgraph gateway ["API Boundary"]
        apiGateway["FastAPI API"]
    end
    subgraph service ["Core and Workers"]
        coreApi["Core Coordination"]
        policyService["Authorization PDP and PEP"]
        ragWorker["RAG Worker"]
        ingestionWorker["Ingestion Worker"]
        modelGateway["Model Gateway"]
        evidenceService["Evidence Verification"]
        toolGateway["Tool Gateway"]
    end
    subgraph datastore ["Authoritative and Derived Stores"]
        postgres["PostgreSQL"]
        qdrant["Qdrant Vector Store"]
        redis["Redis Cache and Rate Limits"]
        objectStorage["Private Object Storage"]
    end
    subgraph async ["Durable Job Queue"]
        jobQueue["PostgreSQL Job Queue"]
    end
    subgraph external ["External Systems"]
        llmProvider["Approved LLM and Embedding Providers"]
        connectors["Allowlisted External Connectors"]
        monitoring["OpenTelemetry and Prometheus Monitoring"]
    end

    webApp -->|"HTTPS"| apiGateway
    apiGateway -->|"Routes and validates"| coreApi
    coreApi -->|"Policy checks"| policyService
    policyService -->|"Authorized scope"| ragWorker
    coreApi -->|"Create jobs"| jobQueue
    jobQueue -.->|"Consume question jobs"| ragWorker
    jobQueue -.->|"Consume ingestion jobs"| ingestionWorker
    coreApi -->|"Metadata and audit"| postgres
    coreApi -->|"Cache and rate limits"| redis
    ragWorker -->|"Retrieve and filter"| qdrant
    ragWorker -->|"Read metadata and versions"| postgres
    ragWorker -->|"Scoped memory and cache"| redis
    ragWorker -->|"Generate and rerank"| modelGateway
    ragWorker -->|"Verify draft evidence"| evidenceService
    ragWorker -->|"Read authorized source"| objectStorage
    ingestionWorker -->|"Write versions and metadata"| postgres
    ingestionWorker -->|"Stage source files"| objectStorage
    ingestionWorker -->|"Build index"| qdrant
    ragWorker -->|"Validated tool calls"| toolGateway
    modelGateway -.->|"LLM, embedding, reranking"| llmProvider
    toolGateway -.->|"Read-only integration calls"| connectors
    coreApi -.->|"Metrics, traces, audit events"| monitoring
    ragWorker -.->|"Metrics, traces, usage"| monitoring
    ingestionWorker -.->|"Metrics, traces, job events"| monitoring
    evidenceService -.->|"Verification metrics"| monitoring
```

## 01 — Presentation Layer

```mermaid
flowchart LR
    user["User"] --> ui["React and TypeScript UI"]
    ui --> request["Validated API request"]
    request --> api["FastAPI Core"]
    api --> answer["Rendered answer"]
    answer --> citation["Collapsed citation and source link"]
    citation --> sourceAccess["Authorized preview or original download"]
```

## 02 — API and Identity

```mermaid
flowchart LR
    request["HTTP request and bearer token"] --> tokenCheck["Validate issuer audience expiry"]
    tokenCheck --> session["Session and MFA checks"]
    session --> rateLimit["Rate limit and login throttle"]
    rateLimit --> principal["Authenticated principal"]
    principal --> requestContext["Principal and request ID"]
    requestContext --> apiRoute["API route and job creation"]
```

## 03 — Authorization

```mermaid
flowchart LR
    input["Principal action and resource"] --> policy["Policy evaluator"]
    policy --> tenant["Tenant and department scope"]
    tenant --> roleAllow["RBAC role allow"]
    tenant --> documentAcl["Document ACL"]
    tenant --> explicitDeny["Explicit deny rules"]
    roleAllow --> decision["Final decision"]
    documentAcl --> decision
    explicitDeny --> decision
    decision --> scope["ALLOW with eligible scope or DENY"]
    fallback["Default deny"] --> decision
```

## 04 — Security and Guardrails

```mermaid
flowchart LR
    untrusted["User input or uploaded file"] --> inputInspect["Input inspection"]
    inputInspect --> fileInspect["Magic bytes checksum malware and parser limits"]
    fileInspect --> contextInspect["Context and prompt injection checks"]
    contextInspect --> toolInspect["Tool allowlist and result inspection"]
    toolInspect --> outputInspect["Output and DLP inspection"]
    outputInspect --> decision["Pass block flag or approval"]
    policy["Security policy"] --> inputInspect
```

## 05 — Agent Orchestration

```mermaid
flowchart LR
    question["Authenticated question"] --> router["Rule-first router"]
    router --> simplePath["Simple direct Hybrid RAG"]
    router --> complexPath["Complex or insufficient evidence"]
    simplePath --> plan["Bounded plan state"]
    complexPath --> planner["Planner and bounded replanning"]
    planner --> plan
    plan --> calls["Maximum rounds subqueries and tool calls"]
    calls --> draft["Synthesized answer draft"]
    tools["Approved read-only tools"] --> calls
```

## 06 — Model Management

```mermaid
flowchart LR
    task["Model task request"] --> classification["Data classification"]
    classification --> egress["Provider egress policy"]
    egress --> route["Model route and budget check"]
    route --> primary["Primary provider"]
    route --> fallback["Approved fallback provider"]
    primary --> output["Model output embedding or rank score"]
    fallback --> output
    output --> usage["Usage accounting and latency"]
```

## 07 — Prompt Management

```mermaid
flowchart LR
    instructions["Versioned system and task prompts"] --> assembler["Context assembler"]
    query["Validated user query"] --> assembler
    evidence["Authorized evidence as untrusted data"] --> assembler
    assembler --> messages["Structured model messages"]
    messages --> model["Approved model gateway"]
    assembler --> version["Prompt and assembly version"]
    version --> audit["Privacy-safe audit and evaluation"]
```

## 08 — RAG Engine

```mermaid
flowchart LR
    query["Authorized query and scope"] --> filters["Tenant ACL and ACTIVE-version filters"]
    filters --> dense["Dense retrieval"]
    filters --> lexical["Lexical or BM25 retrieval"]
    dense --> fusion["RRF fusion"]
    lexical --> fusion
    fusion --> rerank["Reranking"]
    rerank --> parent["Conditional parent expansion"]
    parent --> evidence["Chunk evidence with provenance"]
    evidence --> finalCheck["Permission recheck before return"]
```

## 09 — Evidence Verification

```mermaid
flowchart LR
    draft["Draft answer"] --> claims["Claim extraction"]
    spans["Authorized source spans"] --> support["Support matching"]
    claims --> support
    support --> provenance["Source and version provenance"]
    provenance --> authorization["Citation authorization recheck"]
    authorization --> verified["Verified claims and citations"]
    authorization --> revise["Revise or disclose conflict"]
    authorization --> abstain["INSUFFICIENT_EVIDENCE"]
```

## 10 — Knowledge Management

```mermaid
flowchart LR
    parsed["Parsed headings entities and tables"] --> taxonomy["Taxonomy and metadata"]
    parsed --> parentChild["Parent-child references"]
    taxonomy --> catalog["Searchable catalog"]
    parentChild --> provenance["Provenance graph and relations"]
    catalog --> provenance
    provenance --> searchView["Derived search and relationship views"]
    policy["Authoritative ACL policy"] --> searchView
```

## 11 — Document Lifecycle

```mermaid
flowchart LR
    upload["Authorized upload"] --> quarantine["Quarantine and malware scan"]
    quarantine --> reviewOne["Review 1"]
    reviewOne --> parse["Parse extract chunk and validate"]
    parse --> reviewTwo["Review 2"]
    reviewTwo --> staging["Stage version and index"]
    staging --> active["Atomic ACTIVE publication"]
    active --> serving["Available for authorized retrieval"]
    active --> revoke["Revoke or supersede"]
    revoke --> tombstone["Retrieval block and deletion tombstone"]
```

## 12 — Data Governance

```mermaid
flowchart LR
    owner["Document owner and policy requirements"] --> classification["PUBLIC or INTERNAL classification"]
    classification --> retention["Retention and legal hold"]
    retention --> lineage["Ownership and lineage"]
    lineage --> egress["Provider egress policy"]
    egress --> policyStore["Authoritative governance policy"]
    policyStore --> retrieval["Retrieval filters"]
    policyStore --> models["Model provider checks"]
    policyStore --> logging["Logging and audit rules"]
    policyStore --> deletion["Deletion and restore rules"]
```

## 13 — Memory and Caching

```mermaid
flowchart LR
    request["Authorized conversation request"] --> scope["Tenant principal policy and corpus scope"]
    scope --> cacheKey["Scoped cache key"]
    cacheKey --> cache["Redis cache"]
    cache --> hit["Cache hit"]
    cache --> miss["Cache miss"]
    hit --> response["Response or memory"]
    miss --> checkpoint["PostgreSQL durable checkpoint"]
    checkpoint --> response
    change["ACL role version or policy change"] --> invalidate["Invalidate or bypass"]
    invalidate --> cache
```

## 14 — Integration Layer

```mermaid
flowchart LR
    request["Authorized structured tool request"] --> allowlist["Read-only tool allowlist"]
    allowlist --> schema["Schema and identity validation"]
    schema --> connector["Connector or MCP adapter"]
    connector --> external["External system"]
    external --> normalize["Normalize and attribute response"]
    normalize --> worker["Worker result with trace metadata"]
    schema --> reject["Reject unsafe or invalid request"]
```

## 15 — Observability and Audit

```mermaid
flowchart LR
    events["API job worker model retrieval and security events"] --> otel["OpenTelemetry SDK and Collector"]
    otel --> metrics["Metrics"]
    otel --> traces["Traces"]
    otel --> logs["Redacted structured logs"]
    metrics --> prometheus["Prometheus"]
    prometheus --> grafana["Grafana dashboards"]
    prometheus --> alertmanager["Alertmanager P0 to P3 alerts"]
    logs --> audit["Append-only business audit"]
    traces --> correlation["Correlation IDs and investigation view"]
```

## 16 — Evaluation and Feedback

```mermaid
flowchart LR
    golden["Golden Dataset"] --> evaluation["Offline RAG and agent evaluation"]
    queries["Production-like queries"] --> evaluation
    traces["Execution traces and actual sources"] --> evaluation
    feedback["Authorized feedback labels"] --> dataset["Dataset maintenance"]
    dataset --> golden
    evaluation --> metrics["Recall nDCG grounding security latency and cost"]
    metrics --> gates["Release gates"]
    gates --> report["Evaluation report and release decision"]
```

## 17 — Infrastructure and LLMOps

```mermaid
flowchart LR
    source["Source and configuration"] --> ci["CI validation and tests"]
    ci --> image["Reproducible container image"]
    image --> deploy["Approved deployment pipeline"]
    deploy --> runtime["Private API worker and data runtime"]
    runtime --> migrations["Alembic migrations"]
    runtime --> secrets["Managed secrets"]
    runtime --> backup["PostgreSQL backup and WAL PITR"]
    backup --> restore["Restore verification"]
    runtime --> rollback["Rollback and health checks"]
    runtime --> monitoring["Monitoring and alerting baseline"]
```
