"""Acquisition checks. Passing is not proof that an image is retinal."""
import cv2
import numpy as np

def assess_image_quality(image):
    if not isinstance(image, np.ndarray) or image.ndim != 3 or image.shape[2] != 3 or image.dtype != np.uint8:
        raise ValueError("Se requiere una imagen RGB uint8.")
    h, w = image.shape[:2]
    if min(h, w) == 0:
        raise ValueError("Imagen vacía.")
    small = cv2.resize(image, (384, 384), interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(small, cv2.COLOR_RGB2GRAY)
    visible = gray > 12
    values = gray[visible]
    coverage = float(visible.mean())
    contrast = float(values.std()) if values.size else 0.0
    focus = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    r, g, b = [small[:, :, i].astype(np.int16) for i in range(3)]
    retinal_color = float(((r > g + 15) & (r > b + 30) & visible).sum() / max(1, visible.sum()))
    reasons = []
    if min(h, w) < 128:
        reasons.append("Resolución insuficiente: mínimo 128 píxeles por lado")
    if coverage < .2:
        reasons.append("Campo visible insuficiente o exposición demasiado baja")
    if contrast < 7:
        reasons.append("Contraste insuficiente o imagen uniforme")
    if float((gray > 245).mean()) > .65:
        reasons.append("Sobreexposición excesiva")
    if focus < 8:
        reasons.append("Imagen desenfocada o sin detalle suficiente")
    if retinal_color < .2:
        reasons.append("No se identifica un campo compatible con una retinografía en color")
    return {"evaluable": not reasons, "reasons": reasons,
            "metrics": {"width": w, "height": h, "visible_fraction": round(coverage, 3),
                        "contrast": round(contrast, 2), "focus_variance": round(focus, 2),
                        "retinal_color_fraction": round(retinal_color, 3)},
            "notice": "Control exploratorio de adquisición; no confirma origen retiniano ni calidad diagnóstica."}
