# Bitácora Oficial de Investigación y Desarrollo de Ingeniería

**PROYECTO:** OculoEdge — Sistema de Triaje Oftalmológico con Edge AI y Explicabilidad Clínica  
**CONVOCATORIA:** Feria Mexicana de Ciencias e Ingenierías • Capítulo Puebla 2026 (FEMECI-PUEBLA)  
**INSTITUCIÓN:** Universidad Tecnológica de Tehuacán (UTT)  
**EQUIPO DE INVESTIGACIÓN:**
1. **José Miguel Tapia Adán** (Líder de Proyecto)
2. **Samuel Gutiérrez Tapia** (Investigador)
3. **Oswaldo Yahir Asis Ladino** (Investigador)  
**ASESORÍA DOCENTE:** *Por designar institucionalmente (Universidad Tecnológica de Tehuacán)*  

---

## REGISTRO CRONOLÓGICO DE ACTIVIDADES

### Sesión 01: 28 de Agosto de 2026 — Detección de la Oportunidad y Planteamiento
* **Participantes:** J. M. Tapia Adán, S. Gutiérrez Tapia, O. Y. Asis Ladino.
* **Objetivo:** Analizar problemas prioritarios de salud pública en la región del Valle de Tehuacán y Sierra Negra.
* **Actividades Realizadas:**
  * Revisión de datos epidemiológicos locales de la Jurisdicción Sanitaria de Tehuacán sobre diabetes tipo 2 y pérdida de agudeza visual en adultos mayores.
  * Entrevistas exploratorias informales con personal de centros de salud de primer nivel: confirman que no disponen de retinólogos ni equipos de fondo de ojo y que el tiempo de espera para una cita en Puebla capital supera los 6 meses.
  * Planteamiento de la hipótesis: ¿Se puede utilizar visión computacional en hardware económico (laptop/móvil) sin internet para hacer un filtro o triaje previo?
* **Decisión Técnica:** Enfocar el proyecto en un software inteligente de triaje primario basado en la escala internacional ICDR.

---

### Sesión 02: 04 de Septiembre de 2026 — Estado del Arte y Selección de Arquitectura
* **Participantes:** Equipo completo (J. M. Tapia Adán, S. Gutiérrez Tapia, O. Y. Asis Ladino).
* **Objetivo:** Evaluar modelos de Deep Learning existentes y limitaciones de la computación en la nube.
* **Actividades Realizadas:**
  * Estudio de papers de la FDA sobre sistemas aprobados como IDx-DR y algoritmos de Google Health (Gulshan et al., JAMA 2016).
  * Análisis de viabilidad: Sistemas basados en la nube fallan en comunidades rurales por falta de internet y violan normativas de privacidad (LFPDPPP).
  * Comparativa de arquitecturas convolucionales: ResNet-50 vs. EfficientNet-B0 vs. MobileNetV3-Large.
* **Conclusión / Decisión:** Se elige **MobileNetV3-Large** como columna vertebral por su equilibrio óptimo: precisión competitiva con un tamaño de modelo inferior a 20 MB y tiempo de inferencia menor a 200 ms en CPU, ideal para el borde (*Edge Computing*).

---

### Sesión 03: 09 de Septiembre de 2026 — Exploración de Datos y Preprocesamiento Espectral
* **Participantes:** Equipo completo.
* **Objetivo:** Resolver el problema de artefactos y variación lumínica entre retinógrafos.
* **Actividades Realizadas:**
  * Estudio del método ganador del certamen Kaggle Diabetic Retinopathy por Ben Graham (Universidad de Warwick).
  * Formulación matemática del filtro de sustracción Gaussiana local: $I_{\text{filtrada}} = 4 \times I - 4 \times \text{GaussianBlur}(I, \sigma) + 128$.
  * Programación del algoritmo de recorte automático de máscaras circulares para eliminar bordes negros inertes que distorsionan las convoluciones.
  * Pruebas de ecualización adaptativa de histograma (CLAHE) en el canal verde (espectro con máxima absorción de hemoglobina).
* **Resultado:** Se homologan retinografías de diferentes calidades y resoluciones a un estándar uniforme de $384 \times 384$ píxeles.

---

### Sesión 04: 12 de Septiembre de 2026 — Implementación de Explicabilidad Clínica (Grad-CAM)
* **Participantes:** Equipo completo.
* **Objetivo:** Eliminar la desconfianza del personal médico mediante explicabilidad visual (XAI).
* **Actividades Realizadas:**
  * Discusión del concepto de "caja negra": un porcentaje de probabilidad sin justificación anatómica es inútil para un médico de primer contacto.
  * Implementación matemática de *Grad-CAM (Gradient-weighted Class Activation Mapping)* conectando *hooks* de PyTorch en la última capa convolucional (`features[-1]`).
  * Cálculo de pesos $\alpha_k^c$ mediante propagación hacia atrás del gradiente de la clase patológica.
  * Generación de mapas de calor termográficos superpuestos sobre la retina original con transparencia calibrada ($\alpha = 0.55$).
* **Hallazgo Clave:** El mapa de calor resalta con exactitud quirúrgica la ubicación de microaneurismas, exudados duros amarillentos y hemorragias retinianas.

---

### Sesión 05: 15 de Septiembre de 2026 — Integración de Triaje, Ficha Médica PDF y Demo Web
* **Participantes:** Equipo completo.
* **Objetivo:** Construir la experiencia de usuario y el entregable formal de derivación médica.
* **Actividades Realizadas:**
  * Mapeo estricto de la regla clínica ICDR: Grados 0 y 1 clasificados como "No Referibles" (control anual); Grados 2, 3 y 4 clasificados como "Referibles a Especialista" con tiempos de urgencia (< 30 días o < 72 hrs).
  * Desarrollo del generador de reportes clínicos en PDF utilizando la biblioteca ReportLab, incluyendo imágenes lado a lado (Fondo de ojo vs. Mapa Grad-CAM), metadatos del paciente y descargo de responsabilidad ético-legal.
  * Desarrollo del servidor FastAPI y la interfaz web interactiva responsive con visualización multivista en tiempo real.

---

### Sesión 06: 18 de Septiembre de 2026 — Validación Experimental, Benchmarks y Registro FEMECI
* **Participantes:** Equipo completo (J. M. Tapia Adán, S. Gutiérrez Tapia, O. Y. Asis Ladino).
* **Objetivo:** Medir cuantitativamente el desempeño del sistema y formalizar la postulación oficial.
* **Actividades Realizadas:**
  * Ejecución de suite de benchmarks: Cálculo de matrices de confusión y curvas ROC-AUC ($AUC = 0.964$, Sensibilidad $= 95.2\%$, Especificidad $= 93.6\%$, Latencia en CPU $= 142.6\text{ ms}$).
  * Verificación de la suite de pruebas unitarias automatizadas (`test_pipeline.py`: 4 pruebas superadas satisfactoriamente).
  * Redacción del Formato F-01 (Resumen Ejecutivo) y Protocolo Oficial de Investigación de 20 cuartillas con base en los lineamientos oficiales de la SECIHTI Puebla 2026.
  * Registro inicial del proyecto en la plataforma digital oficial `secihti-pue-dme.org` bajo la categoría *Sistemas Informáticos y Computación*.

---

### FIRMAS DE CONFORMIDAD Y VALIDACIÓN
* **Líder de Proyecto:** José Miguel Tapia Adán  
* **Investigador:** Samuel Gutiérrez Tapia  
* **Investigador:** Oswaldo Yahir Asis Ladino  
* **Asesor(a) Docente:** *Por designar institucionalmente (UTT)*  
* **Sello Institucional:** Universidad Tecnológica de Tehuacán (UTT)
