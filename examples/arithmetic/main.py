# project_name/main.py

from marmot import Model


class Add(Model):
    _id = "add-v1"
    _category = "arith_add"

    def __init__(self, **kwargs):
        super().__init__()

    def sample_input(self):
        return (0, 2, 3, 4, 5, 9)

    def get_output(self, *x: int):
        out = 0

        for num in x:
            out += num

        return out


class Multiply(Model):
    _id = "multiply-v1"
    _category = "arith_mul"

    def __init__(self, **kwargs):
        super().__init__()

    def sample_input(self):
        return (0, 2, 3, 4, 5, 9)

    def get_output(self, *x):
        out = 1

        for num in x:
            out *= num

        return out
