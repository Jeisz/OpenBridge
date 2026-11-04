# Comparación de modelos · flujo completo del asistente

Generado con `python -m ai.eval.run_assistant_eval` el 2026-11-03 a las 02:22. 5 casos × 3 corridas por proveedor; catálogo de 100 repos; umbral 0.2; el modelo ve 3 candidatos por necesidad y se registran 5. La llamada de calentamiento no se cuenta.

## Modelos

| Proveedor | Modelo | Razonamiento | Arranque en frío |
|---|---|---|---|
| claude-haiku | `claude-haiku-5-5` | por defecto | 2.1 s |

## Resumen

| Métrica | claude-haiku |
|---|---|
| Status correcto | 80% |
| Respuesta válida | 80% |
| Necesidades detectadas | 96% |
| Techo de la búsqueda (top 3) | 71% |
| Techo con 5 candidatos | 71% |
| Eligió un aceptable (donde había) | 58% |
| Se abstuvo (donde no había) | 55% |
| Eligió el primer candidato | 38% |
| Consistencia entre corridas | 60% |
| Entender válido al 1.er intento | 100% |
| Generar válido al 1.er intento | 33% |
| Limitaciones repetidas | 1 |
| Ids en el texto | 0 |
| Errores del proveedor | 0/15 |
| Tiempo total (mediana) | 10.3 s |
| Tiempo total (peor caso) | 16.7 s |
| Sobre 15 s | 2/15 |
| Entender · buscar · generar (mediana) | 1.5 s · 0.1 s · 10.1 s |
| Tokens entrada / salida (mediana) | 7278 / 1446 |
| Esperas (límite de uso o error temporal) | 0.0 s |

Evidencia direccional: 5 casos; los porcentajes no son estadística firme.

## Por necesidad

Cuenta sobre las corridas válidas: detectada · había un aceptable en el top 3 (techo) · eligió un aceptable. Sin aceptables, se espera que no elija nada.

| Caso · necesidad | Aceptables | claude-haiku |
|---|---|---|
| `logistica-flota` · messaging | kafka | det 3/3 · techo 3 · eligió 2 |
| `logistica-flota` · data-processing | flink, beam | det 2/3 · techo 2 · eligió 1 |
| `logistica-flota` · database | ClickHouse | det 3/3 · techo 0 · eligió 0 |
| `logistica-flota` · analytics | grafana | det 3/3 · techo 1 · eligió 1 |
| `pantalla-rag-corto` · ai | llama_index, langchain, ollama | det 3/3 · techo 3 · eligió 3 |
| `pantalla-rag-corto` · auth | (ninguno) | det 3/3 · eligió algo 3 |
| `pantalla-observabilidad` · observability | opentelemetry-collector, jaeger, prometheus | det 3/3 · techo 3 · eligió 0 |
| `una-pagos` · payments | (ninguno) | det 3/3 · eligió algo 0 |
| `vago-startup` · (vago) | — | status ok 3/3 |

## Para revisar a mano (corrida 1)

Rúbrica de 1 a 3: español · `rationale` ligado al negocio · coherencia (título, resumen y cajas dicen lo mismo).

### `logistica-flota`

> Mi cliente es una empresa de logística con 200 camiones. Cada camión envía su ubicación cada pocos segundos; quieren procesar esos eventos en tiempo real, guardarlos y ver tableros de entregas por ciudad.

**claude-haiku**
- sin respuesta: None

### `pantalla-rag-corto`

> Propón un RAG privado para consultar documentos con permisos de acceso.

**claude-haiku**
- `ok` · RAG privado con control de acceso por documento usando herramientas open source
- La propuesta cubre IA local con Ollama para el modelo de lenguaje, búsqueda vectorial con pgvector sobre Postgres, control de permisos con HashiCorp Vault y almacenamiento de documentos con etcd. LlamaIndex queda como framework de procesamiento documental que une ingesta, indexado y consulta. Todas las necesidades tienen herramienta asignada, aunque el filtrado por permisos deberá diseñarse sobre la base de datos vectorial.
- **Ollama** (`ollama/ollama`), Ejecuta modelos de lenguaje y embeddings de forma local: Permite correr modelos de lenguaje localmente, lo que mantiene los documentos privados dentro de la infraestructura. Tiene una comunidad muy activa y licencia MIT.
- **pgvector** (`pgvector/pgvector`), Almacena embeddings y realiza búsqueda vectorial dentro de Postgres: Añade búsqueda de similitud vectorial a Postgres, lo que permite combinar los vectores con filtros SQL por permisos de acceso. Su licencia no está identificada por GitHub, conviene revisarla antes de adoptarla.
- **HashiCorp Vault** (`hashicorp/vault`), Gestiona secretos y control de acceso privilegiado: Ofrece gestión de secretos y acceso privilegiado, útil para proteger las credenciales de los documentos y los permisos de consulta. Su licencia no está identificada por GitHub, conviene revisarla antes de adoptarla.
- **etcd** (`etcd-io/etcd`), Guarda metadatos y configuración de permisos de los documentos: Es un almacén clave-valor distribuido y confiable, adecuado para guardar metadatos de los documentos y sus reglas de acceso. Tiene licencia Apache-2.0 y es un proyecto muy maduro.
- Limitación: El pedido no menciona ningún proveedor ni tecnología concreta, por lo que no hay herramientas nombradas fuera del catálogo
- Limitación: La propuesta no define cómo se sincronizan los permisos del origen de los documentos con Vault y etcd
- Limitación: La integración entre las cuatro herramientas requiere desarrollo propio; no hay una solución lista para usar
- Supuesto: Los documentos son de una organización con usuarios que tienen roles distintos de acceso
- Supuesto: El volumen de documentos cabe en una instancia de Postgres con pgvector
- Supuesto: Existe infraestructura propia donde ejecutar modelos locales con suficiente memoria
- Supuesto: LlamaIndex, aunque aparece como candidato, se usaría como capa de ingesta y orquestación del RAG y no como caja independiente
- Rúbrica: español _ · rationale _ · coherencia _

### `pantalla-observabilidad`

> Define un stack de observabilidad con métricas, logs y trazas distribuidas para microservicios en Kubernetes.

**claude-haiku**
- sin respuesta: None

### `una-pagos`

> Necesito cobrar suscripciones mensuales a los clientes de mi software.

**claude-haiku**
- `no_evidence` · 
- El catálogo todavía no tiene herramientas para lo que pides: pagos.
- Limitación: Pagos: el catálogo no tiene herramientas para «cobros recurrentes de suscripciones mensuales».
- Rúbrica: español _ · rationale _ · coherencia _

### `vago-startup`

> Tengo una idea de startup y quiero saber qué tecnologías usar para empezar bien.

**claude-haiku**
- `needs_clarification` · 
- Necesito un poco más de contexto para recomendarte herramientas.
- Pregunta: ¿Qué problema resuelve tu startup y para quién es el producto?
- Pregunta: ¿Qué funciones principales necesita tu producto, por ejemplo cobrar a clientes, tener cuentas de usuario o mostrar contenido?
- Pregunta: ¿Tu producto será una web, una app móvil o ambas?
- Rúbrica: español _ · rationale _ · coherencia _
