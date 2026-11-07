# Ideas de integración: método, resultados y límites

Cómo se generan con el LLM las ideas de integración de la ficha (contrato `IntegrationIdea`),
cómo se validaron y qué no resuelven. Código: `ai/ideas.py`, `ai/scripts/generate_ideas.py`.
Medición: `ai/eval/evaluate_ideas.py` y las referencias `ideas_reference*.json`.

## Qué es una idea

Una forma de conectar la herramienta a una aplicación, de uno de cuatro tipos: `sdk`
(librería o cliente que la aplicación instala o importa), `rest_api` (API HTTP que la
herramienta expone), `docker` (imagen publicada) o `webhook` (avisos HTTP hacia la
aplicación). De 0 a 3 por herramienta, como máximo una por tipo. Si ningún tipo encaja con
evidencia del README, la herramienta queda **sin ideas**: es una respuesta válida.

## Qué escribe el modelo y qué pone el código

| Campo | Lo escribe | Cómo se controla |
|---|---|---|
| Tipo, título, resumen, dificultad, dependencias, disparadores | El modelo | Reintento si hay errores de forma (más de 3 ideas, texto dañado, palabras de venta, largo) |
| Cita de evidencia | El modelo | Tiene que estar en el texto que vio el modelo; si no, la idea se descarta |
| Stack compatible | El modelo | Solo nombres que aparecen en la entrada; si no queda ninguno, la idea se descarta |
| Snippet y su lenguaje | El código | El modelo elige un bloque por su número; se copia del README original (con sus URLs). Sin marca de lenguaje → `"text"`; más de 15 líneas → sin snippet |
| Enlace a la documentación | El código | Sección del README donde está la cita (ancla de GitHub); si no hay título, el sitio del proyecto; si no, el repo |
| `id`, orden, `generated_by`, `reviewed_at`, `based_on_hash` | El código | `llm-<github_id>-<n>`, de menor a mayor dificultad; `llm`; `null` (sin revisar); huella de la entrada |

El modelo ve la descripción, los topics y el README limpio (sin HTML ni URLs en la prosa),
recortado a 8.000 caracteres sin partir un bloque de código. Un repo archivado o con README
casi vacío no se pide al modelo.

## Método

- **Prompt escrito con 8 repos de práctica** y ajustado en 4 vueltas, siempre con reglas
  generales, nunca con casos puntuales: una consola interactiva no es una integración, `sdk`
  nunca es "low" (usar una librería requiere código propio), sin instaladores ni versiones en
  el stack, una idea por tipo, un título o un índice no son evidencia.
- **Referencia escrita antes de escribir el prompt** para 15 repos que el prompt no vio
  (`ideas_reference.json`): ideas requeridas con su cita, admisibles y prohibidas (trampas),
  y repos que deben quedar sin ideas. Criterios fijados antes de correr, dentro del mismo archivo.
- **2 corridas por versión** para medir la estabilidad. Modelo: Gemini 3.5 Flash-Lite, un solo
  proveedor por corrida (sin respaldo automático), para que todo salga del modelo validado.

## Resultados (Gemini 3.5 Flash-Lite, 2 corridas)

| Medición | Requeridas | Sin ideas cuando correspondía | Prohibidas | Estables |
|---|---|---|---|---|
| Versión 4 del prompt, 15 repos sin ver (referencia v1) | 13/16 y 13/16 ✅ | 3/3 ✅ | **1 y 1 ❌** | 12/15 ✅ |
| Versión 5, 3 frameworks sin ver (`ideas_reference_frameworks.json`) | **1/3 y 1/3 ❌** | — | 0 ✅ | 3/3 ✅ |
| Versión 5, los mismos 15 (ya vistos; referencia v2) | 14/15 y 14/15 ✅ | 3/3 ✅ | 0 ✅ | 12/15 ✅ |

La versión 4 es la medición sin sesgo. Su error fue el mismo en las dos corridas: FastAPI
como `rest_api` ("framework para construir APIs" leído como "expone una API"). La versión 5
agrega una regla general (un framework para construir tu propia API es `sdk`), se comprobó con
3 frameworks que el prompt no había visto y se volvieron a correr los 15 solo para ver que
nada empeoraba. Resultado: ninguna idea prohibida, pero 2 de los 3 frameworks nuevos quedan
sin ideas. Se eligió así: una ficha sin ideas es menos dañina que una que dice algo falso.

La referencia v2 corrige dos errores de la v1 antes de medir la versión 5: traefik expone una
API REST ("Exposes a Rest API", que la v1 no vio) y pgvector es una extensión de PostgreSQL a
la que ningún tipo le encaja del todo (`sdk` pasa de requerida a admisible).

## Corrida completa (100 repos, versión 5)

40 repos con ideas y 60 sin ideas (uno sin llamar al modelo). 46 ideas: 34 `sdk`, 7 `docker`,
5 `rest_api`, 0 `webhook`; 20 con snippet. El código descartó 5 (cita corta 2, tipo repetido
2, stack sin respaldo 1). Unos 217 mil tokens de entrada y 9 mil de salida en el nivel
gratuito de Gemini.

Sin ideas, por categoría principal:

| Categoría | Sin ideas |
|---|---|
| dev-tools | 25 de 28 |
| infrastructure | 12 de 16 |
| frontend | 9 de 10 |
| data-processing | 4 de 10 |
| backend | 4 de 7 |
| observability | 2 de 5 |
| search | 2 de 2 |
| database | 1 de 6 |
| automation | 1 de 1 |
| ai, messaging, auth, cache | 0 |

La mayoría de las herramientas sin ideas no se conectan a una aplicación: se usan para
construirla (frameworks) o para trabajar en ella (linters, tests, gestores de paquetes,
compiladores). Con cuatro tipos y sin inventar, lo correcto es no dar ideas. La ficha de esas
herramientas conserva su resumen y sus casos de uso.

## Límites conocidos

- **Frameworks inconsistentes:** react recibe un `sdk`; vue, svelte, angular, flask y
  starlette quedan sin ideas.
- **Citas parafraseadas:** el modelo a veces cambia palabras de la cita y el código la
  descarta (duckdb en una de cada dos corridas). Se pierde la idea, no se muestra una falsa.
- **La cita prueba que el texto existe, no que respalde la idea.** Lo cubre la revisión.
- **El snippet puede no corresponder a la idea** (en una corrida, la idea de enviar trazas a
  Jaeger llevaba el bloque del `docker run`).
- **Sin webhooks:** en el texto que ve el modelo, ningún README explica cómo recibirlos.
- **Anclas en README que no son Markdown:** se verificó que funcionan en uno en
  reStructuredText (celery); si una no coincide, el enlace abre el README desde arriba.
- **Sin revisión humana del catálogo completo:** todas las ideas quedan con `reviewed_at`
  nulo; la ficha decide cómo mostrar "sin revisar".

## Cómo regenerar y medir

    python -m ai.scripts.generate_ideas                    # los 100 repos → ai/data/catalog/ideas.json
    python -m ai.scripts.generate_ideas --repos A/B C/D --out salida.json
    python -m ai.eval.evaluate_ideas CORRIDA1.json CORRIDA2.json --out reporte.md

Si cambian las reglas del prompt, sube `PROMPT_VERSION` en `ai/ideas.py`: el lote regenera
todo. Para medir una versión nueva sin sesgo hacen falta repos que el prompt no haya visto.
