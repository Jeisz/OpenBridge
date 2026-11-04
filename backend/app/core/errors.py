"""Errores de dominio de la API del catálogo.

Las rutas no conocen HTTP: los servicios levantan estos errores y
`backend.app.api.handlers` los traduce a respuestas JSON con un código estable.
"""


class CatalogUnavailableError(RuntimeError):
    """La base de datos no está configurada, no responde o devuelve datos inválidos."""


class RepoNotFoundError(LookupError):
    """No existe el repositorio pedido en el catálogo."""

    def __init__(self, full_name: str) -> None:
        super().__init__(f"No existe el repositorio '{full_name}' en el catálogo.")
        self.full_name = full_name


class InvalidRequestError(ValueError):
    """Parámetro válido para FastAPI pero fuera de las reglas del catálogo."""
