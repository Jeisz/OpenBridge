# Evaluación del paso de entender

Generado con `python -m ai.eval.run_understand_eval` el 2026-11-03 a las 22:17. 5 casos × 3 corridas por proveedor; la llamada de calentamiento no se cuenta.

## Modelos

| Proveedor | Modelo | Razonamiento | Arranque en frío |
|---|---|---|---|
| gemini | `gemini-3.5-flash-lite` | por defecto | 1.6 s |
| groq-low | `openai/gpt-oss-120b` | low | 1.1 s |

## Resumen

| Métrica | gemini | groq-low |
|---|---|---|
| Casos exactos | 87% | 80% |
| Cobertura de necesidades | 93% | 100% |
| Necesidades inventadas | 3 | 3 |
| Vagos bien tratados | 0/0 | 0/0 |
| Pidió aclaración sin necesidad | 0 | 0 |
| Consistencia entre corridas | 80% | 100% |
| Válida al primer intento | 100% | 100% |
| Válida tras el reintento | 100% | 100% |
| Errores del proveedor | 0/15 | 0/15 |
| Evidencia literal | 100% | 90% |
| Consultas de 3 a 8 palabras | 100% | 100% |
| Tiempo (mediana) | 1.1 s | 1.2 s |
| Tiempo (peor caso) | 1.7 s | 1.4 s |
| Tokens de entrada (mediana) | 2064 | 2304 |
| Tokens de salida (mediana) | 113 | 139 |
| Esperas (límite de uso o error temporal) | 0.0 s | 182.0 s |

Evidencia direccional: 5 casos; los porcentajes no son estadística firme.

## Por caso

Una marca por corrida: ✅ exacto · ❌ no exacto · ⚠️ error del proveedor. `+x` = detectó x sin que se esperara; `−x` = faltó x en alguna corrida.

| Caso | Esperado | gemini | groq-low |
|---|---|---|---|
| `inmobiliaria-portal` | search, storage | ✅✅✅ | ✅✅✅ |
| `agencia-viajes-web` | frontend | ✅✅✅ | ✅✅✅ |
| `cooperativa-api` | backend, database | ✅✅✅ | ✅✅✅ |
| `colegio-avisos` | communication, data-processing | ✅❌❌ +backend +database −data-processing | ❌❌❌ +database |
| `ong-voluntarios` | auth, storage | ✅✅✅ | ✅✅✅ |

## Para revisar a mano (corrida 1)

### gemini

- `inmobiliaria-portal`: **search** «búsqueda semántica de texto libre» ← “escribiendo cosas como 'apartamento con balcón cerca del metro'”; **storage** «almacenamiento de archivos multimedia y documentos» ← “los agentes suben las fotos y los planos de cada inmueble”
- `agencia-viajes-web`: **frontend** «framework web para renderizado rápido» ← “Necesitamos un framework web para construir páginas de destinos que carguen muy rápido y se posicionen bien en Google.”
- `cooperativa-api`: **backend** «framework para construir la api» ← “un framework para la API que registra las entregas de café de cada productor”; **database** «base de datos relacional» ← “una base de datos relacional para guardar esos registros”
- `colegio-avisos`: **communication** «envío de correos y mensajes de texto» ← “avisar por correo o SMS a los padres cuando baje del 80 %”; **data-processing** «cálculo automático de porcentajes de asistencia» ← “Cada noche debe calcular el porcentaje de asistencia de cada estudiante”
- `ong-voluntarios`: **auth** «inicio de sesión con proveedores externos» ← “que sus voluntarios entren con su cuenta de Google”; **storage** «almacenamiento de archivos y documentos» ← “guardar los certificados escaneados de cada uno en PDF”

### groq-low

- `inmobiliaria-portal`: **search** «búsqueda de texto completo» ← “Los clientes tienen que poder buscar propiedades escribiendo cosas como 'apartamento con balcón cerca del metro'”; **storage** «almacenamiento de archivos y objetos» ← “Los agentes suben las fotos y los planos de cada inmueble”
- `agencia-viajes-web`: **frontend** «desarrollo de frontend rápido y SEO» ← “Necesitamos un framework web para construir páginas de destinos que carguen muy rápido y se posicionen bien en Google.”
- `cooperativa-api`: **backend** «framework para construir API» ← “Queremos elegir un framework para la API que registra las entregas de café de cada productor”; **database** «base de datos relacional» ← “una base de datos relacional para guardar esos registros”
- `colegio-avisos`: **database** «almacenamiento de datos estructurados» ← “los profesores registren la asistencia”; **data-processing** «procesamiento por lotes y cálculos» ← “Cada noche debe calcular el porcentaje de asistencia de cada estudiante”; **communication** «envío de notificaciones por correo y SMS» ← “avisar por correo o SMS a los padres cuando baje del 80 %”
- `ong-voluntarios`: **auth** «autenticación mediante Google» ← “entrar con su cuenta de Google”; **storage** «almacenamiento de archivos PDF» ← “guardar los certificados escaneados de cada uno en PDF”
