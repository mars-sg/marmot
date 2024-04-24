from typing import Sequence

from ..model import Model

FloatSequence = Sequence[float]


class MeanModel(Model[FloatSequence, float]):
    @property
    def dummy_input(self) -> FloatSequence:
        return (0.0, 1.3)

    @property
    def dummy_output(self) -> float:
        return 1.3
