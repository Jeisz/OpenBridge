"""Ejemplos que validan contra los contratos de shared/contracts/.

Correr desde la raíz del repo:
    python -m pytest tests/contracts -v
"""
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from shared.contracts.assistant import AssistantRequest, AssistantResponse, ErrorResponse
from shared.contracts.integration_idea import IntegrationIdea
from shared.contracts.repo import CategoryList, Repo
from shared.contracts.repo_detail import RepoDetail

CONTRACTS_DIR = Path(__file__).resolve().parents[2] / "shared" / "contracts"

# Ejemplos válidos (valores ilustrativos)
REPO = {
    "full_name": "keycloak/keycloak", "github_id": 11125589,
    "description": "Open Source Identity and Access Management For Modern Applications and Services",
    "topics": ["keycloak", "oidc", "saml"],
    "language": "Java", "license_spdx_id": "Apache-2.0",
    "stargazers_count": 37435, "pushed_at": "2026-10-19T18:51:53Z", "open_issues_count": 3273,
    "archived": False,
    "disabled": False,
    "is_maintained": True,
    "readme_text": "Keycloak is an Open Source Identity and Access Management solution...",
    "homepage": "https://www.keycloak.org",
    "health_score": None,
    "categories": [{"category_id": "auth", "assigned_by": "llm"}],
    "use_cases": ["SSO para apps internas", "Login social con Google/GitHub"],
    "summary_es": "Gestión de identidad y acceso de código abierto: login único, roles y permisos.",
}

IDEA = {
    "id": "idea_keycloak_01", "full_name": "keycloak/keycloak",
    "title": "Login único (SSO) con OIDC en una app web",
    "integration_type": "rest_api",
    "summary": "Delegar el login de tu app a Keycloak usando OIDC, sin guardar contraseñas en tu backend.",
    "compatible_stack": ["Next.js", "FastAPI"],
    "dependencies": ["Servidor Keycloak en ejecución", "Un realm y un client configurados"],
    "difficulty": "medium", "snippet": None,
    "docs_url": "https://www.keycloak.org/documentation",
    "generated_by": "llm", "reviewed_at": None, "based_on_hash": "a1b2c3",
}

# Ficha: el repo y las ideas que encajan (0–3). Cuatro ideas exceden el tope.
FICHA = {"repo": REPO, "integration_ideas": [IDEA]}
CUATRO_IDEAS = [{**IDEA, "id": f"idea_keycloak_0{n}"} for n in range(1, 5)]

RESPONSE = {
    "id": "resp_0001", "status": "ok", "title": "Un estudio de yoga, conectado.",
    "summary": "App React con login en Keycloak y API FastAPI que guarda reservas en PostgreSQL.",
    "components": [
        {"key": "c1", "label": "Tu app web (React)", "role": "interfaz", "full_name": None,
         "rationale": "El equipo ya conoce React."},
        {"key": "c2", "label": "API (FastAPI)", "role": "API", "full_name": None,
         "rationale": "Aquí vive la lógica de reservas y cupos."},
        {"key": "c3", "label": "PostgreSQL", "role": "base de datos", "full_name": "postgres/postgres",
         "rationale": "Relacional, para clases, cupos y reservas."},
        {"key": "c4", "label": "Keycloak", "role": "identidad", "full_name": "keycloak/keycloak",
         "rationale": "Cuentas con roles para alumnos y profesores."},
    ],
    "connections": [
        {"from_key": "c1", "to_key": "c4", "protocol": "OIDC", "description": "Inicio de sesión."},
        {"from_key": "c1", "to_key": "c2", "protocol": "REST", "description": "Pide clases y crea reservas."},
        {"from_key": "c2", "to_key": "c4", "protocol": "JWT", "description": "Verifica token y rol."},
        {"from_key": "c2", "to_key": "c3", "protocol": "SQL", "description": "Lee y guarda reservas."},
    ],
    "assumptions": ["Sin pagos en la primera versión."],
    "limitations": ["El control de cupos requiere lógica propia en la API."],
    "generated_at": "2026-10-19T22:00:00Z",
}

SIN_EVIDENCIA = {
    "id": "resp_0002", "status": "no_evidence",
    "summary": "El catálogo no tiene herramientas para control de satélites. "
               "Prueba describiendo la parte web o de datos de tu proyecto.",
    "generated_at": "2026-10-19T22:05:00Z",
}

ERROR = {"error": {"code": "timeout", "message": "La respuesta tardó más de 15 s."}}

# Quinta caja con una key que ya existe; las flechas siguen siendo válidas.
COMPONENTE_REPETIDO = {"key": "c4", "label": "Redis", "role": "caché", "full_name": "redis/redis",
                       "rationale": "Guarda los cupos en memoria."}

# Fila como la entrega la vista:
FILA_VISTA = {
    "github_id": 53631945, "full_name": "BurntSushi/ripgrep", "name": "ripgrep",
    "description": "ripgrep recursively searches directories for a regex pattern",
    "homepage": "", "language": "Rust", "topics": ["cli", "search"],
    "stargazers_count": 50000, "forks_count": 2000, "pushed_at": "2026-10-18T10:00:00Z",
    "archived": False, "license_spdx_id": "Unlicense", "content_hash": "x" * 64,
    "readme_text": None,
}


@pytest.fixture(scope="module")
def category_ids() -> set[str]:
    data = json.loads((CONTRACTS_DIR / "categories.json").read_text(encoding="utf-8"))
    return {c.id for c in CategoryList.model_validate(data).categories}


def test_ids_de_categorias_unicos():
    data = json.loads((CONTRACTS_DIR / "categories.json").read_text(encoding="utf-8"))
    ids = [c["id"] for c in data["categories"]]
    assert len(ids) == len(set(ids)), "id de categoría duplicado"


def test_repo_validado(category_ids):
    repo = Repo.model_validate(REPO)
    assert all(a.category_id in category_ids for a in repo.categories)


def test_idea_valida():
    IntegrationIdea.model_validate(IDEA)


def test_ficha_valida():
    RepoDetail.model_validate(FICHA)


def test_ficha_sin_ideas_es_valida():
    # Cero ideas es válido: repo archivado, sin README o sin ideas revisadas.
    ficha = RepoDetail.model_validate({"repo": {**REPO, "archived": True}, "integration_ideas": []})
    assert ficha.integration_ideas == []


def test_pregunta_valida():
    AssistantRequest(query="Quiero una app web para un estudio de yoga con reservas de clases.")


def test_respuesta_valida():
    AssistantResponse.model_validate(RESPONSE)


def test_respuesta_sin_evidencia_valida():
    AssistantResponse.model_validate(SIN_EVIDENCIA)


@pytest.mark.parametrize("code", ["invalid_query", "invalid_response", "provider_unavailable", "timeout"])
def test_error_valido(code):
    ErrorResponse.model_validate({"error": {"code": code, "message": "Mensaje de ejemplo."}})


def test_fila_de_la_vista_se_lee():
    # Como la entrega la vista: homepage "", columnas extra, sin open_issues_count
    # ni los campos de v1.2 (disabled, is_maintained) → None = sin dato
    repo = Repo.model_validate(FILA_VISTA)
    assert repo.homepage is None
    assert repo.open_issues_count is None
    assert repo.disabled is None
    assert repo.is_maintained is None


def test_summary_es_de_250_es_valido():
    # El límite es inclusivo: 250 caracteres entran; 251 se rechazan (casos inválidos).
    Repo.model_validate({**REPO, "summary_es": "a" * 250})


@pytest.mark.parametrize(
    "modelo, base, cambio",
    [
        (Repo, REPO, {"stargazers_count": -5}),
        (Repo, REPO, {"homepage": "no es url"}),
        (Repo, REPO, {"full_name": "sin-barra"}),
        (Repo, REPO, {"summary_es": "a" * 251}),
        (Repo, REPO, {"is_maintained": "quizás"}),
        (IntegrationIdea, IDEA, {"snippet": "print('hola')"}),
        (AssistantResponse, RESPONSE, {"connections": [
            {"from_key": "c1", "to_key": "c9", "protocol": "REST", "description": "x"}]}),
        (AssistantResponse, RESPONSE, {"status": "needs_clarification"}),
        (AssistantResponse, RESPONSE, {"components": RESPONSE["components"] + [COMPONENTE_REPETIDO]}),
        (AssistantResponse, RESPONSE, {"generated_at": "2026-10-19T22:00:00"}),
        (AssistantResponse, SIN_EVIDENCIA, {"summary": None}),
        (AssistantResponse, RESPONSE, {"summary": "   "}),
        (AssistantResponse, RESPONSE, {"components": [
            {**RESPONSE["components"][0], "label": "   "}, *RESPONSE["components"][1:]]}),
        (AssistantResponse, RESPONSE, {"assumptions": [""]}),
        (IntegrationIdea, IDEA, {"compatible_stack": [
            "Cualquier aplicación web moderna compatible con OpenID Connect"]}),
        (IntegrationIdea, IDEA, {"dependencies": [
            "Un servidor Keycloak en ejecución, con un realm, un client público con PKCE y usuarios de prueba"]}),
        (IntegrationIdea, IDEA, {"compatible_stack": ["React", " "]}),
        (ErrorResponse, ERROR, {"error": {"code": "server_error", "message": "x"}}),
        (RepoDetail, FICHA, {"integration_ideas": [{**IDEA, "full_name": "otro/repo"}]}),
        (RepoDetail, FICHA, {"repo": {**REPO, "archived": True}}),
        (RepoDetail, FICHA, {"integration_ideas": CUATRO_IDEAS}),
    ],
    ids=["estrellas-negativas", "homepage-invalida", "full-name-sin-barra",
         "summary-es-251", "is-maintained-no-booleano",
         "snippet-sin-lenguaje", "flecha-a-caja-inexistente", "aclaracion-sin-preguntas",
         "key-repetida", "fecha-sin-zona", "sin-evidencia-sin-summary", "summary-solo-espacios",
         "label-solo-espacios", "supuesto-vacio", "stack-largo", "dependencia-larga",
         "stack-elemento-vacio", "error-code-desconocido",
         "ficha-idea-de-otro-repo", "ficha-archivado-con-ideas", "ficha-cuatro-ideas"],
)
def test_casos_invalidos_se_rechazan(modelo, base, cambio):
    with pytest.raises(ValidationError):
        modelo.model_validate({**base, **cambio})
