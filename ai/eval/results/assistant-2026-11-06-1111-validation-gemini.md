# Comparación de modelos · flujo completo del asistente

Generado con `python -m ai.eval.run_assistant_eval` el 2026-11-06 a las 11:11. 10 casos × 2 corridas por proveedor; catálogo de 100 repos; umbral 0.23; el modelo ve 5 candidatos por necesidad y se registran 5. La llamada de calentamiento no se cuenta.

## Modelos

| Proveedor | Modelo | Razonamiento | Arranque en frío |
|---|---|---|---|
| gemini | `gemini-3.5-flash-lite` | por defecto | 2.1 s |

## Resumen

| Métrica | gemini |
|---|---|
| Status correcto | 90% |
| Respuesta válida | 100% |
| Necesidades detectadas | 93% |
| Techo de la búsqueda (top 5) | 89% |
| Techo con 5 candidatos | 89% |
| Eligió un aceptable (donde había) | 88% |
| Se abstuvo (donde no había) | 50% |
| Acierto de punta a punta (comparable entre k) | 79% |
| Sin caja donde el caso no tiene herramientas | 55% |
| Eligió el primer candidato | 54% |
| Consistencia entre corridas | 60% |
| Entender válido al 1.er intento | 100% |
| Generar válido al 1.er intento | 100% |
| Limitaciones repetidas · borrador del modelo | 6 |
| Limitaciones repetidas · respuesta final | 0 |
| Textos del modelo que hablan del catálogo | 17 |
| Ids en el texto | 0 |
| Errores del proveedor | 0/20 |
| Tiempo total (mediana) | 4.1 s |
| Tiempo total (peor caso) | 5.2 s |
| Sobre 15 s | 0/20 |
| Entender · buscar · generar (mediana) | 1.7 s · 0.1 s · 2.1 s |
| Tokens entrada / salida (mediana) | 3410 / 501 |
| Esperas (límite de uso o error temporal) | 0.0 s |

Evidencia direccional: 10 casos; los porcentajes no son estadística firme.

## Por necesidad

Cuenta sobre las corridas válidas: detectada · había un aceptable en el top 3 (techo) · eligió un aceptable. Sin aceptables, se espera que no elija nada.

| Caso · necesidad | Aceptables | gemini |
|---|---|---|
| `inmobiliaria-portal` · search | OpenSearch | det 2/2 · techo 2 · eligió 2 |
| `inmobiliaria-portal` · storage | (ninguno) | det 2/2 · eligió algo 1 |
| `agencia-viajes-web` · frontend | next.js, astro, nuxt | det 2/2 · techo 2 · eligió 2 |
| `cooperativa-api` · backend | fastapi, django, flask | det 2/2 · techo 2 · eligió 2 |
| `cooperativa-api` · database | (ninguno) | det 2/2 · eligió algo 2 |
| `colegio-avisos` · data-processing | airflow, prefect, dagster | det 1/2 · techo 0 · eligió 0 |
| `colegio-avisos` · communication | (ninguno) | det 2/2 · eligió algo 0 |
| `ong-voluntarios` · auth | (ninguno) | det 2/2 · eligió algo 0 |
| `ong-voluntarios` · storage | (ninguno) | det 2/2 · eligió algo 0 |
| `gimnasio-cobros` · payments | (ninguno) | det 2/2 · eligió algo 0 |
| `gimnasio-cobros` · communication | (ninguno) | det 2/2 · eligió algo 0 |
| `gimnasio-cobros` · database | (ninguno) | det 2/2 · eligió algo 2 |
| `repuestos-buscador` · search | OpenSearch | det 2/2 · techo 2 · eligió 2 |
| `repuestos-buscador` · observability | prometheus | det 2/2 · techo 2 · eligió 1 |
| `restaurantes-reportes` · data-processing | airflow, prefect, dagster | det 2/2 · techo 1 · eligió 0 |
| `restaurantes-reportes` · communication | (ninguno) | det 2/2 · eligió algo 2 |
| `energia-medidores` · messaging | kafka | det 2/2 · techo 2 · eligió 2 |
| `energia-medidores` · database | ClickHouse | det 2/2 · techo 2 · eligió 2 |
| `energia-medidores` · analytics | grafana | det 0/2 · techo 0 · eligió 0 |
| `contable-chatbot` · ai | ollama, vllm | det 2/2 · techo 2 · eligió 2 |
| `contable-chatbot` · auth | (ninguno) | det 2/2 · eligió algo 2 |

## Para revisar a mano (corrida 1)

Rúbrica de 1 a 3: español · `rationale` ligado al negocio · coherencia (título, resumen y cajas dicen lo mismo).

### `inmobiliaria-portal`

> Estamos construyendo el portal web de una inmobiliaria. Los clientes tienen que poder buscar propiedades escribiendo cosas como 'apartamento con balcón cerca del metro', y los agentes suben las fotos y los planos de cada inmueble.

**gemini**
- `ok` · Portal Inmobiliario con Búsqueda Semántica
- Proponemos una solución basada en OpenSearch para la búsqueda de propiedades mediante texto libre, complementada con herramientas de almacenamiento no incluidas en el catálogo.
- **OpenSearch** (`opensearch-project/OpenSearch`), Motor de búsqueda: Resuelve la búsqueda semántica de texto libre permitiendo encontrar propiedades según las descripciones de los usuarios. Cuenta con licencia Apache-2.0 y su último cambio fue hace un mes.
- Limitación: Almacenamiento: el catálogo no tiene herramientas para «almacenamiento de archivos multimedia».
- Supuesto: Se requiere un sistema de almacenamiento externo para gestionar las fotos y los planos subidos por los agentes.
- Rúbrica: español _ · rationale _ · coherencia _

### `agencia-viajes-web`

> Somos una agencia de viajes y vamos a rehacer nuestro sitio. Necesitamos un framework web para construir páginas de destinos que carguen muy rápido y se posicionen bien en Google.

**gemini**
- `ok` · Propuesta de framework web para agencia de viajes
- Implementamos un framework web optimizado para sitios orientados a contenido, asegurando alta velocidad de carga y posicionamiento en motores de búsqueda para las páginas de destinos.
- **Astro** (`withastro/astro`), Framework web: Es un framework web diseñado específicamente para sitios orientados a contenido como las páginas de destinos de la agencia, permitiendo una carga muy rápida gracias a su arquitectura basada en islas.
- Limitación: La licencia de la herramienta elegida no fue identificada por GitHub.
- Limitación: No se incluyen herramientas para pruebas automatizadas ni para la gestión completa del backend o base de datos.
- Supuesto: La agencia cuenta con desarrolladores con experiencia en JavaScript o en el ecosistema de componentes de Astro.
- Supuesto: El contenido de los destinos se gestionará mediante archivos estáticos o un CMS headless integrado.
- Rúbrica: español _ · rationale _ · coherencia _

### `cooperativa-api`

> Somos dos desarrolladores de Python en una cooperativa agrícola. Queremos elegir un framework para la API que registra las entregas de café de cada productor, y una base de datos relacional para guardar esos registros.

**gemini**
- `ok` · Arquitectura de API y base de datos para cooperativa
- Se propone el uso de FastAPI para construir la API y SQLModel como herramienta para estructurar y guardar los registros de entregas de café en una base de datos relacional. Ambas herramientas ofrecen un desarrollo rápido, rendimiento y compatibilidad con Python.
- **FastAPI** (`fastapi/fastapi`), Framework para la API: Es un framework de alto rendimiento, fácil de aprender y rápido de codificar, ideal para construir la API que registra las entregas de café.
- **SQLModel** (`fastapi/sqlmodel`), Gestión de base de datos relacional: Está diseñado para bases de datos SQL en Python con foco en la simplicidad, compatibilidad y robustez, facilitando el guardado de los registros.
- Supuesto: Se asume que la cooperativa agrícola requiere un sistema desplegable en un entorno de producción estándar con soporte para Python.
- Rúbrica: español _ · rationale _ · coherencia _

### `colegio-avisos`

> Un colegio quiere una aplicación donde los profesores registren la asistencia. Cada noche debe calcular el porcentaje de asistencia de cada estudiante y avisar por correo o SMS a los padres cuando baje del 80 %.

**gemini**
- `ok` · Sistema open source para registro y control de asistencia escolar
- Propuesta para implementar un sistema donde los profesores registren la asistencia y se almacene de forma segura. La funcionalidad de cálculo nocturno y la comunicación por correo o SMS a los padres quedan fuera de las herramientas seleccionadas.
- **etcd** (`etcd-io/etcd`), Almacenamiento de registros de asistencia: Proporciona un almacén de valores clave distribuido y confiable para guardar los datos críticos del sistema de asistencia del colegio. Su licencia es Apache-2.0 y su desarrollo se mantiene activo con actualizaciones recientes.
- Limitación: Comunicación: el catálogo no tiene herramientas para «envío de correos y mensajes de texto».
- Limitación: La propuesta no incluye la lógica para el cálculo nocturno del porcentaje de asistencia.
- Limitación: No se dispone de herramientas en el catálogo para el envío de correos o SMS a los padres.
- Supuesto: El colegio cuenta con personal técnico para desplegar y mantener un almacén de valores clave distribuido.
- Supuesto: La necesidad de comunicación con los padres por correo o SMS requiere desarrollos o integraciones adicionales no cubiertas por el catálogo.
- Rúbrica: español _ · rationale _ · coherencia _

### `ong-voluntarios`

> Una ONG de voluntariado quiere que sus voluntarios entren con su cuenta de Google y guardar los certificados escaneados de cada uno en PDF.

**gemini**
- `no_evidence` · Sistema de gestión para voluntarios
- Propuesta de infraestructura para permitir autenticación externa y gestión segura de datos para la ONG, dejando el almacenamiento de archivos sin una herramienta directa en el catálogo.
- Limitación: Autenticación: ninguna herramienta del catálogo encaja. Ninguno de los candidatos disponibles en el catálogo ofrece autenticación de usuarios mediante proveedores externos como Google.
- Limitación: Almacenamiento: ninguna herramienta del catálogo encaja. Ninguno de los candidatos del catálogo provee almacenamiento de archivos y documentos para guardar certificados en PDF.
- Supuesto: Se asume que la ONG requiere un sistema web centralizado para operar.
- Supuesto: Se asume que la integración con Google se resolverá mediante un servicio externo de identidad.
- Rúbrica: español _ · rationale _ · coherencia _

### `gimnasio-cobros`

> Un gimnasio con tres sedes quiere cobrar las mensualidades en línea, avisar por WhatsApp a los socios que se atrasan en el pago y guardar el historial de pagos en una base de datos relacional.

**gemini**
- `ok` · Sistema de gestión de pagos y base de datos para gimnasio
- Esta propuesta integra una base de datos relacional para guardar el historial de pagos del gimnasio en tres sedes. Las necesidades de cobros en línea y avisos por WhatsApp quedan pendientes de herramientas específicas ya que no se encuentran en el catálogo.
- **SQLAlchemy** (`sqlalchemy/sqlalchemy`), Almacenamiento de datos: Permite gestionar el almacenamiento en base de datos relacional ofreciendo un conjunto de herramientas para Python y SQL. Su licencia es MIT y cuenta con mantenimiento activo reciente.
- Limitación: Pagos: el catálogo no tiene herramientas para «cobro de mensualidades en linea».
- Limitación: Comunicación: el catálogo no tiene herramientas para «envio de mensajes por whatsapp».
- Supuesto: El gimnasio cuenta con personal técnico capaz de integrar soluciones mediante código en Python.
- Supuesto: Se requiere procesar cobros en línea a través de una pasarela de pagos externa.
- Supuesto: Se requiere una API para enviar mensajes automatizados por WhatsApp.
- Rúbrica: español _ · rationale _ · coherencia _

### `repuestos-buscador`

> Tenemos una tienda en línea de repuestos para motos con la API hecha en Django. Queremos agregar un buscador de productos por nombre o referencia (el equipo pensaba en Elasticsearch) y medir la latencia y los errores de la API.

**gemini**
- `ok` · Arquitectura de búsqueda y observabilidad para tienda online
- Esta propuesta implementa un motor de búsqueda distribuido y RESTful para los productos y una plataforma de visualización de métricas para monitorear la latencia y los errores de la API en Django.
- **OpenSearch** (`opensearch-project/OpenSearch`), Motor de búsqueda de productos: Provee un motor de búsqueda distribuido y RESTful bajo licencia Apache-2.0, ideal para buscar productos por nombre o referencia en la tienda en línea.
- **Grafana** (`grafana/grafana`), Plataforma de visualización y monitoreo: Ofrece una plataforma abierta y componible para la visualización y análisis de datos de observabilidad, permitiendo supervisar la latencia y los errores de la API.
- Limitación: El usuario mencionó Elasticsearch, pero la herramienta elegida para la búsqueda es OpenSearch.
- Supuesto: Se asume que la API en Django cuenta con instrumentación para exportar métricas de latencia y errores hacia la plataforma de observabilidad.
- Rúbrica: español _ · rationale _ · coherencia _

### `restaurantes-reportes`

> Una cadena de doce restaurantes quiere procesar cada noche las ventas del día de todos sus locales para recalcular el inventario de cada uno, y mandar por correo el reporte a cada gerente a primera hora.

**gemini**
- `ok` · Sistema nocturno de procesamiento de inventario y reportes
- La propuesta utiliza Apache Spark para procesar por lotes las ventas nocturnas y recalcular el inventario de los locales. Alertmanager se encarga de enviar las notificaciones automatizadas con los reportes generados a los gerentes.
- **Apache Spark** (`apache/spark`), Procesamiento de datos por lotes: Es un motor de análisis unificado para el procesamiento de datos a gran escala, ideal para recalcular el inventario de cada local a partir de las ventas del día.
- **Alertmanager** (`prometheus/alertmanager`), Envío de notificaciones por correo: Permite gestionar el envío de notificaciones por correo electrónico para alertar o reportar información a los gerentes a primera hora.
- Limitación: Apache Beam y Apache Flink podrían complementar el procesamiento de datos, pero Spark cubre adecuadamente el requerimiento por lotes.
- Supuesto: Se asume que los datos de ventas de los doce restaurantes se consolidan en una fuente accesible cada noche.
- Supuesto: Se asume que Alertmanager puede configurarse para enviar reportes informativos por correo electrónico más allá de alertas de monitoreo.
- Rúbrica: español _ · rationale _ · coherencia _

### `energia-medidores`

> Una empresa de energía recibe lecturas de 50.000 medidores cada 15 minutos. Quiere recibirlas en streaming con Kafka, guardarlas en una base de datos para series de tiempo como InfluxDB y mostrar tableros de consumo en Grafana.

**gemini**
- `ok` · Sistema de procesamiento y visualización de consumo energético
- Esta propuesta implementa una plataforma para recibir lecturas de medidores en streaming y mostrarlas en tableros de visualización. Cubre la ingesta mediante streaming y la capa de visualización, apoyándose en una base de datos analítica como alternativa.
- **ClickHouse** (`ClickHouse/ClickHouse`), Almacenamiento analítico de alta velocidad: ClickHouse es un sistema de base de datos para análisis en tiempo real bajo licencia Apache-2.0, con actualización reciente, útil para manejar grandes volúmenes de datos de medidores.
- **Apache Kafka** (`apache/kafka`), Plataforma de streaming de eventos: Apache Kafka provee la plataforma distribuida de streaming de eventos solicitada por el usuario para recibir las lecturas de los medidores en tiempo real.
- **Grafana** (`grafana/grafana`), Visualización de tableros de consumo: Grafana ofrece la plataforma de visualización y tableros para mostrar el consumo energético, tal como pidió el usuario.
- Limitación: El usuario solicitó específicamente InfluxDB, pero no está disponible entre los candidatos de base de datos; se eligió ClickHouse como alternativa analítica.
- Limitación: El catálogo no incluye una herramienta de procesamiento intermedio para transformar los eventos de Kafka antes de guardarlos.
- Supuesto: La empresa cuenta con infraestructura para operar clústeres distribuidos de mensajería y bases de datos analíticas.
- Rúbrica: español _ · rationale _ · coherencia _

### `contable-chatbot`

> Un estudio contable quiere un chatbot interno que responda preguntas sobre sus manuales de procedimientos usando un modelo de lenguaje que corra en sus propios servidores, y que solo puedan entrar los empleados con cuenta.

**gemini**
- `ok` · Arquitectura segura para chatbot interno contable
- Esta propuesta implementa un chatbot local para responder consultas sobre manuales de procedimientos y asegura que solo los empleados autenticados accedan al sistema.
- **Ollama** (`ollama/ollama`), Ejecución local de modelos de lenguaje: Permite poner en marcha y ejecutar modelos de lenguaje directamente en sus propios servidores, cumpliendo con el requerimiento de procesamiento local.
- **HashiCorp Vault** (`hashicorp/vault`), Gestión de accesos y secretos: Gestiona el acceso privilegiado y la seguridad del sistema. Su licencia no fue identificada por GitHub, por lo que se debe revisar antes del despliegue.
- Limitación: La herramienta de autenticación seleccionada está orientada a gestión de secretos y accesos privilegiados, por lo que requerirá configuración adicional para la gestión estándar de cuentas de empleados.
- Supuesto: Se asume que la empresa cuenta con infraestructura propia con soporte para contenedores y la potencia de cómputo necesaria para correr modelos de lenguaje.
- Rúbrica: español _ · rationale _ · coherencia _
