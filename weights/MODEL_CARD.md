# Estado de los pesos

oculoedge_calibrated.pth procede de la versión inicial del repositorio. No incluye manifiesto de entrenamiento ni evaluación independiente disponible. No se carga automáticamente ni se incluye en el paquete portable.

El modo neuronal requiere un checkpoint .pth y .json generado por core.train. Ambos deben describir arquitectura, preprocesamiento, SHA-256, clases, historial y procedencia declarada. La coincidencia de hash verifica consistencia del archivo, no calidad clínica ni veracidad externa de la declaración.

La demostración portable utiliza reglas experimentales; no oculta esta condición ni asigna confianza clínica. Véase README.md para entrenar y evaluar con un dataset etiquetado independiente.
