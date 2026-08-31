# INDUSAI-X System Integration & API Contracts (Frozen Specification)

This document specifies the frozen JSON interfaces, communication protocols, status lifecycles, and machine-to-machine (M2M) authentication contracts between the **Backend Spine** and specialized member subsystems:
- **Member 4**: Local LLM Orchestration (Ollama / Llama-3-Industrial)
- **Member 5**: Multi-Agent Routing & Hybrid Retrieval (LangGraph, ChromaDB, RAG)
- **Member 6**: Multi-Modal Ingestion & Analytics (PyMuPDF, python-docx, DuckDB, Vision P&ID)

---

## 1. Machine-to-Machine (M2M) Authentication

All internal callbacks from background ingestion workers (Members 5 & 6) to the Backend Spine must include the secret internal header:

```http
X-Internal-Service-Key: <INTERNAL_SERVICE_KEY>
```

- **Default Development Secret**: `indusai-internal-worker-key-dev`
- **Rejection**: Requests without this header or with an invalid key return `403 Forbidden`.

---

## 2. Ingestion & Status Lifecycle Contracts (Member 5 & 6 <-> Backend)

### 2.1 Storage Path Convention
When a user uploads a file, the backend saves it under:
`storage/workspaces/{workspace_id}/{file_id}{extension}`

The backend sets `status: "uploaded"`.

### 2.2 Worker Status Callback
When Member 6 finishes text/tabular extraction or Member 5 finishes chunk embedding into ChromaDB, the worker updates file status:

**Endpoint**: `PATCH /api/files/{file_id}/status`  
**Headers**:
```http
Content-Type: application/json
X-Internal-Service-Key: indusai-internal-worker-key-dev
```

#### Payload (Transition to Processing):
```json
{
  "status": "processing"
}
```

#### Payload (Transition to Indexed):
```json
{
  "status": "indexed"
}
```

#### Payload (Transition to Failed):
```json
{
  "status": "failed",
  "error_message": "Corrupt raster layers in P&ID drawing"
}
```

---

## 3. Retrieval & Vector Search Contract (Member 5 <-> Backend)

### 3.1 Document Retrieval Request
When a query arrives, the backend calls Member 5's RAG server:

**Request**: `POST /retrieve`  
```json
{
  "workspace_id": "8f3b6183-4927-4f40-8ea7-b3dafb37286a",
  "question": "What caused pump P-101 bearing failure?",
  "top_k": 3
}
```

### 3.2 Document Retrieval Response
```json
{
  "workspace_id": "8f3b6183-4927-4f40-8ea7-b3dafb37286a",
  "chunks": [
    {
      "file_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "filename": "Pump_P101_Maintenance_Manual.pdf",
      "file_type": "pdf",
      "page": 42,
      "sheet_or_table": null,
      "snippet_or_data": "Section 4.3: Bearing Lubrication. Standard operating temperature for inboard bearing is 65°C-80°C. Prolonged operation above 95°C indicates coolant flow restriction or lubricant starvation.",
      "confidence": 0.94
    }
  ]
}
```

---

## 4. Vision & P&ID Diagram Contract (Member 6 <-> Backend)

### 4.1 Vision Inspection Request
**Request**: `POST /vision/analyze`  
```json
{
  "workspace_id": "8f3b6183-4927-4f40-8ea7-b3dafb37286a",
  "question": "What caused pump P-101 bearing failure?"
}
```

### 4.2 Vision Inspection Response
```json
{
  "workspace_id": "8f3b6183-4927-4f40-8ea7-b3dafb37286a",
  "citations": [
    {
      "file_id": "c3d4e5f6-a7b8-9012-cdef-345678901234",
      "filename": "PID_Cooling_Water_Circuit_P101.png",
      "file_type": "image",
      "page": 1,
      "sheet_or_table": "P&ID Sheet 2 / Grid D4",
      "snippet_or_data": "Identified Valve CV-104B on the lube oil heat exchanger return line. Manual isolation bypass valve V-109 was flagged in normally closed (NC) state.",
      "confidence": 0.96
    }
  ]
}
```

---

## 5. Multi-Modal Citation Schema

Every query response contains an immutable list of structured `sources`:

```json
[
  {
    "file_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "filename": "Pump_P101_Maintenance_Manual.pdf",
    "file_type": "pdf",
    "page": 42,
    "sheet_or_table": null,
    "snippet_or_data": "Section 4.3: Bearing Lubrication & Thermal Limits...",
    "confidence": 0.94,
    "file_available": true
  },
  {
    "file_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "filename": "Pump_P101_Vibration_Telemetry.csv",
    "file_type": "csv",
    "page": null,
    "sheet_or_table": "telemetry_timeseries",
    "snippet_or_data": {
      "row_range": "Rows 1420-1435",
      "excursion_variable": "inboard_bearing_temp_c",
      "peak_value": 104.2,
      "vibration_rms_peak": 9.82
    },
    "confidence": 0.98,
    "file_available": true
  },
  {
    "file_id": "c3d4e5f6-a7b8-9012-cdef-345678901234",
    "filename": "PID_Cooling_Water_Circuit_P101.png",
    "file_type": "image",
    "page": 1,
    "sheet_or_table": "P&ID Sheet 2 / Grid D4",
    "snippet_or_data": "Identified Valve CV-104B on the lube oil heat exchanger return line...",
    "confidence": 0.96,
    "file_available": true
  }
]
```

> **Forensic Immutability Rule**: If the source file is deleted after query completion, `file_available` is dynamically resolved to `false`, but the snippet text, page number, and data snapshot remain intact in the historical query record.

---

## 6. Query Polling Contract (`GET /api/query/{query_id}`)

### Statuses:
- `pending`: Query queued in background task list.
- `processing`: Specialized agents (triage, doc, tabular, vision, synthesis) currently executing.
- `completed`: Synthesis complete, response & citations available.
- `failed`: Query failed with descriptive `error_message`.

### Response Payload:
```json
{
  "query_id": "9a1b2c3d-4e5f-6789-0abc-def123456789",
  "status": "completed",
  "poll_url": "/api/query/9a1b2c3d-4e5f-6789-0abc-def123456789",
  "question": "What caused pump P-101 bearing failure?",
  "response": "### Industrial Root-Cause Analysis: Pump P-101 Bearing Failure\n\n...",
  "sources": [ ... ],
  "agent_tasks": [
    {
      "id": "task-uuid-1",
      "agent_name": "triage_agent",
      "input_data": { "question": "What caused pump P-101 bearing failure?" },
      "output_data": { "intent": "ROOT_CAUSE_FAILURE_ANALYSIS" },
      "status": "completed",
      "created_at": "2026-08-31T12:00:00Z",
      "completed_at": "2026-08-31T12:00:01Z"
    },
    {
      "id": "task-uuid-2",
      "agent_name": "document_agent",
      "status": "completed",
      "created_at": "2026-08-31T12:00:01Z",
      "completed_at": "2026-08-31T12:00:02Z"
    },
    {
      "id": "task-uuid-3",
      "agent_name": "tabular_agent",
      "status": "completed",
      "created_at": "2026-08-31T12:00:02Z",
      "completed_at": "2026-08-31T12:00:03Z"
    },
    {
      "id": "task-uuid-4",
      "agent_name": "vision_agent",
      "status": "completed",
      "created_at": "2026-08-31T12:00:03Z",
      "completed_at": "2026-08-31T12:00:04Z"
    },
    {
      "id": "task-uuid-5",
      "agent_name": "synthesis_agent",
      "status": "completed",
      "created_at": "2026-08-31T12:00:04Z",
      "completed_at": "2026-08-31T12:00:05Z"
    }
  ],
  "created_at": "2026-08-31T12:00:00Z",
  "completed_at": "2026-08-31T12:00:05Z",
  "error_message": null
}
```
