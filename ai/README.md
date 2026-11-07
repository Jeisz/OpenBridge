# ai/ — Vertical de IA de OpenBridge

Asistente que recibe la descripción de un negocio y recomienda un stack de
herramientas open source, citando solo repos del catálogo.

Esta carpeta tiene su propio `requirements.txt`, sus datos y sus tests. La forma
de un repo no se define aquí: se usa el contrato compartido `Repo` de
[`shared/contracts/`](../shared/contracts/). Por eso los comandos se ejecutan
desde la raíz del repo.

## Estado

**Datos.** La IA lee el snapshot del catálogo real (`data/catalog/`, 100 repos de la vista
`public.v_repos_for_ai`) con `load_repos()`. Los 20 repos de ejemplo (`data/repos.json`,
con categorías asignadas a mano) se conservan para pruebas y para repetir la elección del
modelo de embeddings: `load_repos(source="sample")`.

**Búsqueda semántica.** Dada la necesidad de un cliente en lenguaje natural (en español o inglés),
devuelve los repos del catálogo más parecidos por significado, con filtros por licencia,
health score y categoría.

**Evaluación de la búsqueda.** Dos golden sets (catálogo real y datos de ejemplo), métricas
(hit@3, MRR, recall) y umbral de "sin evidencia", con un solo comando. Resultados y
decisiones en [`eval/SEARCH_DECISION.md`](eval/SEARCH_DECISION.md).

**Casos de prueba del asistente.** 18 pedidos de negocio con el status, las necesidades y
los repos aceptables esperados, escritos contra el snapshot del catálogo real, y 5 casos de
validación aparte para comprobar reglas nuevas con pedidos que el prompt no vio. Detalle en
[`eval/ASSISTANT_CASES.md`](eval/ASSISTANT_CASES.md).

**Asistente.** `asistir()` responde un pedido en tres pasos: **entender** (modelo de lenguaje:
necesidades o preguntas), **buscar** (embeddings, una búsqueda por necesidad) y **generar** el
mapa (modelo de lenguaje: una herramienta por necesidad, solo entre sus 5 primeros candidatos,
o ninguna si no sirven). El modelo escribe con salida estructurada; el código valida contra el
contrato `AssistantResponse` y reintenta una vez si no cumple. Todo el pedido tiene un
presupuesto de 15 s, y si el proveedor principal falla por algo temporal, la llamada pasa al
respaldo sin esperar. Se expone como servicio HTTP (`POST /assistant`, ver [Servicio del asistente](#servicio-del-asistente)).

**Modelo de lenguaje.** Principal: Gemini 3.5 Flash-Lite. Respaldo: gpt-oss-120b en Groq, con
razonamiento bajo. Criterios, comparación y descartados en
[`eval/LLM_DECISION.md`](eval/LLM_DECISION.md).

## Estructura

```
ai/
├── catalog.py                  # load_repos(source) y load_categories(): único punto de acceso a los datos
├── embeddings.py               # Modelo de embeddings (EmbeddingGemma por defecto) y umbral
├── search.py                   # SearchIndex: texto a embeber, filtros y ranking
├── llm.py                      # generar(): registro de proveedores de LLM, salida estructurada y errores
├── assistant.py                # entender(), generar_mapa() y asistir(): el flujo del asistente
├── requirements.txt
├── scripts/
│   ├── build_sample_data.py        # Regenera ai/data/ desde la API de GitHub
│   ├── check_llm.py                # Prueba de humo de los proveedores de LLM
│   ├── export_catalog_snapshot.py  # Regenera ai/data/catalog/ desde la base (solo lectura)
│   └── load_seed_example.py        # Carga o borra los datos de ejemplo en las tablas ai.*
├── data/
│   ├── repos.json              # 20 repos de ejemplo con la forma del contrato, sin el README
│   ├── readmes/                # README de cada repo (<owner>__<name>.md)
│   ├── catalog/                # Snapshot del catálogo real: repos.json, readmes/, meta.json
│   └── seed/                   # Datos de ejemplo para las tablas de la IA (8 repos)
├── eval/
│   ├── README.md               # Evaluación de la búsqueda: cómo correrla y leerla
│   ├── SEARCH_DECISION.md      # Modelo de embeddings y umbral: decisión y evidencia
│   ├── ASSISTANT_CASES.md      # Información de casos de prueba del asistente
│   ├── LLM_DECISION.md         # Elección del modelo de lenguaje: criterios, resultados y descartados
│   ├── assistant_cases.json    # Casos de prueba del asistente
│   ├── assistant_cases.py      # Carga y valida los casos
│   ├── search_queries_catalog.json  # Golden set contra el catálogo real
│   ├── search_queries.json     # Golden set contra los datos de ejemplo
│   ├── golden.py               # Carga y valida los golden sets
│   ├── metrics.py              # hit@k, MRR, recall y umbral
│   ├── run_search_eval.py      # python -m ai.eval.run_search_eval
│   ├── understand_metrics.py   # Métricas del paso de entender
│   ├── run_understand_eval.py  # Compara modelos en el paso de entender (18 casos)
│   ├── flow_metrics.py         # Métricas del flujo completo
│   ├── run_assistant_eval.py   # Compara modelos con el flujo completo (casos rápidos)
│   ├── diagnose_latency.py     # Dónde se va el tiempo del paso de generar
│   └── results/                # Un reporte por evaluación y modelo
└── tests/
    ├── test_catalog.py           # Cómo se elige el origen de los datos
    ├── test_catalog_snapshot.py  # Valida el snapshot y las funciones del script (sin base)
    ├── test_assistant_cases.py   # Valida los casos del asistente (sin base ni modelo)
    ├── test_sample_data.py       # Valida los datos de ejemplo contra el contrato
    ├── test_search.py            # Búsqueda: filtros y orden (sin modelo) y pruebas con el modelo real
    ├── test_search_queries.py    # Valida los golden sets
    ├── test_seed_example.py      # Valida los datos de ejemplo y cómo se convierten en filas (sin base)
    ├── test_eval_metrics.py      # Métricas de la evaluación (sin modelo)
    ├── test_llm.py               # generar(): opciones por proveedor y errores (proveedor simulado)
    ├── test_assistant.py         # Entender: esquema, reglas y reintento (modelo simulado)
    ├── test_generate.py          # Generar: mensaje, esquema, reglas y respuesta del contrato
    ├── test_asistir.py           # Flujo completo con búsqueda y modelo simulados
    ├── test_understand_metrics.py  # Métricas de entender
    └── test_flow_metrics.py      # Métricas del flujo completo
```

## Puesta en marcha

Desde la raíz del repo, con Python 3.12 y [uv](https://docs.astral.sh/uv/):

```bash
uv venv --python 3.12
source .venv/Scripts/activate      # Git Bash en Windows
# source .venv/bin/activate        # Linux / macOS
uv pip install -r ai/requirements.txt
```

### Modelo de embeddings

El modelo por defecto es `google/embeddinggemma-300m`. Por qué este modelo:
[`eval/SEARCH_DECISION.md`](eval/SEARCH_DECISION.md).

**Requisito, una vez por máquina:** el modelo pide aceptar su licencia en
Hugging Face.

1. Crear una cuenta en [huggingface.co](https://huggingface.co) y aceptar la
   licencia en la [página del modelo](https://huggingface.co/google/embeddinggemma-300m).
2. Crear un token de tipo **Read** (Settings → Access Tokens).
3. `hf auth login` → "Paste an access token". El token queda en la carpeta
   del usuario (`~/.cache/huggingface/`); **nunca va al repo ni a `.env`**.

Después:

- La primera vez se descargan ~1,2 GB a la caché de Hugging Face; luego se
  leen de ahí. Para trabajar sin internet: `export HF_HUB_OFFLINE=1`.
- Corre en CPU, con ~1,2 GB de RAM aproximadamente. Construir el índice del
  catálogo (100 repos) tarda ~9 s; cada consulta, menos de 0,1 s.
- Otro modelo del registro: `AI_EMBEDDING_MODEL=qwen3` (Qwen3-Embedding-0.6B,
  sin licencia que aceptar, ~2,4 GB de RAM, sin umbral calibrado).
- En Windows puede aparecer una advertencia de Hugging Face sobre *symlinks*:
  es inofensiva.

### Modelo de lenguaje

Se elige con `AI_LLM_PROVIDER` en `.env` (por defecto, `gemini`). Cada proveedor necesita su
clave en `.env` (nombres en `.env.example`); **las claves nunca van al repo, al chat ni a las notas**.

| Proveedor (`AI_LLM_PROVIDER`) | Clave | Dónde se obtiene | Costo |
|---|---|---|---|
| `gemini` (principal) | `GEMINI_API_KEY` | Google AI Studio → Get API key | Nivel gratuito: 500 consultas/día, 15/min |
| `groq-low` (respaldo) | `GROQ_API_KEY` | console.groq.com → API Keys | Nivel gratuito, por organización: 30 consultas/min, 1.000/día, 8.000 tokens/min y **200.000 tokens/día** |
| `claude-haiku` | `ANTHROPIC_API_KEY` | console.anthropic.com → API Keys | De pago |
| `ollama` | — | Ollama instalado y abierto en la máquina | Local |

**Respaldo y presupuesto.** Si no se pide un proveedor concreto, `generar()` usa el principal
y, si falla por algo temporal (límite de uso, caída, tiempo agotado), repite la llamada con los
respaldos de `AI_LLM_FALLBACK`, en orden y **sin esperar** (por defecto `groq-low,claude-haiku`;
un respaldo sin clave se omite; vacío = sin respaldo). Si la falla fue lenta (tiempo agotado o
sin conexión), ese proveedor queda **desconectado 60 s** (disyuntor): mientras tanto, las
llamadas van directo al siguiente, así que solo el primer pedido después de una caída paga la
espera. Un límite de uso (429) o un error del servidor (5xx) no desconectan: responden al
instante y probarlos otra vez casi no cuesta. `asistir()` le da a todo el pedido 15 s
(`BUDGET_SECONDS`): cada llamada usa solo el tiempo que queda, el que tiene un respaldo detrás
tiene un tope de 7 s, y si no alcanza para otra llamada se corta con `LLMTimeout`.
`error_response()` traduce cada error al código HTTP y al cuerpo del contrato (502, 503, 504).

- Un flujo usa unos 5.000 tokens: el límite diario de Groq alcanza para unos 40 pedidos y se
  comparte con las evaluaciones. **No correr evaluaciones con Groq el día de una demo.**
- Con el nivel gratuito, Google usa el contenido de las consultas para mejorar sus servicios.
- En Groq conviene activar "Inference APIs ZDR" en la configuración de la cuenta para que no
  guarde las consultas.
- Agregar un proveedor = una entrada en `PROVIDERS` (`ai/llm.py`).
- El registro conserva proveedores descartados para repetir la comparación; la causa de cada
  descarte está en [`eval/LLM_DECISION.md`](eval/LLM_DECISION.md).

```python
from ai import embeddings
from ai.assistant import asistir, error_response
from ai.llm import LLMError
from ai.search import SearchIndex

index = SearchIndex.build()
try:
    assisted = asistir("Necesito cobrar suscripciones mensuales a mis clientes.",
                       index.search, min_score=embeddings.model_spec().min_score)
    print(assisted.response or error_response(None))   # None = sin respuesta válida → 502
except LLMError as err:
    print(error_response(err))                          # (503 o 504, ErrorResponse)
```

### Servicio del asistente

Capa HTTP delgada sobre el núcleo, en `ai/service/`: el servicio importa del núcleo y el núcleo
nunca del servicio (lo comprueba un test). Se levanta desde la raíz del repo:

```bash
python -m uvicorn ai.service.app:create_app --factory --port 8001
```

Al arrancar carga el modelo de embeddings y el índice del catálogo (unos segundos) y muestra la
cadena de proveedores (`listo: 100 repos, proveedores gemini → groq-low → claude-haiku`). No
acepta pedidos hasta terminar.

| Ruta | Qué hace |
|---|---|
| `POST /assistant` | Cuerpo `AssistantRequest` (`{"query": "…"}`, 20–2000 caracteres) → `AssistantResponse`, o `ErrorResponse` con 422 `invalid_query`, 502 `invalid_response`, 503 `provider_unavailable` o 504 `timeout` |
| `GET /health` | Repos cargados, modelo de embeddings, umbral y, por proveedor, si tiene clave y cuántos segundos le quedan desconectado (nunca muestra claves) |
| `GET /docs` | Documentación interactiva generada desde el contrato |

- **CORS:** acepta los orígenes de `AI_CORS_ORIGINS` (separados por comas; por defecto
  `http://localhost:4173,http://127.0.0.1:4173`, el frontend en local).
- **Frontend:** `NEXT_PUBLIC_ASSISTANT_API_BASE_URL=http://127.0.0.1:8001/` (este servicio).
  El backend del catálogo tiene su propio `POST /assistant`, que hoy responde siempre 503: el
  frontend debe apuntar al puerto 8001, no al del catálogo.
- Las causas de los errores (proveedor, límite, tiempo) quedan en la terminal del servicio,
  no en la respuesta.
- Probar desde Git Bash: escribir las tildes como escapes de JSON (`\u00ed` = í), porque la
  terminal de Windows puede no enviarlas en UTF-8:

```bash
curl -s -X POST http://127.0.0.1:8001/assistant -H "Content-Type: application/json" \
  -d '{"query": "Una librer\u00eda quiere que sus clientes busquen libros por tema."}'
```

## Comandos

```bash
python -m pytest -q                              # todos los tests del repo, sin el modelo
python -m pytest ai/tests -v                     # tests de la IA, sin el modelo
AI_MODEL_TESTS=1 python -m pytest ai/tests -v    # incluye las pruebas con el modelo real (~20 s)
python -m pytest tests/contracts -v              # valida los ejemplos del contrato
python -m ai.scripts.build_sample_data           # regenera ai/data/ (requiere `gh` autenticado)
python -m ai.scripts.export_catalog_snapshot     # regenera ai/data/catalog/ (requiere AI_READER_DATABASE_URL en .env)
python -m ai.scripts.load_seed_example           # carga los datos de ejemplo en ai.* (requiere AI_DATABASE_URL en .env)
python -m ai.scripts.load_seed_example --limpiar # borra los datos de ejemplo
python -m ai.eval.run_search_eval                # evalúa la búsqueda sobre el catálogo real (--golden sample: datos de ejemplo)
python -m ai.scripts.check_llm gemini groq-low   # prueba de humo de los proveedores de LLM (requiere las claves)
python -m ai.eval.run_understand_eval gemini     # compara modelos en el paso de entender (--cases validation: casos de validación)
python -m ai.eval.run_assistant_eval gemini groq-low  # compara modelos con el flujo completo (--cases validation, --shown 3)
python -m ai.eval.diagnose_latency gemini        # dónde se va el tiempo del paso de generar
```

Se usa `python -m` desde la raíz para que `ai` y `shared` se puedan importar
(`from shared.contracts.repo import Repo`). Desde otra carpeta, el import falla.

## Snapshot del catálogo real

`ai/scripts/export_catalog_snapshot.py` lee la vista `public.v_repos_for_ai` con el usuario
de solo lectura y escribe `ai/data/catalog/`:

- `repos.json`: campos de la ingesta del contrato `Repo`, sin el README, ordenados por `full_name`.
- `readmes/<owner>__<name>.md`: README de cada repo.
- `meta.json`: cuándo se tomó (UTC), de dónde, cuántos repos y qué columnas de la vista
  sobran o faltan frente al contrato.

**Requisito:** `AI_READER_DATABASE_URL` en `.env` (ver `.env.example`). Si la contraseña tiene
símbolos (`? " < > [ @ : / #`…), va codificada en la URL (*percent-encoding*). Para obtenerla sin
que quede en el historial (PowerShell):

    python -c "from getpass import getpass; from urllib.parse import quote; print(quote(getpass('Contraseña: '), safe=''))"

El script valida cada fila contra `Repo` antes de escribir: si alguna no cumple, no toca el
snapshot anterior. Regenerarlo reescribe `readmes/` completo; el diff muestra qué cambió en el catálogo.

## Datos de ejemplo en las tablas de la IA

`ai/data/seed/ejemplo_ia.json` tiene resumen, categorías e ideas de integración para 8 repos
del catálogo, para probar la API y la ficha antes de que la IA genere los datos reales. Están
escritos desde el README de cada repo y revisados de forma manual. No son salida del LLM.

Los repos se eligieron para cubrir los casos de la ficha:

| Caso | Repos |
|---|---|
| 3, 2, 1 y 0 ideas | ollama · redis, pgvector, fastapi · duckdb, vault · grafana, ripgrep |
| Idea con fragmento de código | ollama, redis, duckdb, pgvector, fastapi |
| Idea sin fragmento («Código no disponible») | vault, y una idea de ollama, redis y fastapi |
| Sin sitio web (`homepage` vacío) | pgvector, ripgrep |
| Licencia sin confirmar (`NOASSERTION`) | redis, pgvector, vault |
| Sin datos de la IA | los demás repos del catálogo |

`ai/scripts/load_seed_example.py` los valida contra los contratos y los escribe con el usuario
escritor (`AI_DATABASE_URL` en `.env`, con la contraseña codificada como en la sección anterior).
Todo va en una sola transacción: si algo falla, la base queda como estaba. Se puede correr las
veces que haga falta: borra los datos de ejemplo y los vuelve a insertar.

**Antes de generar los datos reales de la IA, hay que borrarlos:**

    python -m ai.scripts.load_seed_example --limpiar

Las filas de ejemplo se reconocen por `ai_input_hash` y `based_on_hash` = `seed-ejemplo`.
La limpieza borra solo esas filas (y las categorías de esos repos), nunca datos reales. Si ya
hay datos reales para alguno de estos repos, la carga falla sin cambiar nada.

## Cómo leer los datos

```python
from ai.catalog import load_repos

repos = load_repos()                   # catálogo real (snapshot), list[Repo] con readme_text
sample = load_repos(source="sample")   # 20 repos de ejemplo
```

El código de la IA lee los repos solo con `load_repos()`. Une `repos.json` con los archivos
de `readmes/` del origen elegido; cuando la IA lea de la base de datos, se agrega un origen
en `ai/catalog.py` y el resto del código no cambia.

## Cómo buscar

```python
from ai.search import SearchIndex

index = SearchIndex.build()   # una vez: carga el catálogo y calcula los vectores

results = index.search(
    "login social con Google para los clientes de una app",
    k=3,
    licenses=["MIT", "Apache-2.0"],   # opcional
    categories=["auth"],              # opcional
    min_health=60,                    # opcional
)
for r in results:
    print(r.score, r.repo.full_name, r.license_unconfirmed, r.health_unknown)
```

- Cada búsqueda responde a **una** necesidad. Para un stack completo se busca
  una vez por necesidad.
- Se filtra antes de ordenar: se devuelven hasta `k` repos que cumplen todos
  los filtros.
- Los repos archivados no aparecen nunca.
- Licencia: sin filtro entran todos, y `license_unconfirmed` marca los
  `NOASSERTION` o sin licencia. Con filtro, solo pasan las licencias de la
  lista.
- `min_health`: los repos sin `health_score` pasan, marcados con `health_unknown`.
- `categories`: pasa un repo si alguna de sus categorías está en la lista.
- Cada repo se representa con un texto: nombre, categorías (`name` y
  `description` de `categories.json`; `llm_notes` no entra), descripción y topics sin ruido
  (`NOISE_TOPICS` en `search.py`). El README no se usa.
- Cambiar el modelo, ese texto o `categories.json` obliga a recalcular los
  vectores. Hoy ocurre solo, al construir el índice.

## Contrato `Repo`

Definido en [`shared/contracts/repo.py`](../shared/contracts/repo.py)
(v1.0, acordado con la ingesta). Usa los nombres de GitHub (`full_name`,
`stargazers_count`, `license_spdx_id`, `open_issues_count`). Las categorías
salen de [`shared/contracts/categories.json`](../shared/contracts/categories.json).

Los datos de ejemplo son más estrictos que el contrato:

- El contrato ignora campos desconocidos (lector tolerante). Los tests exigen
  que toda clave de `repos.json` sea un campo del contrato, para detectar
  errores de tipeo.
- El contrato admite repos sin categoría ni README. Los datos de ejemplo no:
  sus categorías son la referencia clasificada a mano (`assigned_by: "human"`).

Nota: Pydantic normaliza `homepage` (por ejemplo, agrega `/` al final del dominio).

## Por acordar

- Fórmula y rango de `health_score` (lo calcula la ingesta).


## Escritura y revisión de ideas (PR #72)

**Escribir en la base:**

    python -m ai.scripts.write_ideas             # revisar que sea válido
    python -m ai.scripts.write_ideas --escribir

Es una sola transacción (todo o nada) y repetible. Solo reemplaza las ideas regenerables
(`generated_by = 'llm'` y `reviewed_at` nulo) de los repos del archivo. Las revisadas o
escritas por una persona nunca se tocan y ocupan cupo: como máximo 3 ideas por repo y una por
tipo, contando las revisadas. Si el README de una idea revisada cambió desde que se revisó,
el informe la muestra para revisarla de nuevo, sin tocarla.

**Aprobar ideas revisadas:** una persona lee la idea en la ficha o en `ideas.json` y, si está
bien sin cambios, la aprueba:

    python -m ai.scripts.review_ideas --aprobar llm-<github_id>-<n> …             # comprueba
    python -m ai.scripts.review_ideas --aprobar llm-<github_id>-<n> … --escribir  # marca

Pone `reviewed_at`; desde ahí la regeneración no la toca. La tabla no guarda quién la revisó.
Verificación después de escribir: `ai/sql/consultas/ideas_ia.sql` y `huerfanos_ia.sql`.

**Qué lee la API del catálogo:** todas las columnas de `ai.ai_integration_ideas` (las del
contrato `IntegrationIdea` más `github_id` para unir; `full_name` lo pone la API), ordenadas
por `id`, como máximo 3 por repo, y nada de los repos archivados. El rol de lectura de la API
necesita `USAGE` en el esquema `ai` y `SELECT` sobre `ai.ai_repo_enrichment`,
`ai.ai_repo_categories` y `ai.ai_integration_ideas` (no sobre `ai.ai_embeddings`, que es
interna de la IA).
