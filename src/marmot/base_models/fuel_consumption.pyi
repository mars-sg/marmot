import abc
from dataclasses import dataclass

from ..core import Model as Model

@dataclass
class NoonReport:
    length: float
    width: float
    gross_tonnage: float
    def __init__(self, length, width, gross_tonnage) -> None: ...

class DailyFuelConsumptionRateModel(Model[NoonReport, float], metaclass=abc.ABCMeta):
    @property
    def dummy_input(self) -> NoonReport: ...
    @property
    def dummy_output(self) -> float: ...
