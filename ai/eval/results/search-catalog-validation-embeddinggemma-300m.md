# Evaluación de la búsqueda · google/embeddinggemma-300m

Generado con `python -m ai.eval.run_search_eval --golden catalog-validation` el 2026-11-06. Golden set `catalog-validation` v1 · catálogo `snapshot` del 2026-10-29 · 100 repos · k = 3 · CPU · datos de la IA en el texto: summary, use_cases.

## Resumen

| Métrica | Valor |
|---|---|
| hit@3 | 19/20 (95%) |
| MRR@3 | 0.90 |
| recall@3 | 84% |
| hit@5 (con 5 candidatos por necesidad) | 20/20 (100%) |
| Carga del modelo + primera consulta | 6.5 s |
| Vectores del catálogo (100 repos) | 18.1 s |
| Consulta (promedio) | 0.06 s |

## Consultas con respuesta

| Consulta | Acierto | Posición de cada esperado | Top-3 (puntaje) |
|---|---|---|---|
| `cola-tareas` | ✅ | celery 1 | celery 0.478 · airflow 0.242 · prefect 0.239 |
| `transformacion-sql` | ✅ | dbt 2 | sqlmodel 0.340 · dbt 0.337 · sqlalchemy 0.336 |
| `db-embebida` | ✅ | duckdb 1 | duckdb 0.528 · ClickHouse 0.436 · dbt 0.419 |
| `clave-valor` | ✅ | etcd 1 | etcd 0.486 · redis 0.294 · celery 0.292 |
| `https-automatico` | ✅ | caddy 1 · traefik 4 | caddy 0.554 · cert-manager 0.423 · nginx 0.411 |
| `certificados-k8s` | ✅ | cert-manager 1 | cert-manager 0.676 · helm 0.449 · kubernetes 0.446 |
| `paquetes-k8s` | ✅ | helm 1 | helm 0.587 · kubernetes 0.554 · argo-cd 0.448 |
| `malla-servicios` | ✅ | istio 1 · envoy 4 | istio 0.424 · traefik 0.374 · jaeger 0.309 |
| `red-contenedores` | ✅ | cilium 2 · istio 5 | containerd 0.386 · cilium 0.370 · kubernetes 0.315 |
| `datos-tabulares` | ✅ | pandas 1 | pandas 0.479 · numpy 0.381 · sqlalchemy 0.370 |
| `redes-neuronales` | ✅ | pytorch 1 · tensorflow 2 | pytorch 0.467 · tensorflow 0.438 · transformers 0.326 |
| `ml-clasico` | ❌ | scikit-learn 4 | transformers 0.356 · tensorflow 0.344 · ollama 0.298 |
| `api-llm` | ✅ | anthropic-sdk-python 2 · openai-python 3 · langchain 1 | langchain 0.437 · anthropic-sdk-python 0.435 · openai-python 0.420 |
| `componentes-ui` | ✅ | react 1 · core 2 · svelte 5 | react 0.480 · core 0.453 · tailwindcss 0.430 |
| `estilos-ui` | ✅ | tailwindcss 1 | tailwindcss 0.490 · storybook 0.356 · react 0.330 |
| `multi-contenedor` | ✅ | compose 1 | compose 0.463 · containerd 0.435 · kubernetes 0.413 |
| `balanceo-carga` | ✅ | nginx 2 · traefik 1 · envoy 9 | traefik 0.406 · nginx 0.352 · cilium 0.251 |
| `metricas-servidores` | ✅ | prometheus 1 · opentelemetry-collector 2 | prometheus 0.423 · opentelemetry-collector 0.422 · jaeger 0.335 |
| `validacion-datos` | ✅ | pydantic 1 | pydantic 0.480 · TypeScript 0.296 · sqlmodel 0.258 |
| `pruebas-js` | ✅ | jest 1 · vitest 2 | jest 0.515 · vitest 0.435 · react-testing-library 0.427 |

## Consultas sin respuesta (el puntaje del 1.º sirve para el umbral)

| Consulta | Top-3 (puntaje) |
|---|---|
| `none-grafos` | etcd 0.351 · grafana 0.349 · ClickHouse 0.331 |
| `none-cdn` | etcd 0.334 · git 0.275 · astro 0.274 |
| `none-respaldos` | vault 0.267 · caddy 0.241 · terraform 0.209 |
| `none-objetos` | vault 0.299 · etcd 0.294 · nginx 0.260 |
| `none-push` | alertmanager 0.233 · prometheus 0.162 · celery 0.136 |
| `none-chat` | redis 0.248 · ClickHouse 0.237 · langchain 0.230 |
| `none-sms` | alertmanager 0.137 · jest 0.133 · envoy 0.122 |
| `none-aprobaciones` | flink 0.255 · flux2 0.249 · airflow 0.248 |
| `none-embudos` | dbt 0.255 · envoy 0.255 · svelte 0.231 |
| `none-sso` | traefik 0.261 · duckdb 0.248 · anthropic-sdk-python 0.246 |
| `none-facturacion-uso` | opentelemetry-collector 0.182 · traefik 0.177 · httpx 0.169 |
| `none-editor-paginas` | vscode 0.429 · neovim 0.382 · prettier 0.335 |
| `none-crm` | alertmanager 0.297 · cert-manager 0.231 · ClickHouse 0.222 |
| `none-agenda` | dagster 0.199 · jest 0.185 · biome 0.184 |
| `none-firma` | cert-manager 0.201 · ecma262 0.181 · etcd 0.164 |

## Umbral de `no_evidence`

Si el 1.er resultado de una necesidad puntúa menos que el umbral, se responde como sin evidencia. Para calcularlo solo cuentan las consultas con respuesta que la búsqueda resuelve (algún esperado en el top-3); las demás son fallos de búsqueda.

| | Valor |
|---|---|
| 1.er resultado, con respuesta resueltas (19) | 0.340 – 0.676 |
| 1.er resultado, con respuesta no resueltas (1) | 0.356 – 0.356 |
| 1.er resultado, sin respuesta (15) | 0.137 – 0.429 |
| Umbral actual del modelo | 0.23 |
| Umbral que sugiere la regla | **0.33** |
| Umbral actual: resueltas bloqueadas (error grave) | 0/19: — |
| Umbral actual: sin respuesta que pasan | 11/15: `none-grafos`, `none-cdn`, `none-respaldos`, `none-objetos`, `none-push`, `none-chat`, `none-aprobaciones`, `none-embudos`, `none-sso`, `none-editor-paginas`, `none-crm` |
| Umbral sugerido: resueltas bloqueadas (error grave) | 0/19: — |
| Umbral sugerido: sin respuesta que pasan | 3/15: `none-grafos`, `none-cdn`, `none-editor-paginas` |

Fallos de búsqueda (no cuentan para el umbral): `ml-clasico`
