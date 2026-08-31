# INDUSAI-X — Sovereign On-Premise Agentic AI Workbench
**MRPL SIH26117 | Intelligence Backbone**

INDUSAI-X is an air-gappable, sovereign industrial AI workbench designed for Mangalore Refinery and Petrochemicals Limited (MRPL). It executes 100% locally with open-weight models, enforces retrieval-time permission boundaries, orchestrates industrial multi-agent workflows with LangGraph, and deploys a Hallucination Firewall to guarantee traceable, evidence-grounded conclusions.

---

## 1. Repository Structure

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
│   ├── agents/                    # Specialized industrial agents
│   │   ├── __init__.py
│   │   ├── planner.py             # Intent classification & workflow planning
│   │   ├── rag_agent.py           # Permission-filtered RAG & self-healing re-retrieval
│   │   ├── investigation_agent.py # Multi-source correlation across reports
│   │   └── engineering_agent.py   # Industrial parameter limits verification
│   │
│   ├── graph/                     # LangGraph workflow orchestration
│   │   ├── __init__.py
│   │   ├── state.py               # TypedDict AgentState
│   │   ├── workflow.py            # Compiled multi-agent StateGraph
│   │   └── routes.py              # FastAPI agent endpoints
│   │
│   ├── rag/                       # Sovereign local RAG pipeline
│   │   ├── __init__.py
│   │   ├── ingestion.py           # Section-aware PDF/DOCX parser
│   │   ├── chunking.py            # Table- & section-preserving chunker
│   │   ├── embeddings.py          # Local SentenceTransformers / Ollama service
│   │   ├── chroma_store.py        # Persistent ChromaDB vector store
│   │   ├── retrieval.py           # Permission filter, reranker, query expander
│   │   └── evidence.py            # Standard Evidence & EvidencePack models
│   │
│   ├── verification/              # Hallucination Firewall
│   │   ├── __init__.py
│   │   ├── claim_extractor.py     # Atomic factual claim extraction
│   │   ├── verifier.py            # Claim NLI, contradiction & Causal Leap Downgrader
│   │   └── guardrails.py          # 5-section response formatter & human review router
│   │
│   └── main.py                    # FastAPI main entrypoint
│
├── tests/
│   ├── test_agents/
│   │   ├── test_planner.py
│   │   └── test_rag_agent.py
│   ├── test_rag/
│   │   ├── test_chunking.py
│   │   ├── test_embeddings.py
│   │   ├── test_evidence.py
│   │   └── test_retrieval.py
│   ├── test_verification/
│   │   ├── test_guardrails.py
│   │   └── test_causality.py
│   └── test_workflow.py
│
├── benchmark_embeddings.py        # Local embedding model benchmark suite
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

# 3. Run the automated test suite
pytest tests/ -v --cov=backend

# 4. Start the FastAPI local server
python -m uvicorn backend.main:app --reload
```

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
