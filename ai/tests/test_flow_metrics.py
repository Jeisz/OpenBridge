"""Tests de las métricas del flujo completo (sin red)."""

from ai import assistant
from ai.assistant import Assisted, LLMResult
from ai.catalog import load_repos
from ai.eval.assistant_cases import load_assistant_cases
from ai.eval.flow_metrics import flow_outcome, mentions, summarize
from ai.search import SearchResult

CASE = {c.id: c for c in load_assistant_cases().cases}["pantalla-observabilidad"]
BASE = load_repos()[0]


def found(*names):
    """Resultados de búsqueda con estos nombres, en este orden."""
    return [SearchResult(repo=BASE.model_copy(update={"full_name": n}), score=0.3,
                         license_unconfirmed=False, health_unknown=True) for n in names]


def assisted(results, pick, other_limitations=(), title="Observabilidad", missing=(),
             rationale="Razón.", final_extra=(), fit=None):
    """Una corrida: entender detectó observability (más `missing`, sin candidatos)
    y el modelo eligió `pick`. La respuesta final la arma `to_response`, como en el flujo;
    `final_extra` agrega limitaciones a la respuesta final, para probar la métrica sola."""
    needs = [{"category": "observability", "query": "métricas y trazas",
              "evidence": "métricas, logs y trazas"}]
    needs += [{"category": c, "query": f"pedido de {c}", "evidence": c} for c in missing]
    understood = assistant.understanding_schema()(needs=needs, clarification_questions=[])
    names = [r.repo.full_name for r in results]
    draft = assistant.draft_schema(["observability"], names)(
        title=title, summary="Resumen.",
        boxes=[{"need": "observability", "fit_check": "Pide algo; el candidato hace algo.",
                "fit": fit or ("serves" if pick else "only_related"),
                "full_name": pick, "label": "Herramienta", "role": "Rol",
                "rationale": rationale}],
        links=[], assumptions=[], other_limitations=list(other_limitations))
    found_ = {"observability": results, **{c: [] for c in missing}}
    response = assistant.to_response(draft, understood.needs, found_, request=CASE.query)
    if final_extra:
        response = response.model_copy(
            update={"limitations": [*response.limitations, *final_extra]})
    return Assisted(response=response,
                    understood=LLMResult(data=understood, attempts=1, seconds=1.0),
                    generated=LLMResult(data=draft, attempts=1, seconds=2.0),
                    found=found_, search_seconds=0.1)


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


def test_id_entre_corchetes_en_el_texto():
    run = assisted(found("prometheus/prometheus"), "prometheus/prometheus",
                   title="Observabilidad [observability]")
    assert flow_outcome(CASE, "fake", 1, run).ids_in_text


def test_limitacion_repetida_cuenta_en_borrador_y_en_respuesta_final():
    repeated = "La autenticación no está cubierta."
    run = assisted(found("prometheus/prometheus"), "prometheus/prometheus",
                   other_limitations=[repeated, "Grafana podría complementar a Prometheus."],
                   missing=["auth"], final_extra=[repeated])
    o = flow_outcome(CASE, "fake", 1, run)
    assert o.repeated_draft == 1      # el modelo repitió la necesidad sin herramienta
    assert o.repeated_final == 1      # y llegó dos veces al usuario: la línea del sistema y la suya


def test_necesidad_descartada_por_el_modelo_cuenta_como_sin_herramienta():
    repeated = "Falta una herramienta de observabilidad."
    run = assisted(found("helm/helm"), None, other_limitations=[repeated],
                   final_extra=[repeated])
    o = flow_outcome(CASE, "fake", 1, run)
    assert o.repeated_draft == 1
    assert o.repeated_final == 1      # "Observabilidad: ninguna herramienta…" + la del modelo


def test_el_filtro_deja_la_respuesta_final_sin_repeticiones():
    run = assisted(found("prometheus/prometheus"), "prometheus/prometheus",
                   other_limitations=["La autenticación no está cubierta."], missing=["auth"])
    o = flow_outcome(CASE, "fake", 1, run)
    assert o.repeated_draft == 1      # el modelo sigue repitiendo en su borrador…
    assert o.repeated_final == 0      # …pero el usuario no lo ve


def test_sin_repeticion_la_respuesta_final_da_cero():
    run = assisted(found("prometheus/prometheus"), "prometheus/prometheus",
                   other_limitations=["Grafana podría complementar a Prometheus."],
                   missing=["auth", "payments"])
    o = flow_outcome(CASE, "fake", 1, run)
    assert o.repeated_draft == 0 and o.repeated_final == 0


def test_palabra_completa_y_sin_tildes():
    assert mentions("Falta la AUTENTICACION de usuarios.", "Autenticación")
    assert mentions("La IA del sistema queda fuera.", "IA")
    assert not mentions("La materia prima queda fuera.", "IA")
    assert mentions("Faltan las bases de datos.", "Bases de datos")


def test_textos_del_modelo_que_hablan_del_catalogo():
    run = assisted(found("prometheus/prometheus"), "prometheus/prometheus",
                   other_limitations=["ClickHouse no está en el catálogo."],
                   rationale="Es el candidato más mantenido.", missing=["auth"])
    o = flow_outcome(CASE, "fake", 1, run)
    # La línea del sistema ("Autenticación: no se encontraron…") no cuenta: no es del modelo.
    assert o.catalog_claims == 1


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


def test_solo_relacionado_cuenta_como_abstencion():
    run = assisted(found("helm/helm"), "helm/helm", fit="only_related")
    assert flow_outcome(CASE, "fake", 1, run).needs[0].chosen is None
