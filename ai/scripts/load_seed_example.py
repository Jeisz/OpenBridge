"""Carga o borra los datos de ejemplo de la IA en las tablas ai.* de Supabase.

Datos: ai/data/seed/ejemplo_ia.json. Escritos desde el README de cada repo y
revisados manualmente. No son salida del LLM. Sirven para probar la API del
catálogo y la ficha antes de que la IA genere los datos reales.

Uso desde la raíz del repo, con el entorno activo:
    python -m ai.scripts.load_seed_example            # borra e inserta (repetible)
    python -m ai.scripts.load_seed_example --limpiar  # solo borra

AI_DATABASE_URL (usuario escritor de la IA) tiene que estar en .env.
Antes de generar los datos reales de la IA, correr con --limpiar.
"""

import argparse
import json
import os
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from pydantic import ValidationError

from ai.catalog import load_categories
from ai.scripts.export_catalog_snapshot import REPOS_FILE as SNAPSHOT_FILE
from ai.scripts.export_catalog_snapshot import redact
from shared.contracts.integration_idea import IntegrationIdea
from shared.contracts.repo import Repo

SEED_FILE = Path(__file__).resolve().parents[1] / "data" / "seed" / "ejemplo_ia.json"
ENV_VAR = "AI_DATABASE_URL"
MARKER = "seed-ejemplo"
MAX_IDEAS = 3  # regla de IntegrationIdea fuera del modelo: 1–3 ideas por herramienta, o ninguna

# Columnas que se escriben en cada tabla (ai/sql/001 y 003).
ENRICHMENT_COLUMNS = ("github_id", "summary_es", "use_cases", "ai_input_hash")
CATEGORY_COLUMNS = ("github_id", "category_id", "assigned_by", "rank")
IDEA_COLUMNS = (
    "id", "github_id", "title", "integration_type", "summary", "compatible_stack",
    "dependencies", "difficulty", "triggers", "snippet", "snippet_language",
    "docs_url", "generated_by", "reviewed_at", "based_on_hash",
)

# Borra solo filas marcadas, para no tocar nunca datos reales. Las categorías no
# tienen marca: se borran las de los repos cuyo resumen sigue marcado, por eso van primero.
DELETE_STATEMENTS = (
    ("ai_repo_categories",
     "delete from ai.ai_repo_categories where github_id in "
     "(select github_id from ai.ai_repo_enrichment where ai_input_hash = %(marker)s)"),
    ("ai_integration_ideas",
     "delete from ai.ai_integration_ideas where based_on_hash = %(marker)s"),
    ("ai_repo_enrichment",
     "delete from ai.ai_repo_enrichment where ai_input_hash = %(marker)s"),
)


def load_seed(path: Path = SEED_FILE) -> dict:
    """Contenido del archivo de la semilla, sin validar."""
    return json.loads(path.read_text(encoding="utf-8"))


def validate_seed(seed: dict, snapshot: list[dict], category_ids: set[str]) -> None:
    """Revisa la semilla antes de tocar la base.

    Junta todos los errores y los lanza juntos en un ValueError, para corregirlos
    de una vez.
    """
    errors = []
    if seed.get("marker") != MARKER:
        errors.append(f"marker debe ser {MARKER!r}")

    catalog = {row["github_id"]: row for row in snapshot}
    for repo in seed["repos"]:
        name = repo["full_name"]

        # Sin clave foránea: nada impide en la base una fila de un repo que no existe.
        row = catalog.get(repo["github_id"])
        if row is None or row["full_name"] != name:
            errors.append(f"{name}: no está en el snapshot con github_id {repo['github_id']}")
            continue

        # Contrato Repo: la fila de la ingesta + la parte que escribe la IA.
        ai_part = {key: repo[key] for key in ("summary_es", "use_cases", "categories")}
        try:
            Repo.model_validate({**row, **ai_part})
        except ValidationError as e:
            errors.append(f"{name}: no cumple Repo\n{e}")

        # CategoryAssignment no comprueba que el id exista.
        for assignment in repo["categories"]:
            if assignment["category_id"] not in category_ids:
                errors.append(f"{name}: categoría que no existe: {assignment['category_id']!r}")

        if len(repo["ideas"]) > MAX_IDEAS:
            errors.append(f"{name}: {len(repo['ideas'])} ideas (máximo {MAX_IDEAS})")

        for idea in repo["ideas"]:
            try:
                IntegrationIdea.model_validate({**idea, "full_name": name})
            except ValidationError as e:
                errors.append(f"{idea['id']}: no cumple IntegrationIdea\n{e}")
            # Marcas que identifican los datos de ejemplo y permiten reemplazarlos.
            if idea["based_on_hash"] != MARKER:
                errors.append(f"{idea['id']}: based_on_hash debe ser {MARKER!r}")
            if idea["reviewed_at"] is not None:
                errors.append(f"{idea['id']}: reviewed_at debe ser null (una idea revisada no se reemplaza al generar las reales)")

    if errors:
        raise ValueError("La semilla no es válida:\n" + "\n".join(f"- {e}" for e in errors))


def to_rows(seed: dict) -> dict[str, list[dict]]:
    """Filas para las tres tablas de la IA, con los nombres de sus columnas.

    El rank de cada categoría es su posición en la lista: la primera es la principal.
    Las ideas se guardan con github_id, no con full_name (la API completa full_name al leer).
    """
    enrichment, categories, ideas = [], [], []
    for repo in seed["repos"]:
        github_id = repo["github_id"]
        enrichment.append({
            "github_id": github_id,
            "summary_es": repo["summary_es"],
            "use_cases": repo["use_cases"],
            "ai_input_hash": seed["marker"],
        })
        for rank, assignment in enumerate(repo["categories"], start=1):
            categories.append({
                "github_id": github_id,
                "category_id": assignment["category_id"],
                "assigned_by": assignment["assigned_by"],
                "rank": rank,
            })
        for idea in repo["ideas"]:
            row = {**idea, "github_id": github_id}
            ideas.append({column: row[column] for column in IDEA_COLUMNS})
    return {"enrichment": enrichment, "categories": categories, "ideas": ideas}


def insert_statement(table: str, columns: tuple[str, ...]) -> str:
    names = ", ".join(columns)
    values = ", ".join(f"%({column})s" for column in columns)
    return f"insert into ai.{table} ({names}) values ({values})"


def delete_seed(cur: psycopg.Cursor) -> dict[str, int]:
    """Borra los datos de ejemplo. Devuelve cuántas filas borró por tabla."""
    deleted = {}
    for table, statement in DELETE_STATEMENTS:
        cur.execute(statement, {"marker": MARKER})
        deleted[table] = cur.rowcount
    return deleted


def insert_seed(cur: psycopg.Cursor, rows: dict[str, list[dict]]) -> dict[str, int]:
    """Inserta las filas de to_rows(). Devuelve cuántas insertó por tabla."""
    targets = (
        ("ai_repo_enrichment", ENRICHMENT_COLUMNS, rows["enrichment"]),
        ("ai_repo_categories", CATEGORY_COLUMNS, rows["categories"]),
        ("ai_integration_ideas", IDEA_COLUMNS, rows["ideas"]),
    )
    for table, columns, table_rows in targets:
        cur.executemany(insert_statement(table, columns), table_rows)
    return {table: len(table_rows) for table, _, table_rows in targets}


def main() -> None:
    parser = argparse.ArgumentParser(description="Carga o borra los datos de ejemplo de la IA.")
    parser.add_argument("--limpiar", action="store_true", help="solo borra los datos de ejemplo")
    args = parser.parse_args()

    load_dotenv()
    url = os.environ.get(ENV_VAR)
    if not url:
        sys.exit(f"Falta {ENV_VAR} en .env (ver .env.example)")

    rows = None
    if not args.limpiar:
        seed = load_seed()
        snapshot = json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))
        try:
            validate_seed(seed, snapshot, set(load_categories()))
        except ValueError as e:
            sys.exit(str(e))
        rows = to_rows(seed)

    # Una sola transacción: al salir del with sin error se confirma. Con error se deshace todo.
    try:
        with psycopg.connect(url) as conn, conn.cursor() as cur:
            deleted = delete_seed(cur)
            inserted = insert_seed(cur, rows) if rows else {}
    except psycopg.Error as e:
        sys.exit(f"No se pudo escribir en la base (no se cambió nada): {redact(str(e), url)}")

    for table, count in deleted.items():
        print(f"{table}: {count} borradas, {inserted.get(table, 0)} insertadas")


if __name__ == "__main__":
    main()
