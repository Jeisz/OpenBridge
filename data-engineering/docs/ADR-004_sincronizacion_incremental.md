# ADR-004 — Sincronización incremental diaria del catálogo

**Estado: PREPARADA TÉCNICAMENTE. Sin escrituras habilitadas.**

## Contexto

- `ADR-002` habilitó una carga inicial **insert-only** (`load.insert_new_batch`).
  Los repositorios que ya existen en el catálogo nunca se actualizan, por lo que
  estrellas, forks, `pushed_at`, topics y README quedan congelados.
- El contrato `openbridge-ai-v1` (`src/hash_contract.py`) calcula un SHA-256
  determinista sobre 12 campos del repositorio más el README (o `null` si el
  README no existe), e incluye `content_hash_version`.
- Cinco filas históricas tienen hashes de origen desconocido y **no** tienen
  versión de hash; el catálogo de producción se llama `postgres` y el pipeline
  histórico (`config.py`, `database.py`) apunta al usuario administrativo.

## Decisión

1. **Coordinador único**: `scripts/update_catalog.py` ejecuta las fases
   configuración → lista aprobada → extracción → transformación → validación →
   hashes → lectura del destino → plan → (opcional) aplicación → verificación →
   resumen. Es el único punto de entrada de la automatización.
2. **Solo lectura por defecto**: sin `--live` no hay HTTP ni SQL; `--dry-run` es
   el modo predeterminado y `--apply` es la única vía de escritura.
3. **Plan puro** en `src/sync_plan.py`, sin I/O. Produce acciones
   `INSERT` / `UPDATE` / `UNCHANGED` / `PRESERVE` por repositorio y por README,
   y `validate_plan` recalcula cada hash v1 antes de abrir una conexión.
4. **Persistencia** en `src/sync_load.py`. Complementa `load.py` (que se conserva
   insert-only para no alterar su contrato ni sus pruebas) con lectura de estado
   de solo lectura, aplicación transaccional y verificación posterior.
5. **Configuración del destino** en `src/sync_config.py`: credenciales solo por
   entorno, validación explícita de host/puerto/base/usuario y rechazo de
   cuentas administrativas (`postgres`, `postgres.*`, `supabase_admin`). No se
   modifica `config.py` ni `database.py` para no reutilizar el usuario
   administrativo ni romper el pipeline histórico.
6. **Compatibilidad de hashes**: se escriben las filas cuyo hash verificable es
   `openbridge-ai-v1` y, por autorización expresa del responsable del contrato de
   IA (2026-10-28), también las filas históricas con `content_hash_version` NULL:
   su hash se recalcula con el contrato canónico v1 y se actualiza junto con la
   versión en la misma sentencia. Las filas con una versión **distinta y
   desconocida** se preservan y se listan: este coordinador no reinterpreta
   contratos ajenos.
7. **404 confirmado ≠ fallo transitorio**: un `NO_ENCONTRADO` se representa como
   `null` en el hash v1 y no crea fila README. Un error de red, cuota, JSON o
   contenido inválido (`ERROR_HTTP`, `LIMITE_API`, `UTF8_INVALIDO`,
   `CONTENIDO_INVALIDO_O_GRANDE`, `NO_CONSULTADO`) **no produce ninguna
   escritura** y marca la ejecución como incompleta.
8. **Sin borrados**: no existe acción ni sentencia `DELETE`. Si un README
   almacenado desaparece en origen (404), se preserva y se advierte.
9. **Autorización por capas** para escribir: `--apply`, destino con
   `OPENBRIDGE_SYNC_ALLOW_WRITES=1`, confirmación exacta en
   `OPENBRIDGE_SYNC_CONFIRMATION`, base y usuario verificados con
   `current_database()`/`current_user`, transacción única y reversión ante
   cualquier discrepancia.
10. **Workflow programado** (`.github/workflows/update_catalog.yml`) a las 11:00
    UTC (06:00 America/Bogota) con `workflow_dispatch`, concurrencia, timeout y
    **solo `--dry-run`**. La aplicación manual está en un paso condicionado a una
    variable de repositorio y a un secreto de confirmación; por defecto no se
    ejecuta.
11. **Reutilización**: `extract_github.fetch_repositories`,
    `transform.transform_records`, `hash_contract.content_hash_v1`,
    `load.LoadPlanError` y el patrón transaccional de `load.py`.

## Reglas del plan

| Situación detectada | Acción repositorio | Acción README |
| --- | --- | --- |
| No existe en el catálogo y el README está resuelto | `INSERT` | `INSERT` o `NONE` (404) |
| Hash v1 igual y README igual | `UNCHANGED` | `UNCHANGED` |
| Hash v1 igual pero README distinto | `UNCHANGED` | `UPDATE` (reparación) |
| Hash v1 distinto con cambios verificables | `UPDATE` | `UPDATE` / `INSERT` / `UNCHANGED` |
| Hash v1 ausente o distinto sin cambios verificables | `PRESERVE` | `PRESERVE` (revisión manual) |
| Versión de hash NULL con extracción verificable | `UPDATE` (backfill `openbridge-ai-v1`) | `UPDATE` / `INSERT` / `UNCHANGED` |
| Versión de hash distinta y desconocida | `PRESERVE` | `PRESERVE` (contrato ajeno) |
| Conflicto de identidad (`full_name` distinto) | `PRESERVE` | `PRESERVE` |
| README no verificable (red/cuota/contenido) | `PRESERVE` | `PRESERVE` |
| 404 confirmado con README almacenado | `PRESERVE` | `PRESERVE` (sin borrado) |
| Falta un repositorio aprobado en la extracción | — | ejecución incompleta (código 3) |

## Consecuencias

- El catálogo deja de ser append-only: se actualizan metadatos y README de filas
  con hash v1, en una sola transacción y con control optimista (`content_hash`
  previo) que detecta planes obsoletos.
- Las cinco filas históricas con versión NULL pasan a `openbridge-ai-v1` en la
  primera aplicación autorizada; a partir de ahí siguen el flujo incremental
  normal. La operación es idempotente: sin cambios, el plan no genera escrituras.
- Las filas con una versión de hash distinta y desconocida siguen intactas hasta
  que exista una migración aprobada para ese contrato.
- La ejecución diaria es reproducible: repetir el plan sin cambios produce cero
  escrituras y la verificación posterior confirma hashes y README.
- `load.py` conserva su comportamiento insert-only y sus pruebas originales.

## Pendientes y riesgos

- **Cuenta de servicio**: el dueño de la base debe crear/confirmar el usuario de
  escritura y su contraseña; no se crean ni modifican roles
  (`openbridge_ai_reader`/`openbridge_ai_writer`) desde este código.
- **Secretos del workflow**: los nombres están definidos en el YAML y en el
  runbook, pero sus valores no se han configurado ni verificado.
- **Hashes históricos**: el backfill está implementado y probado, pero **no se ha
  ejecutado** contra Supabase; requiere la misma autorización de escritura que
  cualquier `--apply`.
- **Borrados**: no hay política automática; el 404 con README almacenado queda
  pendiente de aprobación.
- **Pruebas reales**: toda la cobertura es offline (motor SQL simulado). Antes de
  habilitar `--apply` hacen falta pruebas en una base de staging con el mismo
  esquema, incluidos triggers, privilegios y concurrencia.
- **Transporte**: `psycopg` + `sslmode=require`; el destino Supabase rechaza
  `disable`/`allow`.

## Enmienda 2026-10-28 — Recalculación autorizada de hashes históricos

**Estado: implementado y cubierto por pruebas offline; NO ejecutado en producción.**

Autorización del responsable del contrato de IA (Andrés):

1. `content_hash` pertenece a Ingesta y es de uso interno.
2. La IA calcula su propia huella a partir de `description`, `topics` y
   `readme_text`.
3. La IA no lee `content_hash` ni `content_hash_version`.
4. Recalcular los cinco hashes históricos no provoca reprocesamientos de IA.
5. `github_id` sigue siendo la clave estable de `v_repos_for_ai`.
6. No se renombran ni cambian los tipos de columnas existentes de la vista; se
   pueden añadir columnas compatibles.

Decisión técnica:

- El planificador emite `UPDATE` con `legacy_backfill=True` solo si
  `content_hash_version IS NULL`, la extracción del repositorio está completa y
  el README está disponible o tiene un 404 confirmado. Cualquier error
  transitorio (red, 403/429, JSON inválido, contenido no verificable) mantiene la
  fila en `PRESERVE` y no produce escrituras.
- La sentencia `UPDATE ... SET content_hash = :content_hash,
  content_hash_version = :content_hash_version ... WHERE content_hash IS NOT
  DISTINCT FROM :hash_previo AND content_hash_version IS NOT DISTINCT FROM
  :version_previa` escribe ambos campos en la misma operación. `:version_previa`
  es `NULL`, de modo que una fila versionada en paralelo por otro proceso no se
  sobrescribe (`rowcount = 0` → reversión completa).
- Si el hash recalculado coincide con el almacenado, igualmente se actualiza la
  versión. Si difiere, se reemplaza el hash histórico.
- Se escriben también los metadatos y el README que forman parte del hash, para
  que el valor calculado corresponda al contenido persistido.
- No se emite `DELETE`: un README almacenado se conserva aunque el origen
  devuelva 404.
- `legacy_backfill_ids` lista los IDs planificados y `backfilled_repositories`
  cuenta las filas actualizadas por esta vía.

Variables canónicas: `OPENBRIDGE_SYNC_ALLOW_WRITES=1` y
`OPENBRIDGE_SYNC_CONFIRMATION=<token>`. En GitHub Actions, la variable de
repositorio `OPENBRIDGE_SYNC_ALLOW_WRITES` debe valer `1` para habilitar el paso
de aplicación manual; la ejecución programada nunca escribe.

Separación de responsabilidades: el hash de Ingesta (`openbridge-ai-v1`) es un
control interno de idempotencia y no forma parte del contrato de IA. La huella de
IA se calcula en su propio dominio y no depende de estas columnas.
