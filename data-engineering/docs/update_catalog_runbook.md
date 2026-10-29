# Runbook — sincronización diaria del catálogo

Documento operativo de `scripts/update_catalog.py` y del workflow
`.github/workflows/update_catalog.yml`. Decisiones: `docs/ADR-004_sincronizacion_incremental.md`.

## Componentes

| Archivo | Responsabilidad |
| --- | --- |
| `scripts/update_catalog.py` | Coordinador CLI (14 fases, dry-run por defecto) |
| `src/sync_config.py` | Destinos autorizados, credenciales por entorno, motor de solo lectura, lista aprobada, redacción de secretos |
| `src/sync_plan.py` | Plan puro y validación (recalcula hashes v1, sin I/O) |
| `src/sync_load.py` | Lectura del catálogo, aplicación transaccional, verificación |
| `tests/test_sync_plan.py` | 34 pruebas del planificador |
| `tests/test_sync_load.py` | 23 pruebas de persistencia, backfill y reversión |
| `tests/test_update_catalog.py` | 17 pruebas del coordinador extremo a extremo simulado |

## Uso

```powershell
# 0 solicitudes HTTP y 0 conexiones (modo seguro)
python scripts/update_catalog.py

# Extracción real + plan, sin escribir nada
python scripts/update_catalog.py --live --dry-run --target supabase

# Solo extracción/transformación/validación, sin base de datos
python scripts/update_catalog.py --live --skip-db

# Subconjunto de la lista aprobada (siempre dentro de la lista aprobada)
python scripts/update_catalog.py --live --dry-run --limit 10 --target supabase

# Escritura: requiere --apply, destino habilitado y confirmación
python scripts/update_catalog.py --live --apply --target supabase
```

Opciones relevantes:

- `--dry-run` (predeterminado) y `--apply` son mutuamente excluyentes.
- `--repositories RUTA` usa otra lista aprobada (por defecto
  `approved_repositories_100_verified.txt`).
- `--summary-file RUTA` escribe el resumen Markdown saneado.
- `--target local|supabase`; si se omite, se usa `OPENBRIDGE_SYNC_TARGET`.

## Códigos de salida

| Código | Significado |
| --- | --- |
| `0` | Ejecución completa (plan completo; en apply, verificación correcta) |
| `1` | Error de extracción, transformación, planificación, aplicación o verificación |
| `2` | Uso o configuración inválidos (lista aprobada, `--apply` sin destino) |
| `3` | Ejecución incompleta: faltan repositorios, README no verificable, destino no comparado |
| `4` | Escritura bloqueada por las compuertas de seguridad |

El workflow trata `0` y `3` como advertencia (anotación `::warning::`) y falla con
cualquier otro código. Un plan incompleto nunca se presenta como completo.

## Variables de entorno y secretos

Credenciales **solo** por entorno; nunca se imprimen, y `DatabaseTarget.describe()`
no incluye la contraseña.

| Variable | Destino | Uso |
| --- | --- | --- |
| `GITHUB_TOKEN` | GitHub | Token de lectura para la API (5000 req/h) |
| `OPENBRIDGE_SYNC_TARGET` | — | `local` o `supabase` por defecto |
| `OPENBRIDGE_SUPABASE_DB_HOST` | supabase | Host `*.pooler.supabase.com` o `db.<ref>.supabase.co` |
| `OPENBRIDGE_SUPABASE_DB_PORT` | supabase | `5432` o `6543` |
| `OPENBRIDGE_SUPABASE_DB_NAME` | supabase | Obligatorio `postgres` |
| `OPENBRIDGE_SUPABASE_DB_USER` | supabase | Cuenta de servicio (nunca `postgres`/`postgres.*`) |
| `OPENBRIDGE_SUPABASE_DB_PASSWORD` | supabase | Contraseña de la cuenta de servicio |
| `OPENBRIDGE_SUPABASE_DB_SSLMODE` | supabase | `require` por defecto; `disable`/`allow` prohibidos |
| `OPENBRIDGE_LOCAL_DB_HOST` | local | `localhost`/`127.0.0.1`/`::1` |
| `OPENBRIDGE_LOCAL_DB_NAME` | local | Obligatorio `openbridge_db` |
| `OPENBRIDGE_LOCAL_DB_USER` / `_PASSWORD` | local | Cuenta no administrativa |
| `OPENBRIDGE_SYNC_ALLOW_WRITES` | — | Convención canónica: `1` habilita escrituras (por defecto ausente/`0`) |
| `OPENBRIDGE_SYNC_CONFIRMATION` | — | Debe ser exactamente `CONFIRMO_SINCRONIZACION_INCREMENTAL_OPENBRIDGE_V1` |

`OPENBRIDGE_SYNC_WRITES_ENABLED` fue una denominación preliminar del runbook y
**no** la lee el código: la única variable válida es
`OPENBRIDGE_SYNC_ALLOW_WRITES=1`. En GitHub Actions la variable de repositorio
con ese mismo nombre debe valer `1` para habilitar el paso de aplicación manual.

Secretos de GitHub Actions usados por el workflow:
`OPENBRIDGE_SUPABASE_DB_HOST`, `_PORT`, `_NAME`, `_USER`, `_PASSWORD`.
El token GitHub usa el `GITHUB_TOKEN` automático del workflow.

> **Pendiente de confirmación:** el dueño de la base debe proporcionar los
> valores y confirmar el nombre de la cuenta de servicio. Los nombres de arriba
> son el contrato que espera el código; no se ha verificado ningún valor real.

### Privilegios requeridos

- Lectura (`SELECT`) sobre `public.catalog_repositories`,
  `public.catalog_readmes` e `information_schema.columns` para el modo dry-run.
- `INSERT`/`UPDATE` sobre ambas tablas solo para la cuenta de escritura cuando
  se habilite `--apply`. No se necesitan `DELETE`, DDL ni privilegios de
  propietario.
- Este repositorio **no crea ni altera roles**. `openbridge_ai_reader` y
  `openbridge_ai_writer` se usan tal como estén definidos por el equipo de datos.
- Las credenciales se leen **solo** de variables de entorno: el coordinador no
  carga `data-engineering/.env` para evitar usar credenciales locales por
  accidente. En local, exporte las variables antes de ejecutar con `--live`.

## Workflow

- Horario: `0 11 * * *` (UTC) = 06:00 en America/Bogota; además `workflow_dispatch`.
- `permissions: contents: read`, `concurrency: update-catalog` sin cancelación y
  `timeout-minutes: 30`.
- El trabajo define `OPENBRIDGE_SYNC_ALLOW_WRITES: "0"`: la ejecución programada
  es siempre de solo lectura.
- Ejecuta `pytest tests -q` y después `update_catalog.py --live --dry-run`. En un
  dispatch con `mode=apply` se omite el dry-run para no duplicar la extracción: el
  propio `--apply` imprime el plan antes de escribir.
- El resumen Markdown se publica en la ejecución y como artefacto de 14 días.
- El paso de aplicación manual solo se ejecuta con `mode=apply`, la variable de
  repositorio `OPENBRIDGE_SYNC_ALLOW_WRITES=1` y el secreto
  `OPENBRIDGE_SYNC_CONFIRMATION`. **Por defecto está deshabilitado.**

### Habilitar escrituras más adelante

1. Cerrar las pruebas reales en staging (ver "Pendientes").
2. Confirmar cuenta de servicio y privilegios mínimos con el equipo de datos.
3. Primera aplicación manual con el plan revisado en un dry-run previo de la
   misma ventana de tiempo (el plan bloquea si el catálogo cambió).
4. Configurar el secreto `OPENBRIDGE_SYNC_CONFIRMATION` y la variable de
   repositorio `OPENBRIDGE_SYNC_ALLOW_WRITES=1`.
5. Repetir el dry-run: debe mostrar `0 escrituras` (idempotencia) antes de
   considerar la automatización estable.

## Backfill de hashes históricos (política aprobada 2026-10-28)

Los cinco registros con `content_hash_version IS NULL` ya **no** se preservan por
`hash_version_missing`: el planificador los recalcula con el contrato canónico
`openbridge-ai-v1` y emite un `UPDATE` que escribe `content_hash` y
`content_hash_version` en la misma sentencia.

Condiciones para planificar el backfill (si falta una, la fila se preserva):

1. `content_hash_version` es exactamente `NULL`.
2. El repositorio se extrajo y transformó sin errores.
3. El README está disponible o GitHub devolvió un 404 confirmado.
4. El hash v1 se puede recalcular con los 12 campos del contrato.

La actualización mantiene el control optimista: el `UPDATE` exige el
`content_hash` y la versión previos (`IS NOT DISTINCT FROM`); si otro proceso
cambió la fila, no se escribe nada y se revierte la transacción completa. Si el
hash recalculado coincide con el almacenado, la versión se actualiza igualmente.
No hay `DELETE`: los READMEs existentes se conservan.

Qué observar en el resumen:

- `Hashes históricos sin versión a recalcular con openbridge-ai-v1: N (IDs: ...)`.
- `Hashes con versión no soportada preservados (IDs: ...)` (contrato ajeno).
- `backfill de hash=N` en la línea de resultado de `--apply`.

El backfill **no se ha ejecutado** sobre Supabase: requiere un `--apply`
autorizado igual que cualquier otra escritura.

### Hash de Ingesta vs huella de IA

- `content_hash` / `content_hash_version` son un control **interno de Ingesta**
  para detectar cambios e idempotencia.
- La IA calcula su propia huella con `description`, `topics` y `readme_text`; no
  lee esas dos columnas.
- Recalcular un hash histórico no provoca reprocesamientos de IA.
- `github_id` sigue siendo la clave estable de `v_repos_for_ai`; no se renombran
  ni cambian tipos de columnas existentes de la vista.

## Pruebas

```powershell
python -m pytest tests -q          # 260 pruebas, sin red ni PostgreSQL
```

Las pruebas nuevas cubren: inserción, actualización de metadatos, actualización
de README, ejecución sin cambios, compatibilidad `openbridge-ai-v1`, hashes
inconsistentes, 404 confirmado, errores transitorios, límite de cuota, datos
incompletos, duplicados, reversión transaccional, validación del destino, cuenta
administrativa, dry-run sin escrituras, redacción de secretos e idempotencia.

Cobertura específica del backfill histórico:

- fila con versión `NULL` → `UPDATE` con `legacy_backfill=True`;
- la versión queda en `openbridge-ai-v1` aunque el hash recalculado coincida;
- hash histórico obsoleto se reemplaza y también se actualiza la versión;
- hash almacenado `NULL` se acepta como estado previo;
- README no verificable o 404 con README almacenado → sin escrituras;
- versión distinta y desconocida → `PRESERVE`;
- conflicto concurrente → `Plan obsoleto`, reversión y ningún campo sobrescrito;
- atomicidad: un único `UPDATE` escribe hash y versión;
- segunda ejecución sin cambios → `0` escrituras;
- ninguna sentencia `DELETE`.

## Verificación manual (solo lectura)

```sql
-- Estado general (tras un --apply autorizado debe haber 0 filas fuera de v1)
SELECT content_hash_version, count(*)
FROM public.catalog_repositories
GROUP BY content_hash_version ORDER BY 1;

-- Los cinco hashes históricos del backfill (IDs acordados)
SELECT github_id, full_name, content_hash, content_hash_version
FROM public.catalog_repositories
WHERE github_id IN (2325298, 6838921, 10270250, 33884891, 53631945)
ORDER BY github_id;

-- Filas que siguen sin versión v1 (debe ser 0 tras el backfill)
SELECT github_id, full_name, content_hash_version
FROM public.catalog_repositories
WHERE content_hash_version IS NULL OR content_hash_version <> 'openbridge-ai-v1';

-- Hashes nulos o con longitud distinta de 64
SELECT github_id, full_name, content_hash
FROM public.catalog_repositories
WHERE content_hash IS NULL OR length(content_hash) <> 64;

-- READMEs huérfanos o repositorios sin README
SELECT r.github_id, r.full_name
FROM public.catalog_repositories r
LEFT JOIN public.catalog_readmes m ON m.github_id = r.github_id
WHERE m.github_id IS NULL;
```

## Diagnóstico

| Síntoma | Causa probable | Acción |
| --- | --- | --- |
| `ERROR: Destino no autorizado` | `--target`/`OPENBRIDGE_SYNC_TARGET` inválido | Usar `local` o `supabase` |
| `Falta la contraseña del destino` | Secreto no configurado | Configurar el secreto del destino |
| `no admite cuentas administrativas` | Usuario `postgres`/`postgres.*` | Solicitar cuenta de servicio |
| `no se pudo leer el catálogo` | Credenciales/red/permisos | Revisar el resumen; el dry-run termina con código 3 |
| `Faltan repositorios aprobados` | Fallo de red o cuota | Revisar `HTTP` y `403/429`; el plan no declara completitud |
| `README no verificable` | Error transitorio de README | Repetir; no hay escrituras para ese repositorio |
| `Hashes históricos ... a recalcular` | Filas con versión NULL | Backfill planificado; se aplica solo con `--apply` autorizado |
| `versión de hash no soportada` | Fila con un contrato distinto | Revisar manualmente; no se reescribe |
| `el hash almacenado no corresponde a sus propios datos` | Inconsistencia previa | Revisar manualmente; no se sobrescribe |
| `Plan obsoleto` | Otro proceso modificó el catálogo | Repetir el dry-run y volver a planificar |
| `planificación: fuera de la lista aprobada` | Lista aprobada distinta a la extracción | Corregir la lista; no se escribe nada |
| `ESCRITURA BLOQUEADA` | Falta `--apply`, habilitación o confirmación | Completar la checklist de habilitación |

## Limitaciones conocidas

- No hay eliminación automática de repositorios ni READMEs.
- El backfill de los cinco hashes históricos está implementado y probado offline,
  pero **no se ha ejecutado** contra Supabase.
- La coincidencia de identidad es por `github_id`; un `full_name` distinto se
  preserva y se advierte (los renombrados requieren revisión).
- `topics` se compara aceptando arreglo de PostgreSQL o JSON; formatos
  desconocidos se preservan sin escribir.
- Extraer 100 repositorios implica ~200 peticiones HTTP; sin `GITHUB_TOKEN` la
  cuota anónima (60/h) no alcanza y el plan quedará incompleto.
- La verificación posterior se ejecuta en una conexión nueva de solo lectura; si
  falla, los datos ya aplicados se informan como discrepancia y el proceso
  termina con código 1.
