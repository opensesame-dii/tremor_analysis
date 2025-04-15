from __future__ import annotations

import dataclasses
from abc import ABC, abstractmethod
from typing import Any, Optional, Type, Union

import flet as ft
import numpy as np
from PIL import Image

from tremor_analysis.ui.text_field_with_type import TextFieldWithType


@dataclasses.dataclass
class AnalysisResult:
    """
    解析結果のデータを格納するクラス
    解析結果の数値データと画像データを，それぞれの項目名をキーとするdictに格納する
    """

    numerical_result: dict[str, Union[int, float]]
    image_result: dict[str, Image.Image]
    analysis_method_class: Type[AnalysisMethodBase]
    filename1: Optional[str]
    filename2: Optional[str]


@dataclasses.dataclass
class ConfigParameter:
    name: str
    value: Any
    type: Union[Type[int], Type[float]]


class AnalysisMethodBase(ABC):
    """
    解析クラス

    Args:
        config(Optional[list[ConfigParameter]]): 解析クラスで使う設定．
            アプリ初回起動時は省略することで，デフォルト値が使われる．
    """

    ACCEPTABLE_DATA_COUNT: int = 1  # 実行時に受け取るべきデータの配列の数

    config = [
        ConfigParameter(
            name="param1 (Hz)",  # デフォルト値を書いておき，初回起動時のconfig作成に利用する
            value=1.0,
            type=float,
        ),
        ConfigParameter(
            name="param2 (sec)",  # デフォルト値を書いておき，初回起動時のconfig作成に利用する
            value=2,
            type=int,
        ),
    ]

    @abstractmethod
    def __init__(
        self,
        config: Optional[list[ConfigParameter]] = None,
    ):
        if config is not None:
            name_to_item = {item.name: item for item in self.config}
            for item in config:
                name_to_item[item.name] = item
            self.config = list(name_to_item.values())
        self.configure_ui_components: dict[str, Any] = {}
        for config_entry in self.config:
            self.configure_ui_components[config_entry.name] = TextFieldWithType(
                dtype=config_entry.type,
                default_value=config_entry.value,
            )

    @abstractmethod
    def run(self, data: list[np.ndarray]) -> AnalysisResult:
        """
        解析を実行する．

        Args:
            data(list[np.ndarray]): 解析対象のデータ.
                それぞれのnp.ndarrayはshape=(axis, timestep)

        Returns:
            AnalysisResult: 解析結果
        """
        # 解析処理
        return AnalysisResult(
            numerical_result={"value1": 1, "value2": 2},
            image_result={"image1": Image.new("RGB", (1, 1))},
            analysis_method_class=type(self),
            filename1=None,
            filename2=None,
        )

    def configure_ui(self) -> ft.Control:
        """
        設定項目のUIを作る．
        補足: ft.Controlは，様々なUIの構成要素の基底クラス

        Returns:
            ft.Control: 設定項目のUI．

        """
        column = [ft.Text(self.__class__.__name__, size=15, weight=ft.FontWeight.BOLD)]
        for config_entry in self.config:
            column += [
                ft.Container(
                    ft.Row(
                        [
                            ft.Text(config_entry.name),
                            self.configure_ui_components[config_entry.name].widget,
                        ],
                    ),
                    padding=ft.padding.only(left=10),
                ),
            ]

        return ft.Column(column)

    def update_config(self, new_config: dict[str, Any]):
        """
        新しい設定項目の値を更新する．
        Args:
            new_config (dict[str, Any]): 新しい設定項目の値．
                {項目名 (str): 値 (int or float)}
        """
        for key, value in new_config.items():
            for config_entry in self.config:
                if config_entry.name == key:
                    config_entry.value = value
                    self.configure_ui_components[key].widget.value = str(value)
                    break
