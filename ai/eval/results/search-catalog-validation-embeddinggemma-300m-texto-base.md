# Evaluación de la búsqueda · google/embeddinggemma-300m

Generado con `python -m ai.eval.run_search_eval --golden catalog-validation --texto base` el 2026-11-06. Golden set `catalog-validation` v1 · catálogo `snapshot` del 2026-10-29 · 100 repos · k = 3 · CPU · datos de la IA en el texto: ninguno.

## Resumen

| Métrica | Valor |
|---|---|
| hit@3 | 20/20 (100%) |
| MRR@3 | 0.93 |
| recall@3 | 88% |
| hit@5 (con 5 candidatos por necesidad) | 20/20 (100%) |
| Carga del modelo + primera consulta | 5.5 s |
| Vectores del catálogo (100 repos) | 7.5 s |
| Consulta (promedio) | 0.06 s |

## Consultas con respuesta

| Consulta | Acierto | Posición de cada esperado | Top-3 (puntaje) |
|---|---|---|---|
| `cola-tareas` | ✅ | celery 1 | celery 0.354 · tailwindcss 0.195 · alertmanager 0.185 |
| `transformacion-sql` | ✅ | dbt 1 | dbt 0.283 · sqlmodel 0.273 · sqlalchemy 0.267 |
| `db-embebida` | ✅ | duckdb 1 | duckdb 0.451 · dbt 0.388 · ClickHouse 0.375 |
| `clave-valor` | ✅ | etcd 1 | etcd 0.399 · redis 0.247 · ClickHouse 0.205 |
| `https-automatico` | ✅ | caddy 1 · traefik 18 | caddy 0.461 · cert-manager 0.372 · nginx 0.312 |
| `certificados-k8s` | ✅ | cert-manager 1 | cert-manager 0.642 · helm 0.372 · kubernetes 0.358 |
| `paquetes-k8s` | ✅ | helm 1 | helm 0.411 · kubernetes 0.411 · flux2 0.396 |
| `malla-servicios` | ✅ | istio 1 · envoy 3 | istio 0.332 · traefik 0.263 · envoy 0.253 |
| `red-contenedores` | ✅ | cilium 3 · istio 5 | containerd 0.326 · kubernetes 0.302 · cilium 0.293 |
| `datos-tabulares` | ✅ | pandas 1 | pandas 0.427 · cpython 0.329 · sqlalchemy 0.316 |
| `redes-neuronales` | ✅ | pytorch 1 · tensorflow 2 | pytorch 0.373 · tensorflow 0.365 · transformers 0.283 |
| `ml-clasico` | ✅ | scikit-learn 3 | transformers 0.280 · ollama 0.247 · scikit-learn 0.243 |
| `api-llm` | ✅ | anthropic-sdk-python 5 · openai-python 1 · langchain 3 | openai-python 0.349 · sqlmodel 0.315 · langchain 0.299 |
| `componentes-ui` | ✅ | react 1 · core 2 · svelte 5 | react 0.423 · core 0.381 · storybook 0.377 |
| `estilos-ui` | ✅ | tailwindcss 1 | tailwindcss 0.406 · storybook 0.300 · react 0.298 |
| `multi-contenedor` | ✅ | compose 1 | compose 0.410 · containerd 0.345 · kubernetes 0.291 |
| `balanceo-carga` | ✅ | nginx 1 · traefik 2 · envoy 8 | nginx 0.230 · traefik 0.195 · astro 0.191 |
| `metricas-servidores` | ✅ | prometheus 2 · opentelemetry-collector 1 | opentelemetry-collector 0.384 · prometheus 0.321 · grafana 0.299 |
| `validacion-datos` | ✅ | pydantic 1 | pydantic 0.422 · TypeScript 0.260 · sqlmodel 0.184 |
| `pruebas-js` | ✅ | jest 1 · vitest 7 | jest 0.432 · react-testing-library 0.387 · playwright 0.381 |

## Consultas sin respuesta (el puntaje del 1.º sirve para el umbral)

| Consulta | Top-3 (puntaje) |
|---|---|
| `none-grafos` | grafana 0.311 · prometheus 0.301 · duckdb 0.291 |
| `none-cdn` | etcd 0.271 · astro 0.246 · nginx 0.208 |
| `none-respaldos` | caddy 0.203 · terraform 0.202 · ansible 0.182 |
| `none-objetos` | etcd 0.244 · celery 0.229 · containerd 0.216 |
| `none-push` | alertmanager 0.170 · prometheus 0.088 · grafana 0.087 |
| `none-chat` | redis 0.225 · ClickHouse 0.184 · envoy 0.166 |
| `none-sms` | envoy 0.090 · anthropic-sdk-python 0.083 · jest 0.075 |
| `none-aprobaciones` | flux2 0.200 · terraform 0.192 · prefect 0.165 |
| `none-embudos` | dbt 0.216 · envoy 0.211 · angular 0.178 |
| `none-sso` | traefik 0.234 · envoy 0.214 · caddy 0.206 |
| `none-facturacion-uso` | traefik 0.144 · envoy 0.121 · flux2 0.120 |
| `none-editor-paginas` | vscode 0.348 · core 0.279 · biome 0.275 |
| `none-crm` | cert-manager 0.173 · cli 0.164 · ClickHouse 0.159 |
| `none-agenda` | biome 0.146 · cypress 0.133 · jest 0.132 |
| `none-firma` | ecma262 0.153 · vscode 0.150 · llama_index 0.136 |

## Umbral de `no_evidence`

Si el 1.er resultado de una necesidad puntúa menos que el umbral, se responde como sin evidencia. Para calcularlo solo cuentan las consultas con respuesta que la búsqueda resuelve (algún esperado en el top-3); las demás son fallos de búsqueda.

| | Valor |
|---|---|
| 1.er resultado, con respuesta resueltas (20) | 0.230 – 0.642 |
| 1.er resultado, con respuesta no resueltas (0) | — |
| 1.er resultado, sin respuesta (15) | 0.090 – 0.348 |
| Umbral actual del modelo | 0.23 |
| Umbral que sugiere la regla | **0.23** |
| Umbral actual: resueltas bloqueadas (error grave) | 0/20: — |
| Umbral actual: sin respuesta que pasan | 5/15: `none-grafos`, `none-cdn`, `none-objetos`, `none-sso`, `none-editor-paginas` |

Fallos de búsqueda (no cuentan para el umbral): —
