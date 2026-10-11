"""Optional CNN runtime: explicit local checkpoints, no download on startup."""
import hashlib
import json
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
from torchvision import models, transforms

PREPROCESSING = "ben_graham_384_imagenet_v1"
ARCHITECTURE = "oculoedge_mobilenet_v3_large_v1"

class OculoEdgeNet(nn.Module):
    def __init__(self, num_classes=5):
        super().__init__()
        base = models.mobilenet_v3_large(weights=None)
        self.features = base.features
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.classifier = nn.Sequential(nn.Linear(960, 512), nn.Hardswish(), nn.Dropout(.2),
                                        nn.Linear(512, 128), nn.Hardswish(), nn.Linear(128, num_classes))
    def forward(self, x):
        return self.classifier(torch.flatten(self.avgpool(self.features(x)), 1))

TRANSFORM = transforms.Compose([transforms.ToTensor(),
    transforms.Normalize([.485, .456, .406], [.229, .224, .225])])

class NeuralPredictor:
    def __init__(self, weights_path):
        path = Path(weights_path)
        manifest_path = path.with_suffix(".json")
        if not path.is_file() or not manifest_path.is_file():
            raise ValueError("Checkpoint incompleto: se requieren .pth y manifiesto .json del entrenamiento. Los pesos antiguos carecen de procedencia verificable.")
        self.manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if self.manifest.get("sha256") != digest:
            raise ValueError("El SHA-256 del checkpoint no coincide con su manifiesto.")
        if (self.manifest.get("architecture") != ARCHITECTURE or
            self.manifest.get("preprocessing") != PREPROCESSING or
            self.manifest.get("classes") != [0, 1, 2, 3, 4] or
            self.manifest.get("training_completed") is not True):
            raise ValueError("Manifiesto incompatible o entrenamiento sin completar.")
        torch.set_num_threads(min(4, torch.get_num_threads()))
        self.model = OculoEdgeNet()
        self.model.load_state_dict(torch.load(path, map_location="cpu", weights_only=True), strict=True)
        self.model.eval()
    def tensor(self, image):
        return TRANSFORM(image).unsqueeze(0)
    def predict(self, processed):
        with torch.inference_mode():
            probs = torch.softmax(self.model(self.tensor(processed)), dim=1)[0].numpy()
        if not np.isfinite(probs).all():
            raise ValueError("El checkpoint produjo puntuaciones no finitas.")
        return probs
