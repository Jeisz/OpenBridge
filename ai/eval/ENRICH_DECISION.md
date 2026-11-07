# Enriquecimiento del catálogo: elección del modelo

Qué modelo de lenguaje genera las categorías, el resumen en español y los casos de uso de
los repos del catálogo. Reporte completo: [`results/enrich-validacion.md`](results/enrich-validacion.md).

## Decisión

**Gemini 3.5 Flash-Lite**, el mismo modelo principal del asistente. Gratis y reproducible por
cualquier persona del equipo con su propia clave.

## Por qué se compararon otros modelos

El enriquecimiento corre por lotes, sin un usuario esperando: la latencia no limita. Eso
habilita modelos que el asistente descartó por lentos (un modelo local y modelos que razonan).

## Método

- **Prompt escrito con 8 repos de práctica** (descripción vacía, README casi vacío, README muy
  largo, sin descripción…) y congelado antes de comparar.
- **Validación con 16 repos que el prompt no vio:** 8 con categorías escritas a mano como
  referencia y 9 que **no aparecen** como ejemplo en las notas de `categories.json`. Este
  detalle importa: 43 de los 100 repos están nombrados en esos ejemplos, y en ellos el modelo
  puede acertar copiando el ejemplo. Las reglas solo se ponen a prueba con los no nombrados.
- **2 corridas por modelo**, para medir la estabilidad.
- **Criterios fijados antes de ver los resultados:** salidas válidas al primer intento,
  categoría principal correcta en los no nombrados, casos de uso que sean usos principales y
  no características, y estabilidad entre corridas. Regla: si la ventaja de un modelo de pago
  no es clara (2 repos o más), gana el que el equipo puede reproducir sin costo.
- **Revisión:** la hizo un asistente de IA (Claude) con un argumento por repo, apoyado en la
  nota de la categoría y en el README; una persona verificó los argumentos contra esas dos
  fuentes. Como el revisor es de la misma familia que dos de los candidatos, cada veredicto
  tiene que poder comprobarse en el texto.

## Resultados (16 repos × 2 corridas)

| Criterio | Gemini 3.5 Flash-Lite | Claude Haiku 5.5 (razonando) | Claude Sonnet 5.5 | Qwen 3.5 4B (local) |
|---|---|---|---|---|
| Válidas al primer intento | 32/32 | 32/32 | 32/32 | 32/32 |
| Principal correcta, no nombrados (18) | 17 | 16 | 18 | 15 |
| Misma principal en las 2 corridas | 15/16 | 15/16 | 16/16 | 13/16 |
| Casos de uso aceptados / descartados | 82 / 5 | 90 / 2 | 112 / 0 | 71 / 49 |
| Segundos por repo (mediana) | 1,4 | 4,4 | 2,8 | 6,7 |

Sonnet es mejor en todos los criterios, pero por 1 repo en cada uno: por la regla, gana Gemini.

## Descartados

| Modelo | Causa |
| --- | --- |
| Qwen 3.5 4B en Ollama (local) | 33 citas de evidencia que no existen en el README (las detectó la validación) y categorías secundarias sin base. Requiere una ventana de contexto de al menos 16k: con 4k, Ollama recorta el prompt sin avisar |
| Claude Haiku 5.5 (razonando) | Misma calidad que Gemini; de pago |
| Claude Sonnet 5.5 | Mejor en todo, por poco; de pago y solo reproducible con una clave de pago. Es la primera opción si hace falta más calidad: una corrida de 100 repos cuesta alrededor de US$1,5 |

## Hallazgos que cambiaron el diseño

- **Reglas que el modelo no cumple se pasan al código.** Gemini ignoró "sin adjetivos de venta"
  y "cita la frase completa"; ahora el código rechaza una lista de palabras de venta (con un
  reintento) y exige citas de al menos 15 caracteres y 2 palabras.
- **El ruido entre corridas es del mismo tamaño que las diferencias que se querían medir.**
  Con la misma entrada, un repo pasó de 3 casos de uso a 1. Comparar 4.000 contra 8.000
  caracteres de README no dio diferencias distinguibles del ruido: se eligió 8.000 por razonamiento
  (50 de los 100 README pasan de 4.000 caracteres).
