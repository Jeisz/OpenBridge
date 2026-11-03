"""Tests de las métricas de entender (sin red)."""

import pytest

from ai import assistant
from ai.assistant import Understood
from ai.eval.assistant_cases import load_assistant_cases
from ai.eval.understand_metrics import (case_outcome, evidence_is_literal,
                                        query_length_ok, summarize)

CASES = {c.id: c for c in load_assistant_cases().cases}
REQUEST = "Quiero que mis clientes entren con Google y cobrarles una suscripción mensual."


def understood(needs=(), questions=(), problems_first=()):
    """Una respuesta de entender con los valores que importan para medir."""
    schema = assistant.understanding_schema()
    data = schema(needs=[{"category": c, "query": "cobro de suscripciones",
                          "evidence": "cobrar suscripciones"} for c in needs],
                  clarification_questions=list(questions))
    return Understood(data=data, attempts=1, problems_first=list(problems_first),
                      seconds=1.0, input_tokens=100, output_tokens=10)


@pytest.mark.parametrize("evidence, literal", [
    ("quiero que mis clientes entren con Google", True),   # otra mayúscula
    ("cobrarles una suscripción mensual.", True),          # punto final de más
    ("cobrar una suscripción", False),                     # parafraseado
    ("", False),
])
def test_evidencia_literal(evidence, literal):
    assert evidence_is_literal(evidence, REQUEST) is literal


@pytest.mark.parametrize("query, ok", [
    ("cobro de suscripciones", True),
    ("pagos", False),
    ("una consulta demasiado larga para buscar una herramienta de pagos", False),
])
def test_largo_de_la_consulta(query, ok):
    assert query_length_ok(query) is ok


def test_necesidad_inventada():
    o = case_outcome(CASES["una-pagos"], "fake", 1, understood(["payments", "auth"]))
    assert o.found == {"payments"}
    assert o.invented == {"auth"}
    assert not o.exact


@pytest.mark.parametrize("needs, questions, exact", [
    ([], ["¿Qué vende tu negocio?"], True),    # pregunta: bien
    (["ai"], [], False),                       # inventa un stack: mal
])
def test_pedido_vago(needs, questions, exact):
    o = case_outcome(CASES["vago-startup"], "fake", 1, understood(needs, questions))
    assert o.exact is exact


def test_resumen_separa_errores_del_proveedor():
    outcomes = [
        case_outcome(CASES["una-pagos"], "fake", 1, understood(["payments"])),
        case_outcome(CASES["una-pagos"], "fake", 2, understood(["payments", "auth"])),
        case_outcome(CASES["una-pagos"], "fake", 3, None, error="LLMTimeout"),
    ]
    summary = summarize(outcomes)
    assert summary["errors"] == 1
    assert summary["recall"] == 1.0          # payments encontrado en las 2 válidas
    assert summary["invented"] == 1          # auth, una vez
    assert summary["exact"] == 0.5
    assert summary["consistency"] == 0.0     # las 2 corridas válidas difieren
