# https://github.com/opensesame-dii/tremor_analysis_python/blob/master/multiple_analysis/multiple.py#L733
# power_density_analize関数に対応

from typing import Any, Optional

import flet as ft
import numpy as np

# from analysis_methods.base import AnalysisMethodBase
from base import AnalysisMethodBase
from scipy.signal import butter, detrend, get_window, sosfilt, spectrogram
from sklearn.decomposition import PCA


class PowerDensityAnalysis(AnalysisMethodBase):
    """
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
            "max_frequency": 20,
        },
    ):
        super(PowerDensityAnalysis, self).__init__(content)

        # https://github.com/opensesame-dii/tremor_analysis_python/blob/master/multiple_analysis/multiple.py#L135
        self.sampling_rate = 200
        self.segment_duration_sec = 5

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
        for i in range(3):
            f, t, spec = spectrogram(
                detrend(data[i]),
                self.content["sampling_rate"],
                window=get_window("hamming", int(self.content["nperseg"])),
                nperseg=int(self.content["nperseg"]),
                noverlap=int(self.content["nperseg"] * 0.75),
                nfft=2**12,
                mode="complex",
            )  # scipy
            self.specs.append(np.sum(np.power(np.abs(spec), 1), axis=1) / (len(t)))

        # convert to 3-dimensional ndarray
        specs = np.array(self.specs)  # specs.shape: (3, 640)

        # trim into frequency range
        f_range = (
            np.array([self.content["min_frequency"], self.content["max_frequency"]])
            * len(f)
            * 2
            // self.content["sampling_rate"]
        )
        specs = specs[:, f_range[0] : f_range[1]]
        f = f[f_range[0] : f_range[1]]

        # add norm
        specs = np.append(specs, [np.linalg.norm(specs, axis=0)], axis=0)

        peak_amp = np.max(specs[3])
        peak_idx = np.where(specs[3] == peak_amp)
        peak_freq = f[peak_idx[0][0]]
        tsi = self.tremor_stability_index(data, self.content["sampling_rate"])

        result = {
            "peak_amp": peak_amp.item(),
            "peak_freq": peak_freq.item(),
            "tsi": tsi,
        }
        return super(PowerDensityAnalysis, self).run(data)

    def configure_ui(self) -> ft.Control:
        """
        設定項目のUIを作る．
        補足: ft.Controlは，様々なUIの構成要素の基底クラス

        Returns:
            ft.Control: 設定項目のUI．
        """
        return super(PowerDensityAnalysis, self).configure_ui()

    # https://github.com/opensesame-dii/tremor_analysis_python/blob/master/multiple_analysis/multiple.py#L907
    def tremor_stability_index(self, data, fs) -> int:
        """
        Tremor Stability Index

        Params
        x: array-like
            data
        fs: int/float
            sampling rate
        """
        # highpass filter
        sos = butter(N=3, Wn=0.1, btype="highpass", fs=fs, output="sos")
        data = sosfilt(sos, data, axis=0)

        # principal component analysis
        pca = PCA(n_components=1)
        x = np.ravel(pca.fit_transform(np.array(data).T))
        length = len(x)

        nperseg = self.sampling_rate * self.segment_duration_sec
        nTimesSpectrogram = 500
        L = np.min((length, nperseg))
        noverlap = np.ceil(L - (length - L) / (nTimesSpectrogram - 1))
        noverlap = int(np.max((1, noverlap)))
        amplitude_spectrum = np.abs(np.fft.fft(x))
        freqs = np.fft.fftfreq(len(x), d=1 / fs)
        max_freq = freqs[np.argmax(amplitude_spectrum[: len(x) // 2])]

        if max_freq <= 2:
            max_freq = (
                2.001  # to create bandpass filter, max_freq - 2 maust be larger than 0
            )
        elif max_freq > 9:
            max_freq = 9

        sos = butter(
            N=3, Wn=(max_freq - 2, max_freq + 2), btype="bandpass", fs=fs, output="sos"
        )
        x = sosfilt(sos, x, axis=0)

        idx = 1
        zero_crossing = np.empty(0)
        while idx < length:
            if x[idx - 1] < 0 and x[idx] >= 0:
                zero_crossing = np.append(zero_crossing, idx)
            idx += 1

        f = fs / np.diff(np.array(zero_crossing))
        delta_f = np.diff(f)
        if len(delta_f) == 0:
            q75, q25 = 0, 0
        else:
            q75, q25 = np.percentile(delta_f, [75, 25], interpolation="nearest")

        # tsi
        return q75 - q25


if __name__ == "__main__":
    analysis = PowerDensityAnalysis()
    x = np.linspace(0, 10, 6000)
    y = np.sin(x)
    data = np.tile(y[np.newaxis, :], (3, 1))
    print(analysis.run(data))
