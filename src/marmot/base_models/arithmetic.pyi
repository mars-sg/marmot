import abc
from ..core import Model as Model
from typing import Sequence

FloatSequence = Sequence[float]

class MeanModel(Model[FloatSequence, float], metaclass=abc.ABCMeta):
    @property
    def dummy_input(self) -> FloatSequence: ...
    @property
    def dummy_output(self) -> float: ...
