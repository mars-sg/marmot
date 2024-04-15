# project_name/main.py

from pathlib import Path

import torch

from marmot import Model


class FuelConsumptionModel1(Model):
    _id = "dnn-v1"
    _category = "fcp"

    def __init__(self, **kwargs):
        super().__init__()

        # Initialise your model here
        self.model = torch.load(Path(__file__).parent / "model1.pt")

    def sample_input(self):
        # Return a sample input to the `get_output` function
        return (torch.Tensor([0.33, 0.77]),)

    def get_output(self, x):
        # The logic of the model goes here
        return self.model(x)


class FuelConsumptionModel2(Model):
    _id = "dnn-v2"
    _category = "fcp"

    def __init__(self, **kwargs):
        super().__init__()

        # Initialise your model here
        self.model = torch.load(Path(__file__).parent / "model2.pt")

    def sample_input(self):
        # Return a sample input to the `get_output` function
        return (torch.Tensor([0.33, 0.77]),)

    def get_output(self, x):
        # The logic of the model goes here
        return self.model(x)
