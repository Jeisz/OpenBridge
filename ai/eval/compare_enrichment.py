"""Compara corridas del enriquecimiento para elegir el modelo.

Lee los archivos que escribe ai.scripts.enrich_catalog (uno por corrida) y arma
un reporte Markdown con las métricas por modelo y, por repo, lo que generó cada
corrida, para la revisión manual.

Uso desde la raíz del repo:
    python -m ai.eval.compare_enrichment ARCHIVO [ARCHIVO ...] --out reporte.md

Las corridas de un mismo proveedor se agrupan por el campo "provider" de cada registro,
en el orden en que se pasan los archivos.
"""

import argparse
import json
import re
import statistics
from collections import defaultdict
from pathlib import Path

from ai.catalog import DATA_DIR, load_categories

# Datos de ejemplo escritos a mano desde el README: sirven de referencia de categorías.
SEED_FILE = DATA_DIR / "seed" / "ejemplo_ia.json"


def named_in_examples(full_name: str, categories) -> bool:
    """True si el repo aparece como ejemplo en las notas de alguna categoría.

    Esos repos se pueden clasificar copiando el ejemplo: no prueban las reglas.
    """
    name = full_name.split("/")[1].lower()
    notes = " ".join(c.llm_notes for c in categories.values()).lower()
    return re.search(rf"\b{re.escape(name)}\b", notes) is not None


def load_runs(paths: list[Path]) -> dict[str, list[dict[str, dict]]]:
    """Por modelo, la lista de sus corridas; cada corrida, sus registros por repo."""
    runs = defaultdict(list)
    for path in paths:
        records = json.loads(path.read_text(encoding="utf-8"))["repos"]
        model = records[0]["provider"] if records else path.stem
        runs[model].append({r["full_name"]: r for r in records})
    return dict(runs)


def primary(record: dict | None) -> str | None:
    return record["categories"][0] if record and record["categories"] else None


def model_metrics(runs: list[dict[str, dict]], repos: list[str],
                  seed: dict[str, str]) -> dict:
    """Métricas de un modelo sobre sus corridas."""
    records = [run[n] for run in runs for n in repos if n in run]
    first_ok = sum(r["review"]["attempts"] == 1 and bool(r["categories"]) for r in records)
    seconds = [r["review"]["seconds"] for r in records]
    metrics = {
        "registros": f"{len(records)} de {len(runs) * len(repos)}",
        "válidas al primer intento": f"{first_ok} de {len(records)}",
        "casos de uso aceptados": sum(len(r["use_cases"]) for r in records),
        "casos de uso descartados": sum(len(r["review"]["dropped_use_cases"]) for r in records),
        "tokens por repo (entrada / salida)":
            f"{sum(r['review']['input_tokens'] for r in records) // max(len(records), 1)} / "
            f"{sum(r['review']['output_tokens'] for r in records) // max(len(records), 1)}",
        "segundos por repo (mediana / máx.)":
            f"{statistics.median(seconds):.1f} / {max(seconds):.1f}" if seconds else "—",
    }
    if len(runs) >= 2:
        both = [n for n in repos if n in runs[0] and n in runs[1]]
        same = sum(primary(runs[0][n]) == primary(runs[1][n]) for n in both)
        metrics["misma categoría principal en las 2 corridas"] = f"{same} de {len(both)}"
    hits = [primary(run.get(n)) == seed[n] for run in runs for n in seed if n in run]
    metrics["principal igual a la semilla (referencia)"] = f"{sum(hits)} de {len(hits)}"
    return metrics


def report(runs: dict[str, list[dict[str, dict]]], repos: list[str]) -> str:
    categories = load_categories()
    seed = {r["full_name"]: r["categories"][0]["category_id"]
            for r in json.loads(SEED_FILE.read_text(encoding="utf-8"))["repos"]
            if r["full_name"] in repos}
    lines = ["# Comparación del enriquecimiento", ""]

    names = list(runs)
    lines += ["## Métricas por modelo", "", "| Métrica | " + " | ".join(names) + " |",
              "|---|" + "---|" * len(names)]
    table = {m: model_metrics(runs[m], repos, seed) for m in names}
    for key in table[names[0]]:
        lines.append(f"| {key} | " + " | ".join(str(table[m].get(key, "—")) for m in names) + " |")

    lines += ["", "## Por repo", "",
              "Revisión: ¿la categoría principal es correcta? ¿los casos de uso son usos "
              "principales y no características? ¿el resumen es fiel?", ""]
    for name in repos:
        tag = "nombrado en los ejemplos" if named_in_examples(name, categories) else "no nombrado"
        reference = f" · semilla: `{seed[name]}`" if name in seed else ""
        lines += [f"### {name} ({tag}{reference})", ""]
        for model in names:
            for i, run in enumerate(runs[model], start=1):
                r = run.get(name)
                if r is None:
                    lines.append(f"- **{model} · corrida {i}:** sin registro")
                    continue
                cats = ", ".join(r["categories"]) or "SIN CATEGORÍAS"
                lines.append(f"- **{model} · corrida {i}:** `{cats}` · {r['summary_es']}")
                for use_case in r["use_cases"]:
                    lines.append(f"  - {use_case}")
                for d in r["review"]["dropped_use_cases"]:
                    lines.append(f"  - ~~{d['use_case']}~~ ({d['reason']})")
        lines += ["", "Revisión: ", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compara corridas del enriquecimiento.")
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    runs = load_runs(args.files)
    repos = sorted({n for model in runs.values() for run in model for n in run}, key=str.lower)
    args.out.write_text(report(runs, repos), encoding="utf-8")
    print(f"{len(runs)} modelos, {len(repos)} repos → {args.out}")


if __name__ == "__main__":
    main()
