# Comparación de modelos · flujo completo del asistente

Generado con `python -m ai.eval.run_assistant_eval` el 2026-11-07 a las 07:11. 10 casos × 3 corridas por proveedor; catálogo de 100 repos; umbral 0.23; el modelo ve 5 candidatos por necesidad y se registran 5. La llamada de calentamiento no se cuenta.

## Modelos

| Proveedor | Modelo | Razonamiento | Arranque en frío |
|---|---|---|---|
| gemini | `gemini-3.5-flash-lite` | por defecto | 4.0 s |

## Resumen

| Métrica | gemini |
|---|---|
| Status correcto | 87% |
| Respuesta válida | 100% |
| Necesidades detectadas | 92% |
| Techo de la búsqueda (top 5) | 89% |
| Techo con 5 candidatos | 89% |
| Eligió un aceptable (donde había) | 92% |
| Se abstuvo (donde no había) | 67% |
| Acierto de punta a punta (comparable entre k) | 82% |
| Sin caja donde el caso no tiene herramientas | 67% |
| Eligió el primer candidato | 61% |
| Consistencia entre corridas | 30% |
| Entender válido al 1.er intento | 100% |
| Generar válido al 1.er intento | 100% |
| Limitaciones repetidas · borrador del modelo | 12 |
| Limitaciones repetidas · respuesta final | 0 |
| Textos del modelo que hablan del catálogo | 14 |
| Ids en el texto | 0 |
| Errores del proveedor | 0/30 |
| Tiempo total (mediana) | 4.0 s |
| Tiempo total (peor caso) | 9.3 s |
| Sobre 15 s | 0/30 |
| Entender · buscar · generar (mediana) | 1.8 s · 0.1 s · 2.0 s |
| Tokens entrada / salida (mediana) | 3528 / 546 |
| Esperas (límite de uso o error temporal) | 30.0 s |

Evidencia direccional: 10 casos; los porcentajes no son estadística firme.

## Por corrida

Una diferencia entre versiones menor que el rango entre corridas no se puede atribuir al cambio.

**gemini**

| Métrica | Corrida 1 | Corrida 2 | Corrida 3 | Rango |
|---|---|---|---|---|
| Status correcto | 80% | 90% | 90% | 80% – 90% |
| Eligió un aceptable (donde había) | 88% | 100% | 89% | 88% – 100% |
| Se abstuvo (donde no había) | 64% | 64% | 73% | 64% – 73% |
| Acierto de punta a punta | 78% | 89% | 80% | 78% – 89% |
| Textos del modelo que hablan del catálogo | 3 | 8 | 3 | 3 – 8 |

## Por necesidad

Cuenta sobre las corridas válidas: detectada · había un aceptable en el top 3 (techo) · eligió un aceptable. Sin aceptables, se espera que no elija nada.

| Caso · necesidad | Aceptables | gemini |
|---|---|---|
| `inmobiliaria-portal` · search | OpenSearch | det 3/3 · techo 3 · eligió 3 |
| `inmobiliaria-portal` · storage | (ninguno) | det 3/3 · eligió algo 1 |
| `agencia-viajes-web` · frontend | next.js, astro, nuxt | det 3/3 · techo 3 · eligió 3 |
| `cooperativa-api` · backend | fastapi, django, flask | det 3/3 · techo 3 · eligió 3 |
| `cooperativa-api` · database | (ninguno) | det 3/3 · eligió algo 3 |
| `colegio-avisos` · data-processing | airflow, prefect, dagster | det 1/3 · techo 1 · eligió 1 |
| `colegio-avisos` · communication | (ninguno) | det 3/3 · eligió algo 0 |
| `ong-voluntarios` · auth | (ninguno) | det 3/3 · eligió algo 0 |
| `ong-voluntarios` · storage | (ninguno) | det 3/3 · eligió algo 0 |
| `gimnasio-cobros` · payments | (ninguno) | det 3/3 · eligió algo 0 |
| `gimnasio-cobros` · communication | (ninguno) | det 3/3 · eligió algo 0 |
| `gimnasio-cobros` · database | (ninguno) | det 3/3 · eligió algo 3 |
| `repuestos-buscador` · search | OpenSearch | det 3/3 · techo 3 · eligió 3 |
| `repuestos-buscador` · observability | prometheus | det 3/3 · techo 3 · eligió 2 |
| `restaurantes-reportes` · data-processing | airflow, prefect, dagster | det 3/3 · techo 0 · eligió 0 |
| `restaurantes-reportes` · communication | (ninguno) | det 3/3 · eligió algo 2 |
| `energia-medidores` · messaging | kafka | det 3/3 · techo 3 · eligió 3 |
| `energia-medidores` · database | ClickHouse | det 3/3 · techo 3 · eligió 2 |
| `energia-medidores` · analytics | grafana | det 0/3 · techo 0 · eligió 0 |
| `contable-chatbot` · ai | ollama, vllm | det 3/3 · techo 3 · eligió 3 |
| `contable-chatbot` · auth | (ninguno) | det 3/3 · eligió algo 1 |

## Para revisar a mano (corrida 1)

Rúbrica de 1 a 3: español · `rationale` ligado al negocio · coherencia (título, resumen y cajas dicen lo mismo).

### `inmobiliaria-portal`

> Estamos construyendo el portal web de una inmobiliaria. Los clientes tienen que poder buscar propiedades escribiendo cosas como 'apartamento con balcón cerca del metro', y los agentes suben las fotos y los planos de cada inmueble.

**gemini**
- `ok` · Arquitectura de búsqueda y almacenamiento para portal inmobiliario
- Esta propuesta implementa la búsqueda semántica y textual para las consultas de los clientes sobre las propiedades y el almacenamiento de datos en memoria para el sistema de la inmobiliaria.
- **OpenSearch** (`opensearch-project/OpenSearch`), Motor de búsqueda: Permite realizar búsquedas de texto y análisis de datos de forma distribuida para que los clientes encuentren los inmuebles que buscan. Utiliza licencia Apache-2.0 y cuenta con mantenimiento activo.
- **Redis** (`redis/redis`), Almacenamiento de datos: Funciona como servidor de datos en memoria y motor de consultas para aplicaciones en tiempo real. Su licencia no fue identificada por GitHub y tiene actualizaciones recientes.
- Limitación: La herramienta de almacenamiento elegida está orientada a datos en memoria y caché, por lo que para el almacenamiento persistente masivo de fotos y planos multimedia se requerirá infraestructura adicional.
- Supuesto: Se asume que la plataforma web contará con un servidor web intermediario para gestionar la subida de archivos multimedia de los agentes hacia el sistema de almacenamiento.
- Rúbrica: español _ · rationale _ · coherencia _

### `agencia-viajes-web`

> Somos una agencia de viajes y vamos a rehacer nuestro sitio. Necesitamos un framework web para construir páginas de destinos que carguen muy rápido y se posicionen bien en Google.

**gemini**
- `ok` · Arquitectura web rápida para agencia de viajes
- La propuesta implementa un framework frontend moderno basado en React para construir páginas de destinos con renderizado híbrido, asegurando tiempos de carga rápidos y un excelente posicionamiento en buscadores.
- **Next.js** (`vercel/next.js`), Framework frontend y renderizado web: Next.js es un framework de React con licencia MIT que permite renderizado híbrido y compilación avanzada, ideal para lograr que las páginas de destinos carguen muy rápido y se posicionen bien en Google.
- Limitación: No se han seleccionado herramientas para pruebas automatizadas o gestión de base de datos de destinos.
- Supuesto: Se asume que el equipo de desarrollo cuenta con conocimientos en React para aprovechar el framework seleccionado.
- Rúbrica: español _ · rationale _ · coherencia _

### `cooperativa-api`

> Somos dos desarrolladores de Python en una cooperativa agrícola. Queremos elegir un framework para la API que registra las entregas de café de cada productor, y una base de datos relacional para guardar esos registros.

**gemini**
- `ok` · Sistema para registrar entregas de café en Python
- Esta propuesta utiliza FastAPI para construir la API que registra las entregas de café de cada productor, complementado con SQLModel para la gestión de datos relacionales en Python.
- **FastAPI** (`fastapi/fastapi`), API backend: Es un framework de alto rendimiento, rápido de programar y listo para producción, ideal para construir la API que registra las entregas de café. Posee licencia MIT y actividad reciente.
- **SQLModel** (`fastapi/sqlmodel`), Base de datos relacional: Permite trabajar con bases de datos SQL en Python de forma simple y compatible con FastAPI para guardar los registros de los productores. Tiene licencia MIT.
- Limitación: No se incluyen herramientas para autenticación de usuarios ni para generación de reportes avanzados de café.
- Supuesto: Se asume que la cooperativa cuenta con infraestructura propia o en la nube para alojar la API y la base de datos.
- Rúbrica: español _ · rationale _ · coherencia _

### `colegio-avisos`

> Un colegio quiere una aplicación donde los profesores registren la asistencia. Cada noche debe calcular el porcentaje de asistencia de cada estudiante y avisar por correo o SMS a los padres cuando baje del 80 %.

**gemini**
- `no_evidence` · 
- No se encontraron herramientas del catálogo para lo que pides: comunicación.
- Limitación: Comunicación: no se encontraron herramientas del catálogo para «envío de correos y mensajes de texto».
- Rúbrica: español _ · rationale _ · coherencia _

### `ong-voluntarios`

> Una ONG de voluntariado quiere que sus voluntarios entren con su cuenta de Google y guardar los certificados escaneados de cada uno en PDF.

**gemini**
- `no_evidence` · Sistema de autenticación y almacenamiento para ONG
- La propuesta cubre parcialmente la gestión de secretos con HashiCorp Vault, aunque no incluye herramientas específicas para el inicio de sesión con Google ni para el almacenamiento directo de documentos en PDF.
- Limitación: Autenticación: ninguna de las herramientas encontradas encaja. Se selecciona HashiCorp Vault por ser la opción más cercana en el ámbito de seguridad, aunque no resuelve de forma directa el inicio de sesión de los voluntarios con Google. Su licencia no está identificada por GitHub.
- Limitación: Almacenamiento: ninguna de las herramientas encontradas encaja. etcd almacena datos críticos de sistemas distribuidos, pero no está diseñado para guardar archivos o documentos PDF de los voluntarios. Utiliza la licencia Apache-2.0.
- Limitación: No hay herramientas en los candidatos para almacenar archivos PDF directamente.
- Supuesto: La ONG cuenta con infraestructura en la nube para desplegar las herramientas seleccionadas.
- Supuesto: Se requiere una base de datos documental o de objetos que no está disponible en los candidatos para guardar los PDF.
- Rúbrica: español _ · rationale _ · coherencia _

### `gimnasio-cobros`

> Un gimnasio con tres sedes quiere cobrar las mensualidades en línea, avisar por WhatsApp a los socios que se atrasan en el pago y guardar el historial de pagos en una base de datos relacional.

**gemini**
- `ok` · Arquitectura de datos relacional para el gimnasio
- La propuesta implementa el almacenamiento seguro del historial de pagos mediante una herramienta robusta en Python. Quedan pendientes los servicios específicos para cobros en línea y mensajería de WhatsApp, que no cuentan con candidatos en este catálogo.
- **SQLAlchemy** (`sqlalchemy/sqlalchemy`), ORM y gestor de base de datos relacional: Permite guardar el historial de pagos en una base de datos relacional utilizando Python. Cuenta con licencia MIT y se mantiene activamente con cambios recientes.
- Limitación: Pagos: no se encontraron herramientas del catálogo para «cobro de mensualidades en linea».
- Limitación: Comunicación: no se encontraron herramientas del catálogo para «envio de mensajes por whatsapp».
- Supuesto: El gimnasio requiere desarrollar una aplicación propia en Python para integrar la base de datos relacional con la pasarela de pagos y el servicio de mensajería.
- Rúbrica: español _ · rationale _ · coherencia _

### `repuestos-buscador`

> Tenemos una tienda en línea de repuestos para motos con la API hecha en Django. Queremos agregar un buscador de productos por nombre o referencia (el equipo pensaba en Elasticsearch) y medir la latencia y los errores de la API.

**gemini**
- `ok` · Sistema de Búsqueda y Monitoreo para Tienda en Línea
- La propuesta integra un motor de búsqueda distribuido para localizar repuestos de motos por nombre o referencia y una plataforma de visualización y métricas para medir la latencia y los errores de la API en Django.
- **OpenSearch** (`opensearch-project/OpenSearch`), Motor de búsqueda: Resuelve la búsqueda de productos por nombre o referencia gracias a su capacidad como motor de búsqueda distribuido y RESTful bajo licencia Apache-2.0.
- **Grafana** (`grafana/grafana`), Visualización y monitoreo: Permite visualizar métricas para medir la latencia y los errores de la API mediante una plataforma abierta y componible con licencia AGPL-3.0.
- Limitación: El usuario mencionó inicialmente Elasticsearch, pero el catálogo cuenta con OpenSearch como alternativa equivalente.
- Limitación: La propuesta no incluye recolectores de métricas base como Prometheus ni recolectores de trazas como Jaeger, los cuales serían necesarios para alimentar las gráficas de Grafana.
- Supuesto: Se asume que la tienda en línea cuenta con infraestructura suficiente para desplegar contenedores para OpenSearch y Grafana junto con su API en Django.
- Rúbrica: español _ · rationale _ · coherencia _

### `restaurantes-reportes`

> Una cadena de doce restaurantes quiere procesar cada noche las ventas del día de todos sus locales para recalcular el inventario de cada uno, y mandar por correo el reporte a cada gerente a primera hora.

**gemini**
- `ok` · Sistema nocturno de procesamiento de inventario y reportes
- Esta propuesta implementa el procesamiento por lotes de las ventas nocturnas para recalcular el inventario de los restaurantes. Sin embargo, la herramienta seleccionada para comunicación está enfocada en alertas de monitoreo y no en el envío general de reportes por correo.
- **Apache Spark** (`apache/spark`), Procesamiento nocturno de ventas y cálculo de inventario: Apache Spark resuelve el procesamiento por lotes de las ventas de todos los locales para recalcular el inventario cada noche. Cuenta con licencia Apache-2.0 y soporte activo.
- Limitación: Comunicación: ninguna de las herramientas encontradas encaja. Alertmanager maneja notificaciones por correo pero está diseñado específicamente para alertas del sistema de monitoreo Prometheus, no para enviar reportes comerciales a gerentes.
- Supuesto: Se asume que existe una fuente centralizada donde se consolidan las ventas diarias de los doce restaurantes antes del procesamiento nocturno.
- Supuesto: Se asume que la infraestructura cuenta con la capacidad de cómputo necesaria para ejecutar motores de procesamiento de datos distribuidos.
- Rúbrica: español _ · rationale _ · coherencia _

### `energia-medidores`

> Una empresa de energía recibe lecturas de 50.000 medidores cada 15 minutos. Quiere recibirlas en streaming con Kafka, guardarlas en una base de datos para series de tiempo como InfluxDB y mostrar tableros de consumo en Grafana.

**gemini**
- `ok` · Arquitectura de streaming y almacenamiento para medidores de energía
- Esta propuesta implementa una plataforma para procesar eventos en streaming, almacenar series de tiempo analíticas y visualizar tableros de consumo mediante herramientas de código abierto. Se cubren las necesidades de mensajería y observabilidad de manera directa, utilizando una base de datos analítica como alternativa adecuada para el almacenamiento masivo.
- **ClickHouse** (`ClickHouse/ClickHouse`), Almacenamiento de datos analíticos: ClickHouse es un sistema de gestión de bases de datos de análisis en tiempo real de alto rendimiento bajo licencia Apache-2.0, ideal para procesar grandes volúmenes de datos de medidores.
- **Apache Kafka** (`apache/kafka`), Ingesta de eventos en streaming: Apache Kafka es una plataforma distribuida de streaming de eventos bajo licencia Apache-2.0 que permite recibir y gestionar las lecturas de los medidores en tiempo real.
- **Grafana** (`grafana/grafana`), Visualización y tableros de consumo: Grafana es la plataforma abierta y componible de observabilidad y visualización de datos para mostrar métricas y tableros de consumo.
- Limitación: La tecnología InfluxDB solicitada por el usuario no se encuentra entre los candidatos de la base de datos, por lo que se propone ClickHouse.
- Limitación: La propuesta no incluye componentes específicos para la transformación compleja previa de los datos de streaming más allá de la ingesta.
- Supuesto: Se asume que la empresa cuenta con la infraestructura necesaria para desplegar clústeres distribuidos para Kafka y ClickHouse.
- Supuesto: Se asume que las lecturas de los medidores llegan en un formato estructurado compatible con los conectores de ingestión.
- Rúbrica: español _ · rationale _ · coherencia _

### `contable-chatbot`

> Un estudio contable quiere un chatbot interno que responda preguntas sobre sus manuales de procedimientos usando un modelo de lenguaje que corra en sus propios servidores, y que solo puedan entrar los empleados con cuenta.

**gemini**
- `ok` · Arquitectura para chatbot interno de procedimientos contables
- Esta propuesta implementa un chatbot local para responder consultas sobre manuales y asegura el acceso exclusivo de los empleados mediante gestión de secretos.
- **Ollama** (`ollama/ollama`), Motor de inferencia: Permite levantar y ejecutar los modelos de lenguaje directamente en sus propios servidores de forma sencilla, cumpliendo con el requisito de uso local.
- Limitación: Autenticación: ninguna de las herramientas encontradas encaja. No gestiona cuentas de usuarios ni autenticación de empleados para entrar al chatbot, sino que se enfoca en la gestión de secretos y acceso privilegiado.
- Limitación: La propuesta no incluye una interfaz gráfica de usuario para el chatbot ni un sistema completo de gestión de identidad para las cuentas de los empleados.
- Supuesto: Se asume que la empresa cuenta con infraestructura propia adecuada para ejecutar modelos de lenguaje de manera local.
- Supuesto: Se requiere un componente adicional para la gestión de usuarios y control de acceso que complemente a la herramienta de autenticación.
- Rúbrica: español _ · rationale _ · coherencia _
