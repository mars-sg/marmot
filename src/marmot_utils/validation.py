import importlib
import sys
from pathlib import Path

import marmot  # type: ignore
from marmot import Model, NotImplementedException
from marmot.model import get_available_models


def _check_implemented(model: Model, fn_name: str) -> bool:
    try:
        getattr(model, fn_name)()
    except NotImplementedException:
        print(f"  \033[91m\033[1m✘\033[0m\033[0m {fn_name} is not implemented")
        return False
    except:
        pass

    print(f"  \033[32m\033[1m✔\033[0m\033[0m {fn_name} is implemented")
    return True


def _check_model_output(model: Model) -> bool:
    try:
        _ = model(model.dummy_input)
        print(f"  \033[32m\033[1m✔\033[0m\033[0m model generates output correctly")
        return True
    except Exception as e:
        print(f"  \033[91m\033[1m✘\033[0m\033[0m model output error ({e})")
        return False


def main() -> None:
    _, path_to_model, model_name, *_ = sys.argv

    assert Path(path_to_model).exists()
    sys.path.insert(0, path_to_model)

    try:
        importlib.import_module(model_name)
    except Exception as e:
        print(
            "\033[31mFatal error: \033[0m Failed to load module. Please check if "
            f"the modules are imported correctly in __init__.py.\n{e}"
        )
        exit()

    loaded_models = get_available_models()

    ok = True
    for model_name in loaded_models:
        model_ok = True
        print(f"==> Checking model `{model_name}`")

        print(model_name)

        # try:
        model = marmot.load(model_name)
        # except Exception as e:
        #     model_ok = False
        #     print(
        #         f"  \033[31mError: \033[0m Cannot load model {model_name}. "
        #         f"Check if the entry point is defined correctly. {e}"
        #     )

        if not model_ok:
            ok = False
            continue

        model_ok &= _check_implemented(model, "get_output")

        if model_ok:
            model_ok &= _check_model_output(model)

        ok &= model_ok

    if not ok:
        print(
            "\033[31mFatal error: \033[0m Models are not wrapped correctly. "
            "Please refer to the documentation and messages above and fix accordingly."
        )


if __name__ == "__main__":
    main()
