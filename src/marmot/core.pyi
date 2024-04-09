from marmot.model.registration import ModelSpec as ModelSpec
from typing import Any

class NotImplementedException(BaseException): ...

class Model:
    spec: ModelSpec | None
    def sample_input(self) -> None: ...
    def get_output(self) -> None: ...
    def __call__(self, *args: Any) -> Any: ...
