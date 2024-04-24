from dataclasses import dataclass
from typing import NamedTuple

from ..core import Model


@dataclass
class NoonReport:
    length: float
    width: float
    gross_tonnage: float


class DailyFuelConsumptionModel(Model[NoonReport, float]):
    @property
    def dummy_input(self) -> NoonReport:
        return NoonReport(99.0, 30.0, 30.0)

    @property
    def dummy_output(self) -> float:
        return 3.0
