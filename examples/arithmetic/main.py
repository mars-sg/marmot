# project_name/main.py

from typing import Sequence

from marmot.base_models.arithmetic import MeanModel


class BatchMean(MeanModel):
    _id = "mean-v1"

    def __init__(self) -> None:
        super().__init__()

    def get_output(self, x: Sequence[float]) -> float:
        return sum(x) / len(x)


class RecursiveMean(MeanModel):
    _id = "mean-v2"

    def __init__(self) -> None:
        super().__init__()

    def get_output(self, x: Sequence[float]) -> float:
        cur_mean = 0.0
        cur_k = 0

        for item in x:
            cur_mean = (cur_k * cur_mean + item) / (cur_k + 1)
            cur_k += 1

        return cur_mean
