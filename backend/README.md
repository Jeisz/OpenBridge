# Backend OpenBridge

API FastAPI del catálogo sobre Supabase, en la raíz (sin prefijo `/api`, acuerdo
del 29-oct-2026). Las formas de respuesta son las que ya consume
`frontend/src/data/catalogHttp.mjs`; el frontend conserva esas formas de respuesta:

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

```bash
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -e './backend[dev]'
cp backend/.env.example backend/.env
backend/.venv/bin/python -m uvicorn backend.app.main:app --reload --env-file backend/.env --port 8000
```

Documentación interactiva: http://127.0.0.1:8000/docs

```bash
backend/.venv/bin/python -m pytest backend/tests
```

En Windows, si la instalación de dependencias falla por permisos o falta de red,
sirve cualquier entorno que ya tenga `fastapi`, `sqlalchemy`, `psycopg`,
`pydantic`, `httpx` y `pytest`, por ejemplo:

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

Pruebas: `51 passed` en `backend/tests` (sin base de datos, con repositorio
falso) y una pasada manual contra Supabase que cubre 200/404/422/503, cabeceras
de paginación, escape de comodines, filtros, ficha con ideas, CORS y asistente.
El rol de solo lectura sigue bloqueado; ver
[`docs/acceso-base-datos.md`](docs/acceso-base-datos.md).

## Docker

Desde la raíz:

```bash
docker build -f backend/Dockerfile -t openbridge-backend .
docker run --rm -p 8000:8000 --env-file backend/.env openbridge-backend
```

Esta imagen inicia únicamente la API; no incluye base de datos ni ejecución de IA.


## Integración local en front-back-test (02-nov-2026)

Backend incorporado desde `5b7e932` y Repo v1.2 desde main `e64fc47`.
El frontend solicita todas las páginas secuencialmente y solo publica el catálogo
cuando la carga completa termina. Búsqueda, filtros y categorías visibles siguen
siendo locales sobre el catálogo completo. Si falla una página o cambia el total,
la carga falla y permite reintentar, sin mostrar resultados parciales.
Esta estrategia conserva la interfaz actual; para catálogos mayores se debe
acordar paginación UI, búsqueda del servidor y facetas globales.

La ficha admite `#herramienta/owner/name` sin depender del listado, conservando
los IDs anteriores. El adapter lee disabled e is_maintained sin convertir NULL
en false. Los mensajes remotos no se muestran al usuario.

Pendiente confirmar: Repo v1.2 describe is_maintained mediante 180 días, pero
esta API todavía entrega NULL. No se inventa una fórmula en frontend.
No hay DATABASE_URL configurada en este checkout; no se verificó Supabase real.
Los tests con repositorios falsos no certifican los permisos del lector.
El asistente continúa independiente y el stub local responde 503.
