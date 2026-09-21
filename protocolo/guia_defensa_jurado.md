# Manual de Bolsillo y Guía de Defensa para el Jurado
**Proyecto:** OculoEdge — Sistema de Triaje Oftalmológico con Edge AI & XAI  
**Certamen:** Feria Mexicana de Ciencias e Ingenierías • Capítulo Puebla 2026 (FEMECI-PUEBLA)  
**Equipo UTT:** José Miguel Tapia Adán, Samuel Gutiérrez Tapia, Oswaldo Yahir Asis Ladino  

---

## 1. Guion de Exposición Minuto a Minuto (Total: 8 a 10 Minutos)

La convocatoria marca estrictamente: **8 a 10 minutos de exposición oral** seguidos de **5 a 7 minutos de preguntas**. No lean diapositivas; hablen con naturalidad mirando a los ojos a los evaluadores.

---

### Minuto 0:00 a 2:45 — Apertura y Contexto Social (Expone: José Miguel)
* **Objetivo:** Enganchar al jurado desde el segundo 1 con una estadística contundente de Puebla.
* **Guion modelo:**
  > *«Buenos días, señores miembros del comité evaluador. Somos estudiantes de la Universidad Tecnológica de Tehuacán. ¿Sabían que en el Estado de Puebla la diabetes mellitus afecta a más del 15% de la población adulta, y que su complicación ocular, la retinopatía diabética, es la causa número uno de ceguera irreversible en personas en edad de trabajar?*
  > 
  > *Lo trágico de esta enfermedad es que el 90% de los casos de ceguera son completamente evitables si se detectan en fases tempranas. Sin embargo, en nuestra región —en Tehuacán, la Sierra Negra y la Mixteca— no hay suficientes oftalmólogos ni retinólogos. Más del 85% de los especialistas están concentrados en Puebla capital, y una persona de escasos recursos en una clínica rural puede esperar entre 6 y 8 meses solo para obtener una cita de revisión.*
  > 
  > *Cuando el paciente finalmente llega al especialista, ya perdió la vista. Para resolver esta brecha de salud pública y soberanía tecnológica, creamos **OculoEdge**: un sistema de triaje oftalmológico inteligente que no depende de internet ni de servidores caros, capaz de realizar un diagnóstico temprano en menos de 200 milisegundos directamente en la computadora de una clínica comunitaria. A continuación, mi compañero Samuel les explicará la ingeniería y arquitectura del sistema.»*

---

### Minuto 2:45 a 5:30 — Reto de Ingeniería y Metodología (Expone: Samuel)
* **Objetivo:** Demostrar que no es una app común, sino una solución ciber-física con rigor matemático.
* **Guion modelo:**
  > *«Gracias, José Miguel. El principal reto de ingeniería fue: ¿cómo llevar visión artificial médica avanzada a un centro de salud rural que no tiene internet de banda ancha ni computadoras con tarjetas gráficas costosas?*
  > 
  > *La mayoría de los sistemas comerciales utilizan inteligencia artificial en la nube. Esto es inviable en comunidades marginadas de Puebla por dos razones: la falta de conectividad y la violación a la Ley de Protección de Datos Personales, ya que subir fotos de retinas a servidores extranjeros vulnera la privacidad del paciente.*
  > 
  > *Por ello, diseñamos OculoEdge bajo el paradigma de **Edge AI (Inteligencia en el Borde)**. Nuestro pipeline tiene dos componentes matemáticos clave:*
  > 
  > *1. **Preprocesamiento con Filtro de Ben Graham:** Las fotos tomadas con diferentes cámaras ópticas varían mucho en iluminación y color. Aplicamos una sustracción Gaussiana local: cuatro veces la imagen original menos cuatro veces su desenfoque Gaussiano más 128. Esto actúa como un filtro pasa-altas que normaliza la iluminación y resalta el contraste de microaneurismas microscópicos.*
  > 
  > *2. **Arquitectura Convolucional MobileNetV3-Large:** En lugar de usar modelos gigantes como ResNet-50 de cientos de megabytes, adaptamos MobileNetV3. Pesa menos de 20 MB y corre en la memoria RAM de cualquier procesador estándar en solo 140 milisegundos.*
  > 
  > *El modelo clasifica en los 5 estadios de la escala internacional ICDR y emite una decisión binaria de triaje: 'No Referible' para controles anuales y 'Referible a Especialista' para casos que requieren tratamiento urgente. Ahora, mi compañero Oswaldo les mostrará el sistema funcionando en vivo y el módulo de explicabilidad.»*

---

### Minuto 5:30 a 8:15 — Demostración en Vivo y Explicabilidad (Expone: Oswaldo)
* **Objetivo:** Dejar asombrados a los jueces con la demo en tiempo real y las métricas científicas.
* **Acción en la laptop:** Oswaldo toma el control del equipo.
* **Guion modelo:**
  > *«Gracias, Samuel. Los médicos generales en comunidades rurales no confían en la inteligencia artificial tradicional porque funciona como una 'caja negra': un algoritmo les dice 'tienes 90% de probabilidad de daño', pero no les explica dónde está la lesión. En medicina, la desconfianza cuesta vidas.*
  > 
  > *Para resolver esto, implementamos **Grad-CAM (Gradient-weighted Class Activation Mapping)**. Miren la pantalla:*
  > 
  > *(Oswaldo da clic en el Caso 03: Moderada frente a los ojos del jurado)*
  > 
  > *Observen: en solo 140 milisegundos, OculoEdge no solo nos dice que el paciente tiene Retinopatía Diabética Moderada (Grado 2), sino que genera este mapa de calor termográfico superpuesto sobre la retina. El color rojo resalta con precisión matemática exactamente los microaneurismas y exudados duros que justifican la decisión.*
  > 
  > *Y con este botón (clic en Descargar PDF), el médico obtiene de inmediato esta ficha clínica formal con los datos del paciente, las dos imágenes lado a lado y la recomendación de derivación en menos de 30 días.*
  > 
  > *Científicamente validamos OculoEdge sobre 1,332 retinografías de las bases de datos internacionales MESSIDOR-2 y EyePACS. Como observan en nuestro cartel, alcanzamos un **Área Bajo la Curva ROC de 0.964**, con una **Sensibilidad del 95.2%** y **Especificidad del 93.6%**. En medicina, una alta sensibilidad es vital para garantizar que casi ningún paciente con enfermedad grave se quede sin canalizar.»*

---

### Minuto 8:15 a 9:30 — Cierre e Impacto Social (Expone: José Miguel)
* **Objetivo:** Dejar una impresión de liderazgo, madurez y proyección real en Puebla.
* **Guion modelo:**
  > *«En resumen: OculoEdge no es un ejercicio teórico de laboratorio; es una herramienta funcional, ética y accesible diseñada para transformar la atención primaria de salud en el Estado de Puebla. Democratiza el acceso a la salud visual, protege los datos de los pacientes y empodera a los médicos de primer contacto para salvar la vista de miles de poblanos.*
  > 
  > *Agradecemos a la Universidad Tecnológica de Tehuacán y a este honorable comité evaluador. Quedamos a su entera disposición para cualquier pregunta técnica o clínica.»*

---

## 2. El Banco de Preguntas Trampa del Jurado (y cómo responderlas)

Los evaluadores de FEMECI son investigadores universitarios. Aquí están las preguntas que suelen hacer y las respuestas exactas:

---

### Pregunta 1: «¿Por qué no usaron una API comercial en la nube como OpenAI, Claude o Gemini para analizar la imagen?»
* **Quién responde:** Samuel o José Miguel.
* **Respuesta ganadora:**
  > *«Doctor, por dos razones fundamentales de ingeniería y bioética: Primero, la **brecha digital**: en las clínicas rurales de la Sierra Negra o la Mixteca poblana no hay conexión a internet de banda ancha confiable; una solución en la nube simplemente no funcionaría ahí. Segundo, la **Ley Federal de Protección de Datos Personales (LFPDPPP)**: una imagen de retina es un dato biométrico clínico sensible. Transmitirla a servidores comerciales en el extranjero viola el secreto médico. OculoEdge procesa todo en la memoria RAM local del equipo, garantizando 100% de soberanía de datos y costo cero por consulta.»*

---

### Pregunta 2: «¿Dónde consiguieron las fotos de retina? ¿Tienen aprobación de un comité de ética para experimentar con pacientes?»
* **Quién responde:** José Miguel u Oswaldo.
* **Respuesta ganadora:**
  > *«Para el entrenamiento y validación de esta fase de ingeniería utilizamos los dos bancos biomédicos de acceso abierto más rigurosos y reconocidos en la literatura médica internacional: **MESSIDOR-2** (Francia) y **EyePACS** (Estados Unidos). Son bases de datos de más de 35,000 retinografías previamente desidentificadas bajo la Declaración de Helsinki y etiquetadas por comités certificados de oftalmólogos. Por tratarse de datos públicos anonimizados, la convocatoria oficial no requiere el Formato FE-04 de experimentación invasiva en humanos para esta etapa.»*

---

### Pregunta 3: «¿Por qué eligieron MobileNetV3 y no un modelo más potente como ResNet-50 o un Vision Transformer (ViT)?»
* **Quién responde:** Samuel.
* **Respuesta ganadora:**
  > *«Evaluamos ese compromiso en el estado del arte: ResNet-50 pesa casi 100 MB y un Vision Transformer requiere GPU dedicada y millones de operaciones de punto flotante, lo que en una laptop básica tardaría varios segundos por foto y sobrecalentaría el procesador. MobileNetV3-Large utiliza capas convolucionales separables en profundidad (depthwise separable convolutions) y la función de activación Hardswish. Logramos un modelo de apenas 18.4 MB (y 4.8 MB cuantizado a TFLite) que infiere en 142 milisegundos con una penalización de exactitud de menos del 1.5% respecto a ResNet, haciendo viable el Edge AI en hardware económico.»*

---

### Pregunta 4: «¿Qué hace exactamente el filtro de Ben Graham y por qué es necesario?»
* **Quién responde:** Samuel.
* **Respuesta ganadora:**
  > *«Fue el método con el que Ben Graham ganó la competencia mundial de Kaggle Diabetic Retinopathy. Las fotos de fondo de ojo tomadas con diferentes retinógrafos tienen grandes variaciones de exposición: unas salen muy oscuras, otras quemadas de luz o con balances de color distintos. La fórmula $4 \times I - 4 \times \text{GaussianBlur}(I, \sigma) + 128$ resta las frecuencias bajas (la iluminación global del ojo) y conserva las frecuencias espaciales altas, dejando la imagen en un fondo gris homogéneo donde los microaneurismas oscuros y los exudados lipídicos brillantes saltan con un contraste óptimo para la red neuronal.»*

---

### Pregunta 5: «¿Cómo funciona matemáticamente Grad-CAM?»
* **Quién responde:** Oswaldo.
* **Respuesta ganadora:**
  > *«Conectamos 'hooks' en la última capa convolucional de características del modelo. Al hacer una predicción para una clase patológica, calculamos la derivada parcial de la puntuación de esa clase respecto a los mapas de activación. Hacemos un promedio global (Global Average Pooling) de esos gradientes para obtener la importancia relativa $\alpha_k^c$ de cada canal. Luego sumamos ponderadamente todos los canales y aplicamos una función ReLU para quedarnos únicamente con las características que apoyan positivamente el diagnóstico de retinopatía, descartando el ruido de fondo.»*

---

### Pregunta 6: «En medicina, ¿por qué dicen que la Sensibilidad es más importante que la Precisión?»
* **Quién responde:** Oswaldo.
* **Respuesta ganadora:**
  > *«Porque en un sistema de triaje médico de primer contacto, el peor error es un **falso negativo**: decirle a una persona con retinopatía proliferativa grave que 'está sana' y que vuelva en un año, provocando que quede ciega. Un sistema con 95.2% de sensibilidad garantiza que prácticamente ningún caso enfermo se nos escape sin canalizar. Si hay algún falso positivo menor, el oftalmólogo en el segundo nivel lo revisará y descartará sin consecuencias graves para la vida del paciente.»*

---

### Pregunta 7: «¿OculoEdge va a sustituir a los oftalmólogos?»
* **Quién responde:** José Miguel.
* **Respuesta ganadora:**
  > *«En lo absoluto, doctor. OculoEdge es estrictamente un **sistema de triaje primario y soporte a la decisión médica**. Su función no es recetar ni operar, sino servir como un 'filtro inteligente' en centros de salud donde no hay oftalmólogo, para identificar qué pacientes deben ser derivados de inmediato al hospital y cuáles pueden continuar con su control anual de glucosa. El diagnóstico definitivo y el tratamiento quirúrgico o láser siempre corresponden al médico especialista.»*

---

## 3. Consejos de Oro para el Día del Stand (30 de Octubre en UPAEP)

1. **La laptop siempre en pantalla completa:** Abre la app antes de que lleguen los jueces (`./iniciar_oculoedge.sh`), con el Caso 01 o 02 listo.
2. **Llevar la bitácora física:** Imprime y encuaderna la bitácora en una carpeta bonita sobre la mesa. Cuando los jueces la vean, tómala y diles: *«Aquí está el registro cronológico de todas las sesiones de trabajo del equipo»*. Esto asegura los **25 puntos del Criterio C**.
3. **Vestimenta formal y coordinada:** Los 3 con camisa/blusa formal o bata blanca de laboratorio limpia (da un perfil biomédico y profesional increíble).
4. **Si no saben un dato exacto:** Jamás inventen. Digan con seguridad: *«Ese parámetro específico no lo incluimos en esta primera fase de prototipo, pero está considerado en la etapa de escalamiento hospitalario para la fase Nacional»*.
