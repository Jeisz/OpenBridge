# Evaluación del paso de entender

Generado con `python -m ai.eval.run_understand_eval` el 2026-11-02 a las 10:17. 18 casos × 3 corridas por proveedor; la llamada de calentamiento no se cuenta.

## Modelos

| Proveedor | Modelo | Razonamiento | Arranque en frío |
|---|---|---|---|
| groq-low | `openai/gpt-oss-120b` | low | 1.4 s |

## Resumen

| Métrica | groq-low |
|---|---|
| Casos exactos | 74% |
| Cobertura de necesidades | 95% |
| Necesidades inventadas | 17 |
| Vagos bien tratados | 6/6 |
| Pidió aclaración sin necesidad | 0 |
| Consistencia entre corridas | 67% |
| Válida al primer intento | 100% |
| Válida tras el reintento | 100% |
| Errores del proveedor | 0/54 |
| Evidencia literal | 96% |
| Consultas de 3 a 8 palabras | 98% |
| Tiempo (mediana) | 1.1 s |
| Tiempo (peor caso) | 3.1 s |
| Tokens de entrada (mediana) | 2084 |
| Tokens de salida (mediana) | 178 |
| Esperas (límite de uso o error temporal) | 414.0 s |

Evidencia direccional: 18 casos; los porcentajes no son estadística firme.

## Por caso

Una marca por corrida: ✅ exacto · ❌ no exacto · ⚠️ error del proveedor. `+x` = detectó x sin que se esperara; `−x` = faltó x en alguna corrida.

| Caso | Esperado | groq-low |
|---|---|---|
| `clinica-citas` | auth, communication, payments | ✅✅✅ |
| `tienda-ropa` | analytics, automation, payments, search | ✅✅✅ |
| `academia-online` | ai, auth, payments, storage | ✅✅✅ |
| `logistica-flota` | analytics, data-processing, database, messaging | ❌✅❌ +backend −data-processing |
| `soporte-ia` | ai, observability, search | ✅✅✅ |
| `periodico-digital` | analytics, cms, communication, frontend | ✅❌✅ −frontend |
| `pantalla-saas-largo` | auth, database | ✅✅✅ |
| `pantalla-rag-largo` | ai, auth, search | ✅✅✅ |
| `pantalla-api-largo` | cache, database, infrastructure | ❌✅❌ +backend −infrastructure |
| `pantalla-saas-corto` | auth | ✅✅✅ |
| `pantalla-rag-corto` | ai, auth | ❌❌❌ +backend +search +storage −ai |
| `pantalla-api-corto` | cache, infrastructure | ❌❌❌ +backend −infrastructure |
| `pantalla-eventos` | messaging | ❌❌❌ +backend +payments |
| `pantalla-observabilidad` | observability | ✅✅✅ |
| `una-busqueda` | search | ✅✅✅ |
| `una-pagos` | payments | ✅✅✅ |
| `vago-mejorar-negocio` | (vago) | ✅✅✅ |
| `vago-startup` | (vago) | ✅✅✅ |

## Para revisar a mano (corrida 1)

### groq-low

- `clinica-citas`: **auth** «gestionar autenticación de usuarios» ← “quieran que los pacientes reserven citas en línea con su cuenta”; **communication** «enviar notificaciones a pacientes» ← “reciban recordatorios por WhatsApp o correo”; **payments** «procesar pagos en línea» ← “paguen un abono al reservar”
- `tienda-ropa`: **search** «búsqueda tolerante a errores» ← “un buscador que encuentre productos aunque el cliente escriba mal”; **payments** «procesar pagos con tarjeta y PSE» ← “pagos con tarjeta y PSE”; **analytics** «analizar ventas por producto» ← “ver qué productos se venden más”; **automation** «exportar ventas a hoja de cálculo» ← “cada venta pase sola a nuestra hoja de cálculo contable”
- `academia-online`: **auth** «gestionar autenticación de usuarios» ← “los alumnos entran con su cuenta”; **storage** «almacenar y servir archivos multimedia» ← “ven las clases grabadas que subimos”; **payments** «procesar pagos recurrentes» ← “pagan la mensualidad”; **ai** «implementar chatbot con IA» ← “tienen un chatbot que responde dudas con nuestro material”
- `logistica-flota`: **messaging** «procesar eventos en tiempo real» ← “Cada camión envía su ubicación cada pocos segundos; quieren procesar esos eventos en tiempo real”; **database** «almacenar datos de ubicación» ← “guardarlos”; **backend** «lógica de procesamiento de eventos» ← “procesar esos eventos en tiempo real”; **analytics** «visualizar tableros de entregas» ← “ver tableros de entregas por ciudad”
- `soporte-ia`: **ai** «correr modelo localmente» ← “con un modelo que corra en sus propios servidores”; **search** «buscar en la documentación» ← “un buscador para su centro de ayuda”; **observability** «medir latencia y fallos» ← “saber cuánto tarda y cuántas veces falla el asistente”
- `periodico-digital`: **cms** «gestionar contenido editorial» ← “publicar desde un editor sencillo”; **frontend** «construir interfaz web veloz» ← “un sitio web muy rápido”; **communication** «enviar correos electrónicos» ← “enviar el boletín diario por correo”; **analytics** «medir lectura de artículos» ← “saber qué notas se leen más”
- `pantalla-saas-largo`: **database** «almacenar datos aislados por tenant» ← “multi-tenant con aislamiento de datos”; **auth** «gestionar autenticación y autorización» ← “SSO mediante OIDC y RBAC por organización”
- `pantalla-rag-largo`: **search** «búsqueda híbrida privada» ← “búsqueda híbrida”; **auth** «control de acceso por documento» ← “permisos por documento”; **ai** «modelo de IA alojado internamente» ← “modelos alojados en nuestra infraestructura”
- `pantalla-api-largo`: **database** «almacenar datos en PostgreSQL» ← “API de alta disponibilidad con PostgreSQL”; **cache** «caché distribuida para alta velocidad» ← “caché distribuida”
- `pantalla-saas-corto`: **auth** «gestionar autenticación y roles» ← “Diseña un SaaS multiempresa con autenticación y roles por organización.”
- `pantalla-rag-corto`: **search** «buscar en documentos semánticamente» ← “consultar documentos”; **auth** «controlar permisos de acceso» ← “con permisos de acceso”; **storage** «almacenar documentos privados» ← “consultar documentos”; **backend** «exponer API de RAG» ← “RAG privado”; **ai** «generar respuestas con LLM» ← “RAG privado”
- `pantalla-api-corto`: **backend** «crear API escalable» ← “Diseña una API de alta disponibilidad”; **cache** «añadir caché para respuestas» ← “con caché”; **infrastructure** «implementar escalado horizontal» ← “escalado horizontal”
- `pantalla-eventos`: **messaging** «gestionar colas y reintentos» ← “orientada a eventos con colas, reintentos”; **payments** «procesar pagos» ← “procesar pagos”
- `pantalla-observabilidad`: **observability** «monitorizar métricas y trazas» ← “Define un stack de observabilidad con métricas, logs y trazas distribuidas para microservicios en Kubernetes.”
- `una-busqueda`: **search** «buscar productos con tolerancia a errores» ← “Quiero agregar a mi sitio un buscador de productos que encuentre resultados aunque el cliente escriba mal.”
- `una-pagos`: **payments** «cobrar suscripciones mensuales» ← “Necesito cobrar suscripciones mensuales a los clientes de mi software.”
- `vago-mejorar-negocio`: preguntas: ¿Qué tipo de aplicación o servicio deseas crear o mejorar? / ¿Necesitas funcionalidades específicas como pagos, autenticación, o análisis de datos? / ¿Qué infraestructura o plataformas ya estás usando y deseas integrar?
- `vago-startup`: preguntas: ¿Cuál es el tipo de producto o servicio que ofrecerá la startup? / ¿Qué funcionalidades principales necesita su aplicación (por ejemplo, autenticación, pagos, búsqueda, etc.)? / ¿En qué entorno planea desplegar la solución (cloud, on‑premise, Kubernetes, etc.)?
