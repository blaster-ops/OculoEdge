"""
OculoEdge - Suite de Pruebas Automatizadas de Calidad y Robustez Clínica
Verifica el preprocesamiento, la precisión diagnóstica del modelo en los 5 grados ICDR,
la explicabilidad de Grad-CAM, la robustez del generador de PDF y los endpoints de la API.
"""

import os
import sys
import unittest
import numpy as np
from PIL import Image

# Configurar ruta raíz
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from core.preprocessor import enhance_retina_image
from core.model_engine import DiagnosticEngine, ICDR_CLASSES
from core.explainer import GradCAMExplainer
from data.dataset_loader import get_available_samples, initialize_sample_dataset
from reports.triage_report import generate_pdf_report
from app.server import app
from fastapi.testclient import TestClient


class TestOculoEdgeFullPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.samples_dir = os.path.join(BASE_DIR, "data", "samples")
        initialize_sample_dataset(cls.samples_dir)
        cls.samples = get_available_samples(cls.samples_dir)
        cls.engine = DiagnosticEngine()
        cls.explainer = GradCAMExplainer(cls.engine)
        cls.client = TestClient(app)

    def test_01_preprocessor_ben_graham(self):
        """Verifica que el preprocesamiento Ben Graham produzca imágenes (384, 384, 3) uint8."""
        sample_path = self.samples[0]["path"]
        pil_img = Image.open(sample_path).convert("RGB")
        img_np = np.array(pil_img)

        resized, filtered = enhance_retina_image(img_np, target_size=(384, 384))
        self.assertEqual(resized.shape, (384, 384, 3))
        self.assertEqual(filtered.shape, (384, 384, 3))
        self.assertEqual(filtered.dtype, np.uint8)
        self.assertEqual(resized.dtype, np.uint8)

    def test_02_all_five_icdr_grades_exactness(self):
        """Verifica que los 5 grados clínicos ICDR (G0 a G4) se diagnostiquen con confianza >= 85%."""
        for sample_info in self.samples:
            expected_grade = sample_info["expected_grade"]
            pil_img = Image.open(sample_info["path"]).convert("RGB")
            img_np = np.array(pil_img)

            pred = self.engine.predict(img_np)
            
            self.assertEqual(
                pred["prediction_id"],
                expected_grade,
                f"Fallo en muestra G{expected_grade}: predijo G{pred['prediction_id']} con {pred['confidence_percentage']}%"
            )
            self.assertGreaterEqual(
                pred["confidence"],
                0.85,
                f"Confianza insuficiente para G{expected_grade}: {pred['confidence_percentage']}%"
            )
            self.assertIn("biomarker_metrics", pred)
            self.assertIn("dark_lesion_pixels", pred["biomarker_metrics"])

    def test_03_gradcam_explicability_and_leak_prevention(self):
        """Verifica que Grad-CAM retorne mapa térmico, superposición y libere memoria."""
        sample_path = self.samples[3]["path"]  # Grado 3 (Severo)
        pil_img = Image.open(sample_path).convert("RGB")
        img_np = np.array(pil_img)

        cam_res = self.explainer.generate_heatmap(img_np, target_class_id=3, alpha=0.55)

        self.assertIn("overlay_rgb", cam_res)
        self.assertEqual(cam_res["overlay_rgb"].shape, (384, 384, 3))
        self.assertIn("heatmap_colored_rgb", cam_res)
        self.assertEqual(cam_res["heatmap_colored_rgb"].shape, (384, 384, 3))
        self.assertIn("raw_heatmap_uint8", cam_res)
        self.assertEqual(cam_res["raw_heatmap_uint8"].shape, (384, 384))
        self.assertGreaterEqual(cam_res["hotspots_count"], 0)

        # Verificar que los gradientes internos se hayan limpiado
        self.assertIsNone(self.explainer.gradients)
        self.assertIsNone(self.explainer.activations)

    def test_04_pdf_report_and_fallbacks(self):
        """Verifica la generación de la ficha clínica en PDF y el manejo seguro de campos vacíos."""
        sample_path = self.samples[2]["path"]
        pil_img = Image.open(sample_path).convert("RGB")
        img_np = np.array(pil_img)

        pred = self.engine.predict(img_np)
        cam_res = self.explainer.generate_heatmap(img_np, target_class_id=pred["prediction_id"])

        # Test con campos vacíos para comprobar fallbacks robustos
        pdf_bytes = generate_pdf_report(
            patient_name="",
            patient_id="",
            patient_age="no_int",
            eye_side="",
            diagnosis_data=pred,
            original_img_np=pred["processed_image"],
            gradcam_img_np=cam_res["overlay_rgb"]
        )

        self.assertTrue(len(pdf_bytes) > 20000, "El PDF generado es demasiado pequeño.")
        self.assertTrue(pdf_bytes.startswith(b"%PDF"), "Encabezado PDF inválido.")

    def test_05_api_endpoints_health_and_diagnose(self):
        """Verifica los endpoints REST de la API de FastAPI con TestClient."""
        # 1. Health check
        res_health = self.client.get("/api/health")
        self.assertEqual(res_health.status_code, 200)
        data_health = res_health.json()
        self.assertEqual(data_health["status"], "healthy")
        self.assertEqual(data_health["system"], "OculoEdge")

        # 2. Samples list
        res_samples = self.client.get("/api/samples")
        self.assertEqual(res_samples.status_code, 200)
        self.assertEqual(len(res_samples.json()["samples"]), 5)

        # 3. Diagnose endpoint con sample_id=4 (Proliferativa)
        res_diag = self.client.post("/api/diagnose", data={"sample_id": "4", "alpha": "0.6"})
        self.assertEqual(res_diag.status_code, 200)
        diag_json = res_diag.json()
        self.assertEqual(diag_json["status"], "success")
        self.assertEqual(diag_json["prediction"]["id"], 4)
        self.assertTrue(diag_json["prediction"]["referable"])
        self.assertIn("original_b64", diag_json["images"])
        self.assertIn("heatmap_colored_b64", diag_json["images"])
        self.assertIn("gradcam_overlay_b64", diag_json["images"])

        # 4. Report endpoint
        res_report = self.client.post("/api/report", data={
            "sample_id": "1",
            "patient_name": "Test Paciente",
            "patient_id": "FOLIO-TEST-01",
            "patient_age": "45",
            "eye_side": "OI"
        })
        self.assertEqual(res_report.status_code, 200)
        self.assertEqual(res_report.headers["content-type"], "application/pdf")
        self.assertTrue(res_report.content.startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
