# fcp/__init__.py

from marmot import register

from .main import *

register("add-v1", "arithmetic:Add")
register("multiply-v1", "arithmetic:Multiply")
