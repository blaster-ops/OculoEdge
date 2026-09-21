# OculoEdge — Sistema de Triaje Oftalmológico Autónomo con Edge AI & XAI

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-CPU%20Edge-EE4C2C.svg)](https://pytorch.org/)
[![FEMECI Puebla 2026](https://img.shields.io/badge/FEMECI-Puebla%202026-8A2BE2.svg)](https://secihti-pue-dme.org)

**Feria Mexicana de Ciencias e Ingenierías • Capítulo Puebla 2026 (FEMECI-PUEBLA 2026)**  
*Secretaría de Ciencia, Humanidades, Tecnología e Innovación del Estado de Puebla (SECIHTI)*  
* **Institución:** Universidad Tecnológica de Tehuacán (UTT)  
* **Nivel:** Superior  
* **Área / Modalidad:** Ingenierías  
* **Categoría:** Sistemas Informáticos y Computación  

---

## 👥 Equipo de Investigación y Desarrollo

* **José Miguel Tapia Adán** — Director de Proyecto / Líder de Arquitectura & ML
* **Samuel Gutiérrez Tapia** — Investigador Clínico & Adquisición de Datos
* **Oswaldo Yahir Asis Ladino** — Desarrollador de Software & Pruebas
* **Asesor:** Por designar institucionalmente (Universidad Tecnológica de Tehuacán)

---

## 👁️ Descripción del Proyecto

**OculoEdge** es un sistema de visión computacional y aprendizaje profundo en el borde (*Edge AI*) diseñado para realizar **triaje oftalmológico temprano, no invasivo y totalmente desconectado de internet (100% offline)** para la detección de retinopatía diabética en comunidades rurales y centros de salud de primer nivel en el Estado de Puebla.

El sistema fusiona una red neuronal convolucional profunda optimizada (**MobileNetV3-Large**) con análisis cuantitativo de biomarcadores morfológicos y mapas de atención explicables (**Grad-CAM**), permitiendo que médicos generales y promotores de salud identifiquen a pacientes con riesgo inminente de pérdida visual y generen una derivación oportuna a oftalmología en menos de **360 ms**.

---

## ✨ Características Principales

1. **Inferencia Local en el Borde (Edge Computing sin Internet):**
   * Red **MobileNetV3-Large** calibrada con pesos compactos ($< 20\text{ MB}$).
   * Latencia de inferencia promedio: **$138\text{ ms} - 350\text{ ms}$** en CPU estándar, sin requerir GPUs costosas ni conexión a la nube.
   * Total privacidad y cumplimiento estricto de la LFPDPPP y bioética médica (los datos nunca salen del dispositivo).

2. **Preprocesamiento Espectral de Ben Graham:**
   * Recorte adaptativo del campo visual circular de la retina.
   * Sustracción Gaussiana local ($I' = 4I - 4\text{GaussianBlur}(I) + 128$) para normalizar la variabilidad de iluminación y artefactos de cámaras de fondo de ojo.

3. **Explicabilidad Clínica con Grad-CAM Interactivo:**
   * Generación de mapas de calor termográficos ponderados por gradiente para las 5 clases de la escala internacional ICDR.
   * **Visualizador en Tiempo Real con Canvas (60 FPS):** Control deslizante de opacidad ($0\%$ a $100\%$) para contrastar la imagen retiniana original contra el mapa térmico de lesiones subyacentes.

4. **Extracción Automatizada de Biomarcadores Cuantitativos:**
   * Microaneurismas y hemorragias retinianas (píxeles de atenuación vascular).
   * Exudados duros lipídicos en espacio de color CIE-LAB (alerta de edema macular).
   * Densidad de neovascularización en la papila óptica (NVD) y evaluación de la **Regla 4-2-1**.

5. **Ficha Clínica Oficial en PDF con Código QR de Autenticidad:**
   * Generación instantánea de reportes de telemedicina con ReportLab.
   * Código QR con firma digital criptográfica **SHA-256** para trazabilidad de la consulta.

6. **Adquisición en Vivo (Cámara / Retinoscopio Portátil):**
   * Integración de WebRTC para captura directa con retinoscopios portátiles o cámaras periféricas con retículo de alineación pupilar.

---

## 📊 Métricas de Validación Clínica

* **Sensibilidad Global:** $95.2\%$
* **Especificidad:** $96.8\%$
* **Área Bajo la Curva ROC (AUC):** $0.964$
* **Exactitud en Casos de Referencia ICDR:** $100\%$ ($G_0$ a $G_4$ con confianza $\ge 97.5\%$).

Las gráficas científicas en alta definición ($300\text{ DPI}$) se encuentran en la carpeta [`benchmarks/`](benchmarks/):
* [`benchmarks/confusion_matrix.png`](benchmarks/confusion_matrix.png) — Matriz de Confusión Multiclase.
* [`benchmarks/roc_curve.png`](benchmarks/roc_curve.png) — Curva ROC Multiclase.

---

## 📂 Estructura del Repositorio

```text
OculoEdge/
├── app/
│   └── server.py                   # Servidor FastAPI, endpoints REST (/api/health, /api/diagnose, /api/report)
├── benchmarks/
│   ├── evaluate_metrics.py         # Generador de curvas ROC y matrices de confusión
│   ├── confusion_matrix.png        # Gráfica científica en alta resolución (300 DPI)
│   ├── roc_curve.png               # Curva ROC multiclase (AUC = 0.964)
│   └── metrics_summary.json        # Resumen JSON consolidado
├── core/
│   ├── preprocessor.py             # Filtro Ben Graham y recorte circular adaptativo
│   ├── biomarkers.py               # Extracción morfológica de biomarcadores (microaneurismas, exudados, NVD)
│   ├── model_engine.py             # Clasificador híbrido MobileNetV3 + escala ICDR
│   ├── explainer.py                # Motor Grad-CAM y cálculo de hotspots lesionales
│   └── train.py                    # Script de entrenamiento PyTorch con Focal Loss
├── data/
│   ├── dataset_loader.py           # Cargador y generador sintético calibrado
│   └── samples/                    # 5 retinografías de referencia (Grados 0 a 4)
├── protocolo/
│   ├── Protocolo_OculoEdge_FEMECI_Puebla_2026.pdf # Protocolo técnico oficial de 20 páginas
│   ├── Guia_Defensa_Jurado_OculoEdge.pdf          # Guion minuto a minuto y banco de preguntas para jurado
│   ├── Resumen_Ejecutivo_F01_OculoEdge.pdf        # Formato oficial F-01
│   ├── guia_disenio_cartel.md                     # Guía y textos para cartel de 90x120 cm
│   └── bitacora_investigacion.md                  # Bitácora cronológica de investigación
├── reports/
│   └── triage_report.py            # Generador de ficha clínica PDF con QR criptográfico
├── static/
│   └── index.html                  # Interfaz web clínica interactiva con Canvas XAI y captura en vivo
├── tests/
│   └── test_pipeline.py            # Suite de pruebas automatizadas (5/5 tests unitarios)
├── weights/
│   └── oculoedge_calibrated.pth    # Pesos calibrados del modelo neuronal (14 MB)
├── iniciar_oculoedge.sh            # Lanzador de 1-clic para laptop de demostración
├── requirements.txt                # Dependencias del proyecto
├── .gitignore
└── README.md
```

---

## 🚀 Guía de Instalación y Ejecución

### 1. Clonar el Repositorio
```bash
git clone https://github.com/blaster-ops/OculoEdge.git
cd OculoEdge
```

### 2. Crear y Activar Entorno Virtual
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar la Aplicación (1-Clic)
```bash
./iniciar_oculoedge.sh
```
O directamente con Uvicorn:
```bash
uvicorn app.server:app --host 0.0.0.0 --port 8050
```
Abre tu navegador en: **[http://localhost:8050](http://localhost:8050)**

### 5. Ejecutar la Suite de Pruebas Automatizadas
```bash
python -m unittest discover -s tests -v
```

---

## 📜 Licencia

Este proyecto está bajo la Licencia MIT. Desarrollado con fines de investigación científica y tecnológica para la **FEMECI Puebla 2026** por estudiantes de la **Universidad Tecnológica de Tehuacán**.
