from ..core import Model as Model
from dataclasses import dataclass
from re import Pattern
from typing import Any, Protocol

MODEL_ID_RE: Pattern

class ModelCreator(Protocol):
    def __call__(self, **kwargs: Any) -> Model: ...

@dataclass
class ModelSpec:
    id: str
    entry_point: ModelCreator | str
    kwargs: dict = ...
    namespace: str | None = ...
    name: str = ...
    version: int | None = ...
    def __post_init__(self) -> None: ...
    def __init__(self, id, entry_point, kwargs) -> None: ...

registry: dict[str, ModelSpec]
current_namespace: str | None

def parse_model_id(model_id: str) -> tuple[str | None, str, int | None]: ...
def get_model_id(ns: str | None, name: str, version: int | None) -> str: ...
def find_highest_version(ns: str | None, name: str) -> int | None: ...
def load_model_creator(name: str) -> ModelCreator: ...
def register(id: str, entry_point: str | ModelCreator | None, kwargs: dict = {}) -> None: ...
def get_categories() -> dict[str, list[int]]: ...
def load(id: str | ModelSpec, **kwargs: Any) -> Model: ...
