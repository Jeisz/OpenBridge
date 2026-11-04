"""Métricas de la búsqueda contra el golden set: hit@k, MRR@k, recall@k y umbral."""

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class QueryOutcome:
    """Resultado de una consulta del golden set."""

    query_id: str
    expected_ranks: tuple[int | None, ...]    # Posición de cada esperado. None si no aparece.
    top_score: float

    @property
    def answerable(self) -> bool:
        return bool(self.expected_ranks)

    @property
    def rank(self) -> int | None:
        """Posición del primer esperado. None si no aparace ninguno"""
        found = [r for r in self.expected_ranks if r is not None]
        return min(found) if found else None


def expected_ranks(ranking: list[str], expected: list[str]) -> tuple[int | None, ...]:
    """Posición de cada repo esperado en el ranking, en el orden de `expected`."""
    positions = {full_name: pos for pos, full_name in enumerate(ranking, start=1)}
    return tuple(positions.get(e) for e in expected)


def summarize(outcomes: list[QueryOutcome], k: int) -> dict:
    """hit@k, MRR@k y recall@k sobre las consultas con respuesta.

    Las consultas sin respuesta no cuentan.
    """
    answered = [o for o in outcomes if o.answerable]
    if not answered:
        raise ValueError("no hay consultas con respuesta")
    n = len(answered)
    hits = [o.rank is not None and o.rank <= k for o in answered]
    reciprocal = [1 / o.rank if hit else 0.0 for o, hit in zip(answered, hits)]
    recall = [sum(r is not None and r <= k for r in o.expected_ranks) / len (o.expected_ranks)
              for o in answered
    ]
    return {"n": n,
            "hits": sum(hits),
            "hit_rate": sum(hits) / n,
            "mrr": sum(reciprocal) / n,
            "recall": sum(recall) / n,
}


def threshold_errors(outcomes: list[QueryOutcome],
                     min_score: float) -> tuple[list[str], list[str]]:
    """Errores de un umbral de no_evidence aplicado al 1.er resultado.

    Devuelve (con respuesta que se bloquearían, sin respuesta que pasarían).
    Un puntaje igual al umbral pasa.
    """
    blocked = [o.query_id for o in outcomes if o.answerable and o.top_score < min_score]
    leaked = [o.query_id for o in outcomes if not o.answerable and o.top_score >= min_score]
    return blocked, leaked


def suggest_min_score(outcomes: list[QueryOutcome], k: int) -> float | None:
    """Umbral de no_evidence según la regla de ai/eval/README.md.

    Solo cuentan las consultas con respuesta que la búsqueda resuelve (algún
    esperado en el top-k). Si se separan de las sin respuesta, el corte es el
    menor valor de dos decimales por encima de la mejor sin respuesta; si no,
    la peor resuelta redondeada hacia abajo. None si no hay ninguna resuelta.
    """
    resolved = [o.top_score for o in outcomes
                if o.answerable and o.rank is not None and o.rank <= k]
    if not resolved:
        return None
    worst = min(resolved)
    below_worst = math.floor(round(worst * 100, 6)) / 100
    unanswered = [o.top_score for o in outcomes if not o.answerable]
    if not unanswered:
        return round(below_worst, 2)
    above_best = (math.floor(round(max(unanswered) * 100, 6)) + 1) / 100
    return round(above_best if above_best <= worst else below_worst, 2)
