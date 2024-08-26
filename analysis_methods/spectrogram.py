from typing import Any, Optional

import flet as ft
import numpy as np
# from analysis_methods.base import AnalysisMethodBase
from base import AnalysisMethodBase


class SpectrogramAnalysis(AnalysisMethodBase):
    """
    振動の解析クラス

    Args:
        config(Optional[dict[str, Any]]): 解析クラスで使う設定．
            アプリ初回起動時は省略することで，デフォルト値が使われる．

    Params（tremor_analysis_python/app.py L892-`spectrogram_analize`関数より）
        data: array(3, n)
            x, y, z data
        fs: int/float
            sampling rate
        nperseg: int
            sample number per stft segment
        filename: str
            filename
        sensor: str
            sensor name
        start: integer
            analysis start frame
        end: integer
            analysis end frame
            -1 means end of input data
    """

    def __init__(
            self,
            config: Optional[dict[str, Any]] = {
                "data_idx": 1.0,  # デフォルト値を書いておき，初回起動時のconfig作成に利用する
                "sensor_idx": 2.0,
                "data_i": 3.0,
                "fs": 4.0,
                "nperseg": 5.0,
                "filename": 6.0,
                "sensor": 7.0
            },
            start=0,
            end=-1
    ):
        super().__init__(config)
        self.start = start
        self.end = end

    def run(self, data: np.ndarray) -> dict[str, Any]:
        """
        解析を実行する．

        Args:
            data(np.ndarray): 解析対象のデータ. shape=(axis, timestep)

        Returns:
            dict[str, Any]: 解析結果．項目名と値のdict
        """
        return super().run(data)

    def configure_ui(self) -> ft.Control:
        """
        設定項目のUIを作る．
        補足: ft.Controlは，様々なUIの構成要素の基底クラス

        Returns:
            ft.Control: 設定項目のUI．

        """
        return super().configure_ui()


if __name__ == "__main__":
    spectrogram = SpectrogramAnalysis()
