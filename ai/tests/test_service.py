"""Tests del servicio HTTP del asistente: sin red, sin modelo de embeddings, sin .env."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ai import assistant, llm
from ai.assistant import Assisted
from ai.llm import LLMRateLimited, LLMTimeout, LLMUnavailable
from ai.service.app import Catalog, create_app
from ai.service.settings import DEFAULT_CORS_ORIGINS, Settings

QUERY = {"query": "Necesito cobrar suscripciones mensuales a mis clientes."}
FRONTEND = "http://localhost:4173"


def fake_catalog() -> Catalog:
    return Catalog(buscar=lambda query, k: [], min_score=0.19, repos=3, embedding_model="falso")


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(llm, "_open_until", {})
    monkeypatch.setenv("AI_LLM_PROVIDER", "gemini")
    monkeypatch.setenv("AI_LLM_FALLBACK", "groq-low,claude-haiku")
    monkeypatch.setenv("GEMINI_API_KEY", "clave-falsa")
    monkeypatch.setenv("GROQ_API_KEY", "clave-falsa")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    app = create_app(load=fake_catalog, settings=Settings(cors_origins=(FRONTEND,)))
    with TestClient(app) as c:      # el "with" ejecuta el arranque (lifespan)
        yield c


def answers(monkeypatch, result=None, error=None):
    """Reemplaza asistir(): devuelve `result` o lanza `error`."""
    def fake_asistir(request, buscar, **kwargs):
        if error is not None:
            raise error
        return result
    monkeypatch.setattr(assistant, "asistir", fake_asistir)


# --- Salud ---

def test_salud_muestra_la_cadena_y_los_desconectados_sin_claves(client):
    llm._open_until["gemini"] = llm.time.monotonic() + 3600   # desconectado una hora
    body = client.get("/health").json()
    assert body["repos"] == 3 and body["status"] == "ok"
    assert [x["provider"] for x in body["llm"]] == ["gemini", "groq-low"]   # Claude sin clave
    assert body["llm"][0]["disconnected_seconds"] is not None
    assert body["llm"][1]["disconnected_seconds"] is None
    assert "clave-falsa" not in str(body)


def test_salud_dice_de_cuando_es_el_catalogo(monkeypatch):
    monkeypatch.setenv("AI_LLM_PROVIDER", "gemini")
    monkeypatch.setenv("AI_LLM_FALLBACK", "")
    taken = "2026-10-29T20:42:17+00:00"
    load = lambda: Catalog(buscar=lambda query, k: [], min_score=0.19, repos=3,
                           embedding_model="falso", catalog_taken_at=taken)
    with TestClient(create_app(load=load, settings=Settings(cors_origins=(FRONTEND,)))) as c:
        assert c.get("/health").json()["catalog_taken_at"] == taken


# --- Pedido ---

def test_respuesta_valida(client, monkeypatch):
    answers(monkeypatch, Assisted(response=assistant.clarification_response(["¿Qué vende?"])))
    r = client.post("/assistant", json=QUERY)
    assert r.status_code == 200
    assert r.json()["status"] == "needs_clarification"


@pytest.mark.parametrize("payload", [{"query": "muy corta"}, {"pregunta": "x" * 30}, {}])
def test_pregunta_invalida_responde_con_el_contrato(client, payload):
    r = client.post("/assistant", json=payload)
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "invalid_query"


@pytest.mark.parametrize("error, status, code", [
    (LLMTimeout("x"), 504, "timeout"),
    (LLMRateLimited("x"), 503, "provider_unavailable"),
    (LLMUnavailable("x", status_code=500), 503, "provider_unavailable"),
])
def test_errores_del_modelo(client, monkeypatch, error, status, code):
    answers(monkeypatch, error=error)
    r = client.post("/assistant", json=QUERY)
    assert (r.status_code, r.json()["error"]["code"]) == (status, code)


def test_sin_respuesta_valida_es_502(client, monkeypatch):
    answers(monkeypatch, Assisted(response=None))
    r = client.post("/assistant", json=QUERY)
    assert (r.status_code, r.json()["error"]["code"]) == (502, "invalid_response")


# --- CORS ---

def test_cors_acepta_el_frontend_y_no_otros(client):
    headers = {"Access-Control-Request-Method": "POST"}
    ok = client.options("/assistant", headers={**headers, "Origin": FRONTEND})
    other = client.options("/assistant", headers={**headers, "Origin": "http://otro.test"})
    assert ok.headers.get("access-control-allow-origin") == FRONTEND
    assert "access-control-allow-origin" not in other.headers


def test_origenes_desde_el_entorno(monkeypatch):
    monkeypatch.delenv("AI_CORS_ORIGINS", raising=False)
    assert Settings.from_env().cors_origins == DEFAULT_CORS_ORIGINS
    monkeypatch.setenv("AI_CORS_ORIGINS", "http://a.test, http://b.test")
    assert Settings.from_env().cors_origins == ("http://a.test", "http://b.test")


# --- Frontera entre núcleo y servicio ---

def test_el_nucleo_no_importa_del_servicio():
    ai_dir = Path(__file__).resolve().parents[1]
    core = [p for p in ai_dir.glob("*.py")]          # assistant.py, llm.py, search.py, ...
    offenders = [p.name for p in core if "ai.service" in p.read_text(encoding="utf-8")]
    assert not offenders, f"el núcleo no debe depender del servicio: {offenders}"


def test_cuerpo_ilegible_responde_con_el_contrato(client):
    # "librería" en cp1252, no en UTF-8: lo que puede mandar una terminal de Windows.
    body = '{"query": "Una librería pequeña quiere vender libros en línea."}'.encode("cp1252")
    r = client.post("/assistant", content=body, headers={"Content-Type": "application/json"})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "invalid_query"


def test_ruta_inexistente_sigue_como_fastapi(client):
    assert client.get("/no-existe").status_code == 404
