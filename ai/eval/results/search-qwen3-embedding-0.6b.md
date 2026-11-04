# Evaluación de la búsqueda · Qwen/Qwen3-Embedding-0.6B

Generado con `python -m ai.eval.run_search_eval` el 2026-10-27. Golden set v2 · 20 repos · k = 3 · CPU.

## Resumen

| Métrica | Valor |
|---|---|
| hit@3 | 14/14 (100%) |
| MRR@3 | 0.92 |
| recall@3 | 89% |
| Carga del modelo + primera consulta | 6.5 s |
| Vectores del catálogo (20 repos) | 11.2 s |
| Consulta (promedio) | 0.20 s |

## Consultas con respuesta

| Consulta | Acierto | Posición de cada esperado | Top-3 (puntaje) |
|---|---|---|---|
| `auth-sso` | ✅ | keycloak 1 · zitadel 4 | keycloak 0.615 · kratos 0.571 · supertokens-core 0.533 |
| `auth-social` | ✅ | supertokens-core 1 · pocketbase 2 | supertokens-core 0.564 · pocketbase 0.541 · kratos 0.526 |
| `auth-passkeys` | ✅ | zitadel 5 · kratos 1 | kratos 0.560 · keycloak 0.548 · supertokens-core 0.540 |
| `pay-subs` | ✅ | killbill 2 · lago 1 | lago 0.632 · killbill 0.575 · hyperswitch 0.531 |
| `pay-usage` | ✅ | lago 1 | lago 0.687 · killbill 0.617 · hyperswitch 0.593 |
| `pay-gateways` | ✅ | hyperswitch 1 | hyperswitch 0.683 · killbill 0.519 · lago 0.517 |
| `an-web` | ✅ | analytics 1 · umami 4 | analytics 0.661 · posthog 0.475 · supertokens-core 0.469 |
| `an-product` | ✅ | posthog 2 | analytics 0.563 · posthog 0.555 · umami 0.511 |
| `an-bi` | ✅ | metabase 1 | metabase 0.589 · analytics 0.538 · lago 0.537 |
| `search-shop` | ✅ | meilisearch 2 · typesense 1 | typesense 0.659 · meilisearch 0.640 · qdrant 0.619 |
| `ai-docs` | ✅ | llama_index 1 · langchain 2 | llama_index 0.569 · langchain 0.557 · typesense 0.554 |
| `ai-local` | ✅ | ollama 3 | supabase 0.485 · pocketbase 0.478 · ollama 0.438 |
| `db-backend` | ✅ | supabase 2 · pocketbase 1 | pocketbase 0.619 · supabase 0.578 · redis 0.559 |
| `db-cache` | ✅ | redis 1 | redis 0.605 · pocketbase 0.540 · typesense 0.514 |

## Pares (deben dar resultados distintos)

| Par | Consulta | Top-3 |
|---|---|---|
| analytics | `an-web` | analytics 0.661 · posthog 0.475 · supertokens-core 0.469 |
| analytics | `an-product` | analytics 0.563 · posthog 0.555 · umami 0.511 |
| auth | `auth-sso` | keycloak 0.615 · kratos 0.571 · supertokens-core 0.533 |
| auth | `auth-social` | supertokens-core 0.564 · pocketbase 0.541 · kratos 0.526 |
| billing | `pay-subs` | lago 0.632 · killbill 0.575 · hyperswitch 0.531 |
| billing | `pay-usage` | lago 0.687 · killbill 0.617 · hyperswitch 0.593 |

## Consultas sin respuesta (el puntaje del 1.º sirve para el umbral)

| Consulta | 1.er resultado (puntaje) |
|---|---|
| `none-notify` | langchain 0.448 |
| `none-video` | analytics 0.439 |
| `none-agenda` | pocketbase 0.487 |
| `none-email` | analytics 0.453 |
| `none-accounting` | killbill 0.554 |
| `none-einvoice` | killbill 0.532 |
| `none-inventory` | pocketbase 0.505 |
| `none-videocall` | analytics 0.469 |

## Umbral de `no_evidence`

Sin calibrar para este modelo (`min_score = None`).
