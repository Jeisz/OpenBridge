# Comparación de modelos · flujo completo del asistente

Generado con `python -m ai.eval.run_assistant_eval` el 2026-11-06 a las 23:44. 5 casos × 3 corridas por proveedor; catálogo de 100 repos; umbral 0.23; el modelo ve 5 candidatos por necesidad y se registran 5. La llamada de calentamiento no se cuenta.

## Modelos

| Proveedor | Modelo | Razonamiento | Arranque en frío |
|---|---|---|---|
| gemini | `gemini-3.5-flash-lite` | por defecto | 3.0 s |

## Resumen

| Métrica | gemini |
|---|---|
| Status correcto | 100% |
| Respuesta válida | 100% |
| Necesidades detectadas | 88% |
| Techo de la búsqueda (top 5) | 73% |
| Techo con 5 candidatos | 73% |
| Eligió un aceptable (donde había) | 73% |
| Se abstuvo (donde no había) | 60% |
| Acierto de punta a punta (comparable entre k) | 53% |
| Sin caja donde el caso no tiene herramientas | 83% |
| Eligió el primer candidato | 73% |
| Consistencia entre corridas | 60% |
| Entender válido al 1.er intento | 100% |
| Generar válido al 1.er intento | 100% |
| Limitaciones repetidas · borrador del modelo | 1 |
| Limitaciones repetidas · respuesta final | 0 |
| Textos del modelo que hablan del catálogo | 3 |
| Ids en el texto | 0 |
| Errores del proveedor | 0/15 |
| Tiempo total (mediana) | 5.8 s |
| Tiempo total (peor caso) | 13.1 s |
| Sobre 15 s | 0/15 |
| Entender · buscar · generar (mediana) | 2.9 s · 0.1 s · 3.7 s |
| Tokens entrada / salida (mediana) | 3387 / 507 |
| Esperas (límite de uso o error temporal) | 10.0 s |

Evidencia direccional: 5 casos; los porcentajes no son estadística firme.

## Por corrida

Una diferencia entre versiones menor que el rango entre corridas no se puede atribuir al cambio.

**gemini**

| Métrica | Corrida 1 | Corrida 2 | Corrida 3 | Rango |
|---|---|---|---|---|
| Status correcto | 100% | 100% | 100% | 100% – 100% |
| Eligió un aceptable (donde había) | 75% | 75% | 67% | 67% – 75% |
| Se abstuvo (donde no había) | 33% | 67% | 75% | 33% – 75% |
| Acierto de punta a punta | 60% | 60% | 40% | 40% – 60% |
| Textos del modelo que hablan del catálogo | 0 | 1 | 2 | 0 – 2 |

## Por necesidad

Cuenta sobre las corridas válidas: detectada · había un aceptable en el top 3 (techo) · eligió un aceptable. Sin aceptables, se espera que no elija nada.

| Caso · necesidad | Aceptables | gemini |
|---|---|---|
| `logistica-flota` · messaging | kafka | det 2/3 · techo 2 · eligió 2 |
| `logistica-flota` · data-processing | flink, beam | det 1/3 · techo 1 · eligió 1 |
| `logistica-flota` · database | ClickHouse | det 3/3 · techo 0 · eligió 0 |
| `logistica-flota` · analytics | grafana | det 3/3 · techo 3 · eligió 3 |
| `pantalla-rag-corto` · ai | llama_index, langchain, ollama | det 3/3 · techo 2 · eligió 2 |
| `pantalla-rag-corto` · auth | (ninguno) | det 3/3 · eligió algo 1 |
| `pantalla-observabilidad` · observability | opentelemetry-collector, jaeger, prometheus | det 3/3 · techo 3 · eligió 0 |
| `una-pagos` · payments | (ninguno) | det 3/3 · eligió algo 0 |
| `vago-startup` · (vago) | — | status ok 3/3 |

## Para revisar a mano (corrida 1)

Rúbrica de 1 a 3: español · `rationale` ligado al negocio · coherencia (título, resumen y cajas dicen lo mismo).

### `logistica-flota`

> Mi cliente es una empresa de logística con 200 camiones. Cada camión envía su ubicación cada pocos segundos; quieren procesar esos eventos en tiempo real, guardarlos y ver tableros de entregas por ciudad.

**gemini**
- `ok` · Sistema en tiempo real para logística de camiones
- Esta propuesta implementa una plataforma de streaming de eventos para procesar las ubicaciones de los camiones, una base de datos clave-valor distribuida para el almacenamiento y una herramienta de visualización para los tableros de entregas.
- **Apache Kafka** (`apache/kafka`), Plataforma de streaming de eventos: Permite procesar eventos en tiempo real gracias a su plataforma de streaming distribuida, ideal para manejar el flujo continuo de ubicaciones de los camiones.
- **etcd** (`etcd-io/etcd`), Almacenamiento clave-valor: Proporciona un almacenamiento distribuido y confiable para los datos críticos del sistema, cubriendo la necesidad de guardar información.
- **Grafana** (`grafana/grafana`), Visualización y tableros: Ofrece una plataforma de visualización de datos y creación de tableros para ver la información de entregas.
- Limitación: Ninguna de las opciones de bases de datos elegidas está especializada puramente en consultas geoespaciales complejas.
- Supuesto: La flota de 200 camiones cuenta con dispositivos con conectividad constante para enviar su ubicación.
- Supuesto: El sistema requiere alta disponibilidad para la ingesta continua de datos.
- Rúbrica: español _ · rationale _ · coherencia _

### `pantalla-rag-corto`

> Propón un RAG privado para consultar documentos con permisos de acceso.

**gemini**
- `ok` · Arquitectura de RAG privado con control de accesos
- Esta propuesta implementa un sistema para consultar documentos mediante recuperación y generación aumentada, complementado con gestión de secretos y accesos privilegiados. Se integra un marco de procesamiento de datos para IA y una herramienta de seguridad robusta.
- **LlamaIndex** (`run-llama/llama_index`), Plataforma de procesamiento de documentos para IA: Resuelve la necesidad de construir un RAG privado para consultar documentos gracias a sus capacidades como plataforma de procesamiento de datos para IA. Su licencia es MIT y cuenta con mantenimiento activo.
- **Vault** (`hashicorp/vault`), Gestión de secretos y acceso privilegiado: Permite gestionar el control de acceso y permisos mediante herramientas para secretos y administración de accesos privilegiados. Su licencia no fue identificada por GitHub y posee mantenimiento activo reciente.
- Limitación: Ninguna.
- Supuesto: Se asume que el almacenamiento de documentos es accesible de forma privada dentro de la infraestructura.
- Supuesto: Se requiere una interfaz de usuario personalizada para realizar las consultas sobre los documentos.
- Rúbrica: español _ · rationale _ · coherencia _

### `pantalla-observabilidad`

> Define un stack de observabilidad con métricas, logs y trazas distribuidas para microservicios en Kubernetes.

**gemini**
- `ok` · Stack completo de observabilidad para microservicios
- Esta propuesta incluye la recolección, almacenamiento y visualización de métricas, logs y trazas distribuidas para entornos de microservicios en Kubernetes utilizando herramientas open source estándar de la industria.
- **Grafana** (`grafana/grafana`), Visualización y análisis de datos de observabilidad: Permite visualizar métricas, logs y trazas desde múltiples fuentes como Prometheus y Jaeger en una plataforma de visualización abierta y componible con licencia AGPL-3.0.
- Limitación: La propuesta actual utiliza Grafana como interfaz, pero requiere componentes adicionales como Prometheus y Jaeger para la recolección integral de métricas y trazas.
- Supuesto: Se asume que el despliegue se realizará sobre un clúster de Kubernetes existente.
- Supuesto: Se requiere complementar Grafana con Prometheus para métricas y Jaeger para trazas.
- Rúbrica: español _ · rationale _ · coherencia _

### `una-pagos`

> Necesito cobrar suscripciones mensuales a los clientes de mi software.

**gemini**
- `no_evidence` · 
- El catálogo todavía no tiene herramientas para lo que pides: pagos.
- Limitación: Pagos: el catálogo no tiene herramientas para «cobro de suscripciones recurrentes en linea».
- Rúbrica: español _ · rationale _ · coherencia _

### `vago-startup`

> Tengo una idea de startup y quiero saber qué tecnologías usar para empezar bien.

**gemini**
- `needs_clarification` · 
- Necesito un poco más de contexto para recomendarte herramientas.
- Pregunta: ¿De qué trata tu startup y qué tipo de sistema o aplicación quieres construir?
- Pregunta: ¿Qué características principales tendrá la primera versión de tu producto?
- Pregunta: ¿Qué lenguajes o tecnologías prefieres o ya sabes utilizar?
- Rúbrica: español _ · rationale _ · coherencia _
