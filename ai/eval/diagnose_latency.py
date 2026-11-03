"""Diagnóstico de latencia del paso generar: en qué se va el tiempo de cada modelo.

Uso, desde la raíz del repo:
    python -m ai.eval.diagnose_latency                       # todas las variantes menos ollama
    python -m ai.eval.diagnose_latency gemini claude-nativo --repeats 2

Arma UNA petición de generar (un caso fijo; las necesidades las entiende gemini
una sola vez; los candidatos salen de la búsqueda real) y la envía idéntica a
cada variante, en streaming, con el mismo esquema fijo. Mide:
- primer texto: segundos hasta el primer carácter visible. Si el modelo razona
  antes de responder, ese tiempo aparece aquí.
- total: segundos hasta el final de la respuesta.
- tokens de salida (según el proveedor) y caracteres visibles. Pocos caracteres
  por token = el proveedor cuenta tokens que no vemos (razonamiento oculto).
- escritura: caracteres visibles por segundo, desde el primer texto.
La primera llamada de cada variante se reporta aparte (en frío).
Escribe ai/eval/results/latency-<fecha>.md y .json (con los textos completos).
"""

import argparse
import json
import statistics
import time
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import ValidationError

from ai import embeddings
from ai.assistant import CANDIDATES_SHOWN, GENERATE_RULES, draft_schema, entender, map_message
from ai.catalog import load_categories
from ai.eval.assistant_cases import load_assistant_cases
from ai.eval.run_assistant_eval import FLOW_PAUSE
from ai.eval.run_understand_eval import RESULTS_DIR
from ai.llm import PROVIDERS, _client
from ai.search import SearchIndex

CALL_TIMEOUT = 60.0  # más que el presupuesto: aquí se mide cuánto tarda, no se corta
MAX_TOKENS = 4096    # la API nativa de Claude lo exige; incluye el razonamiento
DEFAULT_CASE = "pantalla-rag-corto"


@dataclass(frozen=True)
class Variant:
    provider: str              # clave en PROVIDERS: modelo, clave y pausa
    route: str                 # "compat" (formato OpenAI) o "native" (SDK de Anthropic)
    extra: dict | None = None  # opciones adicionales de la llamada


VARIANTS = {
    "gemini": Variant("gemini", "compat"),
    "gemini-3.1-lite": Variant("gemini-3.1-lite", "compat"),
    "groq-low": Variant("groq-low", "compat"),
    "groq": Variant("groq", "compat"),
    "gemma": Variant("gemma", "compat"),
    "ollama": Variant("ollama", "compat"),
    "claude-compat": Variant("claude-haiku", "compat"),
    "claude-compat-sin-pensar": Variant("claude-haiku", "compat",
                                        {"thinking": {"type": "disabled"}}),
    "claude-nativo": Variant("claude-haiku", "native"),
    "claude-nativo-low": Variant("claude-haiku", "native", {"effort": "low"}),
    "claude-nativo-sin-pensar": Variant("claude-haiku", "native",
                                        {"thinking": {"type": "disabled"}}),
}
DEFAULT_VARIANTS = [name for name in VARIANTS if name != "ollama"]  # ollama: si está abierto


@dataclass
class Measure:
    """Una llamada: tiempos, tamaño de la salida y si cumple el esquema."""

    first_text: float | None = None  # None = no llegó texto visible
    total: float = 0.0
    output_tokens: int | None = None
    chars: int = 0
    valid: bool = False
    error: str | None = None
    text: str = ""


# --- La petición fija ---

def build_request(case_id: str):
    """El pedido del caso, entendido una vez por gemini, con sus candidatos reales."""
    case = next((c for c in load_assistant_cases().cases if c.id == case_id), None)
    if case is None:
        raise SystemExit(f"Caso desconocido: {case_id}")
    understood = entender(case.query, provider="gemini")
    if understood.data is None or not understood.data.needs:
        raise SystemExit("gemini no devolvió necesidades para este caso; corre otra vez.")
    print("Construyendo el índice del catálogo…")
    index = SearchIndex.build()
    min_score = embeddings.model_spec().min_score
    needs = understood.data.needs
    shown = {}
    for need in needs:
        found = [r for r in index.search(need.query, CANDIDATES_SHOWN) if r.score >= min_score]
        if found:
            shown[need.category] = found
    if not shown:
        raise SystemExit("Ninguna necesidad tiene candidatos; elige otro caso.")
    messages = [{"role": "system", "content": GENERATE_RULES},
                {"role": "user", "content": map_message(case.query, needs, shown,
                                                        datetime.now(timezone.utc))}]
    return case, needs, shown, messages


# --- Las dos formas de llamar ---

def call_compat(variant: Variant, messages: list[dict], schema) -> Measure:
    """Formato OpenAI: temperatura y razonamiento del registro; extra_body, solo el de la
    variante, para medir con y sin razonamiento (claude-compat = razonando)."""
    spec = PROVIDERS[variant.provider]
    options = {}
    if spec.temperature is not None:
        options["temperature"] = spec.temperature
    if spec.reasoning_effort is not None:
        options["reasoning_effort"] = spec.reasoning_effort
    if variant.extra:
        options["extra_body"] = variant.extra  # campos que el SDK de OpenAI no conoce
    m, parts = Measure(), []
    start = time.perf_counter()
    stream = _client(variant.provider).with_options(timeout=CALL_TIMEOUT).chat.completions.create(
        model=spec.model, messages=messages, stream=True,
        stream_options={"include_usage": True},  # los tokens llegan en el último pedazo
        response_format={"type": "json_schema",
                         "json_schema": {"name": schema.__name__,
                                         "schema": schema.model_json_schema(),
                                         "strict": True}},
        **options)
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            if m.first_text is None:
                m.first_text = time.perf_counter() - start
            parts.append(chunk.choices[0].delta.content)
        if chunk.usage:
            m.output_tokens = chunk.usage.completion_tokens
        if time.perf_counter() - start > CALL_TIMEOUT:
            stream.close()  # deja de recibir; el proveedor deja de cobrar
            m.error = f"cortado: más de {CALL_TIMEOUT:.0f} s"
            break
    m.total = time.perf_counter() - start
    m.text = "".join(parts)
    return m


@lru_cache(maxsize=1)
def _native_client():
    import anthropic  # solo para estas variantes: no es dependencia del asistente
    # Lee ANTHROPIC_API_KEY del entorno (.env). Un solo cliente: reutiliza la conexión,
    # igual que el de formato OpenAI, para que la comparación sea justa.
    return anthropic.Anthropic(timeout=CALL_TIMEOUT, max_retries=0)


def call_native(variant: Variant, messages: list[dict], schema) -> Measure:
    """API propia de Anthropic: salida estructurada con output_config."""
    extra = dict(variant.extra or {})
    output_config = {"format": {"type": "json_schema", "schema": schema.model_json_schema()}}
    if "effort" in extra:
        output_config["effort"] = extra.pop("effort")
    m, parts = Measure(), []
    start = time.perf_counter()
    with _native_client().messages.stream(
            model=PROVIDERS[variant.provider].model, max_tokens=MAX_TOKENS,
            system=messages[0]["content"], messages=messages[1:],
            output_config=output_config, **extra) as stream:
        for text in stream.text_stream:  # solo el texto visible, no el razonamiento
            if m.first_text is None:
                m.first_text = time.perf_counter() - start
            parts.append(text)
            if time.perf_counter() - start > CALL_TIMEOUT:
                m.error = f"cortado: más de {CALL_TIMEOUT:.0f} s"
                break
        else:
            m.output_tokens = stream.get_final_message().usage.output_tokens
    m.total = time.perf_counter() - start
    m.text = "".join(parts)
    return m


def measure(name: str, messages: list[dict], schema) -> Measure:
    variant = VARIANTS[name]
    call = call_native if variant.route == "native" else call_compat
    try:
        m = call(variant, messages, schema)
    except Exception as err:  # diagnóstico: se anota cualquier fallo y se sigue
        return Measure(error=f"{type(err).__name__}: {str(err)[:200]}")
    m.chars = len(m.text)
    try:
        schema.model_validate_json(m.text)
        m.valid = True
    except ValidationError:
        pass
    return m


# --- Reporte ---

def median(values):
    values = [v for v in values if v is not None]
    return statistics.median(values) if values else None


def f1(value) -> str:
    return "—" if value is None else f"{value:.1f}"


def summary_row(name: str, calls: list[Measure]) -> str:
    cold, warm = calls[0], [m for m in calls[1:] if m.error is None]
    ratio = median([m.chars / m.output_tokens for m in warm if m.output_tokens])
    speed = median([m.chars / (m.total - m.first_text) for m in warm
                    if m.first_text is not None and m.total > m.first_text])
    errors = sum(m.error is not None for m in calls)
    cold_cell = "error" if cold.error else f"{f1(cold.first_text)} / {f1(cold.total)}"
    return (f"| {name} | {cold_cell} | {f1(median([m.first_text for m in warm]))} "
            f"| {f1(median([m.total for m in warm]))} "
            f"| {f1(median([m.output_tokens for m in warm]))} "
            f"| {f1(median([m.chars for m in warm]))} | {f1(ratio)} | {f1(speed)} "
            f"| {sum(m.valid for m in warm)}/{len(warm)} | {errors}/{len(calls)} |")


def render(case, needs, results: dict[str, list[Measure]], repeats: int,
           schema_label: str) -> str:
    lines = [
        "# Diagnóstico de latencia · paso generar",
        "",
        f"Generado con `python -m ai.eval.diagnose_latency` el {date.today()} a las "
        f"{time.strftime('%H:%M')}. Caso `{case.id}`; necesidades: "
        f"{', '.join(n.category for n in needs)}. Misma petición y {schema_label} para "
        f"todas las variantes; 1 llamada en frío + {repeats} en caliente; streaming.",
        "",
        "Medianas en caliente. Primer texto y total en segundos; escritura en caracteres "
        "visibles por segundo desde el primer texto.",
        "",
        "| Variante | Frío: primer texto / total | Primer texto | Total | Tokens salida "
        "| Caracteres | Car/token | Escritura | JSON válido | Errores |",
        "|---|---|---|---|---|---|---|---|---|---|",
        *[summary_row(name, calls) for name, calls in results.items()],
        "",
        "## Errores",
        "",
    ]
    errors = [f"- {name}: {m.error}" for name, calls in results.items()
              for m in calls if m.error]
    lines += errors or ["(ninguno)"]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Diagnóstico de latencia del paso generar.")
    parser.add_argument("variants", nargs="*", help="por defecto: " + ", ".join(DEFAULT_VARIANTS))
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--case", default=DEFAULT_CASE)
    parser.add_argument("--closed", action="store_true",
                        help="esquema cerrado de este pedido (el del flujo real de gemini y "
                             "groq) en vez del fijo")
    args = parser.parse_args()
    unknown = [v for v in args.variants if v not in VARIANTS]
    if unknown:
        parser.error(f"variante desconocida: {', '.join(unknown)}")
    names = args.variants or DEFAULT_VARIANTS

    load_dotenv()
    case, needs, shown, messages = build_request(args.case)
    if args.closed:  # cada pedido trae su propio esquema: mide el costo de compilarlo
        repo_names = sorted({r.repo.full_name for found in shown.values() for r in found})
        schema, schema_label = draft_schema(list(shown), repo_names), "esquema cerrado del pedido"
    else:
        schema, schema_label = draft_schema(list(load_categories()), None), "esquema fijo"
    print(f"Caso {case.id}: {', '.join(n.category for n in needs)}")

    results = {}
    for name in names:
        results[name] = []
        for i in range(args.repeats + 1):
            m = measure(name, messages, schema)
            results[name].append(m)
            label = "frío" if i == 0 else f"{i}   "
            print(f"  {name:<26} {label} " + (m.error or
                  f"primer texto {f1(m.first_text)} s · total {f1(m.total)} s · "
                  f"{m.output_tokens} tokens · {m.chars} car · "
                  f"{'válido' if m.valid else 'NO válido'}"))
            time.sleep(FLOW_PAUSE.get(VARIANTS[name].provider, 0))

    RESULTS_DIR.mkdir(exist_ok=True)
    name = f"latency-{date.today()}"
    if names != DEFAULT_VARIANTS:
        name += "-" + "-".join(names)
    if args.closed:
        name += "-cerrado-" + case.id
    stem = RESULTS_DIR / name
    stem.with_suffix(".md").write_text(render(case, needs, results, args.repeats, schema_label),
                                       encoding="utf-8")
    stem.with_suffix(".json").write_text(json.dumps(
        {"case": case.id, "messages": messages,
         "results": {n: [asdict(m) for m in calls] for n, calls in results.items()}},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Reporte: {stem.with_suffix('.md')}")


if __name__ == "__main__":
    main()
