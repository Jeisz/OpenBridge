# Comparación de modelos · flujo completo del asistente

Generado con `python -m ai.eval.run_assistant_eval` el 2026-11-04 a las 00:30. 5 casos × 3 corridas por proveedor; catálogo de 100 repos; umbral 0.19; el modelo ve 5 candidatos por necesidad y se registran 5. La llamada de calentamiento no se cuenta.

## Modelos

| Proveedor | Modelo | Razonamiento | Arranque en frío |
|---|---|---|---|
| gemini | `gemini-3.5-flash-lite` | por defecto | 1.7 s |

## Resumen

| Métrica | gemini |
|---|---|
| Status correcto | 100% |
| Respuesta válida | 100% |
| Necesidades detectadas | 90% |
| Techo de la búsqueda (top 5) | 83% |
| Techo con 5 candidatos | 83% |
| Eligió un aceptable (donde había) | 70% |
| Se abstuvo (donde no había) | 38% |
| Acierto de punta a punta (comparable entre k) | 58% |
| Sin caja donde el caso no tiene herramientas | 50% |
| Eligió el primer candidato | 27% |
| Consistencia entre corridas | 60% |
| Entender válido al 1.er intento | 100% |
| Generar válido al 1.er intento | 100% |
| Limitaciones repetidas | 0 |
| Ids en el texto | 0 |
| Errores del proveedor | 1/15 |
| Tiempo total (mediana) | 3.7 s |
| Tiempo total (peor caso) | 5.7 s |
| Sobre 15 s | 0/14 |
| Entender · buscar · generar (mediana) | 1.8 s · 0.1 s · 2.2 s |
| Tokens entrada / salida (mediana) | 3286 / 408 |
| Esperas (límite de uso o error temporal) | 0.0 s |

Evidencia direccional: 5 casos; los porcentajes no son estadística firme.

## Por necesidad

Cuenta sobre las corridas válidas: detectada · había un aceptable en el top 3 (techo) · eligió un aceptable. Sin aceptables, se espera que no elija nada.

| Caso · necesidad | Aceptables | gemini |
|---|---|---|
| `logistica-flota` · messaging | kafka | det 2/2 · techo 2 · eligió 2 |
| `logistica-flota` · data-processing | flink, beam | det 0/2 · techo 0 · eligió 0 |
| `logistica-flota` · database | ClickHouse | det 2/2 · techo 1 · eligió 1 |
| `logistica-flota` · analytics | grafana | det 2/2 · techo 1 · eligió 1 |
| `pantalla-rag-corto` · ai | llama_index, langchain, ollama | det 3/3 · techo 3 · eligió 3 |
| `pantalla-rag-corto` · auth | (ninguno) | det 3/3 · eligió algo 3 |
| `pantalla-observabilidad` · observability | opentelemetry-collector, jaeger, prometheus | det 3/3 · techo 3 · eligió 0 |
| `una-pagos` · payments | (ninguno) | det 3/3 · eligió algo 0 |
| `vago-startup` · (vago) | — | status ok 3/3 |

## Para revisar a mano (corrida 1)

Rúbrica de 1 a 3: español · `rationale` ligado al negocio · coherencia (título, resumen y cajas dicen lo mismo).

### `logistica-flota`

> Mi cliente es una empresa de logística con 200 camiones. Cada camión envía su ubicación cada pocos segundos; quieren procesar esos eventos en tiempo real, guardarlos y ver tableros de entregas por ciudad.

**gemini**
- sin respuesta: LLMTimeout: gemini: sin respuesta en 15.0 s

### `pantalla-rag-corto`

> Propón un RAG privado para consultar documentos con permisos de acceso.

**gemini**
- `ok` · Arquitectura de RAG privado con control de acceso
- Esta propuesta implementa un sistema RAG privado para procesar y consultar documentos mediante una plataforma especializada en IA, apoyada por un motor de búsqueda vectorial y un sistema de gestión de secretos y control de accesos.
- **LlamaIndex** (`run-llama/llama_index`), Plataforma de procesamiento de documentos para IA: LlamaIndex es la plataforma de procesamiento de documentos para IA bajo licencia MIT, ideal para construir la solución de recuperación de información aumentada que solicitaste.
- **Redis** (`redis/redis`), Motor de consulta vectorial y base de datos: Redis funciona como un servidor de estructuras de datos y motor de consulta vectorial para aplicaciones en tiempo real, aunque su licencia no fue identificada por GitHub.
- **Vault** (`hashicorp/vault`), Gestión de accesos y secretos: Vault es una herramienta para la gestión de secretos y control de acceso privilegiado, aunque su licencia no fue identificada por GitHub.
- Limitación: La propuesta no incluye un motor de inferencia de modelos de lenguaje dedicado como vLLM u Ollama para ejecutar los modelos localmente.
- Supuesto: Se asume que el almacenamiento de documentos y la interfaz de usuario se integrarán sobre los componentes seleccionados.
- Rúbrica: español _ · rationale _ · coherencia _

### `pantalla-observabilidad`

> Define un stack de observabilidad con métricas, logs y trazas distribuidas para microservicios en Kubernetes.

**gemini**
- `ok` · Stack de Observabilidad e Infraestructura para Microservicios
- Esta propuesta implementa un entorno robusto utilizando Kubernetes para la gestión de contenedores y Grafana para la visualización integral de métricas, logs y trazas distribuidas.
- **Grafana** (`grafana/grafana`), Visualización y análisis de datos de observabilidad: Grafana permite visualizar métricas, logs y trazas distribuidas desde múltiples fuentes para cumplir con los requerimientos de observabilidad del sistema.
- **Kubernetes** (`kubernetes/kubernetes`), Orquestación y gestión de contenedores: Kubernetes provee la programación y gestión de contenedores a nivel de producción necesaria para los microservicios solicitados.
- Limitación: La solución elegida en Grafana se complementaría idealmente con Prometheus, Jaeger y OpenTelemetry Collector para la captura y almacenamiento de los datos.
- Supuesto: Se asume que los microservicios ya se encuentran instrumentados para exportar métricas, logs y trazas.
- Supuesto: Se requiere un almacenamiento de series temporales y motores de almacenamiento de logs complementarios para el correcto funcionamiento de la plataforma de visualización.
- Rúbrica: español _ · rationale _ · coherencia _

### `una-pagos`

> Necesito cobrar suscripciones mensuales a los clientes de mi software.

**gemini**
- `no_evidence` · 
- El catálogo todavía no tiene herramientas para lo que pides: pagos.
- Limitación: Pagos: el catálogo no tiene herramientas para «cobro de suscripciones recurrentes».
- Rúbrica: español _ · rationale _ · coherencia _

### `vago-startup`

> Tengo una idea de startup y quiero saber qué tecnologías usar para empezar bien.

**gemini**
- `needs_clarification` · 
- Necesito un poco más de contexto para recomendarte herramientas.
- Pregunta: ¿Qué tipo de producto o aplicación quieres construir para tu startup?
- Pregunta: ¿Qué funcionalidades principales tendrá tu sistema en su primera versión?
- Pregunta: ¿Tienes alguna preferencia de lenguaje de programación o experiencia previa con alguna tecnología?
- Rúbrica: español _ · rationale _ · coherencia _
