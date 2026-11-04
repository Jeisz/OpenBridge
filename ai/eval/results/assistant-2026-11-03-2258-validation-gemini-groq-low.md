# Comparación de modelos · flujo completo del asistente

Generado con `python -m ai.eval.run_assistant_eval` el 2026-11-03 a las 22:58. 5 casos × 3 corridas por proveedor; catálogo de 100 repos; umbral 0.19; el modelo ve 3 candidatos por necesidad y se registran 5. La llamada de calentamiento no se cuenta.

## Modelos

| Proveedor | Modelo | Razonamiento | Arranque en frío |
|---|---|---|---|
| gemini | `gemini-3.5-flash-lite` | por defecto | 1.5 s |
| groq-low | `openai/gpt-oss-120b` | low | 0.9 s |

## Resumen

| Métrica | gemini | groq-low |
|---|---|---|
| Status correcto | 80% | 93% |
| Respuesta válida | 100% | 93% |
| Necesidades detectadas | 96% | 100% |
| Techo de la búsqueda (top 3) | 91% | 92% |
| Techo con 5 candidatos | 91% | 92% |
| Eligió un aceptable (donde había) | 100% | 82% |
| Se abstuvo (donde no había) | 75% | 75% |
| Eligió el primer candidato | 57% | 47% |
| Consistencia entre corridas | 40% | 40% |
| Entender válido al 1.er intento | 100% | 93% |
| Generar válido al 1.er intento | 100% | 93% |
| Limitaciones repetidas | 3 | 1 |
| Ids en el texto | 0 | 0 |
| Errores del proveedor | 0/15 | 0/15 |
| Tiempo total (mediana) | 3.3 s | 2.7 s |
| Tiempo total (peor caso) | 4.5 s | 4.7 s |
| Sobre 15 s | 0/15 | 0/15 |
| Entender · buscar · generar (mediana) | 1.6 s · 0.1 s · 1.7 s | 1.1 s · 0.1 s · 1.5 s |
| Tokens entrada / salida (mediana) | 3128 / 408 | 3841 / 568 |
| Esperas (límite de uso o error temporal) | 0.0 s | 1449.0 s |

Evidencia direccional: 5 casos; los porcentajes no son estadística firme.

## Por necesidad

Cuenta sobre las corridas válidas: detectada · había un aceptable en el top 3 (techo) · eligió un aceptable. Sin aceptables, se espera que no elija nada.

| Caso · necesidad | Aceptables | gemini | groq-low |
|---|---|---|---|
| `inmobiliaria-portal` · search | OpenSearch | det 3/3 · techo 3 · eligió 3 | det 3/3 · techo 3 · eligió 3 |
| `inmobiliaria-portal` · storage | (ninguno) | det 3/3 · eligió algo 0 | det 3/3 · eligió algo 0 |
| `agencia-viajes-web` · frontend | next.js, astro, nuxt | det 3/3 · techo 3 · eligió 3 | det 3/3 · techo 3 · eligió 3 |
| `cooperativa-api` · backend | fastapi, django, flask | det 3/3 · techo 3 · eligió 3 | det 3/3 · techo 3 · eligió 3 |
| `cooperativa-api` · database | (ninguno) | det 3/3 · eligió algo 3 | det 3/3 · eligió algo 2 |
| `colegio-avisos` · data-processing | airflow, prefect, dagster | det 2/3 · techo 1 · eligió 1 | det 3/3 · techo 2 · eligió 0 |
| `colegio-avisos` · communication | (ninguno) | det 3/3 · eligió algo 0 | det 3/3 · eligió algo 2 |
| `ong-voluntarios` · auth | (ninguno) | det 3/3 · eligió algo 0 | det 3/3 · eligió algo 0 |
| `ong-voluntarios` · storage | (ninguno) | det 3/3 · eligió algo 1 | det 3/3 · eligió algo 0 |

## Para revisar a mano (corrida 1)

Rúbrica de 1 a 3: español · `rationale` ligado al negocio · coherencia (título, resumen y cajas dicen lo mismo).

### `inmobiliaria-portal`

> Estamos construyendo el portal web de una inmobiliaria. Los clientes tienen que poder buscar propiedades escribiendo cosas como 'apartamento con balcón cerca del metro', y los agentes suben las fotos y los planos de cada inmueble.

**gemini**
- `ok` · Portal inmobiliario con búsqueda avanzada
- Proponemos OpenSearch para resolver la búsqueda semántica y de texto libre en el portal. Queda pendiente el almacenamiento de archivos para las fotos y planos de los inmuebles.
- **OpenSearch** (`opensearch-project/OpenSearch`), Búsqueda y análisis: Permite realizar búsquedas distribuidas y RESTful orientadas a motores de búsqueda, facilitando consultas avanzadas de texto libre como las que requieren los clientes.
- Limitación: Almacenamiento: el catálogo no tiene herramientas para «almacenamiento de archivos y objetos multimedia».
- Limitación: La propuesta no incluye el almacenamiento de fotos y planos de los inmuebles, que requiere una solución dedicada.
- Supuesto: Suponemos que el sistema contará con una base de datos relacional o servicio de almacenamiento compatible para los metadatos de las propiedades.
- Supuesto: El almacenamiento de archivos para fotos y planos de los inmuebles requiere una solución externa.
- Rúbrica: español _ · rationale _ · coherencia _

**groq-low**
- `ok` · Portal inmobiliario con búsqueda y gestión de archivos
- Se propone OpenSearch para la búsqueda de inmuebles y se indica que ningún candidato del catálogo cubre adecuadamente el almacenamiento de fotos y planos, requiriendo una solución de almacenamiento de objetos externa. No hay enlaces directos entre componentes.
- **OpenSearch** (`opensearch-project/OpenSearch`), Motor de búsqueda de texto completo para consultas de inmuebles: OpenSearch es un motor de búsqueda distribuido y RESTful que permite consultas de texto libre como "apartamento con balcón cerca del metro".
- Limitación: Almacenamiento: ninguna herramienta del catálogo encaja. Ninguno de los candidatos (etcd, Vault, NGINX) está diseñado para almacenar archivos y objetos binarios de gran tamaño; por lo tanto no satisfacen la necesidad de almacenar imágenes y planos.
- Limitación: Los candidatos de almacenamiento listados no manejan eficientemente archivos grandes; se necesitará una herramienta especializada en almacenamiento de objetos.
- Supuesto: Se asumirá que se integrará una solución de almacenamiento de objetos (por ejemplo, MinIO o S3 compatible) externa al catálogo para gestionar los archivos multimedia.
- Rúbrica: español _ · rationale _ · coherencia _

### `agencia-viajes-web`

> Somos una agencia de viajes y vamos a rehacer nuestro sitio. Necesitamos un framework web para construir páginas de destinos que carguen muy rápido y se posicionen bien en Google.

**gemini**
- `ok` · Arquitectura web rápida para agencia de viajes
- Propuesta de framework web para construir páginas de destinos optimizadas para carga rápida y posicionamiento en buscadores. Permite desarrollar una interfaz moderna y eficiente para los usuarios de la agencia.
- **Next.js** (`vercel/next.js`), Framework web para renderizado y desarrollo frontend: Es el framework de React ideal para construir páginas de destinos que carguen muy rápido y se posicionen bien en Google gracias a sus capacidades híbridas y de compilación. Cuenta con licencia MIT y alta actividad reciente.
- Limitación: No se incluyeron herramientas específicas para la gestión del contenido de los destinos o base de datos.
- Supuesto: La agencia de viajes cuenta con recursos de desarrollo con experiencia en React.
- Rúbrica: español _ · rationale _ · coherencia _

**groq-low**
- `ok` · Sitio de viajes rápido y SEO-friendly con Astro
- Se propone usar Astro como framework principal para construir las páginas de destinos, garantizando carga ultra rápida y buena indexación en Google. No se requieren herramientas adicionales para la capa frontend. Todas las demás necesidades del proyecto están cubiertas.
- **Astro** (`withastro/astro`), Framework web para crear sitios estáticos y dinámicos con gran rendimiento y SEO: Astro está diseñado para sitios centrados en contenido, genera HTML estático que se carga rápidamente y es altamente amigable con los motores de búsqueda, cumpliendo con la necesidad de velocidad y posicionamiento.
- Rúbrica: español _ · rationale _ · coherencia _

### `cooperativa-api`

> Somos dos desarrolladores de Python en una cooperativa agrícola. Queremos elegir un framework para la API que registra las entregas de café de cada productor, y una base de datos relacional para guardar esos registros.

**gemini**
- `ok` · Sistema de Registro de Entregas de Café
- Esta propuesta utiliza FastAPI para construir la interfaz de la API y SQLModel para gestionar la base de datos relacional que almacena las entregas de café de los productores.
- **FastAPI** (`fastapi/fastapi`), Framework para la API: Es un framework moderno y de alto rendimiento en Python, ideal para desarrollar rápidamente la API que registra las entregas de café de cada productor.
- **SQLModel** (`fastapi/sqlmodel`), Base de datos relacional: Permite interactuar con bases de datos SQL en Python de forma sencilla y robusta para guardar los registros de los productores.
- Supuesto: Se asume que la cooperativa cuenta con infraestructura propia o en la nube para desplegar la API y la base de datos.
- Rúbrica: español _ · rationale _ · coherencia _

**groq-low**
- `ok` · Propuesta de API y almacenamiento de entregas de café
- Se selecciona FastAPI como framework para la API que registrará las entregas de café, ya que cumple con los requisitos de desarrollo de APIs en Python. No se encontró una base de datos relacional entre los candidatos, por lo que se indica la ausencia de herramienta adecuada. Se sugiere considerar otras opciones de bases de datos relacionales de código abierto fuera del catálogo.
- **FastAPI** (`fastapi/fastapi`), Framework para crear la API REST de registros de entregas: FastAPI es un framework de alto rendimiento, fácil de aprender y listo para producción, ideal para desarrollar APIs en Python.
- Limitación: Bases de datos: ninguna herramienta del catálogo encaja. Ninguno de los candidatos (Redis, etcd, pandas) es una base de datos relacional; por lo tanto, no cumplen con la necesidad especificada.
- Rúbrica: español _ · rationale _ · coherencia _

### `colegio-avisos`

> Un colegio quiere una aplicación donde los profesores registren la asistencia. Cada noche debe calcular el porcentaje de asistencia de cada estudiante y avisar por correo o SMS a los padres cuando baje del 80 %.

**gemini**
- `no_evidence` · 
- El catálogo todavía no tiene herramientas para lo que pides: comunicación.
- Limitación: Comunicación: el catálogo no tiene herramientas para «envío de correos o mensajes de texto».
- Rúbrica: español _ · rationale _ · coherencia _

**groq-low**
- `ok` · Sistema de registro y cálculo de asistencia escolar
- Se propone usar Redis como base de datos para registrar la asistencia de los estudiantes y Apache Beam para procesar los datos cada noche y generar los porcentajes de asistencia. No se incluye una solución de comunicación, por lo que los avisos por correo o SMS deberán implementarse por separado. Otros candidatos podrían complementar la solución pero no son seleccionados como principales.
- **Redis** (`redis/redis`), Almacén de datos estructurados de asistencia: Redis permite guardar rápidamente registros de asistencia en estructuras de datos en memoria, es fácil de escalar y su licencia no está identificada, pero sigue siendo adecuado para almacenar la información requerida.
- **Apache Beam** (`apache/beam`), Cálculo nocturno del porcentaje de asistencia: Apache Beam ofrece un modelo unificado para procesamiento por lotes, permite ejecutar un pipeline cada noche que lea los datos de asistencia de Redis y calcule los porcentajes solicitados.
- Limitación: Comunicación: el catálogo no tiene herramientas para «envío de notificaciones por correo o SMS».
- Limitación: Para la notificación a padres se requeriría una herramienta de comunicación que no está en el catálogo.
- Supuesto: Se dispone de un entorno donde se pueden ejecutar contenedores Docker o procesos de Python.
- Supuesto: Los datos de asistencia pueden almacenarse como estructuras clave‑valor (p. ej., hash por estudiante).
- Supuesto: La notificación a los padres se implementará fuera del alcance de este diseño.
- Rúbrica: español _ · rationale _ · coherencia _

### `ong-voluntarios`

> Una ONG de voluntariado quiere que sus voluntarios entren con su cuenta de Google y guardar los certificados escaneados de cada uno en PDF.

**gemini**
- `no_evidence` · Sistema Open Source para Autenticación y Almacenamiento de Voluntarios
- Esta propuesta integra herramientas para la gestión de infraestructura y certificados, aunque ninguna de las opciones disponibles en el catálogo resuelve directamente la autenticación de usuarios mediante cuentas de Google ni el almacenamiento específico de archivos PDF.
- Limitación: Autenticación: ninguna herramienta del catálogo encaja. Ninguno de los candidatos resuelve la autenticación de usuarios mediante proveedores externos como Google, ya que se centran en certificados TLS, proxies o infraestructura como código.
- Limitación: Almacenamiento: ninguna herramienta del catálogo encaja. El candidato disponible es una base de datos clave-valor distribuida y no está diseñado para almacenar archivos y documentos escaneados en formato PDF.
- Limitación: No se dispone de herramientas en el catálogo para el inicio de sesión con cuentas de Google.
- Limitación: No se dispone de herramientas para la gestión y almacenamiento documental de archivos PDF.
- Supuesto: Se asume que la ONG cuenta con personal técnico para desplegar infraestructura en Kubernetes o entornos cloud.
- Rúbrica: español _ · rationale _ · coherencia _

**groq-low**
- `no_evidence` · Propuesta de autenticación y almacenamiento para ONG
- Se propone una solución que permite a los voluntarios autenticarse con Google y almacenar sus certificados PDF. Ninguna de las herramientas del catálogo satisface completamente estas necesidades, por lo que se indica la ausencia de una herramienta adecuada.
- Limitación: Autenticación: ninguna herramienta del catálogo encaja. Ninguno de los candidatos (cert-manager, traefik, terraform) brinda autenticación directa con proveedores externos como Google; su funcionalidad es distinta.
- Limitación: Almacenamiento: ninguna herramienta del catálogo encaja. etcd es un almacén clave‑valor distribuido, no un sistema de archivos para guardar PDFs; no cumple con la necesidad de almacenar documentos binarios.
- Limitación: Para autenticación con Google sería necesario integrar una herramienta especializada en OIDC/OAuth, como Keycloak o Dex, que no está en el catálogo.
- Limitación: Para almacenar PDFs se requeriría un sistema de objetos o un gestor de archivos (ej. MinIO, Nextcloud), también fuera del catálogo.
- Supuesto: Se asume que la ONG dispone de infraestructura para ejecutar servicios web.
- Supuesto: Se asume que los certificados PDF deben estar accesibles mediante una API o interfaz de usuario.
- Rúbrica: español _ · rationale _ · coherencia _
