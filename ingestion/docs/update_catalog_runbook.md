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

# Escritura con compuertas adicionales: plan completo, tope de filas y cuota
python scripts/update_catalog.py --live --apply --target supabase `
  --require-complete --max-writes 120 --preflight-rate-limit
```

Opciones relevantes:

- `--dry-run` (predeterminado) y `--apply` son mutuamente excluyentes.
- `--repositories RUTA` usa otra lista aprobada (por defecto
  `approved_repositories_127_verified.txt`).
- `--summary-file RUTA` escribe el resumen Markdown saneado.
- `--target local|supabase`; si se omite, se usa `OPENBRIDGE_SYNC_TARGET`.
- `--require-complete` (con `--apply`) bloquea la escritura si el plan queda
  incompleto: devuelve `4` sin abrir conexión de escritura ni modificar el
  catálogo.
- `--max-writes N` (con `--apply`) bloquea la escritura si el plan supera `N`
  filas; devuelve `4`. Es el tope ante un plan anómalo.
- `--fail-on-incomplete` devuelve `1` en lugar de `3` cuando la ejecución queda
  incompleta, para que el workflow falle en vez de anotar una advertencia.
- `--preflight-rate-limit` consulta `GET /rate_limit` (una sola petición) antes
  de extraer; si la cuota no alcanza, omite la extracción y devuelve `3`, o `4`
  si se combina con `--apply --require-complete`.

## Códigos de salida

| Código | Significado |
| --- | --- |
| `0` | Ejecución completa (plan completo; en apply, verificación correcta) |
| `1` | Error de extracción, transformación, planificación, aplicación o verificación |
| `2` | Uso o configuración inválidos (lista aprobada, `--apply` sin destino) |
| `3` | Ejecución incompleta: faltan repositorios, README no verificable, destino no comparado, cuota insuficiente (`1` si se añade `--fail-on-incomplete`) |
| `4` | Escritura bloqueada por las compuertas de seguridad: falta autorización, plan incompleto con `--require-complete` o plan que supera `--max-writes` |

El workflow invoca la sincronización con `--fail-on-incomplete`: `0` es éxito y
cualquier otro código hace fallar la ejecución (un plan incompleto sale `1`, no
`3`). Un plan incompleto nunca se presenta como completo; sin la bandera ese
mismo caso solo anotaría `::warning::` y el workflow lo daría por bueno.

## Cuota de GitHub y preflight de cuota

`--preflight-rate-limit` realiza **una** petición a `GET /rate_limit` antes de
extraer y compara `resources.core.remaining` con lo que necesita el lote.

| Concepto | Valor | Justificación |
| --- | --- | --- |
| Peticiones por repositorio | `2` | `GET /repos/{owner}/{repo}` + `GET /repos/{owner}/{repo}/readme`; `_approved_endpoints` no genera ningún otro endpoint y topics, licencia y fechas llegan en el payload de metadatos |
| Lote de 127 repositorios | `254` | `127 × 2`, el tamaño real de `approved_repositories_127_verified.txt` |
| Sondeo | `+1` | la petición a `/rate_limit`, contada aparte del lote |
| Colchón mínimo | `250` | constante `RATE_LIMIT_HEADROOM`; absorbe reintentos y ejecuciones concurrentes |

Con token (límite de `5000`/hora) el consumo nominal es `254 + 1 = 255` (5,1 %).
La condición exigida es `254 ≤ 5000 − 250 = 4750`, de modo que tras el lote
quedan `4496` peticiones de margen.

Por qué `250` y no un valor menor: cada reintento por `5xx`/timeout puede añadir
hasta `max_attempts − 1 = 2` peticiones por endpoint, así que un lote degradado
consume más que el nominal; `250` cubre el sondeo y del orden de 124 reintentos
dobles, además de dejar aire a otra ejecución concurrente (plan diario más un
dry-run manual sobre la misma cuenta). Si el consumo real supera el colchón, la
red de seguridad es otra: ante `403/429` el extractor detiene el lote completo
(`stop_batch`) en lugar de esperar, la ejecución queda incompleta y
`--require-complete` impide escribir el plan parcial. El sondeo es un aviso
temprano, no la compuerta de escritura.

Si `/rate_limit` no responde, responde un código distinto de `200` o falla la red,
el sondeo queda como no consultado (`consulted=False`): se emite una advertencia
y la ejecución continúa con el comportamiento anterior. Una respuesta `200` sin
`remaining` interpretable sí marca la ejecución como incompleta.

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
  carga `ingestion/.env` para evitar usar credenciales locales por
  accidente. En local, exporte las variables antes de ejecutar con `--live`.

## Workflow

- Horario: `0 11 * * *` (UTC) = 06:00 en America/Bogota; además `workflow_dispatch`
  manual con input `mode` (`dry-run` por defecto, `apply` solo manual).
- `permissions: contents: read`, `concurrency: update-catalog` sin cancelación y
  `timeout-minutes: 45`.
- El trabajo define `OPENBRIDGE_SYNC_ALLOW_WRITES: "0"`: la ejecución programada
  es siempre de solo lectura.
- Ejecuta `pytest tests -q` y después `update_catalog.py --live --dry-run
  --fail-on-incomplete`: un plan incompleto sale con `1` y la ejecución falla. En
  un dispatch con `mode=apply` se omite el dry-run para no duplicar la extracción:
  el propio `--apply` imprime el plan antes de escribir.
- El resumen Markdown se publica en la ejecución y como artefacto de 90 días.
- Si el trabajo falla, el trabajo `notify` abre una incidencia (o comenta la ya
  abierta) con la URL de la ejecución; solo ese trabajo tiene `issues: write`.
- El paso de aplicación manual solo se ejecuta con `mode=apply`, la variable de
  repositorio `OPENBRIDGE_SYNC_ALLOW_WRITES=1` y el secreto
  `OPENBRIDGE_SYNC_CONFIRMATION`. **Por defecto está deshabilitado y el cron
  nunca lo activa.**

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
python -m pytest tests -q          # 285 pruebas, sin red ni PostgreSQL
```

Las pruebas nuevas cubren: inserción, actualización de metadatos, actualización
de README, ejecución sin cambios, compatibilidad `openbridge-ai-v1`, hashes
inconsistentes, 404 confirmado, errores transitorios, límite de cuota, datos
incompletos, duplicados, reversión transaccional, validación del destino, cuenta
administrativa, dry-run sin escrituras, redacción de secretos e idempotencia.
Añadidas con las compuertas de escritura: `--require-complete` y `--max-writes`
(bloqueo antes de abrir cualquier conexión de escritura), `--fail-on-incomplete`,
preflight de cuota (`/rate_limit`: parseo, colchón y degradación ante fallo) y un
caso que demuestra que un fallo del sondeo no habilita la escritura de un plan
incompleto.

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
- Extraer 127 repositorios implica ~254 peticiones HTTP; sin `GITHUB_TOKEN` la
  cuota anónima (60/h) no alcanza y el plan quedará incompleto.
- La verificación posterior se ejecuta en una conexión nueva de solo lectura; si
  falla, los datos ya aplicados se informan como discrepancia y el proceso
  termina con código 1.
