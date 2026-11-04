# Evaluación de la búsqueda · Qwen/Qwen3-Embedding-0.6B

Generado con `python -m ai.eval.run_search_eval --golden catalog` el 2026-11-03. Golden set `catalog` v2 · catálogo `snapshot` del 2026-10-29 · 100 repos · k = 3 · CPU.

## Resumen

| Métrica | Valor |
|---|---|
| hit@3 | 45/60 (75%) |
| MRR@3 | 0.68 |
| recall@3 | 61% |
| hit@5 (con 5 candidatos por necesidad) | 52/60 (87%) |
| Carga del modelo + primera consulta | 7.4 s |
| Vectores del catálogo (100 repos) | 41.0 s |
| Consulta (promedio) | 0.33 s |

## Consultas con respuesta

| Consulta | Acierto | Posición de cada esperado | Top-3 (puntaje) |
|---|---|---|---|
| `msg-eventos` | ❌ | kafka 5 | flux2 0.491 · opentelemetry-collector 0.491 · airflow 0.490 |
| `proc-tiempo-real` | ❌ | flink 19 · beam 5 | prometheus 0.469 · grafana 0.462 · opentelemetry-collector 0.451 |
| `db-analitica` | ❌ | ClickHouse 10 · duckdb 19 | opentelemetry-collector 0.553 · grafana 0.551 · prometheus 0.537 |
| `an-tableros` | ❌ | grafana 4 | pgvector 0.518 · OpenSearch 0.503 · sqlmodel 0.477 |
| `ai-rag` | ✅ | llama_index 1 · langchain 3 | llama_index 0.544 · OpenSearch 0.529 · langchain 0.525 |
| `obs-stack` | ✅ | opentelemetry-collector 1 · prometheus 4 · grafana 2 | opentelemetry-collector 0.653 · grafana 0.602 · istio 0.543 |
| `tienda-search` | ✅ | OpenSearch 2 | ruff 0.511 · OpenSearch 0.495 · eslint 0.489 |
| `tienda-search-v2` | ✅ | OpenSearch 3 | ripgrep 0.543 · ruff 0.522 · OpenSearch 0.514 |
| `tienda-analytics` | ✅ | grafana 1 | grafana 0.541 · opentelemetry-collector 0.525 · prometheus 0.492 |
| `tienda-analytics-v2` | ✅ | grafana 1 | grafana 0.523 · opentelemetry-collector 0.519 · OpenSearch 0.510 |
| `academia-ai` | ✅ | langchain 1 · llama_index 6 | langchain 0.637 · ollama 0.614 · openai-python 0.611 |
| `academia-ai-v2` | ✅ | langchain 2 · llama_index 7 | ollama 0.650 · langchain 0.614 · transformers 0.608 |
| `logistica-messaging` | ✅ | kafka 3 · flink 5 · beam 2 | airflow 0.494 · beam 0.474 · kafka 0.472 |
| `logistica-messaging-v2` | ✅ | kafka 1 · flink 4 · beam 3 | kafka 0.471 · airflow 0.468 · beam 0.466 |
| `logistica-database` | ❌ | ClickHouse 25 | pgvector 0.532 · sqlmodel 0.468 · OpenSearch 0.450 |
| `logistica-database-v2` | ❌ | ClickHouse 19 | pgvector 0.504 · grafana 0.456 · OpenSearch 0.449 |
| `logistica-analytics` | ✅ | grafana 2 | sqlmodel 0.587 · grafana 0.584 · dagster 0.503 |
| `logistica-analytics-v2` | ✅ | grafana 1 | grafana 0.601 · pandas 0.524 · opentelemetry-collector 0.506 |
| `soporte-ai` | ✅ | ollama 2 · vllm 6 | sqlmodel 0.495 · ollama 0.429 · ruff 0.424 |
| `soporte-ai-v2` | ✅ | ollama 1 · vllm 4 | ollama 0.579 · datasets 0.577 · transformers 0.572 |
| `soporte-search` | ✅ | OpenSearch 1 | OpenSearch 0.651 · ripgrep 0.616 · pgvector 0.554 |
| `soporte-search-v2` | ✅ | OpenSearch 1 | OpenSearch 0.653 · ripgrep 0.552 · pgvector 0.528 |
| `soporte-observability` | ✅ | grafana 3 · opentelemetry-collector 1 · prometheus 2 | opentelemetry-collector 0.612 · prometheus 0.588 · grafana 0.586 |
| `soporte-observability-v2` | ✅ | grafana 2 · opentelemetry-collector 1 · prometheus 3 | opentelemetry-collector 0.633 · grafana 0.613 · prometheus 0.594 |
| `periodico-frontend` | ✅ | nuxt 15 · next.js 14 · astro 1 | astro 0.535 · caddy 0.506 · fastapi 0.502 |
| `periodico-frontend-v2` | ✅ | nuxt 29 · next.js 20 · astro 2 | fastapi 0.538 · astro 0.525 · flask 0.523 |
| `rag-largo-ai` | ✅ | ollama 4 · vllm 1 | vllm 0.487 · ruff 0.480 · sqlmodel 0.475 |
| `rag-largo-ai-v2` | ❌ | ollama 6 · vllm 5 | transformers 0.601 · datasets 0.569 · tensorflow 0.562 |
| `rag-largo-search` | ✅ | OpenSearch 2 · pgvector 1 | pgvector 0.548 · OpenSearch 0.539 · llama_index 0.483 |
| `rag-largo-search-v2` | ✅ | OpenSearch 2 · pgvector 1 | pgvector 0.598 · OpenSearch 0.556 · llama_index 0.508 |
| `api-largo-cache` | ✅ | redis 1 | redis 0.567 · etcd 0.467 · pgvector 0.463 |
| `api-largo-cache-v2` | ✅ | redis 1 | redis 0.552 · etcd 0.501 · vault 0.460 |
| `api-largo-infrastructure` | ❌ | kubernetes 27 · nginx 17 · traefik 29 | flux2 0.473 · airflow 0.454 · pgvector 0.444 |
| `api-largo-infrastructure-v2` | ❌ | kubernetes 4 | runc 0.660 · containerd 0.656 · compose 0.643 |
| `rag-corto-ai` | ❌ | langchain 7 · llama_index 8 | openai-python 0.644 · vllm 0.584 · ollama 0.576 |
| `rag-corto-ai-v2` | ❌ | langchain 8 · llama_index 6 | openai-python 0.596 · datasets 0.591 · vllm 0.564 |
| `api-corto-cache` | ✅ | redis 1 | redis 0.544 · vault 0.511 · OpenSearch 0.458 |
| `api-corto-cache-v2` | ✅ | redis 1 | redis 0.539 · vault 0.460 · OpenSearch 0.454 |
| `api-corto-infrastructure` | ❌ | kubernetes 4 | containerd 0.616 · runc 0.606 · compose 0.596 |
| `api-corto-infrastructure-v2` | ❌ | kubernetes 29 · nginx 22 · traefik 25 | airflow 0.504 · flux2 0.491 · dagster 0.469 |
| `eventos-messaging` | ✅ | kafka 17 · celery 1 | celery 0.451 · httpx 0.435 · airflow 0.435 |
| `eventos-messaging-v2` | ✅ | kafka 45 · celery 1 | celery 0.539 · airflow 0.460 · httpx 0.431 |
| `observabilidad-observability` | ✅ | opentelemetry-collector 1 · prometheus 3 · grafana 2 | opentelemetry-collector 0.692 · grafana 0.663 · prometheus 0.576 |
| `observabilidad-observability-v2` | ✅ | jaeger 10 · opentelemetry-collector 1 · prometheus 3 | opentelemetry-collector 0.673 · grafana 0.613 · prometheus 0.567 |
| `una-busqueda-search` | ❌ | OpenSearch 9 | ruff 0.536 · eslint 0.511 · black 0.506 |
| `back-api` | ✅ | fastapi 1 · django 8 · flask 2 | fastapi 0.726 · flask 0.614 · starlette 0.613 |
| `back-asgi` | ✅ | starlette 1 · fastapi 5 | starlette 0.537 · astro 0.490 · httpx 0.476 |
| `dev-lint-python` | ✅ | ruff 2 · black 1 | black 0.737 · ruff 0.733 · prettier 0.645 |
| `dev-lint-javascript` | ✅ | eslint 1 · biome 8 | eslint 0.759 · jest 0.622 · prettier 0.616 |
| `dev-test-navegador` | ✅ | playwright 1 · cypress 2 | playwright 0.672 · cypress 0.614 · jest 0.601 |
| `dev-test-unitarias` | ✅ | pytest 1 | pytest 0.707 · black 0.546 · ruff 0.535 |
| `dev-dependencias` | ✅ | uv 2 | pnpm 0.579 · uv 0.531 · scipy 0.498 |
| `infra-despliegue-continuo` | ❌ | argo-cd 7 · flux2 4 | containerd 0.608 · compose 0.578 · runc 0.573 |
| `infra-como-codigo` | ✅ | terraform 1 | terraform 0.608 · flux2 0.542 · airflow 0.538 |
| `auto-servidores` | ✅ | ansible 1 | ansible 0.537 · caddy 0.457 · runc 0.440 |
| `obs-trazas` | ✅ | jaeger 5 · opentelemetry-collector 1 | opentelemetry-collector 0.560 · grafana 0.523 · istio 0.519 |
| `seguridad-secretos` | ✅ | vault 1 | vault 0.678 · caddy 0.454 · cert-manager 0.446 |
| `datos-lotes` | ✅ | spark 1 · beam 4 | spark 0.572 · flink 0.511 · airflow 0.507 |
| `datos-orquestacion` | ✅ | airflow 1 · prefect 3 · dagster 2 | airflow 0.659 · dagster 0.622 · prefect 0.575 |
| `busqueda-vectorial` | ✅ | pgvector 1 · OpenSearch 2 | pgvector 0.726 · OpenSearch 0.584 · ripgrep 0.520 |

## Pares (deben dar resultados distintos)

| Par | Consulta | Top-3 |
|---|---|---|
| access | `clinica-auth` | vault 0.518 · sqlmodel 0.436 · containerd 0.406 |
| access | `seguridad-secretos` | vault 0.678 · caddy 0.454 · cert-manager 0.446 |
| automation | `tienda-automation` | sqlmodel 0.455 · pandas 0.454 · airflow 0.453 |
| automation | `auto-servidores` | ansible 0.537 · caddy 0.457 · runc 0.440 |
| lint | `dev-lint-python` | black 0.737 · ruff 0.733 · prettier 0.645 |
| lint | `dev-lint-javascript` | eslint 0.759 · jest 0.622 · prettier 0.616 |
| tests | `dev-test-navegador` | playwright 0.672 · cypress 0.614 · jest 0.601 |
| tests | `dev-test-unitarias` | pytest 0.707 · black 0.546 · ruff 0.535 |

## Consultas sin respuesta (el puntaje del 1.º sirve para el umbral)

| Consulta | Top-3 (puntaje) |
|---|---|
| `none-pagos` | vault 0.496 · alertmanager 0.486 · pnpm 0.486 |
| `none-login` | vault 0.502 · OpenSearch 0.472 · sqlmodel 0.468 |
| `none-recordatorios` | alertmanager 0.460 · opentelemetry-collector 0.434 · openai-python 0.434 |
| `none-videos` | vault 0.495 · caddy 0.467 · fastapi 0.458 |
| `none-cms` | prettier 0.508 · ruff 0.504 · black 0.503 |
| `none-analitica-web` | OpenSearch 0.638 · grafana 0.562 · opentelemetry-collector 0.544 |
| `clinica-auth` | vault 0.518 · sqlmodel 0.436 · containerd 0.406 |
| `clinica-auth-v2` | vault 0.501 · sqlmodel 0.452 · OpenSearch 0.420 |
| `clinica-communication` | alertmanager 0.515 · celery 0.452 · airflow 0.444 |
| `clinica-communication-v2` | alertmanager 0.529 · openai-python 0.486 · celery 0.474 |
| `clinica-payments` | airflow 0.413 · vault 0.411 · sqlmodel 0.410 |
| `clinica-payments-v2` | caddy 0.421 · airflow 0.409 · sqlmodel 0.386 |
| `tienda-payments` | psycopg 0.420 · vault 0.419 · fastapi 0.418 |
| `tienda-payments-v2` | vault 0.420 · sqlmodel 0.391 · psycopg 0.391 |
| `tienda-automation` | sqlmodel 0.455 · pandas 0.454 · airflow 0.453 |
| `academia-auth` | OpenSearch 0.485 · vault 0.482 · sqlmodel 0.470 |
| `academia-storage` | vault 0.523 · OpenSearch 0.458 · flux2 0.431 |
| `academia-storage-v2` | vault 0.491 · OpenSearch 0.472 · ripgrep 0.422 |
| `academia-payments` | alertmanager 0.467 · opentelemetry-collector 0.464 · flux2 0.461 |
| `academia-payments-v2` | pnpm 0.489 · alertmanager 0.476 · vault 0.468 |
| `periodico-cms` | OpenSearch 0.478 · prettier 0.452 · astro 0.446 |
| `periodico-cms-v2` | OpenSearch 0.490 · vault 0.449 · containerd 0.448 |
| `periodico-communication` | openai-python 0.475 · alertmanager 0.467 · vault 0.454 |
| `periodico-communication-v2` | alertmanager 0.479 · openai-python 0.459 · vault 0.457 |
| `periodico-analytics` | opentelemetry-collector 0.512 · OpenSearch 0.501 · ruff 0.491 |
| `periodico-analytics-v2` | OpenSearch 0.572 · opentelemetry-collector 0.569 · grafana 0.563 |
| `saas-largo-auth` | vault 0.492 · containerd 0.438 · fastapi 0.429 |
| `saas-largo-auth-v2` | vault 0.476 · flux2 0.422 · containerd 0.418 |
| `rag-largo-auth` | vault 0.496 · OpenSearch 0.422 · llama_index 0.412 |
| `rag-largo-auth-v2` | vault 0.471 · llama_index 0.423 · OpenSearch 0.419 |
| `api-largo-database` | sqlmodel 0.661 · psycopg 0.604 · sqlalchemy 0.577 |
| `saas-corto-auth` | vault 0.486 · sqlmodel 0.431 · fastapi 0.381 |
| `saas-corto-auth-v2` | vault 0.503 · sqlmodel 0.430 · openai-python 0.384 |
| `rag-corto-auth` | vault 0.554 · sqlmodel 0.429 · containerd 0.406 |
| `rag-corto-auth-v2` | vault 0.536 · OpenSearch 0.441 · sqlmodel 0.419 |
| `una-pagos-payments` | alertmanager 0.456 · flux2 0.450 · pnpm 0.443 |
| `none-contabilidad` | sqlmodel 0.465 · vault 0.460 · grafana 0.442 |
| `none-inventario` | vault 0.483 · pnpm 0.454 · OpenSearch 0.454 |
| `none-videollamadas` | vite 0.485 · angular 0.483 · OpenSearch 0.469 |
| `none-factura-electronica` | black 0.428 · vault 0.413 · sqlmodel 0.413 |

## Umbral de `no_evidence`

Si el 1.er resultado de una necesidad puntúa menos que el umbral, se responde como sin evidencia. Para calcularlo solo cuentan las consultas con respuesta que la búsqueda resuelve (algún esperado en el top-3); las demás son fallos de búsqueda.

| | Valor |
|---|---|
| 1.er resultado, con respuesta resueltas (45) | 0.451 – 0.759 |
| 1.er resultado, con respuesta no resueltas (15) | 0.469 – 0.660 |
| 1.er resultado, sin respuesta (40) | 0.413 – 0.661 |
| Umbral actual del modelo | sin calibrar |
| Umbral que sugiere la regla | **0.45** |
| Umbral sugerido: resueltas bloqueadas (error grave) | 0/45: — |
| Umbral sugerido: sin respuesta que pasan | 35/40: `none-pagos`, `none-login`, `none-recordatorios`, `none-videos`, `none-cms`, `none-analitica-web`, `clinica-auth`, `clinica-auth-v2`, `clinica-communication`, `clinica-communication-v2`, `tienda-automation`, `academia-auth`, `academia-storage`, `academia-storage-v2`, `academia-payments`, `academia-payments-v2`, `periodico-cms`, `periodico-cms-v2`, `periodico-communication`, `periodico-communication-v2`, `periodico-analytics`, `periodico-analytics-v2`, `saas-largo-auth`, `saas-largo-auth-v2`, `rag-largo-auth`, `rag-largo-auth-v2`, `api-largo-database`, `saas-corto-auth`, `saas-corto-auth-v2`, `rag-corto-auth`, `rag-corto-auth-v2`, `una-pagos-payments`, `none-contabilidad`, `none-inventario`, `none-videollamadas` |

Fallos de búsqueda (no cuentan para el umbral): `msg-eventos`, `proc-tiempo-real`, `db-analitica`, `an-tableros`, `logistica-database`, `logistica-database-v2`, `rag-largo-ai-v2`, `api-largo-infrastructure`, `api-largo-infrastructure-v2`, `rag-corto-ai`, `rag-corto-ai-v2`, `api-corto-infrastructure`, `api-corto-infrastructure-v2`, `una-busqueda-search`, `infra-despliegue-continuo`
