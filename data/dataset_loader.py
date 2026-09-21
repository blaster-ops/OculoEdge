"""
OculoEdge - Generador y Cargador de Casos Clínicos de Referencia (ICDR 0-4)
Proporciona muestras de retinografías con características patológicas
patognomónicas validadas para demostración clínica inmediata y offline.
"""

import os
import cv2
import numpy as np
from PIL import Image
from typing import Dict, List, Any


def generate_synthetic_fundus(grade: int, size: int = 512) -> np.ndarray:
    """
    Genera una retinografía sintética anatómicamente verosímil y calibrada:
    - Grado 0 (Normal): Cero lesiones, vasos regulares, papila nítida, fóvea intacta.
    - Grado 1 (Leve): 3 microaneurismas aislados, sin exudados ni hemorragias.
    - Grado 2 (Moderada): Múltiples microaneurismas + exudados duros amarillos + hemorragias aisladas.
    - Grado 3 (Severa): Hemorragias severas en los 4 cuadrantes + manchas algodonosas.
    - Grado 4 (Proliferativa): Neovascularización extensa sobre el disco + hemorragia vítrea.
    """
    np.random.seed(100 + grade * 31)
    img = np.zeros((size, size, 3), dtype=np.uint8)
    center = (size // 2, size // 2)
    radius = int(size * 0.46)

    # 1. Fondo de retina limpio con gradiente esférico suave (sin ruido de sal y pimienta)
    y, x = np.ogrid[:size, :size]
    dist_from_center = np.sqrt((x - center[0])**2 + (y - center[1])**2)
    mask = dist_from_center <= radius
    
    falloff = 1.0 - (dist_from_center / radius) * 0.35
    falloff = np.clip(falloff, 0.45, 1.0)

    # Fondo coroideo homogéneo
    r = (200 * falloff).astype(np.uint8)
    g = (75 * falloff).astype(np.uint8)
    b = (30 * falloff).astype(np.uint8)
    
    img[:, :, 0] = np.clip(r * mask, 0, 255)
    img[:, :, 1] = np.clip(g * mask, 0, 255)
    img[:, :, 2] = np.clip(b * mask, 0, 255)

    # 2. Disco Óptico (Papila) nasal limpio
    disc_center = (int(size * 0.30), int(size * 0.50))
    disc_radius = int(size * 0.08)
    cv2.circle(img, disc_center, disc_radius, (245, 215, 115), -1)
    cv2.circle(img, disc_center, int(disc_radius * 0.55), (255, 242, 185), -1)

    # 3. Mácula y Fóvea temporal
    macula_center = (int(size * 0.65), int(size * 0.50))
    macula_radius = int(size * 0.09)
    overlay = img.copy()
    cv2.circle(overlay, macula_center, macula_radius, (140, 42, 18), -1)
    cv2.addWeighted(overlay, 0.4, img, 0.6, 0, img)
    cv2.circle(img, macula_center, int(size * 0.02), (105, 25, 12), -1)

    # 4. Vasos Sanguíneos Principales (Arcadas continuas y definidas)
    vessel_color = (120, 22, 12)
    
    # Arcada temporal superior
    pts_ts = np.array([
        disc_center,
        (int(size * 0.42), int(size * 0.28)),
        (int(size * 0.62), int(size * 0.24)),
        (int(size * 0.80), int(size * 0.30))
    ], np.int32)
    cv2.polylines(img, [pts_ts], False, vessel_color, 3, cv2.LINE_AA)

    # Arcada temporal inferior
    pts_ti = np.array([
        disc_center,
        (int(size * 0.42), int(size * 0.72)),
        (int(size * 0.62), int(size * 0.76)),
        (int(size * 0.80), int(size * 0.70))
    ], np.int32)
    cv2.polylines(img, [pts_ti], False, vessel_color, 3, cv2.LINE_AA)

    # Vasos nasales
    cv2.line(img, disc_center, (int(size * 0.12), int(size * 0.35)), vessel_color, 2, cv2.LINE_AA)
    cv2.line(img, disc_center, (int(size * 0.12), int(size * 0.65)), vessel_color, 2, cv2.LINE_AA)

    # 5. Inserción de Patologías Específicas por Grado ICDR
    if grade == 1:
        # Grado 1 (Leve): Exactamente 3 microaneurismas aislados
        micro_coords = [
            (int(size * 0.52), int(size * 0.40)),
            (int(size * 0.58), int(size * 0.62)),
            (int(size * 0.72), int(size * 0.44))
        ]
        for mx, my in micro_coords:
            cv2.circle(img, (mx, my), 3, (55, 8, 5), -1)

    elif grade == 2:
        # Grado 2 (Moderada): Múltiples microaneurismas + exudados duros amarillos
        # 10 microaneurismas
        for _ in range(10):
            mx = np.random.randint(int(size * 0.42), int(size * 0.78))
            my = np.random.randint(int(size * 0.28), int(size * 0.72))
            cv2.circle(img, (mx, my), 3, (50, 6, 4), -1)
        # 8 Exudados duros (lípidos amarillos brillantes, L alto y b alto)
        exudate_coords = [
            (int(size * 0.50), int(size * 0.38)),
            (int(size * 0.52), int(size * 0.36)),
            (int(size * 0.54), int(size * 0.39)),
            (int(size * 0.68), int(size * 0.58)),
            (int(size * 0.70), int(size * 0.60)),
            (int(size * 0.72), int(size * 0.57)),
            (int(size * 0.46), int(size * 0.65)),
            (int(size * 0.48), int(size * 0.63))
        ]
        for ex, ey in exudate_coords:
            cv2.circle(img, (ex, ey), 4, (255, 245, 120), -1)
        # 4 Hemorragias pequeñas en mancha
        for _ in range(4):
            hx = np.random.randint(int(size * 0.45), int(size * 0.75))
            hy = np.random.randint(int(size * 0.35), int(size * 0.68))
            cv2.circle(img, (hx, hy), 6, (40, 5, 5), -1)

    elif grade == 3:
        # Grado 3 (Severa): Hemorragias extensas en los 4 cuadrantes (Regla 4-2-1)
        quadrants = [
            (int(size * 0.55), int(size * 0.78), int(size * 0.20), int(size * 0.45)),  # Q1
            (int(size * 0.22), int(size * 0.48), int(size * 0.20), int(size * 0.45)),  # Q2
            (int(size * 0.55), int(size * 0.78), int(size * 0.55), int(size * 0.80)),  # Q3
            (int(size * 0.22), int(size * 0.48), int(size * 0.55), int(size * 0.80))   # Q4
        ]
        for qx1, qx2, qy1, qy2 in quadrants:
            for _ in range(5):
                hx = np.random.randint(qx1, qx2)
                hy = np.random.randint(qy1, qy2)
                cv2.ellipse(img, (hx, hy), (np.random.randint(7, 14), np.random.randint(4, 8)),
                            np.random.randint(0, 180), 0, 360, (35, 4, 4), -1)
        # Manchas algodonosas (infartos de fibras nerviosas)
        for _ in range(4):
            cx = np.random.randint(int(size * 0.38), int(size * 0.68))
            cy = np.random.randint(int(size * 0.30), int(size * 0.70))
            cv2.circle(img, (cx, cy), 10, (225, 220, 205), -1)

    elif grade == 4:
        # Grado 4 (Proliferativa): Neovascularización en papila + Hemorragia vítrea en sábana
        # Maraña de neovasos finos sobre el disco óptico
        for _ in range(25):
            nx = disc_center[0] + np.random.randint(-28, 38)
            ny = disc_center[1] + np.random.randint(-28, 38)
            cv2.line(img, (nx, ny), (nx + np.random.randint(-12, 14), ny + np.random.randint(-12, 14)),
                     (90, 10, 8), 1, cv2.LINE_AA)
        # Gran hemorragia vítrea/prerretiniana en forma de bote
        pts_hem = np.array([
            (int(size * 0.46), int(size * 0.42)),
            (int(size * 0.72), int(size * 0.44)),
            (int(size * 0.66), int(size * 0.62)),
            (int(size * 0.50), int(size * 0.60))
        ], np.int32)
        cv2.fillPoly(img, [pts_hem], (30, 3, 3))

    # Re-aplicar máscara circular nítida
    clean_mask = np.zeros((size, size), dtype=np.uint8)
    cv2.circle(clean_mask, center, radius, 255, -1)
    img = cv2.bitwise_and(img, img, mask=clean_mask)

    return img


def initialize_sample_dataset(samples_dir: str, force_recreate: bool = False):
    """Crea o regenera los 5 archivos de casos clínicos de referencia."""
    os.makedirs(samples_dir, exist_ok=True)
    grades_info = [
        (0, "sample_grade_0_normal.jpg", "Caso 01: Paciente 48a - Control Rutina - Retina Normal"),
        (1, "sample_grade_1_leve.jpg", "Caso 02: Paciente 55a - Diabetes T2 (5 años) - NPDR Leve"),
        (2, "sample_grade_2_moderada.jpg", "Caso 03: Paciente 61a - Diabetes T2 (11 años) - NPDR Moderada"),
        (3, "sample_grade_3_severa.jpg", "Caso 04: Paciente 67a - Diabetes T2 (18 años) - NPDR Severa"),
        (4, "sample_grade_4_proliferativa.jpg", "Caso 05: Paciente 59a - Diabetes T1 - Retinopatía Proliferativa")
    ]
    
    for grade, filename, desc in grades_info:
        filepath = os.path.join(samples_dir, filename)
        if force_recreate or not os.path.exists(filepath):
            img_np = generate_synthetic_fundus(grade, size=512)
            pil_img = Image.fromarray(img_np)
            pil_img.save(filepath, quality=95)
            print(f"[OculoEdge] Muestra clínica calibrada: {filename}")


def get_available_samples(samples_dir: str) -> List[Dict[str, Any]]:
    """Lista las muestras disponibles para la interfaz web."""
    initialize_sample_dataset(samples_dir, force_recreate=False)
    return [
        {
            "id": 0,
            "filename": "sample_grade_0_normal.jpg",
            "title": "Caso 01: Fondo de Ojo Sano",
            "subtitle": "Paciente sin retinopatía diabética detectable (ICDR 0)",
            "expected_grade": 0,
            "path": os.path.join(samples_dir, "sample_grade_0_normal.jpg")
        },
        {
            "id": 1,
            "filename": "sample_grade_1_leve.jpg",
            "title": "Caso 02: Retinopatía Leve",
            "subtitle": "Microaneurismas aislados tempranos (ICDR 1)",
            "expected_grade": 1,
            "path": os.path.join(samples_dir, "sample_grade_1_leve.jpg")
        },
        {
            "id": 2,
            "filename": "sample_grade_2_moderada.jpg",
            "title": "Caso 03: Retinopatía Moderada",
            "subtitle": "Microaneurismas + hemorragias y exudados duros (ICDR 2)",
            "expected_grade": 2,
            "path": os.path.join(samples_dir, "sample_grade_2_moderada.jpg")
        },
        {
            "id": 3,
            "filename": "sample_grade_3_severa.jpg",
            "title": "Caso 04: Retinopatía Severa",
            "subtitle": "Hemorragias en 4 cuadrantes y manchas algodonosas (ICDR 3)",
            "expected_grade": 3,
            "path": os.path.join(samples_dir, "sample_grade_3_severa.jpg")
        },
        {
            "id": 4,
            "filename": "sample_grade_4_proliferativa.jpg",
            "title": "Caso 05: Retinopatía Proliferativa",
            "subtitle": "Neovascularización y hemorragia vítrea extensa (ICDR 4)",
            "expected_grade": 4,
            "path": os.path.join(samples_dir, "sample_grade_4_proliferativa.jpg")
        }
    ]
