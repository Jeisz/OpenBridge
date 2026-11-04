# Comparación de modelos · flujo completo del asistente

Generado con `python -m ai.eval.run_assistant_eval` el 2026-11-04 a las 00:25. 5 casos × 3 corridas por proveedor; catálogo de 100 repos; umbral 0.19; el modelo ve 3 candidatos por necesidad y se registran 5. La llamada de calentamiento no se cuenta.

## Modelos

| Proveedor | Modelo | Razonamiento | Arranque en frío |
|---|---|---|---|
| gemini | `gemini-3.5-flash-lite` | por defecto | 1.7 s |

## Resumen

| Métrica | gemini |
|---|---|
| Status correcto | 100% |
| Respuesta válida | 100% |
| Necesidades detectadas | 87% |
| Techo de la búsqueda (top 3) | 64% |
| Techo con 5 candidatos | 71% |
| Eligió un aceptable (donde había) | 89% |
| Se abstuvo (donde no había) | 45% |
| Acierto de punta a punta (comparable entre k) | 57% |
| Sin caja donde el caso no tiene herramientas | 50% |
| Eligió el primer candidato | 53% |
| Consistencia entre corridas | 40% |
| Entender válido al 1.er intento | 100% |
| Generar válido al 1.er intento | 100% |
| Limitaciones repetidas | 1 |
| Ids en el texto | 0 |
| Errores del proveedor | 1/15 |
| Tiempo total (mediana) | 4.6 s |
| Tiempo total (peor caso) | 11.1 s |
| Sobre 15 s | 0/14 |
| Entender · buscar · generar (mediana) | 2.2 s · 0.1 s · 2.4 s |
| Tokens entrada / salida (mediana) | 3176 / 417 |
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
| `pantalla-rag-corto` · auth | (ninguno) | det 3/3 · eligió algo 3 |
| `pantalla-observabilidad` · observability | opentelemetry-collector, jaeger, prometheus | det 2/2 · techo 2 · eligió 1 |
| `una-pagos` · payments | (ninguno) | det 3/3 · eligió algo 0 |
| `vago-startup` · (vago) | — | status ok 3/3 |

## Para revisar a mano (corrida 1)

Rúbrica de 1 a 3: español · `rationale` ligado al negocio · coherencia (título, resumen y cajas dicen lo mismo).

### `logistica-flota`

> Mi cliente es una empresa de logística con 200 camiones. Cada camión envía su ubicación cada pocos segundos; quieren procesar esos eventos en tiempo real, guardarlos y ver tableros de entregas por ciudad.

**gemini**
- `ok` · Sistema de monitoreo en tiempo real para flota de camiones
- Esta propuesta implementa una plataforma robusta para procesar eventos de ubicación en tiempo real desde 200 camiones, almacenarlos de forma confiable y visualizarlos mediante tableros interactivos por ciudad. Se utiliza una plataforma de streaming distribuido para la ingesta, una base de datos distribuida de alta disponibilidad para el almacenamiento y una herramienta líder en visualización para los tableros operativos.
- **Apache Kafka** (`apache/kafka`), Plataforma de streaming para procesar eventos en tiempo real: Resuelve la necesidad de procesar los eventos de ubicación enviados por cada camión en tiempo real gracias a su arquitectura como plataforma de streaming distribuido.
- **etcd** (`etcd-io/etcd`), Almacenamiento clave-valor para datos críticos del sistema: Permite guardar la información generada por los camiones utilizando un almacén clave-valor distribuido y confiable para sistemas críticos.
- **Grafana** (`grafana/grafana`), Plataforma de visualización para ver tableros por ciudad: Resuelve directamente la creación de tableros de entregas por ciudad al ofrecer una plataforma componible de visualización de datos.
- Limitación: La base de datos elegida está optimizada para datos clave-valor críticos y podría requerir componentes adicionales de procesamiento analítico masivo para consultas geográficas complejas.
- Limitación: La licencia de etcd es Apache-2.0 y la de Grafana es AGPL-3.0, lo cual debe validarse con las políticas de uso de la empresa.
- Supuesto: Se asume que la empresa cuenta con infraestructura propia o en la nube para hospedar los servicios distribuidos.
- Supuesto: Se asume que los dispositivos en los camiones envían la información utilizando protocolos compatibles con la plataforma de mensajería.
- Rúbrica: español _ · rationale _ · coherencia _

### `pantalla-rag-corto`

> Propón un RAG privado para consultar documentos con permisos de acceso.

**gemini**
- `ok` · Arquitectura de RAG Privado con Control de Acceso
- Esta propuesta integra una plataforma de ingeniería de agentes para construir el sistema de recuperación y generación aumentada, complementada con una herramienta para la gestión de secretos y control de accesos privilegiados.
- **LangChain** (`langchain-ai/langchain`), Plataforma de agentes y recuperación de información: Resuelve la necesidad de construir el sistema de consulta de documentos con una plataforma madurada para agentes de inteligencia artificial y con actividad reciente bajo licencia MIT.
- **Vault** (`hashicorp/vault`), Gestión de secretos y accesos: Gestiona los permisos de acceso y secretos de la plataforma. La licencia no está identificada por GitHub, por lo que se debe revisar este aspecto legal.
- Limitación: La propuesta no incluye un motor de inferencia de modelos de lenguaje dedicado, el cual se complementaría utilizando vLLM u otra herramienta de servicio de modelos.
- Supuesto: Se asume que la infraestructura se despliega en un entorno local o privado para cumplir con el requisito de privacidad.
- Rúbrica: español _ · rationale _ · coherencia _

### `pantalla-observabilidad`

> Define un stack de observabilidad con métricas, logs y trazas distribuidas para microservicios en Kubernetes.

**gemini**
- `ok` · Stack de observabilidad para microservicios
- Esta propuesta implementa un colector centralizado para gestionar las métricas, los logs y las trazas distribuidas del sistema en Kubernetes. Queda pendiente el almacenamiento a largo plazo y la visualización final.
- **OpenTelemetry Collector** (`open-telemetry/opentelemetry-collector`), Recopilar telemetría: Recopila métricas, logs y trazas de forma estandarizada, adaptándose a los requerimientos de observabilidad para microservicios.
- Limitación: La propuesta no incluye una interfaz de visualización como Grafana ni una base de datos de series temporales como Prometheus para el almacenamiento persistente.
- Supuesto: Se asume que los microservicios en Kubernetes ya están instrumentados para emitir datos en formatos compatibles.
- Rúbrica: español _ · rationale _ · coherencia _

### `una-pagos`

> Necesito cobrar suscripciones mensuales a los clientes de mi software.

**gemini**
- `no_evidence` · 
- El catálogo todavía no tiene herramientas para lo que pides: pagos.
- Limitación: Pagos: el catálogo no tiene herramientas para «cobro de suscripciones mensuales».
- Rúbrica: español _ · rationale _ · coherencia _

### `vago-startup`

> Tengo una idea de startup y quiero saber qué tecnologías usar para empezar bien.

**gemini**
- `needs_clarification` · 
- Necesito un poco más de contexto para recomendarte herramientas.
- Pregunta: ¿Qué tipo de producto o servicio planeas ofrecer con tu startup?
- Pregunta: ¿Qué funcionalidades principales tendrá la primera versión de tu sistema?
- Pregunta: ¿Tienes experiencia previa con algún lenguaje de programación o plataforma tecnológica?
- Rúbrica: español _ · rationale _ · coherencia _
