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

A modular, high-performance, and production-grade **FastAPI backend spine** for the **INDUSAI-X** multi-agent industrial intelligence platform. 

This backend acts as the central orchestration, persistence, and audit layer integrating:
- **Member 4**: Local LLM Orchestration (Ollama / Llama-3-Industrial)
- **Member 5**: LangGraph Routing, Multi-Agent Coordination, and ChromaDB Hybrid RAG
- **Member 6**: Multi-Modal Ingestion (PyMuPDF, python-docx, DuckDB Telemetry, and P&ID Vision Analysis)

---

## Key Features & Architecture

- **High-Concurrency SQLite with WAL**: Configured with `PRAGMA journal_mode=WAL;`, `PRAGMA busy_timeout=5000;`, and `PRAGMA foreign_keys=ON;` to handle concurrent multi-agent and audit writes without database locking.
- **Forensic Audit Logging with Snapshotting**: Audit trail captures metadata snapshots (`workspace_name`, `file_name`) so that logs remain permanently intelligible even if parent workspaces or files are deleted.
- **True Async Query Orchestration**: Dispatches queries with immediate `202 Accepted` and `poll_url`, tracking sub-agent execution traces (`triage_agent` -> `document_agent` / `tabular_agent` / `vision_agent` -> `synthesis_agent`).
- **Magic-Byte Sniffing**: Inspects raw byte headers (`%PDF-`, `\x89PNG`, `\xFF\xD8\xFF`, `PK\x03\x04`, plain text) to block disguised executables and malicious files.
- **Startup Recovery Sweep**: Automatically detects and transitions any zombie queries left in `processing` on server restarts into `failed`.
- **Machine-to-Machine (M2M) Security**: Internal file indexing status callbacks protected via `X-Internal-Service-Key`.
- **Forensic Immutability for Citations**: Historical query citations preserve snippets and page references even if source documents are subsequently removed from disk.

---

## Directory Layout

```
c:\Users\aarfa\Clora\Clora\
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI app factory, CORS, startup recovery sweep, DB init
│   │   ├── api/
│   │   │   ├── router.py               # Aggregated API router
│   │   │   └── routes/
│   │   │       ├── health.py           # /health check
│   │   │       ├── workspace.py        # /api/workspaces CRUD
│   │   │       ├── file.py             # /api/workspaces/{id}/files, /api/files/{id}, /api/files/{id}/status (M2M protected)
│   │   │       ├── query.py            # /api/query (async 202 + debug sync), /api/query/{id} polling
│   │   │       └── audit.py            # /api/audit log queries with snapshot resolution
│   │   ├── core/
│   │   │   ├── config.py               # Pydantic Settings & environment variables
│   │   │   └── security.py             # User context resolver & M2M internal key validator
│   │   ├── db/
│   │   │   ├── database.py             # SQLite engine (WAL mode, busy_timeout, FKs) & SessionLocal
│   │   │   └── models.py               # SQLAlchemy models with cascade rules & audit independence
│   │   ├── schemas/
│   │   │   ├── common.py               # Standard response schemas & pagination
│   │   │   ├── workspace.py            # Workspace Pydantic schemas
│   │   │   ├── file.py                 # File & status update schemas
│   │   │   ├── query.py                # Query, citation, agent task execution schemas
│   │   │   └── audit.py                # Audit log response schemas with snapshot support
│   │   ├── services/
│   │   │   ├── audit_service.py        # Centralized audit logging helper with metadata snapshotting
│   │   │   ├── workspace_service.py    # Workspace business logic & disk cleanup
│   │   │   ├── file_service.py         # Magic-byte sniff, UUID disk storage, status updater
│   │   │   └── agent_service.py        # True async orchestrator (BackgroundTasks) & startup sweep
│   │   └── integrations/
│   │       ├── rag_client.py           # Interface + mock/HTTP wrapper for Member 5 ChromaDB RAG
│   │       ├── agent_client.py         # Interface + mock/HTTP wrapper for Member 4 & 5 LangGraph/Ollama
│   │       └── vision_client.py        # Interface + mock/HTTP wrapper for Member 6 Vision/P&ID
│   ├── storage/
│   │   ├── indusai.db                  # SQLite database (auto-created with WAL)
│   │   └── workspaces/                 # UUID-based storage per workspace
│   ├── tests/
│   │   ├── conftest.py                 # Isolated temp SQLite DB & TestClient fixtures
│   │   ├── test_health.py              # Health check test
│   │   ├── test_workspace.py           # Workspace CRUD & cascade delete tests
│   │   ├── test_file.py                # File upload, magic-byte sniff, path safety, status PATCH tests
│   │   ├── test_query.py               # Async query orchestration, background polling & citation tests
│   │   ├── test_concurrency.py         # Multi-query concurrent execution & SQLite WAL stress test
│   │   ├── test_audit.py               # Audit trail generation & snapshot permanence tests
│   │   └── test_e2e_scenario.py        # Pump P-101 Industrial demo scenario test
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .dockerignore
│   └── .env.example
├── docker-compose.yml                  # Container deployment with host.docker.internal
├── API_CONTRACTS.md                    # Frozen JSON integration contracts for M4, M5, M6
└── README.md
```

---

## Quickstart

### Option 1: Running with `uv` (Recommended)

```powershell
# Create virtual environment and install dependencies
uv venv .venv
.\.venv\Scripts\activate
uv pip install -r backend/requirements.txt

# Launch FastAPI backend server
uv run uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

### Option 2: Running with Docker Compose

```powershell
docker compose up --build
```

Access Interactive API Documentation:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Redoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- Health Check: [http://localhost:8000/health](http://localhost:8000/health)

---

## Running the Test Suite

Execute the comprehensive pytest suite including concurrent execution and the Pump P-101 industrial scenario:

```powershell
uv run pytest backend/tests -v
```

---

## API Summary & Key Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Application & database connectivity check |
| `POST` | `/api/workspaces` | Create new industrial workspace |
| `GET` | `/api/workspaces` | List workspaces with file & query counts |
| `GET` | `/api/workspaces/{id}` | Workspace details |
| `DELETE` | `/api/workspaces/{id}` | Cascade delete workspace & disk storage |
| `POST` | `/api/workspaces/{id}/files` | Ingest PDF, diagram, or telemetry file |
| `GET` | `/api/workspaces/{id}/files` | List ingested files in workspace |
| `GET` | `/api/files/{id}` | File metadata |
| `GET` | `/api/files/{id}/download` | Stream physical file from disk |
| `PATCH` | `/api/files/{id}/status` | M2M worker indexing callback (`X-Internal-Service-Key`) |
| `DELETE` | `/api/files/{id}` | Delete file record and wipe storage payload |
| `POST` | `/api/query` | Dispatch industrial investigation query (`202 Accepted`) |
| `GET` | `/api/query/{id}` | Poll query progress, tasks, answer & citations |
| `GET` | `/api/workspaces/{id}/queries` | Query history for workspace |
| `GET` | `/api/audit` | Query audit trail with snapshot resolution |
| `GET` | `/api/audit/{id}` | Detail for single audit entry |
