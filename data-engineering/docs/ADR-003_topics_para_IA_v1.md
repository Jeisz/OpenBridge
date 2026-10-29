# ADR-003 · `topics` como lista para IA, sin cambiar la tabla

**Estado: PROPUESTA PARA REVISIÓN. No autoriza ejecutar migraciones ni escrituras.**

## Contexto comprobado

- Andrés aceptó el contrato Repo v1.0 con los nombres de `v_repos_for_ai` y pidió `topics` como lista.
- `catalog_repositories.topics` es `TEXT`. Las cinco filas históricas contienen sintaxis de arreglo de PostgreSQL, como `{react,ui}` o `{}`.
- `v_repos_for_ai.topics` es actualmente `TEXT` en la base original y `TEXT[]` en `openbridge_restore_test`, donde se realizó una migración persistente controlada y reversible en pruebas.
- Existe respaldo restaurado, comprobado fila por fila; el cambio en base original sigue pendiente.
- Se detectó que `load.py` v0.2 guardaba `topics` como JSON compacto (`["react","ui"]`), **incompatible** con `topics::TEXT[]` sobre los nuevos registros.

## Decisión propuesta

1. Conservar el tipo `TEXT` de la columna física, para evitar una migración de datos de 132 columnas y limitar el alcance.
2. Representar `topics` en esa columna con sintaxis de arreglo de PostgreSQL, tanto en históricos como en nuevos ingresos.
3. En `load.py`, enviar una lista Python mediante bind tipado `ARRAY(Text())`; PostgreSQL transforma `CAST(:topics AS TEXT[])::TEXT` en un literal válido, escapando automáticamente caracteres especiales. No construir literales manualmente.
4. En `v_repos_for_ai`, proyectar `COALESCE(r.topics::text[], ARRAY[]::text[]) AS topics`, conservando las otras 13 columnas y su orden.
5. La vista debe tener 14 columnas. No depender del `content_hash` de Ingesta para la política de reprocesamiento de IA.
6. Mantener una migración **separada** para `content_hash_version`; no ejecutarla como efecto secundario.

## Comprobaciones exigidas antes de producir escrituras

- `pytest`: 182 pruebas anteriores y nuevas regresiones del adaptador, sin conectarse a red o base de datos.
- Ejecutar `scripts/check_topics_serialization_readonly.py` **solo sobre** `openbridge_restore_test` para verificar en PostgreSQL real el round-trip lista → TEXT → TEXT[]. Comprueba arreglos vacíos, Unicode, comas, espacios, comillas y barras invertidas.
- Inspeccionar `sql/003_v_repos_topics_array_REVISAR_NO_EJECUTAR.sql` y obtener autorización explícita para migrar la base original. El SQL solo permite `openbridge_db`, exige PostgreSQL 18, protege el esquema y compara tablas antes y después en la misma transacción. No usa CASCADE.
- Auditar la vista y las filas tras la migración, verificar que ningún hash/README histórico cambió.
- Solo después de la migración `content_hash_version` y autorización independiente, ensayar inserciones de cinco nuevos con idempotencia y rollback.

## Riesgos abiertos

- El SQL de la migración todavía **no se ha ejecutado** ni validado mediante parser PostgreSQL/una instancia real; sus resultados deben comprobarse antes de usarlo en `openbridge_db`.
- La prueba local con FakeEngine simula el `INSERT`; no acredita por sí sola la adaptación del driver psycopg sobre PostgreSQL.
- Cualquier nuevo productor de `catalog_repositories.topics` debe escribir el formato PostgreSQL acordado; JSON compacto invalidaría la vista.
- `DROP VIEW` seguido de `CREATE VIEW` cambia la identidad/OID de la vista, aunque el DDL sea transaccional. Funciones, triggers, políticas, dependencias y permisos personalizados deberán ser inspeccionados si el esquema cambia antes de ejecutar.
- La migración formal es intencionalmente conservadora: exige exactamente cinco filas históricas. Al cambiar el catálogo habrá que reevaluarla y no saltarse esta protección.
