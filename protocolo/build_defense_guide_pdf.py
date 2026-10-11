"""Generate the defense guide from the current reviewed project content."""
try:
    from .pdf_builder import build
except ImportError:
    from pdf_builder import build

def build_defense_guide_pdf():
    return build("protocolo/guia_defensa_jurado.md", "protocolo/Guia_Defensa_Jurado_OculoEdge.pdf", "Guía de exposición y demostración | FEMECI Puebla 2026")

if __name__ == "__main__":
    build_defense_guide_pdf()
