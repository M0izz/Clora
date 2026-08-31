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
