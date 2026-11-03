# Comparación de modelos · flujo completo del asistente

Generado con `python -m ai.eval.run_assistant_eval` el 2026-11-02 a las 23:02. 5 casos × 3 corridas por proveedor; catálogo de 100 repos; umbral 0.2; el modelo ve 3 candidatos por necesidad y se registran 5. La llamada de calentamiento no se cuenta.

## Modelos

| Proveedor | Modelo | Razonamiento | Arranque en frío |
|---|---|---|---|
| gemini | `gemini-3.5-flash-lite` | por defecto | 1.4 s |
| groq-low | `openai/gpt-oss-120b` | low | 0.9 s |
| ollama | `qwen3.5:4b-q4_K_M` | none | 37.2 s |

## Resumen

| Métrica | gemini | groq-low | ollama |
|---|---|---|---|
| Status correcto | 100% | 100% | 90% |
| Respuesta válida | 100% | 100% | 90% |
| Necesidades detectadas | 88% | 86% | 71% |
| Techo de la búsqueda (top 3) | 67% | 50% | 75% |
| Techo con 5 candidatos | 73% | 50% | 75% |
| Eligió un aceptable (donde había) | 70% | 0% | 33% |
| Se abstuvo (donde no había) | 36% | 60% | 57% |
| Eligió el primer candidato | 59% | 100% | 75% |
| Consistencia entre corridas | 60% | 100% | 67% |
| Entender válido al 1.er intento | 93% | 100% | 100% |
| Generar válido al 1.er intento | 89% | 100% | 67% |
| Limitaciones repetidas | 1 | 1 | 0 |
| Ids en el texto | 0 | 0 | 1 |
| Errores del proveedor | 0/15 | 7/15 | 5/15 |
| Tiempo total (mediana) | 3.4 s | 1.5 s | 13.2 s |
| Tiempo total (peor caso) | 6.8 s | 4.2 s | 31.8 s |
| Sobre 15 s | 0/15 | 0/8 | 4/10 |
| Entender · buscar · generar (mediana) | 1.4 s · 0.1 s · 1.9 s | 0.9 s · 0.1 s · 2.0 s | 3.0 s · 0.1 s · 12.7 s |
| Tokens entrada / salida (mediana) | 2854 / 485 | 2136 / 113 | 2712 / 515 |
| Esperas (límite de uso o error temporal) | 0.0 s | 105.0 s | 0.0 s |

Evidencia direccional: 5 casos; los porcentajes no son estadística firme.

## Por necesidad

Cuenta sobre las corridas válidas: detectada · había un aceptable en el top 3 (techo) · eligió un aceptable. Sin aceptables, se espera que no elija nada.

| Caso · necesidad | Aceptables | gemini | groq-low | ollama |
|---|---|---|---|---|
| `logistica-flota` · messaging | kafka | det 2/3 · techo 2 · eligió 2 | det 0/0 · techo 0 · eligió 0 | det 1/1 · techo 1 · eligió 0 |
| `logistica-flota` · data-processing | flink, beam | det 1/3 · techo 0 · eligió 0 | det 0/0 · techo 0 · eligió 0 | det 0/1 · techo 0 · eligió 0 |
| `logistica-flota` · database | ClickHouse | det 3/3 · techo 0 · eligió 0 | det 0/0 · techo 0 · eligió 0 | det 1/1 · techo 0 · eligió 0 |
| `logistica-flota` · analytics | grafana | det 3/3 · techo 3 · eligió 3 | det 0/0 · techo 0 · eligió 0 | det 1/1 · techo 1 · eligió 0 |
| `pantalla-rag-corto` · ai | llama_index, langchain, ollama | det 3/3 · techo 2 · eligió 2 | det 1/2 · techo 0 · eligió 0 | det 1/3 · techo 1 · eligió 1 |
| `pantalla-rag-corto` · auth | (ninguno) | det 3/3 · eligió algo 3 | det 2/2 · eligió algo 2 | det 3/3 · eligió algo 3 |
| `pantalla-observabilidad` · observability | opentelemetry-collector, jaeger, prometheus | det 3/3 · techo 3 · eligió 0 | det 1/1 · techo 1 · eligió 0 | det 0/1 · techo 0 · eligió 0 |
| `una-pagos` · payments | (ninguno) | det 3/3 · eligió algo 0 | det 2/2 · eligió algo 0 | det 3/3 · eligió algo 0 |
| `vago-startup` · (vago) | — | status ok 3/3 | status ok 3/3 | status ok 2/2 |

## Para revisar a mano (corrida 1)

Rúbrica de 1 a 3: español · `rationale` ligado al negocio · coherencia (título, resumen y cajas dicen lo mismo).

### `logistica-flota`

> Mi cliente es una empresa de logística con 200 camiones. Cada camión envía su ubicación cada pocos segundos; quieren procesar esos eventos en tiempo real, guardarlos y ver tableros de entregas por ciudad.

**gemini**
- `ok` · Arquitectura en tiempo real para logística de camiones
- Esta propuesta integra una plataforma de streaming de eventos para procesar las ubicaciones de los flujos de camiones, una base de datos en memoria para el almacenamiento y una plataforma de visualización para los tableros operativos por ciudad.
- **Redis** (`redis/redis`), Almacén de datos geográficos y en memoria: Redis funciona como una base de datos en memoria y motor de consultas para guardar las ubicaciones de los camiones enviadas frecuentemente. Su licencia no fue identificada por GitHub.
- **Grafana** (`grafana/grafana`), Plataforma de visualización y tableros: Grafana permite crear tableros operativos para ver las entregas por ciudad mediante sus capacidades de visualización de datos.
- **Apache Kafka** (`apache/kafka`), Plataforma de streaming de eventos: Apache Kafka gestiona el streaming de eventos en tiempo real para procesar la ubicación que cada camión envía cada pocos segundos.
- Limitación: La propuesta no incluye herramientas específicas de mapas geográficos avanzados para GIS, limitándose a tableros analíticos.
- Supuesto: Se asume que los camiones cuentan con un dispositivo con conectividad celular constante para enviar su ubicación.
- Supuesto: Se requiere personal con capacidad técnica para operar plataformas distribuidas.
- Rúbrica: español _ · rationale _ · coherencia _

**groq-low**
- sin respuesta: LLMUnavailable: groq-low: error 400 del proveedor

**ollama**
- sin respuesta: None

### `pantalla-rag-corto`

> Propón un RAG privado para consultar documentos con permisos de acceso.

**gemini**
- `ok` · Arquitectura para RAG privado y gestión de accesos
- Esta propuesta integra herramientas open source para construir un sistema de RAG privado capaz de consultar documentos. Se utiliza una plataforma orientada a agentes para la recuperación y generación, combinada con una solución de gestión de secretos y accesos con licencia no identificada.
- **LangChain** (`langchain-ai/langchain`), Plataforma para ingeniería de agentes y RAG: Resuelve la necesidad de un sistema para consultar documentos mediante recuperación de información y generación aumentada, siendo una plataforma activa con licencia MIT.
- **Vault** (`hashicorp/vault`), Gestión de accesos y secretos: Gestiona los permisos de acceso requeridos para proteger los documentos en el sistema. La licencia de la herramienta no fue identificada por GitHub.
- Limitación: La licencia de Hashicorp Vault no está identificada, por lo que se debe revisar su adecuación legal antes de implementarla en producción.
- Supuesto: Se asume que la organización cuenta con una infraestructura segura para desplegar servicios de gestión de secretos y modelos de lenguaje.
- Rúbrica: español _ · rationale _ · coherencia _

**groq-low**
- sin respuesta: LLMUnavailable: groq-low: sigue sin responder tras 5 esperas

**ollama**
- `ok` · Sistema RAG Privado con Control de Acceso
- Se propone un conjunto de herramientas para inferencia de modelos de lenguaje privados (Ollama) que permita almacenar y gestionar secretos como los permisos de acceso mediante HashiCorp Vault. Se asume que no se requieren motores de búsqueda vectoriales específicos ni bases de datos externas, y se reconoce que la elección actual prioriza la simplicidad e infraestructura sobre funcionalidades avanzadas de gestión de usuarios o integración RAG completa.
- **Ollama** (`ollama/ollama`), Servidor de inferencia unificada para ejecutar modelos LLMs en privado: Ofrece una solución completa e independiente para correr servicios de inferencia de modelos de lenguaje localmente, permitiendo el uso de múltiples modelos modernos en un entorno cerrado sin dependencias externas. Su licencia MIT facilita su adoctrinamiento y mantenimiento en entornos comerciales sin restricciones compartimentadas.
- **HashiCorp Vault** (`hashicorp/vault`), Gestiona secretos y permisos de acceso privilegiado con alta seguridad: Proporciona una solución robusta para gestión de secretos y control de acceso, resolviendo la necesidad de manejar permisos a datos de manera segura mediante el encriptación de las credenciales antes de ser usadas por los modelos. Almacena información sensible como tokens o claves API de forma cifrada y ofrece políticas de acceso granulares que pueden aplicarse a los procesos de consulta interna.
- Limitación: La herramienta seleccionada para inferencia no incluye características nativas de integración con motores de búsqueda vectoriales o bases de datos de knowledge graphs sin contenedores externos.
- Limitación: Vault no gestiona directamente el ciclo de vida completo del sistema RAG (indexación, embedding, recuperación), solo los secrets necesarios para su operación.
- Supuesto: Los documentos a consultar se asumen disponibles en una fuente accesible localmente o mediante red controlada.
- Supuesto: No se requiere un sistema complejo de gestión de usuarios (IAM) separado, limitándose al envío de credenciales por sesión o API key.
- Rúbrica: español _ · rationale _ · coherencia _

### `pantalla-observabilidad`

> Define un stack de observabilidad con métricas, logs y trazas distribuidas para microservicios en Kubernetes.

**gemini**
- `ok` · Stack de observabilidad y orquestación para microservicios
- Esta propuesta integra Grafana para la visualización y análisis unificado de métricas, logs y trazas distribuidas, respaldado por Kubernetes para la gestión y orquestación de la infraestructura de contenedores.
- **Grafana** (`grafana/grafana`), Visualización y análisis de métricas, logs y trazas: Grafana resuelve la necesidad de visualizar métricas, logs y trazas desde múltiples fuentes en una plataforma de observabilidad abierta y componible, adaptándose perfectamente a lo solicitado.
- **Kubernetes** (`kubernetes/kubernetes`), Orquestación y gestión de contenedores: Kubernetes provee la programación y gestión de contenedores a nivel de producción necesaria para ejecutar los microservicios tal como lo solicitó el usuario.
- Supuesto: Se asume que los microservicios ya se encuentran instrumentados para enviar sus datos de observabilidad.
- Rúbrica: español _ · rationale _ · coherencia _

**groq-low**
- `ok` · Stack de observabilidad completo para microservicios en Kubernetes
- Se propone usar Grafana como plataforma central para visualizar métricas, logs y trazas, integrándose con fuentes comunes en Kubernetes. No se requieren herramientas adicionales para cubrir la necesidad de observabilidad, aunque la recolección de datos puede complementarse con coleccionistas externos.
- **Grafana** (`grafana/grafana`), Plataforma de visualización y análisis de métricas, logs y trazas: Grafana permite visualizar métricas, logs y trazas de múltiples fuentes, cubriendo toda la necesidad de observabilidad solicitada por el usuario.
- Supuesto: Los microservicios ya exponen métricas compatibles con Prometheus y logs compatibles con Loki o Elasticsearch.
- Supuesto: Se dispone de un clúster de Kubernetes con acceso a recursos de red para la integración de los componentes.
- Rúbrica: español _ · rationale _ · coherencia _

**ollama**
- sin respuesta: LLMTimeout: ollama: sin respuesta en 15 s

### `una-pagos`

> Necesito cobrar suscripciones mensuales a los clientes de mi software.

**gemini**
- `no_evidence` · 
- El catálogo todavía no tiene herramientas para lo que pides: pagos.
- Limitación: Pagos: el catálogo no tiene herramientas para «cobro de suscripciones recurrentes».
- Rúbrica: español _ · rationale _ · coherencia _

**groq-low**
- `no_evidence` · 
- El catálogo todavía no tiene herramientas para lo que pides: pagos.
- Limitación: Pagos: el catálogo no tiene herramientas para «gestión de cobros recurrentes».
- Rúbrica: español _ · rationale _ · coherencia _

**ollama**
- `no_evidence` · 
- El catálogo todavía no tiene herramientas para lo que pides: pagos.
- Limitación: Pagos: el catálogo no tiene herramientas para «cobro de suscripciones recurrentes».
- Rúbrica: español _ · rationale _ · coherencia _

### `vago-startup`

> Tengo una idea de startup y quiero saber qué tecnologías usar para empezar bien.

**gemini**
- `needs_clarification` · 
- Necesito un poco más de contexto para recomendarte herramientas.
- Pregunta: ¿De qué trata tu idea de startup y qué problema principal busca resolver?
- Pregunta: ¿Qué funcionalidades clave tendrá la primera versión de tu producto?
- Pregunta: ¿Qué tecnologías, lenguajes o plataformas tienes experiencia usando o prefieres evitar?
- Rúbrica: español _ · rationale _ · coherencia _

**groq-low**
- `needs_clarification` · 
- Necesito un poco más de contexto para recomendarte herramientas.
- Pregunta: ¿Qué tipo de producto o servicio ofrecerá su startup?
- Pregunta: ¿Necesita gestionar usuarios, pagos, búsquedas o análisis de datos?
- Pregunta: ¿Qué canales de interacción (web, móvil, API) planea utilizar?
- Rúbrica: español _ · rationale _ · coherencia _

**ollama**
- `needs_clarification` · 
- Necesito un poco más de contexto para recomendarte herramientas.
- Pregunta: H¿Qué tipo de servicios o productos va a ofrecer su startup?
- Pregunta: H¿Quiénes serán sus primeros usuarios o clientes?
- Pregunta: H¿Tienen un presupuesto inicial estimado para el desarrollo?
- Rúbrica: español _ · rationale _ · coherencia _
