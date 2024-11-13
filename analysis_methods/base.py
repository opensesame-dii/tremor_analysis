from abc import ABC, abstractmethod
from PIL import Image
from typing import Any, Optional

import dataclasses
import flet as ft
import numpy as np


@dataclasses.dataclass
class AnalysisResult:
    numerical_result: dict[str, Any]
    image_result: dict[str, Image.Image]


class AnalysisMethodBase(ABC):
    """
    解析クラス

    Args:
        config(Optional[dict[str, Any]]): 解析クラスで使う設定．
            アプリ初回起動時は省略することで，デフォルト値が使われる．
    """

    ACCEPTABLE_DATA_COUNT: int = 1  # 実行時に受け取るべきデータの配列の数

    @abstractmethod
    def __init__(
        self,
        config: Optional[dict[str, Any]] = {
            "param1": 1.0,  # デフォルト値を書いておき，初回起動時のconfig作成に利用する
            "param2": 2.0,
        },
    ):
        self.config = config

    @abstractmethod
    def run(self, data: list[np.ndarray]) -> AnalysisResult:
        """
        解析を実行する．

        Args:
            data(list[np.ndarray]): 解析対象のデータ.
                それぞれのnp.ndarrayはshape=(axis, timestep)

        Returns:
            AnalysisResult: 解析結果．項目名と値のdictと，画像の識別用の名前とpillowの画像オブジェクトのdict
        """
        # 解析処理
        return AnalysisResult(
            numerical_result={"value1": 1, "value2": 2},
            image_result={"image1": Image.new("RGB", (1, 1))}
        )

    @abstractmethod
    def configure_ui(self) -> ft.Control:
        """
        設定項目のUIを作る．
        補足: ft.Controlは，様々なUIの構成要素の基底クラス

        Returns:
            ft.Control: 設定項目のUI．

        """
        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(key),
                        ft.TextField(value=self.config[key]),
                    ]
                )
                for key in self.config.keys()
            ]
        )
