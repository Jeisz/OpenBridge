"""Tests del flujo del asistente (sin red ni modelo de embeddings)."""

import pytest

from ai import assistant
from ai.assistant import LLMResult
from ai.catalog import load_repos
from ai.search import SearchResult
from ai.llm import (LLMConfigError, LLMInvalidResponse, LLMRateLimited, LLMTimeout,
                    LLMUnavailable)

REPO = load_repos()[0]
REQUEST = "Necesito cobrar suscripciones mensuales a los clientes de mi software."


def results(*scores):
    """Resultados de búsqueda con estos puntajes (el repo da igual aquí)."""
    return [SearchResult(repo=REPO, score=s, license_unconfirmed=False, health_unknown=True)
            for s in scores]


def understood(needs=(), questions=(), problems=()):
    """Una respuesta de entender, escrita a mano."""
    data = assistant.understanding_schema()(
        needs=[{"category": c, "query": f"consulta de {c}", "evidence": "fragmento"}
               for c in needs],
        clarification_questions=list(questions))
    return LLMResult(data=data, attempts=1, problems_final=list(problems))


@pytest.fixture
def received(monkeypatch):
    """Simula generar_mapa y guarda los candidatos que recibe."""
    log = []

    def fake_generar_mapa(request, needs, candidates, *, provider=None, deadline=None):
        log.append(candidates)
        return "mapa", LLMResult(attempts=1)

    monkeypatch.setattr(assistant, "generar_mapa", fake_generar_mapa)
    return log


@pytest.fixture
def deadlines(monkeypatch):
    """Simula generar_mapa y guarda la fecha límite que recibe."""
    seen = []

    def fake_generar_mapa(request, needs, candidates, *, provider=None, deadline=None):
        seen.append(deadline)
        return "mapa", LLMResult(attempts=1)

    monkeypatch.setattr(assistant, "generar_mapa", fake_generar_mapa)
    return seen


def understands(monkeypatch, result):
    monkeypatch.setattr(assistant, "entender",
                        lambda request, provider=None, deadline=None: result)


def test_pedido_vago_no_busca_ni_genera(monkeypatch, received):
    understands(monkeypatch, understood(questions=["¿Qué vende tu negocio?"]))
    out = assistant.asistir(REQUEST, lambda q, k: pytest.fail("no debe buscar"), min_score=0.2)
    assert out.response.status == "needs_clarification"
    assert received == [] and out.generated is None


def test_sin_candidatos_sobre_el_umbral_no_genera(monkeypatch, received):
    understands(monkeypatch, understood(["payments"]))
    out = assistant.asistir(REQUEST, lambda q, k: results(0.19, 0.1), min_score=0.2)
    assert out.response.status == "no_evidence"
    assert out.found == {"payments": []}
    assert received == []


def test_registra_cinco_y_el_modelo_ve_los_que_indica_la_constante(monkeypatch, received):
    understands(monkeypatch, understood(["payments"]))
    asked = []

    def buscar(query, k):
        asked.append(k)
        return results(0.5, 0.4, 0.3, 0.25, 0.21)[:k]

    out = assistant.asistir(REQUEST, buscar, min_score=0.2)
    assert asked == [assistant.CANDIDATES_LOGGED]
    assert len(out.found["payments"]) == 5
    assert len(received[0]["payments"]) == assistant.CANDIDATES_SHOWN
    assert out.response == "mapa"


def test_puntaje_igual_al_umbral_pasa(monkeypatch, received):
    understands(monkeypatch, understood(["payments"]))
    out = assistant.asistir(REQUEST, lambda q, k: results(0.2), min_score=0.2)
    assert len(out.found["payments"]) == 1
    assert len(received) == 1


def test_entender_invalido_no_sigue(monkeypatch, received):
    understands(monkeypatch, understood(["payments"], problems=["categoría repetida"]))
    out = assistant.asistir(REQUEST, lambda q, k: pytest.fail("no debe buscar"), min_score=0.2)
    assert out.response is None and out.found == {} and received == []


def test_con_presupuesto_pasa_una_fecha_limite(monkeypatch, deadlines):
    understands(monkeypatch, understood(["payments"]))
    assistant.asistir(REQUEST, lambda q, k: results(0.5), min_score=0.2)
    left = deadlines[0].remaining()
    assert 0 < left <= assistant.BUDGET_SECONDS


def test_sin_presupuesto_no_hay_fecha_limite(monkeypatch, deadlines):
    understands(monkeypatch, understood(["payments"]))
    assistant.asistir(REQUEST, lambda q, k: results(0.5), min_score=0.2, budget=None)
    assert deadlines == [None]


@pytest.mark.parametrize("err, status, code", [
    (None, 502, "invalid_response"),                                   # sin respuesta válida
    (LLMInvalidResponse("x", raw_text="", detail="d"), 502, "invalid_response"),
    (LLMTimeout("x"), 504, "timeout"),
    (LLMRateLimited("x"), 503, "provider_unavailable"),
    (LLMUnavailable("x", status_code=500), 503, "provider_unavailable"),
    (LLMConfigError("x"), 503, "provider_unavailable"),               # falta la clave
])
def test_errores_a_codigos_del_contrato(err, status, code):
    got_status, body = assistant.error_response(err)
    assert (got_status, body.error.code) == (status, code)
