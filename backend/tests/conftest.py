"""Utilidades de prueba: repositorio falso, sin base de datos ni red."""
from typing import Any

from fastapi.testclient import TestClient

from backend.app.api.deps import get_repository
from backend.app.core.config import Settings
from backend.app.main import create_app
from backend.app.repositories.repos import RepoPage

TEST_DSN = "postgresql+psycopg://api:secret@localhost:5432/openbridge"


class FakeRepository:
    """Sustituye a RepoRepository: registra las llamadas y devuelve filas fijas."""

    def __init__(
        self,
        rows: list[dict[str, Any]] | None = None,
        *,
        total: int | None = None,
        detail: dict[str, Any] | None = None,
        error: Exception | None = None,
    ) -> None:
        self.rows = rows or []
        self.total = len(self.rows) if total is None else total
        self.detail = detail
        self.error = error
        self.list_calls: list[dict[str, Any]] = []
        self.detail_calls: list[str] = []

    def list_repos(self, filters, *, limit: int, offset: int) -> RepoPage:
        self.list_calls.append({"filters": filters, "limit": limit, "offset": offset})
        if self.error is not None:
            raise self.error
        return RepoPage(rows=self.rows, total=self.total)

    def get_repo(self, full_name: str) -> dict[str, Any] | None:
        self.detail_calls.append(full_name)
        if self.error is not None:
            raise self.error
        return self.detail


def build_client(
    repository: FakeRepository,
    *,
    settings: Settings | None = None,
    cors_origins: tuple[str, ...] = (),
) -> TestClient:
    app = create_app(settings or Settings(database_url=TEST_DSN, cors_origins=cors_origins))
    app.dependency_overrides[get_repository] = lambda: repository
    return TestClient(app)


def list_row(**overrides: Any) -> dict[str, Any]:
    """Fila del listado: contrato Repo + columnas que la API añade."""
    row: dict[str, Any] = {
        "github_id": 2218615,
        "full_name": "keycloak/keycloak",
        "name": "keycloak",
        "description": "Open Source Identity and Access Management.",
        "homepage": "https://www.keycloak.org/",
        "language": "Java",
        "license_spdx_id": "Apache-2.0",
        "stargazers_count": 26000,
        "forks_count": 6400,
        "pushed_at": "2026-10-22T22:19:40Z",
        "archived": False,
        "disabled": None,
        "open_issues_count": 1234,
        "summary_es": "Servidor de identidades y acceso para aplicaciones.",
        "use_cases": ["SSO para varias aplicaciones"],
        "categories": [
            {"category_id": "auth", "assigned_by": "llm"},
            {"category_id": "database", "assigned_by": "human"},
        ],
    }
    row.update(overrides)
    return row


def detail_row(**overrides: Any) -> dict[str, Any]:
    row = list_row()
    row.update(
        {
            "topics": ["iam", "oauth2", "saml"],
            "readme_text": "# Keycloak\n\nIdentity and access management.",
            "html_url": "https://github.com/keycloak/keycloak",
            "ideas": [],
        }
    )
    row.update(overrides)
    return row


def idea_row(**overrides: Any) -> dict[str, Any]:
    idea: dict[str, Any] = {
        "id": "idea-keycloak-1",
        "title": "Centralizar el login con Keycloak",
        "integration_type": "rest_api",
        "summary": "Delegar autenticación en Keycloak usando OIDC.",
        "compatible_stack": ["Django", "Next.js"],
        "dependencies": ["pyjwt"],
        "difficulty": "medium",
        "triggers": ["login"],
        "snippet": None,
        "snippet_language": None,
        "docs_url": "https://www.keycloak.org/docs/latest/securing_apps/",
        "generated_by": "llm",
        "reviewed_at": None,
        "based_on_hash": "sha256:0123456789abcdef",
    }
    idea.update(overrides)
    return idea
