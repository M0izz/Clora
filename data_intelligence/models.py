"""
Data Intelligence Models and Contract Specifications.
INDUSAI-X / SIH Problem Statement 26117 (MRPL)
Member 6: Data Intelligence + Knowledge Graph + Security Engineer

Provides formal integration contracts for:
- Member 5 (RAG Engine): DocumentExtractionResult, PageExtraction, DocumentChunk
- Member 3 (Agent Orchestrator): MEMBER3_TOOL_DEFINITIONS, Flattened Tool Call Payloads
- Deliverable Builder: ApprovalNoteInput, FindingItem
"""

import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional


@dataclass
class DocumentChunk:
    """Structured chunk for Member 5 Vector Embedding & RAG ingestion."""
    chunk_id: str                              # e.g., "DOC001_P1_C0"
    page_number: int                           # 1-indexed
    block_type: str                            # 'header' | 'paragraph' | 'table' | 'ocr_block'
    heading_level: Optional[int]               # 1 for H1, 2 for H2, None for body text
    text: str                                  # Clean chunk content
    char_offset_start: int                     # Character start offset in page
    char_offset_end: int                       # Character end offset in page
    bbox: List[float] = field(default_factory=list)  # [x0, y0, x1, y1] coordinates
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PageExtraction:
    """Standardized page-level extraction output."""
    page_number: int                           # 1-indexed
    text: str                                  # Aggregated clean text (native + OCR)
    char_count: int                            # Character count
    extraction_method: str                     # 'native_text' | 'ocr_fallback' | 'hybrid'
    tables: List[List[List[str]]] = field(default_factory=list)   # List of 2D string matrices
    blocks: List[Dict[str, Any]] = field(default_factory=list)    # Bounding boxes
    chunks: List[DocumentChunk] = field(default_factory=list)     # Ready-to-embed chunks for Member 5
    ocr_confidence: Optional[float] = None     # Mean OCR confidence (0.0 to 100.0)
    needs_human_review: bool = False           # True if OCR confidence < 60% or anomalous extraction


@dataclass
class DocumentExtractionResult:
    """Document-level extraction output contract for Member 5 (RAG Pipeline)."""
    document_id: str                           # Unique SHA-256 or UUID of the document
    filename: str                              # Filename e.g., 'crude_pump_inspection.pdf'
    file_path: str                             # Absolute or relative path
    total_pages: int                           # Total number of pages
    primary_method: str                        # 'native_text' | 'ocr_fallback' | 'hybrid'
    metadata: Dict[str, Any]                   # PDF metadata (author, title, creation_date, dimensions)
    pages: List[PageExtraction] = field(default_factory=list)
    chunks: List[DocumentChunk] = field(default_factory=list)      # Aggregated chunks across all pages
    full_text: str = ""                        # Concatenated text of all pages
    needs_human_review: bool = False           # True if any page requires review

    def to_dict(self) -> Dict[str, Any]:
        """Convert extraction result to a serializable dictionary."""
        return asdict(self)

    def to_json(self, output_path: Optional[str] = None, indent: int = 2) -> str:
        """Export extraction result to JSON string or write directly to a file."""
        json_str = json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(json_str)
        return json_str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentExtractionResult":
        """Deserialize from dictionary."""
        data_copy = dict(data)
        pages_data = data_copy.pop("pages", [])
        chunks_data = data_copy.pop("chunks", [])

        pages = []
        for p in pages_data:
            p_chunks = [DocumentChunk(**c) for c in p.pop("chunks", [])]
            pages.append(PageExtraction(chunks=p_chunks, **p))

        chunks = [DocumentChunk(**c) for c in chunks_data]
        return cls(pages=pages, chunks=chunks, **data_copy)


@dataclass
class FindingItem:
    """Structured equipment finding item for reporting."""
    equipment_tag: str                         # e.g., "P-102A"
    parameter: str                             # e.g., "Bearing Vibration (DE)"
    observed_value: str                        # e.g., "7.8 mm/s RMS"
    threshold_limit: str                       # e.g., "4.5 mm/s RMS"
    severity: str                              # "CRITICAL" | "WARNING" | "NORMAL"
    action_required: str                       # e.g., "Immediate overhaul"


@dataclass
class ApprovalNoteInput:
    """Contract for generating boardroom-ready MRPL/PSU Approval Notes."""
    note_number: str                           # e.g., "MRPL/MAINT/2026/CDU-042"
    department: str                            # e.g., "Inspection & Maintenance Dept."
    date_str: str                              # e.g., "31-Aug-2026"
    subject: str                               # e.g., "Approval for Emergency Overhaul of CDU Charge Pump P-102A"
    priority: str                              # "HIGH" | "URGENT" | "ROUTINE"
    author_name: str                           # e.g., "Rajesh Kumar (Senior Maintenance Engineer)"
    approver_name: str                         # e.g., "Chief General Manager (Technical Services)"
    executive_summary: str
    findings: List[FindingItem] = field(default_factory=list)
    risk_assessment: str = ""
    financial_estimate_inr: float = 0.0
    recommendation: str = ""
    output_docx_path: str = "approval_note.docx"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ApprovalNoteInput":
        """Construct from dictionary with automatic findings translation."""
        data_copy = dict(data)
        findings_raw = data_copy.pop("findings", [])
        findings = []
        for f in findings_raw:
            if isinstance(f, FindingItem):
                findings.append(f)
            elif isinstance(f, dict):
                findings.append(FindingItem(**f))
        return cls(findings=findings, **data_copy)


# Member 3 Agent Orchestrator Tool Definitions
# Flattened top-level parameters ensure open-weight models (Qwen, Llama via Ollama) never fail JSON schema parsing
MEMBER3_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "extract_document_data",
            "description": "Extracts structured text, RAG chunks, metadata, and tables from digital or scanned PDF inspection reports.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pdf_path": {
                        "type": "string",
                        "description": "File path to the PDF document to extract."
                    }
                },
                "required": ["pdf_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_tabular_data",
            "description": "Executes a safe, read-only SQL query against in-memory refinery equipment/telemetry datasets.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql_query": {
                        "type": "string",
                        "description": "Read-only SQL SELECT statement to query telemetry/equipment data."
                    }
                },
                "required": ["sql_query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_approval_note",
            "description": "Generates a styled, executive-ready MRPL formatted Word (.docx) approval note from structured parameters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "note_number": {
                        "type": "string",
                        "description": "Official note reference number (e.g., 'MRPL/MAINT/2026/042')"
                    },
                    "department": {
                        "type": "string",
                        "description": "Originating department (e.g., 'Inspection & Maintenance Dept.')"
                    },
                    "date_str": {
                        "type": "string",
                        "description": "Date string (e.g., '31-Aug-2026')"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Subject of the approval note"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["ROUTINE", "HIGH", "URGENT"],
                        "description": "Priority level of the note"
                    },
                    "author_name": {
                        "type": "string",
                        "description": "Name and designation of authoring engineer"
                    },
                    "approver_name": {
                        "type": "string",
                        "description": "Name and designation of target approving authority"
                    },
                    "executive_summary": {
                        "type": "string",
                        "description": "Executive summary of the issue and technical context"
                    },
                    "findings_summary": {
                        "type": "string",
                        "description": "Summary of findings or semicolon-separated findings items"
                    },
                    "risk_assessment": {
                        "type": "string",
                        "description": "Risk analysis and potential operational impact"
                    },
                    "financial_estimate_inr": {
                        "type": "number",
                        "description": "Estimated financial budget required in INR"
                    },
                    "recommendation": {
                        "type": "string",
                        "description": "Specific action requested for executive sign-off"
                    },
                    "output_docx_path": {
                        "type": "string",
                        "description": "Destination file path for the generated .docx file"
                    }
                },
                "required": ["note_number", "department", "subject", "executive_summary", "recommendation"]
            }
        }
    }
]
