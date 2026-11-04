# Evaluación del paso de entender

Generado con `python -m ai.eval.run_understand_eval` el 2026-11-02 a las 01:04. 18 casos × 3 corridas por proveedor; la llamada de calentamiento no se cuenta.

## Modelos

| Proveedor | Modelo | Razonamiento | Arranque en frío |
|---|---|---|---|
| gemini | `gemini-3.5-flash-lite` | por defecto | 1.9 s |
| groq | `openai/gpt-oss-120b` | por defecto | 1.3 s |

## Resumen

| Métrica | gemini | groq |
|---|---|---|
| Casos exactos | 56% | 67% |
| Cobertura de necesidades | 91% | 96% |
| Necesidades inventadas | 16 | 18 |
| Vagos bien tratados | 6/6 | 6/6 |
| Pidió aclaración sin necesidad | 0 | 0 |
| Consistencia entre corridas | 78% | 83% |
| Válida al primer intento | 100% | 100% |
| Válida tras el reintento | 100% | 100% |
| Errores del proveedor | 0/54 | 0/54 |
| Evidencia literal | 99% | 97% |
| Consultas de 3 a 8 palabras | 98% | 100% |
| Tiempo (mediana) | 1.2 s | 1.8 s |
| Tiempo (peor caso) | 5.0 s | 5.6 s |
| Tokens de entrada (mediana) | 1834 | 2132 |
| Tokens de salida (mediana) | 124 | 456 |
| Esperas (límite de uso o error temporal) | 0.0 s | 497.0 s |

Evidencia direccional: 18 casos; los porcentajes no son estadística firme.

## Por caso

Una marca por corrida: ✅ exacto · ❌ no exacto · ⚠️ error del proveedor. `+x` = detectó x sin que se esperara; `−x` = faltó x en alguna corrida.

| Caso | Esperado | gemini | groq |
|---|---|---|---|
| `clinica-citas` | auth, communication, payments | ✅✅✅ | ❌❌❌ +backend +frontend |
| `tienda-ropa` | analytics, automation, payments, search | ❌❌✅ +data-processing −automation | ✅✅✅ |
| `academia-online` | ai, auth, payments, storage | ✅✅✅ | ✅✅✅ |
| `logistica-flota` | analytics, data-processing, database, messaging | ❌❌❌ −data-processing −messaging | ❌❌❌ −messaging |
| `soporte-ia` | ai, observability, search | ✅✅✅ | ✅✅✅ |
| `periodico-digital` | analytics, cms, communication, frontend | ✅✅✅ | ✅✅✅ |
| `pantalla-saas-largo` | auth, database | ❌❌❌ −database | ✅✅✅ |
| `pantalla-rag-largo` | ai, auth, search | ❌❌✅ −auth | ✅✅✅ |
| `pantalla-api-largo` | cache, database, infrastructure | ❌❌❌ +backend | ❌❌❌ +backend −infrastructure |
| `pantalla-saas-corto` | auth | ✅✅✅ | ✅✅✅ |
| `pantalla-rag-corto` | ai, auth | ❌✅❌ +search +storage | ❌❌❌ +search +storage −ai |
| `pantalla-api-corto` | cache, infrastructure | ❌❌❌ +backend | ❌❌❌ +backend |
| `pantalla-eventos` | messaging | ❌❌❌ +payments | ❌❌❌ +payments |
| `pantalla-observabilidad` | observability | ❌❌❌ +infrastructure | ✅✅✅ |
| `una-busqueda` | search | ✅✅✅ | ✅✅✅ |
| `una-pagos` | payments | ✅✅✅ | ✅✅✅ |
| `vago-mejorar-negocio` | (vago) | ✅✅✅ | ✅✅✅ |
| `vago-startup` | (vago) | ✅✅✅ | ✅✅✅ |

## Para revisar a mano (corrida 1)

### gemini

- `clinica-citas`: **auth** «gestionar cuentas de usuario» ← “con su cuenta”; **communication** «enviar recordatorios por whatsapp y correo» ← “reciban recordatorios por WhatsApp o correo”; **payments** «cobrar un abono al reservar» ← “paguen un abono al reservar”
- `tienda-ropa`: **search** «buscador tolerante a errores de escritura» ← “un buscador que encuentre productos aunque el cliente escriba mal”; **payments** «procesar pagos con tarjeta y PSE» ← “pagos con tarjeta y PSE”; **data-processing** «enviar ventas a hoja contable» ← “que cada venta pase sola a nuestra hoja de cálculo contable”; **analytics** «analizar productos más vendidos» ← “ver qué productos se venden más”
- `academia-online`: **auth** «gestionar inicio de sesion de usuarios» ← “los alumnos entran con su cuenta”; **storage** «guardar clases grabadas en video» ← “ven las clases grabadas que subimos”; **payments** «cobrar la mensualidad a alumnos» ← “pagan la mensualidad”; **ai** «chatbot para responder dudas con material» ← “tienen un chatbot que responde dudas con nuestro material”
- `logistica-flota`: **messaging** «procesar eventos de ubicación en tiempo real» ← “Cada camión envía su ubicación cada pocos segundos; quieren procesar esos eventos en tiempo real”; **database** «guardar datos de ubicación y entregas» ← “guardarlos”; **analytics** «ver tableros de entregas por ciudad» ← “ver tableros de entregas por ciudad”
- `soporte-ia`: **ai** «ejecutar modelo de inteligencia artificial en servidores propios» ← “con un modelo que corra en sus propios servidores”; **search** «buscar dentro de la documentación del centro de ayuda» ← “un buscador para su centro de ayuda”; **observability** «monitorear rendimiento y errores del sistema» ← “saber cuánto tarda y cuántas veces falla el asistente”
- `periodico-digital`: **cms** «publicar notas desde un editor sencillo» ← “que los periodistas publiquen desde un editor sencillo”; **frontend** «construir un sitio web muy rápido» ← “un sitio web muy rápido”; **communication** «enviar el boletín diario por correo» ← “enviar el boletín diario por correo”; **analytics** «saber qué notas se leen más» ← “saber qué notas se leen más”
- `pantalla-saas-largo`: **auth** «Implementar SSO con OIDC y control de accesos» ← “SSO mediante OIDC y RBAC por organización”
- `pantalla-rag-largo`: **ai** «Servir modelos de lenguaje localmente» ← “modelos alojados en nuestra infraestructura”; **search** «Búsqueda híbrida y vectorial con filtrado» ← “búsqueda híbrida, permisos por documento”
- `pantalla-api-largo`: **database** «Base de datos PostgreSQL de alta disponibilidad» ← “PostgreSQL”; **cache** «Caché distribuida para alto rendimiento» ← “caché distribuida”; **backend** «API de alta disponibilidad con escalado horizontal» ← “API de alta disponibilidad con... escalado horizontal para 10.000 solicitudes/s”; **infrastructure** «Orquestación para escalado horizontal de servicios» ← “escalado horizontal para 10.000 solicitudes/s”
- `pantalla-saas-corto`: **auth** «gestionar autenticacion y roles por organizacion» ← “autenticación y roles por organización”
- `pantalla-rag-corto`: **ai** «construir un sistema RAG privado» ← “RAG privado”; **search** «buscar documentos mediante similitud vectorial» ← “consultar documentos”; **auth** «gestionar permisos de acceso de usuarios» ← “con permisos de acceso”
- `pantalla-api-corto`: **backend** «construir una API de alta disponibilidad» ← “Diseña una API de alta disponibilidad”; **cache** «añadir capa de caché en memoria» ← “con caché”; **infrastructure** «configurar infraestructura para escalado horizontal» ← “escalado horizontal”
- `pantalla-eventos`: **messaging** «gestionar colas y eventos de pagos» ← “arquitectura orientada a eventos con colas, reintentos e idempotencia para procesar pagos”; **payments** «procesar transacciones de pagos en línea» ← “procesar pagos”
- `pantalla-observabilidad`: **observability** «recopilar y visualizar métricas, logs y trazas distribuidas» ← “Define un stack de observabilidad con métricas, logs y trazas distribuidas”; **infrastructure** «ejecutar aplicaciones en contenedores en Kubernetes» ← “para microservicios en Kubernetes.”
- `una-busqueda`: **search** «buscar productos con tolerancia a errores» ← “un buscador de productos que encuentre resultados aunque el cliente escriba mal.”
- `una-pagos`: **payments** «cobrar suscripciones mensuales a clientes» ← “Necesito cobrar suscripciones mensuales a los clientes de mi software.”
- `vago-mejorar-negocio`: preguntas: ¿A qué se dedica tu negocio y qué problema principal buscas resolver? / ¿Qué tipo de herramientas o sistemas utilizas actualmente en tu operación diaria? / ¿Qué procesos específicos te gustaría automatizar o mejorar con tecnología?
- `vago-startup`: preguntas: ¿Qué tipo de producto o servicio ofrecerá tu startup? / ¿Qué funcionalidades principales tendrá la primera versión de tu aplicación? / ¿Tienes experiencia previa con algún lenguaje de programación o tecnología en particular?

### groq

- `clinica-citas`: **auth** «gestionar inicio de sesión de usuarios» ← “reserven citas en línea con su cuenta”; **communication** «enviar recordatorios por WhatsApp y correo» ← “reciban recordatorios por WhatsApp o correo”; **payments** «procesar pagos al reservar cita» ← “paguen un abono al reservar”; **backend** «manejar lógica de reservas y API» ← “reservar citas en línea con su cuenta”
- `tienda-ropa`: **search** «búsqueda tolerante a errores» ← “un buscador que encuentre productos aunque el cliente escriba mal”; **payments** «procesar pagos con tarjeta y PSE» ← “pagos con tarjeta y PSE”; **automation** «exportar ventas a hoja de cálculo» ← “cada venta pase sola a nuestra hoja de cálculo contable”; **analytics** «analizar productos más vendidos» ← “ver qué productos se venden más”
- `academia-online`: **auth** «gestionar autenticación de usuarios» ← “los alumnos entran con su cuenta”; **storage** «almacenar y servir videos» ← “ven las clases grabadas que subimos”; **payments** «procesar pagos recurrentes» ← “pagan la mensualidad”; **ai** «chatbot con IA para preguntas» ← “tienen un chatbot que responde dudas con nuestro material”
- `logistica-flota`: **database** «almacenar ubicaciones de camiones» ← “guardarlos”; **data-processing** «procesar eventos en tiempo real» ← “procesar esos eventos en tiempo real”; **analytics** «ver tableros de entregas por ciudad» ← “ver tableros de entregas por ciudad”
- `soporte-ia`: **ai** «servir modelo de IA» ← “un modelo que corra en sus propios servidores”; **search** «buscar en documentación» ← “un buscador para su centro de ayuda”; **observability** «monitorizar latencia y fallos» ← “saber cuánto tarda y cuántas veces falla el asistente”
- `periodico-digital`: **cms** «gestionar contenido editorial» ← “publicen desde un editor sencillo”; **frontend** «construir sitio web rápido» ← “un sitio web muy rápido”; **communication** «enviar boletín diario por email» ← “enviar el boletín diario por correo”; **analytics** «medir lecturas de notas» ← “saber qué notas se leen más”
- `pantalla-saas-largo`: **database** «almacenar datos aislados por inquilinos» ← “aislamiento de datos”; **auth** «autenticación SSO con OIDC y RBAC» ← “SSO mediante OIDC y RBAC por organización”
- `pantalla-rag-largo`: **search** «realizar búsqueda híbrida» ← “búsqueda híbrida”; **auth** «controlar acceso por documento» ← “permisos por documento”; **ai** «servir modelos de IA internamente» ← “modelos alojados en nuestra infraestructura”
- `pantalla-api-largo`: **database** «Almacenar datos relacionales» ← “con PostgreSQL”; **cache** «Almacenar caché en memoria distribuida» ← “caché distribuida”; **backend** «Servir API de alta disponibilidad» ← “API de alta disponibilidad”
- `pantalla-saas-corto`: **auth** «gestionar autenticación y roles» ← “autenticación y roles por organización”
- `pantalla-rag-corto`: **auth** «gestionar permisos de acceso» ← “con permisos de acceso”; **search** «buscar documentos relevantes» ← “consultar documentos”; **ai** «generar respuestas con LLM» ← “RAG”; **storage** «almacenar documentos de forma segura» ← “consultar documentos con permisos de acceso”
- `pantalla-api-corto`: **backend** «Crear API REST» ← “Diseña una API de alta disponibilidad”; **cache** «Almacenar respuestas en caché» ← “con caché”; **infrastructure** «Orquestar despliegue escalable» ← “escalado horizontal”
- `pantalla-eventos`: **payments** «procesar pagos en línea» ← “para procesar pagos”; **messaging** «orquestar eventos con colas» ← “arquitectura orientada a eventos con colas, reintentos e idempotencia”
- `pantalla-observabilidad`: **observability** «recopilar métricas, logs y trazas» ← “stack de observabilidad con métricas, logs y trazas distribuidas”
- `una-busqueda`: **search** «buscar productos con tolerancia a errores» ← “agregar a mi sitio un buscador de productos que encuentre resultados aunque el cliente escriba mal”
- `una-pagos`: **payments** «gestionar cobros recurrentes» ← “Necesito cobrar suscripciones mensuales a los clientes de mi software.”
- `vago-mejorar-negocio`: preguntas: ¿Cuál es el principal producto o servicio de su negocio? / ¿Qué áreas específicas (ventas, atención al cliente, gestión interna, etc.) desea modernizar? / ¿Qué sistemas o herramientas está utilizando actualmente y qué problemas enfrenta con ellos?
- `vago-startup`: preguntas: ¿Cuál es el modelo de negocio de tu startup? / ¿Qué tipo de producto o servicio ofrecerás? / ¿Qué funcionalidades principales necesitas en tu producto o aplicación?
