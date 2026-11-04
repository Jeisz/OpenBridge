# Backend OpenBridge

API FastAPI del catálogo sobre Supabase, en la raíz (sin prefijo `/api`, acuerdo
del 29-oct-2026). Las formas de respuesta son las que ya consume
`frontend/src/data/catalogHttp.mjs`; el frontend no necesita cambios:

- `GET /health` — liveness del proceso (no comprueba base de datos ni IA).
- `GET /repos` — **array** de repositorios con búsqueda y filtros. La paginación
  viaja en las cabeceras `X-Total-Count`, `X-Total-Pages`, `X-Page` y
  `X-Page-Size`, así que el cuerpo sigue siendo el array del contrato.
- `GET /repos/{owner}/{name}` — `{"repo": {...}, "integration_ideas": [...]}`,
  que es `shared.contracts.repo_detail.RepoDetail`.
- `POST /assistant` — servicio independiente. Valida `AssistantRequest` (v1.1) y
  hoy responde 503 `provider_unavailable`: no hay proveedor conectado y no se
  simula una respuesta.

`/categories`, `/integrations` y `/repos/{owner}/{name}/integration-ideas` no se
exponen (404).

## Ejecutar desde la raíz del repositorio

Requiere Python 3.11 o superior. El directorio de trabajo siempre es la raíz del
repositorio: `backend` y `shared` se importan como paquetes desde ahí.

POSIX:

```bash
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -e './backend[dev]'
cp backend/.env.example backend/.env
backend/.venv/bin/python -m uvicorn backend.app.main:app --reload --env-file backend/.env --port 8000
backend/.venv/bin/python -m pytest backend/tests
```

Windows (PowerShell):

```powershell
python -m venv backend\.venv
backend\.venv\Scripts\python.exe -m pip install -e "backend[dev]"
Copy-Item backend\.env.example backend\.env
backend\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --env-file backend/.env --port 8000
backend\.venv\Scripts\python.exe -m pytest backend/tests -q
```

`--env-file` lo aporta `uvicorn[standard]`, que incluye `python-dotenv`.
Documentación interactiva: http://127.0.0.1:8000/docs

Sin `DATABASE_URL` la API arranca igual y `/repos` responde 503
`catalog_unavailable`: sirve para revisar `/docs` y los errores, nunca para
servir datos falsos. Un repositorio de prueba vacío no necesita base de datos.

Si la instalación de dependencias falla por permisos o falta de red, sirve
cualquier entorno que ya tenga `fastapi`, `sqlalchemy`, `psycopg`, `pydantic`,
`httpx` y `pytest`:

```powershell
cd C:\ruta\al\worktree
C:\Users\...\.venv\Scripts\python.exe -m pytest backend/tests -q
```

## Variables de entorno

| Variable | Uso | Por defecto |
| --- | --- | --- |
| `DATABASE_URL` | DSN del rol de **solo lectura** (`postgresql+psycopg://...`). Sin ella, `/repos` responde 503. | vacío |
| `CORS_ORIGINS` | Orígenes permitidos, separados por comas. | vacío |
| `CATALOG_PAGE_SIZE` | Tamaño de página por defecto. | `20` |
| `CATALOG_MAX_PAGE_SIZE` | Tamaño máximo aceptado por petición. | `100` |
| `DB_CONNECT_TIMEOUT` | Timeout de conexión (segundos). | `5` |
| `DB_STATEMENT_TIMEOUT_MS` | Timeout de sentencia (ms). | `8000` |

Nunca se usan credenciales de administrador en la API. El estado del acceso de
lectura y los permisos que faltan están en
[`docs/acceso-base-datos.md`](docs/acceso-base-datos.md).

## Contrato y decisiones

- Las respuestas se construyen con `shared.contracts.repo.Repo`,
  `shared.contracts.repo_detail.RepoDetail` e
  `shared.contracts.integration_idea.IntegrationIdea`; no se copian modelos.
  `backend.app.api.schemas.CatalogRepo` es un superconjunto de `Repo` que añade
  `html_url`, `forks_count`, `disabled` y `is_maintained` para la ficha.
- `GET /repos` no consulta `readme_text` ni `topics`: esas claves sólo viajan en
  la ficha. Emitirlas vacías en el listado sugeriría que el repositorio no tiene
  README ni temas.
- `summary_es` se recorta a los 250 caracteres del contrato y se registra un
  aviso para IA. Es el único campo que se ajusta; la alternativa era romper la
  respuesta entera por una fila.
- `categories`, `use_cases` e `integration_ideas` salen vacíos (`[]`/`null`)
  cuando la IA todavía no ha procesado el repositorio.
- `integration_ideas`: máximo tres, todas del mismo repositorio y ninguna si el
  repositorio está archivado (reglas de `repo_detail`). Las ideas inválidas se
  omiten y se registran.
- `archived` es obligatorio en el contrato: si la base lo trae NULL, la API
  responde 503 `catalog_unavailable` en vez de inventar `false`.
- `is_maintained` y `health_score` viajan siempre en `null`: no hay campo,
  criterio ni fórmula acordados. No se inventan valores.
- `maintenance=active|inactive` es la aproximación local acordada con Frontend
  (`active` = ni archivado ni deshabilitado).
- Orden del listado: `full_name ASC`, elegido para que la paginación sea
  estable; no es una regla de negocio.
- Búsqueda `q`: `ILIKE` literal sobre `full_name`, nombre, descripción y
  `summary_es` (los comodines del usuario se escapan).
- Errores con cuerpo estable: `{"error": {"code": ..., "message": ...}}`
  (`repo_not_found` 404, `invalid_request` 422, `catalog_unavailable` 503).
  El asistente usa los códigos de su contrato: `invalid_query` 422 y
  `provider_unavailable` 503.

## Compatibilidad con el frontend

`frontend/src/data/catalogHttp.mjs` valida cada respuesta en tiempo de ejecución
y lanza `Respuesta del catálogo inválida` o `Ficha inválida`. La API no toca
`frontend/`; `backend/tests/test_frontend_contract.py` replica esas reglas para
que una rotura de forma falle aquí antes que en la interfaz:

| Regla del frontend | Cómo la cumple la API |
| --- | --- |
| `github_id` entero, `full_name` texto | contrato `Repo` v1.2 |
| `stargazers_count` número finito | `int` obligatorio; nunca `null` |
| `archived` booleano | `NULL` en la base ⇒ 503, no `false` |
| `pushed_at` aceptado por `Date.parse` | ISO 8601; `NULL` ⇒ 503 |
| `categories` array | `[]` cuando la IA no ha clasificado |
| `summary_es` nulo o de 250 caracteres como mucho | se recorta a 250 y se registra el aviso |
| listado = array; ficha = `{repo, integration_ideas}` | formas del acuerdo 29-oct-2026 |
| ideas ≤ 3, del mismo repositorio y ninguna si está archivado | reglas de `repo_detail` |
| `integration_type` ∈ {rest_api, docker, sdk, webhook}, `difficulty` ∈ {low, medium, high}, `docs_url` `http(s)` | enums y `HttpUrl` de `IntegrationIdea` v1.1 |

Además el frontend exige `payload.repo.full_name === name`: el nombre de la ruta
tiene que coincidir **exactamente** con el `full_name` que devolvió el listado.
La búsqueda en SQL ignora mayúsculas, pero la ficha se construye con el
`full_name` de la fila, así que una variante de mayúsculas devuelve la forma
canónica y el validador del frontend rechaza esa ficha. Es una regla del
frontend, no un error de la API: el frontend siempre pide el nombre que recibió.

El listado no incluye `readme_text` ni `topics`, y ningún `null` se sustituye por
`0`, `false` o cadena vacía.

Forma publicada, comprobada con `TestClient` sobre esta rama:

```text
GET /repos                      → 200, array de 19 claves + cabeceras X-Total-Count/X-Total-Pages/X-Page/X-Page-Size
  archived, categories, description, disabled, forks_count, full_name, github_id,
  health_score, homepage, html_url, is_maintained, language, license_spdx_id,
  name, open_issues_count, pushed_at, stargazers_count, summary_es, use_cases

GET /repos/{owner}/{name}       → 200, {repo, integration_ideas}
  repo  = las 19 del listado + readme_text + topics   (21 claves)
  idea  = based_on_hash, compatible_stack, dependencies, difficulty, docs_url,
          full_name, generated_by, id, integration_type, reviewed_at, snippet,
          snippet_language, summary, title, triggers   (15 claves)
```

El listado es un subconjunto exacto de `repo` en la ficha: ningún campo cambia de
nombre ni de tipo entre las dos respuestas.

## Divergencias y propuestas de contrato

Nada de esto se cambió en `shared/`: se documenta para que lo resuelvan Jeison y
el equipo de contratos.

1. **`shared/contracts/repo.py` v1.2 no está en el commit de esta rama.** El
   commit tiene v1.0; el árbol **y el índice** lo tienen byte a byte igual a
   `main` (blob `66b92f8`, preparado con `git add`, sin commit). Con v1.0 fallan
   cuatro pruebas de conformidad (`74 passed, 4 failed`); con v1.2 pasan las 78.
   Basta fusionar `main` en la rama para que ese diff desaparezca.
2. **`shared/contracts/repo_detail.py` sólo existe en la rama `backend`.**
   `main` publica cinco archivos en `shared/contracts/` y no incluye este, así
   que la ficha (`{repo, integration_ideas}`) depende de un contrato **sin
   ratificar**. Hay que llevarlo a `main` con un PR de contratos avisando a
   Frontend e IA, o la rama no se podrá integrar tal cual. Sólo compone
   contratos existentes: `repo: Repo` y una lista de como mucho tres
   `IntegrationIdea`. Texto exacto propuesto y cambios de soporte en
   [`docs/propuestas-contrato.md`](docs/propuestas-contrato.md).
3. **Columnas extra sobre `Repo`: `name`, `html_url`, `forks_count`.** Salen de
   `public.catalog_repositories` y viajan en el listado y en la ficha. Ningún
   consumidor las lee: `git grep` no las encuentra en `frontend/`, `pm/`, `ai/`
   ni `ingestion/`, el frontend deriva el nombre de `full_name`
   (`repo.full_name.split('/').at(-1)`) y arma la URL de GitHub con
   `` `https://github.com/${tool.repo}` ``. Quitarlas cambiaría la forma de la
   respuesta (19 → 16 claves en el listado), así que la decisión entre añadirlas
   al contrato o eliminarlas es la propuesta B de
   [`docs/propuestas-contrato.md`](docs/propuestas-contrato.md).
4. **Más de tres categorías en la base ⇒ 503.** `Repo.categories` admite tres
   (`max_length=3`) y el servicio no recorta, a diferencia de `summary_es` y de
   las ideas: una cuarta asignación tumba la página entera. Recortar en el borde
   necesita una decisión explícita (ver
   `test_categories_over_the_contract_limit_break_the_response`).
5. **Un `404` de ruta desconocida no usa el cuerpo de error de la API.**
   Responde `{"detail": "Not Found"}` del framework. Los códigos
   `repo_not_found`, `invalid_request` y `catalog_unavailable` son sólo para los
   `404`, `422` y `503` documentados en `/docs`.

## Responsabilidades

- `app/api`: HTTP, validación de entrada, dependencias y manejadores de error.
- `app/services`: reglas del catálogo y traducción de filas a modelos.
- `app/repositories`: SQL de solo lectura (SQLAlchemy Core + `text()`).
- `app/db`: motor y conexión (`AUTOCOMMIT`, sin sesiones de escritura).
- `app/core`: configuración de entorno y errores de dominio.
- `app/clients`: comunicación con IA cuando se acuerde su interfaz (sin uso hoy).

Importar los modelos desde `shared.contracts`, sin copiarlos aquí. Ejecutar
siempre desde la raíz para que estén disponibles `backend` y `shared`.

## Estado de los datos y validación (31-oct-2026)

Medido con `SET TRANSACTION READ ONLY` contra la base de Supabase:

| Dato | Valor |
| --- | --- |
| Repositorios en `catalog_repositories` | 100 |
| Resúmenes en `ai.ai_repo_enrichment` | 8 (máximo 238 caracteres) |
| Asignaciones en `ai.ai_repo_categories` | 12 filas, 10 ids distintos |
| Ideas en `ai.ai_integration_ideas` | 11 |
| `archived = true` / `disabled = true` | 0 / 0 |
| `html_url`, `open_issues_count`, `disabled` NULL | 95 de 100 |
| `homepage` NULL | 3 |
| `description` NULL | 1 |

Los 10 ids de categoría que hay en la base existen en
`shared/contracts/categories.json` (18 categorías): no hay drift. Las 100 filas
cumplen `Repo` en cuanto los NULL de `categories`/`use_cases` se normalizan a
`[]`.

Pruebas: `78 passed` en `backend/tests`, sin base de datos y sin red (repositorio
falso); ver [Pruebas](#pruebas). Encima de eso hay una pasada manual contra
Supabase que cubre 200/404/422/503, cabeceras de paginación, escape de
comodines, filtros, ficha con ideas, CORS y asistente. El rol de solo lectura
sigue bloqueado; ver [`docs/acceso-base-datos.md`](docs/acceso-base-datos.md).

## Pruebas

```bash
python -m pytest backend/tests -q     # 78 pruebas, sin base de datos ni red
python -m pytest backend/tests -v     # nombre y caso de cada prueba
```

| Módulo | Qué fija |
| --- | --- |
| `test_app.py` | arranque, CORS con cabeceras de paginación expuestas, rutas sin `/api`, asistente independiente |
| `test_repos_list.py` | array del contrato, paginación (defecto, máximo, página inexistente), filtros y errores |
| `test_repo_detail.py` | ficha `{repo, integration_ideas}`, ideas inválidas, archivado, 404 y búsqueda sin distinguir mayúsculas |
| `test_catalog.py` | reglas del servicio: repositorio sin enriquecimiento y tope de 250 caracteres |
| `test_repository_sql.py` | SQL generado: fuentes, filtros como binds, escape de comodines, sin `is_maintained` ni `health_score` |
| `test_contract_compat.py` | alineación con `shared.contracts` y superficie HTTP publicada |
| `test_contract_conformance.py` | forma publicada frente a los contratos; `archived`/`pushed_at` NULL ⇒ 503; `homepage` fuera de contrato ⇒ 503 |
| `test_frontend_contract.py` | reglas del validador de `frontend/src/data/catalogHttp.mjs` |

Las pruebas no escriben en Supabase, no abren conexiones y no simulan respuestas
de IA: el repositorio falso de `tests/conftest.py` devuelve filas fijas.

## Docker

Desde la raíz:

```bash
docker build -f backend/Dockerfile -t openbridge-backend .
docker run --rm -p 8000:8000 --env-file backend/.env openbridge-backend
```

Esta imagen inicia únicamente la API; no incluye base de datos ni ejecución de IA.

