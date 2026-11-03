"""Tests de ai/assistant.py (entender) sin red: el modelo se simula."""

import pytest
from pydantic import ValidationError

from ai import assistant
from ai.catalog import load_categories
from ai.llm import Generation, LLMInvalidResponse


def understanding(needs=(), questions=()):
    """Una respuesta de entender, con valores de relleno."""
    schema = assistant.understanding_schema()
    return schema(needs=[{"category": c, "query": "consulta", "evidence": "fragmento"}
                         for c in needs],
                  clarification_questions=list(questions))


def fake_generar(replies):
    """Un generar() falso que responde en orden y guarda lo que recibió."""
    calls = []

    def generar(messages, *, schema=None, provider=None):
        calls.append(list(messages))  # copia: entender() agrega mensajes a la misma lista
        reply = replies[len(calls) - 1]
        if isinstance(reply, Exception):
            raise reply
        return Generation(text=reply.model_dump_json(), provider="fake", model="fake",
                          seconds=0.1, input_tokens=100, output_tokens=10, data=reply)

    return generar, calls


# --- Esquema y prompt ---

def test_categorias_como_lista_cerrada():
    schema = assistant.understanding_schema().model_json_schema()
    allowed = schema["$defs"]["Need"]["properties"]["category"]["enum"]
    assert allowed == list(load_categories())


def test_categoria_inexistente_no_cumple_el_esquema():
    with pytest.raises(ValidationError):
        understanding(needs=["subscripciones"])


def test_prompt_incluye_todas_las_categorias():
    prompt = assistant.system_prompt()
    for category_id in load_categories():
        assert f"- {category_id}:" in prompt


# --- Reglas que el esquema no expresa ---

@pytest.mark.parametrize("needs, questions, problems", [
    (["auth", "payments"], [], 0),
    ([], ["¿Qué vende tu negocio?"], 0),
    (["auth", "auth"], [], 1),                                          # repetida
    (["auth", "payments", "search", "cache", "ai", "cms"], [], 1),      # más de 5
    (["auth"], ["¿Qué vende tu negocio?"], 1),                          # las dos cosas
    ([], [], 1),                                                        # ninguna
])
def test_reglas(needs, questions, problems):
    assert len(assistant.rule_problems(understanding(needs, questions))) == problems


# --- Reintento ---

def test_reintenta_una_vez_con_los_problemas(monkeypatch):
    generar, calls = fake_generar([understanding(["auth", "auth"]),
                                   understanding(["auth"])])
    monkeypatch.setattr(assistant, "generar", generar)

    result = assistant.entender("Quiero que mis clientes entren con Google.")

    assert result.attempts == 2
    assert result.problems_first and not result.problems_final
    assert result.input_tokens == 200                # se suman los dos intentos
    assert calls[1][-2]["role"] == "assistant"       # ve su respuesta anterior
    assert "repetidas" in calls[1][-1]["content"]    # y qué corregir


def test_sin_respuesta_valida_tras_el_reintento(monkeypatch):
    invalid = LLMInvalidResponse("no cumple", raw_text="{", detail="JSON incompleto")
    generar, calls = fake_generar([invalid, invalid])
    monkeypatch.setattr(assistant, "generar", generar)

    result = assistant.entender("Quiero que mis clientes entren con Google.")

    assert result.data is None
    assert result.attempts == 2
    assert result.problems_final
    assert len(calls) == 2                           # nunca más de un reintento


def test_reintento_sin_texto_no_manda_un_mensaje_vacio(monkeypatch):
    error = LLMInvalidResponse("no cumple", raw_text="", detail="detalle")
    generar, calls = fake_generar([error, error])
    monkeypatch.setattr(assistant, "generar", generar)

    assistant.entender("Necesito cobrar suscripciones mensuales a mis clientes.")

    retry = calls[1]  # la segunda llamada: el reintento
    assert retry[-2] == {"role": "assistant", "content": "(respuesta vacía)"}
