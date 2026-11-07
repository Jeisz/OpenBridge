"""Marca como revisadas ideas de integración que ya están en la base.

Pone reviewed_at = ahora en las ideas indicadas por su id. Solo acepta ideas generadas por
el LLM que todavía no estén revisadas. Una idea revisada queda protegida: al regenerar,
el script de escritura no la borra ni la reemplaza.

Uso desde la raíz del repo, con el entorno activo:
    python -m ai.scripts.review_ideas --aprobar ID [ID ...]              # solo comprueba
    python -m ai.scripts.review_ideas --aprobar ID [ID ...] --escribir   # marca

AI_DATABASE_URL (usuario escritor de la IA) tiene que estar en .env.
"""

import argparse
import os
import sys

import psycopg
from dotenv import load_dotenv

from ai.scripts.export_catalog_snapshot import redact
from ai.scripts.load_seed_example import ENV_VAR

SELECT_IDEAS = """
select id, generated_by, reviewed_at is not null
from ai.ai_integration_ideas
where id = any(%(ids)s)
"""
APPROVE = """
update ai.ai_integration_ideas set reviewed_at = now()
where id = any(%(ids)s) and generated_by = 'llm' and reviewed_at is null
"""


def check_ids(requested: list[str], found: list[tuple[str, str, bool]]) -> list[str]:
    """Problemas de los ids pedidos frente a lo que hay en la base. Vacía = se pueden aprobar."""
    rows = {idea_id: (generated_by, reviewed) for idea_id, generated_by, reviewed in found}
    problems = []
    for idea_id in requested:
        if idea_id not in rows:
            problems.append(f"{idea_id}: no está en la base")
        elif rows[idea_id][0] != "llm":
            problems.append(f"{idea_id}: no es una idea del LLM")
        elif rows[idea_id][1]:
            problems.append(f"{idea_id}: ya está revisada")
    if len(set(requested)) != len(requested):
        problems.append("hay ids repetidos")
    return problems


def main() -> None:
    parser = argparse.ArgumentParser(description="Marca ideas de integración como revisadas.")
    parser.add_argument("--aprobar", nargs="+", required=True, metavar="ID")
    parser.add_argument("--escribir", action="store_true",
                        help="marca en la base; sin esta opción solo comprueba los ids")
    args = parser.parse_args()

    load_dotenv()
    url = os.environ.get(ENV_VAR)
    if not url:
        sys.exit(f"Falta {ENV_VAR} en .env (ver .env.example)")
    try:
        with psycopg.connect(url) as conn, conn.cursor() as cur:
            cur.execute(SELECT_IDEAS, {"ids": args.aprobar})
            problems = check_ids(args.aprobar, cur.fetchall())
            if problems:
                sys.exit("No se marcó nada:\n" + "\n".join(f"- {p}" for p in problems))
            if not args.escribir:
                print(f"Se pueden aprobar {len(args.aprobar)} ideas. Sin --escribir no se toca la base.")
                return
            cur.execute(APPROVE, {"ids": args.aprobar})
            print(f"Marcadas como revisadas: {cur.rowcount}")
    except psycopg.Error as e:
        sys.exit(f"No se pudo usar la base (no se cambió nada): {redact(str(e), url)}")


if __name__ == "__main__":
    main()
