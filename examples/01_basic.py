import sys

import marmot as mt
from marmot.model.registration import get_available_models, registry

sys.path.insert(0, "/Users/leek4/Desktop/marmot/examples")

import fcp

print(registry)
print(get_available_models())
