# Evaluación del paso de entender

Generado con `python -m ai.eval.run_understand_eval` el 2026-11-03 a las 23:21. 18 casos × 3 corridas por proveedor; la llamada de calentamiento no se cuenta.

## Modelos

| Proveedor | Modelo | Razonamiento | Arranque en frío |
|---|---|---|---|
| gemini | `gemini-3.5-flash-lite` | por defecto | 2.3 s |

## Resumen

| Métrica | gemini |
|---|---|
| Casos exactos | 63% |
| Cobertura de necesidades | 93% |
| Necesidades inventadas | 13 |
| Vagos bien tratados | 6/6 |
| Pidió aclaración sin necesidad | 0 |
| Consistencia entre corridas | 89% |
| Válida al primer intento | 100% |
| Válida tras el reintento | 100% |
| Errores del proveedor | 0/54 |
| Evidencia literal | 99% |
| Consultas de 3 a 8 palabras | 98% |
| Tiempo (mediana) | 1.2 s |
| Tiempo (peor caso) | 4.8 s |
| Tokens de entrada (mediana) | 2044 |
| Tokens de salida (mediana) | 108 |
| Esperas (límite de uso o error temporal) | 0.0 s |

Evidencia direccional: 18 casos; los porcentajes no son estadística firme.

## Por caso

Una marca por corrida: ✅ exacto · ❌ no exacto · ⚠️ error del proveedor. `+x` = detectó x sin que se esperara; `−x` = faltó x en alguna corrida.

| Caso | Esperado | gemini |
|---|---|---|
| `clinica-citas` | auth, communication, payments | ✅✅✅ |
| `tienda-ropa` | analytics, automation, payments, search | ✅✅❌ +data-processing −automation |
| `academia-online` | ai, auth, payments, storage | ✅✅✅ |
| `logistica-flota` | analytics, data-processing, database, messaging | ❌❌❌ −data-processing |
| `soporte-ia` | ai, observability, search | ✅✅✅ |
| `periodico-digital` | analytics, cms, communication, frontend | ✅❌✅ −frontend |
| `pantalla-saas-largo` | auth, database | ❌❌❌ −database |
| `pantalla-rag-largo` | ai, auth, search | ✅✅✅ |
| `pantalla-api-largo` | cache, database, infrastructure | ❌❌❌ +backend |
| `pantalla-saas-corto` | auth | ✅✅✅ |
| `pantalla-rag-corto` | ai, auth | ✅✅✅ |
| `pantalla-api-corto` | cache, infrastructure | ❌❌❌ +backend |
| `pantalla-eventos` | messaging | ❌❌❌ +payments |
| `pantalla-observabilidad` | observability | ❌❌❌ +infrastructure |
| `una-busqueda` | search | ✅✅✅ |
| `una-pagos` | payments | ✅✅✅ |
| `vago-mejorar-negocio` | (vago) | ✅✅✅ |
| `vago-startup` | (vago) | ✅✅✅ |

## Para revisar a mano (corrida 1)

### gemini

- `clinica-citas`: **auth** «gestión de cuentas de usuario» ← “reserven citas en línea con su cuenta”; **communication** «envío de recordatorios por mensajería» ← “reciban recordatorios por WhatsApp o correo”; **payments** «procesamiento de pagos en línea» ← “paguen un abono al reservar”
- `tienda-ropa`: **search** «búsqueda de texto tolerante a errores» ← “un buscador que encuentre productos aunque el cliente escriba mal”; **payments** «procesamiento de pagos con tarjeta y pasarela» ← “pagos con tarjeta y PSE”; **automation** «automatización de registro en hoja de cálculo» ← “que cada venta pase sola a nuestra hoja de cálculo contable”; **analytics** «analítica de productos más vendidos» ← “ver qué productos se venden más”
- `academia-online`: **auth** «inicio de sesión y gestión de usuarios» ← “los alumnos entran con su cuenta”; **storage** «almacenamiento de archivos multimedia» ← “ven las clases grabadas que subimos”; **payments** «cobro de suscripciones mensuales» ← “pagan la mensualidad”; **ai** «chatbot con recuperación de conocimiento» ← “tienen un chatbot que responde dudas con nuestro material”
- `logistica-flota`: **messaging** «procesamiento de eventos en tiempo real» ← “procesar esos eventos en tiempo real”; **database** «almacenamiento de datos geoespaciales» ← “guardarlos”; **analytics** «tablero de control de entregas» ← “ver tableros de entregas por ciudad”
- `soporte-ia`: **ai** «inferencia de modelos en servidores propios» ← “un modelo que corra en sus propios servidores”; **search** «busqueda de texto en documentacion» ← “un buscador para su centro de ayuda”; **observability** «monitoreo de rendimiento y errores» ← “saber cuánto tarda y cuántas veces falla el asistente”
- `periodico-digital`: **cms** «edicion sencilla de contenidos periodisticos» ← “que los periodistas publiquen desde un editor sencillo”; **frontend** «construccion de sitio web rapido» ← “un sitio web muy rápido”; **communication** «envio masivo de correos electronicos» ← “enviar el boletín diario por correo”; **analytics** «medicion de lecturas de articulos» ← “saber qué notas se leen más”
- `pantalla-saas-largo`: **auth** «autenticación mediante OIDC y control de acceso basado en roles» ← “SSO mediante OIDC y RBAC por organización”
- `pantalla-rag-largo`: **search** «búsqueda híbrida y vectorial de documentos» ← “búsqueda híbrida”; **auth** «control de acceso y permisos de usuario» ← “permisos por documento”; **ai** «servidor de inferencia para modelos locales» ← “modelos alojados en nuestra infraestructura”
- `pantalla-api-largo`: **database** «gestión de base de datos relacional» ← “PostgreSQL”; **cache** «almacenamiento en caché distribuida» ← “caché distribuida”; **infrastructure** «orquestación y escalado horizontal» ← “escalado horizontal para 10.000 solicitudes/s”; **backend** «construcción de servicios API» ← “Propón una API de alta disponibilidad”
- `pantalla-saas-corto`: **auth** «gestion de usuarios y roles organizacionales» ← “autenticación y roles por organización”
- `pantalla-rag-corto`: **ai** «recuperacion de informacion y generacion aumentada» ← “RAG privado para consultar documentos”; **auth** «gestion de permisos de acceso» ← “con permisos de acceso”
- `pantalla-api-corto`: **backend** «desarrollo de servicios de interfaz de programación» ← “Diseña una API”; **cache** «almacenamiento temporal en memoria caché» ← “con caché”; **infrastructure** «orquestación y escalado de contenedores» ← “de alta disponibilidad con [...] escalado horizontal”
- `pantalla-eventos`: **messaging** «arquitectura orientada a eventos con colas» ← “arquitectura orientada a eventos con colas, reintentos e idempotencia”; **payments** «procesamiento y cobro de pagos» ← “procesar pagos”
- `pantalla-observabilidad`: **observability** «recoleccion de metricas logs y trazas» ← “observabilidad con métricas, logs y trazas distribuidas”; **infrastructure** «orquestacion de contenedores en cluster» ← “en Kubernetes”
- `una-busqueda`: **search** «buscador de productos con tolerancia a errores» ← “buscador de productos que encuentre resultados aunque el cliente escriba mal”
- `una-pagos`: **payments** «cobro de suscripciones recurrentes» ← “cobrar suscripciones mensuales a los clientes”
- `vago-mejorar-negocio`: preguntas: ¿A qué se dedica tu negocio y qué tipo de actividades realizas actualmente? / ¿Qué problemas específicos o tareas manuales te gustaría resolver con tecnología? / ¿Utilizas algún software o herramienta actualmente en tu negocio?
- `vago-startup`: preguntas: ¿Qué tipo de producto o aplicación quieres construir para tu startup? / ¿Qué funcionalidades principales tendrá el sistema en su primera versión? / ¿Qué tecnologías, lenguajes o plataformas prefieres o ya sabes utilizar?
