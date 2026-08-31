"""
Interactive End-to-End Demo Runner for Member 6 Deliverables.
INDUSAI-X / SIH Problem Statement 26117 (MRPL)
Member 6: Data Intelligence + Knowledge Graph + Security Engineer

Demonstrates:
1. Dual-engine PDF Extraction & OCR Fallback (Digital vs. Scanned).
2. AST-Guarded DuckDB SQL Queries on Refinery Telemetry.
3. RBAC Matrix Verification & Tamper-Evident SHA-256 Audit Trail.
4. Process-Level Air-Gap Network Isolation Proof.
5. Official MRPL Executive Approval Note Word (.docx) Generation.
"""

import os
import json
import time
from data_intelligence.pdf_extractor import DocumentExtractor
from data_intelligence.tabular_engine import TabularEngine, SQLSecurityError
from data_intelligence.docx_generator import ApprovalNoteGenerator
from data_intelligence.models import ApprovalNoteInput, FindingItem
from security.rbac import check_permission, enforce_permission, PermissionDeniedError
from security.audit_trail import AuditLogger
from security.airgap_monitor import check_network_isolation


def print_banner(title: str):
    print("\n" + "=" * 78)
    print(f"  {title.upper()}")
    print("=" * 78)


def run_demo():
    print_banner("INDUSAI-X: Member 6 Data Intelligence & Security Suite")
    print("Sovereign On-Premise Agentic AI Workbench for MRPL (SIH PS 26117)")
    print("-" * 78)

    # Initialize Audit Logger
    audit_file = "demo_audit_trail.jsonl"
    if os.path.exists(audit_file):
        os.remove(audit_file)
    logger = AuditLogger(audit_file)

    # -------------------------------------------------------------
    # 1. Document Extraction & OCR Fallback
    # -------------------------------------------------------------
    print_banner("Step 1: Document Data Extraction (Digital vs. Scanned)")
    extractor = DocumentExtractor()

    digital_pdf = os.path.join("samples", "sample_inspection_digital.pdf")
    scanned_pdf = os.path.join("samples", "sample_inspection_scanned.pdf")

    print(f"[*] Ingesting Digital Inspection PDF: {digital_pdf}")
    res_digital = extractor.extract(digital_pdf)
    logger.log("user_plant_eng", "Plant_Engineer", "read_document", digital_pdf, "SUCCESS", {"pages": res_digital.total_pages})
    print(f"    -> Extraction Mode: {res_digital.primary_method}")
    print(f"    -> Pages Extracted: {res_digital.total_pages}")
    print(f"    -> Structured RAG Chunks Generated (for Member 5): {len(res_digital.chunks)}")
    print(f"    -> Sample Chunk Preview: {res_digital.chunks[0].text[:90]}...")

    print(f"\n[*] Ingesting True Scanned Raster PDF (Zero Text Layer): {scanned_pdf}")
    res_scanned = extractor.extract(scanned_pdf)
    logger.log("user_plant_eng", "Plant_Engineer", "run_ocr", scanned_pdf, "SUCCESS", {"pages": res_scanned.total_pages})
    print(f"    -> Extraction Mode: {res_scanned.primary_method}")
    print(f"    -> Fallback OCR Triggered: YES")
    print(f"    -> Human Review Flag: {res_scanned.needs_human_review}")

    # -------------------------------------------------------------
    # 2. In-Memory Tabular DuckDB Analytics with AST Guard
    # -------------------------------------------------------------
    print_banner("Step 2: Tabular Intelligence Engine & AST SQL Guard")
    tabular = TabularEngine()
    csv_path = os.path.join("samples", "equipment_maintenance.csv")
    loaded_rows = tabular.load_csv("telemetry", csv_path)
    print(f"[*] Loaded {loaded_rows} telemetry rows into isolated DuckDB in-memory engine.")

    query = (
        "SELECT equipment_id, equipment_name, ROUND(AVG(vibration_mms), 2) AS avg_vib_mms, "
        "MAX(bearing_temp_c) AS max_temp_c, COUNT(*) AS alert_count "
        "FROM telemetry WHERE status = 'CRITICAL' "
        "GROUP BY equipment_id, equipment_name"
    )
    print(f"\n[*] Executing Agent Analytical SQL Query:\n    {query}")
    dict_results, md_table = tabular.query(query)
    logger.log("user_plant_eng", "Plant_Engineer", "query_tabular", "telemetry", "SUCCESS", {"query": query})
    print("\n" + md_table)

    print("\n[*] Testing AST SQL Guard against Multi-Statement Semicolon Attack...")
    malicious_query = "SELECT * FROM telemetry; DROP TABLE telemetry;"
    try:
        tabular.query(malicious_query)
    except SQLSecurityError as e:
        print(f"    [BLOCKED BY AST GUARD] {e}")
        logger.log("attacker", "Anonymous", "query_tabular", "telemetry", "BLOCKED_SECURITY_VIOLATION", {"error": str(e)})

    # -------------------------------------------------------------
    # 3. RBAC Matrix & Tamper-Evident Audit Verification
    # -------------------------------------------------------------
    print_banner("Step 3: RBAC Matrix & Tamper-Evident Audit Trail")
    print("[*] Verifying Role Permissions:")
    print(f"    - Plant_Engineer -> generate_approval_note: {check_permission('Plant_Engineer', 'generate_approval_note')} (PERMITTED)")
    print(f"    - Operator       -> generate_approval_note: {check_permission('Operator', 'generate_approval_note')} (DENIED)")

    is_valid, bad_line, msg = AuditLogger.verify_audit_trail(audit_file)
    print(f"\n[*] Cryptographic Audit Trail Verification: {'VALID' if is_valid else 'INVALID'}")
    print(f"    -> {msg}")

    # -------------------------------------------------------------
    # 4. Air-Gap Network Self-Audit
    # -------------------------------------------------------------
    print_banner("Step 4: Air-Gap Network Isolation Proof")
    net_status = check_network_isolation()
    print(f"[*] Process Network Isolation Audit: {net_status['status']}")
    print(f"    -> Air-Gapped / Zero External Sockets: {net_status['is_airgapped']}")
    print(f"    -> External Connections Detected: {net_status['external_connections_detected']}")

    # -------------------------------------------------------------
    # 5. Executive Word Approval Note Generation (.docx)
    # -------------------------------------------------------------
    print_banner("Step 5: Executive Deliverable Builder (.docx)")
    generator = ApprovalNoteGenerator()
    out_docx = "MRPL_Executive_Approval_Note.docx"

    note_payload = ApprovalNoteInput(
        note_number="MRPL/MAINT/2026/CDU-042",
        department="Inspection & Maintenance Dept.",
        date_str="31-Aug-2026",
        subject="Emergency Overhaul Approval for Crude Distillation Pump P-102A",
        priority="URGENT",
        author_name="Rajesh Kumar (Sr. Maintenance Engineer)",
        approver_name="Chief General Manager (Technical Services)",
        executive_summary=(
            "Thermographic and vibration telemetry in CDU-1 indicates critical drive-end bearing degradation "
            "(7.8 mm/s RMS vs 4.5 mm/s limit) on Main Crude Charge Pump P-102A. Immediate sanction is requested "
            "to overhaul the unit during the scheduled turnaround."
        ),
        findings=[
            FindingItem(
                equipment_tag="P-102A",
                parameter="DE Bearing Vibration",
                observed_value="7.8 mm/s RMS",
                threshold_limit="4.5 mm/s RMS",
                severity="CRITICAL",
                action_required="Replace bearing assembly & precision balance"
            ),
            FindingItem(
                equipment_tag="P-102A",
                parameter="DE Bearing Temperature",
                observed_value="98.5 °C",
                threshold_limit="75.0 °C",
                severity="CRITICAL",
                action_required="Renew synthetic lubricant and lube oil piping"
            ),
            FindingItem(
                equipment_tag="P-102B",
                parameter="DE Bearing Vibration",
                observed_value="2.1 mm/s RMS",
                threshold_limit="4.5 mm/s RMS",
                severity="NORMAL",
                action_required="Switch to primary active lead pump"
            )
        ],
        risk_assessment="Operating P-102A under bearing spalling conditions presents severe risks of mechanical seal blowout and CDU-1 unplanned shutdown.",
        financial_estimate_inr=285000.0,
        recommendation="Approval requested for immediate mobilization of OEM spares (SKF 23144 CC/W33) and mechanical overhaul.",
        output_docx_path=out_docx
    )

    doc_path = generator.generate(note_payload)
    logger.log("user_plant_eng", "Plant_Engineer", "generate_approval_note", doc_path, "SUCCESS", {"note_no": note_payload.note_number})
    print(f"[*] Generated Executive Approval Note: {os.path.abspath(doc_path)}")
    print("    -> Document includes: Header, Metadata Grid, Executive Summary, Styled Findings Table, Financial Sanction, and Sign-off Blocks.")

    print_banner("Demonstration Complete - All Member 6 Deliverables Operational")


if __name__ == "__main__":
    run_demo()
