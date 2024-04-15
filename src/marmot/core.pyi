from typing import Any

from marmot.model.registration import ModelSpec as ModelSpec

class NotImplementedException(BaseException): ...

class ModelMetadata:
    id: str
    category: str

class Model:
    metadata: ModelMetadata
    spec: ModelSpec | None
    def sample_input(self) -> None: ...
    def get_output(self) -> None: ...
    def __call__(self, *args: Any) -> Any: ...
    @classmethod
    def register(cls) -> None: ...
