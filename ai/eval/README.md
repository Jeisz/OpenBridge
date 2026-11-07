# Evaluación de la búsqueda

Mide si la búsqueda semántica (`ai/search.py`) encuentra la herramienta correcta
para cada necesidad. El asistente busca **una vez por necesidad** y el modelo de
lenguaje elige entre los primeros resultados: lo que no llega ahí, no se puede
recomendar.

Esta evaluación cubre solo la búsqueda. El flujo completo del asistente se mide
con sus casos de prueba ([`ASSISTANT_CASES.md`](ASSISTANT_CASES.md)). Por qué se
eligieron el modelo de embeddings y el umbral, con su evidencia:
[`SEARCH_DECISION.md`](SEARCH_DECISION.md).

## Estado actual

| | |
|---|---|
| Modelo de embeddings | EmbeddingGemma-300m |
| Texto de cada repo | nombre, resumen de la IA, descripción, topics y casos de uso de la IA (sin categorías) |
| Umbral de "sin evidencia" (`min_score`) | 0,23 |
| Acierto en el catálogo real (hit@3) | 52 de 60 consultas (87 %); con 5 candidatos, 54 (90 %) |
| Golden set | `catalog` v2: 100 consultas, snapshot del 2026-10-29 |

El umbral frena la mitad de los pedidos sin respuesta (20 de 40 pasan). Los que
*suenan* parecido a un repo que no los resuelve (por ejemplo, "comunicación con
clientes" → alertmanager, "inicio de sesión" → vault) pasan, y el freno tiene que
venir del paso que elige entre los candidatos.

Para comparar variantes del texto: `python -m ai.eval.run_search_eval --texto <variante>`
(variantes en `TEXT_VARIANTS`, `ai/search.py`).

## Cómo correrla

Desde la raíz del repo, con el entorno activo:

```bash
python -m ai.eval.run_search_eval                             # catálogo real, modelo por defecto
python -m ai.eval.run_search_eval --golden sample             # 20 repos de ejemplo
AI_EMBEDDING_MODEL=qwen3 python -m ai.eval.run_search_eval    # otro modelo del registro
```

Cada corrida escribe un reporte en `ai/eval/results/`
(`search-catalog-<modelo>.md` o `search-<modelo>.md`). Tarda menos de un minuto
con EmbeddingGemma en CPU.

## Golden sets

Cada golden set declara contra qué catálogo se escribió (`source`), y la
evaluación construye el índice con ese mismo catálogo.

| Nombre | Archivo | Catálogo | Para qué |
|---|---|---|---|
| `catalog` (por defecto) | `search_queries_catalog.json` | Snapshot del catálogo real (`ai/data/catalog/`, 100 repos) | Medir la búsqueda que usa el asistente y calibrar el umbral |
| `catalog-validation` | `search_queries_catalog_validation.json` | Snapshot del catálogo real | Validar con consultas nuevas el texto de búsqueda elegido con `catalog`; no se usa para ajustar |
| `sample` | `search_queries.json` | 20 repos de ejemplo (`ai/data/`) | Repetir la elección del modelo de embeddings |

- Cada consulta tiene sus repos aceptables (`expected`). Una lista vacía
  significa que el catálogo no tiene respuesta: esas consultas sirven para el umbral.
- Las respuestas se escriben **antes** de mirar lo que devuelve la búsqueda. Un
  repo es aceptable solo si su descripción, sus topics o su README muestran lo
  que pide la consulta como propósito principal; cada consulta lo justifica en `note`.
- Las consultas de `catalog` son cortas y en español, como las que escribe el
  asistente. `note` dice su origen: escrita por el paso de entender (las
  variantes terminan en `-v2`), escrita a mano o de la versión 1.
- Si se cambian las respuestas esperadas, se sube `version`: resultados de
  versiones distintas no se comparan.
- `catalog` guarda la fecha del snapshot (`catalog_taken_at`). Si el snapshot se
  renueva, un test falla a propósito hasta revisar las consultas.

## Cómo leer el reporte

| Métrica | Qué responde |
|---|---|
| **hit@3** | ¿Llegó al menos una herramienta correcta al top-3? |
| **MRR@3** | ¿Qué tan arriba? 1 si está primera, 0,5 si segunda, 0,33 si tercera, 0 si no llegó; promedio |
| **recall@3** | ¿Qué parte de *todas* las herramientas correctas llegó al top-3? |
| **hit@5** | Como hit@3, con 5 candidatos por necesidad |

Las consultas sin respuesta no cuentan para estas métricas. Se usan en la
sección **"Umbral"**, que muestra los puntajes del 1.er resultado de cada grupo,
el umbral actual, el que sugiere la regla (`suggest_min_score` en `metrics.py`)
y, para cada uno, qué consultas bloquea o deja pasar. Las consultas con
respuesta que la búsqueda no resuelve se listan como fallos de búsqueda.

## Medir una mejora del texto de los repos

El reporte de EmbeddingGemma es la línea base para medir cualquier cambio en el
texto de los repos (por ejemplo, agregar categorías y un resumen en español):

1. Hacer el cambio sin tocar el golden set ni el snapshot.
2. Correr `python -m ai.eval.run_search_eval`.
3. Ver qué cambió con `git diff ai/eval/results/search-catalog-embeddinggemma-300m.md`:
   el diff muestra, consulta por consulta, qué posición subió o bajó y cómo se
   movió el umbral.

Si cambia el golden set o el snapshot, los números dejan de ser comparables.

## Cuando cambie el catálogo

1. Volver a exportar el snapshot (`python -m ai.scripts.export_catalog_snapshot`).
   El test de la fecha falla hasta revisar el golden set `catalog`.
2. Revisar que las consultas sin respuesta sigan sin respuesta y si hay
   herramientas nuevas válidas para las otras: agregarlas **solo con evidencia**,
   con su `note`, y subir `version`.
3. Actualizar `catalog_taken_at` y correr la evaluación. Si el umbral sugerido
   cambia, actualizar `min_score` en `ai/embeddings.py` y `SEARCH_DECISION.md`.
