# Comparación de modelos · flujo completo del asistente

Generado con `python -m ai.eval.run_assistant_eval` el 2026-11-03 a las 03:01. 5 casos × 3 corridas por proveedor; catálogo de 100 repos; umbral 0.2; el modelo ve 3 candidatos por necesidad y se registran 5. La llamada de calentamiento no se cuenta.

## Modelos

| Proveedor | Modelo | Razonamiento | Arranque en frío |
|---|---|---|---|
| gemini | `gemini-3.5-flash-lite` | por defecto | 1.8 s |
| groq-low | `openai/gpt-oss-120b` | low | 0.9 s |
| claude-haiku | `claude-haiku-5-5` | por defecto | 2.0 s |

## Resumen

| Métrica | gemini | groq-low | claude-haiku |
|---|---|---|---|
| Status correcto | 100% | 100% | 93% |
| Respuesta válida | 100% | 100% | 93% |
| Necesidades detectadas | 88% | 83% | 96% |
| Techo de la búsqueda (top 3) | 73% | 71% | 65% |
| Techo con 5 candidatos | 73% | 79% | 65% |
| Eligió un aceptable (donde había) | 73% | 70% | 82% |
| Se abstuvo (donde no había) | 40% | 22% | 67% |
| Eligió el primer candidato | 65% | 82% | 15% |
| Consistencia entre corridas | 60% | 40% | 60% |
| Entender válido al 1.er intento | 100% | 100% | 93% |
| Generar válido al 1.er intento | 100% | 100% | 33% |
| Limitaciones repetidas | 1 | 0 | 4 |
| Ids en el texto | 0 | 0 | 0 |
| Errores del proveedor | 0/15 | 1/15 | 0/15 |
| Tiempo total (mediana) | 3.9 s | 2.5 s | 10.2 s |
| Tiempo total (peor caso) | 5.3 s | 4.3 s | 19.2 s |
| Sobre 15 s | 0/15 | 0/14 | 1/15 |
| Entender · buscar · generar (mediana) | 1.7 s · 0.1 s · 2.3 s | 1.1 s · 0.1 s · 1.9 s | 1.4 s · 0.1 s · 10.5 s |
| Tokens entrada / salida (mediana) | 2958 / 509 | 3540 / 530 | 7138 / 1477 |
| Esperas (límite de uso o error temporal) | 0.0 s | 0.0 s | 0.0 s |

Evidencia direccional: 5 casos; los porcentajes no son estadística firme.

## Por necesidad

Cuenta sobre las corridas válidas: detectada · había un aceptable en el top 3 (techo) · eligió un aceptable. Sin aceptables, se espera que no elija nada.

| Caso · necesidad | Aceptables | gemini | groq-low | claude-haiku |
|---|---|---|---|---|
| `logistica-flota` · messaging | kafka | det 3/3 · techo 3 · eligió 3 | det 1/3 · techo 1 · eligió 1 | det 3/3 · techo 3 · eligió 2 |
| `logistica-flota` · data-processing | flink, beam | det 0/3 · techo 0 · eligió 0 | det 2/3 · techo 1 · eligió 1 | det 2/3 · techo 2 · eligió 1 |
| `logistica-flota` · database | ClickHouse | det 3/3 · techo 0 · eligió 0 | det 3/3 · techo 0 · eligió 0 | det 3/3 · techo 0 · eligió 0 |
| `logistica-flota` · analytics | grafana | det 3/3 · techo 3 · eligió 3 | det 3/3 · techo 3 · eligió 3 | det 3/3 · techo 0 · eligió 0 |
| `pantalla-rag-corto` · ai | llama_index, langchain, ollama | det 3/3 · techo 2 · eligió 2 | det 2/3 · techo 2 · eligió 1 | det 3/3 · techo 3 · eligió 3 |
| `pantalla-rag-corto` · auth | (ninguno) | det 3/3 · eligió algo 3 | det 3/3 · eligió algo 3 | det 3/3 · eligió algo 3 |
| `pantalla-observabilidad` · observability | opentelemetry-collector, jaeger, prometheus | det 3/3 · techo 3 · eligió 0 | det 3/3 · techo 3 · eligió 1 | det 3/3 · techo 3 · eligió 3 |
| `una-pagos` · payments | (ninguno) | det 3/3 · eligió algo 0 | det 2/2 · eligió algo 0 | det 3/3 · eligió algo 0 |
| `vago-startup` · (vago) | — | status ok 3/3 | status ok 3/3 | status ok 3/3 |

## Para revisar a mano (corrida 1)

Rúbrica de 1 a 3: español · `rationale` ligado al negocio · coherencia (título, resumen y cajas dicen lo mismo).

### `logistica-flota`

> Mi cliente es una empresa de logística con 200 camiones. Cada camión envía su ubicación cada pocos segundos; quieren procesar esos eventos en tiempo real, guardarlos y ver tableros de entregas por ciudad.

**gemini**
- `ok` · Arquitectura de Logística en Tiempo Real para Camiones
- Esta propuesta integra almacenamiento eficiente, visualización mediante tableros y procesamiento de eventos en tiempo real para gestionar la flota de camiones. Se asegura la ingesta continua y la consulta rápida de las entregas por ciudad.
- **Redis** (`redis/redis`), Almacenamiento rápido: Redis funciona como una base de datos en memoria para guardar las ubicaciones enviadas por los camiones. Su licencia no fue identificada por GitHub.
- **Grafana** (`grafana/grafana`), Visualización de datos: Grafana permite ver tableros de entregas por ciudad de forma visual y componible. Utiliza la licencia AGPL-3.0.
- **Apache Kafka** (`apache/kafka`), Transmisión de eventos: Apache Kafka procesa los eventos en tiempo real de los camiones que envían su ubicación. Cuenta con licencia Apache-2.0.
- Limitación: No se incluye una herramienta específica para la limpieza y transformación avanzada de datos previos a la analítica.
- Supuesto: La empresa cuenta con infraestructura en la nube o servidores propios para alojar los servicios seleccionados.
- Supuesto: Los dispositivos GPS en los camiones envían los datos utilizando un formato estándar compatible con Kafka.
- Rúbrica: español _ · rationale _ · coherencia _

**groq-low**
- `ok` · Sistema de procesamiento y visualización de datos de logística en tiempo real
- Se propone una arquitectura basada en Apache Beam para el procesamiento en tiempo real de las ubicaciones de los camiones, almacenamiento de los datos en etcd y visualización de los resultados con Grafana. La solución cubre todas las necesidades detectadas, aunque el almacén etcd no está optimizado para series temporales de gran volumen.
- **Apache Beam** (`apache/beam`), Procesamiento en tiempo real de eventos de ubicación: Apache Beam permite construir pipelines de streaming que pueden ingerir los datos de los camiones y transformarlos en tiempo real, cumpliendo con la necesidad de procesar eventos cada pocos segundos.
- **etcd** (`etcd-io/etcd`), Almacenamiento de pares clave‑valor de ubicaciones: etcd es un almacén distribuido de clave‑valor fiable que puede usarse para guardar la última posición conocida de cada camión, cumpliendo con la necesidad de persistir los datos.
- **Grafana** (`grafana/grafana`), Visualización de tableros de entregas por ciudad: Grafana ofrece dashboards personalizables para mostrar métricas y mapas de entregas, satisfaciendo la necesidad de visualizar los datos de ubicación por ciudad.
- Limitación: etcd no está diseñado como base de datos de series temporales de alta ingestión; para un volumen mayor sería más apropiado ClickHouse u otro TSDB.
- Supuesto: Se dispone de un mecanismo de ingestión (por ejemplo, MQTT o HTTP) que envía los eventos de ubicación al pipeline de Beam.
- Supuesto: Los datos de ubicación se almacenarán como pares clave‑valor en etcd, asumiendo que el volumen es manejable para este almacén.
- Supuesto: Grafana se conectará a etcd a través de un exporter o a una fuente compatible para visualizar los datos.
- Rúbrica: español _ · rationale _ · coherencia _

**claude-haiku**
- sin respuesta: None

### `pantalla-rag-corto`

> Propón un RAG privado para consultar documentos con permisos de acceso.

**gemini**
- `ok` · Arquitectura de RAG Privado con Control de Acceso
- Propuesta técnica para implementar un sistema de RAG privado que permite consultar documentos aplicando gestión de permisos de acceso. Se integran componentes para la construcción de agentes, búsqueda semántica, gestión de secretos y almacenamiento distribuido.
- **LangChain** (`langchain-ai/langchain`), Plataforma para agentes de IA: Resuelve la necesidad de recuperación de información con modelos generativos para implementar el RAG privado. Cuenta con licencia MIT y alta actividad reciente.
- **LlamaIndex** (`run-llama/llama_index`), Plataforma de procesamiento de documentos: Facilita la búsqueda semántica sobre documentos vectoriales para consultar documentos eficientemente. Utiliza licencia MIT y se mantiene activamente.
- **Vault** (`hashicorp/vault`), Gestión de secretos y accesos: Gestiona los roles y permisos de acceso requeridos para proteger la información. La licencia de la herramienta elegida dice no identificada por GitHub.
- **etcd** (`etcd-io/etcd`), Almacenamiento clave-valor: Proporciona un almacenamiento confiable para los datos críticos del sistema. Cuenta con licencia Apache-2.0 y actualizaciones recientes.
- Limitación: La propuesta no incluye un motor de inferencia de alta eficiencia como vLLM para los modelos de lenguaje.
- Supuesto: Se asume que la infraestructura base opera en un entorno contenerizado.
- Supuesto: Se asume la necesidad de cifrar los datos en reposo y en tránsito.
- Rúbrica: español _ · rationale _ · coherencia _

**groq-low**
- `ok` · RAG privado con control de acceso y búsqueda semántica
- Se propone una arquitectura basada en FastAPI como backend, que expone APIs para consultas RAG. Los documentos se almacenan en etcd y se indexan con pgvector en PostgreSQL para búsqueda semántica. La autenticación y control de acceso se gestionan con HashiCorp Vault. La generación de respuestas utiliza modelos de Hugging Face Transformers. No se identificaron limitaciones adicionales más allá de la licencia no identificada de Vault.
- **pgvector** (`pgvector/pgvector`), Búsqueda semántica de documentos: Permite almacenar vectores en PostgreSQL y realizar consultas de similitud, ideal para un RAG privado que requiere búsqueda basada en contenido.
- **Vault** (`hashicorp/vault`), Gestión de autenticación y control de acceso: Ofrece gestión de secretos y políticas de acceso granular, asegurando que solo usuarios autorizados consulten los documentos.
- **etcd** (`etcd-io/etcd`), Almacenamiento seguro de documentos y metadatos: Es un almacén de claves‑valor distribuido y fiable, adecuado para guardar documentos y sus referencias de forma segura.
- **FastAPI** (`fastapi/fastapi`), Servidor de API y lógica de RAG: Framework rápido y sencillo para crear APIs que coordinan la búsqueda, la generación de texto y la autorización.
- **Transformers** (`huggingface/transformers`), Modelo de generación de texto para respuestas RAG: Proporciona acceso a modelos de lenguaje de última generación que pueden generar respuestas a partir de los fragmentos recuperados.
- Limitación: La licencia de HashiCorp Vault aparece como no identificada en el repositorio.
- Rúbrica: español _ · rationale _ · coherencia _

**claude-haiku**
- `ok` · RAG privado con control de acceso por permisos de documentos
- Se propone un RAG privado donde Ollama ejecuta los modelos de lenguaje y embeddings localmente, pgvector almacena y busca los vectores de los documentos en Postgres, y HashiCorp Vault gestiona secretos y credenciales para controlar el acceso. Hashicorp Vault no es estrictamente un sistema de RBAC sobre documentos, por lo que el filtrado por permisos deberá implementarse en la capa de consulta combinando identidades y políticas de acceso.
- **Ollama** (`ollama/ollama`), Ejecución local de modelos de lenguaje y embeddings: Permite ejecutar modelos de lenguaje y de embeddings de forma local, sin enviar los documentos a servicios externos, lo que cubre la exigencia de privacidad del RAG. Tiene licencia MIT y se mantiene activamente.
- **pgvector** (`pgvector/pgvector`), Almacenamiento y búsqueda vectorial de fragmentos de documentos: Añade búsqueda por similitud vectorial a Postgres, permitiendo consultar documentos por significado. Puede almacenar los metadatos de permisos junto a los vectores para filtrar resultados. Su licencia no ha sido identificada por GitHub, por lo que conviene revisarla antes de usarla.
- **HashiCorp Vault** (`hashicorp/vault`), Gestión de secretos y credenciales de acceso: Gestiona secretos y gestión de privilegios de acceso, útil para proteger las credenciales de la base de datos y de los servicios. Su licencia no ha sido identificada por GitHub, así que debe verificarse. No implementa por sí solo permisos a nivel de documento, que deberán resolverse en la aplicación.
- Limitación: LlamaIndex y LangChain son candidatos complementarios para orquestar la ingesta y la recuperación de documentos, pero no se han elegido como herramienta principal de ninguna necesidad.
- Limitación: Vault gestiona secretos, no permisos por documento; el filtrado de acceso a nivel de documento debe implementarse en la capa de la aplicación.
- Limitación: Ollama es la opción elegida para IA, pero Hugging Face Transformers podría complementarla si se necesitan modelos no disponibles en Ollama o un ajuste fino propio.
- Limitación: Ansible no encaja en el sistema de RAG propuesto y no se ha seleccionado para ninguna necesidad.
- Supuesto: Los documentos son de volumen moderado y caben en una sola instancia de Postgres.
- Supuesto: Existe un directorio de usuarios con roles o grupos que determinan qué documentos puede consultar cada persona.
- Supuesto: La aplicación que orquesta el RAG (por ejemplo, en LangChain o LlamaIndex) no está incluida en la propuesta y deberá desarrollarse.
- Supuesto: El hardware disponible permite ejecutar los modelos elegidos en Ollama con una latencia aceptable.
- Rúbrica: español _ · rationale _ · coherencia _

### `pantalla-observabilidad`

> Define un stack de observabilidad con métricas, logs y trazas distribuidas para microservicios en Kubernetes.

**gemini**
- `ok` · Stack de Observabilidad y Orquestación para Microservicios
- Esta propuesta integra una plataforma de visualización para métricas, logs y trazas junto con la orquestación de contenedores en Kubernetes para garantizar el monitoreo y gestión eficiente del sistema.
- **Grafana** (`grafana/grafana`), Visualización de métricas, logs y trazas: Grafana permite visualizar métricas, logs y trazas desde múltiples fuentes en una plataforma de observabilidad abierta y componible, cumpliendo exactamente con los requerimientos del usuario.
- **Kubernetes** (`kubernetes/kubernetes`), Orquestación de contenedores: Kubernetes ofrece programación y gestión de contenedores a nivel de producción, siendo la base ideal para desplegar microservicios según lo solicitado.
- Limitación: La recolección y el rastreo distribuido detallado se benefician enormemente al complementar Grafana con herramientas como OpenTelemetry Collector o Jaeger.
- Supuesto: Se asume que el entorno de despliegue principal es un clúster de Kubernetes existente.
- Supuesto: Se requiere un sistema centralizado para la visualización unificada de datos de rendimiento.
- Rúbrica: español _ · rationale _ · coherencia _

**groq-low**
- `ok` · Stack de observabilidad completo para Kubernetes
- Se propone Grafana como la solución principal para visualizar métricas, logs y trazas distribuidas en microservicios Kubernetes. Prometheus y OpenTelemetry Collector se mencionan como componentes complementarios para la recolección de métricas y datos de trazas. No existen necesidades sin herramienta en el catálogo.
- **Grafana** (`grafana/grafana`), Plataforma de visualización y análisis de métricas, logs y trazas: Grafana permite visualizar métricas, logs y trazas de múltiples fuentes, cubriendo los tres tipos de datos que el usuario requiere para sus microservicios en Kubernetes.
- Limitación: Para la recolección de métricas y trazas se suele combinar con Prometheus y OpenTelemetry Collector, que complementan a Grafana.
- Rúbrica: español _ · rationale _ · coherencia _

**claude-haiku**
- `ok` · Stack de observabilidad para microservicios en Kubernetes
- La propuesta se centra en Prometheus como herramienta principal para medir el estado de los microservicios en Kubernetes mediante métricas. Trazas distribuidas y visualización unificada quedan como complementos recomendados, aunque no se incluyen como cajas porque el catálogo asigna una sola necesidad de observabilidad.
- **Prometheus** (`prometheus/prometheus`), Recolección, almacenamiento y consulta de métricas de los microservicios: Prometheus es un sistema de monitoreo y base de datos de series temporales orientado a métricas, adecuado para medir el estado de los microservicios en Kubernetes. Tiene licencia Apache-2.0 y se mantiene activamente, con cambios recientes.
- Limitación: Las trazas distribuidas no quedan cubiertas por la caja principal: Jaeger (jaegertracing/jaeger) sería el complemento natural para trazado distribuido y debe incorporarse como herramienta adicional.
- Limitación: La visualización unificada de métricas, logs y trazas no queda cubierta por la caja principal: Grafana (grafana/grafana) sería el complemento recomendado para paneles y alertas.
- Limitación: No se cubren logs: se necesita una herramienta complementaria de agregación de logs (por ejemplo, Loki o Elasticsearch) que integre con Grafana.
- Limitación: No se contempla alta disponibilidad ni escalado a largo plazo de Prometheus (por ejemplo, con almacenamiento remoto), ya que el pedido no lo especifica.
- Supuesto: Los microservicios se despliegan en un clúster de Kubernetes y pueden exponer un endpoint de métricas.
- Supuesto: Se instrumentará el código con OpenTelemetry o una librería compatible para generar trazas.
- Supuesto: El stack de logs (por ejemplo, Loki o Elasticsearch) no está incluido en el catálogo y debe definirse aparte.
- Supuesto: El volumen de datos y el tiempo de retención requeridos no se especificaron en el pedido.
- Rúbrica: español _ · rationale _ · coherencia _

### `una-pagos`

> Necesito cobrar suscripciones mensuales a los clientes de mi software.

**gemini**
- `no_evidence` · 
- El catálogo todavía no tiene herramientas para lo que pides: pagos.
- Limitación: Pagos: el catálogo no tiene herramientas para «cobro de suscripciones recurrentes en línea».
- Rúbrica: español _ · rationale _ · coherencia _

**groq-low**
- sin respuesta: LLMUnavailable: groq-low: error 400 del proveedor: Error code: 400 - Failed to validate JSON. Please adjust your prompt. See 'failed_generation' for more details.

**claude-haiku**
- `no_evidence` · 
- El catálogo todavía no tiene herramientas para lo que pides: pagos.
- Limitación: Pagos: el catálogo no tiene herramientas para «cobros recurrentes por suscripción».
- Rúbrica: español _ · rationale _ · coherencia _

### `vago-startup`

> Tengo una idea de startup y quiero saber qué tecnologías usar para empezar bien.

**gemini**
- `needs_clarification` · 
- Necesito un poco más de contexto para recomendarte herramientas.
- Pregunta: ¿Qué tipo de producto o servicio ofrecerá tu startup?
- Pregunta: ¿Qué funcionalidades principales tendrá la primera versión de tu aplicación?
- Pregunta: ¿Qué lenguajes o tecnologías prefieres utilizar o ya conoces?
- Rúbrica: español _ · rationale _ · coherencia _

**groq-low**
- `needs_clarification` · 
- Necesito un poco más de contexto para recomendarte herramientas.
- Pregunta: ¿Qué tipo de producto o servicio ofrecerá su startup?
- Pregunta: ¿Qué funcionalidades principales necesita su aplicación (por ejemplo, usuarios, pagos, búsquedas, análisis, etc.)?
- Pregunta: ¿En qué plataformas desea desplegar su solución (web, móvil, escritorio) y qué tecnologías prefiere usar?
- Rúbrica: español _ · rationale _ · coherencia _

**claude-haiku**
- `needs_clarification` · 
- Necesito un poco más de contexto para recomendarte herramientas.
- Pregunta: ¿Qué problema resuelve tu startup y para quién es (clientes, usuarios o empresas)?
- Pregunta: ¿Qué funciones principales necesita el producto (por ejemplo, cobros, inicio de sesión, búsqueda, notificaciones o una tienda en línea)?
- Pregunta: ¿Ya tienes algún equipo técnico o planeas construir el producto tú mismo, y tienes preferencia por algún lenguaje o framework?
- Rúbrica: español _ · rationale _ · coherencia _
