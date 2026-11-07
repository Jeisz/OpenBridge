"""Lo que la IA publicó en la base: con qué entrada y con qué reglas se generó cada dato.

Lee y escribe ai.ai_processing (una fila por repo y tipo de dato). Las filas se devuelven con
la forma de los registros del lote (provider, model, prompt_version, ai_input_hash, full_name,
review.skipped), así la comparación (ai/catalog_diff.py) funciona igual con lo publicado que
con los archivos.
"""

import psycopg

KINDS = ("enrichment", "ideas")      # los vectores se suman cuando se guarden en la base

SELECT_PUBLISHED = """
select github_id, kind, full_name, ai_input_hash, provider, model, prompt_version, skipped
from ai.ai_processing
where kind = any(%(kinds)s)
"""
UPSERT_PROCESSING = """
insert into ai.ai_processing
    (github_id, kind, full_name, ai_input_hash, provider, model, prompt_version, skipped, processed_at)
values
    (%(github_id)s, %(kind)s, %(full_name)s, %(ai_input_hash)s, %(provider)s, %(model)s,
     %(prompt_version)s, %(skipped)s, now())
on conflict (github_id, kind) do update set
    full_name = excluded.full_name,
    ai_input_hash = excluded.ai_input_hash,
    provider = excluded.provider,
    model = excluded.model,
    prompt_version = excluded.prompt_version,
    skipped = excluded.skipped,
    processed_at = excluded.processed_at
"""


def to_records(rows: list[tuple]) -> dict[str, dict[int, dict]]:
    """Filas de ai_processing → registros por tipo de dato y github_id."""
    records: dict[str, dict[int, dict]] = {kind: {} for kind in KINDS}
    for github_id, kind, full_name, input_hash, provider, model, version, skipped in rows:
        records[kind][github_id] = {
            "github_id": github_id, "full_name": full_name, "ai_input_hash": input_hash,
            "provider": provider, "model": model, "prompt_version": version,
            "review": {"skipped": skipped},
        }
    return records


def fetch_published(url: str) -> dict[str, dict[int, dict]]:
    """Lo publicado, en una transacción de solo lectura (alcanza con el lector de la IA)."""
    with psycopg.connect(url) as conn:
        conn.read_only = True
        rows = conn.execute(SELECT_PUBLISHED, {"kinds": list(KINDS)}).fetchall()
    return to_records(rows)


def processing_rows(kind: str, records: list[dict]) -> list[dict]:
    """Filas de ai_processing desde los registros del lote que se van a publicar."""
    return [{"github_id": r["github_id"], "kind": kind, "full_name": r["full_name"],
             "ai_input_hash": r["ai_input_hash"], "provider": r["provider"], "model": r["model"],
             "prompt_version": r["prompt_version"], "skipped": r["review"].get("skipped")}
            for r in records]
