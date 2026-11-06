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
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv

from ai.catalog import DATA_DIR, load_categories, load_repos
from ai.enrich import PROMPT_VERSION, README_CHARS, enrich_repo, input_hash, readme_input, user_message
from ai.llm import PROVIDERS, LLMError, LLMRateLimited, LLMUnavailable

OUT_FILE = DATA_DIR / "catalog" / "enrichment.json"
WAIT_SECONDS = 30.0      # espera ante un límite por minuto que no dice cuánto esperar
MAX_WAIT_SECONDS = 120   # si el proveedor pide más, es el límite del día: se detiene
MAX_WAITS = 5            # esperas seguidas por el mismo repo antes de rendirse
REPLACE_TRIES = 5        # en Windows, un antivirus o un editor puede retener el archivo un momento
TRANSIENT_WAIT_SECONDS = 10.0  # espera ante un error temporal del proveedor (503)


def load_records(path: Path) -> dict[int, dict]:
    """Registros ya guardados, por github_id. Vacío si el archivo no existe."""
    if not path.is_file():
        return {}
    return {r["github_id"]: r for r in json.loads(path.read_text(encoding="utf-8"))["repos"]}


def save_records(path: Path, records: dict[int, dict]) -> None:
    """Escribe todos los registros, ordenados por nombre para que el diff sea legible.

    Primero a un archivo temporal y luego se reemplaza: si el proceso se corta
    a mitad de la escritura, el archivo anterior queda intacto. En Windows, el
    reemplazo falla si otro programa tiene el archivo abierto; se reintenta unas veces.
    """
    ordered = sorted(records.values(), key=lambda r: r["full_name"].lower())
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps({"prompt_version": PROMPT_VERSION, "repos": ordered},
                              ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for attempt in range(1, REPLACE_TRIES + 1):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            if attempt == REPLACE_TRIES:
                raise PermissionError(f"No se pudo reemplazar {path}: ¿está abierto en otro "
                                      f"programa? Lo nuevo quedó en {tmp}.") from None
            time.sleep(0.5 * attempt)


def up_to_date(record: dict | None, current_hash: str) -> bool:
    """El registro existe, tiene datos y salió de esta misma entrada, reglas y modelo."""
    return (record is not None and record["ai_input_hash"] == current_hash
            and bool(record["categories"]))


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
    repos = load_repos()
    if args.repos:
        wanted = set(args.repos)
        repos = [r for r in repos if r.full_name in wanted]
        missing = wanted - {r.full_name for r in repos}
        if missing:
            sys.exit(f"No están en el catálogo: {', '.join(sorted(missing))}")

    records = load_records(args.out)
    done = []
    for n, repo in enumerate(repos, start=1):
        current = input_hash(user_message(repo, readme_input(repo, args.readme_chars)), args.provider)
        if not args.force and up_to_date(records.get(repo.github_id), current):
            print(f"[{n}/{len(repos)}] {repo.full_name}: sin cambios, se salta")
            done.append(records[repo.github_id])
            continue
        for _ in range(MAX_WAITS):
            try:
                record = enrich_repo(repo, categories, args.provider, args.readme_chars)
                break
            except LLMRateLimited as err:
                wait = err.retry_after or WAIT_SECONDS
                if wait > MAX_WAIT_SECONDS:
                    save_records(args.out, records)
                    sys.exit(f"{err}\nParece el límite del día. Lo hecho quedó guardado: "
                             "vuelve a correr el mismo comando más tarde.")
                print(f"    límite por minuto: espero {wait:.0f} s")
                time.sleep(wait)
            except LLMUnavailable as err:
                if not err.transient:
                    print(f"[{n}/{len(repos)}] {repo.full_name}: ERROR {err}")
                    record = None
                    break
                print(f"    error temporal del proveedor: espero {TRANSIENT_WAIT_SECONDS:.0f} s")
                time.sleep(TRANSIENT_WAIT_SECONDS)
            except LLMError as err:
                print(f"[{n}/{len(repos)}] {repo.full_name}: ERROR {err} (se reintenta en otra corrida)")
                record = None
                break
        else:
            sys.exit("Demasiadas esperas seguidas; lo hecho quedó guardado.")
        if record is None:
            continue
        records[repo.github_id] = record
        save_records(args.out, records)
        done.append(record)
        print(f"[{n}/{len(repos)}] {repo.full_name}: {', '.join(record['categories']) or 'SIN CATEGORÍAS'}"
              f" · {len(record['use_cases'])} casos de uso · {record['review']['seconds']} s")

    print("\n" + summary(done))
    print(f"\nGuardado en {args.out}")


if __name__ == "__main__":
    main()
