"""Render the reviewed Markdown content without invented official endorsements."""
from html import escape
from pathlib import Path
import re
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak

ROOT = Path(__file__).resolve().parents[1]

def inline(text):
    text = escape(text.replace("–", "-").replace("—", "-").replace("≥", ">=").replace("≤", "<="))
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    return re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", text)

def build(markdown, output, subtitle, figures=False):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("OEtitle",fontName="Helvetica-Bold",fontSize=22,leading=27,textColor=colors.HexColor("#164e63"),spaceAfter=12))
    styles.add(ParagraphStyle("OEheading",fontName="Helvetica-Bold",fontSize=12,leading=16,textColor=colors.HexColor("#164e63"),spaceBefore=12,spaceAfter=6,keepWithNext=True))
    styles.add(ParagraphStyle("OEbody",fontName="Helvetica",fontSize=10,leading=14,spaceAfter=8,textColor=colors.HexColor("#253648")))
    styles.add(ParagraphStyle("OEbullet",parent=styles["OEbody"],leftIndent=12,firstLineIndent=-9,spaceAfter=5))
    styles.add(ParagraphStyle("OEcaption",parent=styles["OEbody"],fontSize=8.5,leading=12,textColor=colors.HexColor("#526576")))
    story=[]; block=[]; references=[]; in_references=False
    def flush():
        if block:
            story.append(Paragraph(inline(" ".join(block)),styles["OEbody"]))
            block.clear()
    for line in (ROOT/markdown).read_text(encoding="utf-8").splitlines():
        if figures and (in_references or line=="## Referencias técnicas"):
            flush(); in_references=True
            if line!="## Referencias técnicas" and line.strip(): references.append(line)
            continue
        if line.startswith("# "):
            flush(); story.append(Paragraph(inline(line[2:]),styles["OEtitle"]))
            story.append(Paragraph(inline(subtitle),styles["OEcaption"])); story.append(Spacer(1,8))
        elif line.startswith("## "):
            flush()
            if line=="## Respuestas que deben poder defender": story.append(PageBreak())
            story.append(Paragraph(inline(line[3:]),styles["OEheading"]))
        elif re.match(r"^(- |\d+\. )",line):
            flush(); story.append(Paragraph(inline(line),styles["OEbullet"]))
        elif not line.strip(): flush()
        else: block.append(line.strip())
    flush()
    if figures:
        story.append(PageBreak())
        story.append(Paragraph("Anexo: evaluación de integración sintética",styles["OEheading"]))
        story.append(Paragraph("Cinco ilustraciones del repositorio. Los resultados comprueban esos casos; no son estimaciones de desempeño sobre pacientes. Datos y predicciones: benchmarks/metrics_summary.json y benchmarks/predictions.json.",styles["OEbody"]))
        for filename,caption in [("confusion_matrix.png","Patrones esperados y obtenidos en cinco muestras sintéticas. Un caso por patrón."),("roc_curve.png","ROC/AUC no disponible: el motor de reglas no produce puntuaciones probabilísticas.")]:
            image=Image(str(ROOT/"benchmarks"/filename)); image._restrictSize(420,205)
            story.append(image); story.append(Spacer(1,5)); story.append(Paragraph(caption,styles["OEcaption"]))
        if references:
            story.append(Paragraph("Referencias técnicas",styles["OEheading"]))
            story.append(Paragraph(inline(" ".join(references)),styles["OEcaption"]))
    output=ROOT/output; output.parent.mkdir(parents=True,exist_ok=True)
    def footer(canvas,doc):
        canvas.saveState(); canvas.setStrokeColor(colors.HexColor("#cbd5e1")); canvas.line(45,42,567,42)
        canvas.setFont("Helvetica",8); canvas.setFillColor(colors.HexColor("#526576"))
        canvas.drawString(45,29,"OculoEdge 2.0 | Investigación | Documento del equipo para revisión")
        canvas.drawRightString(567,29,str(doc.page)); canvas.restoreState()
    SimpleDocTemplate(str(output),pagesize=letter,leftMargin=45,rightMargin=45,topMargin=42,bottomMargin=58,title="OculoEdge - "+subtitle,author="Equipo OculoEdge, UTT").build(story,onFirstPage=footer,onLaterPages=footer)
    print(output)
    return output
