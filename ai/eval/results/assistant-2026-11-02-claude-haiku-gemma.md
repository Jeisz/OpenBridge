# Comparación de modelos · flujo completo del asistente

Generado con `python -m ai.eval.run_assistant_eval` el 2026-11-02 a las 23:59. 5 casos × 1 corridas por proveedor; catálogo de 100 repos; umbral 0.2; el modelo ve 3 candidatos por necesidad y se registran 5. La llamada de calentamiento no se cuenta.

## Modelos

| Proveedor | Modelo | Razonamiento | Arranque en frío |
|---|---|---|---|
| claude-haiku | `claude-haiku-5-5` | por defecto | 5.4 s |
| gemma | `gemma-4-26b-a4b-it` | por defecto | 2.6 s |

## Resumen

| Métrica | claude-haiku | gemma |
|---|---|---|
| Status correcto | 100% | 50% |
| Respuesta válida | 100% | 50% |
| Necesidades detectadas | 100% | 0% |
| Techo de la búsqueda (top 3) | 100% | — |
| Techo con 5 candidatos | 100% | — |
| Eligió un aceptable (donde había) | 0% | — |
| Se abstuvo (donde no había) | 100% | — |
| Eligió el primer candidato | 100% | — |
| Consistencia entre corridas | — | — |
| Entender válido al 1.er intento | 100% | 50% |
| Generar válido al 1.er intento | 100% | — |
| Limitaciones repetidas | 0 | 0 |
| Ids en el texto | 0 | 0 |
| Errores del proveedor | 2/5 | 3/5 |
| Tiempo total (mediana) | 2.8 s | 7.5 s |
| Tiempo total (peor caso) | 16.6 s | 12.4 s |
| Sobre 15 s | 1/3 | 0/2 |
| Entender · buscar · generar (mediana) | 2.8 s · 0.1 s · 12.8 s | 7.5 s · 0.0 s · — |
| Tokens entrada / salida (mediana) | 3925 / 345 | 1891 / 81 |
| Esperas (límite de uso o error temporal) | 0.0 s | 0.0 s |

Evidencia direccional: 5 casos; los porcentajes no son estadística firme.

## Por necesidad

Cuenta sobre las corridas válidas: detectada · había un aceptable en el top 3 (techo) · eligió un aceptable. Sin aceptables, se espera que no elija nada.

| Caso · necesidad | Aceptables | claude-haiku | gemma |
|---|---|---|---|
| `logistica-flota` · messaging | kafka | det 0/0 · techo 0 · eligió 0 | det 0/0 · techo 0 · eligió 0 |
| `logistica-flota` · data-processing | flink, beam | det 0/0 · techo 0 · eligió 0 | det 0/0 · techo 0 · eligió 0 |
| `logistica-flota` · database | ClickHouse | det 0/0 · techo 0 · eligió 0 | det 0/0 · techo 0 · eligió 0 |
| `logistica-flota` · analytics | grafana | det 0/0 · techo 0 · eligió 0 | det 0/0 · techo 0 · eligió 0 |
| `pantalla-rag-corto` · ai | llama_index, langchain, ollama | det 0/0 · techo 0 · eligió 0 | det 0/1 · techo 0 · eligió 0 |
| `pantalla-rag-corto` · auth | (ninguno) | det 0/0 · eligió algo 0 | det 0/1 · eligió algo 0 |
| `pantalla-observabilidad` · observability | opentelemetry-collector, jaeger, prometheus | det 1/1 · techo 1 · eligió 0 | det 0/0 · techo 0 · eligió 0 |
| `una-pagos` · payments | (ninguno) | det 1/1 · eligió algo 0 | det 0/0 · eligió algo 0 |
| `vago-startup` · (vago) | — | status ok 1/1 | status ok 1/1 |

## Para revisar a mano (corrida 1)

Rúbrica de 1 a 3: español · `rationale` ligado al negocio · coherencia (título, resumen y cajas dicen lo mismo).

### `logistica-flota`

> Mi cliente es una empresa de logística con 200 camiones. Cada camión envía su ubicación cada pocos segundos; quieren procesar esos eventos en tiempo real, guardarlos y ver tableros de entregas por ciudad.

**claude-haiku**
- sin respuesta: LLMTimeout: claude-haiku: sin respuesta en 15 s

**gemma**
- sin respuesta: LLMTimeout: gemma: sin respuesta en 15 s

### `pantalla-rag-corto`

> Propón un RAG privado para consultar documentos con permisos de acceso.

**claude-haiku**
- sin respuesta: LLMTimeout: claude-haiku: sin respuesta en 15 s

**gemma**
- sin respuesta: None

### `pantalla-observabilidad`

> Define un stack de observabilidad con métricas, logs y trazas distribuidas para microservicios en Kubernetes.

**claude-haiku**
- `ok` · Grafana para visualizar métricas, logs y trazas de microservicios en Kubernetes
- La propuesta usa Grafana como pieza única de la necesidad de observabilidad, porque su descripción cubre métricas, logs y trazas desde varias fuentes. No recolecta ni almacena esos datos, así que el stack necesita fuentes de datos externas que el pedido no especifica. Ninguna necesidad quedó sin herramienta en el catálogo.
- **Grafana** (`grafana/grafana`), Visualización y consulta de métricas, logs y trazas: Su descripción indica que permite visualizar métricas, logs y trazas desde varias fuentes, como pidió el usuario. Su último cambio es reciente y su licencia es AGPL-3.0.
- Limitación: Grafana visualiza datos, pero no genera ni recolecta métricas, logs o trazas por sí mismo.
- Limitación: La propuesta no define cómo se almacenan ni retienen los datos de logs y trazas.
- Limitación: El catálogo no ofrece candidatos específicos para recolección o almacenamiento de telemetría, así que esas capas quedan sin concretar.
- Supuesto: Los microservicios se ejecutan en Kubernetes y se pueden instrumentar para emitir métricas, logs y trazas.
- Supuesto: El negocio necesita un único lugar para consultar la telemetría de todos los servicios.
- Supuesto: El pedido sugiere necesidades que no están en la lista: almacenamiento de métricas, logs y trazas, recolección de telemetría y alertas. Deben resolverse con herramientas adicionales.
- Supuesto: Se asume que el equipo puede operar un sistema con licencia AGPL-3.0 sin requerir cambios de licencia.
- Rúbrica: español _ · rationale _ · coherencia _

**gemma**
- sin respuesta: LLMTimeout: gemma: sin respuesta en 15 s

### `una-pagos`

> Necesito cobrar suscripciones mensuales a los clientes de mi software.

**claude-haiku**
- `no_evidence` · 
- El catálogo todavía no tiene herramientas para lo que pides: pagos.
- Limitación: Pagos: el catálogo no tiene herramientas para «cobros recurrentes de suscripciones mensuales».
- Rúbrica: español _ · rationale _ · coherencia _

**gemma**
- sin respuesta: LLMTimeout: gemma: sin respuesta en 15 s

### `vago-startup`

> Tengo una idea de startup y quiero saber qué tecnologías usar para empezar bien.

**claude-haiku**
- `needs_clarification` · 
- Necesito un poco más de contexto para recomendarte herramientas.
- Pregunta: ¿Qué problema resuelve tu startup y para quién es (clientes, empresas, dueños de negocios, otros)?
- Pregunta: ¿Qué debe poder hacer el usuario dentro de la aplicación, por ejemplo registrarse, pagar, buscar información, recibir mensajes o subir archivos?
- Pregunta: ¿Tienen equipo técnico y qué lenguajes o herramientas ya conocen, o empiezan desde cero?
- Rúbrica: español _ · rationale _ · coherencia _

**gemma**
- `needs_clarification` · 
- Necesito un poco más de contexto para recomendarte herramientas.
- Pregunta: ¿Qué problema quieres resolver con tu startup?
- Pregunta: ¿Qué funciones principales debe tener tu aplicación (por ejemplo, para cobrar, cobrar por suscripción, tener usuarios con roles y acceso controlado, o búsqueda de productos), para qué tipo de usuario final?
- Rúbrica: español _ · rationale _ · coherencia _
