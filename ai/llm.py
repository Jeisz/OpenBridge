"""Modelo de lenguaje (LLM) detrás de una sola función: generar().

El proveedor se elige con AI_LLM_PROVIDER (por defecto, gemini). Todos los
proveedores aceptan el formato de OpenAI: solo cambian la dirección, el
modelo, la clave y algunas opciones. Solo este archivo sabe qué proveedor se usa.

Respaldo: si no se pide un proveedor concreto y el principal falla por algo
temporal (límite de uso, caída, tiempo agotado), la misma llamada pasa al de
AI_LLM_FALLBACK (por defecto, groq-low; vacío = sin respaldo), sin esperar.
Con una fecha límite (Deadline), cada intento usa solo el tiempo que queda.
"""

import os
import time
from dataclasses import dataclass, field
from functools import lru_cache
from pydantic import BaseModel, ValidationError

import openai
from openai import OpenAI


@dataclass(frozen=True)
class ProviderSpec:
    """Proveedor de LLM y cómo llamarlo."""

    model: str                          # nombre del modelo en el proveedor
    base_url: str                       # dirección compatible con OpenAI
    api_key_env: str | None             # variable con la clave; None = no usa clave
    temperature: float | None = None    # None = valor por defecto del proveedor
    reasoning_effort: str | None = None # cuánto razona antes de responder; None = por defecto
    extra_body: dict | None = None      # campos propios del proveedor, que el SDK de OpenAI no conoce

PROVIDERS = {
    "gemini": ProviderSpec(
        model="gemini-3.5-flash-lite",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key_env="GEMINI_API_KEY",
        # Gemini 3: Google recomienda no cambiar la temperatura.
    ),
    "groq": ProviderSpec(
        model="openai/gpt-oss-120b",
        base_url="https://api.groq.com/openai/v1",
        api_key_env="GROQ_API_KEY",
    ),
    "groq-low": ProviderSpec(
        model="openai/gpt-oss-120b",
        base_url="https://api.groq.com/openai/v1",
        api_key_env="GROQ_API_KEY",
        # Mismo modelo con menos razonamiento oculto: menos tokens por llamada
        # y menos esperas por el límite de tokens por minuto.
        reasoning_effort="low",
    ),
    "ollama": ProviderSpec(
        model="qwen3.5:4b-q4_K_M",
        base_url="http://localhost:11434/v1/",
        api_key_env=None,  # corre en la máquina: no usa clave
        # Por defecto piensa antes de responder: más de 1.000 tokens y
        # más de 20 s para una frase. "none" lo apaga.
        reasoning_effort="none",
    ),
    "gemini-3.1-lite": ProviderSpec(
        model="gemini-3.1-flash-lite",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key_env="GEMINI_API_KEY",
        # Misma clave que gemini, con su propia cuota diaria: respaldo si se agota la de 3.5.
    ),
    "gemma": ProviderSpec(
        model="gemma-4-26b-a4b-it",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key_env="GEMINI_API_KEY",
        # Modelo abierto en la API de Gemini; mucha más cuota diaria que los Gemini.
    ),
    "claude-haiku-razona": ProviderSpec(
        model="claude-haiku-5-5",
        base_url="https://api.anthropic.com/v1/",
        api_key_env="ANTHROPIC_API_KEY",
        # Igual que claude-haiku, pero razonando (por defecto en Claude 5): más lento,
        # útil en procesos por lotes sin usuario esperando, como el enriquecimiento.
    ),
    "claude-sonnet": ProviderSpec(
        model="claude-sonnet-5-5",
        base_url="https://api.anthropic.com/v1/",
        api_key_env="ANTHROPIC_API_KEY",
        # Modelo grande de Anthropic, de pago. Razona por defecto; no acepta temperatura.
    ),
    "claude-haiku": ProviderSpec(
        model="claude-haiku-5-5",
        base_url="https://api.anthropic.com/v1/",
        api_key_env="ANTHROPIC_API_KEY",
        # Razona por defecto, sin mostrarlo, y esta capa ignora reasoning_effort.
        # Medido con ai/eval/diagnose_latency.py (2026-11-03), generar tarda unos
        # 10 s razonando y unos 5 s sin razonar; compilar cada esquema nuevo
        # suma de 0 a 2,5 s. De pago (créditos del plan).
        extra_body={"thinking": {"type": "disabled"}},
    ),
}
DEFAULT_PROVIDER = "gemini"
# Respaldos en orden, separados por comas; uno sin clave se omite. Vacío = sin respaldo.
DEFAULT_FALLBACK = "groq-low,claude-haiku"
COOLDOWN_SECONDS = 60.0  # un proveedor que falla por algo temporal queda desconectado este tiempo
TIMEOUT_SECONDS = 15.0  # tiempo máximo de una llamada sin fecha límite (evaluaciones, pruebas)
# Con fecha límite (el servicio). Valores iniciales, de las evaluaciones del asistente (nov. 2026):
FIRST_TRY_SECONDS = 7.0  # tope del principal si hay respaldo: su peor llamada medida fue ~4,5 s
                         # y deja al respaldo al menos 6 s (Groq tarda ~1,5 s)
MIN_CALL_SECONDS = 2.5   # por debajo no se empieza una llamada: la mediana de generar es ~2 s
# Textos con que algunos proveedores (Groq) rechazan una respuesta que no cumple el esquema.
SCHEMA_REJECTED = ("does not match the expected schema", "Failed to validate JSON")


@dataclass(frozen=True)
class Deadline:
    """Momento en que se acaba el tiempo de un pedido. Se fija una vez y se consulta en cada paso."""

    at: float  # time.monotonic() del final

    @classmethod
    def in_seconds(cls, seconds: float) -> "Deadline":
        return cls(time.monotonic() + seconds)

    def remaining(self) -> float:
        return self.at - time.monotonic()


class LLMError(Exception):
    """Fallo al llamar al modelo. Las subclases dicen cuál."""


class LLMConfigError(LLMError):
    """Proveedor desconocido, falta la clave o la clave no es válida."""


class LLMRateLimited(LLMError):
    """El proveedor rechazó la llamada por límite de uso (429)."""

    def __init__(self, message: str, retry_after: float | None = None):
        super().__init__(message)
        self.retry_after = retry_after  # segundos que pide esperar, si los dice


class LLMTimeout(LLMError):
    """El proveedor no respondió a tiempo."""


class LLMUnavailable(LLMError):
    """No se pudo conectar o el proveedor devolvió un error."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code  # None = no hubo conexión

    @property
    def transient(self) -> bool:
        """Vale la pena reintentar: sin conexión o error del servidor (5xx)."""
        return self.status_code is None or self.status_code >= 500


class LLMInvalidResponse(LLMError):
    """La respuesta no cumple el esquema pedido."""

    def __init__(self, message: str, raw_text: str, detail: str):
        super().__init__(message)
        self.raw_text = raw_text  # lo que escribió el modelo, para revisarlo
        self.detail = detail      # el error de validación, para el reintento


@dataclass(frozen=True)
class Generation:
    """Respuesta del modelo y datos para medirla."""

    text: str
    provider: str
    model: str
    seconds: float
    input_tokens: int | None
    output_tokens: int | None
    data: BaseModel | None = None  # la respuesta validada, si se pidió un esquema


def provider_key(provider: str | None = None) -> str:
    """El proveedor pedido, o el de AI_LLM_PROVIDER."""
    key = provider or os.environ.get("AI_LLM_PROVIDER") or DEFAULT_PROVIDER
    if key not in PROVIDERS:
        raise LLMConfigError(f"Proveedor {key!r} no existe; opciones: {', '.join(PROVIDERS)}")
    return key


# Disyuntor: proveedor -> momento (time.monotonic) hasta el que queda desconectado.
# Compartido por todos los pedidos del proceso: el primero que descubre una caída
# evita que los siguientes la paguen.
_open_until: dict[str, float] = {}


def key_configured(key: str) -> bool:
    """True si el proveedor tiene su clave en el entorno (o no la necesita)."""
    env = PROVIDERS[key].api_key_env
    return env is None or bool(os.environ.get(env))


def provider_chain(provider: str | None = None) -> list[str]:
    """Proveedores a intentar, en orden. Con uno pedido explícitamente, solo ese.

    Sin él: el principal y los respaldos de AI_LLM_FALLBACK que tengan clave.
    """
    if provider is not None:
        return [provider_key(provider)]
    chain = [provider_key()]
    raw = os.environ.get("AI_LLM_FALLBACK", DEFAULT_FALLBACK)
    for name in (n.strip() for n in raw.split(",")):
        if name and name not in chain:
            key = provider_key(name)          # un nombre que no existe es un error de configuración
            if key_configured(key):
                chain.append(key)             # respaldo sin clave: se omite
    return chain


def disconnected() -> dict[str, float]:
    """Proveedores desconectados por el disyuntor y los segundos que les faltan."""
    now = time.monotonic()
    return {k: round(t - now, 1) for k, t in _open_until.items() if t > now}


@lru_cache(maxsize=None)
def _client(key: str) -> OpenAI:
    """Un cliente por proveedor, creado la primera vez que se usa."""
    spec = PROVIDERS[key]
    if spec.api_key_env is None:
        api_key = "sin-clave"  # el cliente exige un valor; Ollama lo ignora
    else:
        api_key = os.environ.get(spec.api_key_env)
        if not api_key:
            raise LLMConfigError(f"Falta {spec.api_key_env} en .env (proveedor {key}).")
    # max_retries=0: los reintentos y las esperas los decide quien llama.
    return OpenAI(base_url=spec.base_url, api_key=api_key,
                  timeout=TIMEOUT_SECONDS, max_retries=0)


def _failed_generation(err: openai.APIStatusError) -> str:
    """El texto que generó el modelo, si el proveedor lo devuelve con el error."""
    body = err.body if isinstance(err.body, dict) else {}
    inner = body.get("error") if isinstance(body.get("error"), dict) else body
    return str(inner.get("failed_generation", ""))


def _generar_uno(key: str, messages: list[dict], schema: type[BaseModel] | None,
                 timeout: float) -> Generation:
    """Una llamada a un proveedor, con un tiempo máximo. Traduce sus errores a los nuestros."""
    spec = PROVIDERS[key]
    options = {}
    if spec.temperature is not None:
        options["temperature"] = spec.temperature
    if spec.reasoning_effort is not None:
        options["reasoning_effort"] = spec.reasoning_effort
    if spec.extra_body is not None:
        options["extra_body"] = spec.extra_body
    if schema is not None:
        options["response_format"] = {
            "type": "json_schema",
            "json_schema": {"name": schema.__name__,
                            "schema": schema.model_json_schema(),
                            "strict": True},
        }

    start = time.perf_counter()
    try:
        response = _client(key).chat.completions.create(
            model=spec.model, messages=messages, timeout=timeout, **options)
    # El orden importa: cada except atrapa también a sus subclases,
    # así que los casos particulares van antes que los generales.
    except openai.APITimeoutError as err:
        raise LLMTimeout(f"{key}: sin respuesta en {timeout:.1f} s") from err
    except openai.APIConnectionError as err:
        hint = " ¿Ollama está abierto?" if key == "ollama" else ""
        raise LLMUnavailable(f"{key}: no se pudo conectar.{hint}") from err
    except openai.RateLimitError as err:
        wait = err.response.headers.get("retry-after")
        detail = str(err.message)[:300]  # dice qué límite fue: por minuto o por día
        raise LLMRateLimited(f"{key}: límite de uso alcanzado: {detail}",
                             retry_after=float(wait) if wait else None) from err
    except (openai.AuthenticationError, openai.PermissionDeniedError) as err:
        raise LLMConfigError(f"{key}: la clave no es válida o no tiene acceso") from err
    except openai.BadRequestError as err:
        detail = str(err.message)[:300]
        # Algunos proveedores (Groq) validan el JSON contra el esquema y responden 400 si no cumple.
        if any(text in detail for text in SCHEMA_REJECTED):
            raise LLMInvalidResponse(f"{key}: la respuesta no cumple el esquema",
                                     raw_text=_failed_generation(err), detail=detail) from err
        raise LLMUnavailable(f"{key}: error 400 del proveedor: {detail}",
                             status_code=400) from err
    except openai.APIStatusError as err:
        detail = str(err.message)[:300]  # lo que explica el proveedor.
        raise LLMUnavailable(f"{key}: error {err.status_code} del proveedor: {detail}",
                             status_code=err.status_code) from err
    seconds = time.perf_counter() - start

    text = response.choices[0].message.content or ""
    data = None
    if schema is not None:
        try:
            data = schema.model_validate_json(text)
        except ValidationError as err:
            raise LLMInvalidResponse(
                f"{key}: la respuesta no cumple {schema.__name__}",
                raw_text=text, detail=str(err)) from err

    usage = response.usage
    return Generation(
        text=text,
        provider=key,
        model=spec.model,
        seconds=round(seconds, 2),
        input_tokens=usage.prompt_tokens if usage else None,
        output_tokens=usage.completion_tokens if usage else None,
        data=data,
    )


def generar(messages: list[dict], *,
            schema: type[BaseModel] | None = None,
            provider: str | None = None,
            deadline: Deadline | None = None) -> Generation:
    """Envía los mensajes al modelo y devuelve su texto con tiempo y tokens.

    Con `schema`, pide la respuesta en ese formato y la valida.
    Con `provider`, usa solo ese proveedor; sin él, la cadena de respaldos,
    saltando los desconectados por el disyuntor. Con `deadline`, nunca se pasa
    de ella: si no alcanza el tiempo para una llamada, lanza LLMTimeout sin hacerla.
    """
    chain = provider_chain(provider)
    breaker = len(chain) > 1          # con un solo proveedor no hay a quién saltar
    connected = [k for k in chain if not (breaker and k in disconnected())]
    candidates = connected or chain   # si todos están desconectados, se intentan igual
    last_error: LLMError | None = None
    for position, key in enumerate(candidates):
        timeout = TIMEOUT_SECONDS
        if deadline is not None:
            left = deadline.remaining()
            if left < MIN_CALL_SECONDS:
                raise LLMTimeout(f"{key}: quedan {max(left, 0):.1f} s; "
                                 "no alcanza para otra llamada") from last_error
            has_next = position < len(candidates) - 1
            # Con alguien detrás, tope por intento para que al siguiente le quede tiempo.
            timeout = min(left, FIRST_TRY_SECONDS) if has_next else left
        try:
            result = _generar_uno(key, messages, schema, timeout)
        except (LLMRateLimited, LLMTimeout) as err:
            last_error = err  # temporal: se prueba el siguiente, sin esperar
        except LLMUnavailable as err:
            if not err.transient:
                raise  # permanente (por ejemplo, un 400): otro proveedor no lo arregla
            last_error = err
        else:
            _open_until.pop(key, None)        # respondió: queda conectado
            return result
        # Solo las fallas lentas desconectan: un tiempo agotado o sin conexión cuestan segundos;
        # un 429 o un 5xx responden al instante, así que probarlos otra vez casi no cuesta.
        slow = isinstance(last_error, LLMTimeout) or (
            isinstance(last_error, LLMUnavailable) and last_error.status_code is None)
        if breaker and slow:
            _open_until[key] = time.monotonic() + COOLDOWN_SECONDS
    raise last_error


# --- Respuesta validada, con un reintento ---

@dataclass
class LLMResult:
    """Respuesta validada de un paso con LLM, con lo que hace falta para medirla."""

    data: BaseModel | None = None          # None = ningún intento cumplió el esquema
    attempts: int = 0
    problems_first: list[str] = field(default_factory=list)  # del primer intento
    problems_final: list[str] = field(default_factory=list)  # vacío = válida
    seconds: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0


def generate_valid(messages: list[dict], schema: type[BaseModel],
                   check, provider: str | None,
                   format_hint: str | None = None,
                   deadline: Deadline | None = None) -> LLMResult:
    """Llama al modelo y reintenta una vez si la respuesta no cumple el esquema o las reglas.

    `check` recibe la respuesta ya validada contra `schema` y devuelve la lista de
    reglas que no cumple (vacía = cumple).
    `format_hint` se suma al aviso cuando la respuesta no cumple el formato: dice qué
    valores son válidos, porque el error del proveedor no lo dice.
    Con `deadline`, si no queda tiempo para el reintento, generar() lanza LLMTimeout.
    """
    out = LLMResult()
    for attempt in (1, 2):
        out.attempts = attempt
        start = time.perf_counter()
        try:
            result = generar(messages, schema=schema, provider=provider, deadline=deadline)
        except LLMInvalidResponse as err:
            out.data, raw = None, err.raw_text
            problems = [f"la respuesta no cumple el formato pedido: {err.detail}"]
            if format_hint:
                problems.append(format_hint)
        else:
            out.data, raw = result.data, result.text
            out.input_tokens += result.input_tokens or 0
            out.output_tokens += result.output_tokens or 0
            problems = check(result.data)
        out.seconds += time.perf_counter() - start

        if attempt == 1:
            out.problems_first = problems
        out.problems_final = problems
        if not problems:
            break
        # Reintento: el modelo ve su respuesta y qué reglas no cumplió.
        # Si el proveedor no devolvió el texto fallido, se envía un aviso:
        # algunos proveedores rechazan un mensaje del asistente vacío.
        messages = messages + [
            {"role": "assistant", "content": raw or "(respuesta vacía)"},
            {"role": "user", "content": "Tu respuesta no cumple estas reglas:\n- "
                                        + "\n- ".join(problems)
                                        + "\nCorrígela y responde otra vez con el mismo formato."},
        ]

    out.seconds = round(out.seconds, 2)
    return out
