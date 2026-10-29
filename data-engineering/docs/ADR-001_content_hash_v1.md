# ADR-001 — Huella canónica de consumo IA (`content_hash`) v1

**Proyecto:** OpenBridge · **Fecha:** 2026-10-20
**Estado:** Aprobado por responsable de la ingesta para implementación local y pruebas. **Pendiente de validación interequipo con IA y de cualquier autorización de migración/escritura.**

## Contexto

- La vista `v_repos_for_ai` expone `content_hash` de `catalog_repositories` y `readme_text` de `catalog_readmes`.
- Los cinco hashes existentes son hexadecimales de 64 caracteres, pero no se conoce su fórmula reproducible.
- T05 mencionaba SHA-256 de README y fecha de push sin serialización definida. Variantes ensayadas no reprodujeron los históricos.
- La transformación actual entrega los campos normalizados del repositorio, los READMEs disponibles y observaciones cuando faltan.

## Decisión para v1

Calcular **SHA-256 de bytes UTF-8 de JSON canónico**, compuesto por estas claves de nivel superior:

```json
{
  "contract_version": "openbridge-ai-v1",
  "readme_text": "... o null",
  "repository": { "...": "los 12 campos declarados abajo" }
}
```

Las claves exactas de `repository` son `github_id`, `full_name`, `name`, `description`, `homepage`, `language`, `topics`, `stargazers_count`, `forks_count`, `pushed_at`, `archived`, `license_spdx_id`.

1. Primero ejecutar `transform_records` de OpenBridge; no se reciben dicts de GitHub sin transformar.
2. Solo aceptar ese conjunto exacto de 12 campos: ni más ni menos. Tipos: `github_id` entero positivo; conteos enteros no negativos; `archived` booleano; `topics` lista de cadenas no vacías, minúsculas, sin duplicados; `full_name` y `name` cadenas no vacías compatibles; `description`, `homepage`, `language`, `license_spdx_id` cadenas o `null`; `pushed_at` fecha ISO 8601 con zona o `null`.
3. Transformar las fechas válidas `pushed_at` a **UTC** y representación exacta `YYYY-MM-DDTHH:MM:SS.ffffffZ` (siempre seis cifras de microsegundos); si es `null`, preservar JSON `null`.
4. Normalizar **NFC** (Unicode) para todas las cadenas y README. No convertir `null` a texto, ni recortar README, ni sustituir saltos de línea, ni cambiar espacios internos.
5. Ordenar alfabéticamente `topics` tras validar normalización. El orden de entrada de etiquetas no modifica el hash.
6. JSON compacto, sin espacios: separación de claves `:`, separación de elementos `,`, **todas las claves ordenadas lexicográficamente** en cada objeto, comillas/escapes según JSON estándar, caracteres no ASCII escritos como UTF-8 (`ensure_ascii=False`). Booleanos JSON (`true`/`false`), `null` JSON. Nada de `NaN`/infinito.
7. Codificar el JSON resultante en UTF-8 **sin BOM**, SHA-256 y obtener 64 caracteres hexadecimales en minúsculas.
8. Incluir `contract_version` dentro de los bytes hasheados. El campo externo `content_hash_version` del preview es informativo; **la columna PostgreSQL correspondiente NO existe todavía**.
9. README ausente se representa por `null` **solo** si GitHub devolvió `NO_ENCONTRADO` confirmado (404). `""` significa archivo README presente y vacío; produce un hash distinto. `NO_CONSULTADO`, `LIMITE_API`, `ERROR_HTTP`, `UTF8_INVALIDO` y otros fallos de recuperación detienen el cálculo del lote.
10. No incluir hora de extracción, hora de carga, token, código HTTP ni metadatos efímeros. **Sí** se incluyen conteos de estrellas/forks: si cambian, el hash cambia aunque el README permanezca igual.

## Tratamiento de legado y persistencia

- Los cinco `content_hash` previos se consideran **versión desconocida**. No se comparan, recalculan ni reescriben en esta entrega.
- Ni `hash_contract.py` ni `load.py` del paquete ejecutan migraciones o escrituras; la versión propuesta solo permite vista previa.
- Para llevar v1 a PostgreSQL se necesitará coordinar con IA el almacenamiento de versión, la convivencia con los hashes históricos, el tratamiento de `NULL` y un plan de UPSERT transaccional e idempotente. **Esto requiere aprobación separada.**
- La decisión incluye campos de metadatos potencialmente volátiles: para IA, un cambio en estrellas puede causar reprocesamiento. Más adelante se podrá estudiar separar `hash_readme`/`hash_metadata` como una nueva versión, sin alterar v1.

## Vectores de interoperabilidad

`content_hash_v1_vectors.json` contiene tres vectores completos: README con Unicode, README 404 representado por `null`, y README presente vacío. Cada vector incluye `repository`, `readme_text`, `canonical_json` y `sha256`. IA puede reproducirlos de forma independiente.

## Criterios de aceptación

- Hash reproducible en dos ejecuciones idénticas.
- Diferencia ante cambios de contenido o campos incluidos.
- Normalización consistente de Unicode, zona horaria y orden de `topics`.
- `null` y `""` se diferencian.
- Una descarga errónea de README no se convierte en 404.
- Cero conexión SQL/HTTP y cero mutaciones sobre `TransformationResult`.
- Cualquier actualización de la especificación requerirá versión nueva y acuerdo con IA.
