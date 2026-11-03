# Comparación de modelos · flujo completo del asistente

Generado con `python -m ai.eval.run_assistant_eval` el 2026-11-02 a las 23:21. 5 casos × 3 corridas por proveedor; catálogo de 100 repos; umbral 0.2; el modelo ve 3 candidatos por necesidad y se registran 5. La llamada de calentamiento no se cuenta.

## Modelos

| Proveedor | Modelo | Razonamiento | Arranque en frío |
|---|---|---|---|
| groq-low | `openai/gpt-oss-120b` | low | 0.9 s |

## Resumen

| Métrica | groq-low |
|---|---|
| Status correcto | 100% |
| Respuesta válida | 100% |
| Necesidades detectadas | 78% |
| Techo de la búsqueda (top 3) | 70% |
| Techo con 5 candidatos | 70% |
| Eligió un aceptable (donde había) | 57% |
| Se abstuvo (donde no había) | 43% |
| Eligió el primer candidato | 82% |
| Consistencia entre corridas | 50% |
| Entender válido al 1.er intento | 100% |
| Generar válido al 1.er intento | 89% |
| Limitaciones repetidas | 0 |
| Ids en el texto | 0 |
| Errores del proveedor | 3/15 |
| Tiempo total (mediana) | 2.7 s |
| Tiempo total (peor caso) | 6.4 s |
| Sobre 15 s | 0/12 |
| Entender · buscar · generar (mediana) | 0.9 s · 0.1 s · 1.7 s |
| Tokens entrada / salida (mediana) | 3442 / 456 |
| Esperas (límite de uso o error temporal) | 0.0 s |

Evidencia direccional: 5 casos; los porcentajes no son estadística firme.

## Por necesidad

Cuenta sobre las corridas válidas: detectada · había un aceptable en el top 3 (techo) · eligió un aceptable. Sin aceptables, se espera que no elija nada.

| Caso · necesidad | Aceptables | groq-low |
|---|---|---|
| `logistica-flota` · messaging | kafka | det 2/2 · techo 1 · eligió 1 |
| `logistica-flota` · data-processing | flink, beam | det 1/2 · techo 1 · eligió 1 |
| `logistica-flota` · database | ClickHouse | det 2/2 · techo 0 · eligió 0 |
| `logistica-flota` · analytics | grafana | det 2/2 · techo 2 · eligió 2 |
| `pantalla-rag-corto` · ai | llama_index, langchain, ollama | det 0/3 · techo 0 · eligió 0 |
| `pantalla-rag-corto` · auth | (ninguno) | det 3/3 · eligió algo 2 |
| `pantalla-observabilidad` · observability | opentelemetry-collector, jaeger, prometheus | det 3/3 · techo 3 · eligió 0 |
| `una-pagos` · payments | (ninguno) | det 1/1 · eligió algo 0 |
| `vago-startup` · (vago) | — | status ok 3/3 |

## Para revisar a mano (corrida 1)

Rúbrica de 1 a 3: español · `rationale` ligado al negocio · coherencia (título, resumen y cajas dicen lo mismo).

### `logistica-flota`

> Mi cliente es una empresa de logística con 200 camiones. Cada camión envía su ubicación cada pocos segundos; quieren procesar esos eventos en tiempo real, guardarlos y ver tableros de entregas por ciudad.

**groq-low**
- `ok` · Arquitectura de procesamiento en tiempo real para rastreo de camiones
- Se propone usar Apache Kafka como bus de mensajería para ingerir ubicaciones de los camiones en tiempo real, y Grafana para visualizar tableros de entregas por ciudad. No se encontró una base de datos adecuada en el catálogo para almacenar los datos de ubicación, por lo que esa necesidad queda sin herramienta asignada. Se asume que se integrará una base de datos de series temporales externa (por ejemplo, InfluxDB o ClickHouse) que Grafana pueda consultar.
- **Kafka** (`apache/kafka`), Ingesta y distribución de eventos de ubicación en tiempo real: Kafka es una plataforma de streaming distribuida que permite procesar los mensajes de ubicación de los camiones en tiempo real, garantizando alta disponibilidad y escalabilidad.
- **Grafana** (`grafana/grafana`), Visualización de tableros de entregas por ciudad: Grafana permite crear dashboards interactivos que pueden consultar los datos de ubicación almacenados y mostrarlos por ciudad.
- Limitación: Bases de datos: ninguna herramienta del catálogo encaja. Ningún candidato del catálogo (etcd) es adecuado para almacenar grandes volúmenes de datos de ubicación; se requiere una base de datos de series temporales externa.
- Limitación: El catálogo no incluye una base de datos especializada en series temporales; por eso la necesidad de almacenamiento queda sin herramienta asignada.
- Supuesto: Se dispone de una base de datos de series temporales o relacional externa para almacenar los eventos de ubicación.
- Supuesto: Los camiones pueden enviar datos a través de protocolos compatibles con Kafka (por ejemplo, MQTT a un conector).
- Supuesto: Grafana podrá conectarse a la base de datos elegida mediante sus plugins nativos.
- Rúbrica: español _ · rationale _ · coherencia _

### `pantalla-rag-corto`

> Propón un RAG privado para consultar documentos con permisos de acceso.

**groq-low**
- `ok` · RAG privado con búsqueda semántica y control de acceso
- Se propone un sistema RAG privado que combina pgvector para búsqueda semántica en Postgres, HashiCorp Vault para gestión de permisos y autenticación, y LlamaIndex para ingestión y almacenamiento de documentos. El flujo permite consultar documentos bajo control de acceso, garantizando privacidad y escalabilidad.
- **pgvector** (`pgvector/pgvector`), Búsqueda semántica de vectores sobre Postgres: Proporciona búsqueda por similitud de vectores dentro de una base PostgreSQL, lo que permite un RAG privado sin depender de servicios externos.
- **Vault** (`hashicorp/vault`), Gestión de secretos y control de acceso a recursos: Ofrece control de acceso basado en políticas y gestión segura de credenciales, adecuado para proteger el acceso a los documentos.
- **LlamaIndex** (`run-llama/llama_index`), Ingesta y almacenamiento de documentos para IA: Permite cargar, indexar y almacenar documentos de forma estructurada, listo para ser consultado por el motor de búsqueda.
- Supuesto: Se dispone de una base PostgreSQL para alojar pgvector.
- Supuesto: Los documentos se pueden representar como embeddings vectoriales.
- Supuesto: Los usuarios acceden al sistema mediante una capa API que valida tokens de Vault.
- Rúbrica: español _ · rationale _ · coherencia _

### `pantalla-observabilidad`

> Define un stack de observabilidad con métricas, logs y trazas distribuidas para microservicios en Kubernetes.

**groq-low**
- `ok` · Stack de observabilidad unificado para Kubernetes
- Se propone usar Grafana como plataforma central para métricas, logs y trazas distribuidas en microservicios sobre Kubernetes. La herramienta cubre toda la necesidad de observabilidad y está activamente mantenida bajo licencia AGPL‑3.0. No se requieren componentes adicionales dentro del modelo propuesto.
- **Grafana** (`grafana/grafana`), visualización y correlación de métricas, logs y trazas: Grafana permite visualizar métricas, logs y trazas de fuentes como Prometheus y OpenTelemetry, cubriendo la necesidad completa del usuario de un stack de observabilidad en Kubernetes.
- Rúbrica: español _ · rationale _ · coherencia _

### `una-pagos`

> Necesito cobrar suscripciones mensuales a los clientes de mi software.

**groq-low**
- `no_evidence` · Propuesta de cobro de suscripciones mensuales
- El usuario requiere una solución para cobrar suscripciones mensuales, pero ninguno de los candidatos disponibles en el catálogo ofrece funcionalidades de gestión de pagos. Por ello, se indica que no hay herramienta adecuada en la lista proporcionada.
- Limitación: Pagos: ninguna herramienta del catálogo encaja. Ninguno de los candidatos disponibles (Alertmanager, pnpm, cert-manager) ofrece funcionalidades de gestión de pagos o suscripciones, por lo que no pueden cubrir la necesidad del usuario.
- Limitación: Ninguno de los candidatos (Alertmanager, pnpm, cert-manager) está relacionado con pagos o suscripciones.
- Rúbrica: español _ · rationale _ · coherencia _

### `vago-startup`

> Tengo una idea de startup y quiero saber qué tecnologías usar para empezar bien.

**groq-low**
- `needs_clarification` · 
- Necesito un poco más de contexto para recomendarte herramientas.
- Pregunta: ¿Qué tipo de producto o servicio ofrecerá su startup?
- Pregunta: ¿Qué funcionalidades principales necesita su aplicación (por ejemplo, autenticación, pagos, búsqueda, etc.)?
- Pregunta: ¿Cuál es el público objetivo y en qué plataformas (web, móvil) planea lanzar su producto?
- Rúbrica: español _ · rationale _ · coherencia _
