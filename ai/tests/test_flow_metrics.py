"""Tests de las métricas del flujo completo (sin red)."""

from ai import assistant
from ai.assistant import Assisted, LLMResult
from ai.catalog import load_repos
from ai.eval.assistant_cases import load_assistant_cases
from ai.eval.flow_metrics import flow_outcome, summarize
from ai.search import SearchResult

CASE = {c.id: c for c in load_assistant_cases().cases}["pantalla-observabilidad"]
BASE = load_repos()[0]


def found(*names):
    """Resultados de búsqueda con estos nombres, en este orden."""
    return [SearchResult(repo=BASE.model_copy(update={"full_name": n}), score=0.3,
                         license_unconfirmed=False, health_unknown=True) for n in names]


def assisted(results, pick, other_limitations=(), title="Observabilidad"):
    """Una corrida: entender detectó observability y el modelo eligió `pick`."""
    understood = assistant.understanding_schema()(
        needs=[{"category": "observability", "query": "métricas y trazas",
                "evidence": "métricas, logs y trazas"}],
        clarification_questions=[])
    names = [r.repo.full_name for r in results]
    draft = assistant.draft_schema(["observability"], names)(
        title=title, summary="Resumen.",
        boxes=[{"need": "observability", "full_name": pick, "label": "Herramienta",
                "role": "Rol", "rationale": "Razón."}],
        links=[], assumptions=[], other_limitations=list(other_limitations))
    response = assistant.to_response(draft, understood.needs, {"observability": results})
    return Assisted(response=response,
                    understood=LLMResult(data=understood, attempts=1, seconds=1.0),
                    generated=LLMResult(data=draft, attempts=1, seconds=2.0),
                    found={"observability": results}, search_seconds=0.1)


def test_aceptable_en_segundo_puesto_y_elegido():
    results = found("grafana/grafana", "prometheus/prometheus", "helm/helm")
    need = flow_outcome(CASE, "fake", 1, assisted(results, "prometheus/prometheus")).needs[0]
    assert need.detected and need.available3 and need.chosen_ok
    assert need.chosen_rank == 2


def test_aceptable_solo_en_el_cuarto_puesto():
    results = found("grafana/grafana", "helm/helm", "nginx/nginx",
                    "jaegertracing/jaeger", "vitejs/vite")
    need = flow_outcome(CASE, "fake", 1, assisted(results[:3], "grafana/grafana"),
                        shown=3).needs[0]
    assert not need.available3 and not need.chosen_ok
    o = flow_outcome(CASE, "fake", 1, Assisted(
        response=None, understood=assisted(results[:3], "grafana/grafana").understood,
        found={"observability": results}), shown=3)
    assert o.needs[0].available5 and not o.needs[0].available3


def test_limitacion_repetida_e_id_filtrado():
    run = assisted(found("prometheus/prometheus"), "prometheus/prometheus",
                   other_limitations=["La autenticación no está cubierta."],
                   title="Observabilidad [observability]")
    run.found["auth"] = []            # una necesidad sin herramientas
    o = flow_outcome(CASE, "fake", 1, run)
    assert o.repeated_limitations == 1
    assert o.ids_in_text


def test_resumen_separa_busqueda_y_modelo():
    good = assisted(found("prometheus/prometheus"), "prometheus/prometheus")
    wrong = assisted(found("prometheus/prometheus", "helm/helm"), "helm/helm")
    outcomes = [flow_outcome(CASE, "fake", 1, good),
                flow_outcome(CASE, "fake", 2, wrong),
                flow_outcome(CASE, "fake", 3, None, error="LLMTimeout")]
    s = summarize(outcomes)
    assert s["errors"] == 1
    assert s["ceiling3"] == 1.0       # en las dos corridas válidas había un aceptable
    assert s["chose_ok"] == 0.5       # lo eligió en una de las dos
    assert s["consistency"] == 0.0    # eligió distinto en cada corrida


def test_con_cinco_candidatos_el_cuarto_puesto_cuenta_como_visto():
    results = found("grafana/grafana", "helm/helm", "nginx/nginx",
                    "jaegertracing/jaeger", "vitejs/vite")
    run = assisted(results, "jaegertracing/jaeger")
    assert not flow_outcome(CASE, "fake", 1, run, shown=3).needs[0].available3   # con 3, no lo vio
    assert flow_outcome(CASE, "fake", 1, run, shown=5).needs[0].available3       # con 5, sí


def test_acierto_de_punta_a_punta_no_depende_de_k():
    results = found("grafana/grafana", "helm/helm", "nginx/nginx", "jaegertracing/jaeger")
    run = assisted(results, "jaegertracing/jaeger")
    for shown in (3, 5):
        s = summarize([flow_outcome(CASE, "fake", 1, run, shown=shown)])
        assert s["chose_ok_all"] == 1.0   # misma cuenta con cualquier k
