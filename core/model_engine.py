"""Offline research engine. Heuristics and trained CNNs have distinct provenance."""
import os
from pathlib import Path
import numpy as np
from core.biomarkers import extract_retina_biomarkers, classify_features
from core.preprocessor import enhance_retina_image
from core.quality import assess_image_quality

VERSION = "2.0.0"
NAMES = ["Sin signos en la demostración", "Patrón leve", "Patrón moderado", "Patrón severo", "Patrón proliferativo"]
COLORS = ["#059669", "#0284c7", "#d97706", "#ea580c", "#be123c"]
ICDR_CLASSES = {i: {"id": i, "name": NAMES[i], "severity": f"G{i}", "color": COLORS[i]} for i in range(5)}
NOTICE = "Prototipo de investigación. Sin validación clínica; no emite diagnósticos ni decisiones de tratamiento."

class DiagnosticEngine:
    def __init__(self, weights_path=None, mode=None):
        path = weights_path or os.environ.get("OCULOEDGE_MODEL")
        self.mode = mode or ("neural" if path else "heuristic")
        self.device = "cpu"
        self.model = None
        self.manifest = None
        self.neural = None
        if self.mode not in {"heuristic", "neural"}:
            raise ValueError("Modo desconocido. Use heuristic o neural.")
        if self.mode == "neural":
            if not path:
                raise ValueError("El modo neuronal requiere OCULOEDGE_MODEL o weights_path.")
            from core.neural import NeuralPredictor
            self.neural = NeuralPredictor(Path(path))
            self.model = self.neural.model
            self.manifest = self.neural.manifest

    def describe(self):
        return {"mode": self.mode, "device": self.device, "clinically_validated": False,
                "model_loaded": self.model is not None,
                "model_id": self.manifest["sha256"] if self.manifest else "heuristic-v2",
                "notice": NOTICE}

    def predict(self, image_np):
        quality = assess_image_quality(image_np)
        original, processed = enhance_retina_image(image_np)
        base = {"quality": quality, "engine": self.describe(), "processed_image": processed,
                "original_resized": original, "confidence": None, "confidence_percentage": None,
                "probabilities": [], "biomarker_metrics": {}, "evaluable": quality["evaluable"],
                "referable": None, "notice": NOTICE}
        if not quality["evaluable"]:
            return dict(base, prediction_id=None, diagnosis="Imagen no evaluable", severity="No evaluable",
                        urgency="Repetir adquisición", badge_color="#64748b",
                        clinical_findings="; ".join(quality["reasons"]),
                        recommendation="Use una retinografía en color, enfocada y con exposición adecuada.",
                        explanation_mask=np.zeros((384, 384), dtype=np.uint8), decision_rule="quality_rejection")
        features = extract_retina_biomarkers(original)
        grade, rule, evidence = classify_features(features)
        probabilities = []
        if self.neural:
            scores = self.neural.predict(processed)
            grade = int(np.argmax(scores))
            probabilities = [{"class_id": i, "name": NAMES[i], "probability": float(p),
                              "percentage": round(float(p) * 100, 2)} for i, p in enumerate(scores)]
            rule = "Salida de MobileNetV3 del checkpoint local; puntuaciones sin calibración clínica."
        return dict(base, prediction_id=grade, diagnosis=f"G{grade} · {NAMES[grade]}", severity=f"G{grade}",
                    badge_color=COLORS[grade], urgency="Revisión por un profesional",
                    clinical_findings=rule, decision_rule=rule, probabilities=probabilities,
                    recommendation="Resultado exploratorio. La valoración y canalización corresponden al profesional de salud.",
                    biomarker_metrics=features["metrics"], explanation_mask=evidence)
