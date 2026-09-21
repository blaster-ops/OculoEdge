"""
OculoEdge - Generador de Informes Médicos de Triaje en PDF
Crea una ficha clínica estandarizada con los resultados de la inferencia,
el mapa explicativo Grad-CAM, desglose de biomarcadores cuantitativos y código QR de verificación.
"""

import os
import io
import hashlib
import datetime
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing


def generate_pdf_report(
    patient_name: str,
    patient_id: str,
    patient_age: int,
    eye_side: str,  # 'OD' (Ojo Derecho) o 'OI' (Ojo Izquierdo)
    diagnosis_data: dict,
    original_img_np,
    gradcam_img_np,
    output_path: str = None
) -> bytes:
    """
    Genera un archivo PDF con formato de reporte clínico de telemedicina/triaje.
    """
    # 1. Sanitización de entradas
    p_name = str(patient_name).strip() if patient_name and str(patient_name).strip() else "Paciente Anónimo"
    p_id = str(patient_id).strip() if patient_id and str(patient_id).strip() else "FOLIO-UTT-2026-01"
    
    try:
        p_age = int(patient_age)
    except (ValueError, TypeError):
        p_age = 50

    p_side = str(eye_side).strip().upper() if eye_side and str(eye_side).strip() else "OD"
    if p_side not in ["OD", "OI"]:
        p_side = "OD"

    buffer = io.BytesIO() if output_path is None else open(output_path, "wb")
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=32,
        bottomMargin=32
    )

    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#0F172A'),
        leading=15
    )
    sub_header = ParagraphStyle(
        'SubHeader',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        textColor=colors.HexColor('#475569'),
        leading=11
    )
    section_title = ParagraphStyle(
        'SectionTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=4
    )
    body_text = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        textColor=colors.HexColor('#334155'),
        leading=11.5
    )
    badge_style = ParagraphStyle(
        'BadgeStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        textColor=colors.white,
        alignment=1,
        leading=13
    )

    story = []

    # Generar Hash Criptográfico de Integridad
    now_dt = datetime.datetime.now()
    now_str = now_dt.strftime("%d/%m/%Y %H:%M:%S")
    raw_signature = f"{p_name}|{p_id}|{p_age}|{p_side}|{diagnosis_data.get('diagnosis')}|{now_str}"
    verification_hash = hashlib.sha256(raw_signature.encode('utf-8')).hexdigest()[:16].upper()

    # Generar widget QR en ReportLab
    qr_payload = f"OCULOEDGE|ID:{p_id}|EYE:{p_side}|DX:{diagnosis_data.get('diagnosis')}|CONF:{diagnosis_data.get('confidence_percentage')}%|HASH:{verification_hash}"
    qr_widget = QrCodeWidget(qr_payload)
    qr_bounds = qr_widget.getBounds()
    qr_size = 50.0
    scale_factor = qr_size / (qr_bounds[2] - qr_bounds[0])
    qr_drawing = Drawing(qr_size, qr_size, transform=[scale_factor, 0, 0, scale_factor, 0, 0])
    qr_drawing.add(qr_widget)

    # 1. Encabezado Institucional
    header_data = [
        [
            Paragraph("<b>UNIVERSIDAD TECNOLÓGICA DE TEHUACÁN</b><br/>"
                      "<font size=7.5 color='#0284C7'><b>OculoEdge • Sistema de Triaje Oftalmológico Autónomo</b></font><br/>"
                      "<font size=7 color='#64748B'>FEMECI Capítulo Puebla 2026 • Modalidad Superior / Ingenierías</font>", header_style),
            qr_drawing,
            Paragraph(f"<b>FICHA CLÍNICA DE TRIAJE</b><br/>"
                      f"<font size=7 color='#64748B'>ID Verificación:</font><br/>"
                      f"<font size=7.5 color='#0F172A' face='Courier'><b>{verification_hash}</b></font><br/>"
                      f"<font size=7 color='#64748B'>Fecha: {now_str}</font>", ParagraphStyle('RightH', parent=sub_header, alignment=2))
        ]
    ]
    t_header = Table(header_data, colWidths=[4.2 * inch, 0.8 * inch, 2.2 * inch])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(t_header)
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284C7"), spaceAfter=8))

    # 2. Datos del Paciente y Estudio
    patient_info_data = [
        [
            Paragraph(f"<b>Paciente:</b> {p_name}", body_text),
            Paragraph(f"<b>Folio / Expediente:</b> {p_id}", body_text),
            Paragraph(f"<b>Edad:</b> {p_age} años", body_text)
        ],
        [
            Paragraph(f"<b>Lateralidad:</b> {p_side} ({'Ojo Derecho' if 'OD' in p_side else 'Ojo Izquierdo'})", body_text),
            Paragraph("<b>Arquitectura:</b> MobileNetV3 + Ben Graham", body_text),
            Paragraph("<b>Modo Inferencia:</b> Edge CPU Offline", body_text)
        ]
    ]
    t_patient = Table(patient_info_data, colWidths=[2.6 * inch, 2.5 * inch, 2.1 * inch])
    t_patient.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_patient)
    story.append(Spacer(1, 8))

    # 3. Diagnóstico Algorítmico y Triaje
    story.append(Paragraph("EVALUACIÓN CLÍNICA AUTOMATIZADA (ESCALA INTERNACIONAL ICDR)", section_title))
    
    badge_bg = colors.HexColor(diagnosis_data.get("badge_color", "#0284C7"))
    is_referable = diagnosis_data.get("referable", False)
    status_text = "REFERIBLE A OFTALMOLOGÍA" if is_referable else "NO REFERIBLE (CONTROL ANUAL)"
    sub_status = "Requiere atención prioritaria" if is_referable else "Sin signos de alarma inmediata"
    
    diag_summary_data = [
        [
            Paragraph(f"<b>Estadio Diagnóstico:</b> {diagnosis_data.get('diagnosis')}<br/>"
                      f"<b>Confianza Algorítmica:</b> {diagnosis_data.get('confidence_percentage')}%<br/>"
                      f"<b>Nivel de Urgencia:</b> {diagnosis_data.get('urgency')}", body_text),
            Paragraph(f"<b>{status_text}</b><br/><font size=7.5 color='#FFFFFF'>{sub_status}</font>", badge_style)
        ]
    ]
    t_diag = Table(diag_summary_data, colWidths=[4.7 * inch, 2.5 * inch])
    t_diag.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#F1F5F9')),
        ('BACKGROUND', (1, 0), (1, 0), badge_bg),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#94A3B8')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_diag)
    story.append(Spacer(1, 8))

    # 4. Biomarcadores Cuantitativos Computarizados
    metrics = diagnosis_data.get("biomarker_metrics", {})
    dark_px = metrics.get("dark_lesion_pixels", 0)
    exud_px = metrics.get("exudate_pixels", 0)
    disc_edges = metrics.get("disc_vascular_edges", 0)
    quadrants = metrics.get("quadrants_damaged", 0)

    biomarker_data = [
        [
            Paragraph("<b>Biomarcador Retiniano Cuantitativo</b>", ParagraphStyle('Bmh', parent=sub_header, fontName='Helvetica-Bold', textColor=colors.HexColor('#0F172A'))),
            Paragraph("<b>Medición Extraída</b>", ParagraphStyle('Bmh2', parent=sub_header, fontName='Helvetica-Bold', textColor=colors.HexColor('#0F172A'))),
            Paragraph("<b>Criterio Clínico ICDR / Umbral</b>", ParagraphStyle('Bmh3', parent=sub_header, fontName='Helvetica-Bold', textColor=colors.HexColor('#0F172A'))),
        ],
        [
            Paragraph("Microaneurismas y Hemorragias Retinianas", body_text),
            Paragraph(f"<b>{dark_px}</b> píxeles oscuros", body_text),
            Paragraph("Normal: &le;230 px | Leve: >230 px | Severa: >1200 px", body_text),
        ],
        [
            Paragraph("Exudados Duros Lipídicos (Espacio CIE-LAB)", body_text),
            Paragraph(f"<b>{exud_px}</b> píxeles reflectantes", body_text),
            Paragraph("Patológico si >40 px (Riesgo de Edema Macular)", body_text),
        ],
        [
            Paragraph("Complejidad Vascular Papilar (Neovasos NVD)", body_text),
            Paragraph(f"<b>{disc_edges}</b> bordes estructurales", body_text),
            Paragraph("Frondas neovasculares activas si >1400 bordes", body_text),
        ],
        [
            Paragraph("Extensión Cuadrantal de Hemorragias", body_text),
            Paragraph(f"<b>{quadrants} / 4</b> cuadrantes afectados", body_text),
            Paragraph("Regla 4-2-1: &ge;3 cuadrantes clasifica como RD Severa", body_text),
        ]
    ]
    t_bio = Table(biomarker_data, colWidths=[2.8 * inch, 1.8 * inch, 2.6 * inch])
    t_bio.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E2E8F0')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_bio)
    story.append(Spacer(1, 8))

    # 5. Evidencia Visual y Explicabilidad Grad-CAM
    story.append(Paragraph("EVIDENCIA DE IMAGEN Y EXPLICABILIDAD CLÍNICA (XAI GRAD-CAM)", section_title))

    # Guardar imágenes temporales en buffer
    orig_pil = Image.fromarray(original_img_np)
    orig_buf = io.BytesIO()
    orig_pil.save(orig_buf, format="JPEG", quality=92)
    orig_buf.seek(0)

    grad_pil = Image.fromarray(gradcam_img_np)
    grad_buf = io.BytesIO()
    grad_pil.save(grad_buf, format="JPEG", quality=92)
    grad_buf.seek(0)

    img_dim = 2.4 * inch
    rl_orig = RLImage(orig_buf, width=img_dim, height=img_dim)
    rl_grad = RLImage(grad_buf, width=img_dim, height=img_dim)

    img_table_data = [
        [rl_orig, rl_grad],
        [
            Paragraph("<font size=7.5 color='#475569'><b>1. Filtro Retiniano Ben Graham (Sustracción Gaussiana)</b></font>", ParagraphStyle('Cap1', parent=sub_header, alignment=1)),
            Paragraph("<font size=7.5 color='#475569'><b>2. Mapa Térmico Grad-CAM (Focos Lesionales Justificados)</b></font>", ParagraphStyle('Cap2', parent=sub_header, alignment=1))
        ]
    ]
    t_imgs = Table(img_table_data, colWidths=[3.6 * inch, 3.6 * inch])
    t_imgs.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(t_imgs)
    story.append(Spacer(1, 6))

    # 6. Hallazgos Clínicos y Recomendación
    recom_data = [
        [
            Paragraph(f"<b>Hallazgos Patognomónicos:</b> {diagnosis_data.get('clinical_findings')}<br/>"
                      f"<b>Recomendación de Manejo:</b> {diagnosis_data.get('recommendation')}", body_text)
        ]
    ]
    t_recom = Table(recom_data, colWidths=[7.2 * inch])
    t_recom.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_recom)
    story.append(Spacer(1, 6))

    # 7. Firmas y Descargo Ético
    disclaimer_text = (
        "<b>Aviso Ético y Regulatorio:</b> OculoEdge es un sistema computacional de triaje primario no invasivo diseñado para "
        "investigación científica en FEMECI Puebla 2026. No sustituye la oftalmoscopía indirecta ni la angiografía fluoresceínica. "
        "Todo diagnóstico referible debe ser confirmado por un oftalmólogo certificado."
    )
    story.append(Paragraph(f"<font size=6.5 color='#64748B'>{disclaimer_text}</font>", body_text))
    story.append(Spacer(1, 10))

    signature_data = [
        [
            Paragraph("__________________________________________<br/><b>José Miguel Tapia Adán</b><br/><font size=7 color='#64748B'>Director de Proyecto • UTT</font>", ParagraphStyle('Sig1', parent=sub_header, alignment=1)),
            Paragraph("__________________________________________<br/><b>Equipo de Investigación OculoEdge</b><br/><font size=7 color='#64748B'>Samuel Gutiérrez T. • Oswaldo Yahir Asis L.</font>", ParagraphStyle('Sig2', parent=sub_header, alignment=1)),
            Paragraph("__________________________________________<br/><b>Asesor Institucional</b><br/><font size=7 color='#64748B'>Universidad Tecnológica de Tehuacán</font>", ParagraphStyle('Sig3', parent=sub_header, alignment=1))
        ]
    ]
    t_sig = Table(signature_data, colWidths=[2.4 * inch, 2.4 * inch, 2.4 * inch])
    t_sig.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(t_sig)

    doc.build(story)
    
    if output_path is None:
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
    else:
        buffer.close()
        return b""
