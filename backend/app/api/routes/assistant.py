"""POST /assistant: servicio independiente del catálogo.

No hay generador propio en esta rama y no se simula una respuesta válida: el
contrato v1.1 dice que un fallo técnico es un error HTTP con `ErrorResponse`.
El código `provider_unavailable` es el que el frontend ya traduce.
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from shared.contracts.assistant import AssistantRequest, ErrorResponse

router = APIRouter(tags=["assistant"])

_UNAVAILABLE = ErrorResponse(
    error={
        "code": "provider_unavailable",
        "message": "El asistente no está disponible ahora.",
    }
)


@router.post(
    "/assistant",
    response_class=JSONResponse,
    summary="Sugerencia de integración",
    description=(
        "Valida `AssistantRequest` (contrato v1.1) y, mientras no haya proveedor "
        "de IA conectado, responde 503 `provider_unavailable`. Una consulta que "
        "no cumple el contrato responde 422 `invalid_query`."
    ),
    responses={
        422: {"model": ErrorResponse, "description": "La consulta no cumple el contrato."},
        503: {"model": ErrorResponse, "description": "El proveedor del modelo no responde."},
    },
)
def assistant(request: AssistantRequest) -> JSONResponse:
    # `request` se valida con el contrato; el contenido no se usa todavía.
    del request
    return JSONResponse(status_code=503, content=_UNAVAILABLE.model_dump())
