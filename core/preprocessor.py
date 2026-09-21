"""
OculoEdge - Módulo de Preprocesamiento de Imágenes de Retina
Implementa el algoritmo de normalización de iluminación y realce de lesiones
desarrollado por Ben Graham (Kaggle Diabetic Retinopathy Winner), recorte circular
y extracción de canal verde optimizado para diagnóstico oftalmológico.
"""

import cv2
import numpy as np
from PIL import Image
import io
import base64
from typing import Tuple, Dict, Any


def crop_image_from_gray(img: np.ndarray, tol: int = 7) -> np.ndarray:
    """
    Recorta los bordes negros inertes que rodean el globo ocular en retinografías.
    tol: Umbral de tolerancia de intensidad para considerar fondo negro.
    """
    if img.ndim == 2:
        mask = img > tol
        return img[np.ix_(mask.any(1), mask.any(0))]
    elif img.ndim == 3:
        gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        mask = gray_img > tol
        check_shape = img[:, :, 0][np.ix_(mask.any(1), mask.any(0))].shape[0]
        if check_shape == 0:
            return img  # Imagen demasiado oscura, devolver original
        else:
            img1 = img[:, :, 0][np.ix_(mask.any(1), mask.any(0))]
            img2 = img[:, :, 1][np.ix_(mask.any(1), mask.any(0))]
            img3 = img[:, :, 2][np.ix_(mask.any(1), mask.any(0))]
            return np.stack([img1, img2, img3], axis=-1)
    return img


def ben_graham_filter(image: np.ndarray, sigma_x: int = 30) -> np.ndarray:
    """
    Aplica la fórmula de sustracción Gaussiana local de Ben Graham:
    I_norm = 4 * I - 4 * GaussianBlur(I, sigma) + 128
    Esto elimina variaciones de iluminación entre diferentes cámaras retinales
    y maximiza la visibilidad de microaneurismas y exudados.
    """
    blurred = cv2.GaussianBlur(image, (0, 0), sigma_x)
    return cv2.addWeighted(image, 4, blurred, -4, 128)


def enhance_retina_image(image_np: np.ndarray, target_size: Tuple[int, int] = (384, 384)) -> Tuple[np.ndarray, np.ndarray]:
    """
    Pipeline completo de preprocesamiento clínico:
    1. Recorte de margen inerte.
    2. Redimensionamiento a target_size.
    3. Aplicación de filtro Ben Graham.
    4. Aplicación de máscara circular para limpiar artefactos en los bordes.

    Retorna: (imagen_recortada_rgb, imagen_filtrada_ben_graham)
    """
    # 1. Recorte inteligente
    cropped = crop_image_from_gray(image_np)
    if cropped.shape[0] < 20 or cropped.shape[1] < 20:
        cropped = image_np

    # 2. Redimensionar
    resized = cv2.resize(cropped, target_size, interpolation=cv2.INTER_AREA)

    # 3. Filtro Ben Graham
    filtered = ben_graham_filter(resized, sigma_x=target_size[0] // 10)

    # 4. Máscara circular
    mask = np.zeros(target_size, dtype=np.uint8)
    center = (target_size[0] // 2, target_size[1] // 2)
    radius = int(target_size[0] * 0.48)
    cv2.circle(mask, center, radius, 1, -1)

    filtered_masked = cv2.bitwise_and(filtered, filtered, mask=mask)
    # Rellenar exterior con 128 (gris neutro característico de Ben Graham)
    exterior_mask = (mask == 0)
    filtered_masked[exterior_mask] = 128

    return resized, filtered_masked


def clahe_green_channel(image_rgb: np.ndarray) -> np.ndarray:
    """
    Aplica ecualización adaptativa de histograma (CLAHE) en el canal verde,
    que es el canal espectral con mayor absorción de hemoglobina y contraste de lesiones.
    """
    green_channel = image_rgb[:, :, 1]
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced_green = clahe.apply(green_channel)
    enhanced_rgb = image_rgb.copy()
    enhanced_rgb[:, :, 1] = enhanced_green
    return enhanced_rgb


def np_to_base64(image_np: np.ndarray, format: str = "JPEG") -> str:
    """Convierte una matriz NumPy RGB a cadena Base64 para consumo en API/Web."""
    pil_img = Image.fromarray(image_np.astype(np.uint8))
    buffered = io.BytesIO()
    pil_img.save(buffered, format=format, quality=90)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/{format.lower()};base64,{img_str}"


def base64_to_np(b64_str: str) -> np.ndarray:
    """Convierte una cadena Base64 a matriz NumPy RGB."""
    if "," in b64_str:
        b64_str = b64_str.split(",")[1]
    img_data = base64.b64decode(b64_str)
    pil_img = Image.open(io.BytesIO(img_data)).convert("RGB")
    return np.array(pil_img)
