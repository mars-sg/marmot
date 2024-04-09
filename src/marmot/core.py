from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from marmot.model.registration import ModelSpec


class NotImplementedException(BaseException):
    pass


class Model:
    _REQUIRED_KEYS = ["name"]

    spec: ModelSpec | None = None
    # name = ""

    # def __init__(self, info: dict[str, Any]) -> None:
    #     self._find_and_set_parameters(info)

    # def _find_and_set_parameter(self, key: str, info: dict[str, Any]) -> None:
    #     assert key in info, f"Key `{key}` not found in initialisation."

    #     self.__dict__[key] = info[key]

    # def _find_and_set_parameters(self, info: dict[str, Any]) -> None:
    #     for key in self._REQUIRED_KEYS:
    #         self._find_and_set_parameter(key, info)

    def _raise_not_defined_error(self, fn_name: str) -> None:
        if self.spec is None:
            raise NotImplementedException(
                f"`{fn_name}` function not defined for `{type(self).__name__}` model"
            )
        else:
            raise NotImplementedException(
                f"`{fn_name}` function not defined for `{self.spec.id}` model"
            )

    def sample_input(self):
        self._raise_not_defined_error("sample_input")

    def get_output(self):
        self._raise_not_defined_error("get_output")

    def __call__(self, *args: Any) -> Any:
        return self.get_output(*args)


if __name__ == "__main__":

    class TestModel(Model):
        pass

    model = TestModel()
    model()
