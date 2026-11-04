"""Prueba de humo del LLM: una llamada corta a cada proveedor.

Uso desde la raíz del repo, con el entorno activo:
    python -m ai.scripts.check_llm            # los tres proveedores
    python -m ai.scripts.check_llm groq       # solo uno

Comprueba clave, dirección y modelo, y muestra tiempo y tokens. Cada
proveedor se llama dos veces: la primera puede incluir el arranque en frío.
"""

import sys

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict

from ai.llm import PROVIDERS, LLMError, LLMInvalidResponse, generar

PROMPT = [{"role": "user",
           "content": "Responde con una sola frase corta en español: ¿qué es una caché?"}]


class Need(BaseModel):
    """Esquema de prueba: una necesidad del pedido."""
    model_config = ConfigDict(extra="forbid")
    category: str
    query: str


class Needs(BaseModel):
    """Esquema de prueba con la forma del paso de entender."""
    model_config = ConfigDict(extra="forbid")
    needs: list[Need]
    clarification: str | None


SCHEMA_PROMPT = [{"role": "user", "content": (
    "Pedido de un cliente: 'Quiero que mis clientes entren con Google y cobrarles "
    "una suscripción mensual.' Lista sus necesidades: para cada una, una categoría "
    "en inglés (por ejemplo auth, payments) y una consulta corta en español para "
    "buscar herramientas. Si el pedido es claro, clarification es null.")}]


def check_schema(key: str) -> bool:
    """Una llamada con esquema. True si la respuesta lo cumple."""
    try:
        result = generar(SCHEMA_PROMPT, schema=Needs, provider=key)
    except LLMInvalidResponse as err:
        print(f"  {key:<7} esquema  INVÁLIDA: {err.detail[:150]!r}")
        print(f"          escribió: {err.raw_text[:150]!r}")
        return False
    except LLMError as err:
        print(f"  {key:<7} esquema  ERROR {type(err).__name__}: {err}")
        return False
    print(f"  {key:<7} esquema  {result.seconds:>6.2f} s  "
          f"tokens {result.input_tokens}→{result.output_tokens}  {result.data}")
    return True


def check(key: str) -> bool:
    """Llama dos veces al proveedor; True si las dos respondieron."""
    for attempt in ("1.ª", "2.ª"):
        try:
            result = generar(PROMPT, provider=key)
        except LLMError as err:
            print(f"  {key:<7} {attempt}  ERROR {type(err).__name__}: {err}")
            return False
        print(f"  {key:<7} {attempt}  {result.seconds:>6.2f} s  "
              f"tokens {result.input_tokens}→{result.output_tokens}  "
              f"{result.text[:70]!r}")
    return True


def main() -> int:
    load_dotenv()
    keys = sys.argv[1:] or list(PROVIDERS)
    unknown = [k for k in keys if k not in PROVIDERS]
    if unknown:
        print(f"Proveedor desconocido: {', '.join(unknown)}. Opciones: {', '.join(PROVIDERS)}")
        return 2

    results = {key: check(key) and check_schema(key) for key in keys}
    failed = [key for key, ok in results.items() if not ok]
    print("Todo responde." if not failed else f"Fallaron: {', '.join(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
