"""Servicio HTTP del asistente: POST /assistant y GET /health.

Valida la pregunta con el contrato, llama a asistir() y traduce los errores a
ErrorResponse. Lo pesado (modelo de embeddings e índice del catálogo) se carga
una vez al arrancar, antes de aceptar pedidos.

Arranque, desde la raíz del repo:
    uvicorn ai.service.app:create_app --factory --port 8001
"""

import logging
from collections.abc import Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from ai import assistant, llm
from ai.service.settings import Settings
from shared.contracts.assistant import (AssistantRequest, AssistantResponse, ErrorDetail,
                                        ErrorResponse)

log = logging.getLogger("ai.service")


@dataclass(frozen=True)
class Catalog:
    """Lo que el servicio carga una vez al arrancar."""

    buscar: Callable        # buscar(query, k) -> resultados, como espera asistir()
    min_score: float
    repos: int
    embedding_model: str
    catalog_taken_at: str | None = None   # cuándo se tomó la copia del catálogo que usa


def load_catalog() -> Catalog:
    """Modelo de embeddings e índice del catálogo. Tarda unos segundos."""
    from ai import embeddings           # importa torch: solo al arrancar el servicio
    from ai.search import SearchIndex
    from ai.catalog import snapshot_taken_at

    index = SearchIndex.build()
    spec = embeddings.model_spec()
    return Catalog(buscar=index.search, min_score=spec.min_score,
                   repos=len(index.repos), embedding_model=spec.name,
                   catalog_taken_at=snapshot_taken_at())


def _error(status: int, body: ErrorResponse) -> JSONResponse:
    return JSONResponse(status_code=status, content=body.model_dump())


def create_app(load: Callable[[], Catalog] = load_catalog,
               settings: Settings | None = None) -> FastAPI:
    """La app del servicio. Sin `settings`, lee el entorno y el archivo .env."""
    if settings is None:
        load_dotenv()
        settings = Settings.from_env()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.providers = llm.provider_chain()   # falla aquí si un nombre no existe
        if not llm.key_configured(app.state.providers[0]):
            log.warning("el proveedor principal no tiene clave: %s", app.state.providers[0])
        app.state.catalog = load()
        log.warning("listo: %d repos, proveedores %s",
                    app.state.catalog.repos, " → ".join(app.state.providers))
        yield

    app = FastAPI(title="OpenBridge · asistente", version="1.1", lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=list(settings.cors_origins),
                       allow_methods=["GET", "POST"], allow_headers=["Content-Type"])

    @app.exception_handler(RequestValidationError)
    async def invalid_query(request: Request, exc: RequestValidationError) -> JSONResponse:
        # El contrato promete ErrorResponse en todos los errores, también en este.
        return _error(422, ErrorResponse(error=ErrorDetail(
            code="invalid_query",
            message="La pregunta debe ser un objeto con 'query' de 20 a 2000 caracteres.")))

    @app.exception_handler(StarletteHTTPException)
    async def unreadable_body(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        # Un cuerpo ilegible (por ejemplo, texto que no es UTF-8) llega como 400, no como
        # error de validación: para el contrato también es una pregunta inválida.
        if exc.status_code == 400:
            return await invalid_query(request, exc)
        return await http_exception_handler(request, exc)   # 404, 405…: como FastAPI

    @app.get("/health")
    def health() -> dict:
        catalog: Catalog = app.state.catalog
        paused = llm.disconnected()
        llms = [{"provider": p, "model": llm.PROVIDERS[p].model,
                 "key_configured": llm.key_configured(p),
                 "disconnected_seconds": paused.get(p)} for p in app.state.providers]
        return {"status": "ok" if llms[0]["key_configured"] else "incomplete",
                "repos": catalog.repos,
                "catalog_taken_at": catalog.catalog_taken_at,
                "embedding_model": catalog.embedding_model,
                "min_score": catalog.min_score,
                "llm": llms}

    @app.post("/assistant", response_model=AssistantResponse,
              responses={422: {"model": ErrorResponse}, 502: {"model": ErrorResponse},
                         503: {"model": ErrorResponse}, 504: {"model": ErrorResponse}})
    def ask(question: AssistantRequest):
        # def, no async def: asistir() bloquea (red y CPU); FastAPI lo corre en un hilo aparte.
        catalog: Catalog = app.state.catalog
        try:
            assisted = assistant.asistir(question.query, catalog.buscar,
                                         min_score=catalog.min_score)
        except llm.LLMError as err:
            status, body = assistant.error_response(err)
            log.warning("pedido sin respuesta (%d): %s", status, err)
            return _error(status, body)
        if assisted.response is None:
            status, body = assistant.error_response(None)
            log.warning("pedido sin respuesta válida tras el reintento")
            return _error(status, body)
        return assisted.response

    return app
