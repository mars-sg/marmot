from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

import marmot

from .validation import _check_implemented, _check_model_output


class NotImplementedException(BaseException):
    pass


@dataclass
class ModelMetadata:
    id: str


I = TypeVar("I")
O = TypeVar("O")


class Model(ABC, Generic[I, O]):
    _id: str

    def __init__(self) -> None:
        self.metadata = ModelMetadata(self._id)

    @property
    @abstractmethod
    def dummy_input(self) -> I:
        pass

    @property
    @abstractmethod
    def dummy_output(self) -> O:
        pass

    @abstractmethod
    def get_output(self, *args: Any, **kwargs: Any) -> O:
        pass

    @classmethod
    def register_model(cls) -> None:
        try:
            cls()
        except Exception as e:
            raise RuntimeError(f"`{cls.__name__}` model not defined properly. {e}")

        def create_model(**kwargs) -> Model:
            return cls()

        marmot.register(cls._id, create_model)

    def __call__(self, *args: Any, **kwargs: Any) -> O:
        return self.get_output(*args, **kwargs)

    def validate(self, verbose: bool = False) -> bool:
        if not _check_implemented(self, "get_output", verbose=verbose):
            return False

        if not _check_model_output(self, verbose=verbose):
            return False

        return True


if __name__ == "__main__":

    class TestModel(Model[float, float]):
        _id = "test-v1"

        def __init__(self) -> None:
            super().__init__()

        @property
        def dummy_input(self) -> float:
            return 1.0

        @property
        def dummy_output(self) -> float:
            return 1.0

        def get_output(self, x: float) -> float:
            return x

    model = TestModel()
    model(0.0)
