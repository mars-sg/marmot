import abc
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

class NotImplementedException(BaseException): ...

@dataclass
class ModelMetadata:
    id: str
    def __init__(self, id) -> None: ...
I = TypeVar('I')
O = TypeVar('O')

class Model(ABC, Generic[I, O], metaclass=abc.ABCMeta):
    @property
    @abstractmethod
    def dummy_input(self) -> I: ...
    @property
    @abstractmethod
    def dummy_output(self) -> O: ...
    @abstractmethod
    def get_output(self, *args: Any, **kwargs: Any) -> O: ...
    @classmethod
    def register_model(cls) -> None: ...
    def __call__(self, *args: Any, **kwargs: Any) -> O: ...
