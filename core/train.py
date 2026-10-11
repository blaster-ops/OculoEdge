"""Reproducible CPU training with patient-separated validation and checkpoint manifest."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import numpy as np
from PIL import Image, ImageOps
import torch
from torch.utils.data import DataLoader, Dataset
from core.neural import OculoEdgeNet, TRANSFORM, PREPROCESSING, ARCHITECTURE
from core.preprocessor import enhance_retina_image
from data.evaluation_dataset import load_manifest

class FundusDataset(Dataset):
    def __init__(self, rows):
        self.rows = rows
    def __len__(self):
        return len(self.rows)
    def __getitem__(self, index):
        row = self.rows[index]
        with Image.open(row["path"]) as img:
            array = np.array(ImageOps.exif_transpose(img).convert("RGB"))
        _, processed = enhance_retina_image(array)
        return TRANSFORM(processed), row["label"]

def train_model(csv_path, epochs=15, batch_size=8, lr=1e-4, output_weights="weights/oculoedge_best.pth",
                seed=42, data_kind="unspecified", initial_weights=None):
    if epochs < 1 or batch_size < 1 or lr <= 0:
        raise ValueError("Épocas, lote y tasa de aprendizaje deben ser positivos.")
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    torch.set_num_threads(min(4, torch.get_num_threads()))
    torch.use_deterministic_algorithms(True)
    rows, csv_hash = load_manifest(csv_path)
    train_rows = [r for r in rows if r["split"] == "train"]
    val_rows = [r for r in rows if r["split"] == "val"]
    if len(train_rows) < 2 or not val_rows or {r["label"] for r in train_rows} != set(range(5)):
        raise ValueError("Se requieren entrenamiento con cinco clases y validación independiente.")
    train = DataLoader(FundusDataset(train_rows), batch_size=batch_size, shuffle=True, num_workers=0,
                       generator=torch.Generator().manual_seed(seed))
    val = DataLoader(FundusDataset(val_rows), batch_size=batch_size, shuffle=False, num_workers=0)
    model = OculoEdgeNet()
    initialization = "random-no-download"
    if initial_weights:
        model.load_state_dict(torch.load(initial_weights, map_location="cpu", weights_only=True))
        initialization = hashlib.sha256(Path(initial_weights).read_bytes()).hexdigest()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    loss_fn = torch.nn.CrossEntropyLoss()
    out = Path(output_weights); out.parent.mkdir(parents=True, exist_ok=True)
    best_loss = float("inf")
    history = []
    for epoch in range(1, epochs + 1):
        model.train(); total_loss = 0.; count = 0
        for x, y in train:
            optimizer.zero_grad(set_to_none=True)
            logits = model(x); loss = loss_fn(logits, y)
            if not torch.isfinite(loss):
                raise ValueError("Pérdida no finita durante entrenamiento.")
            loss.backward(); optimizer.step()
            total_loss += loss.item() * len(y); count += len(y)
        model.eval(); val_loss = 0.; val_count = 0; correct = 0
        with torch.inference_mode():
            for x, y in val:
                logits = model(x)
                val_loss += loss_fn(logits, y).item() * len(y)
                correct += int((logits.argmax(1) == y).sum()); val_count += len(y)
        row = {"epoch": epoch, "train_loss": total_loss / count,
               "val_loss": val_loss / val_count, "val_accuracy": correct / val_count}
        history.append(row)
        print(json.dumps(row), flush=True)
        if row["val_loss"] < best_loss:
            best_loss = row["val_loss"]
            torch.save(model.state_dict(), out)
            best_epoch = epoch
    manifest = {"architecture": ARCHITECTURE, "preprocessing": PREPROCESSING, "classes": list(range(5)),
                "sha256": hashlib.sha256(out.read_bytes()).hexdigest(), "training_completed": True,
                "clinically_validated": False, "calibrated": False, "dataset_kind": data_kind,
                "dataset_manifest_sha256": csv_hash, "seed": seed, "epochs": epochs, "best_epoch": best_epoch,
                "selection": "minimum_validation_cross_entropy", "training_images": len(train_rows),
                "validation_images": len(val_rows), "initialization": initialization,
                "created_at": datetime.now(timezone.utc).isoformat(), "torch_version": str(torch.__version__),
                "history": history}
    out.with_suffix(".json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest

def main():
    parser = argparse.ArgumentParser(description="Entrenar MobileNetV3 con CSV y particiones por paciente.")
    parser.add_argument("--csv", required=True)
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default="weights/oculoedge_best.pth")
    parser.add_argument("--data-kind", choices=["real", "synthetic", "unspecified"], default="unspecified")
    parser.add_argument("--init", help="Checkpoint local para inicialización; no descarga pesos.")
    args = parser.parse_args()
    train_model(args.csv, args.epochs, args.batch_size, args.lr, args.output, args.seed, args.data_kind, args.init)

if __name__ == "__main__":
    main()
