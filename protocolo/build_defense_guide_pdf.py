"""
Compilador a PDF del Manual de Bolsillo y Guía de Defensa para el Jurado.
Genera Guia_Defensa_Jurado_OculoEdge.pdf en protocolo/ y en ~/Documentos/
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROTOCOLO_DIR = os.path.join(BASE_DIR, "protocolo")


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(40, 38, letter[0] - 40, 38)
        self.drawString(40, 26, "OculoEdge • Guía de Defensa para el Jurado • FEMECI Puebla 2026")
        self.drawRightString(letter[0] - 40, 26, f"Página {self._pageNumber} de {page_count}")
        self.restoreState()


def build_defense_guide_pdf():
    pdf_filename = os.path.join(PROTOCOLO_DIR, "Guia_Defensa_Jurado_OculoEdge.pdf")
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=45,
        rightMargin=45,
        topMargin=45,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()
    c_primary = colors.HexColor("#701A31")
    c_blue = colors.HexColor("#0284C7")
    c_dark = colors.HexColor("#0F172A")
    c_body = colors.HexColor("#334155")

    h1_style = ParagraphStyle(
        'H1', fontName='Helvetica-Bold', fontSize=13, textColor=c_primary, leading=16, spaceBefore=12, spaceAfter=6, keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'H2', fontName='Helvetica-Bold', fontSize=10.5, textColor=c_blue, leading=14, spaceBefore=8, spaceAfter=4, keepWithNext=True
    )
    body_style = ParagraphStyle(
        'Body', fontName='Helvetica', fontSize=8.5, textColor=c_body, leading=12.5, spaceAfter=5
    )
    speech_style = ParagraphStyle(
        'Speech', fontName='Helvetica-Oblique', fontSize=8.5, textColor=colors.HexColor("#1E293B"), leading=13
    )

    story = []

    # Encabezado
    story.append(Paragraph(
        "<b>MANUAL DE BOLSILLO Y GUÍA DE DEFENSA ANTE EL JURADO</b><br/>"
        "<font size=9 color='#64748B'>Estrategia de Exposición Oral (Pitch 10 Min) y Banco de Preguntas Trampa</font><br/>"
        "<font size=8 color='#701A31'><b>OculoEdge • Universidad Tecnológica de Tehuacán • FEMECI Puebla 2026</b></font>",
        ParagraphStyle('Hdr', fontName='Helvetica-Bold', fontSize=13, alignment=1, leading=16, textColor=c_primary)
    ))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceAfter=10))

    # Resumen de roles
    roles_data = [
        [Paragraph("<b>José Miguel Tapia Adán</b><br/><i>Líder / Orquestador</i>", body_style), Paragraph("<b>Apertura (Min 0-3) y Cierre (Min 9-10):</b> Problemática de diabetes en Puebla, déficit de especialistas en Tehuacán, propuesta de valor de OculoEdge e impacto comunitario.", body_style)],
        [Paragraph("<b>Samuel Gutiérrez Tapia</b><br/><i>Ingeniería y Pipeline</i>", body_style), Paragraph("<b>Metodología (Min 3-6):</b> Reto de ingeniería, por qué Edge AI offline (LFPDPPP), filtro de Ben Graham y modelo MobileNetV3 optimizado para CPU.", body_style)],
        [Paragraph("<b>Oswaldo Yahir Asis Ladino</b><br/><i>XAI y Resultados</i>", body_style), Paragraph("<b>Demostración en Vivo (Min 6-9):</b> Manejo de la app en la laptop frente a los jueces, mapa térmico Grad-CAM, matriz de confusión y curva ROC (AUC=0.964).", body_style)]
    ]
    t_roles = Table(roles_data, colWidths=[2.2 * inch, 4.8 * inch])
    t_roles.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_roles)
    story.append(Spacer(1, 10))

    # SECCIÓN 1: GUION MINUTO A MINUTO
    story.append(Paragraph("1. GUION MINUTO A MINUTO (PITCH DE 10 MINUTOS)", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_primary, spaceAfter=6))

    story.append(Paragraph("Minuto 0:00 - 2:45 • Apertura y Problema en Puebla (José Miguel)", h2_style))
    box_jm = [
        [Paragraph(
            "«Buenos días, miembros del comité evaluador. Somos estudiantes de la Universidad Tecnológica de Tehuacán. "
            "¿Sabían que en Puebla más del 15% de la población adulta vive con diabetes y que la retinopatía diabética es la causa #1 "
            "de ceguera en edad laboral? El 90% de los casos se previenen a tiempo, pero en Tehuacán y la Sierra Negra no hay especialistas "
            "y una cita tarda hasta 8 meses en Puebla capital. Creamos <b>OculoEdge</b>: triaje oftalmológico inteligente con Edge AI que funciona "
            "en menos de 150 ms sin internet. Samuel les explicará la ingeniería del sistema.»",
            speech_style
        )]
    ]
    t_jm = Table(box_jm, colWidths=[7.0 * inch])
    t_jm.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FEF3C7')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#D97706')),
        ('LEFTPADDING', (0, 0), (-1, -1), 8), ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
    ]))
    story.append(t_jm)

    story.append(Paragraph("Minuto 2:45 - 5:30 • Reto de Ingeniería y Preprocesamiento (Samuel)", h2_style))
    box_sg = [
        [Paragraph(
            "«El reto fue: ¿cómo llevar visión artificial médica a clínicas rurales sin internet ni GPUs caras? "
            "Las soluciones en la nube fallan por falta de conectividad y violan la LFPDPPP al subir fotos de retinas a servidores extranjeros. "
            "Diseñamos un pipeline Edge AI con dos pilares: (1) <b>Filtro Ben Graham</b>: resta la iluminación global y resalta microaneurismas oscuros; "
            "(2) <b>MobileNetV3-Large</b>: modelo liviano de 18 MB que infiere en 142 ms en CPU. Clasifica en la escala ICDR (0 a 4) y dicta si el caso es Referible o No. "
            "Oswaldo les mostrará la demo en vivo.»",
            speech_style
        )]
    ]
    t_sg = Table(box_sg, colWidths=[7.0 * inch])
    t_sg.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#E0F2FE')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#0284C7')),
        ('LEFTPADDING', (0, 0), (-1, -1), 8), ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
    ]))
    story.append(t_sg)

    story.append(Paragraph("Minuto 5:30 - 8:15 • Demo en Vivo, Grad-CAM y Métricas (Oswaldo)", h2_style))
    box_oy = [
        [Paragraph(
            "«Los médicos desconfían de la IA porque es una 'caja negra'. Para resolver esto, implementamos <b>Grad-CAM</b>. "
            "<i>(Muestra la laptop y da clic en un caso)</i>. En 140 ms, OculoEdge genera este mapa de calor termográfico que resalta exactamente "
            "los microaneurismas y exudados duros. Y con este botón, descarga la ficha clínica PDF para el paciente. "
            "Evaluado sobre 1,332 imágenes (MESSIDOR-2 y EyePACS), logramos un <b>ROC-AUC de 0.964</b>, <b>Sensibilidad del 95.2%</b> y "
            "<b>Especificidad del 93.6%</b>. Una alta sensibilidad es vital para que ningún caso grave se quede sin canalizar.»",
            speech_style
        )]
    ]
    t_oy = Table(box_oy, colWidths=[7.0 * inch])
    t_oy.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F3E8FF')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#9333EA')),
        ('LEFTPADDING', (0, 0), (-1, -1), 8), ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
    ]))
    story.append(t_oy)

    story.append(Paragraph("Minuto 8:15 - 9:30 • Cierre e Impacto Social (José Miguel)", h2_style))
    box_cl = [
        [Paragraph(
            "«OculoEdge es una herramienta funcional y ética diseñada para la atención primaria en Puebla. Democratiza el acceso visual, "
            "protege los datos y ayuda a salvar la vista de miles de personas. Agradecemos a la UTT y al jurado; quedamos a su disposición para preguntas.»",
            speech_style
        )]
    ]
    t_cl = Table(box_cl, colWidths=[7.0 * inch])
    t_cl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#DCFCE7')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#16A34A')),
        ('LEFTPADDING', (0, 0), (-1, -1), 8), ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
    ]))
    story.append(t_cl)

    story.append(PageBreak())

    # SECCIÓN 2: BANCO DE PREGUNTAS TRAMPA
    story.append(Paragraph("2. BANCO DE PREGUNTAS TRAMPA DEL JURADO (RESPUESTAS MODELO)", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_primary, spaceAfter=8))

    qa_list = [
        (
            "1. ¿Por qué no usaron una API comercial en la nube como OpenAI o Claude?",
            "Samuel / José Miguel: «Por dos razones: (1) Brecha digital en la Sierra Negra (no hay internet de banda ancha confiable); (2) Ley Federal de Protección de Datos Personales (LFPDPPP), ya que la retina es un dato biométrico sensible que no debe viajar a servidores comerciales extranjeros. OculoEdge procesa 100% en local con costo cero por consulta.»"
        ),
        (
            "2. ¿Dónde consiguieron las fotos? ¿Tienen aval bioético para experimentar con pacientes?",
            "José Miguel / Oswaldo: «Utilizamos dos bancos biomédicos internacionales abiertos y validados: MESSIDOR-2 y EyePACS (más de 35,000 retinografías anonimizadas bajo la Declaración de Helsinki). Al ser datos abiertos desidentificados, la convocatoria oficial no exige el Formato FE-04 de experimentación invasiva en esta fase.»"
        ),
        (
            "3. ¿Por qué MobileNetV3 y no ResNet-50 o un Vision Transformer?",
            "Samuel: «Por eficiencia en el borde: ResNet pesa 100 MB y un Vision Transformer exige GPU dedicada, tardando segundos por foto en una laptop común. MobileNetV3 pesa 18.4 MB (4.8 MB en TFLite), corre en CPU en 142 ms y mantiene una exactitud competitiva con pérdida de menos del 1.5% respecto a modelos pesados.»"
        ),
        (
            "4. ¿Qué hace matemáticamente el filtro de Ben Graham?",
            "Samuel: «Aplica sustracción Gaussiana local: 4·I - 4·GaussianBlur(I, σ) + 128. Elimina las frecuencias espaciales bajas (la iluminación global del ojo que varía según la cámara) y realza las frecuencias altas (bordes nítidos de microaneurismas y exudados lipídicos).»"
        ),
        (
            "5. ¿Cómo funciona matemáticamente Grad-CAM?",
            "Oswaldo: «Calculamos la derivada parcial de la puntuación de la clase respecto a los mapas de activación de la última capa convolucional. Hacemos un promedio global (GAP) de esos gradientes para ponderar la importancia de cada canal y aplicamos ReLU para conservar solo las características que respaldan positivamente la lesión.»"
        ),
        (
            "6. ¿Por qué la Sensibilidad es más importante que la Precisión en medicina?",
            "Oswaldo: «Porque en triaje de primer contacto el peor error es un falso negativo: decirle a alguien con daño severo que está sano, causando que pierda la vista. Una sensibilidad de 95.2% asegura que casi ningún caso grave escape; si hay un falso positivo menor, el especialista en segundo nivel lo descarta sin riesgo para el paciente.»"
        ),
        (
            "7. ¿OculoEdge va a sustituir a los oftalmólogos?",
            "José Miguel: «No. Es una herramienta de triaje primario y soporte a la decisión médica. Sirve como filtro en centros de salud rurales para canalizar a quienes requieren tratamiento urgente y descongestionar hospitales. El diagnóstico definitivo siempre es del médico especialista.»"
        )
    ]

    for q, a in qa_list:
        story.append(Paragraph(f"<b>{q}</b>", h2_style))
        story.append(Paragraph(a, body_style))
        story.append(Spacer(1, 4))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[Guía PDF] Generada con éxito: {pdf_filename} ({os.path.getsize(pdf_filename)} bytes)")
    return pdf_filename


if __name__ == "__main__":
    build_defense_guide_pdf()
