"""Project content for review; does not replace official signed forms."""
try:
    from .pdf_builder import build
except ImportError:
    from pdf_builder import build

def build_protocol_pdf():
    return build("protocolo/protocolo_investigacion_femeci.md", "protocolo/Protocolo_OculoEdge_FEMECI_Puebla_2026.pdf", "FEMECI Puebla 2026 | Protocolo de ingeniería | 11 de octubre de 2026", figures=True)

def build_f01_pdf():
    return build("protocolo/F01_resumen_ejecutivo.md", "protocolo/Resumen_Ejecutivo_F01_OculoEdge.pdf", "Contenido para trasladar al formato F-01 oficial")

if __name__ == "__main__":
    build_protocol_pdf()
    build_f01_pdf()
