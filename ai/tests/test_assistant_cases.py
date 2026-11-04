"""Valida los casos de prueba del asistente: los de siempre y los de validación.

Sin base de datos ni modelo de lenguaje. Correr desde la raíz del repo:
    python -m pytest ai/tests/test_assistant_cases.py -v
"""

import json
from datetime import datetime

import pytest
from pydantic import ValidationError

from ai.catalog import load_categories
from ai.eval.assistant_cases import (CASE_FILES, AssistantCase, AssistantCaseSet,
                                     load_assistant_cases)
from ai.scripts.export_catalog_snapshot import META_FILE, REPOS_FILE


@pytest.fixture(scope="module", params=sorted(CASE_FILES))
def case_set(request) -> AssistantCaseSet:
    """Cada test que la usa corre una vez por archivo de casos."""
    return load_assistant_cases(CASE_FILES[request.param])


@pytest.fixture(scope="module")
def snapshot() -> dict[str, dict]:
    """Repos del snapshot del catálogo, por full_name."""
    return {r["full_name"]: r for r in json.loads(REPOS_FILE.read_text(encoding="utf-8"))}


def all_needs(case_set):
    return [(c.id, n) for c in case_set.cases for n in c.needs]


# --- Reglas contra otros archivos ---

def test_necesidades_son_categorias(case_set):
    categories = load_categories()
    for case_id, need in all_needs(case_set):
        assert need.category in categories, f"{case_id}: '{need.category}' no es una categoría"


def test_aceptables_existen_en_el_catalogo(case_set, snapshot):
    for case_id, need in all_needs(case_set):
        missing = set(need.acceptable) - snapshot.keys()
        assert not missing, f"{case_id}/{need.category}: {missing} no está en el catálogo"


def test_aceptables_no_archivados(case_set, snapshot):
    # El asistente nunca recomienda un repo archivado.
    for case_id, need in all_needs(case_set):
        archived = [r for r in need.acceptable if snapshot.get(r, {}).get("archived")]
        assert not archived, f"{case_id}/{need.category}: {archived} está archivado"


def test_licencia_sin_identificar_se_justifica(case_set, snapshot):
    # NOASSERTION = GitHub no identificó la licencia: aceptarlo exige citar la evidencia.
    for case_id, need in all_needs(case_set):
        unknown = [r for r in need.acceptable if snapshot.get(r, {}).get("license_spdx_id") == "NOASSERTION"]
        if unknown:
            assert "licencia" in need.note.lower(), (
                f"{case_id}/{need.category}: {unknown} sin licencia identificada; justificarla en note"
            )


def test_casos_escritos_con_el_catalogo_actual(case_set):
    # Si el catálogo cambió, hay que revisar los casos: pueden aparecer repos
    # para necesidades que hoy son limitación.
    taken_at = datetime.fromisoformat(json.loads(META_FILE.read_text(encoding="utf-8"))["taken_at"])
    assert case_set.catalog_taken_at == taken_at, (
        "El catálogo cambió desde que se escribieron los casos: revisarlos y actualizar catalog_taken_at"
    )


def test_validacion_separada_de_la_base():
    # Los casos de validación miden pedidos que el prompt no vio: no pueden repetir los de la base.
    base = load_assistant_cases(CASE_FILES["base"]).cases
    validation = load_assistant_cases(CASE_FILES["validation"]).cases
    assert not {c.id for c in base} & {c.id for c in validation}, "id repetido entre archivos"
    assert not {c.query for c in base} & {c.query for c in validation}, "pedido repetido entre archivos"
    assert not any(c.quick_set for c in validation), "los casos rápidos son de la base"


# --- Reglas del esquema ---

def caso(**cambios) -> dict:
    base = {
        "id": "x",
        "query": "Quiero que mis clientes busquen productos en mi tienda en línea",
        "expected_status": "ok",
        "needs": [{"category": "search", "acceptable": ["a/b"], "note": "evidencia"}],
        "note": "caso de prueba",
    }
    return {**base, **cambios}


def test_caso_valido():
    AssistantCase.model_validate(caso())


@pytest.mark.parametrize("cambios", [
    {"query": "muy corta"},                                   # menos de 20 caracteres
    {"expected_status": "no_evidence"},                       # tiene un repo aceptable → ok
    {"expected_status": "error"},                             # no es un status del contrato
    {"needs": [{"category": "search", "acceptable": [], "note": "n"}] * 2},  # necesidad repetida
    {"needs": [{"category": "search", "acceptable": ["a/b", "a/b"], "note": "n"}]},
    {"needs": [{"category": "search", "acceptable": ["a/1", "a/2", "a/3", "a/4"], "note": "n"}]},
    {"note": ""},
    {"extra": 1},                                             # campo desconocido
])
def test_caso_invalido(cambios):
    with pytest.raises(ValidationError):
        AssistantCase.model_validate(caso(**cambios))


@pytest.mark.parametrize("needs, status", [
    ([], "needs_clarification"),
    ([{"category": "payments", "acceptable": [], "note": "n"}], "no_evidence"),
    ([{"category": "payments", "acceptable": [], "note": "n"},
      {"category": "search", "acceptable": ["a/b"], "note": "n"}], "ok"),
])
def test_status_segun_necesidades(needs, status):
    assert AssistantCase.model_validate(caso(needs=needs, expected_status=status)).expected_status == status


def test_subconjunto_rapido():
    # Cinco casos de la base para comparar modelos rápido; deben cubrir cada comportamiento.
    quick = [c for c in load_assistant_cases().cases if c.quick_set]
    assert len(quick) == 5
    assert {c.expected_status for c in quick} == {"ok", "no_evidence", "needs_clarification"}
    assert any(len(c.needs) >= 3 for c in quick), "falta un negocio de varias necesidades"
    assert any(len(c.needs) == 1 for c in quick), "falta un pedido de una sola necesidad"
    assert any(
        c.expected_status == "ok" and any(not n.acceptable for n in c.needs) for c in quick
    ), "falta un caso con limitación"
