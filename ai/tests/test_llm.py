"""Tests de ai/llm.py con un proveedor simulado: sin red ni claves."""

from types import SimpleNamespace

import httpx2  # librería HTTP de openai. Para fabricar sus errores
import openai
import pytest
from pydantic import BaseModel, ConfigDict

from ai import llm

MESSAGES = [{"role": "user", "content": "hola"}]
REQUEST = httpx2.Request("POST", "https://proveedor.test/v1/chat/completions")


class FakeCompletions:
    """Imita client.chat.completions: guarda lo enviado y responde lo pedido."""

    def __init__(self):
        self.reply = "hola"
        self.error = None
        self.sent = {}

    def create(self, **kwargs):
        self.sent = kwargs
        if self.error is not None:
            raise self.error
        message = SimpleNamespace(content=self.reply)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)],
                               usage=SimpleNamespace(prompt_tokens=10, completion_tokens=5))


@pytest.fixture
def fake(monkeypatch):
    """Reemplaza el cliente real por uno falso y lo devuelve para configurarlo."""
    completions = FakeCompletions()
    client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    monkeypatch.setattr(llm, "_client", lambda key: client)
    return completions


def status_error(cls, code, headers=None):
    """Un error de la librería con código HTTP, como los que lanza el cliente."""
    response = httpx2.Response(code, headers=headers or {}, request=REQUEST)
    return cls("error simulado", response=response, body=None)


class Answer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    word: str


# --- Proveedor y clave ---

@pytest.mark.parametrize("value", [None, ""])
def test_proveedor_por_defecto(monkeypatch, value):
    if value is None:
        monkeypatch.delenv("AI_LLM_PROVIDER", raising=False)
    else:
        monkeypatch.setenv("AI_LLM_PROVIDER", value)
    assert llm.provider_key() == llm.DEFAULT_PROVIDER


def test_proveedor_desconocido():
    with pytest.raises(llm.LLMConfigError, match="opciones"):
        llm.provider_key("openia")


def test_falta_la_clave(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    llm._client.cache_clear()
    with pytest.raises(llm.LLMConfigError, match="GROQ_API_KEY"):
        llm._client("groq")
    llm._client.cache_clear()


# --- Lo que se envía ---

def test_ollama_no_piensa_y_gemini_usa_sus_valores(fake):
    llm.generar(MESSAGES, provider="ollama")
    assert fake.sent["reasoning_effort"] == "none"

    llm.generar(MESSAGES, provider="gemini")
    assert "temperature" not in fake.sent
    assert "reasoning_effort" not in fake.sent


def test_claude_no_razona_y_los_demas_no_mandan_extra_body(fake):
    llm.generar(MESSAGES, provider="claude-haiku")
    assert fake.sent["extra_body"] == {"thinking": {"type": "disabled"}}

    llm.generar(MESSAGES, provider="gemini")
    assert "extra_body" not in fake.sent


# --- Esquema ---

def test_respuesta_con_esquema(fake):
    fake.reply = '{"word": "listo"}'
    result = llm.generar(MESSAGES, schema=Answer, provider="groq")
    assert result.data == Answer(word="listo")
    assert fake.sent["response_format"]["json_schema"]["strict"] is True


def test_respuesta_que_no_cumple_el_esquema(fake):
    fake.reply = '{"palabra": "listo"}'
    with pytest.raises(llm.LLMInvalidResponse) as caught:
        llm.generar(MESSAGES, schema=Answer, provider="groq")
    assert caught.value.raw_text == '{"palabra": "listo"}'
    assert "word" in caught.value.detail


# --- Errores del proveedor ---

@pytest.mark.parametrize("error, expected", [
    (openai.APITimeoutError(request=REQUEST), llm.LLMTimeout),
    (openai.APIConnectionError(request=REQUEST), llm.LLMUnavailable),
    (status_error(openai.RateLimitError, 429), llm.LLMRateLimited),
    (status_error(openai.AuthenticationError, 401), llm.LLMConfigError),
    (status_error(openai.InternalServerError, 500), llm.LLMUnavailable),
])
def test_errores_del_proveedor(fake, error, expected):
    fake.error = error
    with pytest.raises(expected):
        llm.generar(MESSAGES, provider="groq")


def test_limite_de_uso_con_espera(fake):
    fake.error = status_error(openai.RateLimitError, 429, {"retry-after": "30"})
    with pytest.raises(llm.LLMRateLimited) as caught:
        llm.generar(MESSAGES, provider="groq")
    assert caught.value.retry_after == 30.0


@pytest.mark.parametrize("error, transient", [
    (status_error(openai.InternalServerError, 503), True),
    (status_error(openai.BadRequestError, 400), False),
    (openai.APIConnectionError(request=REQUEST), True),
])
def test_error_temporal_o_permanente(fake, error, transient):
    fake.error = error
    with pytest.raises(llm.LLMUnavailable) as caught:
        llm.generar(MESSAGES, provider="groq")
    assert caught.value.transient is transient


@pytest.mark.parametrize("message", [
    "Generated JSON does not match the expected schema.",
    "Failed to validate JSON. Please adjust your prompt.",
])
def test_esquema_rechazado_por_el_proveedor_es_respuesta_invalida(fake, message):
    response = httpx2.Response(400, request=REQUEST)
    fake.error = openai.BadRequestError(
        message, response=response,
        body={"error": {"failed_generation": '{"label": null}'}})
    with pytest.raises(llm.LLMInvalidResponse) as caught:
        llm.generar(MESSAGES, provider="groq")
    assert caught.value.raw_text == '{"label": null}'


# --- Respaldo y fecha límite ---

@pytest.fixture
def fakes(monkeypatch):
    """Un cliente falso por proveedor, creado al pedirlo; sin variables de entorno."""
    made = {}

    def client(key):
        made.setdefault(key, FakeCompletions())
        return SimpleNamespace(chat=SimpleNamespace(completions=made[key]))

    monkeypatch.setattr(llm, "_client", client)
    monkeypatch.delenv("AI_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("AI_LLM_FALLBACK", raising=False)
    return made


def fails(fakes, key, error):
    """Hace que el proveedor `key` responda con `error`."""
    fakes.setdefault(key, FakeCompletions()).error = error


def test_cadena_de_proveedores(monkeypatch):
    monkeypatch.delenv("AI_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("AI_LLM_FALLBACK", raising=False)
    assert llm.provider_chain() == ["gemini", "groq-low"]
    assert llm.provider_chain("groq") == ["groq"]          # explícito: sin respaldo
    monkeypatch.setenv("AI_LLM_FALLBACK", "")
    assert llm.provider_chain() == ["gemini"]               # vacío: respaldo apagado


def test_pasa_al_respaldo_ante_limite_de_uso(fakes):
    fails(fakes, "gemini", status_error(openai.RateLimitError, 429))
    result = llm.generar(MESSAGES)
    assert result.provider == "groq-low"


def test_pasa_al_respaldo_ante_error_temporal(fakes):
    fails(fakes, "gemini", status_error(openai.InternalServerError, 503))
    assert llm.generar(MESSAGES).provider == "groq-low"


def test_proveedor_explicito_no_usa_respaldo(fakes):
    fails(fakes, "gemini", status_error(openai.RateLimitError, 429))
    with pytest.raises(llm.LLMRateLimited):
        llm.generar(MESSAGES, provider="gemini")
    assert "groq-low" not in fakes


def test_error_permanente_no_usa_respaldo(fakes):
    fails(fakes, "gemini", status_error(openai.BadRequestError, 400))
    with pytest.raises(llm.LLMUnavailable):
        llm.generar(MESSAGES)
    assert "groq-low" not in fakes


def test_sin_tiempo_no_llama_al_modelo(fakes):
    with pytest.raises(llm.LLMTimeout):
        llm.generar(MESSAGES, deadline=llm.Deadline.in_seconds(llm.MIN_CALL_SECONDS - 1))
    assert fakes == {}


def test_tope_del_primer_intento_solo_si_hay_respaldo(fakes, monkeypatch):
    llm.generar(MESSAGES, deadline=llm.Deadline.in_seconds(15))
    assert fakes["gemini"].sent["timeout"] <= llm.FIRST_TRY_SECONDS

    monkeypatch.setenv("AI_LLM_FALLBACK", "")
    llm.generar(MESSAGES, deadline=llm.Deadline.in_seconds(15))
    assert fakes["gemini"].sent["timeout"] > llm.FIRST_TRY_SECONDS


def test_el_limite_de_uso_guarda_el_mensaje_del_proveedor(fakes):
    fails(fakes, "groq", status_error(openai.RateLimitError, 429))
    with pytest.raises(llm.LLMRateLimited) as caught:
        llm.generar(MESSAGES, provider="groq")
    assert "error simulado" in str(caught.value)
