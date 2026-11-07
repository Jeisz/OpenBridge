# Comparación de modelos · flujo completo del asistente

Generado con `python -m ai.eval.run_assistant_eval` el 2026-11-07 a las 07:18. 5 casos × 3 corridas por proveedor; catálogo de 100 repos; umbral 0.23; el modelo ve 5 candidatos por necesidad y se registran 5. La llamada de calentamiento no se cuenta.

## Modelos

| Proveedor | Modelo | Razonamiento | Arranque en frío |
|---|---|---|---|
| gemini | `gemini-3.5-flash-lite` | por defecto | 3.9 s |

## Resumen

| Métrica | gemini |
|---|---|
| Status correcto | 100% |
| Respuesta válida | 100% |
| Necesidades detectadas | 88% |
| Techo de la búsqueda (top 5) | 73% |
| Techo con 5 candidatos | 73% |
| Eligió un aceptable (donde había) | 82% |
| Se abstuvo (donde no había) | 30% |
| Acierto de punta a punta (comparable entre k) | 60% |
| Sin caja donde el caso no tiene herramientas | 50% |
| Eligió el primer candidato | 61% |
| Consistencia entre corridas | 60% |
| Entender válido al 1.er intento | 93% |
| Generar válido al 1.er intento | 100% |
| Limitaciones repetidas · borrador del modelo | 0 |
| Limitaciones repetidas · respuesta final | 0 |
| Textos del modelo que hablan del catálogo | 1 |
| Ids en el texto | 0 |
| Errores del proveedor | 0/15 |
| Tiempo total (mediana) | 3.6 s |
| Tiempo total (peor caso) | 11.7 s |
| Sobre 15 s | 0/15 |
| Entender · buscar · generar (mediana) | 1.6 s · 0.1 s · 2.4 s |
| Tokens entrada / salida (mediana) | 3377 / 451 |
| Esperas (límite de uso o error temporal) | 10.0 s |

Evidencia direccional: 5 casos; los porcentajes no son estadística firme.

## Por corrida

Una diferencia entre versiones menor que el rango entre corridas no se puede atribuir al cambio.

**gemini**

| Métrica | Corrida 1 | Corrida 2 | Corrida 3 | Rango |
|---|---|---|---|---|
| Status correcto | 100% | 100% | 100% | 100% – 100% |
| Eligió un aceptable (donde había) | 75% | 100% | 75% | 75% – 100% |
| Se abstuvo (donde no había) | 33% | 25% | 33% | 25% – 33% |
| Acierto de punta a punta | 60% | 60% | 60% | 60% – 60% |
| Textos del modelo que hablan del catálogo | 0 | 0 | 1 | 0 – 1 |

## Por necesidad

Cuenta sobre las corridas válidas: detectada · había un aceptable en el top 3 (techo) · eligió un aceptable. Sin aceptables, se espera que no elija nada.

| Caso · necesidad | Aceptables | gemini |
|---|---|---|
| `logistica-flota` · messaging | kafka | det 3/3 · techo 3 · eligió 3 |
| `logistica-flota` · data-processing | flink, beam | det 0/3 · techo 0 · eligió 0 |
| `logistica-flota` · database | ClickHouse | det 3/3 · techo 0 · eligió 0 |
| `logistica-flota` · analytics | grafana | det 3/3 · techo 2 · eligió 2 |
| `pantalla-rag-corto` · ai | llama_index, langchain, ollama | det 3/3 · techo 3 · eligió 3 |
| `pantalla-rag-corto` · auth | (ninguno) | det 3/3 · eligió algo 3 |
| `pantalla-observabilidad` · observability | opentelemetry-collector, jaeger, prometheus | det 3/3 · techo 3 · eligió 1 |
| `una-pagos` · payments | (ninguno) | det 3/3 · eligió algo 0 |
| `vago-startup` · (vago) | — | status ok 3/3 |

## Para revisar a mano (corrida 1)

Rúbrica de 1 a 3: español · `rationale` ligado al negocio · coherencia (título, resumen y cajas dicen lo mismo).

### `logistica-flota`

> Mi cliente es una empresa de logística con 200 camiones. Cada camión envía su ubicación cada pocos segundos; quieren procesar esos eventos en tiempo real, guardarlos y ver tableros de entregas por ciudad.

**gemini**
- `ok` · Arquitectura en tiempo real para logística de camiones
- Esta propuesta cubre la ingesta de eventos de ubicación de los camiones con una plataforma distribuida de streaming, el almacenamiento fiable de los datos y la visualización de tableros de entregas por ciudad.
- **Apache Kafka** (`apache/kafka`), Plataforma de streaming de eventos: Apache Kafka es una plataforma de streaming de eventos distribuida bajo licencia Apache-2.0 con actividad reciente, ideal para procesar los flujos de datos enviados por los camiones.
- **etcd** (`etcd-io/etcd`), Almacenamiento de datos: etcd es un almacén de valores clave distribuido y fiable bajo licencia Apache-2.0 con mantenimiento constante, adecuado para guardar la información requerida.
- **Grafana** (`grafana/grafana`), Plataforma de visualización y tableros: Grafana es una plataforma abierta de visualización de datos bajo licencia AGPL-3.0 que permite construir los tableros solicitados para ver las entregas por ciudad.
- Limitación: La propuesta no incluye herramientas específicas para el procesamiento avanzado o analítica pesada como Apache Flink o Spark, que podrían complementar a Kafka.
- Limitación: El almacenamiento con etcd está optimizado para datos clave-valor y podría no ser el más eficiente para consultas analíticas masivas.
- Supuesto: Se asume que la empresa cuenta con infraestructura propia para desplegar los servicios seleccionados.
- Supuesto: Se asume que los dispositivos en los camiones pueden conectarse mediante protocolos compatibles con la plataforma de mensajería.
- Rúbrica: español _ · rationale _ · coherencia _

### `pantalla-rag-corto`

> Propón un RAG privado para consultar documentos con permisos de acceso.

**gemini**
- `ok` · Sistema RAG Privado con Control de Acceso
- Esta propuesta implementa un sistema para consultar documentos de manera privada mediante la indexación y recuperación de información, asegurando además la gestión de secretos y accesos privilegiados.
- **LlamaIndex** (`run-llama/llama_index`), Plataforma de procesamiento de documentos para IA: LlamaIndex es la plataforma ideal para procesar y consultar documentos en un esquema de recuperación de información, bajo licencia MIT y con mantenimiento activo.
- **Vault** (`hashicorp/vault`), Gestión de secretos y accesos privilegiados: Vault gestiona secretos y el acceso privilegiado requerido para proteger los datos, aunque su licencia no está identificada por GitHub y su último cambio fue hace 1 mes.
- Limitación: Otras herramientas del ecosistema de IA como Hugging Face Transformers o LangChain podrían complementar el flujo, pero se ha seleccionado LlamaIndex como plataforma principal de documentos.
- Supuesto: Se asume que la autenticación de usuarios para los permisos de acceso se integrará mediante credenciales gestionadas de forma segura.
- Rúbrica: español _ · rationale _ · coherencia _

### `pantalla-observabilidad`

> Define un stack de observabilidad con métricas, logs y trazas distribuidas para microservicios en Kubernetes.

**gemini**
- `ok` · Stack de Observabilidad para Microservicios en Kubernetes
- La propuesta implementa una plataforma de visualización y análisis para recopilar y mostrar métricas, logs y trazas distribuidas en entornos de Kubernetes.
- **Grafana** (`grafana/grafana`), Visualización y análisis de datos: Grafana permite visualizar métricas, logs y trazas desde múltiples fuentes como Prometheus y Elasticsearch, cumpliendo perfectamente con la recopilación y monitoreo solicitados para el stack.
- Limitación: La solución elegida requiere complementarse con colectores de telemetría y bases de datos de series temporales específicas para la ingesta completa de trazas y métricas.
- Supuesto: Se asume que las fuentes de datos como Prometheus y Loki ya están desplegadas en el cluster de Kubernetes para alimentar la plataforma de visualización.
- Rúbrica: español _ · rationale _ · coherencia _

### `una-pagos`

> Necesito cobrar suscripciones mensuales a los clientes de mi software.

**gemini**
- `no_evidence` · 
- No se encontraron herramientas del catálogo para lo que pides: pagos.
- Limitación: Pagos: no se encontraron herramientas del catálogo para «cobro de suscripciones mensuales».
- Rúbrica: español _ · rationale _ · coherencia _

### `vago-startup`

> Tengo una idea de startup y quiero saber qué tecnologías usar para empezar bien.

**gemini**
- `needs_clarification` · 
- Necesito un poco más de contexto para recomendarte herramientas.
- Pregunta: ¿Qué tipo de producto o aplicación web/móvil planeas construir con tu startup?
- Pregunta: ¿Qué funcionalidades principales tendrá tu sistema para los usuarios?
- Pregunta: ¿Tienes alguna preferencia de lenguaje de programación o experiencia técnica previa?
- Rúbrica: español _ · rationale _ · coherencia _
