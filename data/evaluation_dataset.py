"""CSV manifests enforce patient and image separation across dataset splits."""
import csv
import hashlib
from pathlib import Path

def load_manifest(path):
    path = Path(path).resolve()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not {"path", "label", "patient_id", "split"}.issubset(reader.fieldnames or []):
            raise ValueError("CSV requerido: path,label,patient_id,split (train/val/test).")
        rows = []
        patients, hashes = {}, {}
        seen_paths = set()
        for row in reader:
            label = int(row["label"])
            split = row["split"].strip().lower()
            patient = row["patient_id"].strip()
            image = (path.parent / row["path"]).resolve()
            if label not in range(5) or split not in {"train", "val", "test"} or not patient:
                raise ValueError("Etiqueta, partición o patient_id inválido en CSV.")
            if not image.is_file():
                raise ValueError(f"Imagen no encontrada: {image}")
            if image in seen_paths:
                raise ValueError("Una ruta de imagen aparece más de una vez.")
            seen_paths.add(image)
            digest = hashlib.sha256(image.read_bytes()).hexdigest()
            if patient in patients and patients[patient] != split:
                raise ValueError("Fuga de datos: un paciente aparece en varias particiones.")
            if digest in hashes and hashes[digest] != split:
                raise ValueError("Fuga de datos: imágenes idénticas aparecen en varias particiones.")
            patients[patient], hashes[digest] = split, split
            rows.append({"path": image, "label": label, "patient_id": patient, "split": split, "sha256": digest})
    if not rows:
        raise ValueError("El manifiesto está vacío.")
    return rows, hashlib.sha256(path.read_bytes()).hexdigest()
