"""Casos de prueba del asistente: pedidos de negocio con lo que debería responder.

Cada caso fija el status esperado, las necesidades (ids de categorías) que el
asistente debería detectar y, por necesidad, los repos del catálogo que se
aceptan como recomendación. Lista vacía = el catálogo no cubre esa necesidad y
la respuesta debería mencionarlo como limitación.

Las reglas que comparan contra otros archivos (categorías, catálogo) viven en
ai/tests/test_assistant_cases.py.
Los casos de validación y los reservados viven aparte, con el mismo esquema.
"""

from pathlib import Path

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator, model_validator

from shared.contracts.assistant import AssistantRequest, AssistantResponse

EVAL_DIR = Path(__file__).resolve().parent
ASSISTANT_CASES_FILE = EVAL_DIR / "assistant_cases.json"
# Casos escritos para validar reglas nuevas del prompt. No se usan para ajustarlo:
# si se ajusta mirándolos, dejan de medir lo que el asistente hace con pedidos nuevos.
VALIDATION_CASES_FILE = EVAL_DIR / "assistant_cases_validation.json"
# Casos reservados: se escriben antes de cambiar el prompt y se corren solo con la línea
# base y con la versión final. Sus textos no se leen para ajustar.
HOLDOUT_CASES_FILE = EVAL_DIR / "assistant_cases_holdout.json"
CASE_FILES = {"base": ASSISTANT_CASES_FILE, "validation": VALIDATION_CASES_FILE,
              "holdout": HOLDOUT_CASES_FILE}

# Mismos valores que el status de la respuesta del asistente.
Status = AssistantResponse.model_fields["status"].annotation


def status_for(needs: list["ExpectedNeed"]) -> str:
    """Status que corresponde a unas necesidades, según las políticas del asistente."""
    if not needs:
        return "needs_clarification"
    if any(n.acceptable for n in needs):
        return "ok"
    return "no_evidence"


class ExpectedNeed(BaseModel):
    """Una necesidad del pedido y los repos que la resuelven."""
    model_config = ConfigDict(extra="forbid")

    category: str = Field(min_length=1)
    acceptable: list[str] = Field(max_length=3)
    note: str = Field(min_length=1)

    @field_validator("acceptable")
    @classmethod
    def sin_repetidos(cls, v: list[str]) -> list[str]:
        if len(v) != len(set(v)):
            raise ValueError("repo aceptable repetido")
        return v


class AssistantCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    query: str
    expected_status: Status # type: ignore
    needs: list[ExpectedNeed] = Field(max_length=5)
    quick_set: bool = False
    note: str = Field(min_length=1)

    @field_validator("query")
    @classmethod
    def query_valida_para_el_asistente(cls, v: str) -> str:
        AssistantRequest(query=v)
        return v

    @model_validator(mode="after")
    def check_consistency(self):
        categories = [n.category for n in self.needs]
        if len(categories) != len(set(categories)):
            raise ValueError("necesidad repetida")
        expected = status_for(self.needs)
        if self.expected_status != expected:
            raise ValueError(
                f"expected_status '{self.expected_status}' no corresponde a sus necesidades ('{expected}')"
            )
        return self


class AssistantCaseSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int
    catalog_taken_at: AwareDatetime
    cases: list[AssistantCase]

    @model_validator(mode="after")
    def ids_unicos(self):
        ids = [c.id for c in self.cases]
        if len(ids) != len(set(ids)):
            raise ValueError("id de caso repetido")
        return self


def load_assistant_cases(path: Path = ASSISTANT_CASES_FILE) -> AssistantCaseSet:
    """Carga y valida los casos de un archivo. Lanza `ValidationError` si no cumplen."""
    return AssistantCaseSet.model_validate_json(path.read_bytes())
