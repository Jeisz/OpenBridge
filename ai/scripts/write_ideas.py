"""Escribe las ideas de integración (ai/data/catalog/ideas.json) en ai.ai_integration_ideas.

Solo reemplaza ideas regenerables (generated_by = 'llm' y reviewed_at nulo) de los repos que
están en el archivo. Las ideas revisadas o escritas por una persona nunca se tocan y ocupan
cupo: un repo tiene como máximo 3 ideas y una por tipo, contando las revisadas.
Antes borra las ideas de los datos de ejemplo, si quedara alguna (solo ideas: el
enriquecimiento y las categorías de ejemplo los limpia write_enrichment).

Todo va en una sola transacción: o se escribe completo, o no cambia nada.
Repetible: correrlo dos veces deja la base igual que correrlo una.

Uso desde la raíz del repo, con el entorno activo:
    python -m ai.scripts.write_ideas              # solo valida el archivo y muestra qué haría
    python -m ai.scripts.write_ideas --escribir   # escribe

AI_DATABASE_URL (usuario escritor de la IA) tiene que estar en .env.
"""

import argparse
import json
import os
import sys
from collections import defaultdict

import psycopg
from dotenv import load_dotenv

from ai.ideas import MAX_IDEAS
from ai.scripts.export_catalog_snapshot import REPOS_FILE as SNAPSHOT_FILE
from ai.scripts.export_catalog_snapshot import redact
from ai.scripts.generate_ideas import OUT_FILE as IDEAS_FILE
from ai.scripts.load_seed_example import ENV_VAR, IDEA_COLUMNS, MARKER, insert_statement
from shared.contracts.integration_idea import IntegrationIdea

SELECT_PROTECTED = """
select id, github_id, integration_type, based_on_hash
from ai.ai_integration_ideas
where github_id = any(%(ids)s) and (generated_by = 'human' or reviewed_at is not null)
"""
DELETE_REGENERABLE = """
delete from ai.ai_integration_ideas
where github_id = any(%(ids)s) and generated_by = 'llm' and reviewed_at is null
"""

# Solo las ideas de los datos de ejemplo: el enriquecimiento y las categorías de ejemplo
# los limpia write_enrichment.
DELETE_SEED_IDEAS = "delete from ai.ai_integration_ideas where based_on_hash = %(marker)s"


def validate_records(records: list[dict], snapshot: list[dict]) -> None:
    """Revisa el archivo contra el catálogo y el contrato antes de tocar la base.

    Junta todos los errores y los lanza juntos en un ValueError.
    """
    errors = []
    catalog = {row["github_id"]: row for row in snapshot}
    seen_ids: set[str] = set()
    for r in records:
        name = r["full_name"]
        row = catalog.get(r["github_id"])
        if row is None or row["full_name"] != name:
            errors.append(f"{name}: no está en el snapshot con github_id {r['github_id']}")
            continue
        if r["review"]["failed"]:
            errors.append(f"{name}: sin respuesta válida del modelo; corre generate_ideas de nuevo")
        if row["archived"] and r["ideas"]:
            errors.append(f"{name}: repo archivado con ideas")
        if len(r["ideas"]) > MAX_IDEAS:
            errors.append(f"{name}: {len(r['ideas'])} ideas; el máximo es {MAX_IDEAS}")
        for idea in r["ideas"]:
            if idea["id"] in seen_ids:
                errors.append(f"{name}: id repetido {idea['id']}")
            seen_ids.add(idea["id"])
            try:
                data = {k: v for k, v in idea.items() if k in IntegrationIdea.model_fields}
                IntegrationIdea.model_validate(data)
            except ValueError as e:
                errors.append(f"{name}: {idea['id']} no cumple IntegrationIdea\n{e}")
            if idea["full_name"] != name:
                errors.append(f"{name}: {idea['id']} dice ser de {idea['full_name']}")
    if errors:
        raise ValueError("El archivo no es válido:\n" + "\n".join(f"- {e}" for e in errors))


def plan_rows(records: list[dict], protected: list[dict]) -> tuple[list[dict], dict]:
    """Filas para insertar, respetando las ideas protegidas (revisadas o de una persona).

    protected: filas de la base con id, github_id, integration_type y based_on_hash.
    Devuelve (filas, informe). Por repo: cupo = 3 − protegidas; se salta una idea de un
    tipo que ya tiene una protegida; si el id choca con uno protegido, toma el siguiente libre.
    """
    by_repo: dict[int, list[dict]] = defaultdict(list)
    for p in protected:
        by_repo[p["github_id"]].append(p)
    rows: list[dict] = []
    report = {"skipped_type": [], "skipped_full": [], "stale_reviewed": []}
    for r in records:
        gid = r["github_id"]
        kept = by_repo.get(gid, [])
        report["stale_reviewed"] += [f"{r['full_name']} · {p['id']}" for p in kept
                                     if p["based_on_hash"] != r["ai_input_hash"]]
        types = {p["integration_type"] for p in kept}
        used_ids = {p["id"] for p in kept}
        room = MAX_IDEAS - len(kept)
        for idea in r["ideas"]:
            if idea["integration_type"] in types:
                report["skipped_type"].append(f"{r['full_name']} · {idea['id']}")
                continue
            if room == 0:
                report["skipped_full"].append(f"{r['full_name']} · {idea['id']}")
                continue
            row = {column: idea.get(column) for column in IDEA_COLUMNS if column != "github_id"}
            row["github_id"] = gid
            if row["id"] in used_ids:
                n = 1
                while f"llm-{gid}-{n}" in used_ids:
                    n += 1
                row["id"] = f"llm-{gid}-{n}"
            used_ids.add(row["id"])
            types.add(idea["integration_type"])
            room -= 1
            rows.append(row)
    return rows, report


def write(cur: psycopg.Cursor, records: list[dict]) -> dict:
    """Borra la semilla y las ideas regenerables de los repos del archivo, y escribe las nuevas."""
    ids = [r["github_id"] for r in records]
    cur.execute(DELETE_SEED_IDEAS, {"marker": MARKER})
    deleted_seed = cur.rowcount
    cur.execute(SELECT_PROTECTED, {"ids": ids})
    protected = [dict(zip(("id", "github_id", "integration_type", "based_on_hash"), row))
                 for row in cur.fetchall()]
    rows, report = plan_rows(records, protected)
    cur.execute(DELETE_REGENERABLE, {"ids": ids})
    replaced = cur.rowcount
    cur.executemany(insert_statement("ai_integration_ideas", IDEA_COLUMNS), rows)
    return {
        "ideas de ejemplo borradas": deleted_seed,
        "ideas regenerables borradas": replaced,
        "ideas escritas": len(rows),
        "ideas protegidas (revisadas o de una persona, sin tocar)": len(protected),
        "saltadas por tipo ya revisado": report["skipped_type"],
        "saltadas por cupo lleno": report["skipped_full"],
        "revisadas con README cambiado (revisar de nuevo)": report["stale_reviewed"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Escribe las ideas de integración en Supabase.")
    parser.add_argument("--escribir", action="store_true",
                        help="escribe en la base; sin esta opción solo muestra qué haría")
    args = parser.parse_args()

    records = json.loads(IDEAS_FILE.read_text(encoding="utf-8"))["repos"]
    snapshot = json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))
    try:
        validate_records(records, snapshot)
    except ValueError as e:
        sys.exit(str(e))
    total = sum(len(r["ideas"]) for r in records)
    print(f"Válido: {len(records)} repos, {total} ideas "
          f"({sum(bool(r['ideas']) for r in records)} repos con ideas).")
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
            counts = write(cur, records)
    except psycopg.Error as e:
        sys.exit(f"No se pudo escribir en la base (no se cambió nada): {redact(str(e), url)}")
    for key, value in counts.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
