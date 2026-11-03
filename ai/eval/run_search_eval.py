"""Mide la búsqueda contra el golden set y escribe el reporte en ai/eval/results/.

Uso, desde la raíz del repo:
    python -m ai.eval.run_search_eval                  # catálogo real (snapshot)
    python -m ai.eval.run_search_eval --golden sample  # 20 repos de ejemplo
"""

import argparse
import time
from datetime import date

from ai import embeddings
from ai.eval.golden import (DEFAULT_GOLDEN,
                            EVAL_DIR,
                            GOLDEN_FILES,
                            SearchGoldenSet,
                            SearchQuery,
                            load_search_queries,)
from ai.eval.metrics import QueryOutcome, expected_ranks, summarize, threshold_errors
from ai.search import SearchIndex, SearchResult

K = 3
RESULTS_DIR = EVAL_DIR / "results"

# Nombre del reporte por golden set.
REPORT_PREFIX = {"catalog": "search-catalog", "sample": "search"}


def short(full_name: str) -> str:
    return full_name.split("/")[1]


def top_cell(results: list[SearchResult]) -> str:
    return " · ".join(f"{short(r.repo.full_name)} {r.score:.3f}" for r in results)


def render_report(model: str, min_score: float | None, golden_name: str,
                  golden: SearchGoldenSet, n_repos: int, summary: dict, times: dict,
                  rows: list[tuple[SearchQuery, list[SearchResult], QueryOutcome]]) -> str:
    taken = f" del {golden.catalog_taken_at:%Y-%m-%d}" if golden.catalog_taken_at else ""
    lines = [
        f"# Evaluación de la búsqueda · {model}",
        "",
        f"Generado con `python -m ai.eval.run_search_eval --golden {golden_name}` el {date.today()}. "
        f"Golden set `{golden_name}` v{golden.version} · catálogo `{golden.source}`{taken} · "
        f"{n_repos} repos · k = {K} · CPU.",
        "",
        "## Resumen",
        "",
        "| Métrica | Valor |",
        "|---|---|",
        f"| hit@{K} | {summary['hits']}/{summary['n']} ({summary['hit_rate']:.0%}) |",
        f"| MRR@{K} | {summary['mrr']:.2f} |",
        f"| recall@{K} | {summary['recall']:.0%} |",
        f"| Carga del modelo + primera consulta | {times['load']:.1f} s |",
        f"| Vectores del catálogo ({n_repos} repos) | {times['build']:.1f} s |",
        f"| Consulta (promedio) | {times['query']:.2f} s |",
        "",
        "## Consultas con respuesta",
        "",
        f"| Consulta | Acierto | Posición de cada esperado | Top-{K} (puntaje) |",
        "|---|---|---|---|",
    ]
    for q, top, outcome in rows:
        if q.answerable:
            hit = "✅" if outcome.rank is not None and outcome.rank <= K else "❌"
            positions = " · ".join(
                f"{short(e)} {r or '—'}" for e, r in zip(q.expected, outcome.expected_ranks)
            )
            lines.append(f"| `{q.id}` | {hit} | {positions} | {top_cell(top)} |")

    pair_rows = sorted((r for r in rows if r[0].pair), key=lambda r: r[0].pair)
    if pair_rows:
        lines += ["", "## Pares (deben dar resultados distintos)", "",
                  f"| Par | Consulta | Top-{K} |", "|---|---|---|"]
        for q, top, _ in pair_rows:
            lines.append(f"| {q.pair} | `{q.id}` | {top_cell(top)} |")

    lines += ["", "## Consultas sin respuesta (el puntaje del 1.º sirve para el umbral)", "",
              f"| Consulta | Top-{K} (puntaje) |", "|---|---|"]
    for q, top, _ in rows:
        if not q.answerable:
            lines.append(f"| `{q.id}` | {top_cell(top)} |")

    lines += ["", "## Umbral de `no_evidence`", ""]
    if min_score is None:
        lines.append("Sin calibrar para este modelo (`min_score = None`).")
    else:
        outcomes = [o for _, _, o in rows]
        answered = [o.top_score for o in outcomes if o.answerable]
        unanswered = [o.top_score for o in outcomes if not o.answerable]
        blocked, leaked = threshold_errors(outcomes, min_score)
        ids = lambda xs: ", ".join(f"`{x}`" for x in xs) or "—"
        lines += [
            f"Umbral: **{min_score:.3f}**. Si el 1.er resultado puntúa menos, "
            "la necesidad se responde como sin evidencia.",
            "",
            "| | Valor |",
            "|---|---|",
            f"| 1.er resultado, consultas con respuesta | {min(answered):.3f} – {max(answered):.3f} |",
            f"| 1.er resultado, consultas sin respuesta | {min(unanswered):.3f} – {max(unanswered):.3f} |",
            f"| Con respuesta bloqueadas (error grave) | {len(blocked)}/{len(answered)}: {ids(blocked)} |",
            f"| Sin respuesta que pasan (las puede frenar el LLM) | {len(leaked)}/{len(unanswered)}: {ids(leaked)} |",
        ]

    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Mide la búsqueda contra un golden set.")
    parser.add_argument("--golden", choices=sorted(GOLDEN_FILES), default=DEFAULT_GOLDEN,
                        help="golden set a medir (por defecto: %(default)s)")
    args = parser.parse_args(argv)

    golden = load_search_queries(args.golden)
    spec = embeddings.model_spec()
    model = spec.name

    start = time.perf_counter()
    embeddings.embed_query("calentamiento")      # carga el modelo
    load_s = time.perf_counter() - start

    start = time.perf_counter()
    index = SearchIndex.build(source=golden.source)   # el catálogo del golden set
    build_s = time.perf_counter() - start
    n_repos = len(index.repos)

    rows, outcomes, query_s = [], [], []
    for q in golden.queries:
        start = time.perf_counter()
        results = index.search(q.query, k=n_repos)   # ranking completo
        query_s.append(time.perf_counter() - start)
        outcome = QueryOutcome(q.id,
                               expected_ranks([r.repo.full_name for r in results], q.expected),
                               results[0].score,)
        rows.append((q, results[:K], outcome))
        outcomes.append(outcome)

    summary = summarize(outcomes, K)
    times = {"load": load_s, "build": build_s, "query": sum(query_s) / len(query_s)}

    RESULTS_DIR.mkdir(exist_ok=True)
    path = RESULTS_DIR / f"{REPORT_PREFIX[args.golden]}-{short(model).lower()}.md"
    path.write_text(render_report(model, spec.min_score, args.golden, golden, n_repos,
                                  summary, times, rows),
                    encoding="utf-8",)

    print(f"Modelo: {model} · golden set: {args.golden} · catálogo: {golden.source} ({n_repos} repos)")
    print(f"hit@{K}: {summary['hits']}/{summary['n']}  MRR@{K}: {summary['mrr']:.2f}  "
          f"recall@{K}: {summary['recall']:.0%}")
    print(f"Reporte: {path}")


if __name__ == "__main__":
    main()
