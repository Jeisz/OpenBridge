"""Métricas del flujo completo del asistente contra los casos (funciones puras).

Por cada necesidad esperada separa tres causas de fallo: entender no la detectó,
la búsqueda no trajo un repo aceptable (techo) o el modelo no lo eligió.
"""

from collections import defaultdict
from dataclasses import dataclass
from statistics import median

from ai.assistant import CANDIDATES_SHOWN, Assisted
from ai.catalog import load_categories
from ai.eval.assistant_cases import AssistantCase

BUDGET_SECONDS = 15.0  # presupuesto de la IA; el frontend espera 20 s


@dataclass(frozen=True)
class NeedOutcome:
    """Una necesidad esperada del caso, en una corrida."""

    category: str
    detected: bool            # entender la detectó
    wants_tool: bool          # el caso acepta al menos un repo para ella
    available3: bool          # había un aceptable entre los candidatos que vio el modelo
    available5: bool          # ... entre los 5 primeros de la búsqueda
    chosen: str | None        # repo elegido (None = sin caja o descartada)
    chosen_rank: int | None   # puesto del elegido entre los candidatos (1 = el primero)
    chosen_ok: bool           # el elegido está entre los aceptables


@dataclass(frozen=True)
class FlowOutcome:
    """Lo que hizo un proveedor con un caso, en una corrida del flujo completo."""

    case_id: str
    provider: str
    run: int
    expected_status: str
    status: str | None                # None = sin respuesta válida
    needs: tuple[NeedOutcome, ...]
    understand_first_ok: bool
    generate_first_ok: bool | None    # None = no hizo falta generar
    repeated_limitations: int         # del modelo, que repiten una necesidad sin herramientas
    ids_in_text: bool                 # algún texto para el usuario trae un id entre corchetes
    understand_seconds: float
    search_seconds: float
    generate_seconds: float
    input_tokens: int
    output_tokens: int
    waited: float = 0.0
    error: str | None = None

    @property
    def seconds(self) -> float:
        return self.understand_seconds + self.search_seconds + self.generate_seconds

    @property
    def status_ok(self) -> bool:
        return self.status == self.expected_status


def _chosen(assisted: Assisted) -> dict[str, str | None]:
    """Repo elegido por necesidad, según el borrador del modelo."""
    generated = assisted.generated
    if generated is None or generated.data is None or generated.problems_final:
        return {}
    return {box.need: box.full_name for box in generated.data.boxes}


def _user_texts(response) -> list[str]:
    """Todos los textos que ve el usuario en la respuesta."""
    texts = [response.title or "", response.summary or "",
             *response.assumptions, *response.limitations]
    return texts + [t for c in response.components for t in (c.label, c.role, c.rationale)]


def flow_outcome(case: AssistantCase, provider: str, run: int, assisted: Assisted | None,
                 *, waited: float = 0.0, error: str | None = None) -> FlowOutcome:
    """Compara una corrida del flujo con lo esperado del caso."""
    understood = assisted.understood if assisted else None
    generated = assisted.generated if assisted else None
    response = assisted.response if assisted else None
    found = assisted.found if assisted else {}
    detected = ({n.category for n in understood.data.needs}
                if understood and understood.data else set())
    chosen = _chosen(assisted) if assisted else {}

    needs = []
    for need in case.needs:
        names = [r.repo.full_name for r in found.get(need.category, [])]
        pick = chosen.get(need.category)
        needs.append(NeedOutcome(
            category=need.category,
            detected=need.category in detected,
            wants_tool=bool(need.acceptable),
            available3=any(n in need.acceptable for n in names[:CANDIDATES_SHOWN]),
            available5=any(n in need.acceptable for n in names),
            chosen=pick,
            chosen_rank=names.index(pick) + 1 if pick in names else None,
            chosen_ok=pick in need.acceptable,
        ))

    categories = load_categories()
    missing = [categories[c].name.lower() for c, f in found.items() if not f]
    other = generated.data.other_limitations if generated and generated.data else []
    return FlowOutcome(
        case_id=case.id,
        provider=provider,
        run=run,
        expected_status=case.expected_status,
        status=response.status if response else None,
        needs=tuple(needs),
        understand_first_ok=bool(understood and not understood.problems_first),
        generate_first_ok=None if generated is None else not generated.problems_first,
        repeated_limitations=sum(any(m in lim.lower() for m in missing) for lim in other),
        ids_in_text=response is not None and any(
            f"[{c}]" in text for text in _user_texts(response) for c in categories),
        understand_seconds=understood.seconds if understood else 0.0,
        search_seconds=assisted.search_seconds if assisted else 0.0,
        generate_seconds=generated.seconds if generated else 0.0,
        input_tokens=(understood.input_tokens if understood else 0)
                     + (generated.input_tokens if generated else 0),
        output_tokens=(understood.output_tokens if understood else 0)
                      + (generated.output_tokens if generated else 0),
        waited=waited,
        error=error,
    )


def consistency(outcomes: list[FlowOutcome]) -> float | None:
    """Parte de los casos en que todas las corridas dieron el mismo status y los mismos repos."""
    by_case = defaultdict(list)
    for o in outcomes:
        if o.error is None:
            picks = tuple(sorted((n.category, n.chosen or "") for n in o.needs))
            by_case[o.case_id].append((o.status, picks))
    repeated = [runs for runs in by_case.values() if len(runs) > 1]
    if not repeated:
        return None
    return sum(len(set(runs)) == 1 for runs in repeated) / len(repeated)


def summarize(outcomes: list[FlowOutcome]) -> dict:
    """Resumen de un proveedor. Las corridas con error del proveedor se cuentan aparte."""
    ok = [o for o in outcomes if o.error is None]
    needs = [n for o in ok for n in o.needs]
    tool_needs = [n for n in needs if n.wants_tool and n.detected]
    available = [n for n in tool_needs if n.available3]
    unavailable = [n for n in needs if n.detected and not n.available3]
    chosen = [n for n in needs if n.chosen]
    generated = [o for o in ok if o.generate_first_ok is not None]

    def ratio(part, whole):
        return part / whole if whole else None

    def med(values):
        values = list(values)
        return median(values) if values else None

    return {
        "flows": len(outcomes),
        "errors": len(outcomes) - len(ok),
        "status_ok": ratio(sum(o.status_ok for o in ok), len(ok)),
        "valid": ratio(sum(o.status is not None for o in ok), len(ok)),
        "understand_first_ok": ratio(sum(o.understand_first_ok for o in ok), len(ok)),
        "generate_first_ok": ratio(sum(o.generate_first_ok for o in generated), len(generated)),
        "detected": ratio(sum(n.detected for n in needs), len(needs)),
        "ceiling3": ratio(len(available), len(tool_needs)),
        "ceiling5": ratio(sum(n.available5 for n in tool_needs), len(tool_needs)),
        "chose_ok": ratio(sum(n.chosen_ok for n in available), len(available)),
        "declined_ok": ratio(sum(n.chosen is None for n in unavailable), len(unavailable)),
        "first_rank": ratio(sum(n.chosen_rank == 1 for n in chosen), len(chosen)),
        "repeated_limitations": sum(o.repeated_limitations for o in ok),
        "ids_in_text": sum(o.ids_in_text for o in ok),
        "consistency": consistency(ok),
        "median_seconds": med(o.seconds for o in ok),
        "max_seconds": max((o.seconds for o in ok), default=None),
        "over_budget": sum(o.seconds > BUDGET_SECONDS for o in ok),
        "median_understand": med(o.understand_seconds for o in ok),
        "median_search": med(o.search_seconds for o in ok),
        "median_generate": med(o.generate_seconds for o in generated),
        "median_input_tokens": med(o.input_tokens for o in ok),
        "median_output_tokens": med(o.output_tokens for o in ok),
        "waited": sum(o.waited for o in outcomes),
    }
