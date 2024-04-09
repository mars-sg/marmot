import importlib
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Callable

import requests

_MARMOT_VALIDATION_VENV_NAME = ".marmot-validation-venv"
_MARMOT_TMP_DIR = ".marmot-tmp"


def _check_file_exists(file: str, directory: Path) -> bool:
    assert directory.is_dir()

    if (directory / file).exists():
        print(f"  \033[32m\033[1m✔\033[0m\033[0m {file} exists")
        return True
    else:
        print(f"  \033[91m\033[1m✘\033[0m\033[0m {file} is missing")
        return False


def _create_validation_virtual_env() -> Path:
    venv_path = Path.cwd() / _MARMOT_VALIDATION_VENV_NAME

    print(f"==> Creating new virtual environment for validation ({venv_path})")

    python = sys.executable
    subprocess.run([python, "-m", "venv", str(venv_path)])

    if os.name == "posix":
        venv_python = venv_path / "bin" / "python"
    elif os.name == "nt":
        venv_python = venv_path / "bin" / "python.exe"
    else:
        raise RuntimeError("OS not supported!")

    return venv_python


def _cleanup() -> None:
    print(f"==> Cleaning up...")

    venv_path = Path.cwd() / _MARMOT_VALIDATION_VENV_NAME
    if venv_path.exists():
        shutil.rmtree(venv_path)

    tmp_path = Path.cwd() / _MARMOT_TMP_DIR
    if tmp_path.exists():
        shutil.rmtree(tmp_path)


def validate_model(path_to_model: str, print: Callable = lambda *args: None):
    directory = Path(path_to_model)
    model_name = directory.stem

    print(
        f"==> Validating model with name `\033[1m{model_name}\033[0m` "
        f"({directory.absolute()})..."
    )

    # Check file requirements
    print(f"==> Checking file requirements...")
    ok = True
    ok &= _check_file_exists(f"__init__.py", directory)
    ok &= _check_file_exists(f"requirements.txt", directory)

    venv_python = _create_validation_virtual_env()

    subprocess.call(
        [
            venv_python,
            "-m",
            "pip",
            "install",
            "-q",
            "git+ssh://git@github.com/mars-sg/marmot.git",
        ]
    )
    subprocess.call(
        [
            venv_python,
            "-m",
            "pip",
            "install",
            "-qr",
            directory.absolute() / "requirements.txt",
        ]
    )

    out = subprocess.run(
        [
            venv_python,
            Path(__file__).parent / "validation.py",
            directory.absolute().parent,
            model_name,
        ],
        capture_output=True,
        text=True,
    ).stdout.strip()

    print(out)

    if "Fatal error" not in out:
        print(f"==> Models OK")
        print(f"==> Packing and compressing models...")
        tmp_path = Path(_MARMOT_TMP_DIR)
        tmp_path.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(tmp_path / f"{model_name}.zip", mode="w") as archive:
            for file in directory.glob("*"):
                if file.name == "__pycache__":
                    continue

                if file.suffix == ".pyc":
                    continue

                archive.write(file)

        print(f"==> Uploading models...")
        files = {"file": open(tmp_path / f"{model_name}.zip", "rb")}
        requests.post(f"http://172.20.116.94:8234/models/{model_name}", files=files)

        print(f"==> Done!")

    _cleanup()
