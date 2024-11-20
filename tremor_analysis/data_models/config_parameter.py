import dataclasses
from typing import Any, Optional, Type, Union


@dataclasses.dataclass
class ConfigParameter:
    name: str
    value: Any
    type: Union[Type[int], Type[float]]
