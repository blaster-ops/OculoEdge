"""Compute metrics from predictions. Default dataset is explicitly synthetic, n=5."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
import numpy as np
from PIL import Image, ImageOps
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from core.model_engine import DiagnosticEngine, VERSION
from data.dataset_loader import get_available_samples
from data.evaluation_dataset import load_manifest

ROOT = Path(__file__).resolve().parents[1]

def binary_roc(labels, scores):
    labels, scores = np.asarray(labels, dtype=bool), np.asarray(scores, dtype=float)
    pos, neg = int(labels.sum()), int((~labels).sum())
    if not pos or not neg:
        return None
    order = np.argsort(-scores, kind="stable")
    labels, scores = labels[order], scores[order]
    ends = np.r_[np.where(np.diff(scores))[0], len(scores) - 1]
    tp = np.r_[0, np.cumsum(labels)[ends]] / pos
    fp = np.r_[0, np.cumsum(~labels)[ends]] / neg
    return {"fpr": fp.tolist(), "tpr": tp.tolist(), "auc": float(np.trapezoid(tp, fp))}

def evaluate(csv_path=None, weights=None, output_dir=None, dataset_kind="unspecified"):
    out = Path(output_dir or ROOT / "benchmarks"); out.mkdir(parents=True, exist_ok=True)
    engine = DiagnosticEngine(weights_path=weights)
    manifest_hash = None
    if csv_path:
        rows, manifest_hash = load_manifest(csv_path)
        rows = [r for r in rows if r["split"] == "test"]
        if not rows:
            raise ValueError("El CSV no contiene partición test.")
    else:
        dataset_kind = "synthetic"
        rows = [{"path": Path(s["path"]), "label": s["expected_grade"],
                 "sha256": hashlib.sha256(Path(s["path"]).read_bytes()).hexdigest()}
                for s in get_available_samples(str(ROOT / "data/samples"))]
    cm = np.zeros((5, 5), dtype=int)
    results, times, rejected = [], [], [0]*5
    scores, labels = [], []
    # Warm-up is excluded from latency measurements.
    with Image.open(rows[0]["path"]) as img:
        engine.predict(np.array(ImageOps.exif_transpose(img).convert("RGB")))
    for row in rows:
        with Image.open(row["path"]) as img:
            array = np.array(ImageOps.exif_transpose(img).convert("RGB"))
        t0 = time.perf_counter(); pred = engine.predict(array); ms = (time.perf_counter()-t0)*1000
        times.append(ms); grade = pred["prediction_id"]
        if grade is None:
            rejected[row["label"]] += 1
        else:
            cm[row["label"], grade] += 1
            if pred["probabilities"]:
                scores.append(sum(p["probability"] for p in pred["probabilities"] if p["class_id"] >= 2))
                labels.append(row["label"] >= 2)
        results.append({"file": row["path"].name, "image_sha256": row["sha256"], "label": row["label"],
                        "prediction": grade, "evaluable": pred["evaluable"], "latency_ms": round(ms, 3),
                        "probabilities": pred["probabilities"], "quality": pred["quality"]})
    tp, fn, tn, fp = [int(v) for v in [cm[2:,2:].sum(), cm[2:,:2].sum(), cm[:2,:2].sum(), cm[:2,2:].sum()]]
    pos_rejected, neg_rejected = sum(rejected[2:]), sum(rejected[:2])
    safe_div = lambda n,d: n/d if d else None
    roc = binary_roc(labels, scores) if scores else None
    summary = {"version": VERSION, "created_at": datetime.now(timezone.utc).isoformat(),
               "dataset_kind": dataset_kind, "dataset_manifest_sha256": manifest_hash,
               "clinical_validation": False, "engine": engine.describe(), "total_images": len(rows),
               "evaluable_images": int(cm.sum()), "rejected_by_class": rejected,
               "multiclass_accuracy_including_rejections": float(cm.trace()/len(rows)),
               "binary_grade_2_plus": {"tp": tp, "fn": fn, "tn": tn, "fp": fp,
                   "sensitivity_including_rejections": safe_div(tp,tp+fn+pos_rejected),
                   "specificity_including_rejections": safe_div(tn,tn+fp+neg_rejected),
                   "accepted_only_auc": roc["auc"] if roc else None,
                   "auc_note": "AUC requiere puntuaciones neuronales y ambas clases; se calcula solo sobre imágenes aceptadas."},
               "latency_prediction_only_ms": {"median": float(np.median(times)), "p95": float(np.percentile(times,95)),
                                              "warmup_excluded": True},
               "notice": "Cinco muestras sintéticas comprueban integración; no estiman rendimiento clínico." if not csv_path else
                         "Evaluación técnica sobre el CSV indicado; requiere validación externa y revisión especializada."}
    (out/"metrics_summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    (out/"predictions.json").write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding="utf-8")
    fig, ax = plt.subplots(figsize=(7,6), dpi=150)
    ax.imshow(cm, cmap="Blues"); ax.set_xticks(range(5), [f"G{i}" for i in range(5)]); ax.set_yticks(range(5),[f"G{i}" for i in range(5)])
    for i in range(5):
        for j in range(5): ax.text(j,i,str(cm[i,j]),ha="center",va="center",color="black")
    ax.set_xlabel("Predicción experimental"); ax.set_ylabel("Etiqueta de referencia")
    ax.set_title(f"OculoEdge · {dataset_kind} · n={len(rows)}\nEvaluación técnica, sin validación clínica")
    fig.tight_layout(); fig.savefig(out/"confusion_matrix.png"); plt.close(fig)
    fig, ax = plt.subplots(figsize=(7,5), dpi=150)
    if roc:
        ax.plot(roc["fpr"],roc["tpr"],label=f"AUC aceptadas = {roc['auc']:.3f}"); ax.legend()
        ax.set_xlabel("Tasa de falsos positivos"); ax.set_ylabel("Tasa de verdaderos positivos")
    else:
        ax.text(.5,.5,"ROC no disponible\nEl motor de reglas no produce probabilidades clínicas",ha="center",va="center",transform=ax.transAxes)
        ax.set_axis_off()
    ax.set_title("OculoEdge · evaluación reproducible"); fig.tight_layout(); fig.savefig(out/"roc_curve.png"); plt.close(fig)
    return summary

def main():
    p=argparse.ArgumentParser(); p.add_argument("--csv"); p.add_argument("--weights"); p.add_argument("--output")
    p.add_argument("--data-kind",choices=["real","synthetic","unspecified"],default="unspecified")
    a=p.parse_args(); print(json.dumps(evaluate(a.csv,a.weights,a.output,a.data_kind),ensure_ascii=False,indent=2))

if __name__ == "__main__": main()
