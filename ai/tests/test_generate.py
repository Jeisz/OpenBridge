"""Tests del paso de generar (sin red): mensaje, esquema, reglas y respuesta."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from ai import assistant
from ai.catalog import load_repos
from ai.llm import Generation, LLMInvalidResponse
from ai.search import SearchResult

NOW = datetime(2026, 11, 2, tzinfo=timezone.utc)
REQUEST = "Propón un RAG privado para consultar documentos con permisos de acceso."
# Repos que están en los datos de ejemplo y en el snapshot: el test sirve con los dos.
REPOS = {r.full_name: r for r in load_repos()}
AI_NAMES = ["run-llama/llama_index", "langchain-ai/langchain", "ollama/ollama"]


def result(repo):
    return SearchResult(repo=repo, score=0.3, license_unconfirmed=False, health_unknown=True)


CANDIDATES = {"ai": [result(REPOS[n]) for n in AI_NAMES],
              "cache": [result(REPOS["redis/redis"])]}


def needs(*categories):
    """Necesidades de entender, escritas a mano."""
    return assistant.understanding_schema()(
        needs=[{"category": c, "query": f"consulta de {c}", "evidence": "fragmento"}
               for c in categories],
        clarification_questions=[]).needs


def box(full_name="run-llama/llama_index", need="ai"):
    return {"need": need, "full_name": full_name, "label": "Herramienta",
            "role": "Rol", "rationale": "Razón."}


def draft(boxes, links=(), title="RAG privado", other=()):
    """Un borrador con el esquema de un pedido con IA y caché."""
    schema = assistant.draft_schema(["ai", "cache"], AI_NAMES + ["redis/redis"])
    return schema(title=title, summary="Resumen.", boxes=list(boxes), links=list(links),
                  assumptions=[], other_limitations=list(other))


VALID = [box(), box("redis/redis", need="cache")]


# --- Lo que ve el modelo ---

def test_candidato_sin_licencia_identificada_y_sin_puntaje():
    repo = REPOS["redis/redis"].model_copy(update={"license_spdx_id": "NOASSERTION"})
    line = assistant.candidate_line(result(repo), NOW)
    assert "licencia no identificada por GitHub" in line
    assert "0.3" not in line


def test_descripcion_larga_se_recorta():
    repo = REPOS["redis/redis"].model_copy(update={"description": "palabra " * 60})
    description = assistant.candidate_line(result(repo), NOW).split(" · ")[1]
    assert description.endswith("…")
    assert len(description) <= assistant.DESCRIPTION_CHARS + 1


def test_mensaje_con_ids_y_necesidades_sin_herramientas():
    message = assistant.map_message(REQUEST, needs("ai", "auth"), {"ai": CANDIDATES["ai"]}, NOW)
    assert "[ai]" in message
    assert "run-llama/llama_index" in message
    assert message.rstrip().endswith("[auth] Autenticación.")


# --- Esquema del borrador ---

def test_esquema_rechaza_repos_que_no_son_candidatos():
    with pytest.raises(ValidationError):
        draft([box("stripe/stripe-python")])


def test_esquema_acepta_ninguno():
    assert draft([box(None)]).boxes[0].full_name is None


# --- Reglas que el esquema no expresa ---

@pytest.mark.parametrize("boxes, title, expected", [
    (VALID, "RAG privado", None),
    ([box("redis/redis"), box("redis/redis", need="cache")], "RAG privado", "no es candidato de ai"),
    ([box()], "RAG privado", "faltan cajas para: cache"),
    ([box(), box("langchain-ai/langchain"), box("redis/redis", need="cache")],
     "RAG privado", "más de una caja"),
    (VALID, "x" * 81, "el máximo es 80"),
])
def test_reglas_del_borrador(boxes, title, expected):
    problems = assistant.draft_problems(draft(boxes, title=title), CANDIDATES)
    if expected is None:
        assert problems == []
    else:
        assert any(expected in p for p in problems)


# --- Respuesta del contrato ---

def test_caja_descartada_conexion_invalida_y_necesidad_sin_candidatos():
    d = draft([box(), box(None, need="cache")],
              links=[{"from_need": "ai", "to_need": "cache", "protocol": "REST",
                      "description": "consulta"}],
              other=["Otra limitación."])
    response = assistant.to_response(d, needs("ai", "cache", "auth"), CANDIDATES)
    assert response.status == "ok"
    assert [c.full_name for c in response.components] == ["run-llama/llama_index"]
    assert response.connections == []        # apuntaba a la caja descartada
    assert response.limitations[0].startswith("Caché: ninguna herramienta")
    assert response.limitations[1].startswith("Autenticación: el catálogo no tiene")
    assert response.limitations[-1] == "Otra limitación."


def test_si_descarta_todo_queda_sin_evidencia():
    response = assistant.to_response(draft([box(None), box(None, need="cache")]),
                                     needs("ai", "cache"), CANDIDATES)
    assert response.status == "no_evidence"
    assert response.components == []


def test_plantillas_cumplen_el_contrato():
    assert assistant.clarification_response(["¿Qué vende tu negocio?"]).status == "needs_clarification"
    response = assistant.no_evidence_response(needs("payments", "auth"))
    assert response.status == "no_evidence"
    assert len(response.limitations) == 2


# --- generar_mapa ---

def test_sin_candidatos_no_llama_al_modelo():
    with pytest.raises(ValueError, match="no_evidence_response"):
        assistant.generar_mapa(REQUEST, needs("auth"), {})


def test_reintenta_si_elige_un_repo_de_otra_necesidad(monkeypatch):
    replies = [draft([box("redis/redis"), box("redis/redis", need="cache")]), draft(VALID)]
    calls = []

    def fake_generar(messages, *, schema=None, provider=None, deadline=None):
        calls.append(messages)
        reply = replies[len(calls) - 1]
        return Generation(text=reply.model_dump_json(), provider="fake", model="fake",
                          seconds=0.1, input_tokens=100, output_tokens=10, data=reply)

    monkeypatch.setattr(assistant, "generar", fake_generar)
    response, result_ = assistant.generar_mapa(REQUEST, needs("ai", "cache"), CANDIDATES)

    assert result_.attempts == 2
    assert "no es candidato de ai" in result_.problems_first[0]
    assert response is not None and response.status == "ok"


def test_esquema_fijo_acepta_cualquier_texto_y_las_reglas_lo_revisan():
    schema = assistant.draft_schema(["ai", "cache"], None)
    d = schema(title="RAG", summary="Resumen.",
               boxes=[box("stripe/stripe-python"), box("redis/redis", need="cache")],
               links=[], assumptions=[], other_limitations=[])
    problems = assistant.draft_problems(d, CANDIDATES)
    assert any("no es candidato de ai" in p for p in problems)


def test_formato_rechazado_reintenta_con_los_valores_validos(monkeypatch):
    # Algunos proveedores rechazan el JSON con un error técnico que no dice qué valores
    # eran válidos: el reintento debe decirlos, por necesidad, incluido null.
    rejected = LLMInvalidResponse("no cumple", raw_text='{"boxes": []}',
                                  detail="expected null, but got string")
    replies = [rejected, draft(VALID)]
    calls = []

    def fake_generar(messages, *, schema=None, provider=None, deadline=None):
        calls.append(list(messages))
        reply = replies[len(calls) - 1]
        if isinstance(reply, Exception):
            raise reply
        return Generation(text=reply.model_dump_json(), provider="fake", model="fake",
                          seconds=0.1, input_tokens=100, output_tokens=10, data=reply)

    monkeypatch.setattr(assistant, "generar", fake_generar)
    response, result_ = assistant.generar_mapa(REQUEST, needs("ai", "cache"), CANDIDATES)

    retry = calls[1][-1]["content"]  # el mensaje del reintento
    assert "ai: run-llama/llama_index" in retry and "cache: redis/redis" in retry
    assert "o null" in retry
    assert result_.attempts == 2
    assert response is not None and response.status == "ok"
