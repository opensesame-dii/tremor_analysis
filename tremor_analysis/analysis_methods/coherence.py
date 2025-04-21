# https://github.com/opensesame-dii/tremor_analysis_python/blob/master/multiple_analysis/multiple.py#L960
# ft_coherence関数に対応

from typing import Any, Optional

import flet as ft
import numpy as np
from matplotlib.mlab import cohere, window_hanning
from tremor_analysis.analysis_methods.base import AnalysisMethodBase


class CoherenceAnalysis(AnalysisMethodBase):
    """
    Args:
        config(Optional[dict[str, Any]]): 解析クラスで使う設定．
            アプリ初回起動時は省略することで，デフォルト値が使われる．

    Params
        sampling_rate: int/float
            sampling rate
    """

    ACCEPTABLE_DATA_COUNT: int = 2

    def __init__(
        self,
        config: Optional[dict[str, Any]] = {
            "sampling_rate": 200,  # デフォルト値を書いておき，初回起動時のconfig作成に利用する
            "min_frequency": 2,
            "max_frequency": 20,
        },
    ):
        super(CoherenceAnalysis, self).__init__(config)

    def run(self, data: list[np.ndarray]) -> dict[str, Any]:
        """
        解析を実行する

        Args:
            data: list[np.ndarray]:解析対象のデータ

        Returns:
            dict[str, Any]: 解析結果．項目名と値のdict
        """
        # 解析処理
        x1 = data[0]
        x2 = data[1]
        nfft = 2**8
        noverlap = 2**7
        Cyx, f = cohere(
            x2,
            x1,
            NFFT=nfft,
            Fs=self.config["sampling_rate"],
            window=window_hanning,
            noverlap=noverlap,
        )  # matplotlib
        FREQ_LOW = 2
        FREQ_HIGH = 12
        xlim_l = FREQ_LOW
        xlim_r = FREQ_HIGH
        idx = [int(len(f) / f[-1] * xlim_l), int(len(f) / f[-1] * xlim_r)]
        f = f[idx[0] : idx[1]]
        df = f[1] - f[0]
        Cyx = Cyx[idx[0] : idx[1]]

        l = (len(x1) - noverlap) // (nfft - noverlap)
        z = 1 - np.power(0.05, 1 / (l - 1))
        Cyx = Cyx[Cyx >= z]
        coh = np.sum(Cyx) * df

        result = {"coherence": coh}
        return result


if __name__ == "__main__":
    analysis = CoherenceAnalysis()
    # TODO: テスト用の適切なデータにする,今はchatGPTに書いてもらった適当なやつ
    sampling_rate = 1000  # 1kHz のサンプリングレート
    t = np.arange(0, 1.0, 1.0 / sampling_rate)
    data = [np.sin(2 * np.pi * 50 * t), np.sin(2 * np.pi * 80 * t)]

    print(analysis.run(data))
