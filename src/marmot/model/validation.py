from typing import Union

from .registration import ModelSpec, load


def validate_model(id_: Union[str, ModelSpec]) -> bool:
    try:
        model = load(id_)
    except:
        return False

    return model.validate(verbose=True)
