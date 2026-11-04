# Comparación de modelos · flujo completo del asistente

Generado con `python -m ai.eval.run_assistant_eval` el 2026-11-03 a las 23:07. 5 casos × 3 corridas por proveedor; catálogo de 100 repos; umbral 0.19; el modelo ve 3 candidatos por necesidad y se registran 5. La llamada de calentamiento no se cuenta.

## Modelos

| Proveedor | Modelo | Razonamiento | Arranque en frío |
|---|---|---|---|
| gemini | `gemini-3.5-flash-lite` | por defecto | 3.4 s |

## Resumen

| Métrica | gemini |
|---|---|
| Status correcto | 100% |
| Respuesta válida | 100% |
| Necesidades detectadas | 83% |
| Techo de la búsqueda (top 3) | 67% |
| Techo con 5 candidatos | 80% |
| Eligió un aceptable (donde había) | 70% |
| Se abstuvo (donde no había) | 40% |
| Eligió el primer candidato | 31% |
| Consistencia entre corridas | 60% |
| Entender válido al 1.er intento | 100% |
| Generar válido al 1.er intento | 100% |
| Limitaciones repetidas | 0 |
| Ids en el texto | 0 |
| Errores del proveedor | 0/15 |
| Tiempo total (mediana) | 3.7 s |
| Tiempo total (peor caso) | 8.6 s |
| Sobre 15 s | 0/15 |
| Entender · buscar · generar (mediana) | 1.6 s · 0.1 s · 2.2 s |
| Tokens entrada / salida (mediana) | 3095 / 329 |
| Esperas (límite de uso o error temporal) | 0.0 s |

Evidencia direccional: 5 casos; los porcentajes no son estadística firme.

## Por necesidad

Cuenta sobre las corridas válidas: detectada · había un aceptable en el top 3 (techo) · eligió un aceptable. Sin aceptables, se espera que no elija nada.

| Caso · necesidad | Aceptables | gemini |
|---|---|---|
| `logistica-flota` · messaging | kafka | det 3/3 · techo 3 · eligió 3 |
| `logistica-flota` · data-processing | flink, beam | det 0/3 · techo 0 · eligió 0 |
| `logistica-flota` · database | ClickHouse | det 3/3 · techo 0 · eligió 0 |
| `logistica-flota` · analytics | grafana | det 3/3 · techo 2 · eligió 2 |
| `pantalla-rag-corto` · ai | llama_index, langchain, ollama | det 3/3 · techo 2 · eligió 2 |
| `pantalla-rag-corto` · auth | (ninguno) | det 2/3 · eligió algo 2 |
| `pantalla-observabilidad` · observability | opentelemetry-collector, jaeger, prometheus | det 3/3 · techo 3 · eligió 0 |
| `una-pagos` · payments | (ninguno) | det 3/3 · eligió algo 0 |
| `vago-startup` · (vago) | — | status ok 3/3 |

## Para revisar a mano (corrida 1)

Rúbrica de 1 a 3: español · `rationale` ligado al negocio · coherencia (título, resumen y cajas dicen lo mismo).

### `logistica-flota`

> Mi cliente es una empresa de logística con 200 camiones. Cada camión envía su ubicación cada pocos segundos; quieren procesar esos eventos en tiempo real, guardarlos y ver tableros de entregas por ciudad.

**gemini**
- `ok` · Arquitectura de streaming y analítica para logística
- Esta propuesta implementa una plataforma robusta para procesar en tiempo real la ubicación de los camiones, almacenar los eventos de forma persistente y visualizar tableros operativos de entregas por ciudad.
- **Kafka** (`apache/kafka`), Plataforma de streaming de eventos: Funciona como una plataforma de streaming de eventos distribuida para procesar en tiempo real las ubicaciones enviadas por los camiones.
- **DuckDB** (`duckdb/duckdb`), Base de datos analítica: Provee un sistema de base de datos analítica de alto rendimiento para guardar y consultar los datos de los eventos.
- **Grafana** (`grafana/grafana`), Plataforma de visualización: Permite visualizar métricas y crear tableros de control para ver las entregas por ciudad.
- Supuesto: La empresa cuenta con infraestructura propia o en la nube para desplegar los servicios seleccionados.
- Supuesto: Existe un conector o aplicación cliente en los camiones capaz de enviar solicitudes HTTP o TCP hacia el sistema de mensajería.
- Rúbrica: español _ · rationale _ · coherencia _

### `pantalla-rag-corto`

> Propón un RAG privado para consultar documentos con permisos de acceso.

**gemini**
- `ok` · Arquitectura de RAG Privado con Control de Acceso
- Esta propuesta implementa un sistema RAG privado combinando una plataforma de agentes y un motor de búsqueda vectorial para consultar documentos manteniendo la privacidad y los permisos de acceso requeridos.
- **LangChain** (`langchain-ai/langchain`), Plataforma de ingeniería de agentes: Permite construir la lógica de recuperación de información y generación aumentada conectando los modelos de lenguaje con la base de datos documental.
- **OpenSearch** (`opensearch-project/OpenSearch`), Motor de búsqueda distribuido: Proporciona capacidades de búsqueda avanzada y gestión de metadatos para implementar los permisos de acceso solicitados en los documentos. Su licencia es Apache-2.0.
- Limitación: La propuesta no incluye un motor de inferencia de LLM dedicado como vLLM, el cual complementaría la solución para optimizar el rendimiento del modelo.
- Supuesto: Se asume que el negocio cuenta con una infraestructura propia para desplegar los servicios de forma privada.
- Supuesto: Se asume que los documentos ya están procesados y almacenados con sus respectivos metadatos de permisos.
- Rúbrica: español _ · rationale _ · coherencia _

### `pantalla-observabilidad`

> Define un stack de observabilidad con métricas, logs y trazas distribuidas para microservicios en Kubernetes.

**gemini**
- `ok` · Stack de observabilidad para microservicios
- Propuesta de una plataforma centralizada para la visualización de métricas, logs y trazas en un entorno de Kubernetes. Se emplea Grafana como capa principal de análisis y tableros interactivos.
- **Grafana** (`grafana/grafana`), Visualización y análisis: Es la plataforma abierta y componible para visualización de datos que permite analizar métricas, logs y trazas de múltiples fuentes. Cuenta con licencia AGPL-3.0 y se mantiene activa.
- Limitación: OpenTelemetry Collector y Prometheus habrían complementado la recolección y el almacenamiento de datos, pero no se eligieron como herramientas principales en esta caja.
- Supuesto: Se asume que el despliegue se realizará sobre un clúster de Kubernetes existente.
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
- Pregunta: ¿Qué tipo de producto o aplicación web quieres construir?
- Pregunta: ¿Qué funcionalidades principales tendrá tu sistema en esta primera etapa?
- Pregunta: ¿Tienes alguna preferencia de lenguaje de programación o experiencia previa con alguna tecnología?
- Rúbrica: español _ · rationale _ · coherencia _
