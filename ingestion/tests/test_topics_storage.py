"""Regresiones del formato almacenado en catalog_repositories.topics.

No se conecta a PostgreSQL; verifica la sentencia y parámetros enviados.
La prueba real del adaptador PostgreSQL se ejecuta por separado en scripts/.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from sqlalchemy import ARRAY, Text
from sqlalchemy.dialects import postgresql
from load import CatalogSnapshot, prepare_write_batch, insert_new_batch, WRITE_CONFIRMATION
from test_load_v02 import FakeEngine, transformed


def test_sql_serializes_native_array_as_text_not_json():
    batch = prepare_write_batch(transformed(6), CatalogSnapshot({}, frozenset()))
    engine = FakeEngine()
    summary = insert_new_batch(engine, batch, authorization=WRITE_CONFIRMATION)
    assert summary.inserted_repositories == 1
    statements = [(sql, params) for sql, params in engine.calls if sql.startswith('INSERT INTO public.catalog_repositories')]
    assert len(statements) == 1
    sql, params = statements[0]
    assert 'CAST(:topics AS TEXT[])::TEXT' in sql
    assert params['topics'] == ['data', 'etl']  # lista nativa: no texto JSON
    assert isinstance(params['topics'], list)


def test_sql_array_bind_parameter_is_typed_for_postgres():
    from pathlib import Path
    source = (Path(__file__).resolve().parents[1] / 'src' / 'load.py').read_text(encoding='utf-8')
    assert 'bindparam("topics", type_=ARRAY(Text()))' in source
    assert 'CAST(:topics AS TEXT[])::TEXT' in source
    assert 'json.dumps(sorted(repo["topics"])' not in source


def test_empty_topics_list_is_not_json_string():
    result = transformed(6)
    result.repositories[0]['topics'] = []
    batch = prepare_write_batch(result, CatalogSnapshot({}, frozenset()))
    engine = FakeEngine()
    insert_new_batch(engine, batch, authorization=WRITE_CONFIRMATION)
    assert engine.repos[6]['topics'] == []


def test_topics_with_escapes_stay_list_until_driver_serializes():
    result = transformed(6)
    topics = ['unicode-á', 'space tag', 'comma,tag', 'quote"tag', 'back\\slash']
    result.repositories[0]['topics'] = topics
    batch = prepare_write_batch(result, CatalogSnapshot({}, frozenset()))
    engine = FakeEngine()
    insert_new_batch(engine, batch, authorization=WRITE_CONFIRMATION)
    assert engine.repos[6]['topics'] == sorted(topics)
