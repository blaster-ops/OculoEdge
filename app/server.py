"""Local-only offline research API with bounded uploads and immutable result snapshots."""
import base64
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import hashlib
import io
import json
import threading
import time
from pathlib import Path
from uuid import uuid4
import warnings

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool
from core.model_engine import DiagnosticEngine, VERSION
from core.explainer import GradCAMExplainer
from core.preprocessor import np_to_base64
from data.dataset_loader import get_available_samples
from reports.triage_report import generate_pdf_report
from reports.trust import load_key, sign_record, verify_record, sign_pdf

ROOT = Path(__file__).resolve().parents[1]
MAX_UPLOAD = 12 * 1024 * 1024
MAX_PIXELS = 20_000_000
MAX_ANALYSES = 16
TTL_SECONDS = 20 * 60

class AnalysisStore:
    def __init__(self):
        self.items = OrderedDict()
        self.lock = threading.Lock()
    def put(self, analysis_id, data):
        with self.lock:
            self._prune()
            self.items[analysis_id] = (time.monotonic(), data)
            while len(self.items) > MAX_ANALYSES:
                self.items.popitem(last=False)
    def _prune(self):
        expired = [k for k, (created, _) in self.items.items() if time.monotonic() - created > TTL_SECONDS]
        for k in expired:
            self.items.pop(k)
    def get(self, analysis_id):
        with self.lock:
            self._prune()
            if analysis_id not in self.items:
                raise HTTPException(409, "El análisis expiró o el servidor se reinició. Vuelva a analizar la imagen.")
            return self.items[analysis_id][1]

@asynccontextmanager
async def lifespan(app):
    app.state.engine = DiagnosticEngine()
    app.state.explainer = GradCAMExplainer(app.state.engine)
    app.state.store = AnalysisStore()
    app.state.lock = threading.Lock()
    app.state.key = load_key()
    app.state.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="oculoedge-inference")
    app.state.samples = get_available_samples(str(ROOT / "data/samples"))
    yield
    app.state.executor.shutdown(wait=True)
    app.state.store.items.clear()

app = FastAPI(title="OculoEdge · Investigación offline", version=VERSION, lifespan=lifespan)

@app.middleware("http")
async def local_origin(request, call_next):
    length = request.headers.get("content-length", "0") or "0"
    if not length.isdigit():
        return JSONResponse({"detail": "Content-Length inválido."}, status_code=400)
    if int(length) > MAX_UPLOAD + 65536:
        return JSONResponse({"detail": "La solicitud supera el límite de tamaño."}, status_code=413)
    origin = request.headers.get("origin")
    allowed = {f"http://localhost:{request.url.port or 80}", f"http://127.0.0.1:{request.url.port or 80}"}
    if request.method == "POST" and origin and origin not in allowed:
        return JSONResponse({"detail": "Origen no autorizado: use la interfaz local de OculoEdge."}, status_code=403)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store" if request.url.path.startswith("/api/") else "no-cache"
    response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data: blob:; style-src 'self'; script-src 'self'; connect-src 'self'; media-src 'self' blob:; frame-ancestors 'none'; base-uri 'self'"
    return response

@app.get("/")
def root():
    return FileResponse(ROOT / "static/index.html")

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "system": "OculoEdge", "version": VERSION,
            **app.state.engine.describe(), "samples_count": len(app.state.samples),
            "offline_assets": True, "analysis_retention_minutes": TTL_SECONDS // 60}

@app.get("/api/samples")
def list_samples():
    return {"samples": [{k: v for k, v in s.items() if k != "path"} |
                        {"url": f"/api/samples/{s['filename']}"} for s in app.state.samples]}

@app.get("/api/samples/{filename}")
def get_sample_file(filename: str):
    sample = next((s for s in app.state.samples if s["filename"] == filename), None)
    if sample is None:
        raise HTTPException(404, "Muestra no encontrada.")
    return FileResponse(sample["path"])

def decode_image(contents):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(contents)) as img:
                if img.format not in {"JPEG", "PNG", "WEBP"}:
                    raise ValueError("Use JPG, PNG o WebP.")
                if img.width * img.height > MAX_PIXELS:
                    raise ValueError("La imagen supera el límite de 20 megapíxeles.")
                if getattr(img, "is_animated", False):
                    raise ValueError("Use una imagen estática.")
                return np.array(ImageOps.exif_transpose(img).convert("RGB"))
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise HTTPException(400, "Imagen inválida o demasiado grande. Use JPG, PNG o WebP de hasta 20 megapíxeles.") from exc

def run_analysis(image, source, alpha):
    start = time.perf_counter()
    with app.state.lock:
        pred = app.state.engine.predict(image)
        cam = app.state.explainer.generate_heatmap(image, alpha=alpha, prediction=pred)
    inference_ms = round((time.perf_counter() - start) * 1000, 2)
    prediction = {k: v for k, v in pred.items() if k not in {"processed_image", "original_resized", "explanation_mask", "prediction_id"}}
    prediction["id"] = pred["prediction_id"]
    analysis_id = str(uuid4())
    public = {"status": "success", "analysis_id": analysis_id,
              "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "source": source, "inference_time_ms": inference_ms, "prediction": prediction,
              "explicability": {k: v for k, v in cam.items() if not isinstance(v, np.ndarray)},
              "images": {"original_b64": np_to_base64(pred["original_resized"]),
                         "ben_graham_b64": np_to_base64(pred["processed_image"]),
                         "heatmap_colored_b64": np_to_base64(cam["heatmap_colored_rgb"], format="PNG"),
                         "evidence_mask_b64": np_to_base64(cam["raw_heatmap_uint8"], format="PNG"),
                         "gradcam_overlay_b64": np_to_base64(cam["overlay_rgb"])}}
    app.state.store.put(analysis_id, {"public": public, "pred": pred, "cam": cam,
                                   "image_sha256": hashlib.sha256(image.tobytes()).hexdigest()})
    return public

@app.post("/api/diagnose")
async def diagnose_image(file: UploadFile | None = File(None), sample_id: int | None = Form(None),
                         alpha: float = Form(.55, ge=0, le=1)):
    if (file is None) == (sample_id is None):
        raise HTTPException(400, "Seleccione una muestra o un archivo, únicamente uno.")
    if file:
        try:
            contents = await file.read(MAX_UPLOAD + 1)
        finally:
            await file.close()
        if not contents:
            raise HTTPException(400, "El archivo está vacío.")
        if len(contents) > MAX_UPLOAD:
            raise HTTPException(413, "El archivo supera 12 MB.")
        image = await run_in_threadpool(decode_image, contents)
        source = {"kind": "uploaded", "synthetic": False, "filename": Path(file.filename or "imagen").name[:120]}
    else:
        if sample_id not in range(5):
            raise HTTPException(400, "sample_id debe estar entre 0 y 4.")
        s = app.state.samples[sample_id]
        image = await run_in_threadpool(decode_image, Path(s["path"]).read_bytes())
        source = {"kind": "synthetic_sample", "synthetic": True, "sample_id": sample_id, "expected_grade": sample_id}
    import asyncio
    return await asyncio.get_running_loop().run_in_executor(app.state.executor, run_analysis, image, source, alpha)

@app.get("/api/analysis/{analysis_id}")
def analysis_record(analysis_id: str):
    snapshot = app.state.store.get(analysis_id)
    return {k: v for k, v in snapshot["public"].items() if k != "images"} | {"image_sha256": snapshot["image_sha256"]}

@app.post("/api/report")
def generate_report(analysis_id: str = Form(...), patient_name: str = Form("Anónimo", max_length=120),
                    patient_id: str = Form("DEMO", max_length=80), patient_age: int | None = Form(None, ge=0, le=120),
                    eye_side: str = Form("OD")):
    if eye_side not in {"OD", "OI"}:
        raise HTTPException(422, "Seleccione OD u OI.")
    snapshot = app.state.store.get(analysis_id)
    public = snapshot["public"]
    payload = {"version": VERSION, "analysis_id": analysis_id, "created_at": public["created_at"],
               "report_created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "patient": {"name": patient_name.strip() or "Anónimo", "id": patient_id.strip() or "DEMO",
                           "age": patient_age, "eye": eye_side}, "source": public["source"],
               "prediction": public["prediction"], "image_sha256": snapshot["image_sha256"],
               "explanation_sha256": hashlib.sha256(snapshot["cam"]["raw_heatmap_uint8"].tobytes()).hexdigest(),
               "explanation_method": public["explicability"]["method"]}
    record = sign_record(payload, app.state.key)
    data = generate_pdf_report(patient_name, patient_id, patient_age, eye_side, snapshot["pred"],
                               snapshot["pred"]["original_resized"], snapshot["cam"]["overlay_rgb"], record=record)
    record["pdf_sha256"] = hashlib.sha256(data).hexdigest()
    record["pdf_signature"] = sign_pdf(record["pdf_sha256"], app.state.key)
    encoded = base64.b64encode(json.dumps(record, ensure_ascii=False).encode("utf-8")).decode("ascii")
    return Response(data, media_type="application/pdf", headers={
        "Content-Disposition": f'attachment; filename="OculoEdge_{analysis_id[:8]}_{eye_side}.pdf"',
        "X-OculoEdge-Record": encoded})

class VerificationRequest(BaseModel):
    payload: dict
    sha256: str = Field(max_length=64)
    signature: str = Field(max_length=64)
    scheme: str = Field(max_length=50)
    pdf_sha256: str | None = Field(None, max_length=64)
    pdf_signature: str | None = Field(None, max_length=64)

@app.post("/api/verify")
def verify(request: VerificationRequest):
    data = request.model_dump(exclude_none=True)
    if len(json.dumps(data)) > 16000:
        raise HTTPException(413, "Registro demasiado grande.")
    try:
        valid = verify_record(data, app.state.key)
    except (ValueError, TypeError, UnicodeError):
        valid = False
    return {"valid": valid, "scope": "Registro canónico y clave de este equipo; no certificación clínica."}

app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
