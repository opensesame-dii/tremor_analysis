from typing import Optional, Type, Union

import flet as ft

from tremor_analysis.ui.input_filters import InputFilters


class TextFieldWithType:
    def __init__(
        self,
        dtype: Union[Type[int], Type[float], Type[str]],
        default_value: Optional[str] = "",
    ):
        self.dtype = dtype
        if self.dtype == int:
            self.widget = ft.TextField(
                input_filter=InputFilters.int,
                value=default_value,
            )
        elif self.dtype == float:
            self.widget = ft.TextField(
                input_filter=InputFilters.float,
                value=default_value,
            )
        elif self.dtype == str:
            self.widget = ft.TextField(
                value=default_value,
            )
        else:
            raise NotImplementedError("CustomTextField.dtype must be int, float or str")

    @property
    def value(self):
        """
        dtypeで指定した型にキャストしてFieldの値を返す
        """
        try:
            return self.dtype(self.widget.value)
        except ValueError:
            if self.dtype == int:
                return 0
            elif self.dtype == float:
                return 0.0
            elif self.dtype == str:
                return ""


if __name__ == "__main__":

    # 従来
    int_num = 1
    field1 = ft.TextField(value=int_num)
    value1 = field1.value  # value1: str
    print(type(value1))  # int
    float_num = 1.0
    field1 = ft.TextField(value=float_num)
    value1 = field1.value  # value1: str
    print(type(value1))  # float
    str_num = "1"
    field1 = ft.TextField(value=str_num)
    value1 = field1.value  # value1: str
    print(type(value1))  # str

    # これから
    field2 = TextFieldWithType(dtype=int)
    value2 = field2.value  # value2: int
    print(type(value2))  # int
    value2 = field2.value  # value2: int
    print(type(value2))  # str
