# Evaluación de la búsqueda · google/embeddinggemma-300m

Generado con `python -m ai.eval.run_search_eval --golden catalog --texto base` el 2026-11-06. Golden set `catalog` v2 · catálogo `snapshot` del 2026-10-29 · 100 repos · k = 3 · CPU · datos de la IA en el texto: ninguno.

## Resumen

| Métrica | Valor |
|---|---|
| hit@3 | 48/60 (80%) |
| MRR@3 | 0.71 |
| recall@3 | 69% |
| hit@5 (con 5 candidatos por necesidad) | 53/60 (88%) |
| Carga del modelo + primera consulta | 5.4 s |
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
| `obs-stack` | ✅ | opentelemetry-collector 3 · prometheus 4 · grafana 1 | grafana 0.415 · traefik 0.379 · opentelemetry-collector 0.364 |
| `tienda-search` | ✅ | OpenSearch 3 | ripgrep 0.311 · pgvector 0.282 · OpenSearch 0.281 |
| `tienda-search-v2` | ✅ | OpenSearch 2 | ripgrep 0.341 · OpenSearch 0.320 · pgvector 0.316 |
| `tienda-analytics` | ❌ | grafana 6 | duckdb 0.225 · dbt 0.195 · ClickHouse 0.184 |
| `tienda-analytics-v2` | ❌ | grafana 5 | duckdb 0.227 · dbt 0.201 · ClickHouse 0.195 |
| `academia-ai` | ✅ | langchain 1 · llama_index 5 | langchain 0.274 · anthropic-sdk-python 0.268 · datasets 0.241 |
| `academia-ai-v2` | ✅ | langchain 2 · llama_index 7 | transformers 0.277 · langchain 0.266 · anthropic-sdk-python 0.264 |
| `logistica-messaging` | ✅ | kafka 1 · flink 6 · beam 2 | kafka 0.307 · beam 0.303 · airflow 0.272 |
| `logistica-messaging-v2` | ✅ | kafka 1 · flink 5 · beam 3 | kafka 0.308 · redis 0.296 · beam 0.294 |
| `logistica-database` | ❌ | ClickHouse 13 | etcd 0.214 · redis 0.198 · terraform 0.194 |
| `logistica-database-v2` | ❌ | ClickHouse 16 | redis 0.235 · etcd 0.234 · dagster 0.193 |
| `logistica-analytics` | ✅ | grafana 1 | grafana 0.306 · dbt 0.257 · storybook 0.207 |
| `logistica-analytics-v2` | ✅ | grafana 1 | grafana 0.301 · dbt 0.200 · pandas 0.196 |
| `soporte-ai` | ✅ | ollama 2 · vllm 1 | vllm 0.371 · ollama 0.318 · langchain 0.304 |
| `soporte-ai-v2` | ✅ | ollama 1 · vllm 4 | ollama 0.301 · anthropic-sdk-python 0.284 · langchain 0.280 |
| `soporte-search` | ✅ | OpenSearch 3 | llama_index 0.325 · ripgrep 0.319 · OpenSearch 0.285 |
| `soporte-search-v2` | ✅ | OpenSearch 1 | OpenSearch 0.282 · llama_index 0.239 · ripgrep 0.237 |
| `soporte-observability` | ✅ | grafana 2 · opentelemetry-collector 3 · prometheus 1 | prometheus 0.338 · grafana 0.313 · opentelemetry-collector 0.309 |
| `soporte-observability-v2` | ✅ | grafana 2 · opentelemetry-collector 3 · prometheus 1 | prometheus 0.326 · grafana 0.324 · opentelemetry-collector 0.319 |
| `periodico-frontend` | ❌ | nuxt 24 · next.js 16 · astro 5 | vite 0.326 · cypress 0.274 · svelte 0.270 |
| `periodico-frontend-v2` | ❌ | nuxt 22 · next.js 14 · astro 16 | vite 0.392 · tailwindcss 0.386 · react 0.385 |
| `rag-largo-ai` | ✅ | ollama 3 · vllm 2 | transformers 0.294 · vllm 0.261 · ollama 0.249 |
| `rag-largo-ai-v2` | ✅ | ollama 3 · vllm 1 | vllm 0.285 · transformers 0.275 · ollama 0.228 |
| `rag-largo-search` | ✅ | OpenSearch 3 · pgvector 1 | pgvector 0.381 · llama_index 0.278 · OpenSearch 0.267 |
| `rag-largo-search-v2` | ✅ | OpenSearch 3 · pgvector 1 | pgvector 0.424 · llama_index 0.293 · OpenSearch 0.285 |
| `api-largo-cache` | ✅ | redis 1 | redis 0.377 · etcd 0.288 · celery 0.202 |
| `api-largo-cache-v2` | ✅ | redis 1 | redis 0.385 · etcd 0.328 · celery 0.204 |
| `api-largo-infrastructure` | ❌ | kubernetes 9 · nginx 37 · traefik 27 | redis 0.279 · fastapi 0.251 · caddy 0.247 |
| `api-largo-infrastructure-v2` | ✅ | kubernetes 1 | kubernetes 0.361 · compose 0.330 · runc 0.307 |
| `rag-corto-ai` | ✅ | langchain 3 · llama_index 4 | vllm 0.223 · transformers 0.217 · langchain 0.211 |
| `rag-corto-ai-v2` | ❌ | langchain 5 · llama_index 10 | pytorch 0.178 · jaeger 0.172 · vllm 0.170 |
| `api-corto-cache` | ✅ | redis 1 | redis 0.196 · etcd 0.177 · pnpm 0.153 |
| `api-corto-cache-v2` | ✅ | redis 1 | redis 0.305 · etcd 0.193 · nginx 0.176 |
| `api-corto-infrastructure` | ✅ | kubernetes 1 | kubernetes 0.292 · containerd 0.264 · runc 0.244 |
| `api-corto-infrastructure-v2` | ❌ | kubernetes 10 · nginx 40 · traefik 11 | terraform 0.311 · ansible 0.214 · prefect 0.192 |
| `eventos-messaging` | ✅ | kafka 2 · celery 9 | beam 0.228 · kafka 0.223 · airflow 0.186 |
| `eventos-messaging-v2` | ✅ | kafka 7 · celery 1 | celery 0.253 · beam 0.247 · starlette 0.198 |
| `observabilidad-observability` | ✅ | opentelemetry-collector 2 · prometheus 3 · grafana 1 | grafana 0.492 · opentelemetry-collector 0.443 · prometheus 0.379 |
| `observabilidad-observability-v2` | ✅ | jaeger 4 · opentelemetry-collector 1 · prometheus 3 | opentelemetry-collector 0.435 · grafana 0.417 · prometheus 0.369 |
| `una-busqueda-search` | ✅ | OpenSearch 2 | ripgrep 0.329 · OpenSearch 0.305 · eslint 0.291 |
| `back-api` | ✅ | fastapi 3 · django 5 · flask 1 | flask 0.395 · openai-python 0.382 · fastapi 0.366 |
| `back-asgi` | ✅ | starlette 1 · fastapi 3 | starlette 0.416 · caddy 0.347 · fastapi 0.315 |
| `dev-lint-python` | ✅ | ruff 1 · black 3 | ruff 0.414 · cpython 0.412 · black 0.386 |
| `dev-lint-javascript` | ✅ | eslint 1 · biome 13 | eslint 0.477 · TypeScript 0.334 · vscode 0.305 |
| `dev-test-navegador` | ✅ | playwright 1 · cypress 2 | playwright 0.497 · cypress 0.395 · react-testing-library 0.327 |
| `dev-test-unitarias` | ✅ | pytest 1 | pytest 0.513 · cpython 0.340 · vitest 0.299 |
| `dev-dependencias` | ✅ | uv 1 | uv 0.371 · pnpm 0.368 · cpython 0.337 |
| `infra-despliegue-continuo` | ❌ | argo-cd 6 · flux2 4 | kubernetes 0.444 · containerd 0.444 · compose 0.406 |
| `infra-como-codigo` | ✅ | terraform 1 | terraform 0.533 · ansible 0.353 · traefik 0.314 |
| `auto-servidores` | ✅ | ansible 1 | ansible 0.409 · terraform 0.320 · cert-manager 0.288 |
| `obs-trazas` | ✅ | jaeger 1 · opentelemetry-collector 6 | jaeger 0.378 · grafana 0.253 · traefik 0.253 |
| `seguridad-secretos` | ✅ | vault 1 | vault 0.421 · cert-manager 0.323 · alertmanager 0.230 |
| `datos-lotes` | ✅ | spark 2 · beam 1 | beam 0.343 · spark 0.324 · flink 0.277 |
| `datos-orquestacion` | ✅ | airflow 2 · prefect 3 · dagster 1 | dagster 0.358 · airflow 0.349 · prefect 0.330 |
| `busqueda-vectorial` | ✅ | pgvector 1 · OpenSearch 5 | pgvector 0.494 · ripgrep 0.237 · redis 0.218 |

## Pares (deben dar resultados distintos)

| Par | Consulta | Top-3 |
|---|---|---|
| access | `clinica-auth` | vault 0.228 · cert-manager 0.194 · terraform 0.188 |
| access | `seguridad-secretos` | vault 0.421 · cert-manager 0.323 · alertmanager 0.230 |
| automation | `tienda-automation` | airflow 0.200 · ClickHouse 0.185 · ansible 0.180 |
| automation | `auto-servidores` | ansible 0.409 · terraform 0.320 · cert-manager 0.288 |
| lint | `dev-lint-python` | ruff 0.414 · cpython 0.412 · black 0.386 |
| lint | `dev-lint-javascript` | eslint 0.477 · TypeScript 0.334 · vscode 0.305 |
| tests | `dev-test-navegador` | playwright 0.497 · cypress 0.395 · react-testing-library 0.327 |
| tests | `dev-test-unitarias` | pytest 0.513 · cpython 0.340 · vitest 0.299 |

## Consultas sin respuesta (el puntaje del 1.º sirve para el umbral)

| Consulta | Top-3 (puntaje) |
|---|---|
| `none-pagos` | svelte 0.128 · opentelemetry-collector 0.127 · numpy 0.126 |
| `none-login` | react 0.153 · runc 0.133 · cypress 0.130 |
| `none-recordatorios` | alertmanager 0.178 · playwright 0.076 · jest 0.074 |
| `none-videos` | svelte 0.121 · vllm 0.113 · etcd 0.112 |
| `none-cms` | vscode 0.181 · git 0.177 · prettier 0.176 |
| `none-analitica-web` | grafana 0.194 · opentelemetry-collector 0.176 · prometheus 0.166 |
| `clinica-auth` | vault 0.228 · cert-manager 0.194 · terraform 0.188 |
| `clinica-auth-v2` | vault 0.231 · ansible 0.176 · terraform 0.174 |
| `clinica-communication` | alertmanager 0.180 · celery 0.133 · jaeger 0.124 |
| `clinica-communication-v2` | envoy 0.139 · anthropic-sdk-python 0.139 · svelte 0.113 |
| `clinica-payments` | beam 0.208 · prefect 0.163 · ecma262 0.158 |
| `clinica-payments-v2` | beam 0.197 · llama_index 0.163 · ecma262 0.160 |
| `tienda-payments` | caddy 0.097 · beam 0.091 · playwright 0.080 |
| `tienda-payments-v2` | playwright 0.125 · beam 0.120 · caddy 0.090 |
| `tienda-automation` | airflow 0.200 · ClickHouse 0.185 · ansible 0.180 |
| `academia-auth` | react 0.166 · svelte 0.149 · ansible 0.147 |
| `academia-storage` | etcd 0.137 · redis 0.121 · vscode 0.105 |
| `academia-storage-v2` | etcd 0.123 · nginx 0.110 · redis 0.109 |
| `academia-payments` | ripgrep 0.147 · alertmanager 0.141 · anthropic-sdk-python 0.127 |
| `academia-payments-v2` | opentelemetry-collector 0.145 · svelte 0.124 · numpy 0.123 |
| `periodico-cms` | vscode 0.205 · datasets 0.192 · astro 0.183 |
| `periodico-cms-v2` | astro 0.224 · pnpm 0.209 · vault 0.199 |
| `periodico-communication` | envoy 0.119 · alertmanager 0.090 · moby 0.083 |
| `periodico-communication-v2` | envoy 0.124 · nginx 0.086 · celery 0.073 |
| `periodico-analytics` | jest 0.090 · alertmanager 0.078 · grafana 0.077 |
| `periodico-analytics-v2` | duckdb 0.237 · astro 0.232 · scikit-learn 0.212 |
| `saas-largo-auth` | runc 0.248 · react 0.220 · traefik 0.214 |
| `saas-largo-auth-v2` | istio 0.188 · ansible 0.181 · flux2 0.176 |
| `rag-largo-auth` | vault 0.296 · ecma262 0.238 · llama_index 0.237 |
| `rag-largo-auth-v2` | cert-manager 0.283 · ecma262 0.259 · vault 0.245 |
| `api-largo-database` | sqlmodel 0.304 · ClickHouse 0.300 · sqlalchemy 0.289 |
| `saas-corto-auth` | vault 0.232 · ansible 0.231 · istio 0.201 |
| `saas-corto-auth-v2` | vault 0.271 · ansible 0.271 · cert-manager 0.263 |
| `rag-corto-auth` | vault 0.319 · istio 0.248 · cert-manager 0.210 |
| `rag-corto-auth-v2` | vault 0.342 · cert-manager 0.260 · alertmanager 0.240 |
| `una-pagos-payments` | ripgrep 0.152 · alertmanager 0.135 · anthropic-sdk-python 0.129 |
| `none-contabilidad` | pnpm 0.117 · cli 0.112 · alertmanager 0.111 |
| `none-inventario` | flux2 0.171 · ansible 0.161 · kubernetes 0.144 |
| `none-videollamadas` | playwright 0.256 · core 0.192 · cypress 0.186 |
| `none-factura-electronica` | vscode 0.137 · terraform 0.100 · ecma262 0.086 |

## Umbral de `no_evidence`

Si el 1.er resultado de una necesidad puntúa menos que el umbral, se responde como sin evidencia. Para calcularlo solo cuentan las consultas con respuesta que la búsqueda resuelve (algún esperado en el top-3); las demás son fallos de búsqueda.

| | Valor |
|---|---|
| 1.er resultado, con respuesta resueltas (48) | 0.196 – 0.533 |
| 1.er resultado, con respuesta no resueltas (12) | 0.146 – 0.444 |
| 1.er resultado, sin respuesta (40) | 0.090 – 0.342 |
| Umbral actual del modelo | 0.19 |
| Umbral que sugiere la regla | **0.19** |
| Umbral actual: resueltas bloqueadas (error grave) | 0/48: — |
| Umbral actual: sin respuesta que pasan | 18/40: `none-analitica-web`, `clinica-auth`, `clinica-auth-v2`, `clinica-payments`, `clinica-payments-v2`, `tienda-automation`, `periodico-cms`, `periodico-cms-v2`, `periodico-analytics-v2`, `saas-largo-auth`, `rag-largo-auth`, `rag-largo-auth-v2`, `api-largo-database`, `saas-corto-auth`, `saas-corto-auth-v2`, `rag-corto-auth`, `rag-corto-auth-v2`, `none-videollamadas` |

Fallos de búsqueda (no cuentan para el umbral): `proc-tiempo-real`, `an-tableros`, `tienda-analytics`, `tienda-analytics-v2`, `logistica-database`, `logistica-database-v2`, `periodico-frontend`, `periodico-frontend-v2`, `api-largo-infrastructure`, `rag-corto-ai-v2`, `api-corto-infrastructure-v2`, `infra-despliegue-continuo`
