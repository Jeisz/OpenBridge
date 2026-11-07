# Evaluación de la búsqueda · google/embeddinggemma-300m

Generado con `python -m ai.eval.run_search_eval --golden catalog --texto casos` el 2026-11-06. Golden set `catalog` v2 · catálogo `snapshot` del 2026-10-29 · 100 repos · k = 3 · CPU · datos de la IA en el texto: categories, summary, use_cases.

## Resumen

| Métrica | Valor |
|---|---|
| hit@3 | 53/60 (88%) |
| MRR@3 | 0.81 |
| recall@3 | 72% |
| hit@5 (con 5 candidatos por necesidad) | 56/60 (93%) |
| Carga del modelo + primera consulta | 4.6 s |
| Vectores del catálogo (100 repos) | 20.6 s |
| Consulta (promedio) | 0.05 s |

## Consultas con respuesta

| Consulta | Acierto | Posición de cada esperado | Top-3 (puntaje) |
|---|---|---|---|
| `msg-eventos` | ✅ | kafka 1 | kafka 0.335 · flux2 0.332 · flink 0.315 |
| `proc-tiempo-real` | ✅ | flink 1 · beam 5 | flink 0.368 · kafka 0.366 · prefect 0.333 |
| `db-analitica` | ✅ | ClickHouse 1 · duckdb 3 | ClickHouse 0.312 · pandas 0.283 · duckdb 0.280 |
| `an-tableros` | ❌ | grafana 4 | jaeger 0.178 · celery 0.171 · etcd 0.160 |
| `ai-rag` | ✅ | llama_index 1 · langchain 9 | llama_index 0.247 · anthropic-sdk-python 0.238 · ansible 0.222 |
| `obs-stack` | ✅ | opentelemetry-collector 3 · prometheus 5 · grafana 2 | jaeger 0.497 · grafana 0.479 · opentelemetry-collector 0.445 |
| `tienda-search` | ✅ | OpenSearch 1 | OpenSearch 0.371 · pgvector 0.343 · ripgrep 0.327 |
| `tienda-search-v2` | ✅ | OpenSearch 1 | OpenSearch 0.418 · pgvector 0.388 · ripgrep 0.368 |
| `tienda-analytics` | ❌ | grafana 5 | ClickHouse 0.309 · duckdb 0.239 · dbt 0.239 |
| `tienda-analytics-v2` | ❌ | grafana 4 | ClickHouse 0.297 · duckdb 0.238 · dbt 0.224 |
| `academia-ai` | ✅ | langchain 1 · llama_index 8 | langchain 0.361 · ollama 0.345 · transformers 0.339 |
| `academia-ai-v2` | ✅ | langchain 1 · llama_index 7 | langchain 0.376 · transformers 0.373 · ollama 0.364 |
| `logistica-messaging` | ✅ | kafka 2 · flink 1 · beam 4 | flink 0.474 · kafka 0.453 · airflow 0.423 |
| `logistica-messaging-v2` | ✅ | kafka 2 · flink 1 · beam 3 | flink 0.502 · kafka 0.442 · beam 0.406 |
| `logistica-database` | ❌ | ClickHouse 18 | redis 0.281 · etcd 0.267 · pgvector 0.233 |
| `logistica-database-v2` | ❌ | ClickHouse 14 | redis 0.302 · etcd 0.290 · pgvector 0.257 |
| `logistica-analytics` | ✅ | grafana 1 | grafana 0.336 · dbt 0.287 · jaeger 0.246 |
| `logistica-analytics-v2` | ✅ | grafana 1 | grafana 0.363 · dbt 0.270 · opentelemetry-collector 0.256 |
| `soporte-ai` | ✅ | ollama 1 · vllm 2 | ollama 0.487 · vllm 0.478 · langchain 0.419 |
| `soporte-ai-v2` | ✅ | ollama 1 · vllm 2 | ollama 0.456 · vllm 0.395 · langchain 0.392 |
| `soporte-search` | ✅ | OpenSearch 1 | OpenSearch 0.410 · ripgrep 0.380 · pgvector 0.372 |
| `soporte-search-v2` | ✅ | OpenSearch 1 | OpenSearch 0.360 · pgvector 0.315 · ripgrep 0.304 |
| `soporte-observability` | ✅ | grafana 3 · opentelemetry-collector 4 · prometheus 2 | jaeger 0.412 · prometheus 0.407 · grafana 0.392 |
| `soporte-observability-v2` | ✅ | grafana 3 · opentelemetry-collector 4 · prometheus 2 | jaeger 0.417 · prometheus 0.396 · grafana 0.396 |
| `periodico-frontend` | ✅ | nuxt 11 · next.js 7 · astro 3 | vite 0.382 · tailwindcss 0.374 · astro 0.369 |
| `periodico-frontend-v2` | ❌ | nuxt 10 · next.js 8 · astro 9 | tailwindcss 0.534 · svelte 0.500 · core 0.500 |
| `rag-largo-ai` | ✅ | ollama 1 · vllm 4 | ollama 0.392 · langchain 0.358 · transformers 0.349 |
| `rag-largo-ai-v2` | ✅ | ollama 2 · vllm 3 | transformers 0.405 · ollama 0.400 · vllm 0.380 |
| `rag-largo-search` | ✅ | OpenSearch 2 · pgvector 1 | pgvector 0.485 · OpenSearch 0.397 · ripgrep 0.339 |
| `rag-largo-search-v2` | ✅ | OpenSearch 2 · pgvector 1 | pgvector 0.515 · OpenSearch 0.412 · ripgrep 0.346 |
| `api-largo-cache` | ✅ | redis 1 | redis 0.464 · nginx 0.341 · etcd 0.329 |
| `api-largo-cache-v2` | ✅ | redis 1 | redis 0.488 · etcd 0.380 · nginx 0.366 |
| `api-largo-infrastructure` | ✅ | kubernetes 1 · nginx 5 · traefik 11 | kubernetes 0.310 · kafka 0.305 · caddy 0.295 |
| `api-largo-infrastructure-v2` | ✅ | kubernetes 1 | kubernetes 0.431 · containerd 0.397 · runc 0.371 |
| `rag-corto-ai` | ✅ | langchain 5 · llama_index 3 | transformers 0.291 · vllm 0.280 · llama_index 0.266 |
| `rag-corto-ai-v2` | ❌ | langchain 9 · llama_index 6 | transformers 0.243 · vllm 0.231 · jaeger 0.218 |
| `api-corto-cache` | ✅ | redis 1 | redis 0.326 · nginx 0.245 · etcd 0.216 |
| `api-corto-cache-v2` | ✅ | redis 1 | redis 0.444 · nginx 0.388 · etcd 0.241 |
| `api-corto-infrastructure` | ✅ | kubernetes 1 | kubernetes 0.336 · containerd 0.322 · runc 0.279 |
| `api-corto-infrastructure-v2` | ✅ | kubernetes 2 · nginx 8 · traefik 3 | terraform 0.394 · kubernetes 0.302 · traefik 0.294 |
| `eventos-messaging` | ✅ | kafka 1 · celery 5 | kafka 0.351 · flink 0.324 · beam 0.317 |
| `eventos-messaging-v2` | ✅ | kafka 5 · celery 1 | celery 0.420 · beam 0.354 · flink 0.343 |
| `observabilidad-observability` | ✅ | opentelemetry-collector 2 · prometheus 4 · grafana 1 | grafana 0.562 · opentelemetry-collector 0.521 · jaeger 0.471 |
| `observabilidad-observability-v2` | ✅ | jaeger 3 · opentelemetry-collector 1 · prometheus 4 | opentelemetry-collector 0.521 · grafana 0.497 · jaeger 0.475 |
| `una-busqueda-search` | ✅ | OpenSearch 1 | OpenSearch 0.393 · ripgrep 0.352 · pgvector 0.347 |
| `back-api` | ✅ | fastapi 1 · django 4 · flask 2 | fastapi 0.546 · flask 0.529 · httpx 0.499 |
| `back-asgi` | ✅ | starlette 1 · fastapi 5 | starlette 0.525 · flask 0.413 · caddy 0.410 |
| `dev-lint-python` | ✅ | ruff 3 · black 1 | black 0.508 · cpython 0.498 · ruff 0.491 |
| `dev-lint-javascript` | ✅ | eslint 1 · biome 11 | eslint 0.501 · jest 0.410 · TypeScript 0.392 |
| `dev-test-navegador` | ✅ | playwright 1 · cypress 2 | playwright 0.555 · cypress 0.441 · vitest 0.380 |
| `dev-test-unitarias` | ✅ | pytest 1 | pytest 0.580 · cpython 0.473 · black 0.436 |
| `dev-dependencias` | ✅ | uv 1 | uv 0.467 · pnpm 0.411 · sqlalchemy 0.379 |
| `infra-despliegue-continuo` | ✅ | argo-cd 5 · flux2 3 | containerd 0.515 · kubernetes 0.506 · flux2 0.448 |
| `infra-como-codigo` | ✅ | terraform 1 | terraform 0.599 · envoy 0.485 · istio 0.453 |
| `auto-servidores` | ✅ | ansible 1 | ansible 0.472 · caddy 0.380 · terraform 0.363 |
| `obs-trazas` | ✅ | jaeger 1 · opentelemetry-collector 4 | jaeger 0.468 · traefik 0.321 · istio 0.309 |
| `seguridad-secretos` | ✅ | vault 1 | vault 0.526 · cert-manager 0.355 · alertmanager 0.309 |
| `datos-lotes` | ✅ | spark 3 · beam 1 | beam 0.462 · flink 0.416 · spark 0.387 |
| `datos-orquestacion` | ✅ | airflow 1 · prefect 2 · dagster 3 | airflow 0.443 · prefect 0.407 · dagster 0.406 |
| `busqueda-vectorial` | ✅ | pgvector 1 · OpenSearch 2 | pgvector 0.551 · OpenSearch 0.296 · redis 0.292 |

## Pares (deben dar resultados distintos)

| Par | Consulta | Top-3 |
|---|---|---|
| access | `clinica-auth` | vault 0.366 · alertmanager 0.261 · cert-manager 0.251 |
| access | `seguridad-secretos` | vault 0.526 · cert-manager 0.355 · alertmanager 0.309 |
| automation | `tienda-automation` | airflow 0.283 · prefect 0.251 · duckdb 0.243 |
| automation | `auto-servidores` | ansible 0.472 · caddy 0.380 · terraform 0.363 |
| lint | `dev-lint-python` | black 0.508 · cpython 0.498 · ruff 0.491 |
| lint | `dev-lint-javascript` | eslint 0.501 · jest 0.410 · TypeScript 0.392 |
| tests | `dev-test-navegador` | playwright 0.555 · cypress 0.441 · vitest 0.380 |
| tests | `dev-test-unitarias` | pytest 0.580 · cpython 0.473 · black 0.436 |

## Consultas sin respuesta (el puntaje del 1.º sirve para el umbral)

| Consulta | Top-3 (puntaje) |
|---|---|
| `none-pagos` | opentelemetry-collector 0.164 · cert-manager 0.145 · cli 0.143 |
| `none-login` | vault 0.268 · react 0.221 · storybook 0.203 |
| `none-recordatorios` | alertmanager 0.239 · celery 0.146 · jest 0.111 |
| `none-videos` | etcd 0.148 · vllm 0.143 · redis 0.140 |
| `none-cms` | prettier 0.280 · vscode 0.254 · pnpm 0.239 |
| `none-analitica-web` | grafana 0.234 · opentelemetry-collector 0.208 · jaeger 0.193 |
| `clinica-auth` | vault 0.366 · alertmanager 0.261 · cert-manager 0.251 |
| `clinica-auth-v2` | vault 0.331 · alertmanager 0.257 · ClickHouse 0.230 |
| `clinica-communication` | alertmanager 0.271 · celery 0.199 · jaeger 0.189 |
| `clinica-communication-v2` | celery 0.250 · alertmanager 0.247 · kafka 0.246 |
| `clinica-payments` | beam 0.294 · kafka 0.281 · flink 0.273 |
| `clinica-payments-v2` | flink 0.319 · beam 0.284 · kafka 0.278 |
| `tienda-payments` | flink 0.202 · beam 0.188 · spark 0.180 |
| `tienda-payments-v2` | flink 0.214 · beam 0.208 · kafka 0.199 |
| `tienda-automation` | airflow 0.283 · prefect 0.251 · duckdb 0.243 |
| `academia-auth` | vault 0.280 · react 0.227 · core 0.211 |
| `academia-storage` | redis 0.210 · nginx 0.186 · etcd 0.177 |
| `academia-storage-v2` | redis 0.198 · nginx 0.188 · etcd 0.164 |
| `academia-payments` | prefect 0.151 · ripgrep 0.147 · flux2 0.145 |
| `academia-payments-v2` | opentelemetry-collector 0.174 · ClickHouse 0.160 · prometheus 0.155 |
| `periodico-cms` | vscode 0.235 · prettier 0.219 · datasets 0.208 |
| `periodico-cms-v2` | pnpm 0.257 · astro 0.241 · cli 0.241 |
| `periodico-communication` | alertmanager 0.176 · kafka 0.173 · celery 0.164 |
| `periodico-communication-v2` | celery 0.164 · kafka 0.156 · alertmanager 0.125 |
| `periodico-analytics` | opentelemetry-collector 0.146 · grafana 0.142 · alertmanager 0.139 |
| `periodico-analytics-v2` | ClickHouse 0.331 · astro 0.277 · duckdb 0.264 |
| `saas-largo-auth` | vault 0.336 · react 0.292 · etcd 0.271 |
| `saas-largo-auth-v2` | vault 0.320 · flux2 0.237 · etcd 0.226 |
| `rag-largo-auth` | vault 0.359 · cert-manager 0.260 · llama_index 0.215 |
| `rag-largo-auth-v2` | cert-manager 0.307 · vault 0.266 · alertmanager 0.235 |
| `api-largo-database` | sqlalchemy 0.421 · sqlmodel 0.385 · ClickHouse 0.375 |
| `saas-corto-auth` | vault 0.384 · ansible 0.255 · flux2 0.223 |
| `saas-corto-auth-v2` | vault 0.423 · cert-manager 0.324 · ansible 0.304 |
| `rag-corto-auth` | vault 0.437 · cert-manager 0.266 · istio 0.259 |
| `rag-corto-auth-v2` | vault 0.373 · cert-manager 0.295 · alertmanager 0.286 |
| `una-pagos-payments` | prefect 0.154 · opentelemetry-collector 0.150 · flux2 0.145 |
| `none-contabilidad` | pnpm 0.165 · cli 0.160 · alertmanager 0.153 |
| `none-inventario` | flux2 0.221 · opentelemetry-collector 0.206 · vault 0.202 |
| `none-videollamadas` | core 0.263 · playwright 0.257 · react 0.214 |
| `none-factura-electronica` | duckdb 0.136 · ecma262 0.134 · cert-manager 0.133 |

## Umbral de `no_evidence`

Si el 1.er resultado de una necesidad puntúa menos que el umbral, se responde como sin evidencia. Para calcularlo solo cuentan las consultas con respuesta que la búsqueda resuelve (algún esperado en el top-3); las demás son fallos de búsqueda.

| | Valor |
|---|---|
| 1.er resultado, con respuesta resueltas (53) | 0.247 – 0.599 |
| 1.er resultado, con respuesta no resueltas (7) | 0.178 – 0.534 |
| 1.er resultado, sin respuesta (40) | 0.136 – 0.437 |
| Umbral actual del modelo | 0.19 |
| Umbral que sugiere la regla | **0.24** |
| Umbral actual: resueltas bloqueadas (error grave) | 0/53: — |
| Umbral actual: sin respuesta que pasan | 30/40: `none-login`, `none-recordatorios`, `none-cms`, `none-analitica-web`, `clinica-auth`, `clinica-auth-v2`, `clinica-communication`, `clinica-communication-v2`, `clinica-payments`, `clinica-payments-v2`, `tienda-payments`, `tienda-payments-v2`, `tienda-automation`, `academia-auth`, `academia-storage`, `academia-storage-v2`, `periodico-cms`, `periodico-cms-v2`, `periodico-analytics-v2`, `saas-largo-auth`, `saas-largo-auth-v2`, `rag-largo-auth`, `rag-largo-auth-v2`, `api-largo-database`, `saas-corto-auth`, `saas-corto-auth-v2`, `rag-corto-auth`, `rag-corto-auth-v2`, `none-inventario`, `none-videollamadas` |
| Umbral sugerido: resueltas bloqueadas (error grave) | 0/53: — |
| Umbral sugerido: sin respuesta que pasan | 22/40: `none-login`, `none-cms`, `clinica-auth`, `clinica-auth-v2`, `clinica-communication`, `clinica-communication-v2`, `clinica-payments`, `clinica-payments-v2`, `tienda-automation`, `academia-auth`, `periodico-cms-v2`, `periodico-analytics-v2`, `saas-largo-auth`, `saas-largo-auth-v2`, `rag-largo-auth`, `rag-largo-auth-v2`, `api-largo-database`, `saas-corto-auth`, `saas-corto-auth-v2`, `rag-corto-auth`, `rag-corto-auth-v2`, `none-videollamadas` |

Fallos de búsqueda (no cuentan para el umbral): `an-tableros`, `tienda-analytics`, `tienda-analytics-v2`, `logistica-database`, `logistica-database-v2`, `periodico-frontend-v2`, `rag-corto-ai-v2`
