"""
OculoEdge - Módulo de Explicabilidad Clínica (Grad-CAM)
Implementa Gradient-weighted Class Activation Mapping para visualizar y justificar
exactamente qué lesiones de la retina (microaneurismas, exudados, hemorragias o neovasos)
provocaron la predicción del modelo de Deep Learning.
"""

import torch
import cv2
import numpy as np
from typing import Tuple, Dict, Any, List
from core.model_engine import DiagnosticEngine


class GradCAMExplainer:
    """Generador de mapas de calor explicables mediante Grad-CAM sin fugas de memoria."""
    def __init__(self, engine: DiagnosticEngine):
        self.engine = engine
        self.model = engine.model
        self.device = engine.device
        
        self.gradients = None
        self.activations = None
        
        # Conectar hook en la última capa convolucional de MobileNetV3 (features[-1])
        target_layer = self.model.features[-1]
        target_layer.register_forward_hook(self._forward_hook)
        target_layer.register_full_backward_hook(self._backward_hook)

    def _forward_hook(self, module, input, output):
        self.activations = output.detach()

    def _backward_hook(self, module, grad_input, grad_output):
        if grad_output is not None and len(grad_output) > 0:
            self.gradients = grad_output[0].detach()

    def generate_heatmap(
        self,
        image_np: np.ndarray,
        target_class_id: int = None,
        alpha: float = 0.55
    ) -> Dict[str, Any]:
        """
        Calcula el mapa de activación Grad-CAM para la imagen y clase especificada.
        Retorna:
          - overlay_rgb: Imagen compuesta con mapa térmico superpuesto en RGB.
          - raw_heatmap_uint8: Mapa de calor normalizado en escala de grises [0, 255].
          - heatmap_colored_rgb: Mapa térmico termográfico puro (JET).
          - hotspots: Coordenadas y áreas de los focos clínicos de mayor activación.
        """
        self.model.eval()
        self.model.zero_grad(set_to_none=True)
        
        from core.preprocessor import enhance_retina_image
        resized_orig, processed_bg = enhance_retina_image(image_np, target_size=(384, 384))
        
        input_tensor = self.engine.transform(processed_bg).unsqueeze(0).to(self.device)
        input_tensor.requires_grad = True

        # Paso hacia adelante
        logits = self.model(input_tensor)
        
        if target_class_id is None:
            target_class_id = int(torch.argmax(logits, dim=1).item())

        score = logits[0, target_class_id]

        # Paso hacia atrás (backprop)
        self.model.zero_grad(set_to_none=True)
        score.backward()

        # 1. Ponderación global de gradientes (Global Average Pooling)
        if self.gradients is not None and self.activations is not None:
            pooled_gradients = torch.mean(self.gradients, dim=[0, 2, 3])
            activations = self.activations[0].clone()
            for i in range(activations.shape[0]):
                activations[i, :, :] *= pooled_gradients[i]

            # 2. Suma en los canales y aplicación de ReLU
            heatmap = torch.sum(activations, dim=0).cpu().numpy()
            heatmap = np.maximum(heatmap, 0)
            if np.max(heatmap) > 0:
                heatmap /= np.max(heatmap)
            else:
                heatmap = np.zeros_like(heatmap)
        else:
            # Fallback seguro si los gradientes son nulos
            heatmap = np.zeros((384, 384), dtype=np.float32)

        # 3. Limpiar tensores de gradiente para evitar memory leaks
        self.gradients = None
        self.activations = None
        self.model.zero_grad(set_to_none=True)
        input_tensor.grad = None

        # 4. Redimensionar mapa al tamaño de la imagen retiniana (384x384)
        heatmap_resized = cv2.resize(heatmap, (384, 384))
        heatmap_uint8 = np.uint8(255 * heatmap_resized)

        # 5. Aplicar mapa de color termográfico (JET)
        heatmap_colored = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
        heatmap_colored_rgb = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)

        # 6. Superposición ponderada con la imagen original recortada
        overlay = cv2.addWeighted(resized_orig, 1.0 - alpha, heatmap_colored_rgb, alpha, 0)

        # 7. Detección de puntos focales (Hotspots con umbral > 60% de activación)
        threshold_val = int(255 * 0.60)
        _, thresh_mask = cv2.threshold(heatmap_uint8, threshold_val, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        hotspots = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 20:  # Filtrar ruido microscópico
                x, y, w, h = cv2.boundingRect(cnt)
                hotspots.append({
                    "x": int(x),
                    "y": int(y),
                    "w": int(w),
                    "h": int(h),
                    "center": [int(x + w / 2), int(y + h / 2)],
                    "area": float(area)
                })

        return {
            "overlay_rgb": overlay,
            "raw_heatmap_uint8": heatmap_uint8,
            "heatmap_colored_rgb": heatmap_colored_rgb,
            "target_class_id": target_class_id,
            "hotspots_count": len(hotspots),
            "hotspots": hotspots
        }
