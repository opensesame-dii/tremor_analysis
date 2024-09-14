from abc import ABC, abstractmethod
from typing import Any, Optional

import flet as ft
import numpy as np


class AnalysisMethodBase(ABC):
    """
    解析クラス

    Args:
        content(Optional[dict[str, Any]]): 解析クラスで使う設定．
            アプリ初回起動時は省略することで，デフォルト値が使われる．
    """

    @abstractmethod
    def __init__(
        self,
        content: Optional[dict[str, Any]] = {
            # "param1": 1.0,  # デフォルト値を書いておき，初回起動時のcontent作成に利用する
            # "param2": 2.0,
        },
    ):
        self.content = content

    @abstractmethod
    def run(self, data: np.ndarray) -> dict[str, Any]:
        """
        解析を実行する．

        Args:
            data(np.ndarray): 解析対象のデータ. shape=(axis, timestep)

        Returns:
            dict[str, Any]: 解析結果．項目名と値のdict
        """
        # 解析処理
        return self.result

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
                        ft.TextField(value=self.content[key]),
                    ]
                )
                for key in self.content.keys()
            ]
        )
