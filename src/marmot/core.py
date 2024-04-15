from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import marmot

if TYPE_CHECKING:
    from marmot.model.registration import ModelSpec


class NotImplementedException(BaseException):
    pass


@dataclass
class ModelMetadata:
    id: str
    category: str


class Model:
    _id: str
    _category: str

    metadata: ModelMetadata
    spec: ModelSpec | None = None

    def __init__(self) -> None:
        self.metadata = ModelMetadata(id=self._id, category=self._category)

    def _raise_not_defined_error(self, fn_name: str) -> None:
        if self.spec is None:
            raise NotImplementedException(
                f"`{fn_name}` function not defined for `{type(self).__name__}` model"
            )
        else:
            raise NotImplementedException(
                f"`{fn_name}` function not defined for `{self.spec.id}` model"
            )

    def sample_input(self):
        self._raise_not_defined_error("sample_input")

    def get_output(self, *args, **kwargs):
        self._raise_not_defined_error("get_output")

    @classmethod
    def register(cls) -> None:
        def create_model(**kwargs) -> Model:
            return cls()

        marmot.register(cls._id, create_model)

    def __call__(self, *args: Any) -> Any:
        return self.get_output(*args)


if __name__ == "__main__":

    class TestModel(Model):
        _id = "test-v1"
        _category = "test"

        def __init__(self) -> None:
            super().__init__()

        def get_output(self, x: float) -> float:
            return x

    model = TestModel()
    model(0.0)
