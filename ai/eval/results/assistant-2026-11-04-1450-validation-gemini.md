# Comparación de modelos · flujo completo del asistente

Generado con `python -m ai.eval.run_assistant_eval` el 2026-11-04 a las 14:50. 10 casos × 2 corridas por proveedor; catálogo de 100 repos; umbral 0.19; el modelo ve 5 candidatos por necesidad y se registran 5. La llamada de calentamiento no se cuenta.

## Modelos

| Proveedor | Modelo | Razonamiento | Arranque en frío |
|---|---|---|---|
| gemini | `gemini-3.5-flash-lite` | por defecto | 1.9 s |

## Resumen

| Métrica | gemini |
|---|---|
| Status correcto | 75% |
| Respuesta válida | 100% |
| Necesidades detectadas | 90% |
| Techo de la búsqueda (top 5) | 89% |
| Techo con 5 candidatos | 89% |
| Eligió un aceptable (donde había) | 94% |
| Se abstuvo (donde no había) | 59% |
| Acierto de punta a punta (comparable entre k) | 83% |
| Sin caja donde el caso no tiene herramientas | 60% |
| Eligió el primer candidato | 60% |
| Consistencia entre corridas | 20% |
| Entender válido al 1.er intento | 100% |
| Generar válido al 1.er intento | 100% |
| Limitaciones repetidas · borrador del modelo | 5 |
| Limitaciones repetidas · respuesta final | 5 |
| Textos del modelo que hablan del catálogo | 11 |
| Ids en el texto | 0 |
| Errores del proveedor | 0/20 |
| Tiempo total (mediana) | 3.6 s |
| Tiempo total (peor caso) | 10.1 s |
| Sobre 15 s | 0/20 |
| Entender · buscar · generar (mediana) | 1.5 s · 0.1 s · 2.0 s |
| Tokens entrada / salida (mediana) | 3391 / 478 |
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
| `colegio-avisos` · data-processing | airflow, prefect, dagster | det 0/2 · techo 0 · eligió 0 |
| `colegio-avisos` · communication | (ninguno) | det 2/2 · eligió algo 0 |
| `ong-voluntarios` · auth | (ninguno) | det 2/2 · eligió algo 0 |
| `ong-voluntarios` · storage | (ninguno) | det 2/2 · eligió algo 1 |
| `gimnasio-cobros` · payments | (ninguno) | det 2/2 · eligió algo 0 |
| `gimnasio-cobros` · communication | (ninguno) | det 2/2 · eligió algo 0 |
| `gimnasio-cobros` · database | (ninguno) | det 2/2 · eligió algo 2 |
| `repuestos-buscador` · search | OpenSearch | det 2/2 · techo 2 · eligió 2 |
| `repuestos-buscador` · observability | prometheus | det 2/2 · techo 2 · eligió 2 |
| `restaurantes-reportes` · data-processing | airflow, prefect, dagster | det 2/2 · techo 1 · eligió 0 |
| `restaurantes-reportes` · communication | (ninguno) | det 2/2 · eligió algo 0 |
| `energia-medidores` · messaging | kafka | det 2/2 · techo 2 · eligió 2 |
| `energia-medidores` · database | ClickHouse | det 2/2 · techo 1 · eligió 1 |
| `energia-medidores` · analytics | grafana | det 0/2 · techo 0 · eligió 0 |
| `contable-chatbot` · ai | ollama, vllm | det 2/2 · techo 2 · eligió 2 |
| `contable-chatbot` · auth | (ninguno) | det 2/2 · eligió algo 2 |

## Para revisar a mano (corrida 1)

Rúbrica de 1 a 3: español · `rationale` ligado al negocio · coherencia (título, resumen y cajas dicen lo mismo).

### `inmobiliaria-portal`

> Estamos construyendo el portal web de una inmobiliaria. Los clientes tienen que poder buscar propiedades escribiendo cosas como 'apartamento con balcón cerca del metro', y los agentes suben las fotos y los planos de cada inmueble.

**gemini**
- `ok` · Portal Inmobiliario con Búsqueda Semántica
- Esta propuesta implementa un motor de búsqueda avanzado para el portal de la inmobiliaria, permitiendo consultas semánticas y por similitud de vectores. Queda pendiente el almacenamiento persistente de archivos multimedia como fotos y planos.
- **OpenSearch** (`opensearch-project/OpenSearch`), Motor de búsqueda: Resuelve la necesidad de realizar búsquedas avanzadas en el portal web mediante un motor distribuido y con mantenimiento activo. Utiliza la licencia Apache-2.0.
- Limitación: Almacenamiento: el catálogo no tiene herramientas para «almacenamiento de archivos multimedia».
- Limitación: No se incluye una herramienta específica para el almacenamiento de archivos y gestión de imágenes para los agentes.
- Supuesto: Se asume que la base de datos relacional principal del sistema se complementará para el almacenamiento de archivos o se utilizará un servicio externo para las fotos y planos.
- Supuesto: El negocio requiere una interfaz web accesible para clientes y agentes.
- Rúbrica: español _ · rationale _ · coherencia _

### `agencia-viajes-web`

> Somos una agencia de viajes y vamos a rehacer nuestro sitio. Necesitamos un framework web para construir páginas de destinos que carguen muy rápido y se posicionen bien en Google.

**gemini**
- `ok` · Arquitectura web de alto rendimiento para agencia de viajes
- Proponemos el uso de un framework moderno enfocado en la entrega de contenido y rendimiento para optimizar la velocidad de carga y el posicionamiento en buscadores de las páginas de destinos turísticos. La solución cubre completamente el requerimiento principal del proyecto.
- **Astro** (`withastro/astro`), Framework web para contenido: Es un framework optimizado para sitios orientados a contenido que permite construir páginas de destinos con excelente rendimiento y velocidad de carga. Su arquitectura basada en islas reduce el JavaScript enviado al cliente, beneficiando directamente el posicionamiento en Google.
- Limitación: La licencia de la herramienta principal no está identificada por GitHub, por lo que se recomienda verificar sus términos de uso antes de implementarla en producción.
- Supuesto: Suponemos que el sitio web se conectará posteriormente a una API externa o CMS para la gestión dinámica de los paquetes de viaje y destinos.
- Rúbrica: español _ · rationale _ · coherencia _

### `cooperativa-api`

> Somos dos desarrolladores de Python en una cooperativa agrícola. Queremos elegir un framework para la API que registra las entregas de café de cada productor, y una base de datos relacional para guardar esos registros.

**gemini**
- `ok` · Arquitectura de API y Base de Datos para Cooperativa Agrícola
- Proponemos el uso de FastAPI para construir la API que registra las entregas de café y SQLModel para gestionar la base de datos relacional en Python.
- **FastAPI** (`fastapi/fastapi`), Framework para la API: Es un framework de alto rendimiento, fácil de aprender y rápido de codificar, ideal para crear la API que registra las entregas de café.
- **SQLModel** (`fastapi/sqlmodel`), Base de datos relacional: Permite manejar bases de datos SQL en Python con simplicidad, compatibilidad y robustez, adaptándose a las necesidades de la cooperativa.
- Limitación: No se incluyó un ORM puro como SQLAlchemy, ya que SQLModel integra de forma nativa la validación con Pydantic para el ecosistema de FastAPI.
- Supuesto: La cooperativa cuenta con infraestructura propia para hospedar la API y la base de datos.
- Rúbrica: español _ · rationale _ · coherencia _

### `colegio-avisos`

> Un colegio quiere una aplicación donde los profesores registren la asistencia. Cada noche debe calcular el porcentaje de asistencia de cada estudiante y avisar por correo o SMS a los padres cuando baje del 80 %.

**gemini**
- `no_evidence` · 
- El catálogo todavía no tiene herramientas para lo que pides: comunicación.
- Limitación: Comunicación: el catálogo no tiene herramientas para «envio de correos y mensajes de texto».
- Rúbrica: español _ · rationale _ · coherencia _

### `ong-voluntarios`

> Una ONG de voluntariado quiere que sus voluntarios entren con su cuenta de Google y guardar los certificados escaneados de cada uno en PDF.

**gemini**
- `ok` · Sistema de gestión para ONG de voluntarios
- La propuesta establece la infraestructura base para la ONG mediante la gestión de certificados TLS y almacenamiento distribuido. No se encontraron herramientas de autenticación de usuarios que permitan el inicio de sesión con Google en el catálogo actual.
- **Almacenamiento** (`etcd-io/etcd`), Base de datos clave-valor: Proporciona un almacén distribuido y confiable para datos críticos del sistema, aunque etcd está optimizado para metadatos y no directamente para almacenar archivos PDF pesados.
- Limitación: Autenticación: ninguna herramienta del catálogo encaja. Ninguno de los candidatos disponibles en el catálogo resuelve la autenticación de usuarios ni permite la integración con proveedores externos como Google.
- Limitación: La herramienta de autenticación solicitada mediante Google no está disponible entre los candidatos evaluados.
- Supuesto: Se asume que la ONG cuenta con un entorno Kubernetes para desplegar las herramientas de infraestructura seleccionadas.
- Supuesto: La aplicación final requerirá un servicio adicional de almacenamiento de objetos, como S3, para guardar los archivos PDF de los certificados.
- Rúbrica: español _ · rationale _ · coherencia _

### `gimnasio-cobros`

> Un gimnasio con tres sedes quiere cobrar las mensualidades en línea, avisar por WhatsApp a los socios que se atrasan en el pago y guardar el historial de pagos en una base de datos relacional.

**gemini**
- `ok` · Sistema de gestión para historial de pagos de gimnasio
- Esta propuesta implementa el almacenamiento seguro y eficiente del historial de pagos requerido por el negocio utilizando herramientas orientadas a Python y SQL. Las necesidades de cobros en línea y avisos por WhatsApp no cuentan con herramientas en este catálogo y quedan pendientes de integración externa.
- **SQLModel** (`fastapi/sqlmodel`), ORM para la base de datos relacional: Permite interactuar con bases de datos relacionales SQL en Python de forma sencilla y robusta para guardar el historial de pagos. Su licencia es MIT y cuenta con mantenimiento reciente.
- Limitación: Pagos: el catálogo no tiene herramientas para «cobro de mensualidades en linea».
- Limitación: Comunicación: el catálogo no tiene herramientas para «envio de mensajes por whatsapp».
- Limitación: La propuesta no incluye pasarelas para cobrar las mensualidades en línea.
- Limitación: La propuesta no incluye servicios para enviar avisos por WhatsApp a los socios atrasados.
- Supuesto: El gimnasio cuenta con personal técnico para integrar pasarelas de pago y APIs de mensajería.
- Supuesto: Se requiere procesar pagos en línea mediante plataformas externas y enviar mensajes automatizados por WhatsApp.
- Rúbrica: español _ · rationale _ · coherencia _

### `repuestos-buscador`

> Tenemos una tienda en línea de repuestos para motos con la API hecha en Django. Queremos agregar un buscador de productos por nombre o referencia (el equipo pensaba en Elasticsearch) y medir la latencia y los errores de la API.

**gemini**
- `ok` · Arquitectura de búsqueda y observabilidad para tienda de motos
- Esta propuesta integra un motor de búsqueda distribuido para localizar repuestos y un sistema de monitoreo para medir la latencia y los errores de la API en la tienda en línea.
- **OpenSearch** (`opensearch-project/OpenSearch`), Motor de búsqueda: Provee un motor de búsqueda distribuido y RESTful bajo licencia Apache-2.0, ideal para implementar el buscador de productos por nombre o referencia con mantenimiento activo.
- **Prometheus** (`prometheus/prometheus`), Sistema de monitoreo: Permite recolectar y almacenar métricas de series temporales bajo licencia Apache-2.0 para medir la latencia y los errores de la API.
- Limitación: El equipo mencionó Elasticsearch, pero se seleccionó OpenSearch como alternativa compatible y de código abierto.
- Limitación: La solución no incluye herramientas específicas de pruebas o interfaces de usuario adicionales.
- Supuesto: La API de Django se conectará directamente a OpenSearch para las consultas de los usuarios y expondrá métricas compatibles con Prometheus.
- Rúbrica: español _ · rationale _ · coherencia _

### `restaurantes-reportes`

> Una cadena de doce restaurantes quiere procesar cada noche las ventas del día de todos sus locales para recalcular el inventario de cada uno, y mandar por correo el reporte a cada gerente a primera hora.

**gemini**
- `ok` · Sistema nocturno de procesamiento de ventas e inventario
- La propuesta implementa un motor de procesamiento unificado por lotes para calcular el inventario de los locales. Queda pendiente el envío automatizado de correos electrónicos, ya que la herramienta disponible no cumple con esa función específica.
- **Apache Beam** (`apache/beam`), Procesamiento nocturno de ventas e inventario: Apache Beam ofrece un modelo de programación unificado para procesamiento de datos por lotes, ideal para procesar cada noche las ventas del día y recalcular el inventario. Su licencia es Apache-2.0 y cuenta con actividad reciente.
- Limitación: Comunicación: ninguna herramienta del catálogo encaja. Ningún candidato disponible realiza envío de correos electrónicos a gerentes; Ansible es una plataforma de automatización de IT para despliegues y configuración, no un servicio de mensajería o correo.
- Limitación: No se resolvió la necesidad de mandar por correo el reporte a cada gerente porque la única herramienta de comunicación disponible no cumple con dicha función.
- Supuesto: Se asume que los datos de ventas de los doce restaurantes se consolidan en un origen accesible para el procesamiento nocturno.
- Rúbrica: español _ · rationale _ · coherencia _

### `energia-medidores`

> Una empresa de energía recibe lecturas de 50.000 medidores cada 15 minutos. Quiere recibirlas en streaming con Kafka, guardarlas en una base de datos para series de tiempo como InfluxDB y mostrar tableros de consumo en Grafana.

**gemini**
- `ok` · Sistema de monitoreo de consumo energético en streaming
- La arquitectura propuesta procesa el flujo masivo de lecturas de medidores mediante una plataforma de eventos distribuida, almacena los datos en un sistema optimizado para series de tiempo y visualiza los tableros de consumo en tiempo real.
- **Prometheus** (`prometheus/prometheus`), Almacenamiento de series temporales: Provee el sistema de base de datos de series temporales necesario para registrar el consumo energético. Cuenta con licencia Apache-2.0 y actividad reciente.
- **Apache Kafka** (`apache/kafka`), Ingesta de eventos en streaming: Funciona como plataforma de streaming de eventos distribuida para recibir las lecturas de los medidores. Utiliza licencia Apache-2.0 y se mantiene activamente.
- **Grafana** (`grafana/grafana`), Visualización de tableros de consumo: Permite crear tableros de visualización de datos y analítica para mostrar el consumo energético. Posee licencia AGPL-3.0 y actualización reciente.
- Limitación: El usuario solicitó InfluxDB como base de datos, pero se seleccionó Prometheus debido a que no está disponible en los candidatos.
- Supuesto: Se asume que la empresa cuenta con la infraestructura necesaria para desplegar clústeres distribuidos de mensajería y bases de datos.
- Rúbrica: español _ · rationale _ · coherencia _

### `contable-chatbot`

> Un estudio contable quiere un chatbot interno que responda preguntas sobre sus manuales de procedimientos usando un modelo de lenguaje que corra en sus propios servidores, y que solo puedan entrar los empleados con cuenta.

**gemini**
- `ok` · Chatbot interno seguro para estudio contable
- Esta propuesta implementa un servidor de inferencia local para ejecutar modelos de lenguaje con Ollama y protege el acceso con certificados TLS en un servidor web Caddy. El sistema cumple con los requerimientos de privacidad y control de acceso para los empleados.
- **Ollama** (`ollama/ollama`), Servidor de modelos de lenguaje: Permite correr modelos de lenguaje directamente en los servidores propios del estudio contable para responder consultas sobre los manuales de procedimientos.
- **Caddy** (`caddyserver/caddy`), Servidor web y HTTPS: Facilita la gestión de acceso seguro mediante HTTPS para que los empleados accedan al sistema protegido. Su licencia es Apache-2.0.
- Limitación: La autenticación se apoya en cifrado web y HTTPS, pero no incluye un directorio completo de usuarios con gestión de roles avanzados.
- Supuesto: Se asume que la interfaz de usuario del chatbot se conecta mediante HTTP al servidor de inferencia local.
- Rúbrica: español _ · rationale _ · coherencia _
