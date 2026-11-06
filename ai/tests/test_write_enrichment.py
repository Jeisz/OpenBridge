"""Escritura del catálogo enriquecido en la base (sin base real: cursor simulado)."""

import pytest

from ai.scripts.write_enrichment import (DELETE_CATEGORIES, INSERT_CATEGORY, UPSERT_ENRICHMENT,
                                         to_rows, validate_records, write)

SNAPSHOT = [{"full_name": "a/flink", "github_id": 1, "stargazers_count": 1,
             "pushed_at": "2026-10-01T00:00:00Z", "archived": False},
            {"full_name": "b/vault", "github_id": 2, "stargazers_count": 1,
             "pushed_at": "2026-10-01T00:00:00Z", "archived": False}]


def _registro(github_id, nombre, categorias, resumen="Resumen.", casos=()):
    return {"github_id": github_id, "full_name": nombre, "categories": list(categorias),
            "summary_es": resumen, "use_cases": list(casos), "ai_input_hash": "h"}


REGISTROS = [_registro(1, "a/flink", ["data-processing", "messaging"]),
             _registro(2, "b/vault", ["auth"])]
IDS = {"data-processing", "messaging", "auth"}


def test_registros_validos_pasan():
    validate_records(REGISTROS, SNAPSHOT, IDS)


@pytest.mark.parametrize("registro, error", [
    (_registro(9, "x/otro", ["auth"]), "no está en el snapshot"),
    (_registro(1, "a/flink", ["payments"]), "categorías que no existen"),
    (_registro(1, "a/flink", ["auth"], resumen="a" * 251), "no cumple Repo"),
])
def test_registros_invalidos_no_llegan_a_la_base(registro, error):
    with pytest.raises(ValueError, match=error):
        validate_records([registro], SNAPSHOT, IDS)


def test_el_rank_es_la_posicion_de_la_categoria():
    _, categorias = to_rows(REGISTROS)
    assert [(c["github_id"], c["category_id"], c["rank"]) for c in categorias] == [
        (1, "data-processing", 1), (1, "messaging", 2), (2, "auth", 1)]


class CursorSimulado:
    """Guarda lo que se ejecuta; el repo 2 ya tiene categorías humanas."""

    def __init__(self):
        self.ejecutado = []
        self.rowcount = 0

    def execute(self, sql, params=None):
        self.ejecutado.append((sql, params))

    def executemany(self, sql, filas):
        self.ejecutado.extend((sql, f) for f in filas)

    def fetchall(self):
        return [(2,)]


def test_escribe_todo_y_no_toca_las_categorias_humanas():
    cur = CursorSimulado()
    enrichment, categorias = to_rows(REGISTROS)
    conteos = write(cur, enrichment, categorias)
    por_sql = lambda sql: [p for s, p in cur.ejecutado if s == sql]
    assert [p["github_id"] for p in por_sql(UPSERT_ENRICHMENT)] == [1, 2]
    assert por_sql(DELETE_CATEGORIES) == [{"github_id": 1}]
    assert [p["github_id"] for p in por_sql(INSERT_CATEGORY)] == [1, 1]
    assert conteos["repos con categorías humanas (sin tocar)"] == 1
    assert any("seed-ejemplo" in str(p) for _, p in cur.ejecutado)  # borró la semilla primero
