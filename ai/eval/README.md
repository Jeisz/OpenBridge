# Evaluación de la búsqueda

Mide si la búsqueda semántica (`ai/search.py`) encuentra la herramienta
correcta para una necesidad, y con qué modelo de embeddings y umbral conviene
trabajar. Los números se generan con un solo comando; este documento los resume.

## Qué se mide

El asistente arma un stack buscando **una vez por necesidad** ("login con
Google", "cobrar suscripciones") y el LLM elige entre los 3 primeros
resultados. Lo que el LLM no recibe, no lo puede recomendar. Por eso se mide si
la herramienta correcta llega al top-3 de cada búsqueda.

Esta evaluación cubre **solo la búsqueda**. La calidad del stack completo
(descomponer la descripción del negocio, elegir y conectar) se mide aparte,
con los casos de prueba del asistente ([`ASSISTANT_CASES.md`](ASSISTANT_CASES.md)).

## Dos golden sets

Cada golden set declara contra qué catálogo se escribió (`source`), y la
evaluación construye el índice con ese mismo catálogo.

| Nombre | Archivo | Catálogo | Para qué |
|---|---|---|---|
| `catalog` (por defecto) | `search_queries_catalog.json` | Snapshot del catálogo real (`ai/data/catalog/`, 100 repos) | Medir la búsqueda que usa el asistente y calibrar el umbral |
| `sample` | `search_queries.json` | 20 repos de ejemplo (`ai/data/`), con categorías puestas a mano | Elegir el modelo de embeddings; se conserva para poder repetir esa comparación |

El golden set `catalog` guarda la fecha del snapshot (`catalog_taken_at`). Si
el snapshot se renueva, un test falla a propósito hasta revisar las consultas.

## Cómo correrla

Desde la raíz del repo, con el entorno activo:

```bash
python -m ai.eval.run_search_eval                             # catálogo real, modelo por defecto
python -m ai.eval.run_search_eval --golden sample             # 20 repos de ejemplo
AI_EMBEDDING_MODEL=qwen3 python -m ai.eval.run_search_eval    # otro modelo del registro
```

Cada corrida escribe un reporte en `ai/eval/results/`:
`search-catalog-<modelo>.md` o `search-<modelo>.md`, con métricas, top-3 de
cada consulta, pares y umbral. Tarda menos de un minuto en CPU.

## Cómo se escriben las consultas

- **`catalog`:** consultas cortas en español (3 a 8 palabras, sin nombres de
  productos), como las que escribe el asistente al separar el pedido en
  necesidades. Parten de las necesidades de los casos de prueba del asistente.
- **`sample`:** frases de usuario más largas.
- Las respuestas se escriben **antes** de mirar lo que devuelve la búsqueda.
  Un repo es aceptable solo si su descripción, sus topics o su README muestran
  esa necesidad como propósito principal; cada consulta lo justifica en `note`.
- Las consultas sin respuesta (`expected: []`) incluyen algunas que "casi"
  encajan: son las que deciden dónde va el umbral.
- Si se cambian las respuestas esperadas, se sube `version`: resultados de
  versiones distintas no se comparan.

## Métricas

| Métrica | Qué responde |
|---|---|
| **hit@3** | ¿Llegó al menos una herramienta correcta al top-3? |
| **MRR@3** | ¿Qué tan arriba? 1 si está primera, 0,5 si segunda, 0,33 si tercera, 0 si no llegó; promedio |
| **recall@3** | ¿Qué parte de *todas* las herramientas correctas llegó al top-3? Importa para que el LLM pueda comparar opciones |
| **Umbral** | Con el puntaje del 1.er resultado: ¿cuántas necesidades válidas se bloquearían y cuántas sin respuesta pasarían? |

Las consultas sin respuesta no cuentan para hit@3, MRR ni recall.

## Resultados en el catálogo real

Golden set `catalog` v1 (6 con respuesta, 6 sin respuesta) · snapshot del
2026-10-29 · 100 repos · EmbeddingGemma-300m · CPU.

| | Catálogo real (100 repos, sin categorías) | Datos de ejemplo (20 repos, con categorías) |
|---|---|---|
| hit@3 | 4/6 | 14/14 |
| MRR@3 | 0,39 | 0,79 |
| recall@3 | 47 % | 93 % |
| 1.er resultado, consultas con respuesta | 0,146 – 0,415 | 0,201 – 0,549 |
| 1.er resultado, consultas sin respuesta | 0,121 – 0,194 | 0,126 – 0,215 |
| Vectores del catálogo | 6,9 s | 4,0 s |
| Consulta | 0,05 s | 0,05 s |

La búsqueda acierta mucho menos en el catálogo real. Las causas están en el
texto de los repos, no en el tamaño del catálogo:

- **"Procesar eventos en tiempo real":** redis sale 1.º y flink 14.º. La
  descripción de flink en el catálogo es solo "Apache Flink"; redis dice
  "real-time" en su descripción y sus topics.
- **"Tableros de entregas por ciudad":** grafana sale 9.º aunque tiene el topic
  `dashboard`. "Tableros" no se acerca lo suficiente a "dashboard", y las
  palabras del negocio ("entregas", "ciudad") desvían la búsqueda.
- **"Recibir un flujo continuo de eventos":** acierta (kafka 2.º), pero flux2
  sale 1.º por el parecido entre "flujo" y "flux".
- **"Asistente que responde con documentos propios":** acierta con llama_index;
  langchain queda 15.º con una descripción general ("The agent engineering platform").

Con 5 candidatos por necesidad en vez de 3, los aciertos suben a 5/6.

Detalle por consulta en `results/search-catalog-embeddinggemma-300m.md`.

## Decisiones

**Modelo: EmbeddingGemma-300m** (por defecto en `ai/embeddings.py`), elegido
con el golden set `sample`:

| | EmbeddingGemma-300m | Qwen3-Embedding-0.6B |
|---|---|---|
| hit@3 | 14/14 | 14/14 |
| MRR@3 | 0,83 | 0,92 |
| recall@3 | 93 % | 89 % |
| 1.er resultado, consultas con respuesta | 0,207 – 0,558 | 0,485 – 0,687 |
| 1.er resultado, consultas sin respuesta | 0,117 – 0,208 | 0,439 – 0,554 |
| Vectores de 20 repos | 4–5,5 s | 11–15 s |
| Consulta | 0,06–0,09 s | 0,20–0,69 s |
| RAM aproximada | ~1,2 GB (estimada por el tamaño de los pesos) | ~2,4 GB |
| Instalación | Cuenta de Hugging Face, aceptar la licencia Gemma y token de lectura | Libre (Apache 2.0) |

- Separa mucho mejor lo que el catálogo no tiene: con Qwen3, consultas sin
  respuesta como "llevar la contabilidad" puntúan más alto que consultas
  válidas, y no existe un umbral posible.
- Unas 3 veces más rápido y con la mitad de RAM, lo que importa para desplegar.
- Mejor recall y diferencia mejor los pares.
- Pierde en MRR (0,83 frente a 0,92). Con 14 consultas y top-3, la diferencia
  no es concluyente.
- Costo: cada máquina que lo descargue necesita el token (ver `ai/README.md`).
- Reversible: Qwen3 sigue en el registro (`AI_EMBEDDING_MODEL=qwen3`); cambiar
  de modelo obliga a recalibrar el umbral.

**Umbral de "sin evidencia": 0,20** (`min_score` del modelo en `ai/embeddings.py`),
calibrado con el golden set `catalog`. Provisional.

- Si el 1.er resultado de una necesidad puntúa menos de 0,20, el catálogo no
  tiene una herramienta para ella. Un puntaje igual a 0,20 pasa.
- Regla para elegir el corte:
  1. No bloquear consultas válidas **que la búsqueda resuelve** (alguna
     herramienta correcta en el top-3).
  2. Si esas consultas y las sin respuesta se separan, el corte es el menor
     valor de dos decimales por encima de la mejor sin respuesta.
  3. Si se solapan, el corte es la peor de esas válidas, redondeada hacia abajo.
- **La condición del punto 1 se agregó después de ver los resultados.** Con
  todas las válidas, el corte habría bajado a 0,14 por una consulta en la que
  la búsqueda ya había fallado ("tableros de entregas", con jaeger 1.º y
  grafana 9.º), y habrían pasado 4 de 6 consultas sin respuesta. Un umbral no
  arregla una búsqueda que no encontró la herramienta; esas consultas se
  reportan como fallos de búsqueda.
- Resultado: las 4 válidas resueltas quedan entre 0,241 y 0,415; la mejor sin
  respuesta es 0,194 ("medir qué páginas se visitan más", con grafana 1.º), así
  que 0,20 no deja pasar ninguna. "Tableros de entregas" (0,146) queda
  bloqueada: es un fallo de búsqueda.
- El corte va cerca de las consultas sin respuesta a propósito: bloquear una
  necesidad válida no tiene arreglo después (el LLM nunca ve esa herramienta),
  mientras que una necesidad sin respuesta que pasa todavía puede frenarla el LLM.
- Se aplica **sin filtros**: si una necesidad tiene evidencia pero nada cumple
  los filtros del usuario (por ejemplo, la licencia), la respuesta es una
  limitación ("existe, pero no con esa licencia"), no "sin evidencia".

## Límites

- **Pocas consultas:** el umbral se apoya en 4 consultas válidas resueltas y 6
  sin respuesta; el margen con la más cercana es de 0,006. Los números indican
  una dirección, no son precisos.
- **El catálogo real todavía no tiene categorías ni resumen en español** en el
  texto que se convierte en vector. Cuando los tenga, los puntajes cambian y hay
  que recalibrar el umbral con el mismo comando.
- **Un golden set vale para una versión del catálogo.** Con más repos pueden
  aparecer herramientas válidas que no están en las listas, y alguna consulta
  sin respuesta puede dejar de serlo.
- **Los tiempos varían entre corridas** según la carga de la máquina; se comparan
  en proporción. La RAM de EmbeddingGemma es una estimación.
- Las consultas simulan las búsquedas por necesidad que hará el asistente. Si el
  asistente las escribe con otro estilo o en otro idioma, hay que volver a medir.

## Cuando cambie el catálogo

1. Volver a exportar el snapshot (`python -m ai.scripts.export_catalog_snapshot`).
   El test de la fecha falla hasta revisar el golden set `catalog`.
2. Revisar que las consultas sin respuesta sigan sin respuesta y si hay
   herramientas nuevas válidas para las otras: agregarlas **solo con evidencia**,
   con su `note`, y subir `version`.
3. Actualizar `catalog_taken_at`, correr la evaluación y recalibrar `min_score`
   con la regla de arriba.
