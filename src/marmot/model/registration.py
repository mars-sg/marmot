import sys

sys.path.insert(0, ".marmot_models")

import copy
import difflib
import importlib
import json
import logging
import re
from dataclasses import dataclass, field
from importlib.util import find_spec
from pathlib import Path
from typing import Any, Protocol

import requests

from ..core import Model

MODEL_ID_RE = re.compile(
    r"^(?:(?P<namespace>[\w:-]+)\/)?(?:(?P<name>[\w:.-]+?))(?:-v(?P<version>\d+))?$"
)


class ModelCreator(Protocol):
    def __call__(self, **kwargs: Any) -> Model: ...


@dataclass
class ModelSpec:
    id: str
    entry_point: ModelCreator | str

    # model initialisation arguments
    kwargs: dict = field(default_factory=dict)

    # post-init attributes
    namespace: str | None = field(init=False)
    name: str = field(init=False)
    version: int | None = field(init=False)

    def __post_init__(self):
        self.namespace, self.name, self.version = parse_model_id(self.id)


# Global registry of models. Meant to be accessed through `register` and `make`
registry: dict[str, ModelSpec] = {}
current_namespace: str | None = None


def parse_model_id(model_id: str) -> tuple[str | None, str, int | None]:
    match = MODEL_ID_RE.fullmatch(model_id)
    if not match:
        raise Exception(f"Malformed model ID: {model_id}")

    ns, name, version = match.group("namespace", "name", "version")
    if version is not None:
        version = int(version)

    return ns, name, version


def get_model_id(ns: str | None, name: str, version: int | None) -> str:
    full_name = name
    if ns is not None:
        full_name = f"{ns}/{name}"
    if version is not None:
        full_name = f"{full_name}-v{version}"

    return full_name


def find_highest_version(ns: str | None, name: str) -> int | None:
    version: list[int] = [
        model_spec.version
        for model_spec in registry.values()
        if model_spec.namespace == ns
        and model_spec.name == name
        and model_spec.version is not None
    ]

    return max(version, default=None)


def _check_namespace_exists(ns: str | None):
    if ns is None:
        return

    namespaces: set[str] = {
        model_spec.namespace
        for model_spec in registry.values()
        if model_spec.namespace is not None
    }

    if ns in namespaces:
        return

    suggestion = (
        difflib.get_close_matches(ns, namespaces, n=1) if len(namespaces) > 0 else None
    )
    if suggestion:
        suggestion_msg = f"Did you mean: `{suggestion[0]}`"
    else:
        suggestion_msg = f"Have you installed the proper package for {ns}?"

    raise Exception(f"Namespace {ns} not found. {suggestion_msg}")


def _check_name_exists(ns: str | None, name: str):
    _check_namespace_exists(ns)

    names: set[str] = {
        model_spec.name
        for model_spec in registry.values()
        if model_spec.namespace == ns
    }
    if name in names:
        return

    suggestion = difflib.get_close_matches(name, names, n=1)
    namespace_msg = f" in namespace {ns}" if ns else ""
    suggestion_msg = f" Did you mean: `{suggestion[0]}`?" if suggestion else ""

    raise Exception(f"Model `{name}` does not exist{namespace_msg}.{suggestion_msg}")


def _check_version_exists(ns: str | None, name: str, version: int | None):
    if get_model_id(ns, name, version) in registry:
        return

    _check_name_exists(ns, name)
    if version is None:
        return

    message = f"Model version `v{version}` for model `{get_model_id(ns, name, None)}` does not exist."

    model_specs = [
        model_spec
        for model_spec in registry.values()
        if model_spec.namespace == ns and model_spec.name == name
    ]
    model_specs = sorted(
        model_specs, key=lambda model_spec: int(model_spec.version or -1)
    )

    default_spec = [
        model_spec for model_spec in model_specs if model_spec.version is None
    ]

    if default_spec:
        message += f"It provides the default version `{default_spec[0].id}`."
        if len(model_specs) == 1:
            raise Exception(message)

    spec_versions = [
        version for model_spec in model_specs if (version := model_spec.version)
    ]

    latest_version = max(spec_versions, default=None)
    if latest_version is not None and version > latest_version:
        version_list_msg = ", ".join(f"`v{version}`" for version in spec_versions)
        message += f" It provides versioned model: [ {version_list_msg} ]."

        raise Exception(message)


def _check_spec_register(testing_spec: ModelSpec):
    latest_versioned_spec = max(
        (
            model_spec
            for model_spec in registry.values()
            if model_spec.namespace == testing_spec.namespace
            and model_spec.name == testing_spec.name
            and model_spec.version is not None
        ),
        key=lambda spec_: int(spec_.version),  # type: ignore
        default=None,
    )

    unversioned_spec = next(
        (
            model_spec
            for model_spec in registry.values()
            if model_spec.namespace == testing_spec.namespace
            and model_spec.name == testing_spec.name
            and model_spec.version is None
        ),
        None,
    )

    if unversioned_spec is not None and testing_spec.version is not None:
        raise Exception(
            "Cannot register the versioned model"
            f"`{testing_spec.id}` when the unversioned model "
            f"`{unversioned_spec.id}` of the same name already exists."
        )
    elif latest_versioned_spec is not None and testing_spec.version is None:
        raise Exception(
            "Cannot register the unversioned model `{testing_spec.id}` "
            f"when the versioned model `{latest_versioned_spec.id}` "
            "of the same name already exists."
        )


def _find_spec(model_id: str) -> ModelSpec:
    # For string id's, load the model spec from the registry then make the model spec
    assert isinstance(model_id, str)

    # The model name can include an unloaded module in "module:model_name" style
    if ":" in model_id:
        module, model_name = model_id.split(":")
    else:
        module = None
        model_name = model_id

    if module is not None:
        if "#" in module:
            module = module.replace("#", "__")

        if not find_spec(module):
            import urllib.request
            import zipfile

            filename = Path(".marmot-models") / ".compressed" / f"{module}.zip"
            filename.parent.mkdir(parents=True, exist_ok=True)

            urllib.request.urlretrieve(
                f"http://172.20.116.94:8234/models/{module}", filename
            )

            with zipfile.ZipFile(filename, "r") as zip_ref:
                zip_ref.extractall(".marmot-models")

        try:
            importlib.import_module(module)
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                f"{e}. Model registration via importing a module failed. "
                f"Check whether '{module}' contains model registration and can be imported."
            ) from e

    # load the model spec from the registry
    model_spec = registry.get(model_name)

    # update model spec is not version provided, raise warninig if out of date
    ns, name, version = parse_model_id(model_name)

    latest_version = find_highest_version(ns, name)
    if version is None and latest_version is not None:
        version = latest_version
        new_model_id = get_model_id(ns, name, version)
        model_spec = registry.get(new_model_id)
        logging.warn(
            f"Using the latest versioned model `{new_model_id}` "
            f"instead of the unversioned model `{model_name}`."
        )

    if model_spec is None:
        _check_version_exists(ns, name, version)
        raise Exception(
            f"No registered model with id: {model_name}. Did you register it, "
            "or import the package that registers it? Use `marmot.pprint_registry()` "
            "to see all of the registered models."
        )

    return model_spec


def load_model_creator(name: str) -> ModelCreator:
    mod_name, attr_name = name.split(":")
    mod = importlib.import_module(mod_name)
    fn = getattr(mod, attr_name)
    return fn


def register(
    id: str, entry_point: str | ModelCreator | None, kwargs: dict = {}
) -> None:
    assert entry_point is not None, "`entry_point` must be provided"
    global registry, current_namespace
    ns, name, version = parse_model_id(id)

    if current_namespace is not None:
        kwargs_namespace: str | None = kwargs.get("namespace")

        if kwargs_namespace is not None and kwargs_namespace != current_namespace:
            logging.warn(
                f"Custom namespace `{kwargs_namespace}` is being overriden "
                f"by namespace `{current_namespace}`."
            )

        ns_id: str | None = current_namespace
    else:
        ns_id = ns

    full_model_id = get_model_id(ns_id, name, version)

    new_spec = ModelSpec(id=full_model_id, entry_point=entry_point, kwargs=kwargs)
    _check_spec_register(new_spec)

    if new_spec.id in registry:
        logging.warn(f"Overriding model {new_spec.id} already in registry")

    registry[new_spec.id] = new_spec


def get_categories() -> dict[str, list[int]]:
    try:
        response = requests.request("GET", "http://172.20.116.94:8234/models")
        return json.loads(response.text)
    except:
        raise Exception("Could not retrieve model categories from model registry.")


def load(
    id: str | ModelSpec,
    **kwargs: Any,
) -> Model:
    if isinstance(id, ModelSpec):
        model_spec = id
    else:
        assert isinstance(id, str)
        model_spec = _find_spec(id)

    assert isinstance(model_spec, ModelSpec)

    # Update the model spec kwargs with the `make` kwargs
    model_spec_kwargs = copy.deepcopy(model_spec.kwargs)
    model_spec_kwargs.update(kwargs)

    # Load the model creator
    if model_spec.entry_point is None:
        raise Exception(f"{model_spec.id} registered but entry_point is not specified")
    elif callable(model_spec.entry_point):
        model_creator = model_spec.entry_point
    else:
        model_creator = load_model_creator(model_spec.entry_point)

    try:
        model = model_creator(**model_spec_kwargs)
    except TypeError as e:
        raise type(e)(
            f"{e} was raised from the model creator for {model_spec.id} with kwargs ({model_spec_kwargs})"
        )

    if not isinstance(model, Model):
        raise TypeError(
            f"The model must inherit from the marmot.Model class, actual class: {type(model)}."
        )

    model.spec = ModelSpec(
        id=model_spec.id, entry_point=model_spec.entry_point, kwargs=model_spec.kwargs
    )

    assert model.spec is not None
    return model
