# Acceso de la API a la base de datos

Documento de estado y de decisión pendiente. **Este repositorio no ejecuta DDL,
no crea roles y no cambia contraseñas.** Todo lo que sigue debe aprobarlo y
ejecutarlo el equipo de datos (dueño de la base Supabase).

## 1. Qué necesita leer la API

| Objeto | Columnas usadas | Para qué |
| --- | --- | --- |
| `public.catalog_repositories` | `github_id`, `full_name`, `name`, `description`, `homepage`, `language`, `license_spdx_id`, `stargazers_count`, `forks_count`, `pushed_at`, `archived`, `disabled`, `open_issues_count`, `html_url` | Listado y ficha |
| `public.v_repos_for_ai` | `github_id`, `full_name`, `topics`, `readme_text` | Ficha (temas y README) |
| `ai.ai_repo_enrichment` | `github_id`, `summary_es`, `use_cases` | Listado y ficha |
| `ai.ai_repo_categories` | `github_id`, `category_id`, `assigned_by`, `rank` | Tarjetas, filtro `category` y ficha |
| `ai.ai_integration_ideas` | Todas las columnas del contrato `IntegrationIdea` | Ficha |

El listado lee la tabla base porque `v_repos_for_ai` **no** expone `disabled`,
`open_issues_count` ni `html_url`.

## 2. Estado real verificado el 31-oct-2026

Consultado con una credencial administrativa, en modo lectura, sin cambios:

```
roles: openbridge_ai_reader (LOGIN), openbridge_ai_writer, openbridge_data_sync
grants de openbridge_ai_reader: [('public', 'v_repos_for_ai', 'SELECT')]
has_schema_privilege('openbridge_ai_reader', 'ai', 'USAGE') = false
has_schema_privilege('openbridge_ai_reader', 'public', 'USAGE') = true
```

Dos problemas concretos:

1. **Permisos insuficientes.** El rol solo puede leer `public.v_repos_for_ai`.
   No tiene `SELECT` sobre `public.catalog_repositories` ni sobre las tablas
   `ai.*`, y no tiene `USAGE` sobre el esquema `ai`. Con esos permisos la API
   **no puede** servir `summary_es`, `categories`, `use_cases`,
   `integration_ideas`, `disabled`, `open_issues_count` ni `html_url`.
2. **La contraseña no autentica.** Se probó el login por el pooler
   (`aws-0-us-east-1.pooler.supabase.com`) con el usuario
   `openbridge_ai_reader.<project_ref>` y la contraseña de
   `data-engineering/.env.ai-reader` en los puertos 5432 y 6543:
   `FATAL: password authentication failed for user "openbridge_ai_reader"`.
   Con el usuario corto (sin `<project_ref>`) el pooler responde
   `no tenant identifier provided`. Es decir: el rol existe, pero el secreto
   disponible no es el vigente (rol recreado o contraseña rotada).

Mientras no se resuelva ninguno de los dos, `GET /repos` y
`GET /repos/{owner}/{name}` responden `503 catalog_unavailable` y **nunca**
datos inventados. El caso de permisos deja además un log de nivel `ERROR` con
el `sqlstate 42501`.

## 3. Opciones para el equipo de datos

### Opción A (recomendada): ampliar la vista y publicar una vista de IA

Mantiene la superficie del lector en vistas, como ya exige
`data-engineering/scripts/create_ai_reader.py` (`acceso_directo_catalogo` debe
ser `false`). Requiere que el equipo de datos publique:

```sql
-- Propuesta, NO ejecutada por el equipo de API.
-- 1) Añadir a v_repos_for_ai lo que la ficha necesita y la tabla base ya tiene:
--    disabled, open_issues_count, html_url
-- 2) Publicar una vista de resultados de IA, por ejemplo public.v_repo_ai_profile
--    con: github_id, summary_es, use_cases, categories (json), ideas (json)
GRANT SELECT ON public.v_repos_for_ai  TO openbridge_ai_reader;
GRANT SELECT ON public.v_repo_ai_profile TO openbridge_ai_reader;
```

Ventajas: sigue habiendo un único punto de lectura, sin acceso directo a
tablas, y el contrato de la API no cambia. Coste: trabajo de datos.

### Opción B: conceder `SELECT` de solo lectura a las tablas implicadas

```sql
-- Propuesta, NO ejecutada por el equipo de API.
GRANT USAGE ON SCHEMA ai TO openbridge_ai_reader;
GRANT SELECT ON public.catalog_repositories TO openbridge_ai_reader;
GRANT SELECT ON ai.ai_repo_enrichment,
                ai.ai_repo_categories,
                ai.ai_integration_ideas
    TO openbridge_ai_reader;
```

Ventajas: no requiere vistas nuevas. Coste: el lector pasa a ver tablas
directamente, contra la restricción que hoy valida el script del rol.

### Opción C: recortar el contrato

Servir solo lo que hay en `v_repos_for_ai` (sin `summary_es`, categorías,
ideas, `disabled`, `open_issues_count`, `html_url`). No se recomienda: rompe la
ficha de Frontend y contradice los acuerdos del 29-oct-2026.

## 4. Brechas de datos observadas (31-oct-2026)

`public.catalog_repositories`: 100 filas · `v_repos_for_ai`: 100 filas, 100
`github_id` distintos, 0 README vacíos.

| Dato | Estado real | Efecto en la API |
| --- | --- | --- |
| `ai.ai_repo_enrichment` | 8 filas (resumen máximo: 238 caracteres) | 92 repos con `summary_es: null` y `use_cases: []` |
| `ai.ai_repo_categories` | 12 filas, 10 ids distintos, todos presentes en `shared/contracts/categories.json` | 90 repos con `categories: []`; el filtro `category` solo devuelve esos |
| `ai.ai_integration_ideas` | 11 filas | `integration_ideas: []` en el resto de fichas |
| `html_url` | NULL en 95/100 | La ficha devuelve `html_url: null` salvo en 5 filas |
| `open_issues_count` | NULL en 95/100 | `open_issues_count: null` |
| `disabled` | NULL en 95/100; ninguna fila en `true` | `disabled: null`; `maintenance=inactive` depende de `archived` |
| `archived` | ninguna NULL y ninguna en `true` | `maintenance=active` devuelve las 100 filas |
| `description` / `homepage` | 1 y 3 filas en NULL | Se devuelven `null` (el contrato lo permite) |

La API no rellena esos huecos: `null` significa "sin dato". Si el producto
necesita `html_url`, `open_issues_count` o `disabled` en las 100 filas, la
ingesta debe poblarlos; si necesita `summary_es`/categorías/ideas en todo el
catálogo, la IA debe ejecutarse. Ninguna de las dos cosas es parte de esta tarea.

## 5. Cuando se resuelva: cómo se configura

```ini
DATABASE_URL=postgresql+psycopg://openbridge_ai_reader.<project_ref>:<password>@aws-0-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require
```

- Usar el usuario largo del pooler (`rol.<project_ref>`), no el corto.
- La API abre conexiones en `AUTOCOMMIT` y solo ejecuta `SELECT`; no hay
  migraciones ni escrituras en este repositorio.
- Nunca se configuran credenciales administrativas (`postgres`) en la API ni en
  el `.env` versionado.

## 6. Comprobaciones útiles (solo lectura)

```sql
-- Permisos actuales del rol
SELECT table_schema, table_name, privilege_type
FROM information_schema.role_table_grants
WHERE grantee = 'openbridge_ai_reader'
ORDER BY 1, 2, 3;

SELECT nspname, has_schema_privilege('openbridge_ai_reader', nspname, 'USAGE')
FROM pg_namespace WHERE nspname IN ('public', 'ai');
```

Cuando el login funcione, `GET /repos?page_size=1` debe devolver 200 y
`GET /repos/angular/angular` debe traer `readme_text` no nulo.
