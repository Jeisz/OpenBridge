# Comparación de modelos · flujo completo del asistente

Generado con `python -m ai.eval.run_assistant_eval` el 2026-11-07 a las 07:30. 12 casos × 3 corridas por proveedor; catálogo de 100 repos; umbral 0.23; el modelo ve 5 candidatos por necesidad y se registran 5. La llamada de calentamiento no se cuenta.

## Modelos

| Proveedor | Modelo | Razonamiento | Arranque en frío |
|---|---|---|---|
| gemini | `gemini-3.5-flash-lite` | por defecto | 3.9 s |

## Resumen

| Métrica | gemini |
|---|---|
| Status correcto | 86% |
| Respuesta válida | 100% |
| Necesidades detectadas | 86% |
| Techo de la búsqueda (top 5) | 100% |
| Techo con 5 candidatos | 100% |
| Eligió un aceptable (donde había) | 100% |
| Se abstuvo (donde no había) | 85% |
| Acierto de punta a punta (comparable entre k) | 100% |
| Sin caja donde el caso no tiene herramientas | 85% |
| Eligió el primer candidato | 48% |
| Consistencia entre corridas | 83% |
| Entender válido al 1.er intento | 100% |
| Generar válido al 1.er intento | 100% |
| Limitaciones repetidas · borrador del modelo | 11 |
| Limitaciones repetidas · respuesta final | 0 |
| Textos del modelo que hablan del catálogo | 15 |
| Ids en el texto | 0 |
| Errores del proveedor | 0/36 |
| Tiempo total (mediana) | 4.1 s |
| Tiempo total (peor caso) | 10.2 s |
| Sobre 15 s | 0/36 |
| Entender · buscar · generar (mediana) | 2.0 s · 0.1 s · 2.3 s |
| Tokens entrada / salida (mediana) | 3454 / 564 |
| Esperas (límite de uso o error temporal) | 40.0 s |

Evidencia direccional: 12 casos; los porcentajes no son estadística firme.

## Por corrida

Una diferencia entre versiones menor que el rango entre corridas no se puede atribuir al cambio.

**gemini**

| Métrica | Corrida 1 | Corrida 2 | Corrida 3 | Rango |
|---|---|---|---|---|
| Status correcto | 83% | 83% | 92% | 83% – 92% |
| Eligió un aceptable (donde había) | 100% | 100% | 100% | 100% – 100% |
| Se abstuvo (donde no había) | 89% | 78% | 89% | 78% – 89% |
| Acierto de punta a punta | 100% | 100% | 100% | 100% – 100% |
| Textos del modelo que hablan del catálogo | 6 | 6 | 3 | 3 – 6 |

## Por necesidad

Cuenta sobre las corridas válidas: detectada · había un aceptable en el top 3 (techo) · eligió un aceptable. Sin aceptables, se espera que no elija nada.

| Caso · necesidad | Aceptables | gemini |
|---|---|---|
| `ferreteria-sucursales` · auth | (ninguno) | det 0/3 · eligió algo 0 |
| `ferreteria-sucursales` · cache | redis | det 3/3 · techo 3 · eligió 3 |
| `domicilios-push` · communication | (ninguno) | det 3/3 · eligió algo 0 |
| `domicilios-push` · messaging | celery | det 3/3 · techo 3 · eligió 3 |
| `red-mascotas-grafos` · database | (ninguno) | det 3/3 · eligió algo 0 |
| `mercadeo-sitio-vue` · frontend | nuxt, core | det 3/3 · techo 3 · eligió 3 |
| `mercadeo-sitio-vue` · cms | (ninguno) | det 3/3 · eligió algo 0 |
| `laboratorio-respaldos` · storage | (ninguno) | det 3/3 · eligió algo 0 |
| `laboratorio-respaldos` · analytics | grafana | det 3/3 · techo 3 · eligió 3 |
| `cosmeticos-facturas-embudo` · payments | (ninguno) | det 3/3 · eligió algo 0 |
| `cosmeticos-facturas-embudo` · analytics | (ninguno) | det 3/3 · eligió algo 2 |
| `empresa-aprobaciones` · automation | (ninguno) | det 0/3 · eligió algo 0 |
| `startup-trazas-gitops` · observability | jaeger, opentelemetry-collector | det 3/3 · techo 3 · eligió 3 |
| `startup-trazas-gitops` · infrastructure | argo-cd, flux2 | det 3/3 · techo 3 · eligió 3 |
| `artesanias-chat-busqueda` · communication | (ninguno) | det 3/3 · eligió algo 2 |
| `artesanias-chat-busqueda` · search | OpenSearch | det 3/3 · techo 3 · eligió 3 |
| `distribuidora-datos` · data-processing | dbt | det 3/3 · techo 3 · eligió 3 |
| `distribuidora-datos` · database | ClickHouse, duckdb | det 3/3 · techo 3 · eligió 3 |
| `revista-cdn` · infrastructure | (ninguno) | det 0/3 · eligió algo 0 |
| `instituto-videoclases` · communication | (ninguno) | det 3/3 · eligió algo 0 |
| `instituto-videoclases` · storage | (ninguno) | det 3/3 · eligió algo 0 |

## Para revisar a mano (corrida 1)

Rúbrica de 1 a 3: español · `rationale` ligado al negocio · coherencia (título, resumen y cajas dicen lo mismo).

### `ferreteria-sucursales`

> Una cadena de ferreterías con cinco sucursales quiere un sistema interno donde cada sucursal vea solo su propio inventario y sus ventas, y que las consultas repetidas al catálogo de productos respondan rápido.

**gemini**
- `ok` · Sistema interno para gestión de inventario y caché
- Esta propuesta incluye la gestión de secretos y acceso para el sistema interno de las sucursales, junto con una solución de caché en memoria para acelerar las consultas al catálogo de productos. Quedan aspectos específicos de la lógica de negocio de inventario por resolver con herramientas adicionales.
- **Redis** (`redis/redis`), Caché de productos: Redis es un servidor de estructuras de datos en memoria ideal para construir aplicaciones en tiempo real, permitiendo que las consultas repetidas al catálogo respondan rápidamente. Su licencia no fue identificada por GitHub y cuenta con actividad reciente.
- Limitación: Bases de datos: ninguna de las herramientas encontradas encaja. La herramienta elegida se enfoca en la gestión de secretos y cifrado, lo cual es útil para la seguridad del sistema, aunque no provee almacenamiento directo de inventario y ventas.
- Limitación: No se incluye un sistema de base de datos relacional tradicional para almacenar el inventario y las ventas de cada sucursal.
- Limitación: Vault no cumple estrictamente con el almacenamiento persistente de registros de ventas e inventario.
- Supuesto: Se asume que la separación de datos por sucursal se implementará a nivel de aplicación.
- Supuesto: Se asume la necesidad de control de acceso seguro para los empleados de las cinco sucursales.
- Rúbrica: español _ · rationale _ · coherencia _

### `domicilios-push`

> Una app de domicilios quiere enviar una notificación al celular del cliente cuando su pedido salga del restaurante, y generar en segundo plano el recibo en PDF de cada pedido para no demorar la app.

**gemini**
- `ok` · Arquitectura de Notificaciones y Tareas en Segundo Plano
- Esta propuesta implementa un sistema para gestionar las tareas asíncronas de la aplicación de domicilios y el envío de alertas operativas. Se delega la generación de recibos en segundo plano a una cola de tareas distribuida y se utiliza un administrador de alertas para la comunicación.
- **Celery** (`celery/celery`), Cola de tareas asíncronas: Celery resuelve la ejecución de tareas en segundo plano para generar los recibos en PDF de cada pedido, evitando demorar la respuesta de la aplicación. Su licencia no fue identificada por GitHub y cuenta con mantenimiento activo reciente.
- Limitación: Comunicación: ninguna de las herramientas encontradas encaja. Prometheus Alertmanager maneja notificaciones y alertas operativas, pero está enfocado en monitoreo y no en el envío directo de notificaciones push a celulares de clientes finales.
- Supuesto: Se asume que la aplicación principal se comunica con Celery mediante un broker compatible como RabbitMQ o Redis.
- Supuesto: Se requiere integrar un servicio externo de notificaciones push para llegar efectivamente al celular de los clientes.
- Rúbrica: español _ · rationale _ · coherencia _

### `red-mascotas-grafos`

> Estamos armando una red social para dueños de mascotas y queremos guardar quién conoce a quién en una base de datos de grafos, para sugerir amigos de amigos.

**gemini**
- `no_evidence` · Arquitectura de base de datos para red social de mascotas
- Se propone una solución basada en almacenamiento de datos distribuido y en memoria para gestionar la información de la red social. Sin embargo, no se dispone de una base de datos de grafos nativa entre los candidatos encontrados para cumplir estrictamente con el requerimiento de grafos.
- Limitación: Bases de datos: ninguna de las herramientas encontradas encaja. El candidato etcd es un almacén de clave-valor y no una base de datos de grafos como requiere el usuario para modelar relaciones de amistad.
- Limitación: Ninguno de los candidatos analizados es una base de datos de grafos para almacenar quién conoce a quién.
- Supuesto: Se asume que la red social comenzará con un volumen de usuarios manejable para una arquitectura inicial simple.
- Supuesto: El usuario solicitó una base de datos de grafos pero ninguna herramienta candidata cumple con dicha característica específica.
- Rúbrica: español _ · rationale _ · coherencia _

### `mercadeo-sitio-vue`

> Una agencia de mercadeo va a rehacer su sitio web con un framework basado en Vue, y quiere que su equipo, que no sabe programar, cambie los textos y los banners sin pedírselo a los desarrolladores.

**gemini**
- `ok` · Propuesta de sistema web con Vue y gestión de contenido
- Se propone el uso de un framework full-stack basado en Vue para la capa visual, aunque ninguna de las herramientas candidatas para la gestión de contenido cumple directamente con ser un CMS sin código para no programadores.
- **Nuxt** (`nuxt/nuxt`), Framework full-stack basado en Vue para construir el sitio web de la agencia.: Nuxt es el framework full-stack basado en Vue indicado para desarrollar la interfaz de forma híbrida y moderna. Cuenta con licencia MIT y mantenimiento activo.
- Limitación: CMS: ninguna de las herramientas encontradas encaja. Astro es un framework orientado a sitios web con contenido, pero no ofrece una interfaz visual de gestión de contenidos para usuarios que no saben programar. Además, su licencia no fue identificada por GitHub.
- Supuesto: Se asume que la agencia cuenta con desarrolladores que integrarán el CMS headless o la solución de contenido elegida con el framework de Vue.
- Rúbrica: español _ · rationale _ · coherencia _

### `laboratorio-respaldos`

> Un laboratorio clínico quiere copias de seguridad automáticas de los resultados de sus exámenes cada noche, guardadas fuera del servidor principal, y un tablero que muestre cuántas muestras procesa cada sede por día.

**gemini**
- `ok` · Arquitectura de respaldo y analítica para laboratorio clínico
- La propuesta implementa una plataforma de automatización y gestión para copias de seguridad de exámenes médicos, junto con un sistema de visualización para monitorear el procesamiento diario de muestras por sede.
- **Grafana** (`grafana/grafana`), Tablero de visualización: Grafana provee la plataforma de visualización y analítica para crear tableros que muestran métricas operativas. Cuenta con licencia AGPL-3.0 y actividad reciente.
- Limitación: Almacenamiento: ninguna de las herramientas encontradas encaja. Ansible no realiza almacenamiento dedicado de copias de seguridad ni respaldo directo de archivos, sino que automatiza la ejecución de tareas en sistemas operativos.
- Supuesto: Se asume que los resultados de los exámenes se almacenan previamente en una base de datos compatible con Grafana para poder mostrar el conteo diario de muestras por sede.
- Rúbrica: español _ · rationale _ · coherencia _

### `cosmeticos-facturas-embudo`

> Una tienda en línea de cosméticos necesita emitir la factura electrónica de cada venta y saber en qué paso del proceso de compra abandonan los clientes.

**gemini**
- `ok` · Arquitectura de analítica para tienda de cosméticos en línea
- La propuesta incluye una base de datos analítica para procesar los datos de uso de la tienda en línea y medir el comportamiento de compra de los usuarios. Quedan sin resolver las necesidades de facturación electrónica y pagos debido a la falta de candidatos específicos en el catálogo.
- **DuckDB** (`duckdb/duckdb`), Base de datos analítica para procesar consultas del embudo de compra: DuckDB es un sistema de base de datos analítico de alto rendimiento con licencia MIT y mantenimiento activo que permite realizar consultas SQL avanzadas sobre los datos de navegación de la tienda, ayudando a saber en qué paso del proceso de compra abandonan los clientes.
- Limitación: Pagos: no se encontraron herramientas del catálogo para «emisión de facturas electrónicas».
- Limitación: No se encontró ninguna herramienta candidata para la necesidad de emitir la factura electrónica de cada venta.
- Supuesto: Se asume que la tienda cuenta con un sistema de registro de eventos capaz de alimentar la base de datos analítica.
- Supuesto: Se identifica la necesidad de emitir facturas electrónicas mencionada en el pedido, la cual no cuenta con candidatos en este sistema.
- Rúbrica: español _ · rationale _ · coherencia _

### `empresa-aprobaciones`

> Una empresa de 200 empleados quiere que las solicitudes de vacaciones sigan un flujo de aprobación: el empleado la pide, su jefe la aprueba y recursos humanos la registra.

**gemini**
- `needs_clarification` · 
- Necesito un poco más de contexto para recomendarte herramientas.
- Pregunta: ¿Qué tipo de aplicación o plataforma se utilizará para que los empleados registren las solicitudes?
- Pregunta: ¿Se requiere enviar notificaciones por correo electrónico o mensajería cuando cambie el estado de la solicitud?
- Pregunta: ¿Dónde se deben almacenar y registrar las solicitudes de vacaciones?
- Rúbrica: español _ · rationale _ · coherencia _

### `startup-trazas-gitops`

> Una startup tiene diez microservicios en Python sobre Kubernetes. Quiere ver por dónde pasa cada solicitud entre servicios para encontrar dónde se demora, y que cada cambio aprobado en el repositorio se despliegue solo en su clúster.

**gemini**
- `ok` · Arquitectura de observabilidad y despliegue continuo para microservicios
- La propuesta implementa una plataforma de trazas distribuidas para identificar cuellos de botella entre los microservicios y una herramienta de entrega continua basada en GitOps para automatizar los despliegues en el clúster Kubernetes.
- **Jaeger** (`jaegertracing/jaeger`), Plataforma de trazas distribuidas: Resuelve la solicitud de ver por dónde pasa cada solicitud entre servicios y encontrar dónde se demora, utilizando una plataforma de trazas distribuidas con licencia Apache-2.0 y mantenimiento activo.
- **Argo CD** (`argoproj/argo-cd`), Herramienta de entrega continua: Permite que los cambios aprobados en el repositorio se desplieguen de forma declarativa y continua en el clúster, facilitando la automatización con licencia Apache-2.0.
- Limitación: La propuesta no incluye gestión de colas de tareas en Python, para lo cual se podría complementar con Celery si fuera necesario.
- Supuesto: Se asume que los microservicios en Python están instrumentados con OpenTelemetry para enviar las trazas a Jaeger.
- Supuesto: Se asume que los cambios aprobados en el repositorio se publican como manifiestos que Argo CD puede sincronizar.
- Rúbrica: español _ · rationale _ · coherencia _

### `artesanias-chat-busqueda`

> Un marketplace de artesanías quiere un chat en tiempo real entre compradores y vendedores dentro de la página, y un buscador de productos que encuentre resultados aunque el comprador escriba con errores.

**gemini**
- `ok` · Plataforma de marketplace con chat y buscador avanzado
- Esta propuesta incluye la búsqueda avanzada de productos para manejar consultas con errores ortográficos. La necesidad de comunicación en tiempo real no cuenta con una herramienta adecuada en el catálogo de candidatos, por lo que se asume el uso de un servicio externo complementario.
- **OpenSearch** (`opensearch-project/OpenSearch`), Motor de búsqueda: Resuelve la búsqueda de productos en el marketplace gracias a su motor distribuido y RESTful con capacidades de indexación y recuperación de texto completo.
- Limitación: Comunicación: ninguna de las herramientas encontradas encaja. No resuelve el chat de mensajería directa entre usuarios, pero puede registrar eventos analíticos del sistema.
- Limitación: Ninguno de los otros candidatos de búsqueda se especializa en tolerancia a errores ortográficos para comercio electrónico tanto como OpenSearch.
- Supuesto: Se asume que la comunicación en tiempo real requerirá el desarrollo de una solución a medida con WebSockets o un servicio externo de mensajería al no haber herramientas de chat en el catálogo.
- Rúbrica: español _ · rationale _ · coherencia _

### `distribuidora-datos`

> El equipo de datos de una distribuidora quiere transformar las ventas crudas en tablas limpias usando SQL versionado y con pruebas, y guardar el resultado en una base analítica rápida para consultar millones de filas.

**gemini**
- `ok` · Plataforma de datos para transformar ventas crudas con SQL
- Esta propuesta implementa una solución para procesar y transformar datos de ventas utilizando herramientas de análisis y modelado con SQL, respaldada por una base de datos analítica orientada a consultas rápidas sobre millones de filas.
- **dbt** (`dbt-labs/dbt`), Transformación y pruebas de datos: dbt permite transformar las ventas crudas usando SQL versionado y con pruebas mediante prácticas de desarrollo de software. Cuenta con licencia Apache-2.0 y actividad reciente.
- **ClickHouse** (`ClickHouse/ClickHouse`), Base de datos analítica: ClickHouse provee una base de datos para análisis en tiempo real orientada a grandes volúmenes de datos. Utiliza licencia Apache-2.0 y presenta mantenimiento activo.
- Limitación: La propuesta no incluye orquestadores de tareas para automatizar la ejecución periódica de los flujos de transformación.
- Supuesto: Se asume que la distribuidora cuenta con un entorno operativo capaz de ejecutar procesos analíticos y almacenar volúmenes masivos de datos.
- Rúbrica: español _ · rationale _ · coherencia _

### `revista-cdn`

> Una revista digital con lectores en toda Latinoamérica quiere que sus fotos carguen rápido en cualquier país, servidas desde servidores cercanos a cada lector.

**gemini**
- `no_evidence` · Arquitectura de almacenamiento y distribución de fotos para revista digital
- La propuesta plantea una infraestructura enfocada en la distribución eficiente de contenido para lectores en Latinoamérica. La necesidad de almacenamiento y distribución de archivos multimedia se aborda mediante una base de datos distribuida, aunque se requeriría una red de entrega de contenido complementaria para la entrega óptima en múltiples países.
- Limitación: Almacenamiento: ninguna de las herramientas encontradas encaja. etcd ofrece un almacenamiento distribuido confiable para datos críticos de sistemas, pero no está diseñado específicamente para servir archivos multimedia e imágenes de forma optimizada a lectores en múltiples países.
- Limitación: La herramienta seleccionada no incluye de forma nativa una red de entrega de contenidos geográfica para acelerar la carga de fotos en toda Latinoamérica.
- Supuesto: Se asume que la revista digital cuenta con un equipo técnico capaz de configurar infraestructura distribuida.
- Supuesto: El negocio requiere una solución de red de entrega de contenidos que no pudo ser cubierta completamente por los candidatos disponibles.
- Rúbrica: español _ · rationale _ · coherencia _

### `instituto-videoclases`

> Un instituto de idiomas quiere dar clases en vivo por videollamada desde el navegador y guardar las grabaciones para que los estudiantes las vean después.

**gemini**
- `no_evidence` · 
- No se encontraron herramientas del catálogo para lo que pides: comunicación, almacenamiento.
- Limitación: Comunicación: no se encontraron herramientas del catálogo para «realizacion de videollamadas en vivo».
- Limitación: Almacenamiento: no se encontraron herramientas del catálogo para «almacenamiento de archivos de video».
- Rúbrica: español _ · rationale _ · coherencia _
