"""Image measurements and transparent experimental rules, not ICDR clinical criteria."""
import cv2
import numpy as np

def extract_retina_biomarkers(image_rgb):
    h, w = image_rgb.shape[:2]
    green = image_rgb[:, :, 1]
    y, x = np.ogrid[:h, :w]
    field = (x - w // 2) ** 2 + (y - h // 2) ** 2 < (min(h, w) * .44) ** 2
    blurred = cv2.GaussianBlur(green, (31, 31), 0)
    _, _, _, disc_center = cv2.minMaxLoc(blurred, mask=field.astype(np.uint8))
    disc = (x - disc_center[0]) ** 2 + (y - disc_center[1]) ** 2 < (min(h, w) * .15) ** 2
    search = field & ~disc
    red, g, blue = [image_rgb[:, :, i].astype(np.int16) for i in range(3)]
    exudates = (((red > 180) & (g > 160) & (red > blue + 40)) |
                ((red > 220) & (g > 200) & (blue < 155))) & search
    absolute_dark = (green < 22) & search
    focal_dark = (blurred.astype(np.int16) - green.astype(np.int16) > 50) & search
    dark = absolute_dark if absolute_dark.sum() >= focal_dark.sum() else focal_dark
    edges = cv2.Canny(green, 40, 100) > 0
    disc_inner = cv2.erode(disc.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    disc_edges = edges & disc_inner & field
    cy, cx = h // 2, w // 2
    quadrants = [int(dark[:cy, cx:].sum()), int(dark[:cy, :cx].sum()),
                 int(dark[cy:, cx:].sum()), int(dark[cy:, :cx].sum())]
    return {"metrics": {"dark_lesion_pixels": int(dark.sum()), "exudate_pixels": int(exudates.sum()),
                        "disc_vascular_edges": int(disc_edges.sum()),
                        "quadrants_damaged": sum(q > 120 for q in quadrants), "quadrant_pixels": quadrants},
            "dark_mask": dark, "bright_mask": exudates, "disc_mask": disc_edges,
            "optic_disc": {"center": list(disc_center)}, "field_mask": field}

def classify_features(features):
    m = features["metrics"]
    dark, bright, edges = m["dark_lesion_pixels"], m["exudate_pixels"], m["disc_vascular_edges"]
    dark_map, bright_map = features["dark_mask"], features["bright_mask"]
    if ((dark > 250 or bright > 40) and edges > 1400) or dark > 4500:
        grade, rule = 4, f"Regla experimental G4: {dark} píxeles oscuros; {edges} bordes internos."
        mask = dark_map | (features["disc_mask"] if edges > 1400 else False)
    elif m["quadrants_damaged"] == 4 or dark > 1200:
        grade, rule = 3, f"Regla experimental G3: {dark} píxeles oscuros en {m['quadrants_damaged']} cuadrantes. No equivale a la regla clínica 4-2-1."
        mask = dark_map
    elif bright > 40 or dark > 400:
        grade, rule = 2, f"Regla experimental G2: {bright} píxeles brillantes; {dark} píxeles oscuros."
        mask = bright_map | dark_map
    elif dark > 230:
        grade, rule = 1, f"Regla experimental G1: {dark} píxeles oscuros por encima del umbral 230."
        mask = dark_map
    else:
        grade, rule = 0, "Regla experimental G0: las mediciones no superan los umbrales de demostración. Esto no descarta enfermedad."
        mask = np.zeros_like(dark_map)
    return grade, rule, mask.astype(np.uint8) * 255
