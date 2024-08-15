from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from .registration import register


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

        register(cls._id, create_model)

    def __call__(self, *args: Any, **kwargs: Any) -> O:
        return self.get_output(*args, **kwargs)

    def validate(self, verbose: bool = False, return_on_failure: bool = False) -> bool:
        if (
            not _check_implemented(self, "get_output", verbose=verbose)
            and return_on_failure
        ):
            return False

        if not _check_model_output(self, verbose=verbose):
            return False

        return True


def _check_implemented(model: Model, fn_name: str, verbose: bool = False) -> bool:
    try:
        getattr(model, fn_name)()
    except NotImplementedException:
        if verbose:
            print(f"  \033[91m\033[1m✘\033[0m\033[0m {fn_name} is not implemented")
        return False
    except:
        pass

    if verbose:
        print(f"  \033[32m\033[1m✔\033[0m\033[0m {fn_name} is implemented")

    return True


def _check_model_output(model: Model, verbose: bool = True) -> bool:
    try:
        _ = model(model.dummy_input)

        if verbose:
            print(f"  \033[32m\033[1m✔\033[0m\033[0m model generates output correctly")

        return True
    except Exception as e:
        if verbose:
            print(f"  \033[91m\033[1m✘\033[0m\033[0m model output error ({e})")

        return False


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
