# Comparación de modelos · flujo completo del asistente

Generado con `python -m ai.eval.run_assistant_eval` el 2026-11-02 a las 22:46. 5 casos × 1 corridas por proveedor; catálogo de 100 repos; umbral 0.2; el modelo ve 3 candidatos por necesidad y se registran 5. La llamada de calentamiento no se cuenta.

## Modelos

| Proveedor | Modelo | Razonamiento | Arranque en frío |
|---|---|---|---|
| gemini | `gemini-3.5-flash-lite` | por defecto | 3.5 s |

## Resumen

| Métrica | gemini |
|---|---|
| Status correcto | 100% |
| Respuesta válida | 100% |
| Necesidades detectadas | 88% |
| Techo de la búsqueda (top 3) | 60% |
| Techo con 5 candidatos | 60% |
| Eligió un aceptable (donde había) | 33% |
| Se abstuvo (donde no había) | 25% |
| Eligió el primer candidato | 50% |
| Consistencia entre corridas | — |
| Entender válido al 1.er intento | 100% |
| Generar válido al 1.er intento | 100% |
| Limitaciones repetidas | 0 |
| Ids en el texto | 0 |
| Errores del proveedor | 0/5 |
| Tiempo total (mediana) | 3.2 s |
| Tiempo total (peor caso) | 4.2 s |
| Sobre 15 s | 0/5 |
| Entender · buscar · generar (mediana) | 1.6 s · 0.1 s · 2.4 s |
| Tokens entrada / salida (mediana) | 2773 / 294 |
| Esperas (límite de uso o error temporal) | 0.0 s |

Evidencia direccional: 5 casos; los porcentajes no son estadística firme.

## Por necesidad

Cuenta sobre las corridas válidas: detectada · había un aceptable en el top 3 (techo) · eligió un aceptable. Sin aceptables, se espera que no elija nada.

| Caso · necesidad | Aceptables | gemini |
|---|---|---|
| `logistica-flota` · messaging | kafka | det 1/1 · techo 1 · eligió 1 |
| `logistica-flota` · data-processing | flink, beam | det 0/1 · techo 0 · eligió 0 |
| `logistica-flota` · database | ClickHouse | det 1/1 · techo 0 · eligió 0 |
| `logistica-flota` · analytics | grafana | det 1/1 · techo 0 · eligió 0 |
| `pantalla-rag-corto` · ai | llama_index, langchain, ollama | det 1/1 · techo 1 · eligió 0 |
| `pantalla-rag-corto` · auth | (ninguno) | det 1/1 · eligió algo 1 |
| `pantalla-observabilidad` · observability | opentelemetry-collector, jaeger, prometheus | det 1/1 · techo 1 · eligió 0 |
| `una-pagos` · payments | (ninguno) | det 1/1 · eligió algo 0 |
| `vago-startup` · (vago) | — | status ok 1/1 |

## Para revisar a mano (corrida 1)

Rúbrica de 1 a 3: español · `rationale` ligado al negocio · coherencia (título, resumen y cajas dicen lo mismo).

### `logistica-flota`

> Mi cliente es una empresa de logística con 200 camiones. Cada camión envía su ubicación cada pocos segundos; quieren procesar esos eventos en tiempo real, guardarlos y ver tableros de entregas por ciudad.

**gemini**
- `ok` · Arquitectura de streaming y almacenamiento para logística
- Esta propuesta integra herramientas open source para la ingesta en tiempo real de la ubicación de los camiones, su almacenamiento distribuido y la posterior transformación de datos para analítica.
- **Apache Kafka** (`apache/kafka`), Procesamiento de flujos de eventos: Apache Kafka es una plataforma de streaming de eventos distribuida que permite procesar en tiempo real los eventos de ubicación enviados por cada camión de la flota.
- **etcd** (`etcd-io/etcd`), Almacenamiento de datos: etcd ofrece un almacenamiento de clave-valor distribuido y confiable para guardar los datos generados por el sistema de logística.
- **dbt** (`dbt-labs/dbt`), Transformación y modelado de datos: dbt permite a los analistas transformar los datos para preparar las métricas y los tableros de entregas por ciudad solicitados por el negocio.
- Limitación: La solución de analítica elegida realiza modelado y transformación, pero no incluye nativamente la interfaz visual o de tableros de control.
- Supuesto: Se asume que la empresa cuenta con infraestructura propia o en la nube para hospedar los servicios distribuidos.
- Supuesto: Se requiere una herramienta de visualización final conectada a las transformaciones para ver los tableros.
- Rúbrica: español _ · rationale _ · coherencia _

### `pantalla-rag-corto`

> Propón un RAG privado para consultar documentos con permisos de acceso.

**gemini**
- `ok` · Arquitectura de RAG Privado con Control de Acceso
- Esta propuesta integra un motor de inferencia de IA para modelos de lenguaje, una plataforma de procesamiento de datos para la búsqueda documental y una herramienta de gestión de secretos y accesos. Con estas soluciones se cubre la consulta privada de documentos y la seguridad requerida.
- **vLLM** (`vllm-project/vllm`), Inferencia de modelos de lenguaje: Provee un motor de inferencia eficiente en memoria para ejecutar los modelos generativos necesarios en el RAG privado con licencia Apache-2.0.
- **LlamaIndex** (`run-llama/llama_index`), Plataforma de datos y búsqueda: Funciona como la plataforma de procesamiento de datos para la búsqueda semántica y la ingesta de los documentos que se van a consultar.
- **Vault** (`hashicorp/vault`), Gestión de accesos y secretos: La herramienta gestiona la seguridad y los permisos de acceso solicitados. Su licencia no fue identificada por GitHub.
- Limitación: No se incluye una interfaz de usuario web directa en esta arquitectura.
- Supuesto: Se asume que la infraestructura cuenta con soporte para aceleración por hardware compatible con vLLM.
- Supuesto: Se requiere un mecanismo de sincronización entre el control de identidades y la plataforma de datos.
- Rúbrica: español _ · rationale _ · coherencia _

### `pantalla-observabilidad`

> Define un stack de observabilidad con métricas, logs y trazas distribuidas para microservicios en Kubernetes.

**gemini**
- `ok` · Stack de observabilidad integral para Kubernetes
- Esta propuesta integra herramientas para centralizar la visualización de métricas, logs y trazas distribuidas. Se utiliza una plataforma unificada para el monitoreo y análisis de los microservicios.
- **Grafana** (`grafana/grafana`), Visualización de métricas, logs y trazas: Grafana permite visualizar métricas, logs y trazas desde múltiples fuentes en una plataforma composable. Resuelve directamente la necesidad de un stack de observabilidad para los microservicios.
- Limitación: No se incluyeron componentes específicos de recolección de trazas como Jaeger en esta única selección.
- Supuesto: Se cuenta con fuentes de datos existentes como Prometheus o Loki para alimentar los tableros.
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
- Pregunta: ¿De qué trata tu startup y qué problema principal busca resolver?
- Pregunta: ¿Qué funcionalidades clave tendrá la primera versión de tu producto?
- Pregunta: ¿Qué tecnologías, lenguajes o plataformas prefieres o ya sabes utilizar?
- Rúbrica: español _ · rationale _ · coherencia _
