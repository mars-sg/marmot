import importlib
import sys
from pathlib import Path

import marmot  # type: ignore
from marmot.model import get_available_models


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
        print(f"==> Checking model `{model_name}`")

        try:
            model = marmot.load(model_name)
        except Exception as e:
            ok = False

            print(
                f"  \033[31mError: \033[0m Cannot load model {model_name}. "
                f"Check if the entry point is defined correctly. {e}"
            )

            continue

        ok &= model.validate(verbose=True)

    if not ok:
        print(
            "\033[31mFatal error: \033[0m Models are not wrapped correctly. "
            "Please refer to the documentation and messages above and fix accordingly."
        )


if __name__ == "__main__":
    main()
