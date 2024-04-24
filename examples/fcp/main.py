# project_name/main.py

from pathlib import Path

import torch

from marmot.base_models.fuel_consumption import (
    DailyFuelConsumptionRateModel,
    NoonReport,
)


class FuelConsumptionModel1(DailyFuelConsumptionRateModel):
    _id = "dnn-v1"

    def __init__(self):
        super().__init__()

        self.model = torch.load(Path(__file__).parent / "model1.pt")

    def get_output(self, x: NoonReport) -> float:
        return self.model(torch.Tensor([x.length, x.width]))


class FuelConsumptionModel2(DailyFuelConsumptionRateModel):
    _id = "dnn-v2"

    def __init__(self):
        super().__init__()

        self.model = torch.load(Path(__file__).parent / "model2.pt")

    def get_output(self, x: NoonReport) -> float:
        return self.model(torch.Tensor([x.length, x.width]))
