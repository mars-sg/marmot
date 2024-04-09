### Quickstart

```
git clone https://github.com/mars-sg/marmot
cd marmot
pip install .

python examples/01_basic.py
```

### Preparing a model for testing
In order for `marmot` to carry out model testing correctly, the model codes should be wrapped using the `Model` wrapper class. The wrapper provides the model testing facility with information like model initialisation, input requirements, output formats, processing pipelines etc.



To begin, create a folder with a meaningful name. For instance, this could be the name of the project or the name of the model. Inside the newly-created folder, create two files named `__init__.py` and `main.py` respectively. `main.py` could have taken any other name, just remember to change accordingly in `__init__.py` (as we shall see later). In this example, a folder with the name `project_name` is created.

```bash
.
└── project_name
    ├── __init__.py
    └── main.py

```

You can create the folder structure above by running the following in a terminal.

```bash
mkdir project_name
cd project_name
touch __init__.py main.py
```

`main.py` is where the models are wrapped using the wrapper class `Model`. The skeleton of the file looks something like this:

```python
# project_name/main.py

from marmot import Model

class MyModel(Model):
    def __init__(self, **kwargs):
        super().__init__()

        # Initialise your model here
        ...

    def get_output(self, *args):
        # The logic of the model goes here
        ...

        return 1
```

Few things take note here:
1. Initialise your model in the ``__init__`` function of your custom class. This includes codes to initialise the model and load model weights. Any code that should be run only once throughout testing should be housed here.
2. The `get_output` method is required as it tells the model testing facility how to generate outputs from the inputs provided to the model. The arguments to the method should be changed to reflect specific model requirements.

For instance, if you have a trained PyTorch model exported using `torch.save(model, 'path_to_model.pt')`, you can wrap the model as such:

```python
# project_name/main.py

from marmot import Model
import torch

class FuelConsumptionModel(Model):
    def __init__(self, **kwargs):
        super().__init__()

        # Initialise your model here
        self.model = torch.load('path_to_model.pt')

    def get_output(self, x):
        # The logic of the model goes here
        return self.model(x)
```

Once the model is wrapped using the wrapper class `Model`, we need to register and identify the model to `marmot` so that it knows where to locate the model. To do so, we add the following codes in `__init__.py`:

```python
# project_name/__init__.py

from marmot import register
from .main import FuelConsumptionModel

register('fcp-v1', lambda: FuelConsumptionModel())
```

The `register` function takes in two arguments. The first argument is a unique id that is given to the wrapped model. The id is always followed by the version number with the format `<name>-v<version>`. The second argument to the `register` function is the entrypoint to the model. 

From here we can see that if we have multiple versions of the same model we could have added another line to `__init__.py` to register the different versions.

```python
register('fcp-v2', lambda: FuelConsumptionModel2())
```

Once `__init__.py` and `main.py` are sorted out, all that is left is to upload the model to our modelstore for testing. We have provided users with a simple utility that validates the wrapped model, packages and uploads the model to our datastore. To upload the model to our datastore, simply navigate to the parent directory of `project_name` and run the following:

```bash
marmot-util upload project_name 
```