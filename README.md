# OculoEdge 2.0

Estación local de investigación para procesamiento de retinografías y demostración de ingeniería. Universidad Tecnológica de Tehuacán · FEMECI Puebla 2026.

## Abrir la versión portable en Windows

1. Descomprimir `OculoEdge_2_0_Concurso.zip` por completo en una carpeta local.
2. Abrir `Iniciar_OculoEdge.bat` dentro de esa carpeta.
3. Se abrirá `http://127.0.0.1:8050` en el navegador. Mantener la consola abierta; Ctrl+C detiene el servidor.

El paquete incluye Python para Windows x64 y todas las dependencias del modo de demostración. No necesita internet, Python instalado, administrador, GPU ni servicios en la nube. La cámara depende de permisos del navegador y del dispositivo físico; una cámara normal necesita óptica apropiada para adquirir fondo de ojo.

## Qué está implementado

- Interfaz con recursos locales, compatible con escritorio y pantallas pequeñas.
- Carga JPG/PNG/WebP y captura desde cámara USB con selección de dispositivo.
- Límites de 12 MB y 20 MP, corrección de orientación EXIF y controles de exposición, detalle, resolución y color.
- Resultado «no evaluable» para entradas que no pasan los controles, sin grado ni confianza artificial.
- Preprocesamiento Ben Graham y mediciones exploratorias con reglas transparentes.
- Cinco muestras explícitamente sintéticas G0–G4 para demostración de integración.
- Máscara de las regiones utilizadas por las reglas, con opacidad interactiva, vista original y filtro.
- PDF del mismo análisis mostrado, JSON de verificación y exportación del análisis.
- SHA-256 y HMAC-SHA256 para verificar localmente el registro y el PDF.
- Retención limitada: hasta 16 análisis en memoria por 20 minutos; sin almacenamiento automático de imágenes de usuarios.
- Entrenamiento, manifiesto de checkpoint, inferencia neuronal y Grad-CAM opcionales.
- Evaluación calculada a partir de predicciones, exportación por imagen, detección de fuga por paciente y métricas con rechazos incluidos.

## Alcance científico

La versión portable usa **reglas experimentales de imagen**, no un modelo clínicamente validado. Los umbrales son de demostración y no implementan los criterios clínicos ICDR. No se emiten decisiones de tratamiento ni se descarta enfermedad. Las mediciones no equivalen a microaneurismas, edema o neovascularización confirmados.

La confianza clínica se muestra como no disponible. Los porcentajes de la red opcional son softmax sin calibración clínica. Los controles de adquisición no garantizan que una imagen sea retiniana ni que tenga calidad diagnóstica.

El repositorio inicial incluía cifras simuladas atribuidas a MESSIDOR-2/EyePACS. Se reemplazaron con resultados reproducibles de las cinco muestras sintéticas. No hay evidencia disponible de validación con 1,332 imágenes reales. No se distribuye un checkpoint neuronal como entrenado clínicamente: el antiguo `weights/oculoedge_calibrated.pth` se conserva en Git para trazabilidad, no se carga automáticamente y carece del manifiesto requerido.

## Instalar desde el código

Entorno probado: Windows x64, Python 3.13. La ejecución base también está preparada para Linux con Python 3.11–3.13; requiere comprobar instalación en ese sistema.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe run.py --check
.\.venv\Scripts\python.exe run.py
```

También puede abrir `Instalar_OculoEdge.bat` y luego `Iniciar_OculoEdge.bat`. La instalación desde código necesita internet; la versión portable incluye los recursos necesarios para ejecutar sin red. Si el puerto 8050 pertenece a otra aplicación, use `run.py --port 8051`. No se terminan procesos ajenos.

Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
./iniciar_oculoedge.sh
```

## Pruebas y evaluación de demostración

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m benchmarks.evaluate_metrics
```

El benchmark genera `benchmarks/metrics_summary.json`, `predictions.json`, matriz de confusión y una figura que identifica ROC como no disponible para el motor de reglas. Cinco aciertos sintéticos prueban funcionamiento de esos casos; no prueban precisión clínica ni generalización.

## Entrenar un modelo con datos independientes

Instalar el componente neuronal en el entorno de desarrollo, con internet durante esa preparación:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-ml.txt
```

Crear un CSV UTF-8 con rutas relativas al CSV y columnas:

```csv
path,label,patient_id,split
images/ejemplo0.jpg,0,P001,train
images/ejemplo1.jpg,1,P002,val
images/ejemplo2.jpg,2,P003,test
```

Este fragmento ilustra el formato, no es un dataset suficiente. Se requieren las cinco clases en entrenamiento y una validación separada; ningún paciente ni archivo idéntico puede aparecer en distintas particiones. Usar identificadores desidentificados y conjuntos representativos autorizados. Separar también fuentes y equipos para estudiar generalización.

```powershell
.\.venv\Scripts\python.exe -m core.train --csv data/private/dataset.csv --epochs 15 --data-kind real
.\.venv\Scripts\python.exe -m benchmarks.evaluate_metrics --csv data/private/dataset.csv --weights weights/oculoedge_best.pth --data-kind real --output output/evaluation
$env:OCULOEDGE_MODEL = (Resolve-Path weights/oculoedge_best.pth).Path
.\.venv\Scripts\python.exe run.py
```

El entrenamiento no descarga pesos; `--init` permite inicializar desde un checkpoint local con arquitectura compatible. Guarda los pesos y un manifiesto JSON con SHA-256, particiones, historial y configuración. Selecciona el checkpoint por pérdida de validación, no de entrenamiento. La app comprueba arquitectura, preprocesamiento y hash, y Grad-CAM usa exactamente el modelo que produce la clase. Tener un manifiesto de entrenamiento no constituye validación clínica.

## Verificar informes

1. Descargar PDF y registro JSON desde el mismo análisis.
2. En «Verificar un informe», cargar el JSON y el PDF correspondiente.
3. La app valida los HMAC con la clave local y compara SHA-256 del PDF.

El QR contiene hashes y autenticador del registro, sin nombre ni folio. Los datos personales sí están en el PDF y el JSON exportados. La clave se crea en `.local/report.key`; no debe compartirse ni incluirse en el ZIP. Conservarla permite verificar informes anteriores. Otro equipo con otra clave no puede verificar su autenticidad. Esto es autenticación local mediante HMAC, no firma pública ni certificación institucional.

## Paquete y desarrollo

```powershell
.\.venv\Scripts\python.exe tools/build_portable.py
```

El constructor usa el Python Windows y las dependencias ya instaladas, genera un manifiesto de archivos y un ZIP en `dist/`. La versión portable base no incluye PyTorch; las pruebas neuronales se ejecutan en el entorno de desarrollo. Los datos privados, las claves y los pesos sin procedencia se excluyen del paquete.

Equipo: José Miguel Tapia Adán, Samuel Gutiérrez Tapia y Oswaldo Yahir Asis Ladino. Licencia MIT para el código propio; se incluyen licencias de terceros en el paquete. Asesor institucional: pendiente de identificación y validación por el equipo UTT.
