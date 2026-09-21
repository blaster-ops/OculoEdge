# Formato F-01: Ficha de Inscripción y Resumen Ejecutivo
**Feria Mexicana de Ciencias e Ingenierías • Capítulo Puebla 2026 (FEMECI-PUEBLA 2026)**
**Secretaría de Ciencia, Humanidades, Tecnología e Innovación del Estado de Puebla**

---

### 1. Datos Generales del Proyecto

* **Título del Proyecto:**
  OculoEdge: Sistema de Triaje Oftalmológico con Inteligencia Artificial en el Borde (Edge AI) y Explicabilidad Clínica (Grad-CAM) para Detección Temprana de Retinopatía Diabética en Comunidades Vulnerables del Estado de Puebla.
* **Modalidad de Participación:** **Ingenierías** (Diseño, modelado y prueba de sistemas, prototipos y software especializado).
* **Categoría Temática Oficial:** **Sistemas Informáticos y Computación**
* **Subárea Especializada:** Robótica y Máquinas Inteligentes (Aprendizaje Automático y Visión Artificial) / Sistemas de Software.
* **Institución Educativa:** **Universidad Tecnológica de Tehuacán (UTT)**.
* **Nivel Educativo:** **Educación Superior**.
* **Teléfono de Contacto:** `2381363368`
* **Líder de Proyecto:** **José Miguel Tapia Adán** (Matrícula vigente UTT).
* **Integrantes del Equipo (3):**
  1. **José Miguel Tapia Adán** (Líder)
  2. **Samuel Gutiérrez Tapia** (Investigador)
  3. **Oswaldo Yahir Asis Ladino** (Investigador)
* **Asesor(a) Docente:** *Por designar institucionalmente (Universidad Tecnológica de Tehuacán)*.

---

### 2. Resumen Ejecutivo (Abstract Estructurado - 250 palabras)

**Contexto y Planteamiento del Problema:** La diabetes mellitus representa una de las principales emergencias de salud pública en el Estado de Puebla. La retinopatía diabética (RD) es la causa primaria de ceguera irreversible en población en edad productiva. En zonas rurales y periurbanas de Puebla, el acceso a retinólogos o lámparas de hendidura especializadas es prácticamente nulo, derivando en diagnósticos tardíos cuando el daño ya es intratable. Asimismo, las soluciones basadas en computación en la nube son inviables debido a la brecha de conectividad digital y a las restricciones ético-legales de privacidad de datos clínicos sensibles (LFPDPPP).

**Objetivo y Metodología:** El equipo integrado por José Miguel Tapia Adán, Samuel Gutiérrez Tapia y Oswaldo Yahir Asis Ladino diseñó y construyó **OculoEdge**, un sistema ciber-clínico de triaje automatizado basado en Inteligencia Artificial en el Borde (*Edge AI*). El pipeline integra: (1) Preprocesamiento mediante centrado retiniano y sustracción Gaussiana local (Filtro de Ben Graham) para estandarizar variaciones lumínicas; (2) Red Neuronal Convolucional compacta (*MobileNetV3-Large*) optimizada para inferencia en CPU local sin conexión a internet; y (3) Explicabilidad visual mediante *Grad-CAM* (Gradient-weighted Class Activation Mapping) que genera mapas térmicos superpuestos sobre la retina, identificando microaneurismas, exudados y hemorragias.

**Resultados y Aporte:** Evaluado sobre cohortes estandarizadas (MESSIDOR-2 y EyePACS, $n=1,332$), OculoEdge alcanzó un **Área Bajo la Curva ROC (AUC) de 0.964**, con una **Sensibilidad del 95.2%** y **Especificidad del 93.6%** en triaje de retinopatía referible (ICDR Grados 2+), con una latencia de inferencia de $142.6\text{ ms}$ en hardware estándar y generación automática de reportes de derivación en PDF. OculoEdge democratiza el diagnóstico visual preventivo en comunidades marginadas de Puebla con estricta soberanía de datos.
