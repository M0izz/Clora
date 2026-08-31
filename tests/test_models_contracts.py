"""
Tests for Data Intelligence Models and Member 5 & 3 Contracts.
"""

import unittest

from data_intelligence.models import (
    MEMBER3_TOOL_DEFINITIONS,
    ApprovalNoteInput,
    DocumentChunk,
    DocumentExtractionResult,
    PageExtraction,
)


class TestModelsAndContracts(unittest.TestCase):

    def test_document_extraction_result_serialization(self):
        chunk = DocumentChunk(
            chunk_id="DOC1_P1_C0",
            page_number=1,
            block_type="header",
            heading_level=1,
            text="1. Executive Summary",
            char_offset_start=0,
            char_offset_end=20,
            bbox=[10.0, 10.0, 200.0, 30.0]
        )
        page = PageExtraction(
            page_number=1,
            text="1. Executive Summary\nPump failure imminent.",
            char_count=43,
            extraction_method="native_text",
            tables=[[["Col1", "Col2"], ["Val1", "Val2"]]],
            blocks=[{"bbox": [10.0, 10.0, 200.0, 30.0], "text": "1. Executive Summary"}],
            chunks=[chunk],
            ocr_confidence=None,
            needs_human_review=False
        )
        doc = DocumentExtractionResult(
            document_id="DOC1",
            filename="inspection.pdf",
            file_path="/data/inspection.pdf",
            total_pages=1,
            primary_method="native_text",
            metadata={"title": "Audit Report"},
            pages=[page],
            chunks=[chunk],
            full_text="1. Executive Summary\nPump failure imminent.",
            needs_human_review=False
        )

        doc_dict = doc.to_dict()
        self.assertEqual(doc_dict["document_id"], "DOC1")
        self.assertEqual(len(doc_dict["pages"]), 1)
        self.assertEqual(len(doc_dict["chunks"]), 1)

        # Test JSON round-trip
        json_str = doc.to_json()
        self.assertIn("DOC1_P1_C0", json_str)

        doc_recovered = DocumentExtractionResult.from_dict(doc_dict)
        self.assertEqual(doc_recovered.document_id, "DOC1")
        self.assertEqual(doc_recovered.pages[0].chunks[0].chunk_id, "DOC1_P1_C0")

    def test_approval_note_input_adapter(self):
        flat_data = {
            "note_number": "MRPL/MAINT/001",
            "department": "Mechanical",
            "date_str": "31-Aug-2026",
            "subject": "Seal Replacement",
            "priority": "HIGH",
            "author_name": "Engineer A",
            "approver_name": "Manager B",
            "executive_summary": "Seal leak detected.",
            "findings": [
                {
                    "equipment_tag": "P-101",
                    "parameter": "Vibration",
                    "observed_value": "5.0 mm/s",
                    "threshold_limit": "4.5 mm/s",
                    "severity": "WARNING",
                    "action_required": "Inspect seal"
                }
            ],
            "financial_estimate_inr": 50000.0,
            "recommendation": "Approve repair"
        }
        note = ApprovalNoteInput.from_dict(flat_data)
        self.assertEqual(note.note_number, "MRPL/MAINT/001")
        self.assertEqual(len(note.findings), 1)
        self.assertEqual(note.findings[0].severity, "WARNING")

    def test_member3_tool_definitions(self):
        self.assertEqual(len(MEMBER3_TOOL_DEFINITIONS), 3)
        tool_names = [t["function"]["name"] for t in MEMBER3_TOOL_DEFINITIONS]
        self.assertIn("extract_document_data", tool_names)
        self.assertIn("query_tabular_data", tool_names)
        self.assertIn("generate_approval_note", tool_names)


if __name__ == "__main__":
    unittest.main()
