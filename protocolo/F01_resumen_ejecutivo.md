# OculoEdge: resumen ejecutivo para revisión del equipo

FEMECI Puebla 2026 · UTT · Ingenierías / Sistemas Informáticos y Computación. Equipo: José Miguel Tapia Adán, Samuel Gutiérrez Tapia y Oswaldo Yahir Asis Ladino. Asesor: pendiente de identificación y validación institucional.

## Problema y objetivo

Investigar una estación local para procesar imágenes de fondo de ojo, explicar el cálculo y generar resultados trazables en contextos con conectividad limitada.

## Metodología

Aplicación offline con adquisición desde archivo o cámara USB, controles exploratorios de imagen, preprocesamiento Ben Graham, mediciones de píxeles, reglas experimentales transparentes y visualización de sus máscaras. Componente opcional de MobileNetV3 entrenable mediante CSV con particiones por paciente, inferencia local y Grad-CAM coherente con el modelo predictor. PDF del análisis mostrado y registros verificables mediante SHA-256/HMAC local.

## Resultados disponibles

Los cinco casos sintéticos G0–G4 incluidos producen los patrones previstos. La suite de software cubre entradas no evaluables, límites, concurrencia, informes y verificación; además prueba entrenamiento e inferencia neuronal con datos sintéticos de integración. El benchmark guarda predicciones y métricas calculadas desde la ejecución. No hay ROC/AUC para el motor de reglas ni validación clínica sobre pacientes.

## Alcance y limitaciones

Prototipo de investigación sin validación clínica. No diagnostica ni descarta enfermedad. Las muestras sintéticas no sustentan estimaciones clínicas de sensibilidad/especificidad. No se dispone de evaluación reproducible de 1,332 retinografías reales. El siguiente experimento requiere datos reales etiquetados, particiones independientes, análisis de rechazos y revisión especializada.

## Estado documental

Este resumen es contenido del proyecto para trasladar al formato oficial F-01; no sustituye el formulario de inscripción, las firmas ni la validación del asesor.
