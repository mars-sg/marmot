import importlib
import sys
from functools import lru_cache
from pathlib import Path

import marmot  # type: ignore
from marmot import Model, NotImplementedException


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


@lru_cache
def _get_categories() -> dict[str, list[int]]:
    return marmot.model.registration.get_categories()


# def _check_category_exists(model: Model) -> bool:
#     *_name, _version = model.metadata.category.split("-")
#     name = "-".join(_name)
#     version = int(_version[1:])

#     categories = _get_categories()

#     if name in categories and version in categories[name]:
#         print(
#             "  \033[32m\033[1m✔\033[0m\033[0m test for model category "
#             f"`{model.metadata.category}` exists"
#         )
#         return True
#     else:
#         print(
#             "  \033[91m\033[1m✘\033[0m\033[0m test for model category "
#             f"`{model.metadata.category}` not found"
#         )
#         return False


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

    loaded_models = marmot.model.registration.registry.keys()

    ok = True
    for model_name in loaded_models:
        model_ok = True
        print(f"==> Checking model `{model_name}`")

        try:
            model = marmot.load(model_name)
        except:
            model_ok = False
            print(
                f"  \033[31mError: \033[0m Cannot load model {model_name}. "
                "Check if the entry point is defined correctly."
            )

        if not model_ok:
            ok = False
            continue

        # model_ok &= _check_category_exists(model)
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
