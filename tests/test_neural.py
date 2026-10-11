"""Optional CNN training + inference + Grad-CAM exercised together with synthetic smoke data."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
from PIL import Image
from data.dataset_loader import generate_synthetic_fundus

@unittest.skipUnless(importlib.util.find_spec("torch") and importlib.util.find_spec("torchvision"), "Instale requirements-ml.txt para probar MobileNetV3")
class NeuralTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from core.train import train_model
        cls.temp=tempfile.TemporaryDirectory(); root=Path(cls.temp.name)
        lines=["path,label,patient_id,split"]
        for split in ["train","val","test"]:
            for grade in range(5):
                image=generate_synthetic_fundus(grade)
                # Tiny variations ensure no identical bytes across splits; this is only a smoke fixture.
                image[0,0]=[10,{"train":20,"val":30,"test":40}[split],grade]
                name=f"{split}_{grade}.png"; Image.fromarray(image).save(root/name)
                lines.append(f"{name},{grade},{split}_{grade},{split}")
        cls.csv=root/"data.csv"; cls.csv.write_text("\n".join(lines))
        cls.weights=root/"smoke.pth"
        cls.manifest=train_model(cls.csv,epochs=1,batch_size=5,output_weights=cls.weights,data_kind="synthetic")
    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()
    def test_predict_and_cam_use_same_model_and_release_hooks(self):
        from core.model_engine import DiagnosticEngine
        from core.explainer import GradCAMExplainer
        from core.neural import NeuralPredictor
        engine=DiagnosticEngine(weights_path=self.weights)
        image=generate_synthetic_fundus(2); pred=engine.predict(image)
        probs=engine.neural.predict(pred["processed_image"])
        self.assertEqual(pred["prediction_id"],int(probs.argmax()))
        self.assertAlmostEqual(sum(p["probability"] for p in pred["probabilities"]),1,places=5)
        explainer=GradCAMExplainer(engine); layer=engine.model.features[-1]; hooks=len(layer._forward_hooks)
        for _ in range(2):
            cam=explainer.generate_heatmap(image,prediction=pred)
            self.assertEqual(cam["method"],"gradcam")
            self.assertEqual(cam["target_class_id"],pred["prediction_id"])
            self.assertEqual(cam["raw_heatmap_uint8"].shape,(384,384))
            self.assertEqual(len(layer._forward_hooks),hooks)
        self.assertTrue(all(p.grad is None for p in engine.model.parameters()))
    def test_training_selected_validation_loss_and_wrote_manifest(self):
        self.assertTrue(self.manifest["training_completed"])
        self.assertEqual(self.manifest["selection"],"minimum_validation_cross_entropy")
        self.assertFalse(self.manifest["clinically_validated"])
        self.assertEqual(self.manifest["training_images"],5)
    def test_manifest_mismatch_and_legacy_checkpoint_rejected(self):
        from core.neural import NeuralPredictor
        root=Path(self.temp.name); changed=root/"changed.pth"
        changed.write_bytes(self.weights.read_bytes())
        manifest=copy.deepcopy(self.manifest); manifest["sha256"]="0"*64
        changed.with_suffix(".json").write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError,"SHA-256"): NeuralPredictor(changed)
        changed.with_suffix(".json").unlink()
        with self.assertRaisesRegex(ValueError,"procedencia"): NeuralPredictor(changed)
    def test_evaluation_calculates_from_holdout_predictions(self):
        from benchmarks.evaluate_metrics import evaluate
        out=Path(self.temp.name)/"evaluation"
        result=evaluate(self.csv,self.weights,out,"synthetic")
        self.assertEqual(result["total_images"],5)
        rows=json.loads((out/"predictions.json").read_text(encoding="utf-8"))
        correct=sum(r["prediction"]==r["label"] for r in rows)
        self.assertEqual(result["multiclass_accuracy_including_rejections"],correct/5)
        self.assertIsNotNone(result["binary_grade_2_plus"]["accepted_only_auc"])
