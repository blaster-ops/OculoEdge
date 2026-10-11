# Verificación de OculoEdge 2.0

11 de octubre de 2026. Entorno probado: Windows x64, Python 3.13.2, CPU. Rama de trabajo: codex/concurso-funcional.

## Software

La suite ejecutable cubre los cinco patrones sintéticos, entradas no evaluables, límites de archivo y píxeles, controles de origen, snapshots concurrentes, expiración, coherencia del PDF, escapado de campos, verificación de HMAC y rechazo de modificaciones. Un subproceso bloquea conexiones externas y verifica el flujo base sin importar PyTorch.

El componente neuronal se prueba con entrenamiento sintético de una época, selección por pérdida de validación, inferencia del mismo checkpoint, Grad-CAM, rechazo de pesos sin manifiesto/hash y métricas de la partición sintética de prueba. Estas pruebas verifican integración, no rendimiento clínico.

Suite de desarrollo: 28 pruebas aprobadas. Arranque `run.py --check`: aprobado. Sintaxis JavaScript `node --check static/app.js`: aprobada.

## Interfaz y documentos

Verificados en navegador local: selección de muestras, resultado y evidencia, cambios de vista y opacidad, descarga de PDF y registro JSON, verificación conjunta del PDF/JSON, rechazo de registro alterado, carga de imagen negra y limpieza de sesión. Se inspeccionó el diseño de pantalla estrecha y de escritorio. La captura física USB no se ha certificado: requiere cámara y óptica del equipo.

Los PDF del protocolo (3 páginas), resumen (1) y defensa (2) se regeneraron desde el contenido vigente. Se renderizaron todas sus páginas y se revisó su legibilidad. También se inspeccionó un informe exportado desde la interfaz.

El benchmark del repositorio registra cinco casos sintéticos y cinco patrones esperados. Las métricas se calculan desde las predicciones. No se calcula AUC para las reglas. Los resultados y la latencia medida están en benchmarks/metrics_summary.json; no equivalen a validación sobre pacientes.

## Paquete portable

Paquete Windows x64 construido con Python y 31 distribuciones del modo base. Sus rutas de importación están aisladas mediante python313._pth; no usa el Python registrado en el sistema ni PYTHONPATH.

Pruebas del paquete: 24 aprobadas; cuatro pruebas neuronales omitidas porque PyTorch no se incluye. Arranque propio `runtime/python.exe run.py --check`: aprobado. El servidor en localhost y la interfaz se comprobaron utilizando el Python del paquete.

El ZIP se descomprimió a una ruta diferente con espacios. Se comprobó que todas las rutas de importación estuvieran dentro de esa copia; análisis G4, generación de PDF, autenticación del registro y preflight pasaron con conexiones externas bloqueadas. No se incluyeron claves locales, datos privados, pesos originales ni cachés en el ZIP. El manifiesto registra hashes SHA-256 de los archivos distribuidos.

## Límites de lo demostrado

No hay datos clínicos etiquetados disponibles fuera del repositorio, según confirmó el equipo. No se entrega un clasificador clínicamente validado. No se certifica que cualquier fotografía sea retiniana o que pasar los controles básicos garantice calidad diagnóstica. No se ha probado esta versión en Linux ni en otro equipo Windows físico.

La documentación preparada es contenido del proyecto para revisión; el asesor, la inscripción, los formularios oficiales y las firmas institucionales corresponden al equipo. No se han publicado los cambios en GitHub ni ejecutado el workflow remoto.
