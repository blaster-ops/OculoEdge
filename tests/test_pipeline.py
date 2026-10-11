"""Behavioral regressions for image rejection, offline use, snapshots and report integrity."""
import base64
from concurrent.futures import ThreadPoolExecutor
import copy
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import numpy as np
from PIL import Image
from pypdf import PdfReader
from fastapi.testclient import TestClient
from app.server import app, MAX_UPLOAD
from core.model_engine import DiagnosticEngine
from core.explainer import GradCAMExplainer
from core.preprocessor import enhance_retina_image
from core.biomarkers import extract_retina_biomarkers
from data.dataset_loader import get_available_samples, generate_synthetic_fundus
from data.evaluation_dataset import load_manifest
from reports.trust import sign_record, verify_record, sign_pdf
from benchmarks.evaluate_metrics import evaluate, binary_roc

ROOT = Path(__file__).resolve().parents[1]
def png(array):
    stream=io.BytesIO(); Image.fromarray(array).save(stream,format="PNG"); return stream.getvalue()

class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.state=tempfile.TemporaryDirectory()
        cls.old=os.environ.get("OCULOEDGE_STATE_DIR")
        os.environ["OCULOEDGE_STATE_DIR"]=cls.state.name
        cls.client=TestClient(app); cls.client.__enter__()
        cls.engine=DiagnosticEngine(mode="heuristic")
    @classmethod
    def tearDownClass(cls):
        cls.client.__exit__(None,None,None)
        if cls.old is None: os.environ.pop("OCULOEDGE_STATE_DIR",None)
        else: os.environ["OCULOEDGE_STATE_DIR"]=cls.old
        cls.state.cleanup()
    def analyze(self,grade=2):
        r=self.client.post("/api/diagnose",data={"sample_id":grade})
        self.assertEqual(r.status_code,200,r.text)
        return r.json()
    def test_health_exposes_actual_mode(self):
        r=self.client.get("/api/health").json()
        self.assertEqual(r["mode"],"heuristic"); self.assertFalse(r["model_loaded"])
        self.assertFalse(r["clinically_validated"])
    def test_all_demo_samples_are_explicitly_synthetic(self):
        samples=self.client.get("/api/samples").json()["samples"]
        self.assertEqual(len(samples),5)
        for s in samples:
            self.assertTrue(s["synthetic"])
            data=self.analyze(s["id"])
            self.assertEqual(data["prediction"]["id"],s["expected_grade"])
            self.assertIsNone(data["prediction"]["confidence"])
            self.assertIsNone(data["prediction"]["referable"])
            self.assertEqual(data["explicability"]["method"],"rule_mask")
    def test_uniform_images_never_get_a_grade(self):
        for value in [0,128,220,255]:
            data=self.client.post("/api/diagnose",files={"file":("flat.png",png(np.full((384,384,3),value,np.uint8)),"image/png")}).json()
            self.assertFalse(data["prediction"]["evaluable"])
            self.assertIsNone(data["prediction"]["id"])
            self.assertIsNone(data["prediction"]["confidence"])
    def test_wrong_color_and_blurred_and_small_images_rejected(self):
        import cv2
        real=np.array(Image.open(ROOT/"data/samples/sample_grade_0_normal.jpg"))
        bad=[cv2.GaussianBlur(real,(0,0),30),np.repeat(real[:,:,1,None],3,axis=2),cv2.resize(real,(64,64))]
        for image in bad:
            self.assertFalse(self.engine.predict(image)["evaluable"])
    def test_explanation_uses_the_decision_mask(self):
        image=np.array(Image.open(ROOT/"data/samples/sample_grade_2_moderada.jpg"))
        pred=self.engine.predict(image)
        result=GradCAMExplainer(self.engine).generate_heatmap(image,prediction=pred)
        np.testing.assert_array_equal(result["raw_heatmap_uint8"],pred["explanation_mask"])
        self.assertGreater(np.count_nonzero(result["raw_heatmap_uint8"]),0)
    def test_empty_rule_mask_preserves_original(self):
        image=np.array(Image.open(ROOT/"data/samples/sample_grade_0_normal.jpg"))
        pred=self.engine.predict(image)
        cam=GradCAMExplainer(self.engine).generate_heatmap(image,prediction=pred)
        np.testing.assert_array_equal(cam["overlay_rgb"],pred["original_resized"])
    def test_signed_color_arithmetic_does_not_wrap(self):
        m=extract_retina_biomarkers(np.full((384,384,3),220,np.uint8))["metrics"]
        self.assertEqual(m["exudate_pixels"],0)
    def test_non_square_preprocessing_and_empty_rejection(self):
        original,processed=enhance_retina_image(generate_synthetic_fundus(2),target_size=(320,240))
        self.assertEqual(processed.shape,(240,320,3))
        with self.assertRaises(ValueError): enhance_retina_image(np.zeros((0,0,3),np.uint8))
    def test_synthetic_generator_does_not_change_global_rng(self):
        np.random.seed(42); expected=np.random.random(3)
        np.random.seed(42); generate_synthetic_fundus(3)
        np.testing.assert_array_equal(np.random.random(3),expected)
    def test_invalid_requests(self):
        for payload,status in [({},400),({"sample_id":9},400),({"sample_id":"abc"},422),
                               ({"sample_id":1,"alpha":2},422),({"sample_id":1,"alpha":"nan"},422)]:
            self.assertEqual(self.client.post("/api/diagnose",data=payload).status_code,status)
        self.assertEqual(self.client.post("/api/diagnose",files={"file":("empty.jpg",b"","image/jpeg")}).status_code,400)
        self.assertEqual(self.client.post("/api/diagnose",files={"file":("bad.jpg",b"bad image","image/jpeg")}).status_code,400)
        self.assertEqual(self.client.post("/api/diagnose",data={"sample_id":0},files={"file":("bad.jpg",b"bad")}).status_code,400)
    def test_file_limit(self):
        r=self.client.post("/api/diagnose",files={"file":("large.png",b"x"*(MAX_UPLOAD+1),"image/png")})
        self.assertEqual(r.status_code,413)
    def test_pixel_limit(self):
        r=self.client.post("/api/diagnose",files={"file":("large.png",png(np.zeros((4500,4500,3),np.uint8)),"image/png")})
        self.assertEqual(r.status_code,400)
    def test_restricted_sample_paths_and_origins(self):
        self.assertEqual(self.client.get("/api/samples/server.py").status_code,404)
        self.assertEqual(self.client.get("/api/samples/..%5C..%5Capp%5Cserver.py").status_code,404)
        self.assertEqual(self.client.post("/api/diagnose",data={"sample_id":1},headers={"Origin":"https://example.com"}).status_code,403)
    def test_static_assets_are_local_and_csp_present(self):
        html=self.client.get("/")
        self.assertNotIn("https://",html.text); self.assertNotIn("http://",html.text)
        self.assertIn("script-src 'self'",html.headers["content-security-policy"])
        for path in ["/static/app.js","/static/app.css","/static/eye.svg"]:
            self.assertEqual(self.client.get(path).status_code,200)
    def test_report_is_same_snapshot_with_escaped_fields(self):
        analysis=self.analyze(3)
        r=self.client.post("/api/report",data={"analysis_id":analysis["analysis_id"],"patient_name":"Ana <b>Prueba</b>","patient_id":"FOLIO/ñ","patient_age":50,"eye_side":"OI"})
        self.assertEqual(r.status_code,200,r.text); self.assertTrue(r.content.startswith(b"%PDF"))
        record=json.loads(base64.b64decode(r.headers["x-oculoedge-record"]))
        self.assertEqual(record["payload"]["prediction"],analysis["prediction"])
        self.assertEqual(record["payload"]["source"],analysis["source"])
        self.assertTrue(self.client.post("/api/verify",json=record).json()["valid"])
        text="".join(p.extract_text() for p in PdfReader(io.BytesIO(r.content)).pages)
        self.assertIn("Ana <b>Prueba</b>",text)
        self.assertIn("sin validación clínica",text.lower())
        import hashlib
        self.assertEqual(record["pdf_sha256"],hashlib.sha256(r.content).hexdigest())
        altered=copy.deepcopy(record); altered["payload"]["prediction"]["id"]=0
        self.assertFalse(self.client.post("/api/verify",json=altered).json()["valid"])
        altered=copy.deepcopy(record); altered["pdf_sha256"]="0"*64
        self.assertFalse(self.client.post("/api/verify",json=altered).json()["valid"])
    def test_report_validation_and_expiration(self):
        aid=self.analyze()["analysis_id"]
        for data in [{"analysis_id":aid,"eye_side":"OT"},{"analysis_id":aid,"patient_age":-1},
                     {"analysis_id":aid,"patient_age":150},{"analysis_id":aid,"patient_name":"x"*121}]:
            self.assertEqual(self.client.post("/api/report",data=data).status_code,422)
        with app.state.store.lock:
            _,snapshot=app.state.store.items[aid]; app.state.store.items[aid]=(-10000,snapshot)
        self.assertEqual(self.client.post("/api/report",data={"analysis_id":aid}).status_code,409)
    def test_non_evaluable_report_does_not_claim_a_grade(self):
        a=self.client.post("/api/diagnose",files={"file":("flat.png",png(np.zeros((384,384,3),np.uint8)),"image/png")}).json()
        r=self.client.post("/api/report",data={"analysis_id":a["analysis_id"]})
        self.assertEqual(r.status_code,200)
        text="".join(p.extract_text() for p in PdfReader(io.BytesIO(r.content)).pages)
        self.assertIn("Imagen no evaluable",text)
    def test_concurrent_analyses_keep_results_separate(self):
        with ThreadPoolExecutor(max_workers=4) as pool:
            responses=list(pool.map(self.analyze,[0,2,3,4]))
        self.assertEqual([r["prediction"]["id"] for r in responses],[0,2,3,4])
        for r in responses:
            snapshot=self.client.get("/api/analysis/"+r["analysis_id"]).json()
            self.assertEqual(snapshot["prediction"],r["prediction"])
    def test_cache_has_bounded_retention(self):
        from app.server import AnalysisStore, MAX_ANALYSES
        store=AnalysisStore()
        for i in range(MAX_ANALYSES+2): store.put(str(i),{"value":i})
        self.assertEqual(len(store.items),MAX_ANALYSES)
        self.assertNotIn("0",store.items)
    def test_benchmark_computes_demo_metrics_and_no_fake_auc(self):
        with tempfile.TemporaryDirectory() as folder:
            summary=evaluate(output_dir=folder)
            self.assertEqual(summary["dataset_kind"],"synthetic")
            self.assertEqual(summary["total_images"],5)
            self.assertEqual(summary["multiclass_accuracy_including_rejections"],1)
            self.assertIsNone(summary["binary_grade_2_plus"]["accepted_only_auc"])
            self.assertFalse(summary["clinical_validation"])
    def test_roc_ties_and_perfect_ranking(self):
        self.assertAlmostEqual(binary_roc([0,1],[.1,.9])["auc"],1)
        self.assertAlmostEqual(binary_roc([0,1],[.5,.5])["auc"],.5)
        self.assertIsNone(binary_roc([1,1],[.3,.4]))
    def test_offline_without_torch_or_network(self):
        code="""import socket,sys
original_connect=socket.socket.connect
def local_only(self,address):
    if isinstance(address,tuple) and address[0] in ('127.0.0.1','::1'):
        return original_connect(self,address)
    raise RuntimeError('external network blocked')
socket.socket.connect=local_only
from fastapi.testclient import TestClient
from app.server import app
with TestClient(app) as client:
    assert client.get('/api/health').status_code==200
    a=client.post('/api/diagnose',data={'sample_id':4}).json()
    assert a['prediction']['id']==4
    assert client.post('/api/report',data={'analysis_id':a['analysis_id']}).status_code==200
assert 'torch' not in sys.modules
"""
        env=os.environ.copy(); env.pop("OCULOEDGE_MODEL",None)
        r=subprocess.run([sys.executable,"-c",code],cwd=ROOT,env=env,capture_output=True,text=True,timeout=60)
        self.assertEqual(r.returncode,0,r.stderr)

class ManifestTests(unittest.TestCase):
    def test_patient_and_image_leakage_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); (root/"a.png").write_bytes(png(generate_synthetic_fundus(0)))
            (root/"b.png").write_bytes(png(generate_synthetic_fundus(1)))
            path=root/"data.csv"
            path.write_text("path,label,patient_id,split\na.png,0,p1,train\nb.png,1,p1,val\n")
            with self.assertRaisesRegex(ValueError,"paciente"): load_manifest(path)
            path.write_text("path,label,patient_id,split\na.png,0,p1,train\nb.png,1,p2,val\n")
            (root/"b.png").write_bytes((root/"a.png").read_bytes())
            with self.assertRaisesRegex(ValueError,"idénticas"): load_manifest(path)
    def test_wrong_key_cannot_authenticate(self):
        record=sign_record({"value":1},b"a"*32)
        self.assertFalse(verify_record(record,b"b"*32))

if __name__ == "__main__": unittest.main()
