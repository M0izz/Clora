"""
Sample Data Generator for INDUSAI-X / SIH Problem Statement 26117.
Generates:
1. sample_inspection_digital.pdf - Native digital PDF with text layers & tables.
2. sample_inspection_scanned.pdf - True scanned PDF (flat raster images, 0 text layer).
3. equipment_maintenance.csv - 60+ rows of realistic refinery equipment telemetry.
"""

import os
import io
import random
import pandas as pd
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFilter
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_digital_pdf(output_path: str) -> str:
    """Generates a digitally-native industrial inspection report with selectable text and tables."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#003366'),
        spaceAfter=10
    )
    h2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#002244'),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#222222'),
        spaceAfter=6
    )

    story = []

    # Title & Header
    story.append(Paragraph("MANGALORE REFINERY AND PETROCHEMICALS LIMITED (MRPL)", title_style))
    story.append(Paragraph("<b>PLANT TECHNICAL AUDIT & VIBRATION INSPECTION REPORT</b>", h2_style))
    story.append(Spacer(1, 8))

    # Meta Table
    meta_data = [
        ["Report No:", "MRPL/INSP/2026/CDU-042", "Inspection Date:", "31-Aug-2026"],
        ["Plant Unit:", "Crude Distillation Unit-1 (CDU-1)", "Lead Inspector:", "R. K. Sharma (Sr. Insp. Eng.)"],
        ["Asset Group:", "Primary Hydrocarbon Pumps", "Status:", "ACTION REQUIRED - SEVERE"]
    ]
    meta_table = Table(meta_data, colWidths=[100, 170, 100, 170])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F0F4F8')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#111111')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # Section 1: Executive Summary
    story.append(Paragraph("1. Executive Summary", h2_style))
    story.append(Paragraph(
        "During routine thermographic and vibration screening in CDU-1 on 31-Aug-2026, severe abnormal vibration "
        "and elevated drive-end bearing temperatures were detected on Main Crude Charge Pump <b>P-102A</b>. "
        "Spectral analysis indicates progressive bearing inner-race spalling and impending mechanical seal failure. "
        "Immediate controlled shutdown and overhaul are required to prevent catastrophic hydrocarbon leakage.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # Section 2: Detailed Equipment Findings Table
    story.append(Paragraph("2. Equipment Inspection Findings", h2_style))
    findings_data = [
        ["Tag", "Equipment Name", "Observed Parameter", "Recorded", "Threshold", "Severity", "Action"],
        ["P-102A", "Crude Charge Pump A", "DE Bearing Vibration", "7.8 mm/s", "4.5 mm/s", "CRITICAL", "Immediate Overhaul"],
        ["P-102A", "Crude Charge Pump A", "DE Bearing Temp", "98.5 °C", "75.0 °C", "CRITICAL", "Replace Bearing"],
        ["P-102B", "Crude Charge Pump B (Standby)", "DE Bearing Vibration", "2.1 mm/s", "4.5 mm/s", "NORMAL", "Switch to Lead"],
        ["V-104", "Atmospheric Column Feed Valve", "Stem Leakage Rate", "0.02 L/hr", "0.01 L/hr", "WARNING", "Re-pack Gland"],
        ["E-101", "Crude Pre-heat Exchanger", "Differential Pressure", "1.4 bar", "1.8 bar", "NORMAL", "Continue Monitor"]
    ]
    findings_table = Table(findings_data, colWidths=[55, 125, 105, 55, 55, 60, 85])
    findings_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#94A3B8')),
        ('BACKGROUND', (5, 1), (5, 2), colors.HexColor('#FFDDDD')),
        ('TEXTCOLOR', (5, 1), (5, 2), colors.HexColor('#990000')),
        ('BACKGROUND', (5, 4), (5, 4), colors.HexColor('#FFF3CD')),
        ('TEXTCOLOR', (5, 4), (5, 4), colors.HexColor('#856404')),
        ('ALIGN', (3, 0), (5, -1), 'CENTER'),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(findings_table)
    story.append(Spacer(1, 12))

    # Section 3: Recommendations & Financial Estimate
    story.append(Paragraph("3. Recommendations & Corrective Actions", h2_style))
    story.append(Paragraph(
        "1. Immediately transfer crude distillation load from P-102A to standby pump P-102B.<br/>"
        "2. Isolate, depressurize, and de-inventory pump P-102A following MRPL SOP-CDU-SEC-014.<br/>"
        "3. Dismantle DE bearing housing, replace SKF 23144 CC/W33 bearing assembly, and install new John Crane Type 5620 mechanical seal.<br/>"
        "4. Estimated overhaul cost: <b>INR 2,85,000</b> (Spares: INR 1,95,000; Manpower/Tooling: INR 90,000).<br/>"
        "5. Estimated downtime: 18 hours with zero throughput loss due to P-102B readiness.",
        body_style
    ))

    doc.build(story)
    return output_path


def generate_scanned_pdf(digital_pdf_path: str, output_scanned_path: str) -> str:
    """
    Renders each page of the digital PDF into a 200 DPI bitmap image,
    adds realistic scanner degradation (slight skew, brightness variation, noise),
    and embeds ONLY the raw flat image into a new PDF with ZERO selectable text layer.
    """
    os.makedirs(os.path.dirname(output_scanned_path), exist_ok=True)
    doc = fitz.open(digital_pdf_path)
    scanned_doc = fitz.open()

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        # Render at 200 DPI
        zoom = 200 / 72.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)

        # Convert pixmap to PIL Image
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data)).convert("RGB")

        # Simulate scanner aging / skew (0.6 degree subtle rotation)
        rotated_img = img.rotate(0.6, resample=Image.BICUBIC, expand=False, fillcolor=(252, 252, 250))

        # Add subtle paper scan grain
        draw = ImageDraw.Draw(rotated_img)
        draw.line([(20, 15), (70, 15)], fill=(180, 180, 180), width=1)  # subtle scanner mark

        # Save to temporary JPEG buffer
        img_byte_arr = io.BytesIO()
        rotated_img.save(img_byte_arr, format='JPEG', quality=85)
        img_bytes = img_byte_arr.getvalue()

        # Create a new blank page in the scanned document and insert ONLY the image
        rect = page.rect
        scanned_page = scanned_doc.new_page(width=rect.width, height=rect.height)
        scanned_page.insert_image(rect, stream=img_bytes)

    scanned_doc.save(output_scanned_path)
    scanned_doc.close()
    doc.close()
    return output_scanned_path


def generate_telemetry_csv(output_path: str) -> str:
    """Generates 60+ rows of realistic refinery equipment telemetry."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    random.seed(42)

    equipment_list = [
        {"id": "P-101A", "name": "Crude Booster Pump A", "unit": "CDU-1", "base_vib": 2.2, "base_temp": 62.0, "base_press": 12.5},
        {"id": "P-101B", "name": "Crude Booster Pump B", "unit": "CDU-1", "base_vib": 2.1, "base_temp": 61.5, "base_press": 12.4},
        {"id": "P-102A", "name": "Main Crude Charge Pump A", "unit": "CDU-1", "base_vib": 7.8, "base_temp": 98.5, "base_press": 42.0},  # ALERT
        {"id": "P-102B", "name": "Main Crude Charge Pump B", "unit": "CDU-1", "base_vib": 2.4, "base_temp": 64.0, "base_press": 44.5},
        {"id": "P-201A", "name": "VGO Transfer Pump A", "unit": "VDU", "base_vib": 3.1, "base_temp": 71.0, "base_press": 18.0},
        {"id": "P-201B", "name": "VGO Transfer Pump B", "unit": "VDU", "base_vib": 2.8, "base_temp": 69.5, "base_press": 18.2},
        {"id": "K-101", "name": "Off-Gas Compressor", "unit": "CDU-1", "base_vib": 3.8, "base_temp": 78.0, "base_press": 6.5},
        {"id": "P-301A", "name": "FCC Feed Pump A", "unit": "FCCU", "base_vib": 2.9, "base_temp": 68.0, "base_press": 35.0},
    ]

    rows = []
    base_time = pd.Timestamp("2026-08-31 06:00:00")

    for i in range(60):
        t = base_time + pd.Timedelta(minutes=i * 15)
        eq = equipment_list[i % len(equipment_list)]
        
        # Add random sensor jitter
        vib = round(eq["base_vib"] + random.uniform(-0.2, 0.2), 2)
        temp = round(eq["base_temp"] + random.uniform(-1.0, 1.5), 1)
        press = round(eq["base_press"] + random.uniform(-0.5, 0.5), 1)
        flow = round(random.uniform(280.0, 320.0), 1)

        # Status rules
        if vib >= 6.5 or temp >= 90.0:
            status = "CRITICAL"
        elif vib >= 4.5 or temp >= 80.0:
            status = "WARNING"
        else:
            status = "NORMAL"

        rows.append({
            "timestamp": t.strftime("%Y-%m-%d %H:%M:%S"),
            "equipment_id": eq["id"],
            "equipment_name": eq["name"],
            "unit": eq["unit"],
            "vibration_mms": vib,
            "bearing_temp_c": temp,
            "discharge_pressure_bar": press,
            "flow_rate_m3h": flow,
            "status": status,
            "last_serviced_date": "2026-05-15"
        })

    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    return output_path


def generate_all_samples():
    """Builds all sample datasets."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    digital_pdf = os.path.join(base_dir, "sample_inspection_digital.pdf")
    scanned_pdf = os.path.join(base_dir, "sample_inspection_scanned.pdf")
    telemetry_csv = os.path.join(base_dir, "equipment_maintenance.csv")

    print("[*] Generating digital inspection PDF...")
    generate_digital_pdf(digital_pdf)
    print(f"    -> Created: {digital_pdf}")

    print("[*] Generating true scanned raster PDF (no text layer)...")
    generate_scanned_pdf(digital_pdf, scanned_pdf)
    print(f"    -> Created: {scanned_pdf}")

    print("[*] Generating equipment telemetry CSV...")
    generate_telemetry_csv(telemetry_csv)
    print(f"    -> Created: {telemetry_csv}")

    print("\n[+] All sample datasets generated successfully!")


if __name__ == "__main__":
    generate_all_samples()
