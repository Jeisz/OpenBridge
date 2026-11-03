# Evaluación de la búsqueda · google/embeddinggemma-300m

Generado con `python -m ai.eval.run_search_eval --golden catalog` el 2026-11-02. Golden set `catalog` v1 · catálogo `snapshot` del 2026-10-29 · 100 repos · k = 3 · CPU.

## Resumen

| Métrica | Valor |
|---|---|
| hit@3 | 4/6 (67%) |
| MRR@3 | 0.39 |
| recall@3 | 47% |
| Carga del modelo + primera consulta | 4.2 s |
| Vectores del catálogo (100 repos) | 6.9 s |
| Consulta (promedio) | 0.05 s |

## Consultas con respuesta

| Consulta | Acierto | Posición de cada esperado | Top-3 (puntaje) |
|---|---|---|---|
| `msg-eventos` | ✅ | kafka 2 | flux2 0.307 · kafka 0.288 · beam 0.231 |
| `proc-tiempo-real` | ❌ | flink 14 · beam 4 | redis 0.298 · ClickHouse 0.252 · kafka 0.249 |
| `db-analitica` | ✅ | ClickHouse 2 · duckdb 3 | spark 0.241 · ClickHouse 0.237 · duckdb 0.235 |
| `an-tableros` | ❌ | grafana 9 | jaeger 0.146 · celery 0.137 · etcd 0.134 |
| `ai-rag` | ✅ | llama_index 1 · langchain 15 | llama_index 0.242 · ansible 0.211 · anthropic-sdk-python 0.191 |
| `obs-stack` | ✅ | opentelemetry-collector 3 · jaeger 5 · prometheus 4 | grafana 0.415 · traefik 0.379 · opentelemetry-collector 0.364 |

## Consultas sin respuesta (el puntaje del 1.º sirve para el umbral)

| Consulta | Top-3 (puntaje) |
|---|---|
| `none-pagos` | svelte 0.128 · opentelemetry-collector 0.127 · numpy 0.126 |
| `none-login` | react 0.153 · runc 0.133 · cypress 0.130 |
| `none-recordatorios` | alertmanager 0.178 · playwright 0.076 · jest 0.074 |
| `none-videos` | svelte 0.121 · vllm 0.113 · etcd 0.112 |
| `none-cms` | vscode 0.181 · git 0.177 · prettier 0.176 |
| `none-analitica-web` | grafana 0.194 · opentelemetry-collector 0.176 · prometheus 0.166 |

## Umbral de `no_evidence`

Umbral: **0.200**. Si el 1.er resultado puntúa menos, la necesidad se responde como sin evidencia.

| | Valor |
|---|---|
| 1.er resultado, consultas con respuesta | 0.146 – 0.415 |
| 1.er resultado, consultas sin respuesta | 0.121 – 0.194 |
| Con respuesta bloqueadas (error grave) | 1/6: `an-tableros` |
| Sin respuesta que pasan (las puede frenar el LLM) | 0/6: — |
