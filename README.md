# INDUSAI-X: Sovereign On-Premise Agentic AI Workbench
**Smart India Hackathon (SIH 2026) — Problem Statement 26117**  
**Organization:** Mangalore Refinery and Petrochemicals Limited (MRPL)  
**Theme:** Smart Automation (Confidential Industrial Work)

---

## 🛠️ Member 6 Package: Data Intelligence + Knowledge Graph + Security Suite

This repository contains the complete Member 6 subsystem providing document intelligence, safe tabular SQL querying, knowledge graph reasoning, deliverable generation, and cryptographic air-gap verification.

---

## 📂 Project Structure

```
SIH_project/
├── data_intelligence/
│   ├── __init__.py
│   ├── models.py                 # Pydantic & Dataclass contracts for Member 5 & Member 3
│   ├── pdf_extractor.py          # PyMuPDF + OCR fallback + table reconstruction engine
│   ├── tabular_engine.py         # DuckDB in-memory engine with AST-level SQL security guard
│   ├── knowledge_graph.py        # NetworkX refinery asset topology & blast radius reasoning
│   ├── docx_generator.py         # Official MRPL Executive Approval Note Word builder
│   └── api_router.py             # FastAPI REST endpoints for UI and Agent orchestration
├── security/
│   ├── __init__.py
│   ├── rbac.py                   # 5-Role permission matrix enforcement
│   ├── audit_trail.py            # Thread-safe SHA-256 chained JSONL tamper-evident logger
│   ├── airgap_monitor.py         # Process socket inspection for zero WAN connections
│   └── network_proof.py          # Continuous network sentinel & sovereignty certificate generator
├── samples/
│   ├── __init__.py
│   ├── generate_sample_data.py   # Dataset generator (digital PDF, true scanned PDF, CSV)
│   ├── sample_inspection_digital.pdf
│   ├── sample_inspection_scanned.pdf
│   └── equipment_maintenance.csv
├── tests/
│   ├── test_models_contracts.py
│   ├── test_pdf_extractor.py
│   ├── test_tabular_engine.py
│   ├── test_knowledge_graph.py
│   ├── test_docx_generator.py
│   ├── test_security_audit.py
│   ├── test_network_proof.py
│   └── test_api_router.py
├── demo_runner.py                # End-to-end interactive CLI showcase
└── requirements.txt
```

---

## 🚀 Quickstart & Verification

### 1. Run Automated Test Suite (34 Tests)
```bash
python -m pytest tests/ -v
```

### 2. Run Interactive End-to-End Demo
```bash
python demo_runner.py
```

### 3. Generate New Sample Data
```bash
python samples/generate_sample_data.py
```

---

## 🔒 Security & Air-Gap Compliance
- **In-Memory SQL Guard**: Blocks multi-statement injection and restricts execution strictly to `SELECT` / `WITH` AST nodes with `enable_external_access=false`.
- **Tamper-Evident Audit Logging**: Cryptographically links all actions via SHA-256 hash chaining (`prev_hash` $\to$ `entry_hash`) with automated integrity verification.
- **Air-Gap Network Proof**: Generates certified `SOVEREIGNTY_AIRGAP_CERTIFICATE.txt` proving 0 external outbound sockets were opened.
# INDUSAI-X Industrial Intelligence Platform — Backend Spine
# INDUSAI-X — Sovereign On-Premise Agentic AI Workbench
**MRPL SIH26117 | Sovereign Industrial Intelligence Platform**

INDUSAI-X is an air-gappable, sovereign industrial AI workbench designed for Mangalore Refinery and Petrochemicals Limited (MRPL). It executes 100% locally with open-weight models, enforces retrieval-time permission boundaries, orchestrates industrial multi-agent workflows with LangGraph, and deploys a Hallucination Firewall to guarantee traceable, evidence-grounded conclusions.

---

## 1. Unified Repository Architecture

```
INDUSAI-X/
│
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                 # Ruff linting & MyPy type-checking
│   │   ├── tests.yml              # Automated pytest & coverage suite
│   │   └── pr-checks.yml          # Pull request validation
│   └── pull_request_template.md   # Standardized PR checklist
│
├── backend/
│   ├── app/                       # FastAPI Web & Persistence Layer (Spine)
│   │   ├── main.py                # FastAPI app factory, CORS, startup sweep
│   │   ├── api/routes/            # Workspaces, Files, Queries, Audits, Health
│   │   ├── core/                  # Configuration & security context
│   │   ├── db/                    # SQLite WAL database & SQLAlchemy models
│   │   ├── schemas/               # Pydantic request/response schemas
│   │   ├── services/              # Audit, Workspace, File, and Agent services
│   │   └── integrations/          # Clients connecting to RAG, Agents, and Vision
│   │
│   ├── agents/                    # Multi-Agent Intelligence Core
│   │   ├── __init__.py
│   │   ├── planner.py             # Intent classification & workflow planning
│   │   ├── rag_agent.py           # Permission-filtered RAG & self-healing re-retrieval
│   │   ├── investigation_agent.py # Multi-source correlation across reports
│   │   └── engineering_agent.py   # Industrial parameter limits verification
│   │
│   ├── graph/                     # LangGraph Workflow Orchestration
│   │   ├── __init__.py
│   │   ├── state.py               # TypedDict AgentState
│   │   ├── workflow.py            # Compiled multi-agent StateGraph
│   │   └── routes.py              # FastAPI agent endpoints
│   │
│   ├── rag/                       # Sovereign Local RAG Pipeline
│   │   ├── __init__.py
│   │   ├── ingestion.py           # Section-aware PDF/DOCX parser
│   │   ├── chunking.py            # Table- & section-preserving chunker
│   │   ├── embeddings.py          # Local SentenceTransformers / Ollama service
│   │   ├── chroma_store.py        # Persistent ChromaDB vector store
│   │   ├── retrieval.py           # Permission filter, reranker, query expander
│   │   └── evidence.py            # Standard Evidence & EvidencePack models
│   │
│   └── verification/              # Hallucination Firewall & Causality Guard
│       ├── __init__.py
│       ├── claim_extractor.py     # Atomic factual claim extraction
│       ├── verifier.py            # Claim NLI, contradiction & Causal Leap Downgrader
│       └── guardrails.py          # 5-section response formatter & human review router
│
├── tests/                         # Full automated test suites
│   ├── test_agents/
│   ├── test_rag/
│   ├── test_verification/
│   └── test_workflow.py
│
├── benchmark_embeddings.py        # Local embedding model benchmark suite
├── demo.py                        # End-to-end demonstration script
├── docker-compose.yml             # Containerized local deployment
├── API_CONTRACTS.md               # Frozen JSON integration contracts
├── requirements.txt               # Production dependencies
├── requirements-dev.txt           # Development & testing dependencies
├── pyproject.toml                 # Packaging & tool configurations
└── README.md                      # Project documentation
```

---

## 2. Quickstart & Installation

```bash
# 1. Clone the repository
git clone https://github.com/MRPL-SIH/INDUSAI-X.git
cd INDUSAI-X

# 2. Install dependencies
pip install -r requirements-dev.txt

# 3. Run all automated test suites
pytest tests/ -v --cov=backend

# 4. Start the FastAPI local server
python -m uvicorn backend.app.main:app --reload
```

Interactive Documentation:
- Swagger UI: `http://localhost:8000/docs`
- Redoc: `http://localhost:8000/redoc`

---

## 3. GitHub Actions CI/CD Pipeline

Every Pull Request automatically triggers:
1. **Automated Unit Tests & Coverage**: Executes all test suites across Python 3.11/3.14.
2. **Ruff Linting**: Enforces strict Python code style.
3. **MyPy Type Safety**: Validates type hints across the entire backend.

---

## 4. Key Engineering Guarantees

1. **Zero External API Calls**: All embeddings and reasoning run on local models (SentenceTransformers, Ollama).
2. **Retrieval-Time RBAC**: Chunks are filtered by `allowed_roles` before text ever reaches an LLM prompt.
3. **Self-Healing Retrieval**: 1-hop query expansion expands colloquial terms (e.g. *booster pump* $\leftrightarrow$ `P-101`) and gracefully terminates if evidence is absent.
4. **Causal Leap Guard**: Automatically detects unsupported causal assertions and hedges findings to prevent overclaiming.
