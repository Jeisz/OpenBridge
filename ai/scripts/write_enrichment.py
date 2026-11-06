"""Escribe el catálogo enriquecido (ai/data/catalog/enrichment.json) en las tablas ai.* de Supabase.

Escribe en ai.ai_repo_enrichment (resumen y casos de uso) y ai.ai_repo_categories
(categorías, con assigned_by = 'llm'). Antes borra los datos de ejemplo escritos a
mano, para que la ficha no mezcle textos de ejemplo con los generados.

Todo va en una sola transacción: o se escribe completo, o no cambia nada.
Repetible: correrlo dos veces deja la base igual que correrlo una.
Las categorías asignadas por una persona (assigned_by = 'human') nunca se tocan.

Uso desde la raíz del repo, con el entorno activo:
    python -m ai.scripts.write_enrichment              # solo muestra qué haría
    python -m ai.scripts.write_enrichment --escribir   # escribe

AI_DATABASE_URL (usuario escritor de la IA) tiene que estar en .env.
"""

import argparse
import json
import os
import sys

import psycopg
from dotenv import load_dotenv

from ai.catalog import load_categories
from ai.scripts.enrich_catalog import OUT_FILE as ENRICHMENT_FILE
from ai.scripts.export_catalog_snapshot import REPOS_FILE as SNAPSHOT_FILE
from ai.scripts.export_catalog_snapshot import redact
from ai.scripts.load_seed_example import ENV_VAR, delete_seed
from shared.contracts.repo import Repo

UPSERT_ENRICHMENT = """
insert into ai.ai_repo_enrichment (github_id, summary_es, use_cases, ai_input_hash, processed_at)
values (%(github_id)s, %(summary_es)s, %(use_cases)s, %(ai_input_hash)s, now())
on conflict (github_id) do update set
    summary_es = excluded.summary_es,
    use_cases = excluded.use_cases,
    ai_input_hash = excluded.ai_input_hash,
    processed_at = excluded.processed_at
"""
HUMAN_CATEGORIES = "select distinct github_id from ai.ai_repo_categories where assigned_by = 'human'"
DELETE_CATEGORIES = "delete from ai.ai_repo_categories where github_id = %(github_id)s"
INSERT_CATEGORY = """
insert into ai.ai_repo_categories (github_id, category_id, assigned_by, rank)
values (%(github_id)s, %(category_id)s, 'llm', %(rank)s)
"""


def validate_records(records: list[dict], snapshot: list[dict], category_ids: set[str]) -> None:
    """Revisa los registros contra el catálogo y el contrato antes de tocar la base.

    Junta todos los errores y los lanza juntos en un ValueError.
    """
    errors = []
    catalog = {row["github_id"]: row for row in snapshot}
    for r in records:
        name = r["full_name"]
        row = catalog.get(r["github_id"])
        # Sin clave foránea: nada impide en la base una fila de un repo que no existe.
        if row is None or row["full_name"] != name:
            errors.append(f"{name}: no está en el snapshot con github_id {r['github_id']}")
            continue
        unknown = [c for c in r["categories"] if c not in category_ids]
        if unknown:
            errors.append(f"{name}: categorías que no existen: {unknown}")
        try:  # contrato Repo: la fila de la ingesta + la parte que escribe la IA
            Repo.model_validate({**row, "summary_es": r["summary_es"], "use_cases": r["use_cases"],
                                 "categories": [{"category_id": c, "assigned_by": "llm"}
                                                for c in r["categories"]]})
        except ValueError as e:
            errors.append(f"{name}: no cumple Repo\n{e}")
    if errors:
        raise ValueError("El archivo no es válido:\n" + "\n".join(f"- {e}" for e in errors))


def to_rows(records: list[dict]) -> tuple[list[dict], list[dict]]:
    """Filas para ai_repo_enrichment y ai_repo_categories. El rank es la posición: 1 = principal."""
    enrichment = [{"github_id": r["github_id"], "summary_es": r["summary_es"],
                   "use_cases": r["use_cases"], "ai_input_hash": r["ai_input_hash"]}
                  for r in records]
    categories = [{"github_id": r["github_id"], "category_id": c, "rank": rank}
                  for r in records for rank, c in enumerate(r["categories"], start=1)]
    return enrichment, categories


def write(cur: psycopg.Cursor, enrichment: list[dict], categories: list[dict]) -> dict[str, int]:
    """Borra la semilla y escribe las filas. Devuelve conteos para el informe."""
    deleted = delete_seed(cur)
    cur.executemany(UPSERT_ENRICHMENT, enrichment)

    cur.execute(HUMAN_CATEGORIES)
    human = {row[0] for row in cur.fetchall()}
    to_replace = sorted({c["github_id"] for c in categories} - human)
    cur.executemany(DELETE_CATEGORIES, [{"github_id": g} for g in to_replace])
    cur.executemany(INSERT_CATEGORY, [c for c in categories if c["github_id"] not in human])
    return {
        "semilla borrada (filas)": sum(deleted.values()),
        "resúmenes escritos": len(enrichment),
        "categorías escritas": sum(c["github_id"] not in human for c in categories),
        "repos con categorías humanas (sin tocar)": len(human),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Escribe el catálogo enriquecido en Supabase.")
    parser.add_argument("--escribir", action="store_true",
                        help="escribe en la base; sin esta opción solo muestra qué haría")
    args = parser.parse_args()

    records = json.loads(ENRICHMENT_FILE.read_text(encoding="utf-8"))["repos"]
    snapshot = json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))
    try:
        validate_records(records, snapshot, set(load_categories()))
    except ValueError as e:
        sys.exit(str(e))
    enrichment, categories = to_rows(records)
    print(f"Válido: {len(enrichment)} repos, {len(categories)} categorías.")
    if not args.escribir:
        print("Sin --escribir no se toca la base.")
        return

    load_dotenv()
    url = os.environ.get(ENV_VAR)
    if not url:
        sys.exit(f"Falta {ENV_VAR} en .env (ver .env.example)")
    # Una sola transacción: al salir del with sin error se confirma. Con error se deshace todo.
    try:
        with psycopg.connect(url) as conn, conn.cursor() as cur:
            counts = write(cur, enrichment, categories)
    except psycopg.Error as e:
        sys.exit(f"No se pudo escribir en la base (no se cambió nada): {redact(str(e), url)}")
    for key, value in counts.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
