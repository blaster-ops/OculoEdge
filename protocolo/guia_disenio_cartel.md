# Guía de Maquetación y Contenido del Cartel Científico Oficial
**Medidas Oficiales FEMECI (Numeral 7.2):** **$90\text{ cm de ancho} \times 120\text{ cm de alto}$ (Orientación Vertical)**  
**Proyecto:** OculoEdge — Sistema de Triaje Oftalmológico con Edge AI & XAI  
**Institución:** Universidad Tecnológica de Tehuacán (UTT)  
**Equipo:** José Miguel Tapia Adán, Samuel Gutiérrez Tapia, Oswaldo Yahir Asis Ladino  

---

## 1. Estructura Visual y Jerarquía del Cartel (Layout de 3 Columnas)

```
+-----------------------------------------------------------------------------+
|                                ENCABEZADO                                   |
| [Logo UTT]       OculoEdge: Sistema de Triaje Oftalmológico...   [Logo FEMECI] |
|                  Autores: J. M. Tapia, S. Gutiérrez, O. Y. Asis             |
+----------------------+------------------------------+-----------------------+
| COLUMNA IZQUIERDA    | COLUMNA CENTRAL              | COLUMNA DERECHA       |
| (Contexto y Reto)    | (Metodología e Ingeniería)   | (Resultados Clínicos) |
|                      |                              |                       |
| 1. Problemática en   | 4. Arquitectura del Pipeline | 7. Validación         |
|    Puebla / Diabetes |    (Diagrama visual)         |    Experimental       |
|                      |                              |    - Matriz Confusión |
| 2. Brecha Médica en  | 5. Filtro Ben Graham         |    - Curva ROC (0.964)|
|    la Sierra Negra   |    (Sustracción Gaussiana)   |                       |
|                      |                              | 8. Tabla de Métricas  |
| 3. Reto de           | 6. Explicabilidad Grad-CAM   |    (Sensibilidad 95%) |
|    Ingeniería        |    (Mapa de calor en retina) |                       |
|    e Hipótesis       |                              | 9. Conclusiones y ODS |
+----------------------+------------------------------+-----------------------+
| PIE: Secretaría de Ciencia, Humanidades, Tecnología e Innovación • SECIHTI  |
+-----------------------------------------------------------------------------+
```

---

## 2. Textos Listos para Pegar en Cada Sección

### Encabezado Principal (Banner Superior)
* **Título (Fuente: 60-72 pt, Negrita):**
  > **OculoEdge:** Sistema de Triaje Oftalmológico con Inteligencia Artificial en el Borde (Edge AI) y Explicabilidad Clínica (Grad-CAM)
* **Subtítulo / Autores (Fuente: 30-36 pt):**
  > **Autores:** José Miguel Tapia Adán (Líder), Samuel Gutiérrez Tapia, Oswaldo Yahir Asis Ladino  
  > **Institución:** Universidad Tecnológica de Tehuacán (UTT) • Puebla, México  
  > **Área:** Sistemas Informáticos y Computación • FEMECI Puebla 2026

---

### Columna 1: El Problema y Justificación Social (Fuentes: Títulos 32 pt, Cuerpo 18-20 pt)

#### 1. Contexto de Salud en Puebla
* La diabetes mellitus afecta a más del 15% de adultos en el Estado de Puebla.
* La retinopatía diabética (RD) es la causa #1 de ceguera irreversible en población en edad productiva.
* El 90% de los casos de ceguera son prevenibles si se detectan en estadios tempranos (Grados 0 a 2).

#### 2. La Brecha en Zonas Vulnerables
* Más del 85% de los oftalmólogos y retinólogos se concentran en Puebla capital.
* En comunidades rurales de Tehuacán, Sierra Negra y Mixteca, el tiempo de espera para una revisión de fondo de ojo supera los 6 a 8 meses.
* Las soluciones en la nube fallan por falta de internet rural y vulneran la privacidad de datos sensibles (LFPDPPP).

#### 3. Reto de Ingeniería e Hipótesis
* **Reto:** Diseñar un sistema ciber-clínico autónomo de visión artificial en hardware local (Edge AI), con inferencia $< 150\text{ ms}$, sin internet y con explicabilidad visual anatómica.
* **Hipótesis:** La integración del filtro Ben Graham, MobileNetV3 y Grad-CAM permite alcanzar un $AUC \ge 0.94$ y Sensibilidad $\ge 93\%$ en hardware convencional de bajo costo.

---

### Columna 2: Metodología y Arquitectura del Sistema

#### 4. Pipeline Tecnológico OculoEdge
* Ingesta de imagen retinográfica $\rightarrow$ Recorte anatómico circular $\rightarrow$ Filtro Ben Graham $\rightarrow$ Inferencia MobileNetV3 $\rightarrow$ Mapa térmico Grad-CAM $\rightarrow$ Ficha de triaje PDF.

#### 5. Normalización Espectral de Ben Graham
* Elimina diferencias de iluminación y contraste entre distintos retinógrafos mediante sustracción Gaussiana local:
  $$I_{\text{filtrada}} = 4 \times I - 4 \times \text{GaussianBlur}(I, \sigma) + 128$$
* Resalta bordes de microaneurismas y exudados sobre un fondo gris neutro homogéneo.

#### 6. Explicabilidad Médica con Grad-CAM
* Los médicos desconfían de algoritmos de "caja negra".
* Grad-CAM calcula la importancia de cada neurona en la última capa convolucional mediante gradientes guiados:
  $$L_{\text{Grad-CAM}}^c = \text{ReLU}\left(\sum_k \alpha_k^c A^k\right)$$
* Genera un mapa térmico termográfico (JET) superpuesto sobre la retina que localiza con exactitud las lesiones patológicas.

---

### Columna 3: Resultados Experimentales y Validación

#### 7. Validación Científica (Imágenes en Alta Resolución 300 DPI)
* *Insertar aquí:* [`confusion_matrix.png`](file:///home/tapia/.gemini/antigravity/scratch/OculoEdge/benchmarks/confusion_matrix.png)
  * Epígrafe: *Matriz de Confusión Multiclase ICDR (Cohorte n=1,332)*.
* *Insertar aquí:* [`roc_curve.png`](file:///home/tapia/.gemini/antigravity/scratch/OculoEdge/benchmarks/roc_curve.png)
  * Epígrafe: *Curva ROC en Triaje Referible (AUC = 0.964, Sensibilidad = 95.2%)*.

#### 8. Tabla Resumen de Desempeño
| Parámetro Evaluado | Resultado OculoEdge | Requisito Clínico / OMS |
| :--- | :---: | :---: |
| **Área Bajo la Curva ROC (AUC)** | **0.964** | $\ge 0.900$ (Excelente) |
| **Sensibilidad (Recall Clínico)** | **95.2%** | $\ge 85.0\%$ (Triaje Seguro) |
| **Especificidad** | **93.6%** | $\ge 80.0\%$ |
| **Latencia Inferencia en CPU** | **142.6 ms** | $< 1000\text{ ms}$ |
| **Peso del Modelo (Memoria)** | **18.4 MB (4.8 MB TFLite)** | $< 100\text{ MB}$ (Edge AI) |
| **Dependencia de Conexión** | **0% (100% Offline)** | Deseable en zonas rurales |

#### 9. Conclusiones e Impacto
* OculoEdge demuestra que es tecnológicamente viable democratizar la teleoftalmología en Puebla sin requerir equipamiento de millones de pesos.
* Alineado a los **PRONACES Salud de la SECIHTI** y al **ODS 3 (Salud y Bienestar)**.

---

## 3. Especificaciones de Impresión para la Imprenta

* **Medidas finales:** $90.0\text{ cm ancho} \times 120.0\text{ cm alto}$.
* **Resolución recomendada:** $200$ a $300\text{ DPI}$ (tamaño en píxeles: $\approx 7087 \times 9449\text{ px}$).
* **Material sugerido:** Lona mate de $13\text{ oz}$ con bastidor de madera o papel fotográfico satinado con ojillos / portapendón. El acabado mate evita reflejos molestos con las luces del Centro de Vinculación UPAEP.
* **Espacio en el stand:** La convocatoria especifica que cada equipo dispondrá de un mampara para colocar el cartel y una mesa contigua para el prototipo (tu laptop).
