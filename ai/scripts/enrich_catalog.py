"""Genera con el LLM las categorías, el resumen y los casos de uso de los repos del catálogo.

Guarda cada repo apenas llega, así que una corrida cortada se retoma donde quedó:
un repo cuyo hash de entrada no cambió no se vuelve a pedir al modelo.

Uso desde la raíz del repo, con el entorno activo:
    python -m ai.scripts.enrich_catalog                                  # los 100 repos
    python -m ai.scripts.enrich_catalog --repos apache/flink apache/kafka --out salida.json
    python -m ai.scripts.enrich_catalog --provider claude-haiku --readme-chars 4000 --out salida.json

La clave del proveedor tiene que estar en .env.
"""

import argparse
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv

from ai.catalog import ENRICHMENT_FILE, load_categories, load_repos
from ai.enrich import PROMPT_VERSION, README_CHARS, enrich_repo, input_hash, readme_input, user_message
from ai.llm import PROVIDERS
from ai.scripts.batch import run_batch, select_repos

OUT_FILE = ENRICHMENT_FILE


def up_to_date(record: dict | None, current_hash: str) -> bool:
    """El registro existe, tiene datos y salió de esta misma entrada, reglas y modelo."""
    return (record is not None and record["ai_input_hash"] == current_hash
            and bool(record["categories"]))


def describe(record: dict) -> str:
    """Una línea con el resultado de un repo, para el progreso."""
    return (f"{', '.join(record['categories']) or 'SIN CATEGORÍAS'}"
            f" · {len(record['use_cases'])} casos de uso · {record['review']['seconds']} s")


def summary(records: list[dict]) -> str:
    """Conteos para revisar la corrida."""
    reasons = Counter(d["reason"] for r in records for d in r["review"]["dropped_use_cases"])
    lines = [
        f"repos: {len(records)}",
        f"sin categorías: {sum(not r['categories'] for r in records)}",
        f"sin resumen: {sum(r['summary_es'] is None for r in records)}",
        f"con reintento: {sum(r['review']['attempts'] > 1 for r in records)}",
        f"sin casos de uso: {sum(not r['use_cases'] for r in records)}",
        f"casos de uso aceptados: {sum(len(r['use_cases']) for r in records)}",
        f"casos de uso descartados: {sum(reasons.values())} {dict(reasons)}",
        f"tokens: {sum(r['review']['input_tokens'] for r in records)} de entrada, "
        f"{sum(r['review']['output_tokens'] for r in records)} de salida",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Enriquece el catálogo con el LLM.")
    parser.add_argument("--provider", default="gemini", choices=list(PROVIDERS))
    parser.add_argument("--repos", nargs="+", metavar="OWNER/NAME",
                        help="solo estos repos (por defecto, todos)")
    parser.add_argument("--readme-chars", type=int, default=README_CHARS)
    parser.add_argument("--out", type=Path, default=OUT_FILE)
    parser.add_argument("--force", action="store_true", help="regenera aunque el hash no cambie")
    args = parser.parse_args()

    load_dotenv()
    categories = load_categories()
    repos = select_repos(load_repos(), args.repos)

    done = run_batch(
        repos, args.out, PROMPT_VERSION,
        current_hash=lambda r: input_hash(user_message(r, readme_input(r, args.readme_chars)),
                                          args.provider),
        process=lambda r: enrich_repo(r, categories, args.provider, args.readme_chars),
        is_done=up_to_date, describe=describe, force=args.force)

    print("\n" + summary(done))
    print(f"\nGuardado en {args.out}")


if __name__ == "__main__":
    main()
