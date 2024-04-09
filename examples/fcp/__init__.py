# fcp/__init__.py

from marmot import register

from .main import *

register("dnn-v1", "fcp:FuelConsumptionModel1")
register("dnn-v2", "fcp:FuelConsumptionModel2")
