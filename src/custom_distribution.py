import importlib
import inspect
import os
import pathlib
from dicetypes import DiceType
from node import ExprNode

class CustomDistribution(ExprNode):
    ARG_TYPES = None

    def __init__(self, *args):
        self.args: tuple = args

    def sample(self) -> DiceType:
        raise NotImplementedError("You must inherit from CustomDistribution")


### Gather custom distributions from the distributions/ folder

_pkg_name = "distributions"
_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), _pkg_name)

distribution_module_names: list[str] = [
    f[:-3]
    for f in os.listdir(_dir)
    if f.endswith(".py") and f != "__init__.py"
]

distribution_class_names: list[str] = []
distribution_classes: list[type] = []

for module_name in distribution_module_names:
    module = importlib.import_module(f"{_pkg_name}.{module_name}")

    # Automatically collect all classes defined in the module
    for name, obj in inspect.getmembers(module, inspect.isclass):
        # Only collect classes defined in the module (not imported ones)
        if obj.__module__ == f"{_pkg_name}.{module_name}":
            distribution_class_names.append(name)
            distribution_classes.append(obj)

assert len(distribution_classes) > 0

def _type_to_string(arg_type) -> str:
    if arg_type == int:
        return "INT"
    if arg_type == float:
        return "NUMBER"
    if arg_type == list[int]:
        return "ints"
    if arg_type == list[float]:
        return "nums"
    raise TypeError("Custom distributions can only have "
                  + "int, float, list[int], or list[float] arguments")

grammar = "custom  :  "
for i, dist_class in enumerate(distribution_classes):
    if i > 0:
        grammar += "        |  "
    grammar += f'"{dist_class.NAME}" "(" '

    for i, arg_type in enumerate(dist_class.ARG_TYPES):
        if i > 0:
            grammar += ' "," '
        grammar += _type_to_string(arg_type)

    grammar += f' ")" -> custom_{dist_class.NAME}\n'
