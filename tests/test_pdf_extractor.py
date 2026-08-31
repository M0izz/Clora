"""
Tests for PDF Extraction and OCR Fallback Engine.
"""

import os
import unittest
from data_intelligence.pdf_extractor import DocumentExtractor, reconstruct_table_from_ocr_data


class TestPdfExtractor(unittest.TestCase):

    def setUp(self):
        self.extractor = DocumentExtractor()
        self.digital_pdf = os.path.join("samples", "sample_inspection_digital.pdf")
        self.scanned_pdf = os.path.join("samples", "sample_inspection_scanned.pdf")

    def test_digital_pdf_extraction(self):
        self.assertTrue(os.path.exists(self.digital_pdf), "Digital test PDF must exist")
        res = self.extractor.extract(self.digital_pdf)

        self.assertEqual(res.primary_method, "native_text")
        self.assertGreater(res.total_pages, 0)
        self.assertIn("P-102A", res.full_text)
        self.assertIn("Crude Distillation Unit", res.full_text)
        self.assertGreater(len(res.chunks), 0)
        self.assertFalse(res.needs_human_review)

    def test_scanned_pdf_extraction_and_fallback(self):
        self.assertTrue(os.path.exists(self.scanned_pdf), "Scanned test PDF must exist")
        res = self.extractor.extract(self.scanned_pdf)

        self.assertEqual(res.primary_method, "ocr_fallback")
        self.assertGreater(res.total_pages, 0)
        self.assertEqual(len(res.pages), 1)
        self.assertTrue(res.pages[0].extraction_method == "ocr_fallback")

    def test_table_reconstruction_from_ocr_data(self):
        mock_ocr_data = {
            "text": ["Tag", "Parameter", "Status", "P-102A", "Vibration", "CRITICAL", "P-102B", "Vibration", "NORMAL"],
            "conf": [95, 90, 92, 94, 91, 89, 93, 90, 91],
            "left": [50, 150, 300, 50, 150, 300, 50, 150, 300],
            "top": [100, 102, 99, 130, 131, 129, 160, 159, 161],
            "width": [40, 80, 50, 40, 80, 60, 40, 80, 50],
            "height": [15, 15, 15, 15, 15, 15, 15, 15, 15]
        }
        tables = reconstruct_table_from_ocr_data(mock_ocr_data, y_tolerance=10.0)
        self.assertEqual(len(tables), 3)
        self.assertEqual(tables[0], ["Tag", "Parameter", "Status"])
        self.assertEqual(tables[1], ["P-102A", "Vibration", "CRITICAL"])
        self.assertEqual(tables[2], ["P-102B", "Vibration", "NORMAL"])


if __name__ == "__main__":
    unittest.main()
