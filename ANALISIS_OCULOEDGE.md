# Análisis técnico de OculoEdge (estado inicial)

Este informe documenta el código de main antes de los cambios 2.0. Para el estado de la versión actual, consultar README.md y VERIFICACION.md.

Fecha: 11 de octubre de 2026. Repositorio: [blaster-ops/OculoEdge](https://github.com/blaster-ops/OculoEdge). Rama `main`, commit `9da7eda22f648a897a32d10a1439a80a972bcaab`, del 23 de septiembre de 2026.

## Evaluación general

OculoEdge tiene una base útil para un prototipo de investigación: carga y captura de imágenes, preprocesamiento, interfaz para cinco grados ICDR, mapas de calor y generación de reportes PDF. La separación entre servidor, procesamiento, explicabilidad, datos y reportes facilita continuar el desarrollo.

La evidencia revisada todavía no sostiene presentarlo como un sistema clínicamente validado. Los principales problemas son la procedencia de las métricas, la desconexión entre la clasificación y la red neuronal, y la ausencia de rechazo de imágenes no evaluables.

## Funcionamiento real

`/api/diagnose` recibe la imagen y llama a `DiagnosticEngine.predict()`. Este método recorta y redimensiona, cuenta píxeles oscuros y brillantes, mide bordes en una región estimada como disco óptico y aplica umbrales. Después asigna uno de cinco vectores constantes y calcula softmax.

Aunque el motor carga MobileNetV3, `predict()` no llama a esa red. La aplicación llama posteriormente a la red para generar Grad-CAM. Por tanto, el mapa explica una puntuación neuronal distinta del mecanismo que produjo el diagnóstico mostrado.

El módulo `core/biomarkers.py`, que contiene análisis morfológico más detallado, no está integrado en el flujo de diagnóstico revisado.

## Hallazgos prioritarios

### 1. Crítico: métricas simuladas presentadas como validación experimental

[evaluate_metrics.py](https://github.com/blaster-ops/OculoEdge/blob/9da7eda22f648a897a32d10a1439a80a972bcaab/benchmarks/evaluate_metrics.py#L19) contiene una matriz de confusión escrita manualmente, una curva ROC generada por una fórmula y resultados JSON constantes. No carga una cohorte ni ejecuta inferencia. El README, el protocolo y la guía de defensa atribuyen cifras a 1,332 imágenes MESSIDOR-2/EyePACS.

No encontré en el repositorio predicciones por imagen, particiones, identificadores de evaluación ni registros que permitan reproducir esa validación. Esto no prueba que nunca se haya hecho trabajo externo; sí significa que las cifras no quedan sustentadas por el material publicado.

| Medida | Recalculada desde los datos simulados del script | Publicada en el JSON |
|---|---:|---:|
| Exactitud multiclase | 90.77% | 89.2% |
| Sensibilidad binaria, grados 2+ | 96.03% | 95.2% |
| Especificidad binaria, grados 2+ | 97.25% | 93.6% |
| Área de la curva generada | 0.9117 | 0.964 |

El README publica otra especificidad: 96.8%. Los valores recalculados tampoco son resultados clínicos: solo exponen la inconsistencia interna del material simulado.

**Acción:** marcar esas gráficas y cifras como ilustrativas hasta disponer de una evaluación reproducible; corregir también protocolo, resumen ejecutivo, cartel y guía de defensa.

### 2. Crítico: clasificación y explicabilidad no corresponden

[model_engine.py](https://github.com/blaster-ops/OculoEdge/blob/9da7eda22f648a897a32d10a1439a80a972bcaab/core/model_engine.py#L205) decide por reglas. [explainer.py](https://github.com/blaster-ops/OculoEdge/blob/9da7eda22f648a897a32d10a1439a80a972bcaab/core/explainer.py#L61) calcula gradientes de MobileNetV3.

**Acción:** usar la salida de un modelo entrenado y validado para decidir y explicar, o presentar explícitamente el clasificador como heurístico con una visualización de las regiones y reglas que sí intervinieron. Si se implementa fusión, documentar y evaluar la contribución de cada componente.

### 3. Crítico: imágenes inválidas reciben resultados muy seguros

Al ejecutar aisladamente los métodos originales de clasificación, obtuve:

| Entrada | Resultado | Confianza mostrada |
|---|---|---:|
| Negro uniforme | Grado 4, proliferativa | 98.33% |
| Gris uniforme de intensidad 128 | Grado 0, normal | 98.65% |
| Blanco uniforme | Grado 2, moderada | 98.17% |

Las cinco muestras del repositorio reciben los grados esperados, con confianza entre 97.57% y 98.65%. Sin embargo, el cargador genera muestras sintéticas y la prueba de exactitud utiliza únicamente esos cinco casos.

La confianza procede de vectores constantes por regla; no mide incertidumbre individual ni demuestra calibración estadística.

**Acción:** añadir control de calidad y resultado «no evaluable», pruebas con desenfoque, exposición incorrecta e imágenes no retinianas, y calibración sobre datos independientes.

### 4. Alta: funcionamiento sin internet incompleto

[index.html](https://github.com/blaster-ops/OculoEdge/blob/9da7eda22f648a897a32d10a1439a80a972bcaab/static/index.html#L7) descarga Tailwind, fuentes y Lucide desde servidores externos. Sin caché y sin red, `lucide.createIcons()` puede detener el script antes de inicializar la aplicación.

Además, el constructor de MobileNetV3 solicita pesos preentrenados de torchvision antes de cargar el checkpoint local, por lo que el primer arranque necesita esos pesos en caché o acceso de red.

**Acción:** empaquetar CSS, iconos y fuentes localmente, construir el modelo sin descargar pesos cuando se carga un checkpoint completo y comprobar el arranque desde una instalación sin caché y con red deshabilitada.

### 5. Alta: la regla clínica implementada difiere de la documentada

El código etiqueta «regla 4-2-1 positiva» si hay daño en tres cuadrantes o un total de píxeles oscuros superior al umbral. No evalúa arrosariamiento venoso ni IRMA. La regla publicada considera hemorragias graves en cuatro cuadrantes, arrosariamiento venoso en dos o más, o IRMA en uno o más, sin signos proliferativos. Véanse las [guías de la American Society of Retina Specialists](https://pmc.ncbi.nlm.nih.gov/articles/PMC8297841/).

**Acción:** revisar las reglas y los textos de hallazgos con un especialista; diferenciar medidas de imagen, sospechas y hallazgos confirmados.

### 6. Media: el QR no constituye una firma digital

[triage_report.py](https://github.com/blaster-ops/OculoEdge/blob/9da7eda22f648a897a32d10a1439a80a972bcaab/reports/triage_report.py#L107) calcula SHA-256 sobre algunos campos y la fecha, y conserva 16 caracteres hexadecimales. No emplea una clave de firma ni cubre el PDF completo, las imágenes y todos los resultados.

**Acción:** describirlo como identificador de trazabilidad, o implementar firma verificable de un contenido canónico que incluya la evidencia y la versión del modelo.

### 7. Media: reproducibilidad, API e instalación

No hay workflows de GitHub Actions y la consulta de ejecuciones devolvió cero resultados. Las dependencias solo fijan mínimos. El entrenamiento no separa validación y selecciona el checkpoint por pérdida de entrenamiento; además guarda `oculoedge_best.pth`, mientras el servidor carga por defecto `oculoedge_calibrated.pth`.

La API acepta archivos completos en memoria sin un límite explícito, permite CORS amplio y carece de autenticación. El lanzador escucha en todas las interfaces. Los endpoints `async` ejecutan procesamiento pesado de forma síncrona. Son aspectos a resolver si se amplía el uso más allá de una demostración local.

El lanzador y la guía están orientados a Linux; falta un procedimiento equivalente para Windows.

**Acción:** fijar un entorno reproducible, añadir CI, separar conjuntos por paciente, registrar configuración y procedencia del checkpoint, limitar entradas y usar localhost como configuración local predeterminada.

## Verificación y límites

- Revisé el código Python, la interfaz HTML/JavaScript, las dependencias, los documentos Markdown y la actividad disponible en GitHub.
- Todos los archivos Python del repositorio pasaron compilación sintáctica.
- Ejecuté los métodos originales `predict()` y `_extract_clinical_features()` aislados mediante AST, con el preprocesador original, NumPy y OpenCV. Esto comprueba la lógica de clasificación sin inicializar la red neuronal.
- Recalculé la matriz y el área numérica de la curva del script de benchmarks.
- No ejecuté la suite completa de unittest ni Grad-CAM: el entorno no tiene PyTorch, torchvision y FastAPI. No comprobé latencia real, cámara, interfaz en navegador ni entrenamiento del checkpoint.
- No modifiqué el código del repositorio ni publiqué cambios en GitHub.

## Orden de trabajo recomendado

1. Corregir la presentación de resultados y etiquetar claramente las demostraciones sintéticas.
2. Incorporar rechazo de imágenes no evaluables y alinear clasificación con explicabilidad.
3. Eliminar dependencias de red en ejecución y verificar una instalación offline limpia.
4. Construir evaluación reproducible con imágenes reales, particiones independientes y métricas calculadas desde predicciones.
5. Añadir CI, empaquetado para Windows y controles de API adecuados al uso previsto.

La prioridad inmediata es que el comportamiento y la documentación describan fielmente la evidencia disponible. Esa coherencia fortalecerá tanto el desarrollo técnico como la defensa del proyecto.
