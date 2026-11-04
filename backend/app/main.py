"""Entrada ASGI. Ejecutar desde la raíz del repositorio."""
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.handlers import register_exception_handlers
from backend.app.api.router import api_router
from backend.app.api.schemas import PAGINATION_HEADERS
from backend.app.core.config import Settings
from backend.app.db.session import build_engine


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    try:
        yield
    finally:
        engine = getattr(app.state, "engine", None)
        if engine is not None:
            engine.dispose()


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    app = FastAPI(
        title="OpenBridge API",
        version="0.1.0",
        summary="Catálogo de herramientas open source.",
        description=(
            "API de OpenBridge sin prefijo `/api` (acuerdo del 29-oct-2026): "
            "`GET /repos` devuelve un array con la paginación en cabeceras, "
            "`GET /repos/{owner}/{name}` devuelve `{repo, integration_ideas}` y "
            "`POST /assistant` es el servicio independiente del asistente."
        ),
        lifespan=_lifespan,
    )
    app.state.settings = settings
    # Sin DATABASE_URL no hay motor ni conexión: /repos responde 503, nunca datos falsos.
    app.state.engine = build_engine(settings)
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=list(settings.cors_origins),
            allow_methods=["GET", "POST"],
            allow_headers=["Content-Type", "Authorization"],
            # El frontend lee la paginación de las cabeceras del listado.
            expose_headers=list(PAGINATION_HEADERS),
        )
    register_exception_handlers(app)
    app.include_router(api_router)
    return app


app = create_app()

