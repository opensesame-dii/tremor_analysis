import dataclasses
from typing import Any, Type, Union


@dataclasses.dataclass
class ConfigParameter:
    key: str  # パラメーター間でUNIQUEにする
    display_name: str
    value: Any
    type: Union[Type[int], Type[float]]


class ConfigList(list[ConfigParameter]):
    """
    ConfigParameterのリストを作る
    """

    def __init__(self, *args: list[ConfigParameter]):
        super(ConfigList, self).__init__(*args)
        self.name_to_item = {item.key: item for item in self}

    def __getitem__(self, key: str) -> ConfigParameter:
        return self.name_to_item[key]
