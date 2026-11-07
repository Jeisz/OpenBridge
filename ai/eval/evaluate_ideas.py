"""Mide las ideas de integración de la muestra de validación contra la referencia.

Lee una o más corridas de ai.scripts.generate_ideas (el mismo grupo de repos, una por
archivo) y una referencia (por defecto ai/eval/ideas_reference.json), calcula los criterios
fijados en la referencia antes de correr y escribe un reporte Markdown con lo que hay que
revisar a mano.

Uso desde la raíz del repo:
    python -m ai.eval.evaluate_ideas CORRIDA1.json [CORRIDA2.json ...] --out reporte.md
    python -m ai.eval.evaluate_ideas CORRIDA.json --reference ai/eval/otra_referencia.json --out r.md
"""

import argparse
import json
from collections import Counter
from pathlib import Path

REFERENCE_FILE = Path(__file__).parent / "ideas_reference.json"


def load_reference(path: Path = REFERENCE_FILE) -> dict[str, dict]:
    """La referencia, por nombre de repo."""
    return {r["full_name"]: r for r in json.loads(path.read_text(encoding="utf-8"))["repos"]}


def load_criteria(path: Path = REFERENCE_FILE) -> dict[str, int]:
    """Los umbrales fijados en la referencia antes de correr (min_required, min_stable)."""
    return json.loads(path.read_text(encoding="utf-8"))["criteria"]


def load_run(path: Path) -> dict[str, dict]:
    """Una corrida de generate_ideas, por nombre de repo."""
    return {r["full_name"]: r for r in json.loads(path.read_text(encoding="utf-8"))["repos"]}


def problems(idea: dict, ref: dict) -> list[str]:
    """Por qué una idea no debió salir según la referencia. Vacía = permitida."""
    out = []
    if ref.get("max_ideas") == 0:
        out.append("el repo debía quedar sin ideas")
    if idea["integration_type"] in ref["forbidden"]:
        out.append(f"tipo prohibido ({idea['integration_type']})")
    for text in ref.get("forbidden_snippets", []):
        if idea["snippet"] and text in idea["snippet"]:
            out.append(f"snippet prohibido ({text})")
    return out


def score_run(run: dict[str, dict], reference: dict[str, dict]) -> dict:
    """Los criterios para una corrida."""
    required = found = 0
    empty_total = empty_ok = 0
    over_max, forbidden, unexpected, missing = [], [], [], []
    for name, ref in reference.items():
        record = run.get(name)
        if record is None or record["review"]["failed"]:
            missing.append(name)
            continue
        types = {i["integration_type"] for i in record["ideas"]}
        required += len(ref["required"])
        found += sum(r["type"] in types for r in ref["required"])
        if ref.get("max_ideas") == 0:
            empty_total += 1
            empty_ok += not record["ideas"]
        elif ref.get("max_ideas") is not None and len(record["ideas"]) > ref["max_ideas"]:
            over_max.append(name)
        expected = {r["type"] for r in ref["required"]} | set(ref["admissible"])
        for idea in record["ideas"]:
            why = problems(idea, ref)
            if why:
                forbidden.append(f"{name} · {idea['title']}: {'; '.join(why)}")
            elif idea["integration_type"] not in expected:
                unexpected.append(f"{name} · {idea['integration_type']} · {idea['title']}")
    dropped = Counter(d["reason"] for r in run.values() for d in r["review"]["dropped_ideas"])
    return {"required": required, "found": found, "empty_total": empty_total,
            "empty_ok": empty_ok, "over_max": over_max, "forbidden": forbidden,
            "unexpected": unexpected, "missing": missing, "dropped": dict(dropped),
            "ideas": sum(len(r["ideas"]) for r in run.values()),
            "with_snippet": sum(i["snippet"] is not None for r in run.values() for i in r["ideas"])}


def stable_repos(runs: list[dict[str, dict]], reference: dict[str, dict]) -> list[str]:
    """Repos con el mismo conjunto de tipos en todas las corridas."""
    stable = []
    for name in reference:
        sets = [frozenset(i["integration_type"] for i in run[name]["ideas"])
                for run in runs if name in run]
        if len(sets) == len(runs) and len(set(sets)) == 1:
            stable.append(name)
    return stable


def verdicts(score: dict, criteria: dict[str, int]) -> list[tuple[str, str, bool]]:
    """(criterio, valor, cumple) para una corrida."""
    minimum = criteria["min_required"]
    return [
        (f"Requeridas encontradas (≥ {minimum})", f"{score['found']}/{score['required']}",
         score["found"] >= minimum and not score["missing"]),
        ("Repos que debían quedar sin ideas", f"{score['empty_ok']}/{score['empty_total']}",
         score["empty_ok"] == score["empty_total"]),
        ("Repos por encima de su tope", str(len(score["over_max"])), not score["over_max"]),
        ("Ideas prohibidas", str(len(score["forbidden"])), not score["forbidden"]),
    ]


def idea_lines(idea: dict) -> list[str]:
    """Una idea, para revisarla a mano."""
    snippet = (idea["snippet"] or "—").splitlines()[0][:100]
    return [
        f"- **[{idea['integration_type']} · {idea['difficulty']}] {idea['title']}**",
        f"  - Resumen: {idea['summary']}",
        f"  - Cita: «{idea['evidence'][:200]}»",
        f"  - Stack: {', '.join(idea['compatible_stack'])} · Dependencias: "
        f"{', '.join(idea['dependencies']) or '—'} · Disparadores: {', '.join(idea['triggers']) or '—'}",
        f"  - Snippet ({idea['snippet_language'] or '—'}): `{snippet}`",
        f"  - Documentación: {idea['docs_url']}",
    ]


def report(paths: list[Path], runs: list[dict[str, dict]], reference: dict[str, dict],
           criteria: dict[str, int], reference_name: str) -> str:
    """Reporte Markdown: criterios por corrida, estabilidad y detalle por repo."""
    scores = [score_run(run, reference) for run in runs]
    lines = ["# Ideas de integración: validación", "",
             f"Corridas: {', '.join(p.name for p in paths)}. "
             f"Referencia: `{reference_name}` ({len(reference)} repos).", "",
             "## Criterios", "",
             "| Criterio | " + " | ".join(f"Corrida {n}" for n in range(1, len(runs) + 1)) + " |",
             "|---|" + "---|" * len(runs)]
    rows = [verdicts(score, criteria) for score in scores]
    for row, (label, _, _) in enumerate(rows[0]):
        cells = [f"{value} {'✅' if ok else '❌'}" for _, value, ok in (r[row] for r in rows)]
        lines.append(f"| {label} | " + " | ".join(cells) + " |")
    if len(runs) > 1:
        stable = stable_repos(runs, reference)
        ok = len(stable) >= criteria["min_stable"]
        lines += ["", f"**Estabilidad** (mismos tipos en todas las corridas, ≥ {criteria['min_stable']}): "
                      f"{len(stable)}/{len(reference)} {'✅' if ok else '❌'}"]
        unstable = [n for n in reference if n not in stable]
        if unstable:
            lines.append(f"Cambian entre corridas: {', '.join(unstable)}")
    for n, score in enumerate(scores, start=1):
        lines += ["", f"### Corrida {n}", "",
                  f"- Ideas: {score['ideas']} (con snippet: {score['with_snippet']})",
                  f"- Descartadas por el código: {score['dropped'] or 'ninguna'}"]
        for label, key in (("Prohibidas", "forbidden"), ("Fuera de la referencia (revisar)", "unexpected"),
                           ("Por encima del tope", "over_max"), ("Sin registro o sin respuesta válida", "missing")):
            if score[key]:
                lines.append(f"- {label}: " + " · ".join(score[key]))

    lines += ["", "## Por repo (revisión manual)", "",
              "Para cada idea: ¿el tipo y el resumen son coherentes con la cita? "
              "¿Los disparadores aportan o son relleno? ¿El enlace lleva a la sección correcta?"]
    for name, ref in reference.items():
        expected = ", ".join(r["type"] for r in ref["required"]) or "ninguna"
        lines += ["", f"### {name}", "",
                  f"Requeridas: {expected} · Admisibles: {', '.join(ref['admissible']) or '—'} · "
                  f"Prohibidas: {', '.join(ref['forbidden']) or '—'}"
                  + (f" · Tope: {ref['max_ideas']}" if ref.get("max_ideas") is not None else "")]
        if ref.get("note"):
            lines.append(f"Nota: {ref['note']}")
        for n, run in enumerate(runs, start=1):
            record = run.get(name)
            lines += ["", f"**Corrida {n}**"]
            if record is None:
                lines.append("- (sin registro)")
                continue
            if not record["ideas"]:
                lines.append(f"- Sin ideas{' (' + record['review']['skipped'] + ')' if record['review']['skipped'] else ''}")
            for idea in record["ideas"]:
                lines += idea_lines(idea)
            for d in record["review"]["dropped_ideas"]:
                lines.append(f"- Descartada ({d['reason']}): [{d['integration_type']}] {d['title']}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Mide las ideas contra la referencia.")
    parser.add_argument("runs", nargs="+", type=Path, help="corridas de generate_ideas")
    parser.add_argument("--reference", type=Path, default=REFERENCE_FILE)
    parser.add_argument("--out", type=Path, required=True, help="reporte Markdown")
    args = parser.parse_args()

    reference = load_reference(args.reference)
    criteria = load_criteria(args.reference)
    runs = [load_run(p) for p in args.runs]
    args.out.write_text(report(args.runs, runs, reference, criteria,
                               f"ai/eval/{args.reference.name}"), encoding="utf-8")
    for n, score in enumerate(score_run(run, reference) for run in runs):
        print(f"Corrida {n + 1}: " + " · ".join(f"{label.split(' (')[0]} {value}{'' if ok else ' ❌'}"
                                                 for label, value, ok in verdicts(score, criteria)))
    if len(runs) > 1:
        print(f"Estables: {len(stable_repos(runs, reference))}/{len(reference)}")
    print(f"Reporte: {args.out}")


if __name__ == "__main__":
    main()
