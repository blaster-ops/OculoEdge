# OculoEdge: protocolo de ingeniería para revisión del equipo

## Identificación

FEMECI Puebla 2026. Modalidad: Ingenierías. Categoría: Sistemas Informáticos y Computación. Institución: Universidad Tecnológica de Tehuacán. Equipo: José Miguel Tapia Adán, Samuel Gutiérrez Tapia y Oswaldo Yahir Asis Ladino. Asesor institucional: nombre y validación pendientes del equipo UTT. Versión de software: 2.0.0. Actualización: 11 de octubre de 2026.

Este documento describe el prototipo disponible y sus límites. Requiere revisión del equipo y del asesor antes de su presentación como expediente institucional. No contiene firmas ni certificaciones emitidas por terceros.

## Problema y meta de ingeniería

Investigar un flujo local para procesar imágenes de fondo de ojo, visualizar evidencia del cálculo y generar informes reproducibles en entornos con conectividad limitada. La pertinencia regional y cualquier cifra epidemiológica deberán justificarse con fuentes específicas verificadas por el equipo.

Meta de esta etapa: disponer de un prototipo que opere sin servicios externos, rechace entradas manifiestamente inadecuadas, diferencie demostraciones sintéticas de imágenes cargadas y vincule la explicación al mecanismo que produce el resultado.

## Alcance actual

La versión de exhibición utiliza reglas experimentales basadas en mediciones de píxeles. No es un sistema clínicamente validado y no emite diagnóstico, descarte de enfermedad ni decisiones de tratamiento. No se asignan probabilidades clínicas a las reglas. Los cinco grados G0–G4 son patrones de demostración inspirados en la clasificación de retinopatía; los umbrales no implementan criterios clínicos ICDR ni la regla 4-2-1.

MobileNetV3 y Grad-CAM están implementados como componente opcional que requiere checkpoint y manifiesto de entrenamiento. Se probaron con datos sintéticos exclusivamente para verificar funcionamiento de software. No se dispone de imágenes clínicas etiquetadas ni evidencia reproducible de validación de los pesos originales.

## Diseño y metodología

Entrada JPG/PNG/WebP o captura desde cámara USB. Límites explícitos de tamaño y resolución; corrección de orientación. Controles exploratorios de contraste, exposición, detalle y color; resultado no evaluable si fallan. Pasar los controles no garantiza origen retiniano ni calidad diagnóstica.

Preprocesamiento: recorte de bordes oscuros, redimensionamiento a 384 × 384 y filtro de Ben Graham. Mediciones: píxeles oscuros, píxeles brillantes, bordes en región estimada de disco y distribución por cuadrantes. Las máscaras son estimadores de imagen y no segmentaciones de lesiones confirmadas.

Motor de reglas: umbrales transparentes de demostración con texto de la regla aplicada. Explicación: máscara de las regiones usadas por esa regla. Motor neuronal opcional: inferencia de MobileNetV3 con checkpoint local, verificación SHA-256 y Grad-CAM de la misma red. La ejecución no descarga pesos.

Informe: un identificador de análisis conecta resultado mostrado, imágenes y PDF. El informe no recalcula sobre otra imagen. Registro canónico con hashes de imagen/explicación, metadatos de motor y controles; HMAC-SHA256 con clave local para autenticación del registro y del PDF exportado.

## Pruebas ejecutables y resultados

La suite automatizada cubre muestras, imágenes uniformes, desenfoque, resolución baja, límites de archivo/píxeles, entrada inválida, concurrencia, coherencia de snapshots, generación PDF, escapado de campos y rechazo de registros alterados. Comprueba funcionamiento sin conexiones externas. El componente neuronal se ejercita con entrenamiento sintético de una época, inferencia, Grad-CAM y evaluación sobre una partición de prueba sintética; esto no mide desempeño clínico.

El benchmark ejecuta predicciones sobre las cinco muestras sintéticas del repositorio y guarda predicciones por imagen, matriz de confusión, rechazos y latencia local medida. La versión de demostración obtiene los patrones esperados en esas cinco muestras. ROC/AUC no se calcula para las reglas porque no producen puntuaciones probabilísticas.

No se sostienen las cifras anteriores de AUC 0.964, sensibilidad 95.2%, especificidad 93.6% ni una evaluación sobre 1,332 imágenes: el repositorio inicial las generaba mediante simulación. Tampoco se afirma exportación TFLite, latencia garantizada o detección confirmada de edema/neovascularización.

## Plan de evaluación con datos reales

Obtener datos etiquetados con permisos de uso y documentación de procedencia. CSV con path, label, patient_id y split. Separar entrenamiento, validación y prueba por paciente; rechazar archivos idénticos entre particiones. Evaluar representatividad por cámara, fuente y condiciones de adquisición, evitando fuga entre conjuntos.

Seleccionar checkpoint por pérdida de validación y evaluar una vez sobre la partición test. Registrar predicciones, cobertura y rechazos. Calcular exactitud y métricas binarias para grados 2+ incluyendo rechazos; para AUC neuronal, identificar el subconjunto aceptado y su posible sesgo. Estudiar intervalos de incertidumbre, calibración y rendimiento externo antes de proponer uso clínico.

## Limitaciones, ética y datos

Las cinco ilustraciones son sintéticas y no representan una cohorte de pacientes. Los umbrales se ajustan a una demostración y no permiten generalizar. La calidad de adquisición requiere evaluación adicional. Un modelo entrenado y su manifiesto no constituyen una certificación clínica.

La app escucha en localhost. No almacena imágenes del usuario automáticamente; conserva hasta 16 análisis en memoria por 20 minutos. Los PDF/JSON descargados contienen los datos introducidos, y su resguardo corresponde al usuario. La clave local se excluye del paquete distribuible. El QR no incluye nombre ni folio.

Si se incorporan participantes humanos o datos sujetos a restricciones, el equipo y asesor determinarán los formularios y revisiones correspondientes con los organizadores. No se presume exención por ausencia de intervención invasiva.

## Conclusión de esta etapa

Se entrega un prototipo de ingeniería local con adquisición, procesamiento, explicación trazable y reportes verificables, junto con entrenamiento y evaluación reproducibles preparados para datos independientes. La generalización y eficacia clínica siguen pendientes de investigación.

## Referencias técnicas

Convocatoria estatal FEMECI Puebla 2026, documento aportado por el equipo. Torchvision: MobileNetV3-Large (docs.pytorch.org/vision/stable/models/generated/torchvision.models.mobilenet_v3_large.html). FastAPI: concurrencia (fastapi.tiangolo.com/async/). Repositorio OculoEdge: github.com/blaster-ops/OculoEdge. American Society of Retina Specialists: guía de retinopatía diabética (pmc.ncbi.nlm.nih.gov/articles/PMC8297841/).
