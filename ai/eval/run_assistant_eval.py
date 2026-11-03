"""Compara modelos con el flujo completo del asistente: entender → buscar → generar.

Uso, desde la raíz del repo:
    python -m ai.eval.run_assistant_eval                  # gemini, groq-low y ollama, 3 corridas
    python -m ai.eval.run_assistant_eval gemini --runs 1  # ensayo corto

Usa los casos rápidos y la búsqueda sobre el catálogo real (snapshot). Cada
proveedor recibe primero una llamada de calentamiento que no se cuenta; ante
límites de uso o errores temporales se espera y se anota. Escribe
ai/eval/results/assistant-<fecha>[-proveedores].md (reporte) y .json (todas las respuestas).
"""

import argparse
import json
import time
from collections import defaultdict
from datetime import date

from dotenv import load_dotenv

from ai import embeddings
from ai.assistant import CANDIDATES_LOGGED, CANDIDATES_SHOWN, asistir
from ai.eval.assistant_cases import load_assistant_cases
from ai.eval.flow_metrics import BUDGET_SECONDS, flow_outcome, summarize
from ai.eval.run_understand_eval import (DEFAULT_WAIT, MAX_WAITS, RESULTS_DIR, TRANSIENT_WAIT,
                                         num, pct, secs, warm_up)
from ai.llm import PROVIDERS, LLMError, LLMRateLimited, LLMUnavailable
from ai.search import SearchIndex

DEFAULT_PROVIDERS = ["gemini", "gemini-3.1-lite", "groq-low", "claude-haiku"]
FLOW_PAUSE = {"gemini": 8.0, "gemini-3.1-lite": 8.0, "groq": 45.0, "groq-low": 45.0}


def with_waits(action, provider: str):
    """Ejecuta `action()`, esperando ante límites de uso y errores temporales del proveedor."""
    waited = 0.0
    for _ in range(MAX_WAITS):
        try:
            return action(), waited
        except LLMRateLimited as err:
            pause, reason = err.retry_after or DEFAULT_WAIT, "límite de uso"
        except LLMUnavailable as err:
            if not err.transient:
                raise
            pause, reason = TRANSIENT_WAIT, "error temporal del proveedor"
        print(f"    {reason}: espero {pause:.0f} s")
        time.sleep(pause)
        waited += pause
    raise LLMUnavailable(f"{provider}: sigue sin responder tras {MAX_WAITS} esperas")


def _dump(result):
    return result.data.model_dump() if result and result.data else None


def answer_record(case, provider, run, assisted, waited, error) -> dict:
    """Todo lo de una corrida, para revisar o recalcular sin volver a llamar."""
    a = assisted
    return {
        "provider": provider, "run": run, "case": case.id, "error": error, "waited": waited,
        "understood": _dump(a.understood) if a else None,
        "found": ({c: [[r.repo.full_name, round(r.score, 3)] for r in f]
                   for c, f in a.found.items()} if a else {}),
        "draft": _dump(a.generated) if a else None,
        "response": a.response.model_dump(mode="json") if a and a.response else None,
        "problems": {"understand": a.understood.problems_first if a and a.understood else [],
                     "generate": a.generated.problems_first if a and a.generated else []},
    }


def render_review(answers, providers, cases) -> list[str]:
    """Los mapas de la corrida 1, completos, para leerlos con la rúbrica."""
    lines = ["## Para revisar a mano (corrida 1)", "",
             "Rúbrica de 1 a 3: español · `rationale` ligado al negocio · coherencia "
             "(título, resumen y cajas dicen lo mismo).", ""]
    first = {(a["provider"], a["case"]): a for a in answers if a["run"] == 1}
    for case in cases:
        lines += [f"### `{case.id}`", "", f"> {case.query}", ""]
        for p in providers:
            a = first.get((p, case.id))
            lines.append(f"**{p}**")
            if a is None or a["response"] is None:
                lines += [f"- sin respuesta: {a['error'] if a else 'no corrió'}", ""]
                continue
            r = a["response"]
            lines.append(f"- `{r['status']}` · {r['title'] or ''}")
            if r["summary"]:
                lines.append(f"- {r['summary']}")
            lines += [f"- **{c['label']}** (`{c['full_name']}`), {c['role']}: {c['rationale']}"
                      for c in r["components"]]
            lines += [f"- Limitación: {text}" for text in r["limitations"]]
            lines += [f"- Supuesto: {text}" for text in r["assumptions"]]
            lines += [f"- Pregunta: {text}" for text in r["clarification_questions"]]
            lines += ["- Rúbrica: español _ · rationale _ · coherencia _", ""]
    return lines


def render_report(providers, summaries, cold, outcomes, answers, cases, runs,
                  n_repos, min_score) -> str:
    def row(label, fmt):
        return f"| {label} | " + " | ".join(fmt(summaries[p]) for p in providers) + " |"

    lines = [
        "# Comparación de modelos · flujo completo del asistente",
        "",
        f"Generado con `python -m ai.eval.run_assistant_eval` el {date.today()} "
        f"a las {time.strftime('%H:%M')}. {len(cases)} casos × {runs} corridas por proveedor; "
        f"catálogo de {n_repos} repos; umbral {min_score}; el modelo ve {CANDIDATES_SHOWN} "
        f"candidatos por necesidad y se registran {CANDIDATES_LOGGED}. "
        "La llamada de calentamiento no se cuenta.",
        "",
        "## Modelos",
        "",
        "| Proveedor | Modelo | Razonamiento | Arranque en frío |",
        "|---|---|---|---|",
        *[f"| {p} | `{PROVIDERS[p].model}` | {PROVIDERS[p].reasoning_effort or 'por defecto'} "
          f"| {secs(cold[p])} |" for p in providers],
        "",
        "## Resumen",
        "",
        "| Métrica | " + " | ".join(providers) + " |",
        "|---|" + "---|" * len(providers),
        row("Status correcto", lambda s: pct(s["status_ok"])),
        row("Respuesta válida", lambda s: pct(s["valid"])),
        row("Necesidades detectadas", lambda s: pct(s["detected"])),
        row("Techo de la búsqueda (top 3)", lambda s: pct(s["ceiling3"])),
        row("Techo con 5 candidatos", lambda s: pct(s["ceiling5"])),
        row("Eligió un aceptable (donde había)", lambda s: pct(s["chose_ok"])),
        row("Se abstuvo (donde no había)", lambda s: pct(s["declined_ok"])),
        row("Eligió el primer candidato", lambda s: pct(s["first_rank"])),
        row("Consistencia entre corridas", lambda s: pct(s["consistency"])),
        row("Entender válido al 1.er intento", lambda s: pct(s["understand_first_ok"])),
        row("Generar válido al 1.er intento", lambda s: pct(s["generate_first_ok"])),
        row("Limitaciones repetidas", lambda s: str(s["repeated_limitations"])),
        row("Ids en el texto", lambda s: str(s["ids_in_text"])),
        row("Errores del proveedor", lambda s: f"{s['errors']}/{s['flows']}"),
        row("Tiempo total (mediana)", lambda s: secs(s["median_seconds"])),
        row("Tiempo total (peor caso)", lambda s: secs(s["max_seconds"])),
        row(f"Sobre {BUDGET_SECONDS:.0f} s",
            lambda s: f"{s['over_budget']}/{s['flows'] - s['errors']}"),
        row("Entender · buscar · generar (mediana)",
            lambda s: f"{secs(s['median_understand'])} · {secs(s['median_search'])} · "
                      f"{secs(s['median_generate'])}"),
        row("Tokens entrada / salida (mediana)",
            lambda s: f"{num(s['median_input_tokens'])} / {num(s['median_output_tokens'])}"),
        row("Esperas (límite de uso o error temporal)", lambda s: secs(s["waited"])),
        "",
        f"Evidencia direccional: {len(cases)} casos; los porcentajes no son estadística firme.",
        "",
        "## Por necesidad",
        "",
        "Cuenta sobre las corridas válidas: detectada · había un aceptable en el top 3 (techo) · "
        "eligió un aceptable. Sin aceptables, se espera que no elija nada.",
        "",
        "| Caso · necesidad | Aceptables | " + " | ".join(providers) + " |",
        "|---|---|" + "---|" * len(providers),
    ]

    grouped = defaultdict(list)
    for o in outcomes:
        if o.error is None:
            grouped[(o.provider, o.case_id)].append(o)
    for case in cases:
        if not case.needs:  # pedido vago: solo importa el status
            cells = [f"status ok {sum(o.status_ok for o in grouped[(p, case.id)])}"
                     f"/{len(grouped[(p, case.id)])}" for p in providers]
            lines.append(f"| `{case.id}` · (vago) | — | " + " | ".join(cells) + " |")
            continue
        for i, need in enumerate(case.needs):
            cells = []
            for p in providers:
                ns = [o.needs[i] for o in grouped[(p, case.id)]]
                det = f"det {sum(n.detected for n in ns)}/{len(ns)}"
                if need.acceptable:
                    cells.append(f"{det} · techo {sum(n.available3 for n in ns)} · "
                                 f"eligió {sum(n.chosen_ok for n in ns)}")
                else:
                    cells.append(f"{det} · eligió algo {sum(n.chosen is not None for n in ns)}")
            acceptable = ", ".join(a.split("/")[1] for a in need.acceptable) or "(ninguno)"
            lines.append(f"| `{case.id}` · {need.category} | {acceptable} | "
                         + " | ".join(cells) + " |")

    lines += ["", *render_review(answers, providers, cases)]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compara modelos con el flujo completo.")
    parser.add_argument("providers", nargs="*",
                        help="por defecto: " + ", ".join(DEFAULT_PROVIDERS))
    parser.add_argument("--runs", type=int, default=3)
    args = parser.parse_args()
    unknown = [p for p in args.providers if p not in PROVIDERS]
    if unknown:
        parser.error(f"proveedor desconocido: {', '.join(unknown)}")
    providers = args.providers or DEFAULT_PROVIDERS

    load_dotenv()
    print("Construyendo el índice del catálogo…")
    index = SearchIndex.build()
    min_score = embeddings.model_spec().min_score

    def buscar(query, k):
        return index.search(query, k)

    cases = [c for c in load_assistant_cases().cases if c.quick_set]
    outcomes, answers, cold = [], [], {}

    for provider in providers:
        print(f"{provider}: calentamiento")
        start = time.perf_counter()
        if not warm_up(provider):
            print("  no responde; se omite")
            continue
        cold[provider] = time.perf_counter() - start

        for run in range(1, args.runs + 1):
            for case in cases:
                try:
                    assisted, waited = with_waits(
                        lambda: asistir(case.query, buscar, min_score=min_score,
                                        provider=provider),
                        provider)
                    error = None
                except LLMError as err:
                    assisted, waited, error = None, 0.0, f"{type(err).__name__}: {err}"
                o = flow_outcome(case, provider, run, assisted, waited=waited, error=error)
                outcomes.append(o)
                answers.append(answer_record(case, provider, run, assisted, waited, error))
                print(f"  {provider} {run} {case.id:<24} {o.status or 'error':<20} "
                      f"{o.seconds:5.1f} s")
                time.sleep(FLOW_PAUSE.get(provider, 0))

    ran = [p for p in providers if p in cold]
    if not ran:
        print("Ningún proveedor respondió; no se escribe reporte.")
        return
    summaries = {p: summarize([o for o in outcomes if o.provider == p]) for p in ran}

    RESULTS_DIR.mkdir(exist_ok=True)
    name = f"assistant-{date.today()}"
    if ran != DEFAULT_PROVIDERS:
        name += "-" + "-".join(ran)
    stem = RESULTS_DIR / name
    stem.with_suffix(".md").write_text(
        render_report(ran, summaries, cold, outcomes, answers, cases, args.runs,
                      len(index.repos), min_score),
        encoding="utf-8")
    stem.with_suffix(".json").write_text(
        json.dumps(answers, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Reporte: {stem.with_suffix('.md')}")


if __name__ == "__main__":
    main()
