import copy
import importlib
from typing import Any

import marmot as mt
from marmot import Model, ModelSpec


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


def load_model(id: str | ModelSpec, **kwargs: Any) -> Model:
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

    if not isinstance(model, mt.Model):
        raise TypeError(
            f"The model must inherit from the marmot.Model class, actual class: {type(model)}."
        )

    assert model.spec is not None
    return model
