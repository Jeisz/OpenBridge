# ADR-002 — Carga inicial conservadora v0.2

**Estado: PROPUESTA TÉCNICA. No autoriza migración ni escritura.**

## Hechos validados previamente

- Ingesta y transformación real de 10 repositorios y 10 READMEs.
- La tabla `public.catalog_repositories` tiene `github_id` PK, `topics` TEXT y `content_hash` VARCHAR, pero carece de `content_hash_version`.
- `public.catalog_readmes` tiene `github_id` PK/FK (`ON DELETE CASCADE`), `readme_text` TEXT y `updated_at` TIMESTAMPTZ.
- Cinco repositorios históricos tienen hashes de origen desconocido. **Nunca se actualizan en esta versión**.

## Decisión propuesta

1. Conservar el planificador v0.1 y su CLI: `python src/load.py` hace 0 conexiones; `--live --count 10` consulta GitHub y PostgreSQL en modo solo lectura. **No hay CLI de escritura**.
2. `prepare_write_batch` genera en memoria solo candidatos con `github_id` que NO exista en `CatalogSnapshot`; recalcula SHA-256 a través de `preview_transformation_hashes` (ADR-001), con requisitos estrictos de integridad/identidad.
3. `insert_new_batch` es una **API Python**, nunca llamada desde el CLI; exige autorización explícita `WRITE_CONFIRMATION` y base exacta `openbridge_db`. No es autorización de seguridad de usuarios: no reemplaza privilegios mínimos de PostgreSQL ni aprobación humana.
4. Exige que la columna `content_hash_version` ya exista. La migración propuesta está en `sql/002_content_hash_version_REVISAR_NO_EJECUTAR.sql`; **nunca se ejecuta automáticamente**.
5. En una sola transacción de PostgreSQL (`engine.begin`), se lee nuevamente el catálogo para evitar planes obsoletos, se verifica identidad y se inserta exclusivamente un registro de repositorio nuevo con 14 campos seleccionados, incluyendo `content_hash`, `content_hash_version`.
6. Para `topics` TEXT se almacena JSON de lista normalizada, ordenada, compacta y en UTF-8 sin escape ASCII. La codificación del hash usa el JSON canónico de ADR-001, NO este `topics` aislado.
7. **Solo se usan `INSERT ... ON CONFLICT (github_id) DO NOTHING RETURNING`**. No se actualizan registros preexistentes, hashes históricos ni READMEs antiguos; incluso los READMEs faltantes de repositorios históricos quedan pendientes de una política separada.
8. Cuando se insertó un repositorio nuevo y el README estaba disponible, se inserta `catalog_readmes` con `updated_at=CURRENT_TIMESTAMP` en la **misma transacción**. Un error revierte toda la transacción.
9. Un 404 README confirmado se representa como `null` en el hash v1 y no crea fila README. Errores de red/cuota/JSON detienen la preparación antes de abrir conexión.
10. Repetir un lote ya insertado no cambia filas y devuelve 0 inserciones. Un conflicto de `github_id`/`full_name` de diferente identidad aborta; carreras con otros escritores no controlados pueden necesitar índice único por `full_name` y/o coordinación con backend.

## Riesgos y límites

- La capa Python **no sustituye** permisos de BD de solo lectura para la cuenta de IA. Recomendada separación futura: rol ingesta escritor y rol IA lector.
- Los metadatos de GitHub varían entre extracciones; el hash v1 es de la instantánea obtenida al preparar el lote.
- `catalog_repositories` es una tabla amplia con múltiples columnas NULL: v0.2 solo rellena los 14 campos de contrato. La compatibilidad con futuros consumidores se deberá comprobar.
- Esta versión es una carga inicial **insert-only**; no habilita actualización (UPSERT DO UPDATE) porque la política de refresh/cambio está pendiente.
- No se han ejecutado pruebas de inserción en PostgreSQL real ni se ha aplicado la migración. Los tests usan un motor SQL simulado, por lo que faltan pruebas reales de `ON CONFLICT`, triggers, privilegios y rollback.
- Para 100 repositorios, el extractor actual solo admite diez miembros de lista blanca: ampliar la selección es una tarea posterior.

## Criterios previos a cualquier escritura real

- Aprobación explícita de la migración por el equipo dueño del esquema y confirmación con IA sobre hashes versionados.
- Copia de respaldo/verificación de recuperación de la base.
- Revisión del diff de código y pruebas conjuntas aprobadas en equipo.
- Migración aplicada y verificada con `SELECT`.
- Aprobación específica para la primera operación de inserción de cinco repositorios.
- Auditoría pre/post de filas, IDs, READMEs y hashes; segunda ejecución con 0 inserciones.
