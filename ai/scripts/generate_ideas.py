"""Genera con el LLM las ideas de integración de los repos del catálogo.

Guarda cada repo apenas llega, así que una corrida cortada se retoma donde quedó:
un repo cuyo hash de entrada no cambió no se vuelve a pedir al modelo. Un repo sin
ideas (lista vacía) es un resultado válido y tampoco se vuelve a pedir.

Uso desde la raíz del repo, con el entorno activo:
    python -m ai.scripts.generate_ideas                                    # los 100 repos
    python -m ai.scripts.generate_ideas --repos ollama/ollama redis/redis --out salida.json

La clave del proveedor tiene que estar en .env.
"""

import argparse
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv

from ai.catalog import SOURCE_DIRS, load_repos
from ai.enrich import input_hash, user_message
from ai.ideas import PROMPT_VERSION, ideas_for_repo, ideas_input
from ai.llm import PROVIDERS
from ai.scripts.batch import run_batch, select_repos

OUT_FILE = SOURCE_DIRS["snapshot"] / "ideas.json"


def up_to_date(record: dict | None, current_hash: str) -> bool:
    """El registro salió de esta misma entrada, reglas y modelo, y el modelo respondió.

    A diferencia del enriquecimiento, una lista de ideas vacía cuenta como hecha.
    """
    return (record is not None and record["ai_input_hash"] == current_hash
            and not record["review"]["failed"])


def describe(record: dict) -> str:
    """Una línea con el resultado de un repo, para el progreso."""
    review = record["review"]
    if review["skipped"]:
        return f"sin ideas ({review['skipped']})"
    if review["failed"]:
        return "SIN RESPUESTA VÁLIDA"
    types = ", ".join(i["integration_type"] for i in record["ideas"]) or "sin ideas"
    return f"{types} · {len(review['dropped_ideas'])} descartadas · {review['seconds']} s"


def summary(records: list[dict]) -> str:
    """Conteos para revisar la corrida."""
    ideas = [i for r in records for i in r["ideas"]]
    reasons = Counter(d["reason"] for r in records for d in r["review"]["dropped_ideas"])
    skipped = Counter(r["review"]["skipped"] for r in records if r["review"]["skipped"])
    lines = [
        f"repos: {len(records)}",
        f"sin ideas: {sum(not r['ideas'] for r in records)} "
        f"(sin llamar al modelo: {dict(skipped)})",
        f"sin respuesta válida: {sum(r['review']['failed'] for r in records)}",
        f"con reintento: {sum(r['review']['attempts'] > 1 for r in records)}",
        f"ideas: {len(ideas)} {dict(Counter(i['integration_type'] for i in ideas))}",
        f"con snippet: {sum(i['snippet'] is not None for i in ideas)}",
        f"descartadas: {sum(reasons.values())} {dict(reasons)}",
        f"tokens: {sum(r['review']['input_tokens'] for r in records)} de entrada, "
        f"{sum(r['review']['output_tokens'] for r in records)} de salida",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera las ideas de integración con el LLM.")
    parser.add_argument("--provider", default="gemini", choices=list(PROVIDERS))
    parser.add_argument("--repos", nargs="+", metavar="OWNER/NAME",
                        help="solo estos repos (por defecto, todos)")
    parser.add_argument("--out", type=Path, default=OUT_FILE)
    parser.add_argument("--force", action="store_true", help="regenera aunque el hash no cambie")
    parser.add_argument("--new-version", action="store_true",
                        help="sigue aunque el archivo sea de otra versión de las reglas "
                             "(regenera todos los repos)")
    args = parser.parse_args()

    load_dotenv()
    repos = select_repos(load_repos(), args.repos)
    done = run_batch(
        repos, args.out, PROMPT_VERSION,
        current_hash=lambda r: input_hash(user_message(r, ideas_input(r).text), args.provider,
                                          PROMPT_VERSION),
        process=lambda r: ideas_for_repo(r, args.provider),
        is_done=up_to_date, describe=describe, force=args.force,
        allow_version_change=args.new_version)

    print("\n" + summary(done))
    print(f"\nGuardado en {args.out}")


if __name__ == "__main__":
    main()
