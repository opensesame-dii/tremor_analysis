# https://github.com/opensesame-dii/tremor_analysis_python/blob/master/multiple_analysis/multiple.py#L619
# spectrogram_analize関数に対応

from typing import Any, Optional

import flet as ft
import numpy as np
from scipy.signal import detrend, spectrogram, get_window
# from analysis_methods.base import AnalysisMethodBase
from base import AnalysisMethodBase


class SpectrogramAnalysis(AnalysisMethodBase):
    """
    振動の解析クラス

    Args:
        content(Optional[dict[str, Any]]): 解析クラスで使う設定．
            アプリ初回起動時は省略することで，デフォルト値が使われる．

    Params
        sampling_rate: int/float
            sampling rate
        nperseg: int
            sample number per stft segment
    """

    def __init__(
            self,
            content: Optional[dict[str, Any]] = {
                "sampling_rate": 200,  # デフォルト値を書いておき，初回起動時のcontent作成に利用する
                "nperseg": 512,
                "min_frequency": 2,
                "max_frequency": 20
            }
    ):
        super(SpectrogramAnalysis, self).__init__(content)

    def run(self, data: np.ndarray) -> dict[str, Any]:
        """
        解析を実行する．

        Args:
            data(np.ndarray): 解析対象のデータ. shape=(axis, timestep)

        Returns:
            dict[str, Any]: 解析結果．項目名と値のdict
        """
        # 解析処理
        self.specs = []
        x_length = len(data[0])
        nTimesSpectrogram = 500
        L = np.min((x_length, self.content["nperseg"]))
        noverlap = np.ceil(L - (x_length - L) / (nTimesSpectrogram - 1))
        noverlap = int(np.max((1, noverlap)))

        for i in range(3):
            # scipy
            f, t, spec = spectrogram(
                detrend(data[i]),
                self.content["sampling_rate"],
                window=get_window("hamming", int(self.content["nperseg"])),
                nperseg=int(self.content["nperseg"]),
                noverlap=noverlap,
                nfft=2**12,
                mode="magnitude",
            )
            self.specs.append(np.abs(spec))

        # convert to 3-dimensional ndarray
        specs = np.array(self.specs)    # specs.shape: (3, 640, 527)

        # trim into frequency range
        f_range = (
            np.array([self.content["min_frequency"], self.content["max_frequency"]]) * len(f) * 2 // self.content["sampling_rate"]
        )
        specs = specs[:, f_range[0]: f_range[1], :]
        f = f[f_range[0]: f_range[1]]

        # add norm
        specs = np.append(specs, [np.linalg.norm(specs, axis=0)], axis=0)

        peak_amp = np.max(specs[3, :, :])
        peak_idx = np.where(specs[3] == peak_amp)
        peak_freq = f[peak_idx[0][0]]
        peak_time = t[peak_idx[1][0]]

        result: dict[str, Any] = {
            "peak_amp": peak_amp.item(),
            "peak_freq": peak_freq.item(),
            "peak_time": peak_time.item()
        }
        return result

    def configure_ui(self) -> ft.Control:
        """
        設定項目のUIを作る．
        補足: ft.Controlは，様々なUIの構成要素の基底クラス

        Returns:
            ft.Control: 設定項目のUI．

        """
        return super(SpectrogramAnalysis, self).configure_ui()


if __name__ == "__main__":
    analysis = SpectrogramAnalysis()
    x = np.linspace(0, 10, 6000)
    y = np.sin(x)
    data = np.tile(y[np.newaxis, :], (3, 1))
    print(analysis.run(data))
