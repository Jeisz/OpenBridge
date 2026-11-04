"""Punto de registro de las rutas de la API. Sin prefijo /api (acuerdo 29-oct-2026).

Se registran el catálogo (`/repos`) y el asistente (`POST /assistant`), que es
un servicio independiente y no comparte estado con el catálogo. `categories` e
`integrations` no se exponen.
"""
from fastapi import APIRouter

from backend.app.api.routes import assistant, repos
from backend.app.api.schemas import HealthResponse

api_router = APIRouter()
api_router.include_router(repos.router)
api_router.include_router(assistant.router)


@api_router.get(
    "/health",
    tags=["health"],
    response_model=HealthResponse,
    summary="Liveness del proceso",
    description="No certifica disponibilidad de base de datos ni de IA.",
)
def health() -> HealthResponse:
    return HealthResponse(status="ok")

