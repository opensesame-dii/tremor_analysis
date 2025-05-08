# https://github.com/opensesame-dii/tremor_analysis_python/blob/master/multiple_analysis/multiple.py#L619
# spectrogram_analize関数に対応

from typing import Any, Optional

import flet as ft
import numpy as np
from scipy.signal import detrend, spectrogram, get_window
from tremor_analysis.analysis_methods.base import AnalysisMethodBase

from tremor_analysis.data_models.analysis_result import AnalysisResult
from tremor_analysis.data_models.config_parameter import ConfigParameter, ConfigList


class SpectrogramAnalysis(AnalysisMethodBase):
    """
    振動の解析クラス

    Args:
        config(Optional[dict[str, Any]]): 解析クラスで使う設定．
            アプリ初回起動時は省略することで，デフォルト値が使われる．

    Params
        sampling_rate: int/float
            sampling rate
        nperseg: int
            sample number per stft segment
    """

    ACCEPTABLE_DATA_COUNT: int = 1  # 実行時に受け取るべきデータの配列の数
    config: ConfigList = ConfigList(
        [
            ConfigParameter(
                key="sampling_rate",
                display_name="sampling rate",
                value=200,
                type=int,
            ),
            ConfigParameter(
                key="nperseg",
                display_name="sample num per segment",
                value=512,
                type=int,
            ),
            ConfigParameter(
                key="min_frequency",
                display_name="min frequency",
                value=2,
                type=int,
            ),
            ConfigParameter(
                key="max_frequency",
                display_name="max_frequency",
                value=20,
                type=int,
            ),
        ]
    )

    def __init__(
        self,
        config: ConfigList = None,
    ):
        super(SpectrogramAnalysis, self).__init__(config)

    def run(self, data: list[np.ndarray]) -> AnalysisResult:
        """
        解析を実行する．

        Args:
            data(list[np.ndarray]): 解析対象のデータ.
                それぞれのnp.arrayはshape=(axis, timestep)

        Returns:
            dict[str, Any]: 解析結果．項目名と値のdict
        """
        # 解析処理
        data = data[0]
        specs = []
        x_length = len(data[0])
        nTimesSpectrogram = 500
        L = np.min((x_length, self.config["nperseg"].value))
        noverlap = np.ceil(L - (x_length - L) / (nTimesSpectrogram - 1))
        noverlap = int(np.max((1, noverlap)))

        for i in range(3):
            # scipy
            f, t, spec = spectrogram(
                detrend(data[i]),
                self.config["sampling_rate"].value,
                window=get_window("hamming", int(self.config["nperseg"].value)),
                nperseg=int(self.config["nperseg"].value),
                noverlap=noverlap,
                nfft=2**12,
                mode="magnitude",
            )
            specs.append(np.abs(spec))

        # convert to 3-dimensional ndarray
        specs = np.array(specs)  # specs.shape: (3, 640, 527)

        # trim into frequency range
        f_range = (
            np.array(
                [self.config["min_frequency"].value, self.config["max_frequency"].value]
            )
            * len(f)
            * 2
            // self.config["sampling_rate"].value
        )
        specs = specs[:, f_range[0] : f_range[1], :]
        f = f[f_range[0] : f_range[1]]

        # add norm
        specs = np.append(specs, [np.linalg.norm(specs, axis=0)], axis=0)

        peak_amp = np.max(specs[3, :, :])
        peak_idx = np.where(specs[3] == peak_amp)
        peak_freq = f[peak_idx[0][0]]
        peak_time = t[peak_idx[1][0]]

        result: dict[str, Any] = {
            "peak_amp": peak_amp.item(),
            "peak_freq": peak_freq.item(),
            "peak_time": peak_time.item(),
        }
        return result


if __name__ == "__main__":
    analysis = SpectrogramAnalysis()
    x = np.linspace(0, 10, 6000)
    y = np.sin(x)
    data = [np.tile(y[np.newaxis, :], (3, 1))]
    print(analysis.run(data))
