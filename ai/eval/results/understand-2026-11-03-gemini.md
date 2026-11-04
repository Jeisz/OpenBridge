# Evaluación del paso de entender

Generado con `python -m ai.eval.run_understand_eval` el 2026-11-03 a las 16:05. 18 casos × 3 corridas por proveedor; la llamada de calentamiento no se cuenta.

## Modelos

| Proveedor | Modelo | Razonamiento | Arranque en frío |
|---|---|---|---|
| gemini | `gemini-3.5-flash-lite` | por defecto | 2.5 s |

## Resumen

| Métrica | gemini |
|---|---|
| Casos exactos | 67% |
| Cobertura de necesidades | 93% |
| Necesidades inventadas | 12 |
| Vagos bien tratados | 6/6 |
| Pidió aclaración sin necesidad | 0 |
| Consistencia entre corridas | 78% |
| Válida al primer intento | 100% |
| Válida tras el reintento | 100% |
| Errores del proveedor | 0/54 |
| Evidencia literal | 98% |
| Consultas de 3 a 8 palabras | 98% |
| Tiempo (mediana) | 1.2 s |
| Tiempo (peor caso) | 3.6 s |
| Tokens de entrada (mediana) | 1898 |
| Tokens de salida (mediana) | 106 |
| Esperas (límite de uso o error temporal) | 0.0 s |

Evidencia direccional: 18 casos; los porcentajes no son estadística firme.

## Por caso

Una marca por corrida: ✅ exacto · ❌ no exacto · ⚠️ error del proveedor. `+x` = detectó x sin que se esperara; `−x` = faltó x en alguna corrida.

| Caso | Esperado | gemini |
|---|---|---|
| `clinica-citas` | auth, communication, payments | ✅✅✅ |
| `tienda-ropa` | analytics, automation, payments, search | ❌✅❌ +data-processing −automation |
| `academia-online` | ai, auth, payments, storage | ✅✅✅ |
| `logistica-flota` | analytics, data-processing, database, messaging | ❌❌❌ −data-processing |
| `soporte-ia` | ai, observability, search | ✅✅✅ |
| `periodico-digital` | analytics, cms, communication, frontend | ✅✅✅ |
| `pantalla-saas-largo` | auth, database | ❌❌❌ −database |
| `pantalla-rag-largo` | ai, auth, search | ✅✅✅ |
| `pantalla-api-largo` | cache, database, infrastructure | ✅❌✅ +backend |
| `pantalla-saas-corto` | auth | ✅✅✅ |
| `pantalla-rag-corto` | ai, auth | ✅❌❌ +search +storage |
| `pantalla-api-corto` | cache, infrastructure | ❌❌❌ +backend |
| `pantalla-eventos` | messaging | ❌❌❌ +payments |
| `pantalla-observabilidad` | observability | ✅✅❌ +infrastructure |
| `una-busqueda` | search | ✅✅✅ |
| `una-pagos` | payments | ✅✅✅ |
| `vago-mejorar-negocio` | (vago) | ✅✅✅ |
| `vago-startup` | (vago) | ✅✅✅ |

## Para revisar a mano (corrida 1)

### gemini

- `clinica-citas`: **auth** «gestion de identidad de usuarios» ← “con su cuenta”; **communication** «envio de notificaciones por canales digitales» ← “reciban recordatorios por WhatsApp o correo”; **payments** «procesamiento de pagos y cobros» ← “paguen un abono al reservar”
- `tienda-ropa`: **search** «búsqueda tolerante a errores ortográficos» ← “un buscador que encuentre productos aunque el cliente escriba mal”; **payments** «procesamiento de pagos con tarjeta» ← “pagos con tarjeta y PSE”; **data-processing** «integración y sincronización de datos» ← “que cada venta pase sola a nuestra hoja de cálculo contable”; **analytics** «analítica de ventas de productos» ← “ver qué productos se venden más”
- `academia-online`: **auth** «inicio de sesión de usuarios» ← “los alumnos entran con su cuenta”; **storage** «almacenamiento de archivos de video» ← “ven las clases grabadas que subimos”; **payments** «cobros de suscripciones recurrentes» ← “pagan la mensualidad”; **ai** «asistente conversacional con inteligencia artificial» ← “tienen un chatbot que responde dudas con nuestro material”
- `logistica-flota`: **messaging** «procesamiento de flujos de eventos» ← “Cada camión envía su ubicación cada pocos segundos; quieren procesar esos eventos en tiempo real”; **database** «almacenamiento de datos geoespaciales» ← “guardarlos”; **analytics** «visualizacion de tableros de negocio» ← “ver tableros de entregas por ciudad”
- `soporte-ia`: **ai** «servidor para modelos de lenguaje locales» ← “con un modelo que corra en sus propios servidores”; **search** «búsqueda de texto en documentos» ← “un buscador para su centro de ayuda”; **observability** «monitoreo de rendimiento y errores» ← “saber cuánto tarda y cuántas veces falla el asistente”
- `periodico-digital`: **cms** «edición sencilla de contenidos periodísticos» ← “que los periodistas publiquen desde un editor sencillo”; **frontend** «construcción de sitio web rápido» ← “un sitio web muy rápido”; **communication** «envío masivo de correo electrónico» ← “enviar el boletín diario por correo”; **analytics** «medición de lectura de notas» ← “saber qué notas se leen más”
- `pantalla-saas-largo`: **auth** «autenticacion de usuarios mediante OIDC y RBAC» ← “SSO mediante OIDC y RBAC por organización”
- `pantalla-rag-largo`: **search** «búsqueda híbrida y vectorial de texto» ← “búsqueda híbrida”; **auth** «control de acceso y permisos por documento» ← “permisos por documento”; **ai** «modelos de lenguaje e inferencia local» ← “modelos alojados en nuestra infraestructura”
- `pantalla-api-largo`: **database** «gestión de base de datos relacional» ← “PostgreSQL”; **cache** «caché distribuida en memoria» ← “caché distribuida”; **infrastructure** «escalado horizontal y alta disponibilidad» ← “alta disponibilidad con PostgreSQL, caché distribuida y escalado horizontal”
- `pantalla-saas-corto`: **auth** «autenticacion y control de acceso por roles» ← “con autenticación y roles por organización.”
- `pantalla-rag-corto`: **ai** «recuperacion de informacion y generacion aumentada» ← “RAG privado para consultar documentos”; **auth** «gestion de identidad y control de acceso» ← “con permisos de acceso”
- `pantalla-api-corto`: **backend** «construccion de api web escalable» ← “Diseña una API”; **cache** «almacenamiento temporal en memoria» ← “con caché”; **infrastructure** «escalado horizontal de contenedores» ← “y escalado horizontal”
- `pantalla-eventos`: **messaging** «procesamiento asíncrono basado en eventos» ← “arquitectura orientada a eventos con colas”; **payments** «procesamiento y cobro de pagos» ← “procesar pagos”
- `pantalla-observabilidad`: **observability** «recoleccion y visualizacion de metricas logs y trazas» ← “Define un stack de observabilidad con métricas, logs y trazas distribuidas”
- `una-busqueda`: **search** «búsqueda tolerante a errores de escritura» ← “buscador de productos que encuentre resultados aunque el cliente escriba mal”
- `una-pagos`: **payments** «cobro de suscripciones recurrentes» ← “cobrar suscripciones mensuales a los clientes”
- `vago-mejorar-negocio`: preguntas: ¿A qué se dedica tu negocio y qué procesos actuales te gustaría mejorar o automatizar? / ¿Qué tipo de usuarios utilizarán el sistema (clientes, empleados, proveedores) y qué funciones principales necesitan realizar? / ¿Ya cuentas con algún sistema o software funcionando actualmente?
- `vago-startup`: preguntas: ¿Qué tipo de producto o servicio principal planeas ofrecer con tu startup? / ¿Qué funcionalidades clave necesitas que tenga el sistema en su primera versión? / ¿Tienes experiencia previa con algún lenguaje de programación o plataforma tecnológica?
