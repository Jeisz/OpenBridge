# Modelo de lenguaje del asistente: decisión y evidencia

**Decisión (3-nov-2026):** el asistente usa **Gemini 3.5 Flash-Lite** como modelo principal y
**gpt-oss-120b en Groq, con razonamiento bajo** (`groq-low`) como respaldo. Claude Haiku 5.5
queda en el registro como opción evaluada, no por defecto.

Se cambia con una variable (`AI_LLM_PROVIDER`), sin tocar el código. Cómo configurarlo:
[`../README.md`](../README.md) → "Modelo de lenguaje".

## Qué hace el modelo en el asistente

El asistente responde en tres pasos. Solo dos usan el modelo de lenguaje:

1. **Entender** (modelo): convierte el pedido en necesidades (una categoría del catálogo, una
  consulta corta en español y el fragmento del pedido que la justifica), o en preguntas si el
  pedido es vago.
2. **Buscar** (código, sin modelo de lenguaje): busca en el catálogo con embeddings, una vez por
  necesidad, y se queda con los candidatos que superan el umbral.
3. **Generar** (modelo): elige una herramienta por necesidad, **solo entre los candidatos de
  esa necesidad**, y explica la propuesta. El código arma la respuesta del contrato y la valida.

El modelo escribe con **salida estructurada**: el proveedor recibe un esquema JSON y la respuesta
se valida con Pydantic. Si no cumple el esquema o las reglas que el esquema no puede expresar
(por ejemplo, que el repo sea candidato de *esa* necesidad), se reintenta **una vez**, con un
mensaje que dice qué regla no se cumplió.

## Criterios

- Costo $0, o casi, para desarrollo y demo.
- Por API: el servicio no tiene GPU.
- Formato compatible con OpenAI y salida con esquema.
- Español natural.
- **Presupuesto de 15 s** para todo el flujo (el frontend espera 20 s).
- Elegir bien entre los candidatos y no salirse de ellos.

## Cómo se midió

- **Flujo completo** (entender → buscar → generar) sobre el snapshot del catálogo real (100 repos):
  5 casos de prueba × 3 corridas por modelo, más una llamada de calentamiento que no se cuenta.
  Casos en [`ASSISTANT_CASES.md`](ASSISTANT_CASES.md).
- **Entender, por separado:** 18 casos × 3 corridas.
- **Diagnóstico de latencia:** la misma petición de generar para todos los modelos, en streaming,
  para separar el tiempo que el modelo pasa razonando del tiempo que pasa escribiendo
  (`diagnose_latency.py`).
- **Revisión manual** de los mapas con una rúbrica de 1 a 3: español, razón ligada al negocio y
  coherencia.

Con 5 casos, los porcentajes son evidencia direccional, no estadística firme.

## Resultados (flujo completo, prompt definitivo)

Reporte: [`results/assistant-2026-11-03-gemini-groq-low-claude-haiku.md`](results/assistant-2026-11-03-gemini-groq-low-claude-haiku.md).

|     | Gemini 3.5 Flash-Lite | gpt-oss-120b (Groq, bajo) | Claude Haiku 5.5 |
| --- | --- | --- | --- |
| Errores del proveedor | **0/15** | 1/15 | 0/15 |
| Válido al 1.er intento (generar) | **100 %** | **100 %** | 33 % |
| Eligió un repo aceptable (donde había) | 73 % | 70 % | **82 %** |
| Se abstuvo (donde no había) | 40 % | 22 % | **67 %** |
| Consistencia entre corridas | 60 % | 40 % | 60 % |
| Tiempo total, mediana · peor caso | 3,9 s · 5,3 s | **2,5 s · 4,3 s** | 10,2 s · 19,2 s |
| Revisión manual (promedio, 1–3) | 2,67 | 2,44 | 2,78 |
| Costo | $0 (nivel gratuito) | $0 (nivel gratuito) | De pago |

El error de Groq fue un rechazo del JSON con un mensaje que el código todavía no reconocía; ya
se trata como respuesta inválida, con reintento.

## Por qué

- **Gemini, principal:** 0 errores, cumple las reglas al primer intento y queda muy por debajo
  del presupuesto. En calidad de texto, los tres modelos quedan cerca.
- **gpt-oss-120b en Groq, respaldo:** es el más rápido y también cumple al primer intento. Elige
  y se abstiene peor. Su límite gratuito de **8.000 tokens por minuto** permite pocas consultas
  seguidas: sirve para cubrir una caída de Gemini, no para reemplazarlo.
- **Claude Haiku 5.5, fuera del uso por defecto:** elige mejor y explica mejor. Pero en 2 de cada
  3 pedidos su primer intento choca con dos reglas del diseño (un repo por necesidad y solo los
  candidatos de esa necesidad), y el reintento lleva la mediana a ~10 s, con un caso de 19 s. Es
  de pago.

## Descartados, con la causa medida

| Modelo | Causa |
| --- | --- |
| Qwen 3.5 4B en Ollama (local) | Escribe a ~50 tokens/s en la GPU de desarrollo: solo generar tarda 12–16 s, sin contar entender ni el arranque en frío (~37 s) |
| Gemma 4 26B (API de Gemini) | Entra en bucle al escribir el JSON ("manera manera manera…") y no lo termina |
| Gemini 3.1 Flash-Lite | Errores 503 del servidor durante horas; en el flujo, 3 de 15 llamadas cortadas a los 15 s y un peor caso de 17,4 s |

## Hallazgos que cambiaron la configuración

- **Razonamiento oculto.** Claude 5 razona por defecto antes de responder, y esa parte no se ve
  en la respuesta. Medido con la misma petición: ~10 s razonando frente a ~5 s sin razonar. Se
  apaga en el registro (`extra_body`). El mismo patrón estaba en Ollama y en Groq (razonamiento
  bajo: menos tokens y menos esperas por el límite por minuto).
- **Compilar el esquema** cuesta entre 0 y 2,5 s por pedido nuevo en Claude. No era la causa
  principal de su lentitud.
- **Reglas con salida y reintentos que orientan:** cuando una necesidad pide varias herramientas,
  se elige la principal y las demás se nombran como limitación. Los mensajes de reintento dicen
  qué necesidad falla y qué hacer, sin suponer nada sobre el pedido. Con esto Claude pasó de 80 %
  a 93 % de respuestas válidas, y los tres modelos nombran los complementos.

## Qué se pierde

- Elecciones mejores en pedidos que piden varias herramientas para una sola necesidad (por
  ejemplo, observabilidad: Gemini elige Grafana y nombra como complementos al colector de
  OpenTelemetry y a Jaeger).
- Con el nivel gratuito, **Google usa el contenido de las consultas** para mejorar sus servicios.
  Las consultas describen negocios, no datos personales. Con una cuenta de pago no los usa.
- Límite gratuito de Gemini 3.5 Flash-Lite: 500 consultas al modelo por día y 15 por minuto
  (leído en AI Studio). Cada pedido del asistente usa una o dos llamadas, más los reintentos.

## Pendiente para la integración del servicio

- **Límite de tiempo total del flujo.** Hoy cada llamada tiene 15 s, pero con reintentos el peor
  caso teórico es de ~60 s.
- **Cambio automático al respaldo** cuando el principal falla.
- **Decisiones de diseño que hoy limitan a los modelos más capaces:** ¿permitir un candidato de
  otra necesidad?, ¿más de una caja por necesidad? Las dos cambian la regla de grounding o el
  contrato con el frontend.
- **Texto:** decir qué *no* cubre cada herramienta (Gemini y Groq prometen de más), no usar
  frases internas del sistema y definir el trato al usuario (tú o usted).
- **Búsqueda:** varios aceptables no llegan a los candidatos (por ejemplo, ClickHouse para guardar
  eventos). Es un límite de la búsqueda, no del modelo.

## Cómo repetirlo

```bash
python -m ai.scripts.check_llm gemini groq-low            # prueba de humo
python -m ai.eval.run_understand_eval gemini groq-low      # entender, 18 casos
python -m ai.eval.run_assistant_eval gemini groq-low       # flujo completo, casos rápidos
python -m ai.eval.diagnose_latency gemini claude-compat    # dónde se va el tiempo de generar
```

Requiere las claves en `.env`. Groq espera entre pedidos por su límite por minuto: el flujo
completo tarda unos 15 minutos.
