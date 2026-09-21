"""
OculoEdge - Pipeline de Entrenamiento y Transfer Learning
Permite entrenar o afinar la red neuronal MobileNetV3 con datasets reales
(MESSIDOR-2, EyePACS, APTOS 2019) utilizando aumentación de datos y Focal Loss.
"""

import os
import argparse
import time
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import numpy as np

from core.model_engine import OculoEdgeNet
from core.preprocessor import enhance_retina_image


class FocalLoss(nn.Module):
    """Focal Loss para manejar el desbalance de clases clínico en retinopatía."""
    def __init__(self, alpha=None, gamma=2.0):
        super(FocalLoss, self).__init__()
        self.gamma = gamma
        self.alpha = alpha

    def forward(self, inputs, targets):
        ce_loss = nn.functional.cross_entropy(inputs, targets, reduction='none', weight=self.alpha)
        pt = torch.exp(-ce_loss)
        focal_loss = ((1.0 - pt) ** self.gamma) * ce_loss
        return focal_loss.mean()


class FundusDataset(Dataset):
    """Cargador de dataset de retinografías en estructura de carpetas (0 a 4) o lista."""
    def __init__(self, file_paths, labels, transform=None):
        self.file_paths = file_paths
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.file_paths)

    def __getitem__(self, idx):
        path = self.file_paths[idx]
        label = self.labels[idx]
        
        pil_img = Image.open(path).convert('RGB')
        img_np = np.array(pil_img)
        
        # Preprocesar con filtro Ben Graham
        _, processed = enhance_retina_image(img_np, target_size=(384, 384))
        img_pil = Image.fromarray(processed)
        
        if self.transform:
            img_tensor = self.transform(img_pil)
        else:
            img_tensor = transforms.ToTensor()(img_pil)
            
        return img_tensor, torch.tensor(label, dtype=torch.long)


def train_model(data_dir: str, epochs: int = 15, batch_size: int = 16, lr: float = 1e-4, output_weights: str = "weights/oculoedge_best.pth"):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[OculoEdge Training] Dispositivo activo: {device}")
    
    # Transformaciones con aumentación de datos médicos
    train_transforms = transforms.Compose([
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.5),
        transforms.RandomRotation(degrees=30),
        transforms.ColorJitter(brightness=0.1, contrast=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Cargar rutas de imágenes (soporta data_dir/<0..4>/image.jpg)
    train_paths, train_labels = [], []
    for grade in range(5):
        grade_folder = os.path.join(data_dir, str(grade))
        if os.path.exists(grade_folder):
            for fname in os.listdir(grade_folder):
                if fname.lower().endswith(('.jpg', '.jpeg', '.png')):
                    train_paths.append(os.path.join(grade_folder, fname))
                    train_labels.append(grade)

    if len(train_paths) == 0:
        print(f"[OculoEdge Training] No se encontraron imágenes estructuradas en {data_dir}/<0..4>/")
        print("Estructura requerida: data_dir/0/ (Sano), data_dir/1/ (Leve), data_dir/2/ (Moderada), etc.")
        return

    print(f"[OculoEdge Training] Total de imágenes encontradas: {len(train_paths)}")
    dataset = FundusDataset(train_paths, train_labels, transform=train_transforms)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=2)

    model = OculoEdgeNet(num_classes=5).to(device)
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    criterion = FocalLoss(gamma=2.0)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    best_loss = float('inf')
    os.makedirs(os.path.dirname(output_weights), exist_ok=True)

    for epoch in range(1, epochs + 1):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        t0 = time.time()
        
        for inputs, targets in loader:
            inputs, targets = inputs.to(device), targets.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * inputs.size(0)
            preds = torch.argmax(outputs, dim=1)
            correct += (preds == targets).sum().item()
            total += targets.size(0)
            
        scheduler.step()
        epoch_loss = running_loss / max(total, 1)
        epoch_acc = (correct / max(total, 1)) * 100
        el_time = time.time() - t0
        
        print(f"Época [{epoch:02d}/{epochs:02d}] - Pérdida: {epoch_loss:.4f} - Exactitud: {epoch_acc:.2f}% - Tiempo: {el_time:.1f}s")
        
        if epoch_loss < best_loss:
            best_loss = epoch_loss
            torch.save(model.state_dict(), output_weights)
            print(f"  → Checkpoint guardado en: {output_weights}")

    print(f"[OculoEdge Training] Entrenamiento finalizado. Mejor checkpoint en: {output_weights}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Entrenador de OculoEdge")
    parser.add_argument("--data_dir", type=str, default="data/train", help="Ruta al directorio de imágenes organizadas por clases (0-4)")
    parser.add_argument("--epochs", type=int, default=15, help="Número de épocas")
    parser.add_argument("--batch_size", type=int, default=16, help="Tamaño de lote")
    parser.add_argument("--lr", type=float, default=1e-4, help="Tasa de aprendizaje")
    parser.add_argument("--output", type=str, default="weights/oculoedge_best.pth", help="Ruta del checkpoint de pesos")
    args = parser.parse_args()
    
    train_model(args.data_dir, args.epochs, args.batch_size, args.lr, args.output)
