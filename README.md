### Quickstart

```
git clone https://github.com/mars-sg/marmot
cd marmot
pip install .

python examples/01_basic.py
```

### Preparing a model for testing
In order for `marmot` to carry out model testing correctly, the model codes should be wrapped using the `Model` wrapper class. The wrapper provides the model testing facility with information like model initialisation, input requirements, output formats, processing pipelines etc. The `marmot` package can be installed using `pip` as follows:

```bash
pip install git+ssh://git@github.com/mars-sg/marmot.git
```

To begin, we create a folder with a meaningful name. For instance, this could be the name of the project or the name of the model. Inside the newly-created folder, create two files named `__init__.py` and `main.py` respectively. `main.py` could have taken any other name, just remember to change accordingly in `__init__.py` (as we shall see later). In this example, a folder with the name `fcp` is created.

```bash
.
└── fcp
    ├── __init__.py
    └── main.py

```

You can create the folder structure above by running the following in a terminal.

```bash
mkdir fcp
cd fcp
touch __init__.py main.py
```

`main.py` is where the models are wrapped using the wrapper class `Model`. The skeleton of the file looks something like this:

```python
# fcp/main.py

from marmot import Model

class MyModel(Model):
    _id = "model-v1"  # Unique name identifier for model
    _category = "fcp"  # Category to which the model belongs

    def __init__(self, **kwargs):
        super().__init__()

        # Initialise your model here
        ...

    def sample_input(self):
        # Return a sample input to the `get_output` function
        ...

    def get_output(self, *args):
        # The logic of the model goes here
        ...
```

Few things take note here:
1. The `_id` and `_category` tells the model testing facility the name of the model and the category to which the model belongs. The id is always followed by the version number with the format `<name>-v<version>`. This id will be used to load the model for testing. The category metadata ensures that the model testing facility feeds the model with the correct input data for testing.
2. Initialise your model in the `__init__` function of your custom class. This includes codes to initialise the model and load model weights. Any code that should be run only once throughout testing should be housed here.
3. The `get_output` method is required as it tells the model testing facility how to generate outputs from the inputs provided to the model. The arguments to the method should be changed to reflect specific model requirements.
4. The `sample_input` method should return a sample input to the `get_output` function. This allows the model testing facility to determine if the `get_output` function is working and producing output as intended.
5. The dependencies of the models (e.g. pytorch, xgboost, etc) should be indicated in the `requirements.txt` file.

For instance, if you have a trained PyTorch model exported using `torch.save(model, 'path_to_model.pt')`, you can wrap the model as such:

```python
# fcp/main.py

from marmot import Model
import torch

class FuelConsumptionModel(Model):
    _id = "fcp-v1"
    _category = "fcp"

    def __init__(self, **kwargs):
        super().__init__()

        # Initialise your model here
        self.model = torch.load('path_to_model.pt')

    def sample_input(self):
        # Return a sample input to the `get_output` function
        return (torch.Tensor([0.33, 0.77]),)

    def get_output(self, x):
        # The logic of the model goes here
        return self.model(x)
```

Since pytorch is used in the model, we need to indicate this dependency in the `requirements.txt` file as such:

```python
# fcp/requirements.txt

torch==2.2.2
```

Once the model is wrapped using the wrapper class `Model`, we need to register and identify the model to `marmot` so that it knows where to locate the model. To do so, we add the following codes in `__init__.py`:

```python
# fcp/__init__.py

from .main import FuelConsumptionModel

FuelConsumptionModel.register()
```

The `register` function creates an entry in the local model registry such that the user is able to locate and use the model. From here we can see that if we have multiple versions of the same model we could have added another line to `__init__.py` to register the different versions.

```python
FuelConsumptionModel2.register()
```

Once `__init__.py` and `main.py` are sorted out, all that is left is to upload the model to our modelstore for testing. We have provided users with a simple utility that validates the wrapped model, packages and uploads the model to our datastore. To upload the model to our datastore, simply navigate to the parent directory of `fcp` and run the following:

```bash
marmot-utils upload fcp 
```

If everything has been set up properly, `marmot-utils` will upload the model to the model testing facility. Otherwise it will tell you what you need to fix before you try uploading again.

The complete codes used in the example above can be found [here](examples/fcp).