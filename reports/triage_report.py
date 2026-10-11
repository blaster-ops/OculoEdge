"""Research report from one immutable analysis; QR authenticates its canonical record."""
import io
from html import escape
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing

def generate_pdf_report(patient_name, patient_id, patient_age, eye_side, diagnosis_data,
                        original_img_np, gradcam_img_np, output_path=None, record=None):
    """This is an experimental result sheet, not a clinical certificate."""
    record = record or {"payload": {"analysis_id": "sin-registro", "created_at": "sin-fecha"},
                        "sha256": "sin-registro", "signature": "sin-firma"}
    payload = record["payload"]
    buffer = io.BytesIO()
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Small", fontName="Helvetica", fontSize=8, leading=11,
                              textColor=colors.HexColor("#334155")))
    styles.add(ParagraphStyle(name="Banner", fontName="Helvetica-Bold", fontSize=11, leading=15,
                              textColor=colors.HexColor(diagnosis_data.get("badge_color", "#64748b"))))
    def p(value, style="Small"):
        return Paragraph(escape(str(value)), styles[style])
    story = [p("OculoEdge", "Title"), p("UTT · FEMECI Puebla 2026 · Informe experimental"),
             p("INVESTIGACIÓN: sin validación clínica. No usar para diagnóstico, descarte de enfermedad o tratamiento."),
             Spacer(1, 10)]
    rows = [[p("Identificación"), p(patient_name or "Anónimo"), p("Folio"), p(patient_id or "Sin folio")],
            [p("Edad"), p(patient_age if patient_age is not None else "No registrada"), p("Ojo"), p(eye_side)],
            [p("Análisis"), p(payload["analysis_id"][:12]), p("Fecha"), p(payload["created_at"])]]
    table = Table(rows, colWidths=[65, 200, 45, 210])
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
                              ("VALIGN", (0, 0), (-1, -1), "TOP"), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story += [table, Spacer(1, 12), p(diagnosis_data["diagnosis"], "Banner"),
              p(diagnosis_data["clinical_findings"]), Spacer(1, 5), p(diagnosis_data["recommendation"])]
    source = payload.get("source", {})
    engine = diagnosis_data.get("engine", {})
    story += [Spacer(1, 8), p(f"Entrada: {source.get('kind', 'archivo')} · Motor: {engine.get('mode', 'heuristic')}"),
              p("Confianza clínica: no disponible. Las puntuaciones neuronales, si existen, no están calibradas."),
              p(f"Explicación: {payload.get('explanation_method', 'rule_mask')}")]
    metrics = diagnosis_data.get("biomarker_metrics", {})
    if metrics:
        story += [Spacer(1, 10), p("Mediciones de imagen (no hallazgos clínicos confirmados)", "Heading3")]
        rows = [[p("Píxeles oscuros"), p(metrics["dark_lesion_pixels"]),
                 p("Píxeles brillantes"), p(metrics["exudate_pixels"])],
                [p("Bordes internos"), p(metrics["disc_vascular_edges"]),
                 p("Cuadrantes con señal"), p(f"{metrics['quadrants_damaged']} / 4")]]
        table = Table(rows, colWidths=[150, 110, 150, 110])
        table.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), .3, colors.lightgrey),
                                  ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
        story.append(table)
    def image(array):
        stream = io.BytesIO()
        Image.fromarray(array).save(stream, format="PNG")
        stream.seek(0)
        return RLImage(stream, width=174, height=174)
    story += [Spacer(1, 12), Table([[image(original_img_np), image(gradcam_img_np)],
                                   [p("Imagen recortada"), p("Evidencia del cálculo")]], colWidths=[260, 260])]
    story += [Spacer(1, 10), p("Trazabilidad y verificación local", "Heading3")]
    qr = QrCodeWidget(f"OCULOEDGE2|HASH:{record['sha256']}|MAC:{record['signature']}")
    bounds = qr.getBounds()
    side = 62
    draw = Drawing(side, side, transform=[side/(bounds[2]-bounds[0]), 0, 0, side/(bounds[3]-bounds[1]), 0, 0])
    draw.add(qr)
    text = [p("SHA-256 del registro canónico (incluye resultado y hashes de imágenes):"),
            p(record["sha256"]), p("HMAC-SHA256 verificable únicamente con la clave local del equipo emisor."),
            p("Conserve el archivo JSON de verificación junto al PDF. El QR no contiene nombre ni folio.")]
    story.append(Table([[text, draw]], colWidths=[450, 70]))
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=46, rightMargin=46, topMargin=28, bottomMargin=28)
    def footer(canvas, doc):
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#64748b"))
        canvas.drawString(46, 16, "OculoEdge 2.0 · Resultado experimental · Sin certificación clínica")
        canvas.drawRightString(566, 16, str(doc.page))
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    data = buffer.getvalue()
    if output_path:
        from pathlib import Path
        Path(output_path).write_bytes(data)
    return data
