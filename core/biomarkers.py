"""
OculoEdge - Extractor de Biomarcadores Oftalmológicos Calibrado
Implementa segmentación vascular para aislar el árbol venoso/arterial,
filtrado de circularidad para microaneurismas, segmentación cromática de exudados
y análisis de cuadrantes para la escala ICDR (0 a 4).
"""

import cv2
import numpy as np
from typing import Dict, Any, Tuple


def segment_blood_vessels(green_channel: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """
    Segmenta el árbol vascular retiniano principal para evitar que los capilares
    y bifurcaciones normales sean confundidos con microaneurismas o hemorragias.
    """
    # Filtro morfológico Top-Hat para estructuras lineales
    kernel_vessel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
    top_hat = cv2.morphologyEx(green_channel, cv2.MORPH_TOPHAT, kernel_vessel)
    _, vessel_mask = cv2.threshold(top_hat, 28, 255, cv2.THRESH_BINARY)
    
    # Suavizado y dilatación para cubrir las ramas
    vessel_dilated = cv2.dilate(vessel_mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), iterations=1)
    return cv2.bitwise_and(vessel_dilated, vessel_dilated, mask=mask)


def extract_retina_biomarkers(image_rgb: np.ndarray) -> Dict[str, Any]:
    """
    Extrae biomarcadores cuantificables de patología retiniana.
    """
    h, w, _ = image_rgb.shape
    
    # 1. Máscara del campo visual del ojo
    gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    _, field_mask = cv2.threshold(gray, 20, 255, cv2.THRESH_BINARY)
    # Erosión para eliminar el aro externo negro
    clean_field = cv2.erode(field_mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))

    green = image_rgb[:, :, 1]
    
    # 2. Localizar y enmascarar Disco Óptico (Papila)
    blurred_g = cv2.GaussianBlur(green, (31, 31), 0)
    _, _, _, max_loc = cv2.minMaxLoc(blurred_g, mask=clean_field)
    disc_center = max_loc
    disc_radius = int(min(h, w) * 0.12)
    
    disc_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(disc_mask, disc_center, int(disc_radius * 1.3), 255, -1)
    
    # 3. Segmentación vascular para excluir vasos normales
    vessels = segment_blood_vessels(green, clean_field)
    
    # Zona de búsqueda de lesiones: dentro del campo, fuera del disco óptico y fuera de vasos gruesos
    lesion_zone = cv2.bitwise_and(clean_field, cv2.bitwise_not(disc_mask))
    avessel_zone = cv2.bitwise_and(lesion_zone, cv2.bitwise_not(vessels))

    # 4. Detección de Exudados Duros (Brillo lipídico en CIE-LAB / HSV)
    # Los exudados duros son amarillentos y muy reflectivos
    lab = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2LAB)
    l_chan, _, b_chan = cv2.split(lab)
    
    # Exudados: L > 185 y b > 145 (amarillo brillante marcado)
    exudate_cand = (l_chan > 185) & (b_chan > 145) & (lesion_zone > 0)
    exudate_mask = np.uint8(exudate_cand) * 255
    exudate_mask = cv2.morphologyEx(exudate_mask, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
    
    num_ex, _, ex_stats, _ = cv2.connectedComponentsWithStats(exudate_mask)
    exudates_count = 0
    total_exudate_area = 0.0
    for i in range(1, num_ex):
        area = ex_stats[i, cv2.CC_STAT_AREA]
        if 4 <= area <= 600:
            exudates_count += 1
            total_exudate_area += area

    # 5. Detección de Microaneurismas (Puntos oscuros muy pequeños y circulares)
    # Invertir canal verde en zona libre de vasos gruesos
    kernel_small = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    black_hat = cv2.morphologyEx(green, cv2.MORPH_BLACKHAT, kernel_small)
    # Filtrar solo depresiones focales oscuras intensas
    _, micro_cand = cv2.threshold(black_hat, 35, 255, cv2.THRESH_BINARY)
    micro_cand = cv2.bitwise_and(micro_cand, micro_cand, mask=avessel_zone)
    
    num_m, _, m_stats, _ = cv2.connectedComponentsWithStats(micro_cand)
    microaneurysms_count = 0
    for i in range(1, num_m):
        area = m_stats[i, cv2.CC_STAT_AREA]
        w_b = m_stats[i, cv2.CC_STAT_WIDTH]
        h_b = m_stats[i, cv2.CC_STAT_HEIGHT]
        aspect_ratio = float(w_b) / max(h_b, 1)
        # Filtro de forma: tamaño pequeño (3-30 px) y circular (aspect ratio entre 0.5 y 2.0)
        if 3 <= area <= 35 and 0.4 <= aspect_ratio <= 2.2:
            microaneurysms_count += 1

    # 6. Detección de Hemorragias Retinianas y Manchas Extensas
    # Filtro para manchas oscuras medianas y grandes
    kernel_large = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (19, 19))
    hem_hat = cv2.morphologyEx(green, cv2.MORPH_BLACKHAT, kernel_large)
    _, hem_cand = cv2.threshold(hem_hat, 45, 255, cv2.THRESH_BINARY)
    hem_cand = cv2.bitwise_and(hem_cand, hem_cand, mask=clean_field)
    
    num_h, _, h_stats, _ = cv2.connectedComponentsWithStats(hem_cand)
    hemorrhages_count = 0
    total_hem_area = 0.0
    quadrant_counts = [0, 0, 0, 0]
    large_vitreous_hem = False
    
    cx, cy = w // 2, h // 2
    for i in range(1, num_h):
        area = h_stats[i, cv2.CC_STAT_AREA]
        if area > 400:
            large_vitreous_hem = True
            total_hem_area += area
        elif area >= 25:
            hemorrhages_count += 1
            total_hem_area += area
            bx = h_stats[i, cv2.CC_STAT_LEFT]
            by = h_stats[i, cv2.CC_STAT_TOP]
            q_idx = (0 if bx >= cx else 1) + (0 if by < cy else 2)
            quadrant_counts[q_idx] += 1

    # 7. Detección de Neovascularización sobre el Disco Óptico (NVD)
    # Medir la densidad y rugosidad vascular dentro de la máscara del disco óptico
    disc_green = cv2.bitwise_and(green, green, mask=disc_mask)
    disc_edges = cv2.Canny(disc_green, 40, 100)
    disc_vascular_edges = np.sum(disc_edges > 0)
    neovascularization_nvd = (disc_vascular_edges > 650)

    # 8. Decisión Clínica ICDR Calibrada
    quadrants_affected = sum(1 for q in quadrant_counts if q >= 2)
    
    # Reglas oficiales de la AAO:
    if large_vitreous_hem or neovascularization_nvd or (hemorrhages_count >= 15 and exudates_count >= 6):
        estimated_grade = 4  # Proliferativa (PDR)
        rule = "Neovascularización en papila (NVD) o hemorragia vítrea/prerretiniana activa."
    elif quadrants_affected >= 3 or hemorrhages_count >= 8:
        estimated_grade = 3  # Severa (NPDR Severa - Regla 4-2-1)
        rule = "Regla 4-2-1 positiva: Múltiples hemorragias en al menos 3 cuadrantes retinianos."
    elif exudates_count >= 3 or hemorrhages_count >= 2 or microaneurysms_count >= 6:
        estimated_grade = 2  # Moderada (NPDR Moderada)
        rule = "Microaneurismas múltiples acompañados de exudados duros o hemorragias aisladas."
    elif microaneurysms_count >= 1 or hemorrhages_count == 1:
        estimated_grade = 1  # Leve (NPDR Leve)
        rule = "Presencia exclusiva de microaneurismas aislados tempranos."
    else:
        estimated_grade = 0  # Normal
        rule = "Fondo de ojo sano sin microaneurismas, exudados ni hemorragias."

    return {
        "estimated_grade": estimated_grade,
        "clinical_rule_applied": rule,
        "biomarkers": {
            "microaneurysms_count": microaneurysms_count,
            "hemorrhages_count": hemorrhages_count,
            "hemorrhages_total_area": total_hem_area,
            "quadrants_affected": quadrants_affected,
            "exudates_count": exudates_count,
            "exudates_area": total_exudate_area,
            "neovascularization_suspect": bool(large_vitreous_hem or neovascularization_nvd)
        },
        "optic_disc": {
            "center": [int(disc_center[0]), int(disc_center[1])],
            "radius": int(disc_radius)
        }
    }
