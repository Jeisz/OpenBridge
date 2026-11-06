# Evaluación de la búsqueda · google/embeddinggemma-300m

Generado con `python -m ai.eval.run_search_eval --golden catalog --texto resumen` el 2026-11-06. Golden set `catalog` v2 · catálogo `snapshot` del 2026-10-29 · 100 repos · k = 3 · CPU · datos de la IA en el texto: categories, summary.

## Resumen

| Métrica | Valor |
|---|---|
| hit@3 | 53/60 (88%) |
| MRR@3 | 0.76 |
| recall@3 | 72% |
| hit@5 (con 5 candidatos por necesidad) | 56/60 (93%) |
| Carga del modelo + primera consulta | 4.7 s |
| Vectores del catálogo (100 repos) | 16.8 s |
| Consulta (promedio) | 0.05 s |

## Consultas con respuesta

| Consulta | Acierto | Posición de cada esperado | Top-3 (puntaje) |
|---|---|---|---|
| `msg-eventos` | ✅ | kafka 1 | kafka 0.334 · flux2 0.330 · flink 0.289 |
| `proc-tiempo-real` | ✅ | flink 3 · beam 5 | kafka 0.374 · dbt 0.342 · flink 0.334 |
| `db-analitica` | ✅ | ClickHouse 1 · duckdb 14 | ClickHouse 0.310 · pandas 0.272 · redis 0.269 |
| `an-tableros` | ✅ | grafana 3 | jaeger 0.178 · celery 0.156 · grafana 0.152 |
| `ai-rag` | ✅ | llama_index 1 · langchain 7 | llama_index 0.242 · anthropic-sdk-python 0.239 · ansible 0.230 |
| `obs-stack` | ✅ | opentelemetry-collector 3 · prometheus 4 · grafana 2 | jaeger 0.497 · grafana 0.482 · opentelemetry-collector 0.466 |
| `tienda-search` | ✅ | OpenSearch 1 | OpenSearch 0.364 · pgvector 0.346 · ripgrep 0.328 |
| `tienda-search-v2` | ✅ | OpenSearch 1 | OpenSearch 0.409 · pgvector 0.393 · ripgrep 0.370 |
| `tienda-analytics` | ❌ | grafana 5 | ClickHouse 0.302 · dbt 0.247 · pandas 0.227 |
| `tienda-analytics-v2` | ❌ | grafana 6 | ClickHouse 0.292 · dbt 0.230 · pandas 0.219 |
| `academia-ai` | ✅ | langchain 1 · llama_index 8 | langchain 0.346 · ollama 0.331 · anthropic-sdk-python 0.328 |
| `academia-ai-v2` | ✅ | langchain 2 · llama_index 7 | transformers 0.352 · langchain 0.351 · ollama 0.339 |
| `logistica-messaging` | ✅ | kafka 1 · flink 2 · beam 4 | kafka 0.460 · flink 0.454 · airflow 0.420 |
| `logistica-messaging-v2` | ✅ | kafka 2 · flink 1 · beam 3 | flink 0.461 · kafka 0.444 · beam 0.408 |
| `logistica-database` | ❌ | ClickHouse 14 | redis 0.270 · etcd 0.242 · terraform 0.215 |
| `logistica-database-v2` | ❌ | ClickHouse 10 | redis 0.293 · etcd 0.280 · kafka 0.236 |
| `logistica-analytics` | ✅ | grafana 1 | grafana 0.326 · dbt 0.295 · jaeger 0.246 |
| `logistica-analytics-v2` | ✅ | grafana 1 | grafana 0.347 · dbt 0.261 · jaeger 0.245 |
| `soporte-ai` | ✅ | ollama 1 · vllm 2 | ollama 0.449 · vllm 0.414 · langchain 0.376 |
| `soporte-ai-v2` | ✅ | ollama 1 · vllm 3 | ollama 0.420 · tensorflow 0.379 · vllm 0.377 |
| `soporte-search` | ✅ | OpenSearch 1 | OpenSearch 0.400 · pgvector 0.386 · ripgrep 0.385 |
| `soporte-search-v2` | ✅ | OpenSearch 1 | OpenSearch 0.352 · pgvector 0.333 · ripgrep 0.310 |
| `soporte-observability` | ✅ | grafana 3 · opentelemetry-collector 4 · prometheus 2 | jaeger 0.412 · prometheus 0.408 · grafana 0.400 |
| `soporte-observability-v2` | ✅ | grafana 3 · opentelemetry-collector 4 · prometheus 2 | jaeger 0.417 · prometheus 0.397 · grafana 0.397 |
| `periodico-frontend` | ✅ | nuxt 11 · next.js 7 · astro 3 | vite 0.377 · tailwindcss 0.362 · astro 0.352 |
| `periodico-frontend-v2` | ❌ | nuxt 10 · next.js 8 · astro 9 | tailwindcss 0.523 · svelte 0.503 · react 0.503 |
| `rag-largo-ai` | ✅ | ollama 1 · vllm 3 | ollama 0.362 · transformers 0.339 · vllm 0.332 |
| `rag-largo-ai-v2` | ✅ | ollama 2 · vllm 3 | transformers 0.396 · ollama 0.391 · vllm 0.388 |
| `rag-largo-search` | ✅ | OpenSearch 2 · pgvector 1 | pgvector 0.478 · OpenSearch 0.394 · ripgrep 0.349 |
| `rag-largo-search-v2` | ✅ | OpenSearch 2 · pgvector 1 | pgvector 0.505 · OpenSearch 0.405 · ripgrep 0.351 |
| `api-largo-cache` | ✅ | redis 1 | redis 0.459 · nginx 0.334 · etcd 0.305 |
| `api-largo-cache-v2` | ✅ | redis 1 | redis 0.475 · nginx 0.358 · etcd 0.350 |
| `api-largo-infrastructure` | ✅ | kubernetes 3 · nginx 5 · traefik 13 | caddy 0.307 · istio 0.301 · kubernetes 0.298 |
| `api-largo-infrastructure-v2` | ✅ | kubernetes 1 | kubernetes 0.413 · containerd 0.399 · runc 0.373 |
| `rag-corto-ai` | ❌ | langchain 4 · llama_index 5 | transformers 0.289 · vllm 0.272 · pytorch 0.266 |
| `rag-corto-ai-v2` | ❌ | langchain 5 · llama_index 9 | transformers 0.236 · jaeger 0.218 · pytorch 0.215 |
| `api-corto-cache` | ✅ | redis 1 | redis 0.319 · nginx 0.244 · etcd 0.185 |
| `api-corto-cache-v2` | ✅ | redis 1 | redis 0.432 · nginx 0.375 · etcd 0.211 |
| `api-corto-infrastructure` | ✅ | kubernetes 2 | containerd 0.324 · kubernetes 0.317 · runc 0.283 |
| `api-corto-infrastructure-v2` | ✅ | kubernetes 2 · nginx 6 · traefik 3 | terraform 0.392 · kubernetes 0.302 · traefik 0.302 |
| `eventos-messaging` | ✅ | kafka 1 · celery 5 | kafka 0.360 · beam 0.311 · flink 0.308 |
| `eventos-messaging-v2` | ✅ | kafka 4 · celery 1 | celery 0.399 · beam 0.344 · flink 0.328 |
| `observabilidad-observability` | ✅ | opentelemetry-collector 2 · prometheus 4 · grafana 1 | grafana 0.556 · opentelemetry-collector 0.527 · jaeger 0.471 |
| `observabilidad-observability-v2` | ✅ | jaeger 3 · opentelemetry-collector 1 · prometheus 4 | opentelemetry-collector 0.533 · grafana 0.496 · jaeger 0.475 |
| `una-busqueda-search` | ✅ | OpenSearch 1 | OpenSearch 0.384 · ripgrep 0.354 · pgvector 0.348 |
| `back-api` | ✅ | fastapi 2 · django 3 · flask 1 | flask 0.517 · fastapi 0.513 · django 0.507 |
| `back-asgi` | ✅ | starlette 1 · fastapi 5 | starlette 0.511 · flask 0.409 · caddy 0.402 |
| `dev-lint-python` | ✅ | ruff 3 · black 2 | cpython 0.498 · black 0.498 · ruff 0.467 |
| `dev-lint-javascript` | ✅ | eslint 1 · biome 12 | eslint 0.482 · jest 0.410 · TypeScript 0.392 |
| `dev-test-navegador` | ✅ | playwright 1 · cypress 2 | playwright 0.545 · cypress 0.415 · jest 0.375 |
| `dev-test-unitarias` | ✅ | pytest 1 | pytest 0.576 · cpython 0.473 · black 0.429 |
| `dev-dependencias` | ✅ | uv 1 | uv 0.387 · pnpm 0.372 · sqlalchemy 0.360 |
| `infra-despliegue-continuo` | ✅ | argo-cd 5 · flux2 3 | containerd 0.497 · kubernetes 0.488 · flux2 0.442 |
| `infra-como-codigo` | ✅ | terraform 1 | terraform 0.608 · envoy 0.485 · istio 0.472 |
| `auto-servidores` | ✅ | ansible 1 | ansible 0.468 · flux2 0.357 · terraform 0.357 |
| `obs-trazas` | ✅ | jaeger 1 · opentelemetry-collector 4 | jaeger 0.468 · grafana 0.320 · traefik 0.317 |
| `seguridad-secretos` | ✅ | vault 1 | vault 0.506 · cert-manager 0.356 · alertmanager 0.309 |
| `datos-lotes` | ✅ | spark 3 · beam 1 | beam 0.466 · flink 0.406 · spark 0.392 |
| `datos-orquestacion` | ✅ | airflow 1 · prefect 3 · dagster 2 | airflow 0.426 · dagster 0.402 · prefect 0.387 |
| `busqueda-vectorial` | ✅ | pgvector 1 · OpenSearch 4 | pgvector 0.529 · ripgrep 0.293 · redis 0.293 |

## Pares (deben dar resultados distintos)

| Par | Consulta | Top-3 |
|---|---|---|
| access | `clinica-auth` | vault 0.395 · alertmanager 0.254 · cert-manager 0.245 |
| access | `seguridad-secretos` | vault 0.506 · cert-manager 0.356 · alertmanager 0.309 |
| automation | `tienda-automation` | airflow 0.292 · prefect 0.245 · ClickHouse 0.227 |
| automation | `auto-servidores` | ansible 0.468 · flux2 0.357 · terraform 0.357 |
| lint | `dev-lint-python` | cpython 0.498 · black 0.498 · ruff 0.467 |
| lint | `dev-lint-javascript` | eslint 0.482 · jest 0.410 · TypeScript 0.392 |
| tests | `dev-test-navegador` | playwright 0.545 · cypress 0.415 · jest 0.375 |
| tests | `dev-test-unitarias` | pytest 0.576 · cpython 0.473 · black 0.429 |

## Consultas sin respuesta (el puntaje del 1.º sirve para el umbral)

| Consulta | Top-3 (puntaje) |
|---|---|
| `none-pagos` | opentelemetry-collector 0.147 · ClickHouse 0.138 · jaeger 0.132 |
| `none-login` | vault 0.306 · react 0.218 · storybook 0.191 |
| `none-recordatorios` | alertmanager 0.238 · celery 0.129 · jest 0.111 |
| `none-videos` | django 0.136 · pytorch 0.135 · etcd 0.126 |
| `none-cms` | prettier 0.271 · vscode 0.250 · pnpm 0.246 |
| `none-analitica-web` | grafana 0.225 · opentelemetry-collector 0.204 · jaeger 0.193 |
| `clinica-auth` | vault 0.395 · alertmanager 0.254 · cert-manager 0.245 |
| `clinica-auth-v2` | vault 0.338 · alertmanager 0.244 · ClickHouse 0.224 |
| `clinica-communication` | alertmanager 0.274 · celery 0.191 · jaeger 0.189 |
| `clinica-communication-v2` | kafka 0.243 · alertmanager 0.239 · celery 0.234 |
| `clinica-payments` | kafka 0.295 · beam 0.288 · flink 0.277 |
| `clinica-payments-v2` | flink 0.314 · kafka 0.286 · beam 0.275 |
| `tienda-payments` | flink 0.192 · beam 0.182 · kafka 0.180 |
| `tienda-payments-v2` | flink 0.214 · kafka 0.207 · beam 0.203 |
| `tienda-automation` | airflow 0.292 · prefect 0.245 · ClickHouse 0.227 |
| `academia-auth` | vault 0.326 · react 0.228 · core 0.202 |
| `academia-storage` | redis 0.195 · nginx 0.177 · etcd 0.157 |
| `academia-storage-v2` | redis 0.188 · nginx 0.184 · etcd 0.143 |
| `academia-payments` | prefect 0.147 · opentelemetry-collector 0.145 · ripgrep 0.140 |
| `academia-payments-v2` | opentelemetry-collector 0.170 · ClickHouse 0.161 · prometheus 0.145 |
| `periodico-cms` | vscode 0.226 · prettier 0.215 · datasets 0.202 |
| `periodico-cms-v2` | pnpm 0.258 · cli 0.226 · astro 0.225 |
| `periodico-communication` | kafka 0.175 · alertmanager 0.168 · celery 0.145 |
| `periodico-communication-v2` | kafka 0.160 · celery 0.146 · alertmanager 0.116 |
| `periodico-analytics` | opentelemetry-collector 0.146 · grafana 0.142 · alertmanager 0.139 |
| `periodico-analytics-v2` | ClickHouse 0.317 · pandas 0.245 · astro 0.241 |
| `saas-largo-auth` | vault 0.355 · react 0.279 · next.js 0.265 |
| `saas-largo-auth-v2` | vault 0.354 · flux2 0.234 · ansible 0.214 |
| `rag-largo-auth` | vault 0.413 · cert-manager 0.254 · llama_index 0.211 |
| `rag-largo-auth-v2` | cert-manager 0.303 · vault 0.290 · alertmanager 0.229 |
| `api-largo-database` | ClickHouse 0.373 · sqlalchemy 0.371 · sqlmodel 0.368 |
| `saas-corto-auth` | vault 0.432 · ansible 0.256 · flux2 0.214 |
| `saas-corto-auth-v2` | vault 0.455 · cert-manager 0.318 · ansible 0.300 |
| `rag-corto-auth` | vault 0.491 · cert-manager 0.270 · alertmanager 0.259 |
| `rag-corto-auth-v2` | vault 0.420 · cert-manager 0.294 · alertmanager 0.281 |
| `una-pagos-payments` | opentelemetry-collector 0.149 · prefect 0.148 · jaeger 0.133 |
| `none-contabilidad` | pnpm 0.161 · alertmanager 0.150 · cli 0.145 |
| `none-inventario` | opentelemetry-collector 0.207 · vault 0.202 · flux2 0.198 |
| `none-videollamadas` | core 0.260 · playwright 0.252 · react 0.217 |
| `none-factura-electronica` | dbt 0.133 · jaeger 0.133 · ecma262 0.132 |

## Umbral de `no_evidence`

Si el 1.er resultado de una necesidad puntúa menos que el umbral, se responde como sin evidencia. Para calcularlo solo cuentan las consultas con respuesta que la búsqueda resuelve (algún esperado en el top-3); las demás son fallos de búsqueda.

| | Valor |
|---|---|
| 1.er resultado, con respuesta resueltas (53) | 0.178 – 0.608 |
| 1.er resultado, con respuesta no resueltas (7) | 0.236 – 0.523 |
| 1.er resultado, sin respuesta (40) | 0.133 – 0.491 |
| Umbral actual del modelo | 0.19 |
| Umbral que sugiere la regla | **0.17** |
| Umbral actual: resueltas bloqueadas (error grave) | 1/53: `an-tableros` |
| Umbral actual: sin respuesta que pasan | 29/40: `none-login`, `none-recordatorios`, `none-cms`, `none-analitica-web`, `clinica-auth`, `clinica-auth-v2`, `clinica-communication`, `clinica-communication-v2`, `clinica-payments`, `clinica-payments-v2`, `tienda-payments`, `tienda-payments-v2`, `tienda-automation`, `academia-auth`, `academia-storage`, `periodico-cms`, `periodico-cms-v2`, `periodico-analytics-v2`, `saas-largo-auth`, `saas-largo-auth-v2`, `rag-largo-auth`, `rag-largo-auth-v2`, `api-largo-database`, `saas-corto-auth`, `saas-corto-auth-v2`, `rag-corto-auth`, `rag-corto-auth-v2`, `none-inventario`, `none-videollamadas` |
| Umbral sugerido: resueltas bloqueadas (error grave) | 0/53: — |
| Umbral sugerido: sin respuesta que pasan | 32/40: `none-login`, `none-recordatorios`, `none-cms`, `none-analitica-web`, `clinica-auth`, `clinica-auth-v2`, `clinica-communication`, `clinica-communication-v2`, `clinica-payments`, `clinica-payments-v2`, `tienda-payments`, `tienda-payments-v2`, `tienda-automation`, `academia-auth`, `academia-storage`, `academia-storage-v2`, `academia-payments-v2`, `periodico-cms`, `periodico-cms-v2`, `periodico-communication`, `periodico-analytics-v2`, `saas-largo-auth`, `saas-largo-auth-v2`, `rag-largo-auth`, `rag-largo-auth-v2`, `api-largo-database`, `saas-corto-auth`, `saas-corto-auth-v2`, `rag-corto-auth`, `rag-corto-auth-v2`, `none-inventario`, `none-videollamadas` |

Fallos de búsqueda (no cuentan para el umbral): `tienda-analytics`, `tienda-analytics-v2`, `logistica-database`, `logistica-database-v2`, `periodico-frontend-v2`, `rag-corto-ai`, `rag-corto-ai-v2`
