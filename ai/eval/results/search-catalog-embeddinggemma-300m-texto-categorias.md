# Evaluación de la búsqueda · google/embeddinggemma-300m

Generado con `python -m ai.eval.run_search_eval --golden catalog --texto categorias` el 2026-11-06. Golden set `catalog` v2 · catálogo `snapshot` del 2026-10-29 · 100 repos · k = 3 · CPU · datos de la IA en el texto: categories.

## Resumen

| Métrica | Valor |
|---|---|
| hit@3 | 50/60 (83%) |
| MRR@3 | 0.76 |
| recall@3 | 68% |
| hit@5 (con 5 candidatos por necesidad) | 57/60 (95%) |
| Carga del modelo + primera consulta | 5.0 s |
| Vectores del catálogo (100 repos) | 13.0 s |
| Consulta (promedio) | 0.05 s |

## Consultas con respuesta

| Consulta | Acierto | Posición de cada esperado | Top-3 (puntaje) |
|---|---|---|---|
| `msg-eventos` | ✅ | kafka 1 | kafka 0.320 · flux2 0.319 · airflow 0.264 |
| `proc-tiempo-real` | ❌ | flink 5 · beam 4 | kafka 0.376 · dbt 0.353 · prefect 0.332 |
| `db-analitica` | ✅ | ClickHouse 1 · duckdb 6 | ClickHouse 0.305 · pandas 0.271 · redis 0.265 |
| `an-tableros` | ✅ | grafana 3 | jaeger 0.153 · etcd 0.150 · grafana 0.149 |
| `ai-rag` | ✅ | llama_index 2 · langchain 9 | ansible 0.238 · llama_index 0.234 · anthropic-sdk-python 0.228 |
| `obs-stack` | ✅ | opentelemetry-collector 2 · prometheus 4 · grafana 1 | grafana 0.478 · opentelemetry-collector 0.471 · jaeger 0.467 |
| `tienda-search` | ✅ | OpenSearch 1 | OpenSearch 0.367 · pgvector 0.344 · ripgrep 0.313 |
| `tienda-search-v2` | ✅ | OpenSearch 1 | OpenSearch 0.415 · pgvector 0.400 · ripgrep 0.359 |
| `tienda-analytics` | ❌ | grafana 4 | ClickHouse 0.298 · dbt 0.236 · pandas 0.219 |
| `tienda-analytics-v2` | ❌ | grafana 4 | ClickHouse 0.293 · dbt 0.221 · pandas 0.214 |
| `academia-ai` | ✅ | langchain 1 · llama_index 8 | langchain 0.338 · transformers 0.315 · vllm 0.311 |
| `academia-ai-v2` | ✅ | langchain 1 · llama_index 6 | langchain 0.338 · transformers 0.330 · vllm 0.313 |
| `logistica-messaging` | ✅ | kafka 1 · flink 3 · beam 5 | kafka 0.453 · airflow 0.404 · flink 0.400 |
| `logistica-messaging-v2` | ✅ | kafka 1 · flink 2 · beam 3 | kafka 0.437 · flink 0.416 · beam 0.392 |
| `logistica-database` | ❌ | ClickHouse 15 | redis 0.269 · etcd 0.239 · terraform 0.218 |
| `logistica-database-v2` | ❌ | ClickHouse 9 | redis 0.291 · etcd 0.277 · terraform 0.225 |
| `logistica-analytics` | ✅ | grafana 1 | grafana 0.321 · dbt 0.286 · ClickHouse 0.231 |
| `logistica-analytics-v2` | ✅ | grafana 1 | grafana 0.327 · dbt 0.250 · jaeger 0.237 |
| `soporte-ai` | ✅ | ollama 7 · vllm 1 | vllm 0.395 · starlette 0.353 · langchain 0.352 |
| `soporte-ai-v2` | ✅ | ollama 7 · vllm 2 | tensorflow 0.378 · vllm 0.375 · langchain 0.369 |
| `soporte-search` | ✅ | OpenSearch 1 | OpenSearch 0.407 · pgvector 0.393 · ripgrep 0.379 |
| `soporte-search-v2` | ✅ | OpenSearch 1 | OpenSearch 0.354 · pgvector 0.337 · ripgrep 0.298 |
| `soporte-observability` | ✅ | grafana 4 · opentelemetry-collector 3 · prometheus 1 | prometheus 0.407 · jaeger 0.401 · opentelemetry-collector 0.401 |
| `soporte-observability-v2` | ✅ | grafana 4 · opentelemetry-collector 3 · prometheus 2 | jaeger 0.400 · prometheus 0.399 · opentelemetry-collector 0.391 |
| `periodico-frontend` | ❌ | nuxt 13 · next.js 6 · astro 5 | vite 0.352 · tailwindcss 0.341 · svelte 0.335 |
| `periodico-frontend-v2` | ❌ | nuxt 10 · next.js 8 · astro 9 | tailwindcss 0.508 · svelte 0.498 · react 0.491 |
| `rag-largo-ai` | ✅ | ollama 5 · vllm 1 | vllm 0.310 · transformers 0.310 · langchain 0.304 |
| `rag-largo-ai-v2` | ✅ | ollama 6 · vllm 1 | vllm 0.384 · transformers 0.368 · tensorflow 0.348 |
| `rag-largo-search` | ✅ | OpenSearch 2 · pgvector 1 | pgvector 0.491 · OpenSearch 0.397 · ripgrep 0.339 |
| `rag-largo-search-v2` | ✅ | OpenSearch 2 · pgvector 1 | pgvector 0.515 · OpenSearch 0.405 · ripgrep 0.341 |
| `api-largo-cache` | ✅ | redis 1 | redis 0.457 · nginx 0.341 · etcd 0.294 |
| `api-largo-cache-v2` | ✅ | redis 1 | redis 0.471 · nginx 0.367 · etcd 0.336 |
| `api-largo-infrastructure` | ✅ | kubernetes 11 · nginx 2 · traefik 15 | caddy 0.318 · nginx 0.289 · ansible 0.286 |
| `api-largo-infrastructure-v2` | ✅ | kubernetes 1 | kubernetes 0.405 · containerd 0.384 · compose 0.378 |
| `rag-corto-ai` | ❌ | langchain 4 · llama_index 5 | transformers 0.264 · pytorch 0.263 · vllm 0.259 |
| `rag-corto-ai-v2` | ❌ | langchain 5 · llama_index 13 | pytorch 0.211 · transformers 0.205 · vllm 0.203 |
| `api-corto-cache` | ✅ | redis 1 | redis 0.316 · nginx 0.260 · etcd 0.180 |
| `api-corto-cache-v2` | ✅ | redis 1 | redis 0.428 · nginx 0.383 · etcd 0.207 |
| `api-corto-infrastructure` | ✅ | kubernetes 2 | containerd 0.300 · kubernetes 0.298 · runc 0.273 |
| `api-corto-infrastructure-v2` | ✅ | kubernetes 3 · nginx 9 · traefik 2 | terraform 0.390 · traefik 0.299 · kubernetes 0.298 |
| `eventos-messaging` | ✅ | kafka 1 · celery 8 | kafka 0.362 · beam 0.301 · airflow 0.300 |
| `eventos-messaging-v2` | ✅ | kafka 2 · celery 1 | celery 0.348 · kafka 0.343 · beam 0.333 |
| `observabilidad-observability` | ✅ | opentelemetry-collector 2 · prometheus 4 · grafana 1 | grafana 0.548 · opentelemetry-collector 0.535 · jaeger 0.480 |
| `observabilidad-observability-v2` | ✅ | jaeger 2 · opentelemetry-collector 1 · prometheus 4 | opentelemetry-collector 0.545 · jaeger 0.491 · grafana 0.488 |
| `una-busqueda-search` | ✅ | OpenSearch 1 | OpenSearch 0.386 · pgvector 0.345 · ripgrep 0.343 |
| `back-api` | ✅ | fastapi 5 · django 3 · flask 1 | flask 0.511 · httpx 0.482 · django 0.473 |
| `back-asgi` | ✅ | starlette 1 · fastapi 4 | starlette 0.451 · caddy 0.382 · nginx 0.369 |
| `dev-lint-python` | ✅ | ruff 2 · black 3 | cpython 0.480 · ruff 0.465 · black 0.437 |
| `dev-lint-javascript` | ✅ | eslint 1 · biome 15 | eslint 0.477 · jest 0.389 · TypeScript 0.374 |
| `dev-test-navegador` | ✅ | playwright 1 · cypress 2 | playwright 0.528 · cypress 0.386 · astro 0.371 |
| `dev-test-unitarias` | ✅ | pytest 1 | pytest 0.559 · cpython 0.463 · black 0.396 |
| `dev-dependencias` | ✅ | uv 1 | uv 0.374 · pnpm 0.363 · cpython 0.361 |
| `infra-despliegue-continuo` | ❌ | argo-cd 5 · flux2 6 | containerd 0.492 · kubernetes 0.457 · runc 0.421 |
| `infra-como-codigo` | ✅ | terraform 1 | terraform 0.608 · traefik 0.476 · envoy 0.463 |
| `auto-servidores` | ✅ | ansible 1 | ansible 0.472 · terraform 0.359 · flux2 0.355 |
| `obs-trazas` | ✅ | jaeger 1 · opentelemetry-collector 3 | jaeger 0.418 · grafana 0.309 · opentelemetry-collector 0.301 |
| `seguridad-secretos` | ✅ | vault 1 | vault 0.491 · cert-manager 0.354 · alertmanager 0.272 |
| `datos-lotes` | ✅ | spark 2 · beam 1 | beam 0.434 · spark 0.393 · flink 0.388 |
| `datos-orquestacion` | ✅ | airflow 1 · prefect 3 · dagster 2 | airflow 0.403 · dagster 0.394 · prefect 0.367 |
| `busqueda-vectorial` | ✅ | pgvector 1 · OpenSearch 4 | pgvector 0.518 · redis 0.287 · ripgrep 0.284 |

## Pares (deben dar resultados distintos)

| Par | Consulta | Top-3 |
|---|---|---|
| access | `clinica-auth` | vault 0.417 · cert-manager 0.229 · react 0.217 |
| access | `seguridad-secretos` | vault 0.491 · cert-manager 0.354 · alertmanager 0.272 |
| automation | `tienda-automation` | airflow 0.291 · prefect 0.247 · ansible 0.231 |
| automation | `auto-servidores` | ansible 0.472 · terraform 0.359 · flux2 0.355 |
| lint | `dev-lint-python` | cpython 0.480 · ruff 0.465 · black 0.437 |
| lint | `dev-lint-javascript` | eslint 0.477 · jest 0.389 · TypeScript 0.374 |
| tests | `dev-test-navegador` | playwright 0.528 · cypress 0.386 · astro 0.371 |
| tests | `dev-test-unitarias` | pytest 0.559 · cpython 0.463 · black 0.396 |

## Consultas sin respuesta (el puntaje del 1.º sirve para el umbral)

| Consulta | Top-3 (puntaje) |
|---|---|
| `none-pagos` | opentelemetry-collector 0.140 · ClickHouse 0.134 · numpy 0.130 |
| `none-login` | vault 0.320 · react 0.209 · svelte 0.190 |
| `none-recordatorios` | alertmanager 0.224 · celery 0.122 · kafka 0.109 |
| `none-videos` | pytorch 0.161 · django 0.146 · flask 0.131 |
| `none-cms` | prettier 0.265 · git 0.240 · pnpm 0.238 |
| `none-analitica-web` | grafana 0.227 · opentelemetry-collector 0.219 · jaeger 0.200 |
| `clinica-auth` | vault 0.417 · cert-manager 0.229 · react 0.217 |
| `clinica-auth-v2` | vault 0.350 · ClickHouse 0.198 · ansible 0.197 |
| `clinica-communication` | alertmanager 0.275 · jaeger 0.186 · celery 0.179 |
| `clinica-communication-v2` | kafka 0.251 · celery 0.217 · alertmanager 0.212 |
| `clinica-payments` | kafka 0.303 · beam 0.287 · prefect 0.277 |
| `clinica-payments-v2` | flink 0.305 · kafka 0.293 · scipy 0.272 |
| `tienda-payments` | dbt 0.186 · kafka 0.182 · flink 0.176 |
| `tienda-payments-v2` | kafka 0.205 · numpy 0.205 · flink 0.202 |
| `tienda-automation` | airflow 0.291 · prefect 0.247 · ansible 0.231 |
| `academia-auth` | vault 0.341 · react 0.217 · next.js 0.200 |
| `academia-storage` | redis 0.189 · nginx 0.185 · etcd 0.154 |
| `academia-storage-v2` | nginx 0.190 · redis 0.183 · etcd 0.140 |
| `academia-payments` | opentelemetry-collector 0.152 · prefect 0.143 · scipy 0.142 |
| `academia-payments-v2` | opentelemetry-collector 0.174 · ClickHouse 0.157 · sqlmodel 0.143 |
| `periodico-cms` | prettier 0.212 · pnpm 0.190 · datasets 0.187 |
| `periodico-cms-v2` | pnpm 0.240 · cli 0.215 · astro 0.211 |
| `periodico-communication` | kafka 0.180 · celery 0.130 · alertmanager 0.125 |
| `periodico-communication-v2` | kafka 0.169 · celery 0.128 · envoy 0.120 |
| `periodico-analytics` | opentelemetry-collector 0.149 · alertmanager 0.148 · jaeger 0.137 |
| `periodico-analytics-v2` | ClickHouse 0.323 · scipy 0.250 · duckdb 0.249 |
| `saas-largo-auth` | vault 0.365 · react 0.264 · runc 0.260 |
| `saas-largo-auth-v2` | vault 0.348 · flux2 0.238 · fastapi 0.217 |
| `rag-largo-auth` | vault 0.398 · cert-manager 0.238 · flux2 0.217 |
| `rag-largo-auth-v2` | vault 0.299 · cert-manager 0.276 · prefect 0.210 |
| `api-largo-database` | ClickHouse 0.344 · sqlmodel 0.342 · duckdb 0.333 |
| `saas-corto-auth` | vault 0.423 · ansible 0.258 · flux2 0.221 |
| `saas-corto-auth-v2` | vault 0.464 · cert-manager 0.306 · ansible 0.303 |
| `rag-corto-auth` | vault 0.486 · cert-manager 0.266 · istio 0.241 |
| `rag-corto-auth-v2` | vault 0.413 · cert-manager 0.265 · alertmanager 0.238 |
| `una-pagos-payments` | opentelemetry-collector 0.153 · prefect 0.143 · scipy 0.140 |
| `none-contabilidad` | pnpm 0.156 · cli 0.144 · alertmanager 0.142 |
| `none-inventario` | ansible 0.194 · prometheus 0.191 · opentelemetry-collector 0.190 |
| `none-videollamadas` | core 0.250 · playwright 0.235 · angular 0.216 |
| `none-factura-electronica` | ecma262 0.136 · dbt 0.125 · eslint 0.120 |

## Umbral de `no_evidence`

Si el 1.er resultado de una necesidad puntúa menos que el umbral, se responde como sin evidencia. Para calcularlo solo cuentan las consultas con respuesta que la búsqueda resuelve (algún esperado en el top-3); las demás son fallos de búsqueda.

| | Valor |
|---|---|
| 1.er resultado, con respuesta resueltas (50) | 0.153 – 0.608 |
| 1.er resultado, con respuesta no resueltas (10) | 0.211 – 0.508 |
| 1.er resultado, sin respuesta (40) | 0.136 – 0.486 |
| Umbral actual del modelo | 0.19 |
| Umbral que sugiere la regla | **0.15** |
| Umbral actual: resueltas bloqueadas (error grave) | 1/50: `an-tableros` |
| Umbral actual: sin respuesta que pasan | 28/40: `none-login`, `none-recordatorios`, `none-cms`, `none-analitica-web`, `clinica-auth`, `clinica-auth-v2`, `clinica-communication`, `clinica-communication-v2`, `clinica-payments`, `clinica-payments-v2`, `tienda-payments-v2`, `tienda-automation`, `academia-auth`, `academia-storage-v2`, `periodico-cms`, `periodico-cms-v2`, `periodico-analytics-v2`, `saas-largo-auth`, `saas-largo-auth-v2`, `rag-largo-auth`, `rag-largo-auth-v2`, `api-largo-database`, `saas-corto-auth`, `saas-corto-auth-v2`, `rag-corto-auth`, `rag-corto-auth-v2`, `none-inventario`, `none-videollamadas` |
| Umbral sugerido: resueltas bloqueadas (error grave) | 0/50: — |
| Umbral sugerido: sin respuesta que pasan | 37/40: `none-login`, `none-recordatorios`, `none-videos`, `none-cms`, `none-analitica-web`, `clinica-auth`, `clinica-auth-v2`, `clinica-communication`, `clinica-communication-v2`, `clinica-payments`, `clinica-payments-v2`, `tienda-payments`, `tienda-payments-v2`, `tienda-automation`, `academia-auth`, `academia-storage`, `academia-storage-v2`, `academia-payments`, `academia-payments-v2`, `periodico-cms`, `periodico-cms-v2`, `periodico-communication`, `periodico-communication-v2`, `periodico-analytics-v2`, `saas-largo-auth`, `saas-largo-auth-v2`, `rag-largo-auth`, `rag-largo-auth-v2`, `api-largo-database`, `saas-corto-auth`, `saas-corto-auth-v2`, `rag-corto-auth`, `rag-corto-auth-v2`, `una-pagos-payments`, `none-contabilidad`, `none-inventario`, `none-videollamadas` |

Fallos de búsqueda (no cuentan para el umbral): `proc-tiempo-real`, `tienda-analytics`, `tienda-analytics-v2`, `logistica-database`, `logistica-database-v2`, `periodico-frontend`, `periodico-frontend-v2`, `rag-corto-ai`, `rag-corto-ai-v2`, `infra-despliegue-continuo`
