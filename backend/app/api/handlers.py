"""Traducción de errores de dominio a respuestas JSON con código estable."""
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.app.api.schemas import ErrorDetail, ErrorResponse
from backend.app.core.errors import (
    CatalogUnavailableError,
    InvalidRequestError,
    RepoNotFoundError,
)

logger = logging.getLogger("openbridge.api")

# Mensajes en español para los errores de validación que el frontend puede provocar.
_VALIDATION_MESSAGES = {
    "greater_than_equal": "debe ser mayor o igual a {ge}",
    "less_than_equal": "no puede superar {le}",
    "string_too_long": "no puede superar {max_length} caracteres",
    "string_too_short": "debe tener al menos {min_length} caracteres",
    "string_pattern_mismatch": "tiene un formato no válido",
    "literal_error": "debe ser uno de {expected}",
    "int_parsing": "debe ser un número entero",
    "missing": "es obligatorio",
}

_IGNORED_LOCATIONS = {"body", "query", "path"}

# El frontend traduce el asistente por `error.code` (contrato v1.1).
_ASSISTANT_PATH = "/assistant"
_ASSISTANT_INVALID_QUERY = (
    "La descripción debe contener entre 20 y 2000 caracteres."
)


def _validation_message(error: dict) -> str:
    """Mensaje estable en español sin exponer la traza de Pydantic."""
    field = ".".join(
        str(part) for part in error.get("loc", ()) if part not in _IGNORED_LOCATIONS
    )
    template = _VALIDATION_MESSAGES.get(str(error.get("type", "")))
    detail = "no es válido"
    if template is not None:
        try:
            detail = template.format(**(error.get("ctx") or {}))
        except (KeyError, IndexError):
            detail = "no es válido"
    if field:
        return f"El parámetro '{field}' {detail}."
    return f"Parámetro inválido: {detail}."


def _error(status_code: int, code: str, message: str, headers: dict[str, str] | None = None) -> JSONResponse:
    body = ErrorResponse(error=ErrorDetail(code=code, message=message))
    return JSONResponse(status_code=status_code, content=body.model_dump(), headers=headers)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RepoNotFoundError)
    async def repo_not_found(_request: Request, exc: RepoNotFoundError) -> JSONResponse:
        return _error(404, "repo_not_found", str(exc))

    @app.exception_handler(InvalidRequestError)
    async def invalid_request(_request: Request, exc: InvalidRequestError) -> JSONResponse:
        return _error(422, "invalid_request", str(exc))

    @app.exception_handler(CatalogUnavailableError)
    async def catalog_unavailable(
        _request: Request, exc: CatalogUnavailableError
    ) -> JSONResponse:
        logger.warning("Catálogo no disponible: %s", exc)
        return _error(
            503,
            "catalog_unavailable",
            str(exc) or "El catálogo no está disponible en este momento.",
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = exc.errors()
        first = errors[0] if errors else {}
        logger.info("Petición inválida: %s", errors)
        if request.url.path == _ASSISTANT_PATH:
            # Código del contrato del asistente, no el del catálogo.
            return _error(422, "invalid_query", _ASSISTANT_INVALID_QUERY)
        return _error(422, "invalid_request", _validation_message(first))

