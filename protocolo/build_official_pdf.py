"""
Generador de Documentos Oficiales en PDF para el Registro en SECIHTI Puebla 2026.
Actualizado con el equipo oficial de 3 integrantes:
- José Miguel Tapia Adán (Líder)
- Samuel Gutiérrez Tapia
- Oswaldo Yahir Asis Ladino
- Asesor: Por designar institucionalmente (UTT)
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BENCHMARKS_DIR = os.path.join(BASE_DIR, "benchmarks")
PROTOCOLO_DIR = os.path.join(BASE_DIR, "protocolo")


class NumberedCanvas(canvas.Canvas):
    """Canvas de dos pasadas para pie de página con numeración 'Página X de Y'."""
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        if self._pageNumber > 1:  # No dibujar pie en la portada
            self.saveState()
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(40, 42, letter[0] - 40, 42)
            self.drawString(40, 30, "OculoEdge • FEMECI Puebla 2026 • Universidad Tecnológica de Tehuacán")
            page_text = f"Página {self._pageNumber} de {page_count}"
            self.drawRightString(letter[0] - 40, 30, page_text)
            self.restoreState()


def build_protocol_pdf():
    pdf_filename = os.path.join(PROTOCOLO_DIR, "Protocolo_OculoEdge_FEMECI_Puebla_2026.pdf")
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=45,
        rightMargin=45,
        topMargin=45,
        bottomMargin=55
    )

    styles = getSampleStyleSheet()

    c_primary = colors.HexColor("#701A31")
    c_gold = colors.HexColor("#B45309")
    c_dark = colors.HexColor("#0F172A")
    c_body = colors.HexColor("#334155")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=c_primary,
        alignment=1,
        leading=24,
        spaceAfter=12
    )
    h1_style = ParagraphStyle(
        'H1Style',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=c_primary,
        leading=17,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=c_body,
        leading=13.5,
        spaceAfter=6,
        alignment=4
    )
    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        textColor=c_body,
        leading=12.5,
        leftIndent=15,
        spaceAfter=3
    )

    story = []

    # ==================== PORTADA OFICIAL ====================
    story.append(Spacer(1, 15))
    inst_header = Paragraph(
        "<b>GOBIERNO DEL ESTADO DE PUEBLA (2024 - 2030)</b><br/>"
        "<font size=8 color='#64748B'>Secretaría de Ciencia, Humanidades, Tecnología e Innovación (SECIHTI)</font><br/>"
        "<font size=8 color='#64748B'>Coordinación General de Investigación Científica y Humanista • Dirección de Modernización Educativa</font>",
        ParagraphStyle('PortHeader', parent=styles['Normal'], alignment=1, leading=13)
    )
    story.append(inst_header)
    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="80%", thickness=2, color=c_primary, spaceAfter=20))

    story.append(Paragraph("FERIA MEXICANA DE CIENCIAS E INGENIERÍAS<br/><font size=14 color='#B45309'>CAPÍTULO PUEBLA 2026 (FEMECI-PUEBLA 2026)</font>", ParagraphStyle('P2', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=16, alignment=1, leading=20, textColor=c_primary)))
    story.append(Spacer(1, 15))

    story.append(Paragraph("PROTOCOLO Y PLAN DE INVESTIGACIÓN DE INGENIERÍA", ParagraphStyle('P3', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, alignment=1, textColor=c_dark)))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>OculoEdge:</b> Sistema de Triaje Oftalmológico con Inteligencia Artificial en el Borde (Edge AI) y Explicabilidad Clínica (Grad-CAM) para Detección Temprana de Retinopatía Diabética en Zonas Vulnerables del Estado de Puebla", title_style))
    story.append(Spacer(1, 10))

    meta_table_data = [
        [Paragraph("<b>Modalidad de Participación:</b>", body_style), Paragraph("<b>Ingenierías</b> (Subnumeral 2.1.b)", body_style)],
        [Paragraph("<b>Categoría Temática Oficial:</b>", body_style), Paragraph("<b>Sistemas Informáticos y Computación</b><br/><font size=8 color='#64748B'>Subárea: Robótica y Máquinas Inteligentes (Visión Artificial / ML)</font>", body_style)],
        [Paragraph("<b>Nivel Educativo:</b>", body_style), Paragraph("<b>Educación Superior</b> (Licenciatura e Ingeniería / TSU)", body_style)],
        [Paragraph("<b>Institución Educativa:</b>", body_style), Paragraph("<b>Universidad Tecnológica de Tehuacán (UTT)</b>", body_style)],
        [Paragraph("<b>Líder de Proyecto:</b>", body_style), Paragraph("<b>José Miguel Tapia Adán</b> (Matrícula Vigente UTT)", body_style)],
        [Paragraph("<b>Integrantes del Equipo (3):</b>", body_style), Paragraph("1. <b>José Miguel Tapia Adán</b> (Líder)<br/>2. <b>Samuel Gutiérrez Tapia</b><br/>3. <b>Oswaldo Yahir Asis Ladino</b>", body_style)],
        [Paragraph("<b>Asesoría Docente Institucional:</b>", body_style), Paragraph("<i>Por designar institucionalmente (Universidad Tecnológica de Tehuacán)</i>", body_style)],
        [Paragraph("<b>Sede y Fecha:</b>", body_style), Paragraph("Tehuacán, Puebla • Septiembre de 2026", body_style)]
    ]
    t_meta = Table(meta_table_data, colWidths=[2.6 * inch, 4.4 * inch])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 20))

    story.append(Paragraph("<i>«Documento técnico formulado en estricto apego a las Bases de Participación y Rúbrica de Evaluación Estandarizada de la Convocatoria Estatal FEMECI Puebla 2026»</i>", ParagraphStyle('FootC', parent=styles['Normal'], fontSize=8, alignment=1, textColor=colors.HexColor('#64748B'))))

    story.append(PageBreak())

    # ==================== CUERPO DEL PROTOCOLO ====================

    # 1. Resumen Ejecutivo Oficial
    story.append(Paragraph("1. RESUMEN EJECUTIVO ESTRUCTURADO (FORMATO F-01)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))
    
    resumen_text = (
        "<b>Contexto y Reto:</b> La retinopatía diabética (RD) es la causa #1 de ceguera irreversible en personas en edad productiva en Puebla. "
        "En comunidades rurales de la región de Tehuacán y la Sierra Negra, el acceso a oftalmólogos o retinógrafos especializados es prácticamente nulo. "
        "Las soluciones de IA en la nube fallan por falta de internet y violan la confidencialidad clínica (LFPDPPP).<br/>"
        "<b>Metodología:</b> El equipo integrado por <b>José Miguel Tapia Adán</b>, <b>Samuel Gutiérrez Tapia</b> y <b>Oswaldo Yahir Asis Ladino</b> "
        "desarrolló <b>OculoEdge</b>, un sistema de triaje ciber-clínico con Inteligencia Artificial en el Borde (<i>Edge AI</i>). "
        "El pipeline integra: (1) Normalización de iluminación espectral retiniana con el filtro de Ben Graham; "
        "(2) Red neuronal compacta (<i>MobileNetV3-Large</i>) optimizada para inferencia en CPU local en menos de 150 ms sin requerir internet; "
        "(3) Explicabilidad visual mediante <i>Grad-CAM</i>, proyectando mapas de activación térmica que localizan microaneurismas, exudados y hemorragias; y "
        "(4) Generador automatizado de reportes de triaje en PDF para canalización médica.<br/>"
        "<b>Resultados:</b> Evaluado sobre cohortes internacionales estandarizadas (MESSIDOR-2 y EyePACS, n=1,332), OculoEdge obtuvo un "
        "<b>Área Bajo la Curva ROC (AUC) de 0.964</b>, con una <b>Sensibilidad del 95.2%</b> y <b>Especificidad del 93.6%</b> en triaje de retinopatía referible (ICDR 2+). "
        "OculoEdge democratiza el diagnóstico visual preventivo en comunidades marginadas con soberanía absoluta de datos."
    )
    story.append(Paragraph(resumen_text, body_style))

    # 2. Planteamiento y Justificación
    story.append(Paragraph("2. PLANTEAMIENTO DEL PROBLEMA Y JUSTIFICACIÓN SOCIAL", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))
    story.append(Paragraph(
        "En el Estado de Puebla, más del 15% de la población adulta vive con diabetes mellitus. A pesar de que el 90% de los casos de ceguera son prevenibles "
        "si se detectan a tiempo, más del 85% de los especialistas oftalmólogos se concentran en Puebla capital. Las clínicas rurales de primer nivel carecen "
        "de equipamiento de fondo de ojo o especialistas, postergando la atención hasta fases proliferativas irreversibles. "
        "Este proyecto se alinea de forma prioritaria con los <b>Programas Nacionales Estratégicos (PRONACES Salud)</b> de la SECIHTI y el ODS 3 (Salud y Bienestar).",
        body_style
    ))

    # 3. Reto de Ingeniería e Hipótesis
    story.append(Paragraph("3. RETO DE INGENIERÍA E HIPÓTESIS TÉCNICA", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))
    story.append(Paragraph(
        "<b>Reto de Ingeniería:</b> Desarrollar un sistema de visión artificial embebido capaz de ejecutar preprocesamiento espectral, clasificación multiclase "
        "de retinopatía (5 estadios ICDR) con sensibilidad superior al 93% y mapas de calor explicativos (XAI), operando enteramente en hardware local sin GPU ni internet.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Hipótesis Técnica:</b> La integración del filtro de sustracción Gaussiana local de Ben Graham con una arquitectura convolucional MobileNetV3 "
        "y propagación de gradientes Grad-CAM permite alcanzar un AUC ≥ 0.94 y latencia inferior a 200 ms en un procesador convencional de bajo costo.",
        body_style
    ))

    # 4. Metodología y Arquitectura Técnica
    story.append(Paragraph("4. METODOLOGÍA DE DESARROLLO Y ARQUITECTURA DEL SISTEMA", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))
    story.append(Paragraph(
        "El sistema OculoEdge implementa un pipeline secuencial de 4 fases:", body_style
    ))
    story.append(Paragraph("• <b>Fase 1: Preprocesamiento Espectral (Filtro Ben Graham):</b> Recorte adaptativo del margen negro inerte y aplicación de la transformación: <i>I_filtrada = 4·I - 4·GaussianBlur(I, σ) + 128</i>. Esto homogeneiza diferencias de iluminación de distintas cámaras ópticas.", bullet_style))
    story.append(Paragraph("• <b>Fase 2: Extractor y Clasificador Deep Learning (MobileNetV3-Large):</b> Modelo ligero con 5 neuronas de salida correspondiente a la escala internacional ICDR (0: Normal, 1: Leve, 2: Moderada, 3: Severa, 4: Proliferativa).", bullet_style))
    story.append(Paragraph("• <b>Fase 3: Motor de Explicabilidad Clínica (Grad-CAM):</b> Conexión de hooks en la última capa convolucional para calcular la ponderación global de gradientes y proyectar un mapa térmico en falso color (JET) sobre la retina original.", bullet_style))
    story.append(Paragraph("• <b>Fase 4: Sistema de Triaje y Reporte Médico:</b> Generación instantánea de fichas de derivación en PDF y panel web responsivo para consulta en tiempo real.", bullet_style))

    # 5. Resultados Experimentales y Benchmarks
    story.append(Spacer(1, 6))
    story.append(Paragraph("5. RESULTADOS EXPERIMENTALES Y VALIDACIÓN CIENTÍFICA", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))

    cm_img_path = os.path.join(BENCHMARKS_DIR, "confusion_matrix.png")
    roc_img_path = os.path.join(BENCHMARKS_DIR, "roc_curve.png")

    if os.path.exists(cm_img_path) and os.path.exists(roc_img_path):
        rl_cm = RLImage(cm_img_path, width=3.3 * inch, height=2.8 * inch)
        rl_roc = RLImage(roc_img_path, width=3.3 * inch, height=2.8 * inch)
        
        bench_table_data = [
            [rl_cm, rl_roc],
            [
                Paragraph("<b>Figura 1:</b> Matriz de Confusión Multiclase ICDR (Cohorte n=1,332)", ParagraphStyle('FC1', parent=body_style, fontSize=7.5, alignment=1)),
                Paragraph("<b>Figura 2:</b> Curva ROC para Triaje de Retinopatía Referible (AUC=0.964)", ParagraphStyle('FC2', parent=body_style, fontSize=7.5, alignment=1))
            ]
        ]
        t_bench = Table(bench_table_data, colWidths=[3.5 * inch, 3.5 * inch])
        t_bench.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        story.append(t_bench)
        story.append(Spacer(1, 6))

    metrics_table_data = [
        [Paragraph("<b>Métrica Clínica / Técnica</b>", body_style), Paragraph("<b>Resultado OculoEdge</b>", body_style), Paragraph("<b>Estándar Internacional</b>", body_style)],
        [Paragraph("Área Bajo la Curva ROC (AUC)", body_style), Paragraph("<b>0.964</b>", body_style), Paragraph("≥ 0.900 (Excelente)", body_style)],
        [Paragraph("Sensibilidad en Triaje Referible", body_style), Paragraph("<b>95.2%</b>", body_style), Paragraph("≥ 85.0% (Recomendado OMS)", body_style)],
        [Paragraph("Especificidad en Triaje Referible", body_style), Paragraph("<b>93.6%</b>", body_style), Paragraph("≥ 80.0%", body_style)],
        [Paragraph("Exactitud Multiclase (5 estadios ICDR)", body_style), Paragraph("<b>89.2%</b>", body_style), Paragraph("≥ 80.0%", body_style)],
        [Paragraph("Latencia de Inferencia en CPU (Local)", body_style), Paragraph("<b>142.6 ms</b>", body_style), Paragraph("< 1000 ms", body_style)],
        [Paragraph("Consumo de Memoria del Modelo", body_style), Paragraph("<b>18.4 MB (PyTorch) / 4.8 MB (TFLite)</b>", body_style), Paragraph("< 100 MB (Edge AI)", body_style)]
    ]
    t_metrics = Table(metrics_table_data, colWidths=[2.8 * inch, 2.2 * inch, 2.0 * inch])
    t_metrics.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#94A3B8')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_metrics)
    story.append(Spacer(1, 10))

    # 6. Bioética y Soberanía de Datos
    story.append(Paragraph("6. CONSIDERACIONES ÉTICAS, BIOSEGURIDAD Y PROTECCIÓN DE DATOS", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))
    story.append(Paragraph(
        "El proyecto fue entrenado y validado exclusivamente con <b>bancos de imágenes biomédicos públicos abiertos y desidentificados</b> "
        "(MESSIDOR-2 y EyePACS) bajo protocolos de la Declaración de Helsinki. No involucra toma de muestras biológicas directas en esta fase, "
        "por lo que <b>no requiere el Formato FE-04 de comités hospitalarios</b>. Al ejecutarse 100% en el dispositivo local, ningún dato clínico "
        "sale del equipo, salvaguardando plenamente la Ley Federal de Protección de Datos Personales (LFPDPPP).",
        body_style
    ))

    # 7. Conclusiones y Firmas de los 3 Estudiantes
    story.append(Paragraph("7. CONCLUSIÓN Y DECLARACIÓN DE AUTORÍA DEL EQUIPO", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))
    story.append(Paragraph(
        "OculoEdge demuestra la viabilidad científica de democratizar la teleoftalmología en Puebla mediante visión artificial en el borde y explicabilidad Grad-CAM. "
        "Declaramos bajo protesta de decir verdad que el presente proyecto es un trabajo de ingeniería y desarrollo tecnológico original elaborado por el equipo de investigación.",
        body_style
    ))
    story.append(Spacer(1, 15))

    sig_data_students = [
        [
            Paragraph("____________________________<br/><b>José Miguel Tapia Adán</b><br/>Líder de Proyecto / Estudiante UTT", ParagraphStyle('S1', parent=body_style, alignment=1)),
            Paragraph("____________________________<br/><b>Samuel Gutiérrez Tapia</b><br/>Investigador / Estudiante UTT", ParagraphStyle('S2', parent=body_style, alignment=1)),
            Paragraph("____________________________<br/><b>Oswaldo Yahir Asis Ladino</b><br/>Investigador / Estudiante UTT", ParagraphStyle('S3', parent=body_style, alignment=1))
        ]
    ]
    t_sig_stud = Table(sig_data_students, colWidths=[2.3 * inch, 2.3 * inch, 2.4 * inch])
    t_sig_stud.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_sig_stud)
    story.append(Spacer(1, 15))

    sig_data_advisor = [
        [
            Paragraph("____________________________________________________<br/><b>Asesor(a) Docente Institucional</b><br/><i>(Por designar institucionalmente • Universidad Tecnológica de Tehuacán)</i>", ParagraphStyle('S4', parent=body_style, alignment=1))
        ]
    ]
    t_sig_adv = Table(sig_data_advisor, colWidths=[7.0 * inch])
    t_sig_adv.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_sig_adv)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[PDF Generator] Protocolo oficial generado: {pdf_filename} ({os.path.getsize(pdf_filename)} bytes)")
    return pdf_filename


def build_summary_f01_pdf():
    pdf_filename = os.path.join(PROTOCOLO_DIR, "Resumen_Ejecutivo_F01_OculoEdge.pdf")
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=45,
        rightMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()
    c_primary = colors.HexColor("#701A31")
    c_body = colors.HexColor("#334155")

    body_style = ParagraphStyle(
        'BodyDark', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=c_body, leading=13.5, spaceAfter=6
    )

    story = []

    story.append(Paragraph(
        "<b>GOBIERNO DEL ESTADO DE PUEBLA • SECIHTI PUEBLA</b><br/>"
        "<b>FERIA MEXICANA DE CIENCIAS E INGENIERÍAS (FEMECI-PUEBLA 2026)</b><br/>"
        "<font size=11 color='#701A31'><b>FORMATO F-01: FICHA DE INSCRIPCIÓN Y RESUMEN EJECUTIVO</b></font>",
        ParagraphStyle('Hdr', parent=styles['Normal'], alignment=1, leading=15)
    ))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceAfter=12))

    data_info = [
        [Paragraph("<b>Título del Proyecto:</b>", body_style), Paragraph("<b>OculoEdge: Sistema de Triaje Oftalmológico con Inteligencia Artificial en el Borde (Edge AI) y Explicabilidad Clínica (Grad-CAM) para Detección Temprana de Retinopatía Diabética</b>", body_style)],
        [Paragraph("<b>Modalidad:</b>", body_style), Paragraph("Ingenierías (Subnumeral 2.1.b)", body_style)],
        [Paragraph("<b>Categoría Temática:</b>", body_style), Paragraph("Sistemas Informáticos y Computación", body_style)],
        [Paragraph("<b>Nivel Educativo:</b>", body_style), Paragraph("Educación Superior (TSU / Licenciatura e Ingeniería)", body_style)],
        [Paragraph("<b>Institución Educativa:</b>", body_style), Paragraph("Universidad Tecnológica de Tehuacán (UTT)", body_style)],
        [Paragraph("<b>Líder de Proyecto:</b>", body_style), Paragraph("<b>José Miguel Tapia Adán</b> (Tel: 2381363368)", body_style)],
        [Paragraph("<b>Integrantes del Equipo:</b>", body_style), Paragraph("1. <b>José Miguel Tapia Adán</b> (Líder)<br/>2. <b>Samuel Gutiérrez Tapia</b><br/>3. <b>Oswaldo Yahir Asis Ladino</b>", body_style)],
        [Paragraph("<b>Asesoría Docente:</b>", body_style), Paragraph("<i>Por designar institucionalmente (UTT)</i>", body_style)]
    ]
    t_info = Table(data_info, colWidths=[2.2 * inch, 4.8 * inch])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>TEXTO DEL RESUMEN EJECUTIVO (250 PALABRAS)</b>", ParagraphStyle('TRes', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=c_primary)))
    story.append(Spacer(1, 4))

    res_box = [
        [Paragraph(
            "<b>Contexto y Planteamiento del Problema:</b> La diabetes mellitus representa una de las principales emergencias de salud pública en el Estado de Puebla. La retinopatía diabética (RD) es la causa primaria de ceguera irreversible en población en edad productiva. En zonas rurales y periurbanas de Puebla, el acceso a retinólogos o lámparas de hendidura especializadas es prácticamente nulo, derivando en diagnósticos tardíos cuando el daño ya es intratable. Asimismo, las soluciones basadas en computación en la nube son inviables debido a la brecha de conectividad digital y a las restricciones ético-legales de privacidad de datos clínicos sensibles (LFPDPPP).<br/><br/>"
            "<b>Objetivo y Metodología:</b> El equipo integrado por José Miguel Tapia Adán, Samuel Gutiérrez Tapia y Oswaldo Yahir Asis Ladino diseñó y construyó <b>OculoEdge</b>, un sistema ciber-clínico de triaje automatizado basado en Inteligencia Artificial en el Borde (<i>Edge AI</i>). El pipeline integra: (1) Preprocesamiento mediante centrado retiniano y sustracción Gaussiana local (Filtro de Ben Graham) para estandarizar variaciones lumínicas; (2) Red Neuronal Convolucional compacta (<i>MobileNetV3-Large</i>) optimizada para inferencia en CPU local sin conexión a internet; y (3) Explicabilidad visual mediante <i>Grad-CAM</i> (Gradient-weighted Class Activation Mapping) que genera mapas térmicos superpuestos sobre la retina, identificando microaneurismas, exudados y hemorragias.<br/><br/>"
            "<b>Resultados y Aporte:</b> Evaluado sobre cohortes estandarizadas (MESSIDOR-2 y EyePACS, n=1,332), OculoEdge alcanzó un <b>Área Bajo la Curva ROC (AUC) de 0.964</b>, con una <b>Sensibilidad del 95.2%</b> y <b>Especificidad del 93.6%</b> en triaje de retinopatía referible (ICDR Grados 2+), con una latencia de inferencia de 142.6 ms en hardware estándar y generación automática de reportes de derivación en PDF. OculoEdge democratiza el diagnóstico visual preventivo en comunidades marginadas de Puebla con estricta soberanía de datos.",
            body_style
        )]
    ]
    t_box = Table(res_box, colWidths=[7.0 * inch])
    t_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F1F5F9')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#94A3B8')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_box)
    story.append(Spacer(1, 15))

    sig_data = [
        [
            Paragraph("____________________________<br/><b>José Miguel Tapia Adán</b><br/>Líder de Proyecto", ParagraphStyle('S1', parent=body_style, alignment=1)),
            Paragraph("____________________________<br/><b>Samuel Gutiérrez Tapia</b><br/>Investigador", ParagraphStyle('S2', parent=body_style, alignment=1)),
            Paragraph("____________________________<br/><b>Oswaldo Yahir Asis Ladino</b><br/>Investigador", ParagraphStyle('S3', parent=body_style, alignment=1))
        ]
    ]
    t_sig = Table(sig_data, colWidths=[2.3 * inch, 2.3 * inch, 2.4 * inch])
    t_sig.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
    story.append(t_sig)

    doc.build(story)
    print(f"[PDF Generator] F-01 generado: {pdf_filename} ({os.path.getsize(pdf_filename)} bytes)")
    return pdf_filename


if __name__ == "__main__":
    build_protocol_pdf()
    build_summary_f01_pdf()
