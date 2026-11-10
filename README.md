# Enterprise Agentic RAG

### A Secure, Modular, and Scalable Enterprise AI Knowledge Platform

Enterprise Agentic RAG is an AI-powered platform designed to help organizations securely manage, retrieve, and utilize knowledge from enterprise documents.

The system combines **Advanced Retrieval-Augmented Generation (RAG)**, **Agentic AI**, and **Enterprise Security** to deliver accurate, evidence-grounded, and permission-aware responses.

The project follows a **Modular Monolith Architecture** and uses **Codex Multi-Agent Development** to support structured, collaborative implementation.

> **Project Status:** Architecture & Development Harness — Pre-Implementation

---

## 1. Project Overview

The goal of Enterprise Agentic RAG is to provide a reusable AI knowledge management platform that can operate across different organizations and document collections.

Rather than relying solely on a language model's internal knowledge, the system retrieves relevant information from authorized enterprise sources before generating responses.

The platform is designed around three core principles:

- **Security First:** Enforce user permissions and protect sensitive enterprise information.
- **Evidence-Based AI:** Generate responses grounded in verifiable source documents.
- **Modular Development:** Maintain independent, well-defined components that can evolve over time.

For detailed project objectives and scope, see [GOALS.md](GOALS.md).

---

## 2. Project Goals

The primary objectives are to:

- Build a secure and reusable enterprise knowledge platform.
- Support document ingestion, management, and versioning.
- Implement permission-aware information retrieval.
- Develop an Advanced Hybrid RAG pipeline.
- Introduce intelligent, controlled agent orchestration.
- Provide reliable answers with source citations.
- Support enterprise-level monitoring and evaluation.
- Enable collaborative development using specialized Codex agents.

Detailed requirements, constraints, and non-goals are documented in [GOALS.md](GOALS.md).

---

## 3. Key Features

The platform is designed to provide the following capabilities:

| Category | Core Capabilities |
|---|---|
| Document Management | Upload, processing, approval, versioning |
| Authentication & Authorization | Identity management, RBAC, ABAC, ACL |
| Advanced RAG | Hybrid Search, RRF, Reranking, Parent-Child Retrieval |
| Agentic AI | Planning, Tool Calling, Multi-Step Retrieval |
| Security | Prompt Injection Defense, Tool Guardrails, DLP |
| Evidence Verification | Grounding, Source Validation, Citations |
| Memory & Caching | Conversation Memory, Prompt and Retrieval Caching |
| Observability | Logging, Tracing, Auditing |
| Evaluation | Retrieval, Answer Quality, Security Testing |
| Integration | External APIs and Enterprise Connectors |

These are target capabilities and will be implemented incrementally.

---

## 4. High-Level Architecture

The system is organized into **17 logical architecture blocks**, grouped into major functional areas.

```text
                  ENTERPRISE AGENTIC RAG
                            |
                            v
                    APPLICATION LAYER
                 (Admin Portal / Chat UI)
                            |
                            v
                    API & IDENTITY LAYER
                            |
                            v
                   SECURITY & ACCESS
                            |
                            v
                   AGENT ORCHESTRATION
                         (LangGraph)
                            |
                +-----------+-----------+
                |                       |
                v                       v
          MODEL & PROMPT            KNOWLEDGE & RAG
           MANAGEMENT                  ENGINE
                |                       |
                +-----------+-----------+
                            |
                            v
                   EVIDENCE VERIFICATION
                            |
                            v
                      USER RESPONSE


             CROSS-CUTTING COMPONENTS
                            |
          +-----------------+-----------------+
          |                 |                 |
          v                 v                 v
     DATA GOVERNANCE   MEMORY & CACHING   OBSERVABILITY
          |                 |                 |
          +-----------------+-----------------+
                            |
                            v
                    INFRASTRUCTURE
```

The platform supports two primary workflows:

**Document Ingestion:** Securely processes and indexes enterprise documents.

**Agentic Question Answering:** Retrieves authorized information and generates evidence-based responses.

The full architecture, including all 17 logical blocks and their interactions, is documented in:

[Architecture Overview](docs/architecture/overview.md)

[Shared System and 17-Block Diagrams](diagram.md)

[Project Owner Decision Register](docs/architecture/decisions/DECISION-REGISTER.md)

---

## 5. Technology Stack

The following technologies are proposed for the initial implementation.

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| Frontend | React, TypeScript |
| Agent Orchestration | LangGraph |
| Document Parsing | Docling |
| Embedding | BGE-M3 (Candidate) |
| Retrieval | Dense Search, BM25, RRF |
| Reranking | Multilingual Cross-Encoder |
| Vector Database | Qdrant |
| Relational Database | PostgreSQL |
| Caching | Redis |
| Infrastructure | Docker Compose |
| Observability | OpenTelemetry |
| Development Agents | OpenAI Codex |
| Version Control | Git |

Technology choices and versions may be refined during implementation.

---

## 6. Repository Structure

The repository separates application code, architecture documentation, agent configurations, and development coordination.

```text
enterprise-agentic-rag-harness/
│
├── README.md              # Project overview
├── GOALS.md               # Objectives and scope
├── AGENTS.md              # Shared development instructions
├── PLANS.md               # Development roadmap
├── PROMPTS.md             # Reusable development prompts
├── SECURITY.md            # Security guidelines
├── PROJECT_TREE.md        # Complete directory structure
│
├── .codex/                # Codex agent configurations
│
├── backend/               # Backend application
│
├── frontend/              # User and admin interfaces
│
├── docs/                  # Architecture and technical specifications
│
├── harness/               # Task coordination and agent handoffs
│
├── infra/                 # Infrastructure configuration
│
├── tests/                 # Testing and evaluation
│
└── scripts/               # Development utilities
```

Each directory has a clearly defined responsibility.

For the complete folder structure, see [PROJECT_TREE.md](PROJECT_TREE.md).

---

## 7. Getting Started

### Prerequisites

To explore and validate the current development harness, ensure the following tools are available:

- Git
- Python 3.11+
- OpenAI Codex
- A code editor or IDE

Additional services will be required as application development progresses.

### Step 1 — Open the Project

```bash
cd enterprise-agentic-rag-harness
```

### Step 2 — Validate the Harness

```bash
python3 scripts/validate_harness.py
```

### Step 3 — Start Codex

```bash
codex
```

### Step 4 — Initialize Development

Instruct Codex to read the project documentation and prepare the initial implementation plan.

```text
Read AGENTS.md, GOALS.md, PLANS.md,
docs/architecture/overview.md,
docs/contracts/README.md,
and harness/tasks/tasks.json.

Review the architecture and task dependencies.

Prepare the Phase 0 implementation plan.

Do not implement application code yet.
Do not commit, push, or merge.
```

> **Note:** The repository currently provides the development harness. Application runtime setup instructions will be added after the corresponding services are implemented.

---

## 8. Documentation Guide

The repository maintains separate documentation for architecture, security, implementation, and multi-agent coordination.

| Document | Purpose |
|---|---|
| [GOALS.md](GOALS.md) | Project objectives, scope, and requirements |
| [AGENTS.md](AGENTS.md) | Shared rules for Codex development agents |
| [PLANS.md](PLANS.md) | Development phases and milestones |
| [PROMPTS.md](PROMPTS.md) | Reusable Codex instructions |
| [SECURITY.md](SECURITY.md) | Security principles and policies |
| [PROJECT_TREE.md](PROJECT_TREE.md) | Complete repository structure |
| [Architecture Overview](docs/architecture/overview.md) | System architecture and logical blocks |
| [Shared Diagrams](diagram.md) | Overall system and 17-block Mermaid diagrams |
| [Decision Register](docs/architecture/decisions/DECISION-REGISTER.md) | Decisions requiring Project Owner input |
| [Architecture Blocks](docs/architecture/blocks/) | Detailed design of the 17 architecture blocks |
| [API Contracts](docs/contracts/) | Shared interfaces and communication contracts |
| [RAG Documentation](docs/rag/) | Retrieval and knowledge processing design |
| [Task Management](harness/tasks/) | Task tracking and dependencies |
| [Agent Handoffs](harness/handoffs/) | Agent collaboration and deliverables |
| [Multi-Agent Production Workflow](docs/operations/multi-agent-production-workflow.md) | Assignments, execution order and release gates |
| [Codex Configuration](.codex/) | Custom development agent configurations |
| [Testing Documentation](docs/testing/) | Testing strategy and evaluation |

### Recommended Reading Order

For new developers and Codex agents:

```text
README.md
    |
    v
GOALS.md
    |
    v
AGENTS.md
    |
    v
docs/architecture/overview.md
    |
    v
docs/contracts/
    |
    v
PLANS.md
    |
    v
harness/tasks/
    |
    v
Relevant Module Documentation
```

Agents should read additional documentation according to their assigned responsibilities.

---

**Enterprise Agentic RAG**

*Secure Knowledge. Intelligent Retrieval. Evidence-Based AI.*

**Architecture:** Modular Monolith + Advanced Hybrid RAG + LangGraph  
**Development Strategy:** Contract-First, Codex Multi-Agent Development  
**Current Phase:** Phase 0 — Architecture & Planning
