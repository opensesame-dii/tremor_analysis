import flet as ft


class InputFilters:
    int = ft.InputFilter(
        allow=True, regex_string=r"^[0-9]*$", replacement_string=""
    )

    float = ft.InputFilter(
        allow=True, regex_string=r"^[0-9]*\.?[0-9]*$", replacement_string=""
    )
