# Evaluación de la búsqueda · google/embeddinggemma-300m

Generado con `python -m ai.eval.run_search_eval --golden catalog --texto sin-categorias` el 2026-11-06. Golden set `catalog` v2 · catálogo `snapshot` del 2026-10-29 · 100 repos · k = 3 · CPU · datos de la IA en el texto: summary, use_cases.

## Resumen

| Métrica | Valor |
|---|---|
| hit@3 | 52/60 (87%) |
| MRR@3 | 0.78 |
| recall@3 | 71% |
| hit@5 (con 5 candidatos por necesidad) | 54/60 (90%) |
| Carga del modelo + primera consulta | 5.2 s |
| Vectores del catálogo (100 repos) | 16.4 s |
| Consulta (promedio) | 0.06 s |

## Consultas con respuesta

| Consulta | Acierto | Posición de cada esperado | Top-3 (puntaje) |
|---|---|---|---|
| `msg-eventos` | ✅ | kafka 2 | flux2 0.357 · kafka 0.344 · flink 0.339 |
| `proc-tiempo-real` | ✅ | flink 1 · beam 6 | flink 0.334 · redis 0.317 · kafka 0.314 |
| `db-analitica` | ✅ | ClickHouse 2 · duckdb 3 | kafka 0.297 · ClickHouse 0.293 · duckdb 0.288 |
| `an-tableros` | ❌ | grafana 6 | jaeger 0.187 · celery 0.171 · etcd 0.167 |
| `ai-rag` | ✅ | llama_index 1 · langchain 18 | llama_index 0.270 · envoy 0.227 · anthropic-sdk-python 0.222 |
| `obs-stack` | ✅ | opentelemetry-collector 5 · prometheus 4 · grafana 1 | grafana 0.452 · jaeger 0.427 · traefik 0.421 |
| `tienda-search` | ✅ | OpenSearch 2 | ripgrep 0.334 · OpenSearch 0.328 · pgvector 0.303 |
| `tienda-search-v2` | ✅ | OpenSearch 2 | ripgrep 0.355 · OpenSearch 0.355 · pgvector 0.321 |
| `tienda-analytics` | ❌ | grafana 6 | duckdb 0.266 · ClickHouse 0.251 · dbt 0.232 |
| `tienda-analytics-v2` | ❌ | grafana 6 | duckdb 0.265 · ClickHouse 0.246 · dbt 0.227 |
| `academia-ai` | ✅ | langchain 1 · llama_index 3 | langchain 0.334 · ollama 0.294 · llama_index 0.289 |
| `academia-ai-v2` | ✅ | langchain 1 · llama_index 5 | langchain 0.358 · transformers 0.358 · ollama 0.353 |
| `logistica-messaging` | ✅ | kafka 2 · flink 1 · beam 3 | flink 0.459 · kafka 0.390 · beam 0.382 |
| `logistica-messaging-v2` | ✅ | kafka 2 · flink 1 · beam 3 | flink 0.479 · kafka 0.392 · beam 0.366 |
| `logistica-database` | ❌ | ClickHouse 19 | etcd 0.294 · redis 0.263 · pgvector 0.238 |
| `logistica-database-v2` | ❌ | ClickHouse 22 | etcd 0.292 · redis 0.287 · pgvector 0.239 |
| `logistica-analytics` | ✅ | grafana 1 | grafana 0.345 · dbt 0.278 · storybook 0.242 |
| `logistica-analytics-v2` | ✅ | grafana 1 | grafana 0.365 · dbt 0.248 · opentelemetry-collector 0.231 |
| `soporte-ai` | ✅ | ollama 1 · vllm 2 | ollama 0.528 · vllm 0.493 · langchain 0.423 |
| `soporte-ai-v2` | ✅ | ollama 1 · vllm 3 | ollama 0.427 · langchain 0.349 · vllm 0.344 |
| `soporte-search` | ✅ | OpenSearch 2 | ripgrep 0.344 · OpenSearch 0.334 · llama_index 0.319 |
| `soporte-search-v2` | ✅ | OpenSearch 1 | OpenSearch 0.303 · ripgrep 0.273 · datasets 0.242 |
| `soporte-observability` | ✅ | grafana 3 · opentelemetry-collector 4 · prometheus 1 | prometheus 0.394 · jaeger 0.358 · grafana 0.349 |
| `soporte-observability-v2` | ✅ | grafana 3 · opentelemetry-collector 4 · prometheus 1 | prometheus 0.379 · jaeger 0.374 · grafana 0.358 |
| `periodico-frontend` | ✅ | nuxt 16 · next.js 6 · astro 2 | vite 0.413 · astro 0.383 · django 0.365 |
| `periodico-frontend-v2` | ❌ | nuxt 15 · next.js 8 · astro 12 | tailwindcss 0.493 · core 0.465 · vite 0.465 |
| `rag-largo-ai` | ✅ | ollama 1 · vllm 4 | ollama 0.420 · transformers 0.353 · langchain 0.344 |
| `rag-largo-ai-v2` | ✅ | ollama 1 · vllm 3 | ollama 0.374 · transformers 0.352 · vllm 0.332 |
| `rag-largo-search` | ✅ | OpenSearch 2 · pgvector 1 | pgvector 0.397 · OpenSearch 0.309 · ripgrep 0.307 |
| `rag-largo-search-v2` | ✅ | OpenSearch 2 · pgvector 1 | pgvector 0.444 · OpenSearch 0.333 · ripgrep 0.325 |
| `api-largo-cache` | ✅ | redis 1 | redis 0.444 · etcd 0.353 · celery 0.272 |
| `api-largo-cache-v2` | ✅ | redis 1 | redis 0.464 · etcd 0.405 · celery 0.275 |
| `api-largo-infrastructure` | ❌ | kubernetes 4 · nginx 13 · traefik 12 | kafka 0.317 · redis 0.303 · etcd 0.288 |
| `api-largo-infrastructure-v2` | ✅ | kubernetes 1 | kubernetes 0.399 · containerd 0.371 · compose 0.338 |
| `rag-corto-ai` | ✅ | langchain 5 · llama_index 1 | llama_index 0.286 · transformers 0.275 · vllm 0.268 |
| `rag-corto-ai-v2` | ✅ | langchain 11 · llama_index 2 | transformers 0.234 · llama_index 0.225 · vllm 0.224 |
| `api-corto-cache` | ✅ | redis 1 | redis 0.285 · etcd 0.236 · vllm 0.220 |
| `api-corto-cache-v2` | ✅ | redis 1 | redis 0.399 · nginx 0.282 · etcd 0.258 |
| `api-corto-infrastructure` | ✅ | kubernetes 1 | kubernetes 0.334 · containerd 0.326 · runc 0.268 |
| `api-corto-infrastructure-v2` | ❌ | kubernetes 6 · nginx 21 · traefik 4 | terraform 0.349 · prefect 0.225 · ansible 0.222 |
| `eventos-messaging` | ✅ | kafka 4 · celery 2 | beam 0.295 · celery 0.293 · flink 0.290 |
| `eventos-messaging-v2` | ✅ | kafka 8 · celery 1 | celery 0.439 · beam 0.329 · starlette 0.302 |
| `observabilidad-observability` | ✅ | opentelemetry-collector 2 · prometheus 3 · grafana 1 | grafana 0.546 · opentelemetry-collector 0.448 · prometheus 0.422 |
| `observabilidad-observability-v2` | ✅ | jaeger 4 · opentelemetry-collector 2 · prometheus 3 | grafana 0.468 · opentelemetry-collector 0.442 · prometheus 0.425 |
| `una-busqueda-search` | ✅ | OpenSearch 1 | OpenSearch 0.350 · ripgrep 0.338 · ruff 0.319 |
| `back-api` | ✅ | fastapi 1 · django 7 · flask 3 | fastapi 0.536 · openai-python 0.469 · flask 0.458 |
| `back-asgi` | ✅ | starlette 1 · fastapi 7 | starlette 0.534 · caddy 0.403 · flask 0.390 |
| `dev-lint-python` | ✅ | ruff 2 · black 1 | black 0.488 · ruff 0.466 · cpython 0.462 |
| `dev-lint-javascript` | ✅ | eslint 1 · biome 10 | eslint 0.531 · jest 0.384 · TypeScript 0.372 |
| `dev-test-navegador` | ✅ | playwright 1 · cypress 2 | playwright 0.565 · cypress 0.448 · vitest 0.405 |
| `dev-test-unitarias` | ✅ | pytest 1 | pytest 0.559 · cpython 0.384 · vitest 0.383 |
| `dev-dependencias` | ✅ | uv 1 | uv 0.486 · pnpm 0.420 · prefect 0.385 |
| `infra-despliegue-continuo` | ✅ | argo-cd 5 · flux2 3 | containerd 0.518 · kubernetes 0.506 · flux2 0.452 |
| `infra-como-codigo` | ✅ | terraform 1 | terraform 0.546 · ansible 0.360 · istio 0.347 |
| `auto-servidores` | ✅ | ansible 1 | ansible 0.450 · caddy 0.365 · terraform 0.348 |
| `obs-trazas` | ✅ | jaeger 1 · opentelemetry-collector 8 | jaeger 0.474 · istio 0.325 · traefik 0.323 |
| `seguridad-secretos` | ✅ | vault 1 | vault 0.493 · cert-manager 0.359 · alertmanager 0.309 |
| `datos-lotes` | ✅ | spark 3 · beam 1 | beam 0.435 · flink 0.399 · spark 0.353 |
| `datos-orquestacion` | ✅ | airflow 1 · prefect 2 · dagster 3 | airflow 0.442 · prefect 0.430 · dagster 0.404 |
| `busqueda-vectorial` | ✅ | pgvector 1 · OpenSearch 4 | pgvector 0.542 · ripgrep 0.275 · redis 0.260 |

## Pares (deben dar resultados distintos)

| Par | Consulta | Top-3 |
|---|---|---|
| access | `clinica-auth` | alertmanager 0.277 · vault 0.258 · react 0.250 |
| access | `seguridad-secretos` | vault 0.493 · cert-manager 0.359 · alertmanager 0.309 |
| automation | `tienda-automation` | duckdb 0.258 · ClickHouse 0.242 · airflow 0.230 |
| automation | `auto-servidores` | ansible 0.450 · caddy 0.365 · terraform 0.348 |
| lint | `dev-lint-python` | black 0.488 · ruff 0.466 · cpython 0.462 |
| lint | `dev-lint-javascript` | eslint 0.531 · jest 0.384 · TypeScript 0.372 |
| tests | `dev-test-navegador` | playwright 0.565 · cypress 0.448 · vitest 0.405 |
| tests | `dev-test-unitarias` | pytest 0.559 · cpython 0.384 · vitest 0.383 |

## Consultas sin respuesta (el puntaje del 1.º sirve para el umbral)

| Consulta | Top-3 (puntaje) |
|---|---|
| `none-pagos` | cli 0.179 · opentelemetry-collector 0.178 · cli 0.157 |
| `none-login` | react 0.208 · storybook 0.195 · compose 0.181 |
| `none-recordatorios` | alertmanager 0.214 · celery 0.133 · cert-manager 0.131 |
| `none-videos` | etcd 0.162 · redis 0.160 · vllm 0.160 |
| `none-cms` | vscode 0.294 · prettier 0.272 · neovim 0.233 |
| `none-analitica-web` | grafana 0.230 · prometheus 0.205 · playwright 0.192 |
| `clinica-auth` | alertmanager 0.277 · vault 0.258 · react 0.250 |
| `clinica-auth-v2` | alertmanager 0.278 · vault 0.276 · kubernetes 0.251 |
| `clinica-communication` | alertmanager 0.218 · celery 0.180 · jaeger 0.162 |
| `clinica-communication-v2` | alertmanager 0.212 · celery 0.200 · envoy 0.176 |
| `clinica-payments` | beam 0.255 · opentelemetry-collector 0.252 · prefect 0.203 |
| `clinica-payments-v2` | opentelemetry-collector 0.282 · flink 0.273 · beam 0.253 |
| `tienda-payments` | flink 0.159 · beam 0.153 · caddy 0.148 |
| `tienda-payments-v2` | beam 0.168 · playwright 0.155 · flink 0.154 |
| `tienda-automation` | duckdb 0.258 · ClickHouse 0.242 · airflow 0.230 |
| `academia-auth` | react 0.217 · storybook 0.197 · core 0.197 |
| `academia-storage` | etcd 0.204 · redis 0.194 · pgvector 0.186 |
| `academia-storage-v2` | etcd 0.180 · redis 0.177 · vault 0.170 |
| `academia-payments` | ripgrep 0.174 · prefect 0.165 · alertmanager 0.165 |
| `academia-payments-v2` | opentelemetry-collector 0.170 · prometheus 0.162 · cli 0.160 |
| `periodico-cms` | vscode 0.327 · prettier 0.243 · neovim 0.241 |
| `periodico-cms-v2` | astro 0.261 · pnpm 0.255 · alertmanager 0.253 |
| `periodico-communication` | alertmanager 0.181 · celery 0.157 · envoy 0.155 |
| `periodico-communication-v2` | celery 0.171 · envoy 0.149 · nginx 0.131 |
| `periodico-analytics` | prometheus 0.137 · grafana 0.122 · opentelemetry-collector 0.111 |
| `periodico-analytics-v2` | astro 0.305 · ClickHouse 0.275 · duckdb 0.274 |
| `saas-largo-auth` | react 0.293 · runc 0.272 · cert-manager 0.259 |
| `saas-largo-auth-v2` | vault 0.246 · etcd 0.226 · flux2 0.210 |
| `rag-largo-auth` | vault 0.320 · cert-manager 0.256 · llama_index 0.239 |
| `rag-largo-auth-v2` | cert-manager 0.323 · alertmanager 0.261 · vault 0.236 |
| `api-largo-database` | sqlalchemy 0.438 · sqlmodel 0.386 · ClickHouse 0.374 |
| `saas-corto-auth` | vault 0.306 · ansible 0.246 · playwright 0.222 |
| `saas-corto-auth-v2` | vault 0.324 · cert-manager 0.317 · ansible 0.294 |
| `rag-corto-auth` | vault 0.348 · istio 0.261 · alertmanager 0.253 |
| `rag-corto-auth-v2` | vault 0.344 · alertmanager 0.310 · cert-manager 0.308 |
| `una-pagos-payments` | ripgrep 0.179 · prefect 0.172 · alertmanager 0.169 |
| `none-contabilidad` | pnpm 0.163 · alertmanager 0.160 · cli 0.152 |
| `none-inventario` | flux2 0.213 · vault 0.206 · git 0.200 |
| `none-videollamadas` | playwright 0.294 · core 0.236 · cypress 0.233 |
| `none-factura-electronica` | cert-manager 0.147 · duckdb 0.137 · jaeger 0.134 |

## Umbral de `no_evidence`

Si el 1.er resultado de una necesidad puntúa menos que el umbral, se responde como sin evidencia. Para calcularlo solo cuentan las consultas con respuesta que la búsqueda resuelve (algún esperado en el top-3); las demás son fallos de búsqueda.

| | Valor |
|---|---|
| 1.er resultado, con respuesta resueltas (52) | 0.234 – 0.565 |
| 1.er resultado, con respuesta no resueltas (8) | 0.187 – 0.493 |
| 1.er resultado, sin respuesta (40) | 0.137 – 0.438 |
| Umbral actual del modelo | 0.19 |
| Umbral que sugiere la regla | **0.23** |
| Umbral actual: resueltas bloqueadas (error grave) | 0/52: — |
| Umbral actual: sin respuesta que pasan | 27/40: `none-login`, `none-recordatorios`, `none-cms`, `none-analitica-web`, `clinica-auth`, `clinica-auth-v2`, `clinica-communication`, `clinica-communication-v2`, `clinica-payments`, `clinica-payments-v2`, `tienda-automation`, `academia-auth`, `academia-storage`, `periodico-cms`, `periodico-cms-v2`, `periodico-analytics-v2`, `saas-largo-auth`, `saas-largo-auth-v2`, `rag-largo-auth`, `rag-largo-auth-v2`, `api-largo-database`, `saas-corto-auth`, `saas-corto-auth-v2`, `rag-corto-auth`, `rag-corto-auth-v2`, `none-inventario`, `none-videollamadas` |
| Umbral sugerido: resueltas bloqueadas (error grave) | 0/52: — |
| Umbral sugerido: sin respuesta que pasan | 20/40: `none-cms`, `none-analitica-web`, `clinica-auth`, `clinica-auth-v2`, `clinica-payments`, `clinica-payments-v2`, `tienda-automation`, `periodico-cms`, `periodico-cms-v2`, `periodico-analytics-v2`, `saas-largo-auth`, `saas-largo-auth-v2`, `rag-largo-auth`, `rag-largo-auth-v2`, `api-largo-database`, `saas-corto-auth`, `saas-corto-auth-v2`, `rag-corto-auth`, `rag-corto-auth-v2`, `none-videollamadas` |

Fallos de búsqueda (no cuentan para el umbral): `an-tableros`, `tienda-analytics`, `tienda-analytics-v2`, `logistica-database`, `logistica-database-v2`, `periodico-frontend-v2`, `api-largo-infrastructure`, `api-corto-infrastructure-v2`
