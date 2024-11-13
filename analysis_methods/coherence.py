# https://github.com/opensesame-dii/tremor_analysis_python/blob/master/multiple_analysis/multiple.py#L960
# ft_coherence関数に対応

from typing import Any, Optional

import flet as ft
import numpy as np
# from scipy.signal import detrend, spectrogram, get_window
from matplotlib.mlab import cohere, window_hanning
# from analysis_methods.base import AnalysisMethodBase
from base import AnalysisMethodBase


class CoherenceAnalysis(AnalysisMethodBase):
    """
    Args:
        content(Optional[dict[str, Any]]): 解析クラスで使う設定．
            アプリ初回起動時は省略することで，デフォルト値が使われる．

    Params
        sampling_rate: int/float
            sampling rate
    """

    def __init__(
            self,
            content: Optional[dict[str, Any]] = {
                "sampling_rate": 200,  # デフォルト値を書いておき，初回起動時のcontent作成に利用する
                "min_frequency": 2,
                "max_frequency": 20
            }
    ):
        super(CoherenceAnalysis, self).__init__(content)

    def run(self, x1: np.ndarray, x2: np.ndarray) -> dict[str, Any]:
        """
        解析を実行する

        Args:
            x1(np.ndarray): 解析対象のデータ. shape=(axis, timestep)
            x2(np.ndarray): 解析対象のデータ. shape=(axis, timestep)
        Returns:
            dict[str, Any]: 解析結果．項目名と値のdict
        """
        # 解析処理
        nfft = 2 ** 8
        noverlap = 2 ** 7
        Cyx, f = cohere(
            x2,
            x1,
            NFFT=nfft,
            Fs=self.content["sampling_rate"],
            window=window_hanning,
            noverlap=noverlap
        )   # matplotlib
        FREQ_LOW = 2
        FREQ_HIGH = 12
        xlim_l = FREQ_LOW
        xlim_r = FREQ_HIGH
        idx = [int(len(f) / f[-1] * xlim_l), int(len(f) / f[-1] * xlim_r)]
        f = f[idx[0]: idx[1]]
        df = f[1] - f[0]
        Cyx = Cyx[idx[0]: idx[1]]

        l = (len(x1) - noverlap) // (nfft - noverlap)
        z = 1 - np.power(0.05, 1 / (l - 1))
        # print("z: ", z)
        # print("significant points rate: ", len(Cyx[Cyx >= z]) / len(Cyx)) # 有意な値の割合
        Cyx = Cyx[Cyx >= z]
        # print(Cyx)
        coh = np.sum(Cyx) * df

        self.result = {"coherence": coh}
        return super(ConnectionAbortedError, self).run(x1, x2)

    def configure_ui(self) -> ft.Control:
        """
        設定項目のUIを作る．
        補足: ft.Controlは，様々なUIの構成要素の基底クラス

        Returns:
            ft.Control: 設定項目のUI．
        """
        return super(CoherenceAnalysis, self).configure_ui()


if __name__ == "__main__":
    analysis = CoherenceAnalysis()
    x = np.linspace(0, 10, 6000)
    y = np.sin(x)
    # TODO: テスト用の適切なデータにする
    x1 = np.tile(y[np.newaxis, :], (3, 1))
    x2 = np.tile(y[np.newaxis, :], (3, 1))
    print(analysis.run(x1, x2))
