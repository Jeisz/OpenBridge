"""Métricas del paso de entender contra los casos del asistente.

Compara las necesidades detectadas con las esperadas de cada caso y resume
por proveedor. Funciones puras: no llaman al modelo.
"""

from collections import defaultdict
from dataclasses import dataclass
from statistics import median

from ai.assistant import Understood
from ai.eval.assistant_cases import AssistantCase

QUERY_WORDS = (3, 8)  # largo de consulta que pide el prompt


def normalize(text: str) -> str:
    """Minúsculas y espacios simples, para comparar fragmentos de texto."""
    return " ".join(text.lower().split())


def evidence_is_literal(evidence: str, request: str) -> bool:
    """El fragmento aparece en el pedido, sin contar mayúsculas, espacios ni comillas."""
    fragment = normalize(evidence).strip(" .,;:\"'«»")
    return bool(fragment) and fragment in normalize(request)


def query_length_ok(query: str) -> bool:
    low, high = QUERY_WORDS
    return low <= len(query.split()) <= high


@dataclass(frozen=True)
class CaseOutcome:
    """Lo que hizo un proveedor con un caso, en una corrida."""

    case_id: str
    provider: str
    run: int
    expected: frozenset[str]
    detected: frozenset[str]
    asked: bool                  # devolvió preguntas de aclaración
    valid_first: bool
    valid_final: bool
    literal_evidence: int        # necesidades con evidencia literal
    short_queries: int           # necesidades con consulta de largo correcto
    seconds: float
    input_tokens: int
    output_tokens: int
    waited: float = 0.0          # segundos de espera por límite de uso
    error: str | None = None     # error del proveedor: tiempo, conexión…

    @property
    def vague(self) -> bool:
        return not self.expected

    @property
    def found(self) -> frozenset[str]:
        return self.expected & self.detected

    @property
    def invented(self) -> frozenset[str]:
        return self.detected - self.expected

    @property
    def exact(self) -> bool:
        """Mismas necesidades y pregunta solo si el pedido es vago."""
        return self.detected == self.expected and self.asked == self.vague


def case_outcome(case: AssistantCase, provider: str, run: int,
                 understood: Understood | None, *, waited: float = 0.0,
                 error: str | None = None) -> CaseOutcome:
    """Compara una respuesta de entender con lo esperado del caso."""
    data = understood.data if understood else None
    needs = data.needs if data else []
    return CaseOutcome(
        case_id=case.id,
        provider=provider,
        run=run,
        expected=frozenset(n.category for n in case.needs),
        detected=frozenset(n.category for n in needs),
        asked=bool(data and data.clarification_questions),
        valid_first=bool(understood and not understood.problems_first),
        valid_final=bool(data is not None and not understood.problems_final),
        literal_evidence=sum(evidence_is_literal(n.evidence, case.query) for n in needs),
        short_queries=sum(query_length_ok(n.query) for n in needs),
        seconds=understood.seconds if understood else 0.0,
        input_tokens=understood.input_tokens if understood else 0,
        output_tokens=understood.output_tokens if understood else 0,
        waited=waited,
        error=error,
    )


def consistency(outcomes: list[CaseOutcome]) -> float | None:
    """Parte de los casos en que todas las corridas detectaron lo mismo."""
    by_case = defaultdict(list)
    for o in outcomes:
        if o.error is None:
            by_case[o.case_id].append(o.detected)
    repeated = [runs for runs in by_case.values() if len(runs) > 1]
    if not repeated:
        return None
    return sum(len(set(runs)) == 1 for runs in repeated) / len(repeated)


def summarize(outcomes: list[CaseOutcome]) -> dict:
    """Resumen de un proveedor. Las llamadas con error del proveedor se cuentan aparte."""
    ok = [o for o in outcomes if o.error is None]
    clear = [o for o in ok if not o.vague]
    vague = [o for o in ok if o.vague]
    expected = sum(len(o.expected) for o in clear)
    needs = sum(len(o.detected) for o in ok)
    times = [o.seconds for o in ok]

    def ratio(part, whole):
        return part / whole if whole else None

    return {
        "calls": len(outcomes),
        "errors": len(outcomes) - len(ok),
        "valid_first": ratio(sum(o.valid_first for o in ok), len(ok)),
        "valid_final": ratio(sum(o.valid_final for o in ok), len(ok)),
        "exact": ratio(sum(o.exact for o in ok), len(ok)),
        "recall": ratio(sum(len(o.found) for o in clear), expected),
        "invented": sum(len(o.invented) for o in clear),
        "vague_ok": f"{sum(o.exact for o in vague)}/{len(vague)}",
        "asked_when_clear": sum(o.asked for o in clear),
        "literal_evidence": ratio(sum(o.literal_evidence for o in ok), needs),
        "short_queries": ratio(sum(o.short_queries for o in ok), needs),
        "consistency": consistency(outcomes),
        "median_seconds": median(times) if times else None,
        "max_seconds": max(times, default=None),
        "median_input_tokens": median(o.input_tokens for o in ok) if ok else None,
        "median_output_tokens": median(o.output_tokens for o in ok) if ok else None,
        "waited": sum(o.waited for o in outcomes),
    }
