# Ingesta — catálogo OpenBridge

Extracción desde la API de GitHub, normalización, contrato de hash y
sincronización incremental del catálogo (`local` o Supabase). Es la parte del
Data Engineer; los notebooks exploratorios quedan en `notebooks/`.

## Estructura

| Ruta | Contenido |
| --- | --- |
| `src/config.py`, `src/database.py` | Conexión PostgreSQL del pipeline histórico (insert-only) |
| `src/extract_github.py` | Extracción por REST con auditoría de respuestas |
| `src/transform.py` | Normalización y observaciones |
| `src/hash_contract.py` | Contrato canónico `openbridge-ai-v1` (`content_hash_v1`) |
| `src/load.py` | Carga inicial insert-only y CLI de plan (0 escrituras) |
| `src/sync_config.py` | Destinos autorizados, credenciales por entorno, lista aprobada |
| `src/sync_plan.py` | Planificador puro: INSERT/UPDATE/PRESERVE y backfill de hashes |
| `src/sync_load.py` | Lectura del catálogo, aplicación transaccional y verificación |
| `scripts/update_catalog.py` | Coordinador CLI de la sincronización (dry-run por defecto) |
| `tests/` | Pruebas offline (sin red ni PostgreSQL) |
| `docs/` | ADR-001…004, runbook operativo y vectores del hash |
| `approved_repositories_100_verified.txt` | Lista aprobada de repositorios |

## Uso

```powershell
python -m pip install --requirement requirements.txt

# Modo seguro: 0 solicitudes HTTP y 0 conexiones
python scripts/update_catalog.py

# Extracción real + plan sin escrituras
python scripts/update_catalog.py --live --dry-run --target supabase

# Subconjunto de la lista aprobada
python scripts/update_catalog.py --live --dry-run --limit 10

# Escritura: exige --apply, destino habilitado y confirmación explícita
python scripts/update_catalog.py --live --apply --target supabase
```

Las credenciales se leen **solo** de variables de entorno (ver `.env.example` en
la raíz): `OPENBRIDGE_SUPABASE_DB_*`, `OPENBRIDGE_LOCAL_DB_*`, `GITHUB_TOKEN`.
`--apply` requiere `OPENBRIDGE_SYNC_ALLOW_WRITES=1` y
`OPENBRIDGE_SYNC_CONFIRMATION=CONFIRMO_SINCRONIZACION_INCREMENTAL_OPENBRIDGE_V1`,
y rechaza cuentas administrativas (`postgres`, `postgres.*`).

## Pruebas

```powershell
python -m pytest tests -q
```

260 pruebas offline. No requieren red, PostgreSQL ni credenciales.

## Garantías de seguridad

- `--dry-run` es el modo por defecto; sin `--live` no hay HTTP ni SQL.
- El plan se valida antes de escribir y nunca contiene `DELETE`.
- Hash y versión se escriben en la misma sentencia, con control optimista: si
  cambió el contenido, la transacción se revierte completa.
- Las filas con `content_hash_version` desconocida se preservan sin tocarlas.
- El workflow `.github/workflows/update_catalog.yml` es de solo lectura en la
  ejecución programada; la escritura es manual y está deshabilitada por defecto.

Detalle operativo: [`docs/update_catalog_runbook.md`](docs/update_catalog_runbook.md).
Decisiones: [`docs/ADR-004_sincronizacion_incremental.md`](docs/ADR-004_sincronizacion_incremental.md).
