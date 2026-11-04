# Comparación de modelos · flujo completo del asistente

Generado con `python -m ai.eval.run_assistant_eval` el 2026-11-04 a las 15:05. 10 casos × 2 corridas por proveedor; catálogo de 100 repos; umbral 0.19; el modelo ve 5 candidatos por necesidad y se registran 5. La llamada de calentamiento no se cuenta.

## Modelos

| Proveedor | Modelo | Razonamiento | Arranque en frío |
|---|---|---|---|
| gemini | `gemini-3.5-flash-lite` | por defecto | 2.0 s |

## Resumen

| Métrica | gemini |
|---|---|
| Status correcto | 83% |
| Respuesta válida | 100% |
| Necesidades detectadas | 89% |
| Techo de la búsqueda (top 5) | 94% |
| Techo con 5 candidatos | 94% |
| Eligió un aceptable (donde había) | 67% |
| Se abstuvo (donde no había) | 68% |
| Acierto de punta a punta (comparable entre k) | 62% |
| Sin caja donde el caso no tiene herramientas | 72% |
| Eligió el primer candidato | 33% |
| Consistencia entre corridas | 88% |
| Entender válido al 1.er intento | 100% |
| Generar válido al 1.er intento | 100% |
| Limitaciones repetidas · borrador del modelo | 7 |
| Limitaciones repetidas · respuesta final | 0 |
| Textos del modelo que hablan del catálogo | 3 |
| Ids en el texto | 0 |
| Errores del proveedor | 2/20 |
| Tiempo total (mediana) | 5.0 s |
| Tiempo total (peor caso) | 13.3 s |
| Sobre 15 s | 0/18 |
| Entender · buscar · generar (mediana) | 1.9 s · 0.1 s · 2.0 s |
| Tokens entrada / salida (mediana) | 3420 / 498 |
| Esperas (límite de uso o error temporal) | 0.0 s |

Evidencia direccional: 10 casos; los porcentajes no son estadística firme.

## Por necesidad

Cuenta sobre las corridas válidas: detectada · había un aceptable en el top 3 (techo) · eligió un aceptable. Sin aceptables, se espera que no elija nada.

| Caso · necesidad | Aceptables | gemini |
|---|---|---|
| `inmobiliaria-portal` · search | OpenSearch | det 1/1 · techo 1 · eligió 1 |
| `inmobiliaria-portal` · storage | (ninguno) | det 1/1 · eligió algo 1 |
| `agencia-viajes-web` · frontend | next.js, astro, nuxt | det 2/2 · techo 2 · eligió 2 |
| `cooperativa-api` · backend | fastapi, django, flask | det 2/2 · techo 2 · eligió 2 |
| `cooperativa-api` · database | (ninguno) | det 2/2 · eligió algo 2 |
| `colegio-avisos` · data-processing | airflow, prefect, dagster | det 0/2 · techo 0 · eligió 0 |
| `colegio-avisos` · communication | (ninguno) | det 2/2 · eligió algo 0 |
| `ong-voluntarios` · auth | (ninguno) | det 2/2 · eligió algo 0 |
| `ong-voluntarios` · storage | (ninguno) | det 2/2 · eligió algo 0 |
| `gimnasio-cobros` · payments | (ninguno) | det 2/2 · eligió algo 0 |
| `gimnasio-cobros` · communication | (ninguno) | det 2/2 · eligió algo 0 |
| `gimnasio-cobros` · database | (ninguno) | det 2/2 · eligió algo 2 |
| `repuestos-buscador` · search | OpenSearch | det 2/2 · techo 2 · eligió 2 |
| `repuestos-buscador` · observability | prometheus | det 2/2 · techo 2 · eligió 0 |
| `restaurantes-reportes` · data-processing | airflow, prefect, dagster | det 2/2 · techo 2 · eligió 0 |
| `restaurantes-reportes` · communication | (ninguno) | det 2/2 · eligió algo 0 |
| `energia-medidores` · messaging | kafka | det 2/2 · techo 2 · eligió 2 |
| `energia-medidores` · database | ClickHouse | det 2/2 · techo 1 · eligió 0 |
| `energia-medidores` · analytics | grafana | det 0/2 · techo 0 · eligió 0 |
| `contable-chatbot` · ai | ollama, vllm | det 1/1 · techo 1 · eligió 1 |
| `contable-chatbot` · auth | (ninguno) | det 1/1 · eligió algo 0 |

## Para revisar a mano (corrida 1)

Rúbrica de 1 a 3: español · `rationale` ligado al negocio · coherencia (título, resumen y cajas dicen lo mismo).

### `inmobiliaria-portal`

> Estamos construyendo el portal web de una inmobiliaria. Los clientes tienen que poder buscar propiedades escribiendo cosas como 'apartamento con balcón cerca del metro', y los agentes suben las fotos y los planos de cada inmueble.

**gemini**
- `ok` · Sistema de búsqueda y almacenamiento para portal inmobiliario
- Esta propuesta integra un motor de búsqueda distribuido para localizar inmuebles mediante consultas avanzadas y un almacén de valores clave para la gestión de datos críticos del sistema. Faltan componentes específicos de almacenamiento de objetos para las fotos y planos de las propiedades.
- **OpenSearch** (`opensearch-project/OpenSearch`), Motor de búsqueda: Resuelve la necesidad de realizar búsquedas distribuidas y RESTful para que los clientes encuentren propiedades escribiendo descripciones detalladas. Cuenta con la licencia Apache-2.0 y actividad reciente en su desarrollo.
- **etcd** (`etcd-io/etcd`), Almacenamiento de datos clave-valor: Proporciona un almacenamiento distribuido y confiable para datos críticos del sistema. Utiliza la licencia Apache-2.0 y recibe mantenimiento constante.
- Limitación: Los candidatos de almacenamiento disponibles no gestionan archivos binarios de forma nativa para las fotos y planos requeridos por los agentes.
- Supuesto: Se asume que los agentes inmobiliarios se autenticarán mediante un sistema externo no cubierto por los candidatos.
- Supuesto: Las fotos y planos de los inmuebles requerirán una solución de almacenamiento de objetos que no está disponible entre los candidatos de almacenamiento.
- Rúbrica: español _ · rationale _ · coherencia _

### `agencia-viajes-web`

> Somos una agencia de viajes y vamos a rehacer nuestro sitio. Necesitamos un framework web para construir páginas de destinos que carguen muy rápido y se posicionen bien en Google.

**gemini**
- `ok` · Arquitectura web rápida para agencia de viajes
- Proponemos una solución basada en Next.js para construir las páginas de destinos con renderizado híbrido, asegurando tiempos de carga rápidos y un posicionamiento óptimo en buscadores.
- **Next.js** (`vercel/next.js`), Framework web para el renderizado y construcción del sitio: Es el framework de React ideal para desarrollar páginas de destinos que cargan muy rápido y se posicionan bien en Google gracias a sus capacidades de compilación y renderizado híbrido. Cuenta con licencia MIT y alta actividad reciente.
- Limitación: La propuesta no incluye un sistema de gestión de contenidos (CMS) para que la agencia actualice los destinos de forma visual.
- Supuesto: Suponemos que el equipo de desarrollo tiene experiencia previa trabajando con React y JavaScript o TypeScript.
- Rúbrica: español _ · rationale _ · coherencia _

### `cooperativa-api`

> Somos dos desarrolladores de Python en una cooperativa agrícola. Queremos elegir un framework para la API que registra las entregas de café de cada productor, y una base de datos relacional para guardar esos registros.

**gemini**
- `ok` · Arquitectura de API y Base de Datos para Cooperativa Agrícola
- Proponemos el uso de un framework de alto rendimiento para la API y una herramienta robusta de bases de datos para gestionar los registros de entrega de café de los productores.
- **FastAPI** (`fastapi/fastapi`), Framework para la API: Es un framework de alto rendimiento, fácil de aprender y rápido de codificar, ideal para construir la API que registra las entregas de café de cada productor.
- **SQLModel** (`fastapi/sqlmodel`), Gestor de base de datos relacional: Está diseñado para trabajar con bases de datos SQL en Python enfocándose en la simplicidade, compatibilidad y robustez para guardar los registros solicitados.
- Limitación: Flask y otras librerías orientadas a flujos de trabajo como Prefect complementan el ecosistema pero no reemplazan la función principal del framework de API elegido.
- Supuesto: La cooperativa agrícola cuenta con un servidor propio o infraestructura en la nube para desplegar la API y la base de datos.
- Supuesto: El equipo de dos desarrolladores tiene experiencia previa en desarrollo web y Python.
- Rúbrica: español _ · rationale _ · coherencia _

### `colegio-avisos`

> Un colegio quiere una aplicación donde los profesores registren la asistencia. Cada noche debe calcular el porcentaje de asistencia de cada estudiante y avisar por correo o SMS a los padres cuando baje del 80 %.

**gemini**
- `no_evidence` · 
- El catálogo todavía no tiene herramientas para lo que pides: comunicación.
- Limitación: Comunicación: el catálogo no tiene herramientas para «envío de correos o mensajes de texto».
- Rúbrica: español _ · rationale _ · coherencia _

### `ong-voluntarios`

> Una ONG de voluntariado quiere que sus voluntarios entren con su cuenta de Google y guardar los certificados escaneados de cada uno en PDF.

**gemini**
- `no_evidence` · Sistema de gestión documental para certificados de voluntarios
- Esta propuesta integra una solución para el almacenamiento seguro de los certificados escaneados en PDF de los voluntarios. No se encontró ninguna herramienta candidata para cubrir la necesidad de autenticación con cuenta de Google.
- Limitación: Almacenamiento: ninguna herramienta del catálogo encaja. Ninguno de los candidatos analizados sirve para almacenar archivos PDF, ya que la única herramienta disponible es una base de datos clave-valor distribuida.
- Limitación: Autenticación: el catálogo no tiene herramientas para «inicio de sesión federado».
- Supuesto: Se asume que la ONG necesitará integrar un proveedor de identidad externo para la autenticación con Google, ya que no se encontraron candidatos para esa necesidad.
- Rúbrica: español _ · rationale _ · coherencia _

### `gimnasio-cobros`

> Un gimnasio con tres sedes quiere cobrar las mensualidades en línea, avisar por WhatsApp a los socios que se atrasan en el pago y guardar el historial de pagos en una base de datos relacional.

**gemini**
- `ok` · Arquitectura de base de datos relacional para gimnasio
- Se propone una herramienta para gestionar bases de datos relacionales en Python y cumplir con el almacenamiento del historial de pagos. Las necesidades de cobros en línea y avisos por WhatsApp no cuentan con herramientas candidatas en el catálogo proporcionado.
- **SQLModel** (`fastapi/sqlmodel`), Gestión de base de datos relacional: Permite trabajar con bases de datos SQL en Python de forma simple y robusta, facilitando guardar el historial de pagos. Cuenta con licencia MIT y su último cambio fue hace un mes.
- Limitación: Pagos: el catálogo no tiene herramientas para «cobro de mensualidades en linea».
- Limitación: Comunicación: el catálogo no tiene herramientas para «envio de mensajes por whatsapp».
- Limitación: Las herramientas SQLAlchemy y DuckDB encontradas en los candidatos no fueron elegidas por priorizar SQLModel para el desarrollo en Python.
- Supuesto: El gimnasio requiere procesar pagos en línea mediante una pasarela externa no integrada en el sistema actual.
- Supuesto: El envío de mensajes por WhatsApp se realizará mediante una integración con una API externa.
- Rúbrica: español _ · rationale _ · coherencia _

### `repuestos-buscador`

> Tenemos una tienda en línea de repuestos para motos con la API hecha en Django. Queremos agregar un buscador de productos por nombre o referencia (el equipo pensaba en Elasticsearch) y medir la latencia y los errores de la API.

**gemini**
- `ok` · Arquitectura de búsqueda y observabilidad para tienda
- Esta propuesta integra un motor de búsqueda distribuido para localizar repuestos y una plataforma de visualización para monitorear la latencia y los errores de la API en la tienda en línea.
- **OpenSearch** (`opensearch-project/OpenSearch`), Motor de búsqueda de productos: Resuelve la necesidad de un buscador de productos por nombre o referencia mediante un motor de búsqueda distribuido y RESTful bajo licencia Apache-2.0.
- **Grafana** (`grafana/grafana`), Plataforma de visualización y métricas: Permite medir la latencia y los errores de la API a través de su plataforma de observabilidad y visualización de datos bajo licencia AGPL-3.0.
- Limitación: La tecnología Elasticsearch mencionada por el equipo no está entre los candidatos encontrados.
- Limitación: OpenSearch complementa pero no reemplaza directamente al candidato BurntSushi/ripgrep para búsquedas de texto plano en archivos.
- Supuesto: La API en Django se conectará directamente con el motor de búsqueda para procesar las consultas de los usuarios.
- Supuesto: Se cuenta con la infraestructura necesaria para alojar servicios distribuidos.
- Rúbrica: español _ · rationale _ · coherencia _

### `restaurantes-reportes`

> Una cadena de doce restaurantes quiere procesar cada noche las ventas del día de todos sus locales para recalcular el inventario de cada uno, y mandar por correo el reporte a cada gerente a primera hora.

**gemini**
- `ok` · Sistema nocturno de procesamiento de ventas e inventario
- Esta propuesta implementa el procesamiento nocturno de las ventas de los restaurantes para recalcular el inventario de cada local. Quedó sin resolver el envío automatizado por correo del reporte a los gerentes debido a la falta de candidatos para dicha necesidad.
- **Apache Spark** (`apache/spark`), Procesamiento de datos por lotes: Permite realizar un procesamiento de datos a gran escala para procesar cada noche las ventas del día y recalcular el inventario de cada local. Cuenta con una licencia Apache-2.0 y mantenimiento activo reciente.
- Limitación: Comunicación: el catálogo no tiene herramientas para «envío de correos electrónicos».
- Limitación: No se incluye la herramienta para el envío por correo de los reportes a los gerentes, ya que no se encontraron candidatos para cubrir esa necesidad en el catálogo.
- Supuesto: Se asume que los datos de ventas de los doce restaurantes se consolidan en una base de datos o almacenamiento accesible para ser procesados por lotes cada noche.
- Rúbrica: español _ · rationale _ · coherencia _

### `energia-medidores`

> Una empresa de energía recibe lecturas de 50.000 medidores cada 15 minutos. Quiere recibirlas en streaming con Kafka, guardarlas en una base de datos para series de tiempo como InfluxDB y mostrar tableros de consumo en Grafana.

**gemini**
- `ok` · Arquitectura de streaming y tableros para energía
- Se propone una arquitectura basada en Kafka para la ingesta de streaming, Prometheus como base de datos para series temporales y Grafana para la visualización de tableros de consumo. InfluxDB no se encuentra entre los candidatos encontrados.
- **Prometheus** (`prometheus/prometheus`), Base de datos para series temporales: Funciona como un sistema de monitoreo y base de datos de series temporales que se adapta al almacenamiento de las métricas requeridas. Posee licencia Apache-2.0 y actividad reciente.
- **Apache Kafka** (`apache/kafka`), Plataforma de streaming de eventos: Permite recibir las lecturas de los medidores en streaming mediante una plataforma de eventos distribuida. Cuenta con licencia Apache-2.0 y mantenimiento activo.
- **Grafana** (`grafana/grafana`), Visualización de tableros: Ofrece una plataforma componible de observabilidad y visualización de datos para mostrar tableros de consumo. Su licencia es AGPL-3.0 y se mantiene de forma activa.
- Limitación: InfluxDB fue nombrada por el usuario pero no se encuentra entre los candidatos de la base de datos.
- Limitación: El sistema no incluye componentes específicos para la transformación ETL avanzada de los datos de streaming.
- Supuesto: Se asume que la infraestructura cuenta con la capacidad de red necesaria para procesar las lecturas de 50.000 medidores cada 15 minutos.
- Rúbrica: español _ · rationale _ · coherencia _

### `contable-chatbot`

> Un estudio contable quiere un chatbot interno que responda preguntas sobre sus manuales de procedimientos usando un modelo de lenguaje que corra en sus propios servidores, y que solo puedan entrar los empleados con cuenta.

**gemini**
- `ok` · Chatbot interno para manuales de procedimientos contables
- Esta propuesta incluye la ejecución de modelos de lenguaje en servidores propios para el chatbot interno de manuales y la gestión de acceso para empleados. Queda pendiente el desarrollo de la interfaz de usuario del chatbot y la integración con los documentos.
- **Ollama** (`ollama/ollama`), Servidor de inferencia local para el modelo de lenguaje: Permite correr modelos de lenguaje en sus propios servidores de forma sencilla para impulsar el chatbot interno. Cuenta con licencia MIT y actividad reciente.
- Limitación: Autenticación: ninguna herramienta del catálogo encaja. Ninguno de los candidatos analizados proporciona autenticación de usuarios ni gestión de identidad para control de acceso, ya que se centran en secretos, mallas de servicios, certificados, automatización o servidores web.
- Limitación: No se resuelve el almacenamiento ni la recuperación de documentos de los manuales de procedimientos.
- Supuesto: Se asume que la empresa dispone de infraestructura propia con capacidad de cómputo para ejecutar modelos de lenguaje locales.
- Supuesto: El chatbot requiere una interfaz de usuario conversacional que consulte los manuales de procedimientos.
- Rúbrica: español _ · rationale _ · coherencia _
