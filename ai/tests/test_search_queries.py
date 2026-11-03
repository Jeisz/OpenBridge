"""Valida los golden sets de la búsqueda (ai/eval/search_queries*.json)."""

import json
from collections import defaultdict
from datetime import datetime

import pytest

from ai.catalog import load_raw
from ai.eval.golden import GOLDEN_FILES, SearchGoldenSet, load_search_queries
from ai.scripts.export_catalog_snapshot import META_FILE


@pytest.fixture(scope="module", params=sorted(GOLDEN_FILES))
def golden(request) -> SearchGoldenSet:
    # Cada test corre una vez por golden set.
    return load_search_queries(request.param)


def test_ids_unicos(golden):
    ids = [q.id for q in golden.queries]
    assert len(ids) == len(set(ids))


def test_esperados_existen_en_su_catalogo(golden):
    # Un nombre mal escrito haría fallar esa consulta para siempre, en silencio.
    catalog = {r["full_name"] for r in load_raw(golden.source)}
    for q in golden.queries:
        missing = set(q.expected) - catalog
        assert not missing, f"{q.id}: {missing} no está en el catálogo {golden.source}"


def test_esperados_no_archivados(golden):
    # La búsqueda nunca devuelve repos archivados: esperarlos sería un fallo seguro.
    archived = {r["full_name"] for r in load_raw(golden.source) if r.get("archived")}
    for q in golden.queries:
        assert not set(q.expected) & archived, f"{q.id}: espera un repo archivado"


def test_hay_consultas_con_y_sin_respuesta(golden):
    # Sin respuesta: necesarias para calibrar el umbral de no_evidence.
    assert any(q.answerable for q in golden.queries)
    assert any(not q.answerable for q in golden.queries)


def test_pares_completos_y_distintos(golden):
    # Un par mide que la búsqueda diferencia: dos consultas, listas distintas.
    pairs = defaultdict(list)
    for q in golden.queries:
        if q.pair:
            pairs[q.pair].append(q)
    for name, qs in pairs.items():
        assert len(qs) == 2, f"par {name}: {len(qs)} consultas"
        assert set(qs[0].expected) != set(qs[1].expected), f"par {name}: mismas respuestas"


def test_golden_del_catalogo_lleva_la_fecha_del_snapshot_actual():
    # Si el snapshot se renueva, este test falla a propósito: hay que revisar las
    # consultas (repos nuevos pueden responder las que hoy no tienen respuesta).
    golden = load_search_queries("catalog")
    assert golden.source == "snapshot"
    taken_at = datetime.fromisoformat(json.loads(META_FILE.read_text(encoding="utf-8"))["taken_at"])
    assert golden.catalog_taken_at == taken_at, (
        "El catálogo cambió desde que se escribió el golden set: revisarlo y actualizar catalog_taken_at"
    )


def test_golden_desconocido_es_error():
    with pytest.raises(ValueError, match="no existe"):
        load_search_queries("snapshop")
