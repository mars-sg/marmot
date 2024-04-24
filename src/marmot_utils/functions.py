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
_MARMOT_MODELSTORE_API_IP = "172.20.116.94"
_MARMOT_MODELSTORE_API_PORT = "8234"
_MARMOT_REPOSITORY = "git+ssh://git@github.com/mars-sg/marmot.git"


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
    print(f"OS NAME: {os.name}")

    python = sys.executable
    subprocess.run([python, "-m", "venv", str(venv_path)])

    if os.name == "posix":
        venv_python = venv_path / "bin" / "python"
    elif os.name == "nt":
        venv_python = venv_path / "Scripts" / "python.exe"
    else:
        raise RuntimeError("OS not supported!")

    return venv_python


def cleanup() -> None:
    print(f"==> Cleaning up...")

    venv_path = Path.cwd() / _MARMOT_VALIDATION_VENV_NAME
    if venv_path.exists():
        shutil.rmtree(venv_path)

    tmp_path = Path.cwd() / _MARMOT_TMP_DIR
    if tmp_path.exists():
        shutil.rmtree(tmp_path)


def _install_marmot(python: Path, local_repo: Path | None = None) -> str:
    out = subprocess.run(
        [
            python,
            "-m",
            "pip",
            "install",
            "-q",
            _MARMOT_REPOSITORY if local_repo is None else local_repo,
        ],
        capture_output=True,
        text=True,
    )

    if out.returncode != 0:
        raise RuntimeError(
            f"Could not clone marmot repository.\n{'='*80}\n{out.stderr}{'='*80}"
        )

    return out.stdout.strip()


def _install_dependencies(python: Path, requirements_file: Path) -> str:
    out = subprocess.run(
        [python, "-m", "pip", "install", "-qr", requirements_file],
        capture_output=True,
        text=True,
    )

    if out.returncode != 0:
        raise RuntimeError(
            "Unable to install packages from requirements.txt."
            f"\n{'='*80}\n{out.stderr}{'='*80}"
        )

    return out.stdout.strip()


def _run_validation(python: Path, validation_script: Path, path_to_model: Path) -> str:
    out = subprocess.run(
        [
            python,
            validation_script,
            path_to_model.parent.absolute(),
            path_to_model.stem,
        ],
        capture_output=True,
        text=True,
    )

    if out.returncode != 0:
        raise RuntimeError(
            f"Error occurred during validation.\n{'='*80}\n{out.stderr}{'='*80}"
        )

    return out.stdout.strip()


def _compress_model(path_to_model: Path) -> Path:
    tmp_path = Path(_MARMOT_TMP_DIR)
    tmp_path.mkdir(parents=True, exist_ok=True)

    out_filename = tmp_path / f"{path_to_model.stem}.zip"

    with zipfile.ZipFile(tmp_path / f"{path_to_model.stem}.zip", mode="w") as archive:
        for file in path_to_model.glob("*"):
            if file.name == "__pycache__":
                continue

            if file.suffix == ".pyc":
                continue

            archive.write(file)

    return out_filename


def validate_model(
    path_to_model: str,
    print: Callable = lambda *args: None,
    local_repo: Path | None = None,
) -> bool:
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

    if not ok:
        print("===> Aborting, required files not found!")

    venv_python = _create_validation_virtual_env()

    # Install marmot repo in validation venv
    _install_marmot(venv_python, local_repo=local_repo)

    # Install user-defined dependencies in requirements.txt
    requirements_file = (directory / "requirements.txt").absolute()
    _install_dependencies(venv_python, requirements_file)

    # Validate model, all errors are properly handled
    # This block will not raise any error even if the model is not ok
    validation_script = (Path(__file__).parent / "validation.py").absolute()
    out = _run_validation(venv_python, validation_script, directory)

    print(out)

    if "Fatal error" in out:
        return False

    print(f"==> Models OK")
    return True


def upload_model(path_to_model: str, print: Callable = lambda *args: None):
    directory = Path(path_to_model)

    print(f"==> Packing and compressing models...")
    archive_fn = _compress_model(directory)

    print(f"==> Uploading models...")
    requests.post(
        f"http://{_MARMOT_MODELSTORE_API_IP}:{_MARMOT_MODELSTORE_API_PORT}"
        f"/models/{directory.stem}",
        files={"file": archive_fn.open("rb")},
    )
