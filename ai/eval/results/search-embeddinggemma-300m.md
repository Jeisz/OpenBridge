# Evaluación de la búsqueda · google/embeddinggemma-300m

Generado con `python -m ai.eval.run_search_eval` el 2026-10-30. Golden set v2 · 20 repos · k = 3 · CPU.

## Resumen

| Métrica | Valor |
|---|---|
| hit@3 | 14/14 (100%) |
| MRR@3 | 0.79 |
| recall@3 | 93% |
| Carga del modelo + primera consulta | 5.4 s |
| Vectores del catálogo (20 repos) | 4.2 s |
| Consulta (promedio) | 0.05 s |

## Consultas con respuesta

| Consulta | Acierto | Posición de cada esperado | Top-3 (puntaje) |
|---|---|---|---|
| `auth-sso` | ✅ | keycloak 1 · zitadel 2 | keycloak 0.446 · zitadel 0.398 · kratos 0.371 |
| `auth-social` | ✅ | supertokens-core 2 · pocketbase 3 | kratos 0.318 · supertokens-core 0.311 · pocketbase 0.301 |
| `auth-passkeys` | ✅ | zitadel 4 · kratos 3 | supertokens-core 0.403 · keycloak 0.352 · kratos 0.348 |
| `pay-subs` | ✅ | killbill 1 · lago 2 | killbill 0.419 · lago 0.403 · hyperswitch 0.269 |
| `pay-usage` | ✅ | lago 1 | lago 0.513 · killbill 0.402 · hyperswitch 0.352 |
| `pay-gateways` | ✅ | hyperswitch 1 | hyperswitch 0.544 · lago 0.346 · killbill 0.330 |
| `an-web` | ✅ | analytics 1 · umami 2 | analytics 0.441 · umami 0.396 · metabase 0.250 |
| `an-product` | ✅ | posthog 3 | umami 0.358 · analytics 0.343 · posthog 0.337 |
| `an-bi` | ✅ | metabase 3 | lago 0.201 · analytics 0.190 · metabase 0.181 |
| `search-shop` | ✅ | meilisearch 2 · typesense 1 | typesense 0.453 · meilisearch 0.426 · qdrant 0.365 |
| `ai-docs` | ✅ | llama_index 1 · langchain 5 | llama_index 0.336 · meilisearch 0.309 · qdrant 0.308 |
| `ai-local` | ✅ | ollama 2 | langchain 0.379 · ollama 0.344 · supabase 0.321 |
| `db-backend` | ✅ | supabase 2 · pocketbase 1 | pocketbase 0.549 · supabase 0.519 · redis 0.401 |
| `db-cache` | ✅ | redis 1 | redis 0.411 · typesense 0.210 · meilisearch 0.199 |

## Pares (deben dar resultados distintos)

| Par | Consulta | Top-3 |
|---|---|---|
| analytics | `an-web` | analytics 0.441 · umami 0.396 · metabase 0.250 |
| analytics | `an-product` | umami 0.358 · analytics 0.343 · posthog 0.337 |
| auth | `auth-sso` | keycloak 0.446 · zitadel 0.398 · kratos 0.371 |
| auth | `auth-social` | kratos 0.318 · supertokens-core 0.311 · pocketbase 0.301 |
| billing | `pay-subs` | killbill 0.419 · lago 0.403 · hyperswitch 0.269 |
| billing | `pay-usage` | lago 0.513 · killbill 0.402 · hyperswitch 0.352 |

## Consultas sin respuesta (el puntaje del 1.º sirve para el umbral)

| Consulta | 1.er resultado (puntaje) |
|---|---|
| `none-notify` | analytics 0.144 |
| `none-video` | umami 0.126 |
| `none-agenda` | lago 0.147 |
| `none-email` | umami 0.148 |
| `none-accounting` | lago 0.187 |
| `none-einvoice` | killbill 0.180 |
| `none-inventory` | metabase 0.209 |
| `none-videocall` | killbill 0.215 |

## Umbral de `no_evidence`

Umbral: **0.200**. Si el 1.er resultado puntúa menos, la necesidad se responde como sin evidencia.

| | Valor |
|---|---|
| 1.er resultado, consultas con respuesta | 0.201 – 0.549 |
| 1.er resultado, consultas sin respuesta | 0.126 – 0.215 |
| Con respuesta bloqueadas (error grave) | 0/14: — |
| Sin respuesta que pasan (las puede frenar el LLM) | 2/8: `none-inventory`, `none-videocall` |
