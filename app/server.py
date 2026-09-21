"""
OculoEdge - Servidor de Aplicación Web y API de Inferencia Clínica
Proporciona endpoints REST y sirve la interfaz gráfica para la demostración en vivo.
"""

import os
import time
import io
from typing import Optional
import numpy as np
from PIL import Image
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, Response, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from core.preprocessor import enhance_retina_image, np_to_base64, base64_to_np
from core.model_engine import DiagnosticEngine, ICDR_CLASSES
from core.explainer import GradCAMExplainer
from data.dataset_loader import get_available_samples, initialize_sample_dataset
from reports.triage_report import generate_pdf_report

# Directorios del sistema
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
SAMPLES_DIR = os.path.join(BASE_DIR, "data", "samples")

# Inicializar dataset de referencia si no existe
initialize_sample_dataset(SAMPLES_DIR)

# Inicializar motores de IA y Explicabilidad
engine = DiagnosticEngine()
explainer = GradCAMExplainer(engine)

app = FastAPI(
    title="OculoEdge API",
    description="Sistema de Triaje Oftalmológico con Edge AI y Explicabilidad Clínica (Grad-CAM)",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "OculoEdge Server Activo"}


@app.get("/api/health")
async def health_check():
    """Endpoint de verificación de estado y preparación del sistema."""
    samples = get_available_samples(SAMPLES_DIR)
    return {
        "status": "healthy",
        "system": "OculoEdge",
        "version": "1.1.0",
        "device": str(engine.device),
        "model_loaded": engine.model is not None,
        "samples_count": len(samples),
        "competition": "FEMECI Puebla 2026",
        "institution": "Universidad Tecnológica de Tehuacán"
    }


@app.get("/api/samples")
async def list_samples():
    """Devuelve las 5 muestras clínicas de referencia."""
    samples = get_available_samples(SAMPLES_DIR)
    results = []
    for s in samples:
        results.append({
            "id": s["id"],
            "title": s["title"],
            "subtitle": s["subtitle"],
            "expected_grade": s["expected_grade"],
            "url": f"/api/samples/{s['filename']}"
        })
    return {"samples": results}


@app.get("/api/samples/{filename}")
async def get_sample_file(filename: str):
    file_path = os.path.join(SAMPLES_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Muestra no encontrada")
    return FileResponse(file_path)


@app.post("/api/diagnose")
async def diagnose_image(
    file: Optional[UploadFile] = File(None),
    sample_id: Optional[str] = Form(None),
    alpha: float = Form(0.55)
):
    """
    Recibe una imagen retiniana (archivo subido o sample_id) y ejecuta el pipeline completo:
    Preprocesamiento Ben Graham -> Inferencia Edge AI -> Explicabilidad Grad-CAM.
    """
    start_time = time.time()

    # Normalizar sample_id si viene como string
    parsed_sample_id: Optional[int] = None
    if sample_id is not None and str(sample_id).strip() != "":
        try:
            parsed_sample_id = int(sample_id)
        except ValueError:
            parsed_sample_id = None

    if file is not None and file.filename and len(file.filename) > 0:
        contents = await file.read()
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="El archivo subido está vacío.")
        try:
            pil_img = Image.open(io.BytesIO(contents)).convert("RGB")
            image_np = np.array(pil_img)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Formato de imagen inválido: {str(e)}")
    elif parsed_sample_id is not None and 0 <= parsed_sample_id <= 4:
        samples = get_available_samples(SAMPLES_DIR)
        sample_path = samples[parsed_sample_id]["path"]
        pil_img = Image.open(sample_path).convert("RGB")
        image_np = np.array(pil_img)
    else:
        raise HTTPException(status_code=400, detail="Debe proporcionar un archivo de imagen válido o un sample_id entre 0 y 4.")

    # 1. Inferencia diagnóstica híbrida
    pred_result = engine.predict(image_np)

    # 2. Generación del mapa Grad-CAM y capas térmicas
    cam_result = explainer.generate_heatmap(
        image_np,
        target_class_id=pred_result["prediction_id"],
        alpha=alpha
    )

    inference_time_ms = round((time.time() - start_time) * 1000, 1)

    # 3. Codificar imágenes a Base64 para visualización instantánea y blending interactivo
    b64_orig = np_to_base64(pred_result["original_resized"])
    b64_ben_graham = np_to_base64(pred_result["processed_image"])
    b64_heatmap_colored = np_to_base64(cam_result["heatmap_colored_rgb"])
    b64_gradcam = np_to_base64(cam_result["overlay_rgb"])

    return {
        "status": "success",
        "inference_time_ms": inference_time_ms,
        "prediction": {
            "id": pred_result["prediction_id"],
            "diagnosis": pred_result["diagnosis"],
            "severity": pred_result["severity"],
            "confidence": pred_result["confidence"],
            "confidence_percentage": pred_result["confidence_percentage"],
            "referable": pred_result["referable"],
            "urgency": pred_result["urgency"],
            "badge_color": pred_result["badge_color"],
            "clinical_findings": pred_result["clinical_findings"],
            "recommendation": pred_result["recommendation"],
            "probabilities": pred_result["probabilities"],
            "biomarker_metrics": pred_result.get("biomarker_metrics", {})
        },
        "explicability": {
            "hotspots_count": cam_result["hotspots_count"],
            "hotspots": cam_result["hotspots"]
        },
        "images": {
            "original_b64": b64_orig,
            "ben_graham_b64": b64_ben_graham,
            "heatmap_colored_b64": b64_heatmap_colored,
            "gradcam_overlay_b64": b64_gradcam
        }
    }


@app.post("/api/report")
async def generate_report(
    patient_name: Optional[str] = Form("Paciente Anónimo"),
    patient_id: Optional[str] = Form("UTT-2026-01"),
    patient_age: Optional[str] = Form("50"),
    eye_side: Optional[str] = Form("OD"),
    sample_id: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """Genera y descarga la ficha clínica de triaje en formato PDF estandarizado."""
    # Sanitización de datos del paciente
    name_clean = str(patient_name).strip() if patient_name and str(patient_name).strip() else "Paciente Anónimo"
    id_clean = str(patient_id).strip() if patient_id and str(patient_id).strip() else "FOLIO-UTT-2026-01"
    
    try:
        age_clean = int(str(patient_age).strip()) if patient_age and str(patient_age).strip() else 50
    except (ValueError, TypeError):
        age_clean = 50

    side_clean = str(eye_side).strip().upper() if eye_side and str(eye_side).strip() else "OD"
    if side_clean not in ["OD", "OI"]:
        side_clean = "OD"

    parsed_sample_id: Optional[int] = None
    if sample_id is not None and str(sample_id).strip() != "":
        try:
            parsed_sample_id = int(sample_id)
        except ValueError:
            parsed_sample_id = None

    if file is not None and file.filename and len(file.filename) > 0:
        contents = await file.read()
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="El archivo subido está vacío.")
        try:
            pil_img = Image.open(io.BytesIO(contents)).convert("RGB")
            image_np = np.array(pil_img)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Formato de imagen inválido: {str(e)}")
    elif parsed_sample_id is not None and 0 <= parsed_sample_id <= 4:
        samples = get_available_samples(SAMPLES_DIR)
        pil_img = Image.open(samples[parsed_sample_id]["path"]).convert("RGB")
        image_np = np.array(pil_img)
    else:
        raise HTTPException(status_code=400, detail="Debe proporcionar una imagen o sample_id válido.")

    # Diagnóstico y Grad-CAM
    pred_result = engine.predict(image_np)
    cam_result = explainer.generate_heatmap(image_np, target_class_id=pred_result["prediction_id"])

    pdf_bytes = generate_pdf_report(
        patient_name=name_clean,
        patient_id=id_clean,
        patient_age=age_clean,
        eye_side=side_clean,
        diagnosis_data=pred_result,
        original_img_np=pred_result["processed_image"],
        gradcam_img_np=cam_result["overlay_rgb"]
    )

    clean_filename = f"Reporte_OculoEdge_{id_clean}_{side_clean}.pdf".replace(" ", "_")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{clean_filename}"'}
    )


# Montar archivos estáticos
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
