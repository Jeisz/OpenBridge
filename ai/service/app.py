"""Servicio HTTP del asistente: POST /assistant y GET /health.

Valida la pregunta con el contrato, llama a asistir() y traduce los errores a
ErrorResponse. Lo pesado (modelo de embeddings e índice del catálogo) se carga
una vez al arrancar, antes de aceptar pedidos.

El catálogo sale de lo publicado en la base (AI_CATALOG_SOURCE=database, por defecto) o de
los archivos (files). Si la base falla al arrancar, usa los archivos y GET /health lo dice.

Arranque, desde la raíz del repo:
    uvicorn ai.service.app:create_app --factory --port 8001
"""

import logging
import os
import time
from collections.abc import Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import partial

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from ai import assistant, llm
from ai.service.settings import Settings
from shared.contracts.repo import Repo
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
    catalog_source: str = "files"          # database o files
    catalog_fallback_reason: str | None = None   # por qué no se usó la base, si se pidió
    vectors_stored: int = 0         # vectores guardados en la base que sirvieron
    vectors_computed: int = 0       # vectores calculados al arrancar (faltaban o no coincidían)


def read_catalog(settings: Settings
                 ) -> tuple[list[Repo], dict[int, dict], str, str | None, str | None]:
    """Repos del catálogo, vectores guardados, de dónde salieron, de cuándo son y, si hubo
    respaldo, por qué.

    Con la base: el catálogo publicado (vista + tablas de la IA) con el lector de la IA.
    Si no se puede (sin variable, error de conexión, datos que no cumplen el contrato), usa
    los archivos y lo avisa: el servicio arranca igual y nadie cree que está en la base.
    """
    from ai.catalog import load_repos, snapshot_taken_at
    from ai.published import fetch_catalog
    from ai.scripts.export_catalog_snapshot import ENV_VAR, redact

    reason = None
    if settings.catalog_source == "database":
        url = os.environ.get(ENV_VAR)
        if not url:
            reason = f"falta {ENV_VAR}"
        else:
            try:
                repos, stored = fetch_catalog(url)
                taken = datetime.now(timezone.utc).isoformat(timespec="seconds")
                return repos, stored, "database", taken, None
            except Exception as e:      # cualquier falla de la base: se arranca con los archivos
                first = (redact(str(e), url).splitlines() or [type(e).__name__])[0]
                reason = f"no se pudo leer el catálogo de la base: {first}"
        log.warning("catálogo desde los archivos (respaldo): %s", reason)
    return load_repos("snapshot"), {}, "files", snapshot_taken_at(), reason


def load_catalog(settings: Settings) -> Catalog:
    """Catálogo, modelo de embeddings e índice. Tarda unos segundos."""
    from ai import embeddings           # importa torch: solo al arrancar el servicio
    from ai.search import SearchIndex

    repos, stored, source, taken, reason = read_catalog(settings)
    start = time.perf_counter()
    embeddings.preload()                # las preguntas lo necesitan aunque no haya nada que calcular
    loaded = time.perf_counter()
    index = SearchIndex.from_repos(repos, stored=stored)
    log.warning("modelo cargado en %.1f s; vectores: %d guardados, %d calculados (%.1f s)",
                loaded - start, index.reused, index.computed, time.perf_counter() - loaded)
    spec = embeddings.model_spec()
    return Catalog(buscar=index.search, min_score=spec.min_score,
                   repos=len(index.repos), embedding_model=spec.name,
                   catalog_taken_at=taken, catalog_source=source,
                   catalog_fallback_reason=reason,
                   vectors_stored=index.reused, vectors_computed=index.computed)


def _error(status: int, body: ErrorResponse) -> JSONResponse:
    return JSONResponse(status_code=status, content=body.model_dump())


def create_app(load: Callable[[], Catalog] | None = None,
               settings: Settings | None = None) -> FastAPI:
    """La app del servicio. Sin `settings`, lee el entorno y el archivo .env."""
    if settings is None:
        load_dotenv()
        settings = Settings.from_env()
    if load is None:
        load = partial(load_catalog, settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.providers = llm.provider_chain()   # falla aquí si un nombre no existe
        if not llm.key_configured(app.state.providers[0]):
            log.warning("el proveedor principal no tiene clave: %s", app.state.providers[0])
        app.state.catalog = load()
        log.warning("listo: %d repos (%s), proveedores %s", app.state.catalog.repos,
                    app.state.catalog.catalog_source, " → ".join(app.state.providers))
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
                "catalog_source": catalog.catalog_source,
                "catalog_fallback_reason": catalog.catalog_fallback_reason,
                "catalog_taken_at": catalog.catalog_taken_at,
                "vectors": {"stored": catalog.vectors_stored,
                            "computed_at_startup": catalog.vectors_computed},
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
