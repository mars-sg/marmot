from typing import Union

import marmot  # type: ignore
from marmot import Model, NotImplementedException
from marmot.model.registration import ModelSpec


def _check_implemented(model: Model, fn_name: str, verbose: bool = False) -> bool:
    try:
        getattr(model, fn_name)()
    except NotImplementedException:
        if verbose:
            print(f"  \033[91m\033[1m✘\033[0m\033[0m {fn_name} is not implemented")
        return False
    except:
        pass

    if verbose:
        print(f"  \033[32m\033[1m✔\033[0m\033[0m {fn_name} is implemented")

    return True


def _check_model_output(model: Model, verbose: bool = True) -> bool:
    try:
        _ = model(model.dummy_input)

        if verbose:
            print(f"  \033[32m\033[1m✔\033[0m\033[0m model generates output correctly")

        return True
    except Exception as e:
        if verbose:
            print(f"  \033[91m\033[1m✘\033[0m\033[0m model output error ({e})")

        return False


def validate_model(id_: Union[str, ModelSpec]) -> bool:
    model_name = id_ if isinstance(id_, str) else id_.name

    try:
        model = marmot.load(id_)
    except:
        return False

    return model.validate(verbose=True)
