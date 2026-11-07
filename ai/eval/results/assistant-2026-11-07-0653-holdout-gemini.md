# Comparación de modelos · flujo completo del asistente

Generado con `python -m ai.eval.run_assistant_eval` el 2026-11-07 a las 06:53. 12 casos × 3 corridas por proveedor; catálogo de 100 repos; umbral 0.23; el modelo ve 5 candidatos por necesidad y se registran 5. La llamada de calentamiento no se cuenta.

## Modelos

| Proveedor | Modelo | Razonamiento | Arranque en frío |
|---|---|---|---|
| gemini | `gemini-3.5-flash-lite` | por defecto | 2.1 s |

## Resumen

| Métrica | gemini |
|---|---|
| Status correcto | 74% |
| Respuesta válida | 100% |
| Necesidades detectadas | 85% |
| Techo de la búsqueda (top 5) | 100% |
| Techo con 5 candidatos | 100% |
| Eligió un aceptable (donde había) | 100% |
| Se abstuvo (donde no había) | 65% |
| Acierto de punta a punta (comparable entre k) | 100% |
| Sin caja donde el caso no tiene herramientas | 65% |
| Eligió el primer candidato | 49% |
| Consistencia entre corridas | 67% |
| Entender válido al 1.er intento | 100% |
| Generar válido al 1.er intento | 100% |
| Limitaciones repetidas · borrador del modelo | 7 |
| Limitaciones repetidas · respuesta final | 0 |
| Textos del modelo que hablan del catálogo | 37 |
| Ids en el texto | 0 |
| Errores del proveedor | 1/36 |
| Tiempo total (mediana) | 3.6 s |
| Tiempo total (peor caso) | 11.0 s |
| Sobre 15 s | 0/35 |
| Entender · buscar · generar (mediana) | 1.6 s · 0.1 s · 1.8 s |
| Tokens entrada / salida (mediana) | 3270 / 442 |
| Esperas (límite de uso o error temporal) | 0.0 s |

Evidencia direccional: 12 casos; los porcentajes no son estadística firme.

## Por corrida

Una diferencia entre versiones menor que el rango entre corridas no se puede atribuir al cambio.

**gemini**

| Métrica | Corrida 1 | Corrida 2 | Corrida 3 | Rango |
|---|---|---|---|---|
| Status correcto | 67% | 73% | 83% | 67% – 83% |
| Eligió un aceptable (donde había) | 100% | 100% | 100% | 100% – 100% |
| Se abstuvo (donde no había) | 56% | 62% | 78% | 56% – 78% |
| Acierto de punta a punta | 100% | 100% | 100% | 100% – 100% |
| Textos del modelo que hablan del catálogo | 14 | 13 | 10 | 10 – 14 |

## Por necesidad

Cuenta sobre las corridas válidas: detectada · había un aceptable en el top 3 (techo) · eligió un aceptable. Sin aceptables, se espera que no elija nada.

| Caso · necesidad | Aceptables | gemini |
|---|---|---|
| `ferreteria-sucursales` · auth | (ninguno) | det 0/3 · eligió algo 0 |
| `ferreteria-sucursales` · cache | redis | det 3/3 · techo 3 · eligió 3 |
| `domicilios-push` · communication | (ninguno) | det 2/2 · eligió algo 0 |
| `domicilios-push` · messaging | celery | det 2/2 · techo 2 · eligió 2 |
| `red-mascotas-grafos` · database | (ninguno) | det 3/3 · eligió algo 2 |
| `mercadeo-sitio-vue` · frontend | nuxt, core | det 3/3 · techo 3 · eligió 3 |
| `mercadeo-sitio-vue` · cms | (ninguno) | det 3/3 · eligió algo 0 |
| `laboratorio-respaldos` · storage | (ninguno) | det 3/3 · eligió algo 1 |
| `laboratorio-respaldos` · analytics | grafana | det 3/3 · techo 3 · eligió 3 |
| `cosmeticos-facturas-embudo` · payments | (ninguno) | det 3/3 · eligió algo 0 |
| `cosmeticos-facturas-embudo` · analytics | (ninguno) | det 3/3 · eligió algo 3 |
| `empresa-aprobaciones` · automation | (ninguno) | det 0/3 · eligió algo 0 |
| `startup-trazas-gitops` · observability | jaeger, opentelemetry-collector | det 3/3 · techo 3 · eligió 3 |
| `startup-trazas-gitops` · infrastructure | argo-cd, flux2 | det 3/3 · techo 3 · eligió 3 |
| `artesanias-chat-busqueda` · communication | (ninguno) | det 3/3 · eligió algo 3 |
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
- `ok` · Sistema de gestión y caché para cadena de ferreterías
- La propuesta implementa un kit de herramientas en Python para gestionar las bases de datos relacionales de las sucursales y Redis como caché en memoria para acelerar las consultas al catálogo de productos.
- **SQLAlchemy** (`sqlalchemy/sqlalchemy`), Kit de herramientas de base de datos: Permite construir y gestionar el almacenamiento y consulta de datos relacionales para que cada sucursal administre su propio inventario y sus ventas mediante Python. Posee licencia MIT.
- **Redis** (`redis/redis`), Servidor de estructura de datos en memoria y caché: Funciona como el caché preferido y más rápido para lograr que las consultas repetidas al catálogo de productos respondan con la velocidad requerida. Su licencia no fue identificada por GitHub.
- Limitación: No se incluye una interfaz gráfica ni un sistema de control de usuarios para restringir el acceso por sucursal, lo cual deberá desarrollarse de forma complementaria.
- Supuesto: Se asume que la lógica de negocio para separar los datos de las cinco sucursales se implementará a nivel de aplicación usando el kit de base de datos elegido.
- Rúbrica: español _ · rationale _ · coherencia _

### `domicilios-push`

> Una app de domicilios quiere enviar una notificación al celular del cliente cuando su pedido salga del restaurante, y generar en segundo plano el recibo en PDF de cada pedido para no demorar la app.

**gemini**
- `ok` · Sistema de notificaciones y tareas en segundo plano para domicilios
- Esta propuesta implementa la gestión de tareas pesadas en segundo plano mediante una cola de distribución y cubre los requerimientos operativos de la aplicación de domicilios. La necesidad de envío de notificaciones push no cuenta con una herramienta adecuada en el catálogo actual.
- **Celery** (`celery/celery`), Generación de recibos en PDF: Permite la ejecución de tareas distribuidas en segundo plano para procesar la creación de recibos sin demorar la aplicación principal. La licencia no está identificada por GitHub.
- Limitación: Comunicación: ninguna herramienta del catálogo encaja. Ninguna de las herramientas del catálogo cumple con la capacidad de enviar notificaciones push a dispositivos móviles, ya que Prometheus Alertmanager está orientado al monitoreo y alertas operativas.
- Limitación: No se dispone de una herramienta específica para notificaciones push móviles en el catálogo.
- Supuesto: La aplicación móvil cuenta con un canal o servicio propio para la recepción de notificaciones push no cubierto por el catálogo.
- Rúbrica: español _ · rationale _ · coherencia _

### `red-mascotas-grafos`

> Estamos armando una red social para dueños de mascotas y queremos guardar quién conoce a quién en una base de datos de grafos, para sugerir amigos de amigos.

**gemini**
- `ok` · Arquitectura de datos para red social de mascotas
- Esta propuesta implementa un sistema de almacenamiento basado en caché y estructuras de datos en memoria para soportar la aplicación. No se cuenta con una base de datos de grafos nativa en el catálogo, por lo que se utiliza una alternativa de estructura de datos.
- **Redis** (`redis/redis`), Servidor de estructura de datos en memoria: Redis es un servidor de estructura de datos útil para desarrolladores que construyen aplicaciones en tiempo real y orientadas a datos. Su licencia no fue identificada por GitHub.
- Limitación: Ninguno de los candidatos en el catálogo ofrece una base de datos de grafos dedicada para sugerir amigos mediante relaciones directas.
- Supuesto: Se asume que la estructura de datos en memoria de Redis puede adaptarse para guardar las relaciones entre usuarios aunque no sea una base de datos de grafos nativa.
- Rúbrica: español _ · rationale _ · coherencia _

### `mercadeo-sitio-vue`

> Una agencia de mercadeo va a rehacer su sitio web con un framework basado en Vue, y quiere que su equipo, que no sabe programar, cambie los textos y los banners sin pedírselo a los desarrolladores.

**gemini**
- `ok` · Propuesta de arquitectura web para agencia de mercadeo
- Se propone una solución basada en Nuxt para el desarrollo frontend en Vue. Sin embargo, no se encontró una herramienta de gestión de contenidos adecuada en el catálogo para permitir al equipo no técnico editar textos y banners de forma independiente.
- **Nuxt** (`nuxt/nuxt`), Framework full-stack basado en Vue: Resuelve la necesidad de utilizar un framework web basado en Vue con licencia MIT y mantenimiento activo.
- Limitación: CMS: ninguna herramienta del catálogo encaja. Ninguno de los candidatos del catálogo corresponde a un sistema de gestión de contenidos para usuarios no técnicos.
- Limitación: La propuesta actual no incluye una interfaz visual para que el equipo sin conocimientos de programación pueda modificar los textos y banners del sitio web.
- Supuesto: Se asume que la agencia cuenta con desarrolladores capaces de integrar un CMS headless externo si fuera necesario, ya que el catálogo no ofrece una herramienta adecuada para no técnicos.
- Rúbrica: español _ · rationale _ · coherencia _

### `laboratorio-respaldos`

> Un laboratorio clínico quiere copias de seguridad automáticas de los resultados de sus exámenes cada noche, guardadas fuera del servidor principal, y un tablero que muestre cuántas muestras procesa cada sede por día.

**gemini**
- `ok` · Sistema de respaldos y analítica para laboratorio clínico
- Esta propuesta implementa un almacén de claves para datos críticos y una plataforma de visualización para el monitoreo de muestras por sede. Ambas herramientas cuentan con mantenimiento activo y licencias adecuadas para la infraestructura.
- **etcd** (`etcd-io/etcd`), Almacenamiento clave-valor: Funciona como un almacén de datos distribuido y confiable para la información más crítica del sistema, facilitando la retaguardia de los resultados de exámenes.
- **Grafana** (`grafana/grafana`), Tablero de visualización: Proporciona una plataforma de visualización de datos y analítica ideal para construir el tablero que muestra cuántas muestras procesa cada sede por día.
- Limitación: Ninguna de las herramientas incluye por defecto la automatización de respaldos nocturnos, la cual debe configurarse mediante tareas programadas externas.
- Supuesto: Se asume que el laboratorio cuenta con una infraestructura en red para conectar el almacenamiento externo con el servidor principal.
- Rúbrica: español _ · rationale _ · coherencia _

### `cosmeticos-facturas-embudo`

> Una tienda en línea de cosméticos necesita emitir la factura electrónica de cada venta y saber en qué paso del proceso de compra abandonan los clientes.

**gemini**
- `ok` · Sistema de Anal%EDtica para Tienda de Cosm%E9ticos
- Esta propuesta incluye la base de datos anal%EDtica para procesar los datos de conversi%F3n y entender el comportamiento de los clientes. Queda pendiente la soluci%F3n para la emisi%F3n de facturas electr%F3nicas y la integraci%F3n de pagos.
- **DuckDB** (`duckdb/duckdb`), Base de datos anal%EDtica: DuckDB es un sistema de base de datos anal%EDtica de alto rendimiento que permite procesar consultas SQL eficientemente. Cuenta con licencia MIT y actividad reciente.
- Limitación: Pagos: el catálogo no tiene herramientas para «emisión de factura electrónica».
- Limitación: No se incluye ninguna herramienta para emitir la factura electr%F3nica de cada venta.
- Supuesto: Se asume que la tienda de cosm%E9ticos cuenta con una fuente de datos transaccional previa que registra los eventos del proceso de compra.
- Supuesto: La emisi%F3n de factura electr%F3nica requiere una integraci%F3n espec%EDfica que no est%E1 cubierta por las herramientas actuales.
- Rúbrica: español _ · rationale _ · coherencia _

### `empresa-aprobaciones`

> Una empresa de 200 empleados quiere que las solicitudes de vacaciones sigan un flujo de aprobación: el empleado la pide, su jefe la aprueba y recursos humanos la registra.

**gemini**
- `needs_clarification` · 
- Necesito un poco más de contexto para recomendarte herramientas.
- Pregunta: ¿Qué tipo de aplicación o plataforma utilizan actualmente para que los empleados interactúen con la empresa?
- Pregunta: ¿Necesitan integrar este flujo de solicitudes con algún sistema de correo electrónico o calendario existente?
- Pregunta: ¿Cómo prefieren gestionar el almacenamiento de los registros de vacaciones de los empleados?
- Rúbrica: español _ · rationale _ · coherencia _

### `startup-trazas-gitops`

> Una startup tiene diez microservicios en Python sobre Kubernetes. Quiere ver por dónde pasa cada solicitud entre servicios para encontrar dónde se demora, y que cada cambio aprobado en el repositorio se despliegue solo en su clúster.

**gemini**
- `ok` · Arquitectura de observabilidad y despliegue continuo para microservicios
- Esta propuesta implementa una plataforma de trazabilidad distribuida para analizar el rendimiento de las solicitudes y una solución de despliegue continuo para automatizar las actualizaciones en el clúster de Kubernetes.
- **Jaeger** (`jaegertracing/jaeger`), Plataforma de trazas distribuidas: Permite ver por dónde pasa cada solicitud entre servicios y encontrar dónde se demora gracias a sus capacidades de trazabilidad distribuida. Utiliza licencia Apache-2.0 y cuenta con mantenimiento activo reciente.
- **Argo CD** (`argoproj/argo-cd`), Herramienta de despliegue continuo: Automatiza el despliegue continuo en Kubernetes para que cada cambio aprobado en el repositorio se aplique en el clúster. Cuenta con licencia Apache-2.0 y actividad reciente en su repositorio.
- Limitación: La herramienta Istio complementaría la observabilidad gestionando el tráfico de red entre los microservicios.
- Limitación: La herramienta Flux CD ofrecería alternativas adicionales para la entrega continua basada en GitOps.
- Supuesto: Se asume que los microservicios en Python están instrumentados para exportar trazas compatibles con OpenTelemetry.
- Supuesto: Se asume que el repositorio de código está integrado con un flujo de aprobación previo al despliegue continuo.
- Rúbrica: español _ · rationale _ · coherencia _

### `artesanias-chat-busqueda`

> Un marketplace de artesanías quiere un chat en tiempo real entre compradores y vendedores dentro de la página, y un buscador de productos que encuentre resultados aunque el comprador escriba con errores.

**gemini**
- `ok` · Plataforma de comercio para marketplace de artesanías
- Esta propuesta integra una base de datos en memoria para soportar la mensajería en tiempo real entre los usuarios y un motor de búsqueda distribuido que permite encontrar productos de manera eficiente. No se detectaron necesidades sin cubrir en el catálogo actual.
- **Redis** (`redis/redis`), Servidor de datos en memoria para el chat: Redis funciona como una estructura de datos en memoria ideal para desarrolladores que construyen aplicaciones en tiempo real. Su licencia no fue identificada por GitHub y cuenta con mantenimiento reciente.
- **OpenSearch** (`opensearch-project/OpenSearch`), Motor de búsqueda de productos: OpenSearch es un motor de búsqueda distribuido y basado en REST que permite indexar y consultar el catálogo de artesanías. Utiliza la licencia Apache-2.0 y recibe actualizaciones constantes.
- Limitación: La tolerancia a errores ortográficos en las consultas de búsqueda dependerá de la configuración avanzada del motor seleccionado.
- Supuesto: Se asume que la plataforma web del marketplace cuenta con una interfaz de usuario capaz de conectarse mediante APIs a Redis y OpenSearch.
- Rúbrica: español _ · rationale _ · coherencia _

### `distribuidora-datos`

> El equipo de datos de una distribuidora quiere transformar las ventas crudas en tablas limpias usando SQL versionado y con pruebas, y guardar el resultado en una base analítica rápida para consultar millones de filas.

**gemini**
- `ok` · Arquitectura de datos para análisis rápido de ventas
- Esta propuesta implementa un flujo moderno para transformar ventas crudas mediante SQL versionado y pruebas, y almacenarlas en una base analítica orientada a columnas capaz de procesar millones de registros de forma eficiente.
- **dbt** (`dbt-labs/dbt`), Transformación y pruebas de datos con SQL versionado: Permite a los ingenieros y analistas transformar sus datos utilizando prácticas de ingeniería de software, resolviendo directamente la necesidad de usar SQL versionado y con pruebas.
- **ClickHouse** (`ClickHouse/ClickHouse`), Base de datos analítica para consultas rápidas: Es un sistema de gestión de bases de datos para análisis en tiempo real, diseñado para ofrecer un rendimiento óptimo al consultar millones de filas.
- Supuesto: El equipo cuenta con infraestructura propia o en la nube para alojar las herramientas seleccionadas.
- Supuesto: Los datos de ventas crudas ya se encuentran accesibles para ser procesados por la herramienta de transformación.
- Rúbrica: español _ · rationale _ · coherencia _

### `revista-cdn`

> Una revista digital con lectores en toda Latinoamérica quiere que sus fotos carguen rápido en cualquier país, servidas desde servidores cercanos a cada lector.

**gemini**
- `ok` · Arquitectura de almacenamiento distribuido para revista digital
- La propuesta utiliza una base de datos distribuida para gestionar los datos críticos del sistema, asegurando alta disponibilidad. Se asume que el almacenamiento de archivos multimedia para distribución regional se resolverá mediante una red de entrega de contenido externa.
- **etcd** (`etcd-io/etcd`), Almacenamiento de datos críticos: Proporciona un almacén de clave-valor distribuido y confiable para los datos críticos del sistema, bajo licencia Apache-2.0 y con mantenimiento activo.
- Limitación: Ninguno de los candidatos del catálogo es un almacenamiento de objetos tradicional idóneo para servir imágenes a nivel regional directamente.
- Supuesto: Se asume que la distribución rápida de fotos en Latinoamérica se implementará utilizando un servicio externo de red de entrega de contenido o CDN compatible con almacenamiento de objetos.
- Supuesto: El sistema requiere almacenar configuraciones o metadatos críticos de forma distribuida.
- Rúbrica: español _ · rationale _ · coherencia _

### `instituto-videoclases`

> Un instituto de idiomas quiere dar clases en vivo por videollamada desde el navegador y guardar las grabaciones para que los estudiantes las vean después.

**gemini**
- `no_evidence` · 
- El catálogo todavía no tiene herramientas para lo que pides: comunicación, almacenamiento.
- Limitación: Comunicación: el catálogo no tiene herramientas para «realizacion de videollamadas en vivo».
- Limitación: Almacenamiento: el catálogo no tiene herramientas para «almacenamiento de archivos multimedia».
- Rúbrica: español _ · rationale _ · coherencia _
