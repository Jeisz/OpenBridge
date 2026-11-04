"""SQL generado por el repositorio: filtros, parámetros y fuentes de datos.

No hay base de datos en estas pruebas: se inspecciona el SQL y los binds.
"""
from backend.app.repositories.repos import (
    MAINTENANCE_ACTIVE,
    MAINTENANCE_INACTIVE,
    RepoFilters,
    build_detail_statement,
    build_list_statement,
)


def test_list_without_filters_has_no_filter_clause():
    sql, params = build_list_statement(RepoFilters(), limit=20, offset=0)

    assert "ILIKE" not in sql
    assert "= ANY(:categories)" not in sql
    assert "lower(r.language)" not in sql
    assert "r.license_spdx_id =" not in sql
    assert "r.stargazers_count >=" not in sql
    assert "ORDER BY r.full_name ASC" in sql
    assert params == {"limit": 20, "offset": 0}
    assert "public.catalog_repositories" in sql
    assert "ai.ai_repo_enrichment" in sql
    assert "ai.ai_repo_categories" in sql


def test_list_filters_become_bound_parameters():
    filters = RepoFilters(
        search="keycloak",
        categories=("autenticacion", "seguridad"),
        language="Java",
        license_spdx_id="Apache-2.0",
        maintenance=MAINTENANCE_ACTIVE,
        min_stars=1000,
    )
    sql, params = build_list_statement(filters, limit=10, offset=30)

    assert params["search"] == "%keycloak%"
    assert params["categories"] == ["autenticacion", "seguridad"]
    assert params["language"] == "Java"
    assert params["license_spdx_id"] == "Apache-2.0"
    assert params["min_stars"] == 1000
    assert (params["limit"], params["offset"]) == (10, 30)
    assert "fc.category_id = ANY(:categories)" in sql
    assert "lower(r.language) = lower(:language)" in sql
    assert "r.stargazers_count >= :min_stars" in sql


def test_search_wildcards_are_escaped():
    sql, params = build_list_statement(
        RepoFilters(search=r"100%_x\y"), limit=1, offset=0
    )

    assert params["search"] == r"%100\%\_x\\y%"
    assert "ESCAPE" in sql


def test_maintenance_approximation_only_uses_archived_and_disabled():
    active_sql, _ = build_list_statement(
        RepoFilters(maintenance=MAINTENANCE_ACTIVE), limit=1, offset=0
    )
    inactive_sql, _ = build_list_statement(
        RepoFilters(maintenance=MAINTENANCE_INACTIVE), limit=1, offset=0
    )

    assert "COALESCE(r.archived, FALSE) = FALSE" in active_sql
    assert "COALESCE(r.disabled, FALSE) = FALSE" in active_sql
    assert "= TRUE" in inactive_sql
    assert "is_maintained" not in active_sql
    assert "health" not in active_sql


def test_detail_reads_view_base_table_and_ai_results():
    sql = build_detail_statement()

    assert "public.v_repos_for_ai" in sql
    assert "public.catalog_repositories" in sql
    assert "ai.ai_repo_enrichment" in sql
    assert "ai.ai_repo_categories" in sql
    assert "ai.ai_integration_ideas" in sql
    assert "lower(v.full_name) = lower(:full_name)" in sql
    assert "v.readme_text" in sql
    assert "r.html_url" in sql
