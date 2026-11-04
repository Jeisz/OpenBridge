from fastapi.testclient import TestClient
from backend.app.main import create_app
from backend.app.core.config import Settings


def test_health_does_not_require_external_services():
    with TestClient(create_app(Settings())) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


def test_cors_allows_only_configured_origin():
    with TestClient(create_app(Settings(cors_origins=("http://localhost:4173",)))) as client:
        for origin, expected in [("http://localhost:4173", 200), ("https://example.com", 400)]:
            response = client.options("/health", headers={
                "Origin": origin, "Access-Control-Request-Method": "GET",
            })
            assert response.status_code == expected


def test_catalog_without_database_is_503_not_a_fake_success():
    with TestClient(create_app(Settings())) as client:
        response = client.get("/repos")
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "catalog_unavailable"


def test_routes_are_not_under_api_prefix():
    with TestClient(create_app(Settings())) as client:
        assert client.get("/api/health").status_code == 404
        assert client.get("/api/repos").status_code == 404


def test_assistant_is_an_independent_service_without_a_provider():
    with TestClient(create_app(Settings())) as client:
        response = client.post(
            "/assistant", json={"query": "Necesito una aplicación para gestionar usuarios"}
        )

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "provider_unavailable"


def test_assistant_invalid_query_uses_its_own_error_code():
    with TestClient(create_app(Settings())) as client:
        response = client.post("/assistant", json={"query": "hola"})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_query"
    assert "20 y 2000" in response.json()["error"]["message"]


def test_cors_exposes_the_pagination_headers():
    settings = Settings(cors_origins=("http://localhost:4173",))
    with TestClient(create_app(settings)) as client:
        response = client.get("/health", headers={"Origin": "http://localhost:4173"})

    assert "x-total-count" in response.headers["access-control-expose-headers"].lower()

