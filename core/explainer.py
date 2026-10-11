"""Explain the actual decision: rule masks or Grad-CAM from the predicting CNN."""
import cv2
import numpy as np

class GradCAMExplainer:
    def __init__(self, engine):
        self.engine = engine
        self.gradients = None
        self.activations = None

    def generate_heatmap(self, image_np, target_class_id=None, alpha=.55, prediction=None):
        if not 0 <= alpha <= 1 or not np.isfinite(alpha):
            raise ValueError("La opacidad debe estar entre 0 y 1.")
        pred = prediction or self.engine.predict(image_np)
        if pred["evaluable"] and self.engine.neural:
            import torch
            model = self.engine.model
            tensors = {}
            def capture(module, args, output):
                tensors["activation"] = output
            handle = model.features[-1].register_forward_hook(capture)
            try:
                with torch.enable_grad():
                    inp = self.engine.neural.tensor(pred["processed_image"]).requires_grad_(True)
                    logits = model(inp)
                    cid = pred["prediction_id"] if target_class_id is None else target_class_id
                    if cid not in range(5):
                        raise ValueError("Clase Grad-CAM inválida.")
                    activations = tensors["activation"]
                    gradients = torch.autograd.grad(logits[0, cid], activations)[0]
                    cam = (gradients.mean((2, 3), keepdim=True) * activations).sum(1).relu()[0]
                    raw = cam.detach().cpu().numpy()
                    maximum = float(raw.max())
                    raw = raw / maximum if maximum else np.zeros_like(raw)
                    mask = (cv2.resize(raw, (384, 384)) * 255).astype(np.uint8)
            finally:
                handle.remove()
                tensors.clear()
                model.zero_grad(set_to_none=True)
            method, label = "gradcam", "Grad-CAM del modelo que produjo la puntuación"
        else:
            mask = pred["explanation_mask"]
            method, label = "rule_mask", "Regiones utilizadas por las reglas experimentales"
        colored = cv2.cvtColor(cv2.applyColorMap(mask, cv2.COLORMAP_INFERNO), cv2.COLOR_BGR2RGB)
        active = (mask.astype(np.float32) / 255 * alpha)[..., None]
        original = pred["original_resized"]
        overlay = (original * (1 - active) + colored * active).clip(0, 255).astype(np.uint8)
        contours, _ = cv2.findContours((mask > 153).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        hotspots = []
        for c in contours:
            area = cv2.contourArea(c)
            if area >= 3:
                x, y, w, h = cv2.boundingRect(c)
                hotspots.append({"x": x, "y": y, "w": w, "h": h, "area": float(area),
                                 "center": [x + w // 2, y + h // 2]})
        return {"method": method, "label": label, "overlay_rgb": overlay, "heatmap_colored_rgb": colored,
                "raw_heatmap_uint8": mask, "hotspots_count": len(hotspots), "hotspots": hotspots,
                "target_class_id": pred["prediction_id"]}
