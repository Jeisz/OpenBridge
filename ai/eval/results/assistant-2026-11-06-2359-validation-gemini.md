# Comparación de modelos · flujo completo del asistente

Generado con `python -m ai.eval.run_assistant_eval` el 2026-11-06 a las 23:59. 10 casos × 3 corridas por proveedor; catálogo de 100 repos; umbral 0.23; el modelo ve 5 candidatos por necesidad y se registran 5. La llamada de calentamiento no se cuenta.

## Modelos

| Proveedor | Modelo | Razonamiento | Arranque en frío |
|---|---|---|---|
| gemini | `gemini-3.5-flash-lite` | por defecto | 3.7 s |

## Resumen

| Métrica | gemini |
|---|---|
| Status correcto | 77% |
| Respuesta válida | 100% |
| Necesidades detectadas | 92% |
| Techo de la búsqueda (top 5) | 75% |
| Techo con 5 candidatos | 75% |
| Eligió un aceptable (donde había) | 95% |
| Se abstuvo (donde no había) | 49% |
| Acierto de punta a punta (comparable entre k) | 71% |
| Sin caja donde el caso no tiene herramientas | 53% |
| Eligió el primer candidato | 78% |
| Consistencia entre corridas | 30% |
| Entender válido al 1.er intento | 100% |
| Generar válido al 1.er intento | 100% |
| Limitaciones repetidas · borrador del modelo | 10 |
| Limitaciones repetidas · respuesta final | 0 |
| Textos del modelo que hablan del catálogo | 18 |
| Ids en el texto | 0 |
| Errores del proveedor | 0/30 |
| Tiempo total (mediana) | 4.3 s |
| Tiempo total (peor caso) | 11.3 s |
| Sobre 15 s | 0/30 |
| Entender · buscar · generar (mediana) | 1.7 s · 0.1 s · 2.0 s |
| Tokens entrada / salida (mediana) | 3358 / 482 |
| Esperas (límite de uso o error temporal) | 0.0 s |

Evidencia direccional: 10 casos; los porcentajes no son estadística firme.

## Por corrida

Una diferencia entre versiones menor que el rango entre corridas no se puede atribuir al cambio.

**gemini**

| Métrica | Corrida 1 | Corrida 2 | Corrida 3 | Rango |
|---|---|---|---|---|
| Status correcto | 70% | 80% | 80% | 70% – 80% |
| Eligió un aceptable (donde había) | 100% | 100% | 86% | 86% – 100% |
| Se abstuvo (donde no había) | 50% | 42% | 54% | 42% – 54% |
| Acierto de punta a punta | 78% | 78% | 60% | 60% – 78% |
| Textos del modelo que hablan del catálogo | 7 | 4 | 7 | 4 – 7 |

## Por necesidad

Cuenta sobre las corridas válidas: detectada · había un aceptable en el top 3 (techo) · eligió un aceptable. Sin aceptables, se espera que no elija nada.

| Caso · necesidad | Aceptables | gemini |
|---|---|---|
| `inmobiliaria-portal` · search | OpenSearch | det 3/3 · techo 3 · eligió 3 |
| `inmobiliaria-portal` · storage | (ninguno) | det 3/3 · eligió algo 0 |
| `agencia-viajes-web` · frontend | next.js, astro, nuxt | det 3/3 · techo 3 · eligió 3 |
| `cooperativa-api` · backend | fastapi, django, flask | det 3/3 · techo 3 · eligió 3 |
| `cooperativa-api` · database | (ninguno) | det 3/3 · eligió algo 3 |
| `colegio-avisos` · data-processing | airflow, prefect, dagster | det 1/3 · techo 0 · eligió 0 |
| `colegio-avisos` · communication | (ninguno) | det 3/3 · eligió algo 0 |
| `ong-voluntarios` · auth | (ninguno) | det 3/3 · eligió algo 0 |
| `ong-voluntarios` · storage | (ninguno) | det 3/3 · eligió algo 3 |
| `gimnasio-cobros` · payments | (ninguno) | det 3/3 · eligió algo 0 |
| `gimnasio-cobros` · communication | (ninguno) | det 3/3 · eligió algo 0 |
| `gimnasio-cobros` · database | (ninguno) | det 3/3 · eligió algo 3 |
| `repuestos-buscador` · search | OpenSearch | det 3/3 · techo 3 · eligió 3 |
| `repuestos-buscador` · observability | prometheus | det 3/3 · techo 3 · eligió 2 |
| `restaurantes-reportes` · data-processing | airflow, prefect, dagster | det 3/3 · techo 0 · eligió 0 |
| `restaurantes-reportes` · communication | (ninguno) | det 3/3 · eligió algo 3 |
| `energia-medidores` · messaging | kafka | det 3/3 · techo 3 · eligió 3 |
| `energia-medidores` · database | ClickHouse | det 3/3 · techo 0 · eligió 0 |
| `energia-medidores` · analytics | grafana | det 0/3 · techo 0 · eligió 0 |
| `contable-chatbot` · ai | ollama, vllm | det 3/3 · techo 3 · eligió 3 |
| `contable-chatbot` · auth | (ninguno) | det 3/3 · eligió algo 2 |

## Para revisar a mano (corrida 1)

Rúbrica de 1 a 3: español · `rationale` ligado al negocio · coherencia (título, resumen y cajas dicen lo mismo).

### `inmobiliaria-portal`

> Estamos construyendo el portal web de una inmobiliaria. Los clientes tienen que poder buscar propiedades escribiendo cosas como 'apartamento con balcón cerca del metro', y los agentes suben las fotos y los planos de cada inmueble.

**gemini**
- `ok` · Portal Inmobiliario con Búsqueda Semántica
- Esta propuesta implementa un motor de búsqueda avanzado para el portal inmobiliario, permitiendo consultas en lenguaje natural sobre las propiedades. Queda pendiente el almacenamiento persistente de las fotos y planos subidos por los agentes.
- **OpenSearch** (`opensearch-project/OpenSearch`), Motor de búsqueda: Resuelve la necesidad de realizar búsqueda de texto libre y analítica de manera distribuida. Utiliza la licencia Apache-2.0 y cuenta con desarrollo activo reciente.
- Limitación: Almacenamiento: el catálogo no tiene herramientas para «almacenamiento de archivos y objetos multimedia».
- Supuesto: Se asume que el sistema contará con un servicio de almacenamiento externo para gestionar las imágenes y planos subidos por los agentes.
- Rúbrica: español _ · rationale _ · coherencia _

### `agencia-viajes-web`

> Somos una agencia de viajes y vamos a rehacer nuestro sitio. Necesitamos un framework web para construir páginas de destinos que carguen muy rápido y se posicionen bien en Google.

**gemini**
- `ok` · Arquitectura web rápida para agencia de viajes
- Implementamos una solución basada en Next.js para construir las páginas de destinos de la agencia, garantizando un rendimiento óptimo y un excelente posicionamiento en buscadores mediante renderizado híbrido.
- **Next.js** (`vercel/next.js`), Framework web para el sitio de la agencia: Permite construir páginas de destinos con renderizado híbrido bajo licencia MIT y mantenimiento activo, lo que asegura tiempos de carga rápidos y un óptimo posicionamiento en Google.
- Limitación: El uso de Vue o Nuxt.js, sugerido indirectamente por preferencias de equipo, no fue seleccionado ya que se priorizó Next.js.
- Supuesto: Se cuenta con personal con experiencia en React para desarrollar sobre el framework elegido.
- Rúbrica: español _ · rationale _ · coherencia _

### `cooperativa-api`

> Somos dos desarrolladores de Python en una cooperativa agrícola. Queremos elegir un framework para la API que registra las entregas de café de cada productor, y una base de datos relacional para guardar esos registros.

**gemini**
- `ok` · Arquitectura de API y Base de Datos para Cooperativa Agrícola
- Esta propuesta incluye un framework moderno de alto rendimiento para construir la API y un kit de herramientas robusto para la interacción con bases de datos relacionales en Python, cubriendo todas las necesidades planteadas para el registro de entregas de café.
- **FastAPI** (`fastapi/fastapi`), Framework para la API: Es un framework de alto rendimiento, fácil de aprender y rápido de codificar, ideal para crear la API que registra las entregas de café de los productores.
- **SQLAlchemy** (`sqlalchemy/sqlalchemy`), Toolkit de base de datos relacional: Proporciona el conjunto de herramientas de base de datos para Python necesario para interactuar con la base de datos relacional y guardar los registros.
- Supuesto: Se asume que la cooperativa requiere una API REST tradicional sin procesamiento avanzado de inteligencia artificial.
- Supuesto: Se asume que el sistema se desplegará en un entorno compatible con aplicaciones Python modernas utilizando bases de datos relacionales estándar como PostgreSQL o MySQL a través de SQLAlchemy.
- Rúbrica: español _ · rationale _ · coherencia _

### `colegio-avisos`

> Un colegio quiere una aplicación donde los profesores registren la asistencia. Cada noche debe calcular el porcentaje de asistencia de cada estudiante y avisar por correo o SMS a los padres cuando baje del 80 %.

**gemini**
- `no_evidence` · 
- El catálogo todavía no tiene herramientas para lo que pides: comunicación.
- Limitación: Comunicación: el catálogo no tiene herramientas para «envío de correos y mensajes de texto».
- Rúbrica: español _ · rationale _ · coherencia _

### `ong-voluntarios`

> Una ONG de voluntariado quiere que sus voluntarios entren con su cuenta de Google y guardar los certificados escaneados de cada uno en PDF.

**gemini**
- `ok` · Sistema de autenticación y almacenamiento para voluntarios
- La propuesta cubre la gestión de secretos con HashiCorp Vault, aunque no resuelve directamente la autenticación con Google ni el almacenamiento de archivos PDF en disco. Ninguno de los candidatos del catálogo satisface de forma adecuada el inicio de sesión con proveedores externos ni el almacenamiento documental.
- **Vault** (`hashicorp/vault`), Almacenamiento de secretos: Permite la gestión de secretos y cifrado, aunque su licencia no fue identificada por GitHub y no está diseñado específicamente para guardar archivos PDF.
- Limitación: Autenticación: ninguna herramienta del catálogo encaja. Ninguno de los candidatos disponibles en el catálogo ofrece autenticación de usuarios mediante proveedores externos como Google.
- Limitación: No se encontró ninguna herramienta en el catálogo para el inicio de sesión con cuentas de Google.
- Limitación: Ninguno de los candidatos de almacenamiento está especializado en guardar documentos PDF.
- Supuesto: Se asume que la ONG requiere un sistema centralizado para gestionar el acceso y la seguridad de la información.
- Supuesto: Se asume que los certificados en PDF se pueden asegurar mediante servicios de cifrado.
- Rúbrica: español _ · rationale _ · coherencia _

### `gimnasio-cobros`

> Un gimnasio con tres sedes quiere cobrar las mensualidades en línea, avisar por WhatsApp a los socios que se atrasan en el pago y guardar el historial de pagos en una base de datos relacional.

**gemini**
- `ok` · Arquitectura de datos para la gestión de pagos del gimnasio
- Se propone una solución basada en Python para gestionar la capa de datos y el mapeo relacional del historial de pagos. Las necesidades de cobro en línea y notificaciones por WhatsApp quedan pendientes de integración con servicios externos.
- **SQLAlchemy** (`sqlalchemy/sqlalchemy`), Mapeador objeto-relacional para el historial de pagos: Permite interactuar con bases de datos relacionales en Python de forma robusta, facilitando el almacenamiento del historial de pagos requerido por el negocio.
- Limitación: Pagos: el catálogo no tiene herramientas para «cobro de mensualidades en linea».
- Limitación: Comunicación: el catálogo no tiene herramientas para «envio de mensajes por whatsapp».
- Limitación: La propuesta no incluye la integración con la API de WhatsApp para enviar avisos de cobro.
- Supuesto: El negocio cuenta con tres sedes que compartirán una única base de datos centralizada.
- Supuesto: Se integrará una pasarela de pagos externa para procesar los cobros en línea de las mensualidades.
- Supuesto: Se utilizará una API de mensajería externa para el envío de avisos por WhatsApp a los socios con pagos atrasados.
- Rúbrica: español _ · rationale _ · coherencia _

### `repuestos-buscador`

> Tenemos una tienda en línea de repuestos para motos con la API hecha en Django. Queremos agregar un buscador de productos por nombre o referencia (el equipo pensaba en Elasticsearch) y medir la latencia y los errores de la API.

**gemini**
- `ok` · Arquitectura de búsqueda y monitoreo para tienda de repuestos
- Esta propuesta implementa OpenSearch para cubrir el buscador de productos por nombre o referencia y Prometheus para medir la latencia y los errores de la API en Django.
- **OpenSearch** (`opensearch-project/OpenSearch`), Motor de búsqueda y análisis: Es un motor de búsqueda distribuido y RESTful que permite realizar búsquedas de texto completo para productos por nombre o referencia. Utiliza licencia Apache-2.0 y cuenta con actividad reciente.
- **Prometheus** (`prometheus/prometheus`), Sistema de monitoreo y base de datos de series temporales: Es un sistema de monitoreo y base de datos de series temporales ideal para medir métricas como la latencia y los errores de la API. Cuenta con licencia Apache-2.0 y actualizaciones recientes.
- Limitación: El usuario mencionó Elasticsearch, pero se seleccionó OpenSearch como la alternativa open source principal del catálogo.
- Limitación: La visualización avanzada de las métricas de Prometheus requeriría una herramienta complementaria como Grafana.
- Supuesto: La API en Django se conectará directamente a OpenSearch para las consultas de los usuarios y expondrá métricas compatibles con Prometheus.
- Rúbrica: español _ · rationale _ · coherencia _

### `restaurantes-reportes`

> Una cadena de doce restaurantes quiere procesar cada noche las ventas del día de todos sus locales para recalcular el inventario de cada uno, y mandar por correo el reporte a cada gerente a primera hora.

**gemini**
- `ok` · Sistema automatizado para reportes de inventario y ventas
- Esta propuesta implementa la gestión de alertas y notificaciones para el envío de reportes a los gerentes de cada restaurante. El procesamiento nocturno de las ventas y el inventario deberá resolverse externamente ya que no se cuenta con una herramienta específica en el catálogo.
- **Prometheus Alertmanager** (`prometheus/alertmanager`), Gestión de notificaciones y envío de avisos: Permite el envío de correos electrónicos para notificar a los gerentes de cada local. Cuenta con soporte para notificaciones por email bajo licencia Apache-2.0 y mantenimiento activo.
- Limitación: Procesamiento de datos: el catálogo no tiene herramientas para «procesamiento nocturno de ventas e inventario».
- Limitación: No se incluye ninguna herramienta en el catálogo para el procesamiento nocturno de las ventas y el recálculo de inventario.
- Limitación: Las opciones de ClickHouse y el SDK de Anthropic no corresponden a la necesidad de enviar correos electrónicos.
- Supuesto: Se asume que el procesamiento de datos nocturno se realizará mediante scripts o herramientas externas no incluidas en el catálogo.
- Supuesto: Se asume que los datos de ventas y el inventario recalculado se integrarán previamente al flujo de alertas.
- Rúbrica: español _ · rationale _ · coherencia _

### `energia-medidores`

> Una empresa de energía recibe lecturas de 50.000 medidores cada 15 minutos. Quiere recibirlas en streaming con Kafka, guardarlas en una base de datos para series de tiempo como InfluxDB y mostrar tableros de consumo en Grafana.

**gemini**
- `ok` · Arquitectura de streaming y visualización para medidores eléctricos
- Esta propuesta implementa un sistema para la ingesta de datos en streaming con Kafka, el almacenamiento de series temporales y la visualización de métricas en tableros con Grafana.
- **Prometheus** (`prometheus/prometheus`), Almacenamiento de series temporales: Proporciona un sistema de monitoreo y base de datos de series temporales para gestionar los registros necesarios.
- **Apache Kafka** (`apache/kafka`), Ingesta de datos en streaming: Funciona como una plataforma de streaming de eventos distribuida para recibir la ingesta de datos.
- **Grafana** (`grafana/grafana`), Visualización de métricas: Permite mostrar tableros de consumo mediante su plataforma de observabilidad y visualización de datos.
- Limitación: El usuario solicitó InfluxDB como base de datos, pero se seleccionó Prometheus ya que InfluxDB no está disponible en los candidatos.
- Supuesto: Se asume que la empresa requiere procesar las lecturas de los 50.000 medidores cada 15 minutos de forma continua.
- Rúbrica: español _ · rationale _ · coherencia _

### `contable-chatbot`

> Un estudio contable quiere un chatbot interno que responda preguntas sobre sus manuales de procedimientos usando un modelo de lenguaje que corra en sus propios servidores, y que solo puedan entrar los empleados con cuenta.

**gemini**
- `ok` · Arquitectura de chatbot interno para estudio contable
- Se propone una solución integral utilizando Ollama para la ejecución local de modelos de lenguaje sobre los manuales de procedimientos. Para la autenticación y control de acceso de los empleados se identificó una herramienta de gestión de secretos y accesos privilegiados.
- **HashiCorp Vault** (`hashicorp/vault`), Gestión de accesos: Permite el control de acceso y gestión de secretos con licencia no identificada por GitHub, aunque está enfocado en privilegios técnicos más que en autenticación de usuarios finales.
- **Ollama** (`ollama/ollama`), Servidor de inferencia local: Permite correr modelos de lenguaje en sus propios servidores de forma sencilla, cumpliendo con la necesidad de ejecutar el chatbot internamente bajo licencia MIT.
- Limitación: La herramienta de autenticación elegida está orientada a gestión de secretos y accesos privilegiados, por lo que requerirá configuración adicional para la autenticación estándar de empleados.
- Limitación: Ninguno de los candidatos de inteligencia artificial incluye de forma nativa la interfaz de usuario para el chatbot ni la indexación documental completa por sí solos, requiriendo complementos como LlamaIndex o LangChain.
- Supuesto: Se asume que el estudio contable dispone de infraestructura propia con capacidad de cómputo para alojar modelos de lenguaje locales.
- Supuesto: Se asume que la interfaz de chat para los empleados se construirá de forma complementaria utilizando los servicios de inferencia.
- Rúbrica: español _ · rationale _ · coherencia _
