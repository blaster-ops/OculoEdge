# Preparación de OculoEdge para FEMECI Puebla 2026

## Abrir y demostrar

Descomprimir el paquete portable completo y abrir Iniciar_OculoEdge.bat. Comprobar la app con la red deshabilitada antes de trasladarse. Usar localhost y mantener la consola abierta.

1. Seleccionar G0, G1, G2, G3 y G4: son muestras sintéticas identificadas como tales.
2. Explicar la medición observada y su regla experimental, sin afirmar diagnóstico clínico.
3. Cambiar Original / Ben Graham / Evidencia y ajustar opacidad.
4. Cargar una imagen negra: debe producir «Imagen no evaluable» y ningún grado.
5. Generar un PDF, descargar el JSON de verificación y comprobar ambos en la interfaz.
6. Explicar el entrenamiento y la evaluación preparados para un dataset real independiente.

La cámara USB está implementada; su demostración depende del equipo conectado, los permisos y la óptica. Tener las muestras y archivos locales como alternativa de adquisición.

## Preparación del equipo

Según la convocatoria aportada, la jornada de exhibición está prevista para el 30 de octubre de 2026 en UPAEP. El PDF indica cierre de expedientes el 18 de octubre; el portal público consultado el 11 de octubre muestra 25 de octubre. Confirmar la fecha efectiva con los organizadores y atender la fecha más temprana mientras se aclara.

Se requiere asesor institucional, carta de respaldo, identificaciones, formatos F-01 a F-05, protocolo y bitácora. Los formularios especiales se determinan según las actividades reales. No asumir exención automática por ser un estudio no invasivo.

Cartel 90 × 120 cm. Presentación de 15 minutos totales: 8–10 de exposición y 5–7 de preguntas. Participan los tres integrantes. Rúbrica: metodología y diseño 50 puntos; innovación y competencias 25; defensa y bitácora 25. Mínimo 80/100 para aspirar a premios/acreditación; no equivale a precisión de la app.

## Guion sugerido de 8 minutos

- Minuto 0–1: problema de acceso y meta de ingeniería, con fuentes comprobables.
- Minuto 1–3: arquitectura local, controles de entrada y alcance de esta versión.
- Minuto 3–5: demostración con dos grados sintéticos y rechazo de imagen inválida.
- Minuto 5–6: generación y verificación del informe.
- Minuto 6–7: resultados reproducibles y límites del tamaño de muestra.
- Minuto 7–8: entrenamiento/evaluación pendientes con datos reales y siguientes experimentos.

## Respuestas que deben poder defender

¿Es un diagnóstico? No; esta versión produce patrones experimentales de imagen.

¿Utiliza MobileNetV3? El modo neuronal está implementado y probado mediante entrenamiento sintético de integración. La demostración portable usa reglas transparentes porque no hay un checkpoint clínico con evidencia de entrenamiento/validación disponible.

¿Qué significa 5/5? Que los cinco casos sintéticos de integración producen el patrón previsto. No permite estimar sensibilidad, AUC ni seguridad clínica sobre pacientes.

¿El mapa explica el resultado? En reglas, muestra los píxeles usados por la regla seleccionada; en modo neuronal, Grad-CAM calcula activaciones de la misma red que produce la clase.

¿Qué falta para estudiar aplicación clínica? Datos etiquetados y representativos, separación por paciente y fuente, evaluación independiente, estudio de rechazos y calibración, y revisión especializada y de requisitos aplicables al uso previsto.

## Material para llevar

Laptop Windows x64, cargador, carpeta portable descomprimida y copia del ZIP en USB; muestras, PDF actualizado, bitácora, cartel y documentación institucional. No distribuir la clave local de reportes ni datos personales con el código. Registrar las pruebas reales y sus fallos en la bitácora.
