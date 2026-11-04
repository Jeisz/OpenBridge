# Comparación de modelos · flujo completo del asistente

Generado con `python -m ai.eval.run_assistant_eval` el 2026-11-03 a las 02:00. 5 casos × 3 corridas por proveedor; catálogo de 100 repos; umbral 0.2; el modelo ve 3 candidatos por necesidad y se registran 5. La llamada de calentamiento no se cuenta.

## Modelos

| Proveedor | Modelo | Razonamiento | Arranque en frío |
|---|---|---|---|
| gemini | `gemini-3.5-flash-lite` | por defecto | 2.0 s |
| gemini-3.1-lite | `gemini-3.1-flash-lite` | por defecto | 11.1 s |
| groq-low | `openai/gpt-oss-120b` | low | 1.2 s |
| claude-haiku | `claude-haiku-5-5` | por defecto | 2.9 s |

## Resumen

| Métrica | gemini | gemini-3.1-lite | groq-low | claude-haiku |
|---|---|---|---|---|
| Status correcto | 100% | 100% | 100% | 93% |
| Respuesta válida | 100% | 100% | 100% | 93% |
| Necesidades detectadas | 88% | 89% | 75% | 96% |
| Techo de la búsqueda (top 3) | 73% | 75% | 78% | 76% |
| Techo con 5 candidatos | 73% | 83% | 78% | 76% |
| Eligió un aceptable (donde había) | 73% | 67% | 57% | 85% |
| Se abstuvo (donde no había) | 40% | 14% | 38% | 40% |
| Eligió el primer candidato | 53% | 67% | 75% | 28% |
| Consistencia entre corridas | 60% | 50% | 100% | 40% |
| Entender válido al 1.er intento | 100% | 100% | 100% | 100% |
| Generar válido al 1.er intento | 100% | 89% | 100% | 33% |
| Limitaciones repetidas | 1 | 0 | 0 | 2 |
| Ids en el texto | 0 | 0 | 0 | 0 |
| Errores del proveedor | 0/15 | 3/15 | 1/15 | 0/15 |
| Tiempo total (mediana) | 3.6 s | 5.4 s | 2.4 s | 8.1 s |
| Tiempo total (peor caso) | 4.7 s | 17.4 s | 4.6 s | 13.6 s |
| Sobre 15 s | 0/15 | 2/12 | 0/14 | 0/15 |
| Entender · buscar · generar (mediana) | 1.7 s · 0.1 s · 2.0 s | 1.8 s · 0.1 s · 3.6 s | 1.1 s · 0.1 s · 1.9 s | 1.5 s · 0.1 s · 9.3 s |
| Tokens entrada / salida (mediana) | 2898 / 516 | 2932 / 548 | 3461 / 460 | 7444 / 1618 |
| Esperas (límite de uso o error temporal) | 0.0 s | 0.0 s | 0.0 s | 0.0 s |

Evidencia direccional: 5 casos; los porcentajes no son estadística firme.

## Por necesidad

Cuenta sobre las corridas válidas: detectada · había un aceptable en el top 3 (techo) · eligió un aceptable. Sin aceptables, se espera que no elija nada.

| Caso · necesidad | Aceptables | gemini | gemini-3.1-lite | groq-low | claude-haiku |
|---|---|---|---|---|---|
| `logistica-flota` · messaging | kafka | det 3/3 · techo 3 · eligió 3 | det 0/2 · techo 0 · eligió 0 | det 2/2 · techo 2 · eligió 2 | det 3/3 · techo 3 · eligió 3 |
| `logistica-flota` · data-processing | flink, beam | det 0/3 · techo 0 · eligió 0 | det 2/2 · techo 1 · eligió 1 | det 0/2 · techo 0 · eligió 0 | det 2/3 · techo 2 · eligió 1 |
| `logistica-flota` · database | ClickHouse | det 3/3 · techo 0 · eligió 0 | det 2/2 · techo 0 · eligió 0 | det 2/2 · techo 0 · eligió 0 | det 3/3 · techo 0 · eligió 0 |
| `logistica-flota` · analytics | grafana | det 3/3 · techo 3 · eligió 3 | det 2/2 · techo 2 · eligió 2 | det 2/2 · techo 2 · eligió 2 | det 3/3 · techo 2 · eligió 2 |
| `pantalla-rag-corto` · ai | llama_index, langchain, ollama | det 3/3 · techo 2 · eligió 2 | det 3/3 · techo 3 · eligió 3 | det 0/3 · techo 0 · eligió 0 | det 3/3 · techo 3 · eligió 3 |
| `pantalla-rag-corto` · auth | (ninguno) | det 3/3 · eligió algo 3 | det 3/3 · eligió algo 3 | det 3/3 · eligió algo 3 | det 3/3 · eligió algo 3 |
| `pantalla-observabilidad` · observability | opentelemetry-collector, jaeger, prometheus | det 3/3 · techo 3 · eligió 0 | det 3/3 · techo 3 · eligió 0 | det 3/3 · techo 3 · eligió 0 | det 3/3 · techo 3 · eligió 2 |
| `una-pagos` · payments | (ninguno) | det 3/3 · eligió algo 0 | det 1/1 · eligió algo 0 | det 3/3 · eligió algo 0 | det 3/3 · eligió algo 0 |
| `vago-startup` · (vago) | — | status ok 3/3 | status ok 3/3 | status ok 3/3 | status ok 3/3 |

## Para revisar a mano (corrida 1)

Rúbrica de 1 a 3: español · `rationale` ligado al negocio · coherencia (título, resumen y cajas dicen lo mismo).

### `logistica-flota`

> Mi cliente es una empresa de logística con 200 camiones. Cada camión envía su ubicación cada pocos segundos; quieren procesar esos eventos en tiempo real, guardarlos y ver tableros de entregas por ciudad.

**gemini**
- `ok` · Arquitectura en tiempo real para logística de camiones
- Esta propuesta integra almacenamiento confiable, transmisión de eventos en tiempo real y visualización avanzada para procesar las ubicaciones de los 200 camiones y generar tableros por ciudad.
- **etcd** (`etcd-io/etcd`), Almacenamiento clave-valor: Permite guardar los datos críticos de las entregas en un almacén clave-valor distribuido y confiable con licencia Apache-2.0.
- **Grafana** (`grafana/grafana`), Visualización y tableros: Resuelve la necesidad de ver tableros de entregas por ciudad mediante una plataforma de visualización de datos con licencia AGPL-3.0.
- **Apache Kafka** (`apache/kafka`), Streaming de eventos: Procesa eficientemente los eventos de ubicación en tiempo real enviados por los camiones utilizando una plataforma de transmisión de eventos distribuida.
- Limitación: La propuesta no incluye el software específico de geolocalización o mapas embebidos para la visualización geoespacial detallada en los tableros.
- Supuesto: Se asume que la empresa cuenta con infraestructura propia o en la nube para desplegar servicios distribuidos.
- Supuesto: Se asume que los dispositivos en los camiones pueden conectarse mediante un protocolo compatible con la plataforma de streaming.
- Rúbrica: español _ · rationale _ · coherencia _

**gemini-3.1-lite**
- sin respuesta: LLMTimeout: gemini-3.1-lite: sin respuesta en 15 s

**groq-low**
- sin respuesta: LLMUnavailable: groq-low: sigue sin responder tras 5 esperas

**claude-haiku**
- `ok` · Pipeline de ubicaciones con Kafka, Beam, Prometheus y Grafana en tiempo real
- Para ingesta y transporte de los eventos de ubicación de 200 camiones se propone Apache Kafka, una plataforma de streaming distribuida con licencia Apache-2.0 y mantenimiento reciente. El procesamiento en tiempo real se apoya en Apache Beam, que ofrece un modelo unificado para flujos de datos, y las series temporales de ubicación se guardan en Prometheus, que es una base de datos de series temporales. Los tableros de entregas por ciudad se construyen con Grafana sobre esos datos.
- **Apache Kafka** (`apache/kafka`), Ingesta y distribución de eventos de ubicación: Kafka es una plataforma de streaming distribuida que puede recibir los eventos de ubicación que cada camión envía cada pocos segundos. Su licencia Apache-2.0 y su mantenimiento reciente la hacen una opción sólida para el flujo continuo de datos.
- **Apache Beam** (`apache/beam`), Procesamiento de flujos de eventos en tiempo real: Beam es un modelo de programación unificado para procesamiento por lotes y en streaming, lo que permite procesar los eventos de ubicación en tiempo real. Está bajo licencia Apache-2.0 y se mantiene activamente.
- **Prometheus** (`prometheus/prometheus`), Almacenamiento de series temporales de ubicación: Prometheus es un sistema de monitoreo y base de datos de series temporales que puede guardar las ubicaciones de los camiones a lo largo del tiempo. Usa licencia Apache-2.0 y tiene desarrollo reciente, aunque está orientado principalmente a métricas y no a grandes volúmenes de eventos históricos.
- **Grafana** (`grafana/grafana`), Tableros de entregas por ciudad: Grafana es una plataforma de visualización de datos que puede conectarse a múltiples fuentes para construir tableros de entregas por ciudad. Su licencia es AGPL-3.0, que conviene revisar si el cliente planea modificar y distribuir la herramienta.
- Limitación: ClickHouse y Redis aparecen entre los candidatos de varias necesidades, pero no se eligieron para la base de datos: ClickHouse no está entre los candidatos de esta necesidad y Redis tiene licencia no identificada por GitHub.
- Limitación: Prometheus no está diseñado para conservar grandes volúmenes de eventos individuales a largo plazo, por lo que el almacenamiento histórico podría requerir una solución adicional.
- Limitación: La propuesta no define alertas operativas ni monitoreo de la propia plataforma.
- Limitación: El pedido no especifica si se requieren rutas, geocercas o cálculo de ETA, que no están cubiertos por estas herramientas sin desarrollo adicional.
- Supuesto: Cada camión envía coordenadas con identificador de vehículo, marca de tiempo y ciudad o datos que permitan derivarla.
- Supuesto: El volumen estimado de eventos es de unos 200 camiones con envíos cada pocos segundos, sin datos de cifras exactas en el pedido.
- Supuesto: El cliente tiene infraestructura o capacidad para operar Kafka, Beam y Prometheus, o contratará soporte para ello.
- Supuesto: Los tableros serán de uso interno y no se publicarán a terceros.
- Rúbrica: español _ · rationale _ · coherencia _

### `pantalla-rag-corto`

> Propón un RAG privado para consultar documentos con permisos de acceso.

**gemini**
- `ok` · Arquitectura de RAG privado con control de acceso seguro
- Esta propuesta despliega una plataforma de agentes y modelos de lenguaje para implementar el sistema RAG privado, complementada con herramientas para la gestión de permisos de acceso. Se integran componentes modernos con licencias abiertas para garantizar la privacidad y seguridad de los documentos.
- **LangChain** (`langchain-ai/langchain`), Plataforma de agentes y recuperación de información: Permite construir la arquitectura RAG para consultar documentos de manera privada, utilizando una plataforma de agentes madura con licencia MIT y mantenimiento activo.
- **Vault** (`hashicorp/vault`), Gestión de secretos y accesos privilegiados: Resuelve la necesidad de controlar los permisos de acceso requeridos para la consulta segura. La licencia de la herramienta es no identificada por GitHub.
- Limitación: La propuesta no incluye un motor de inferencia de modelos de lenguaje dedicado, el cual requeriría componentes adicionales como vLLM si se procesan grandes volúmenes de datos localmente.
- Supuesto: Se asume que la empresa cuenta con infraestructura propia para desplegar los servicios de IA y gestión de secretos.
- Supuesto: Se requiere un mecanismo centralizado para validar las credenciales de los usuarios antes de permitir la consulta de documentos.
- Rúbrica: español _ · rationale _ · coherencia _

**gemini-3.1-lite**
- `ok` · Arquitectura para RAG privado con control de acceso a documentos
- Esta propuesta integra herramientas para la ingesta, búsqueda y gestión de permisos sobre documentos. Se articula el procesamiento de datos con almacenamiento vectorial, protegiendo los accesos sensibles mediante gestión de secretos.
- **LangChain** (`langchain-ai/langchain`), Orquestador de flujos de IA: Permite conectar los componentes de tu RAG para procesar las consultas de manera eficiente y escalable. Su licencia es MIT, facilitando su adopción en entornos privados.
- **HashiCorp Vault** (`hashicorp/vault`), Gestión de secretos y accesos: Centraliza el control de permisos y credenciales, garantizando que el acceso a los documentos sea seguro. La licencia no está identificada por GitHub.
- **LlamaIndex** (`run-llama/llama_index`), Plataforma de procesamiento de datos: Optimiza la ingesta y consulta de documentos para el sistema de IA bajo licencia MIT. Es fundamental para organizar la estructura de datos que alimentará el RAG.
- Limitación: La propuesta no incluye una solución de base de datos relacional para el almacenamiento de metadatos o la persistencia de usuarios, lo cual debería añadirse para completar la gestión de permisos.
- Supuesto: Se asume la disponibilidad de un motor de base de datos vectorial para persistir los embeddings generados.
- Supuesto: El sistema requiere una capa de infraestructura para desplegar y comunicar estos servicios.
- Rúbrica: español _ · rationale _ · coherencia _

**groq-low**
- `ok` · RAG privado con búsqueda semántica y control de acceso
- Se propone un sistema RAG privado que combina pgvector para búsqueda semántica sobre PostgreSQL, HashiCorp Vault para autenticación y gestión segura de documentos, y etcd como almacén de metadatos confiable. La solución cubre todas las necesidades detectadas, aunque la gestión de grandes archivos de documento requerirá integración externa.
- **pgvector** (`pgvector/pgvector`), Búsqueda semántica de vectores en PostgreSQL: Permite almacenar y consultar embeddings vectoriales de documentos, ofreciendo similitud aproximada y estática bajo licencia no identificada.
- **HashiCorp Vault** (`hashicorp/vault`), Gestión de autenticación y control de acceso: Ofrece autenticación robusta y políticas de acceso granulares para proteger documentos, aunque su licencia no está identificada.
- **etcd** (`etcd-io/etcd`), Almacenamiento confiable de metadatos de documentos: Proporciona un almacén clave‑valor distribuido, ideal para guardar referencias y permisos de documentos con alta disponibilidad.
- Limitación: HashiCorp Vault tiene licencia no identificada, lo que puede requerir revisión legal.
- Limitación: etcd no está optimizado para almacenar archivos grandes; se necesita un sistema de almacenamiento de objetos adicional.
- Supuesto: Los documentos completos se almacenarán fuera de etcd (por ejemplo, en un bucket de objetos) y solo sus metadatos y referencias se guardarán en etcd.
- Supuesto: Se dispone de un modelo de embeddings para generar los vectores que pgvector indexará.
- Rúbrica: español _ · rationale _ · coherencia _

**claude-haiku**
- `ok` · RAG privado con control de acceso por documento usando modelos locales
- La propuesta usa Ollama para ejecutar modelos de lenguaje y embeddings de forma local, de modo que los documentos no salgan del entorno, y LlamaIndex como capa de procesamiento e indexación para el RAG. El control de permisos se apoya en la autenticación por roles, donde Istio aplica políticas de acceso a los servicios y HashiCorp Vault gestiona secretos, mientras que la búsqueda vectorial y el almacenamiento de documentos quedan cubiertos por LlamaIndex. Todas las necesidades tienen herramienta asignada.
- **Ollama** (`ollama/ollama`), Ejecución local de modelos de lenguaje y embeddings: Permite ejecutar modelos como Gemma, Qwen y DeepSeek en local, lo que mantiene privados los documentos consultados en el RAG. Tiene licencia MIT y un mantenimiento reciente.
- **LlamaIndex** (`run-llama/llama_index`), Procesamiento de documentos, indexación y recuperación para el RAG: Es una plataforma de procesamiento de documentos para IA, adecuada para consultar documentos con filtros de acceso. Tiene licencia MIT y se mantiene activamente.
- **Istio** (`istio/istio`), Aplicación de políticas de acceso entre servicios: Permite aplicar políticas de control de acceso sobre los servicios del sistema, lo que ayuda a restringir qué usuarios consultan los documentos. Tiene licencia Apache-2.0 y mantenimiento reciente, aunque su complejidad es considerable para un sistema pequeño.
- **LlamaIndex** (`run-llama/llama_index`), Gestión de los documentos fuente para la indexación: Su capacidad de procesamiento de documentos permite cargar y preparar los archivos que se consultan, aunque el almacenamiento físico de archivos no es su función principal. Tiene licencia MIT.
- Limitación: Vault no está incluido en las cajas porque no fue candidato de la necesidad detectada, pero podría ser necesario para gestionar credenciales de los modelos y bases de datos.
- Limitación: Ripgrep y pgvector fueron candidatos de búsqueda, pero no se eligieron: pgvector podría servir para búsqueda vectorial si se requiere una base de datos relacional con vectores.
- Limitación: Istio agrega complejidad operativa considerable para un RAG privado de escala pequeña o mediana.
- Limitación: La calidad de las respuestas depende del modelo local elegido y de los recursos de hardware disponibles.
- Supuesto: Los documentos tienen niveles de permiso asignables por usuario o rol.
- Supuesto: El negocio cuenta con hardware suficiente para ejecutar modelos locales.
- Supuesto: La autenticación de usuarios (identidad) se gestiona fuera de esta propuesta, por ejemplo con un proveedor de identidad existente.
- Supuesto: El volumen de documentos no requiere un almacenamiento distribuido especializado.
- Rúbrica: español _ · rationale _ · coherencia _

### `pantalla-observabilidad`

> Define un stack de observabilidad con métricas, logs y trazas distribuidas para microservicios en Kubernetes.

**gemini**
- `ok` · Stack de observabilidad para microservicios
- Esta propuesta integra herramientas para centralizar métricas, logs y trazas en un entorno de Kubernetes. Se seleccionó Grafana para la visualización y análisis unificado de datos.
- **Grafana** (`grafana/grafana`), Visualización y análisis de métricas, logs y trazas: Permite visualizar métricas, logs y trazas desde múltiples fuentes en una plataforma unificada, cumpliendo exactamente con lo solicitado para los microservicios.
- Limitación: La propuesta cubre la visualización y análisis, pero requiere componentes adicionales de recolección como Prometheus u OpenTelemetry Collector para la ingesta completa de datos.
- Supuesto: Se asume que el despliegue se realiza sobre un clúster de Kubernetes existente.
- Rúbrica: español _ · rationale _ · coherencia _

**gemini-3.1-lite**
- `ok` · Stack de observabilidad e infraestructura sobre Kubernetes
- Esta propuesta integra Grafana para la visualización unificada de métricas, logs y trazas junto con Kubernetes para la gestión de microservicios. Se ha seleccionado Grafana por su capacidad para centralizar datos de múltiples fuentes, garantizando un despliegue escalable sobre un entorno Kubernetes robusto.
- **Grafana** (`grafana/grafana`), Plataforma de visualización y observabilidad: Grafana permite visualizar y unificar métricas, logs y trazas distribuidas desde diversas fuentes en una sola interfaz. Es una plataforma composable bajo licencia AGPL-3.0 con alta actividad reciente, ideal para consolidar la visibilidad del sistema.
- **Kubernetes** (`kubernetes/kubernetes`), Orquestador de contenedores: Es la herramienta estándar de industria para la gestión y despliegue de microservicios en contenedores a gran escala. Bajo licencia Apache-2.0, garantiza la escalabilidad necesaria para el entorno de producción solicitado.
- Limitación: La propuesta no incluye el almacenamiento de logs ni la recolección de trazas nativa, por lo que se recomienda integrar herramientas complementarias como Loki o Jaeger junto a Grafana.
- Supuesto: Se asume que el usuario cuenta con fuentes de datos compatibles como Prometheus o Loki para alimentar a Grafana.
- Supuesto: El entorno de Kubernetes ya está configurado o en proceso de despliegue.
- Rúbrica: español _ · rationale _ · coherencia _

**groq-low**
- `ok` · Stack de observabilidad basado en Grafana para Kubernetes
- Se propone utilizar Grafana como la herramienta central de observabilidad, capaz de visualizar métricas, logs y trazas de microservicios en Kubernetes. No se requieren herramientas adicionales para cubrir la necesidad identificada. Se asume que el entorno es Kubernetes y que se integrarán fuentes de datos compatibles.
- **Grafana** (`grafana/grafana`), visualización y paneles de métricas, logs y trazas: Grafana permite crear dashboards que muestran métricas, logs y trazas de múltiples fuentes, cumpliendo con la solicitud del usuario de observabilidad integral para microservicios en Kubernetes.
- Supuesto: El entorno de ejecución es un clúster Kubernetes donde se desplegarán los microservicios.
- Supuesto: Se dispondrá de fuentes de datos compatibles (Prometheus, Loki, OpenTelemetry) que Grafana podrá consumir.
- Rúbrica: español _ · rationale _ · coherencia _

**claude-haiku**
- sin respuesta: None

### `una-pagos`

> Necesito cobrar suscripciones mensuales a los clientes de mi software.

**gemini**
- `no_evidence` · 
- El catálogo todavía no tiene herramientas para lo que pides: pagos.
- Limitación: Pagos: el catálogo no tiene herramientas para «cobro de suscripciones recurrentes».
- Rúbrica: español _ · rationale _ · coherencia _

**gemini-3.1-lite**
- sin respuesta: LLMTimeout: gemini-3.1-lite: sin respuesta en 15 s

**groq-low**
- `no_evidence` · 
- El catálogo todavía no tiene herramientas para lo que pides: pagos.
- Limitación: Pagos: el catálogo no tiene herramientas para «gestión de pagos recurrentes».
- Rúbrica: español _ · rationale _ · coherencia _

**claude-haiku**
- `no_evidence` · 
- El catálogo todavía no tiene herramientas para lo que pides: pagos.
- Limitación: Pagos: el catálogo no tiene herramientas para «cobro recurrente de suscripciones mensuales».
- Rúbrica: español _ · rationale _ · coherencia _

### `vago-startup`

> Tengo una idea de startup y quiero saber qué tecnologías usar para empezar bien.

**gemini**
- `needs_clarification` · 
- Necesito un poco más de contexto para recomendarte herramientas.
- Pregunta: ¿Qué tipo de producto o servicio principal ofrecerá tu startup?
- Pregunta: ¿Qué funcionalidades clave necesitas que tenga el sistema en su primera versión?
- Rúbrica: español _ · rationale _ · coherencia _

**gemini-3.1-lite**
- `needs_clarification` · 
- Necesito un poco más de contexto para recomendarte herramientas.
- Pregunta: ¿Qué tipo de producto o servicio intentas construir?
- Pregunta: ¿Qué funcionalidades principales debe tener tu MVP?
- Pregunta: ¿Tienes experiencia previa con algún lenguaje de programación o framework?
- Rúbrica: español _ · rationale _ · coherencia _

**groq-low**
- `needs_clarification` · 
- Necesito un poco más de contexto para recomendarte herramientas.
- Pregunta: ¿Cuál es el tipo de producto o servicio que ofrecerá la startup?
- Pregunta: ¿Qué funcionalidades principales necesita la aplicación (por ejemplo, usuarios, pagos, búsqueda, etc.)?
- Pregunta: ¿En qué entorno planea desplegar la solución (cloud, on‑premise, contenedores, etc.)?
- Rúbrica: español _ · rationale _ · coherencia _

**claude-haiku**
- `needs_clarification` · 
- Necesito un poco más de contexto para recomendarte herramientas.
- Pregunta: ¿Qué problema resuelve tu startup y para quién es el producto?
- Pregunta: ¿Qué funciones necesitan tus usuarios, por ejemplo cobrar, iniciar sesión, buscar contenido o enviar notificaciones?
- Pregunta: ¿Ya tienes algún prototipo o tecnologías que quieras mantener?
- Rúbrica: español _ · rationale _ · coherencia _
