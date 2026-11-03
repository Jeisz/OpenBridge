# Evaluación del paso de entender

Generado con `python -m ai.eval.run_understand_eval` el 2026-11-02 a las 01:17. 18 casos × 3 corridas por proveedor; la llamada de calentamiento no se cuenta.

## Modelos

| Proveedor | Modelo | Razonamiento | Arranque en frío |
|---|---|---|---|
| ollama | `qwen3.5:4b-q4_K_M` | none | 27.9 s |

## Resumen

| Métrica | ollama |
|---|---|
| Casos exactos | 50% |
| Cobertura de necesidades | 83% |
| Necesidades inventadas | 31 |
| Vagos bien tratados | 5/6 |
| Pidió aclaración sin necesidad | 0 |
| Consistencia entre corridas | 22% |
| Válida al primer intento | 93% |
| Válida tras el reintento | 100% |
| Errores del proveedor | 0/54 |
| Evidencia literal | 88% |
| Consultas de 3 a 8 palabras | 72% |
| Tiempo (mediana) | 3.2 s |
| Tiempo (peor caso) | 11.4 s |
| Tokens de entrada (mediana) | 1881 |
| Tokens de salida (mediana) | 142 |
| Esperas (límite de uso o error temporal) | 0.0 s |

Evidencia direccional: 18 casos; los porcentajes no son estadística firme.

## Por caso

Una marca por corrida: ✅ exacto · ❌ no exacto · ⚠️ error del proveedor. `+x` = detectó x sin que se esperara; `−x` = faltó x en alguna corrida.

| Caso | Esperado | ollama |
|---|---|---|
| `clinica-citas` | auth, communication, payments | ✅❌✅ +frontend |
| `tienda-ropa` | analytics, automation, payments, search | ❌❌❌ +ai +data-processing +frontend +storage −analytics −automation |
| `academia-online` | ai, auth, payments, storage | ❌❌❌ +database +frontend +search −ai −payments −storage |
| `logistica-flota` | analytics, data-processing, database, messaging | ✅❌✅ −data-processing |
| `soporte-ia` | ai, observability, search | ❌✅✅ +analytics −observability |
| `periodico-digital` | analytics, cms, communication, frontend | ✅✅✅ |
| `pantalla-saas-largo` | auth, database | ✅✅❌ +backend +frontend −database |
| `pantalla-rag-largo` | ai, auth, search | ✅❌✅ +backend −ai |
| `pantalla-api-largo` | cache, database, infrastructure | ❌❌❌ +backend +frontend −infrastructure |
| `pantalla-saas-corto` | auth | ✅❌❌ +backend +database |
| `pantalla-rag-corto` | ai, auth | ❌❌❌ +database +search −ai −auth |
| `pantalla-api-corto` | cache, infrastructure | ❌❌❌ +backend −infrastructure |
| `pantalla-eventos` | messaging | ❌❌❌ +backend +database +payments |
| `pantalla-observabilidad` | observability | ✅✅❌ +infrastructure |
| `una-busqueda` | search | ✅✅✅ |
| `una-pagos` | payments | ✅✅✅ |
| `vago-mejorar-negocio` | (vago) | ✅✅✅ |
| `vago-startup` | (vago) | ✅❌✅ +backend +database +frontend +infrastructure |

## Para revisar a mano (corrida 1)

### ollama

- `clinica-citas`: **auth** «Permitir que los pacientes inicien sesión con su cuenta» ← “con su cuenta”; **payments** «Procesar la cobranza de un abono al reservar» ← “paguen un abono al reservar”; **communication** «Enviar recordatorios a pacientes por WhatsApp o correo» ← “reciban recordatorios por WhatsApp o correo”
- `tienda-ropa`: **search** «Busca productos tolerante a errores ortográfico» ← “un buscador que encuentre productos aunque el cliente escriba mal”; **payments** «Procesa pagos con tarjeta y PSE» ← “pagos con tarjeta y PSE”; **analytics** «Haga dashboards de lo que se vende más por producto» ← “ver qué productos se venden más”
- `academia-online`: **frontend** «crear interfaz para ver clases y gestionar pagos» ← “"los alumnos entran", "ven las clases grabadas"”; **auth** «permitir inicio de sesión con cuenta única» ← “"los alumnos entran con su cuenta"”; **payments** «cobrar mensualidad de manera recurrente» ← “"pagan la mensualidad"”; **search** «buscar material usando contexto semántico» ← “"responda dudas con nuestro material"”; **ai** «ejecutar modelo para generar respuestas a preguntas» ← “"tienen un chatbot que responde"”
- `logistica-flota`: **messaging** «Recibir y enviar mensajes entre servicios o procesos» ← “"quieren procesar esos eventos en tiempo real"”; **data-processing** «Mover, transformar y calcular datos por lotes o en tiempo real» ← “"Cada camión envía su ubicación cada pocos segundos"”; **database** «Almacenar información estructurada y consultarla desde el código» ← “"guardarlos"”; **analytics** «Medir eventos y mostrar tableros de negocio con dashboards» ← “"ver tableros de entregas por ciudad"”
- `soporte-ia`: **ai** «Ejecutar modelos de IA con RAG en los propios servidores» ← “con un modelo que corra en sus propios servidores, su documentación”; **search** «Buscar texto completo dentro de la base de datos» ← “un buscador para su centro de ayuda”; **analytics** «Medir tiempos de respuesta y tasas de fallo del asistente» ← “saber cuánto tarda y cuántas veces falla el asistente”
- `periodico-digital`: **cms** «Editar contenido y publicarlo para la web» ← “editores sencillo”; **frontend** «Ofrecer experiencia web rápida» ← “sitio web muy rápido”; **communication** «Enviar boletín diario por correo» ← “enviar el boletín diario por correo”; **analytics** «Medir lecturas para identificar notas populares» ← “saber qué notas se leen más”
- `pantalla-saas-largo`: **auth** «Gestionar autenticación multi-società y gestión de roles» ← “SSO mediante OIDC y RBAC por organización”; **database** «Proteger datos con aislamiento a nivel de base de datos» ← “SaaS multi-tenant con aislamiento de datos”
- `pantalla-rag-largo`: **search** «Permita búsqueda híbrida de documentos con texto completo y semántica.» ← “"RAG privado con búsqueda híbrida"”; **auth** «Gestione permisos específicos por documento para el usuario.» ← “"permisos por documento"”; **ai** «Integre modelos de IA alojados localmente sin servicios externos.» ← “"modelos alojados en nuestra infraestructura"”
- `pantalla-api-largo`: **backend** «Prover una API escableble con alta disponibilidad» ← “Propón una API de alta disponibilidad”; **database** «Almacenar datos en una base de datos relacional PostgreSQL» ← “PostgreSQL”; **cache** «Implementar un caché distribuido para responder rápidamente» ← “caché distribuida”
- `pantalla-saas-corto`: **auth** «Gestionar inicio de sesión único, roles por organización y permisos» ← “SaaS multiempresa con autenticación y roles por organización”
- `pantalla-rag-corto`: **search** «buscar texto en documentos privados» ← “'consultar documentos'”; **auth** «gestionar permisos de acceso restrictivo» ← “'con permisos de acceso'”
- `pantalla-api-corto`: **backend** «construir una arquitectura de APIs escalable» ← “Diseña una API”; **cache** «implementar almacenamiento temporal en memoria para mejorar rendimiento» ← “con caché”; **infrastructure** «orquestar servicios con alta disponibilidad y escalado horizontal» ← “escalado horizontal”
- `pantalla-eventos`: **payments** «Orquestar pagos y cobros en línea» ← “"procesar pagos"”; **messaging** «Mantener colas de mensajes de eventos» ← “"orientada a eventos con colas"”; **backend** «Garantizar la idempotencia de las operaciones» ← “"reintentos e idempotencia"”; **database** «Almacenar los estados transaccionales y reintentos» ← “nada”
- `pantalla-observabilidad`: **observability** «Medir métricas, logs y trazas distribuidados» ← “stack de observabilidad con métricas, logs y trazas distribuidos”
- `una-busqueda`: **search** «Buscar texto con corrección de fallos ortográficos» ← “"buscador de productos" ... "escritba mal"”
- `una-pagos`: **payments** «cobrar pagos recurrentes» ← “'suscripciones mensuales'}]”
- `vago-mejorar-negocio`: preguntas: ¿En qué fase del ciclo de vida operam tu empresa actualmente? / ¿Qué problemas específicos necesitas resolver para considerar la 'modernización'? / ¿Tienes ya alguna arquitectura técnica definida o prefieres desde cero?
- `vago-startup`: preguntas: ¿Qué tipo de negocio o servicio va a ofrecer? / ¿De qué manera interactúan las personas con su aplicación? / ¿Existen requisitos específicos de tecnología que considere usar?
