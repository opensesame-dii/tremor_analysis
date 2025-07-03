# https://github.com/opensesame-dii/tremor_analysis_python/blob/master/multiple_analysis/multiple.py#L733
# power_density_analize関数に対応

from typing import Any, Optional

import flet as ft
import numpy as np
from matplotlib import pyplot as plt
from scipy.signal import butter, detrend, get_window, sosfilt, spectrogram
from sklearn.decomposition import PCA

from tremor_analysis.analysis_methods.base import AnalysisMethodBase
from tremor_analysis.data_models.analysis_result import AnalysisResult
from tremor_analysis.data_models.config_parameter import ConfigList, ConfigParameter
from tremor_analysis.utils.result_image import fig2img


class PowerDensityAnalysis(AnalysisMethodBase):
    """
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
                display_name="sample num per stft segment",
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
            ConfigParameter(
                key="segment_duration_sec",
                display_name="segment duration sec",
                value=5,
                type=int,
            ),
        ]
    )

    def __init__(
        self,
        config: ConfigList = None,
    ):
        super(PowerDensityAnalysis, self).__init__(config)

    def run(self, data: list[np.ndarray]) -> AnalysisResult:
        """
        解析を実行する．

        Args:
            data(list[np.ndarray]): 解析対象のデータ.
                それぞれのnp.ndarrayはshape=(axis, timestep)

        Returns:
            dict[str, Any]: 解析結果．項目名と値のdict
        """
        # 解析処理
        data = data[0]
        specs = []
        for i in range(3):
            f, t, spec = spectrogram(
                detrend(data[:, i]),
                self.config["sampling_rate"].value,
                window=get_window("hamming", int(self.config["nperseg"].value)),
                nperseg=int(self.config["nperseg"].value),
                noverlap=int(self.config["nperseg"].value * 0.75),
                nfft=2**12,
                mode="complex",
            )  # scipy
            specs.append(np.sum(np.power(np.abs(spec), 1), axis=1) / (len(t)))

        # convert to 3-dimensional ndarray
        specs = np.array(specs)  # specs.shape: (3, 640)

        # trim into frequency range
        f_range = (
            np.array(
                [self.config["min_frequency"].value, self.config["max_frequency"].value]
            )
            * len(f)
            * 2
            // self.config["sampling_rate"].value
        )
        specs = specs[:, f_range[0] : f_range[1]]
        f = f[f_range[0] : f_range[1]]

        # add norm
        specs = np.append(specs, [np.linalg.norm(specs, axis=0)], axis=0)

        peak_amp = np.max(specs[3])
        peak_idx = np.where(specs[3] == peak_amp)
        peak_freq = f[peak_idx[0][0]]
        tsi = self.tremor_stability_index(data, self.config["sampling_rate"].value)

        # TODO: FWHM(full width half maximum), HWP(half-width power) の実装
        image, is_estimated, fwhm, hwp = self.create_result_image(specs, f)

        return AnalysisResult(
            analysis_method_class=type(self),
            numerical_result={
                "peak_amp": peak_amp.item(),
                "peak_freq": peak_freq.item(),
                "TSI": tsi,
                "FWHM": fwhm,
                "HWP": hwp,
                "is_estimated": is_estimated,
            },
            image_result={"power_density": image},
            filename1=None,
            filename2=None,
        )

    def create_result_image(self, specs: np.ndarray, f: np.ndarray) -> ft.Image:
        """
        Create a result image from the spectrogram data.

        Args:
            specs (np.ndarray): Spectrogram data.

        Returns:
            ft.Image: Result image.
        """

        # spectral amptitude
        vmin = np.min(specs)
        vmax = np.max(specs)

        fig, axs = plt.subplots(
            2, 3, figsize=(12, 6), gridspec_kw={"height_ratios": [1, 1]}
        )

        # upper_freq
        ax_pca = plt.subplot2grid((2, 4), (0, 0), colspan=3)
        ax_pca.set_ylim(0, vmax * 1.2)
        ax_pca.set_title("Spectral Amplitude")
        ax_pca.set_xlabel("Frequency [Hz]")
        ax_pca.set_ylabel("Amplitude")
        ax_pca.plot(f, specs[3])

        titles = ["X", "Y", "Z"]
        for i in range(3):
            ax = plt.subplot2grid((2, 4), (1, i))
            ax.set_ylim(0, vmax * 1.2)
            ax.set_title(titles[i])
            ax.set_xlabel("Frequency [Hz]")
            ax.set_ylabel("Amplitude")
            ax.plot(f, specs[i])
        # TODO: fwhmの結果から，グラフの色を塗る領域を決める
        is_estimated, lower_freq, upper_freq, hwp, fwhm = self.full_width_half_maximum(
            f, specs[3]
        )
        if lower_freq is not None and upper_freq is not None:
            ax_pca.fill_between(
                f[lower_freq:upper_freq],
                specs[3, lower_freq:upper_freq],
                color="r",
                alpha=0.5,
            )

        image = fig2img(fig)
        plt.close(fig)
        return image, is_estimated, fwhm, hwp

    def full_width_half_maximum(self, x, y):
        """
        calcurate Full-width Half Maximum and Half-witdh power

        Params
        x: array-like
        y: array-like

        Retuerns
        is_estimated: bool
            whether estimation value is used
        lower_freq: int
            lower_freq limit index
        upper_freq: int
            upper_freq limit index
        lower_value: int/float
            lower_freq limit value (approximate)
        upper_value: int/float
            upper_freq limit value (approximate)
        hwp: int/float
            Half-width power
        """
        y_ndarray = np.array(y)
        length = len(y_ndarray)
        peak_val_half = np.max(y_ndarray) / 2
        peak_idx = y_ndarray.argmax()
        lower_freq = peak_idx
        upper_freq = peak_idx
        d = np.abs(x[1] - x[0])
        is_estimated = False

        while lower_freq > 0 and y_ndarray[lower_freq] > peak_val_half:
            lower_freq -= 1
        if y_ndarray[lower_freq] != peak_val_half and lower_freq != 0:
            lower_value = x[lower_freq] + d * (
                peak_val_half - y_ndarray[lower_freq]
            ) / (
                y_ndarray[lower_freq + 1] - y_ndarray[lower_freq]
            )  # linear interpolation
        else:
            lower_value = x[lower_freq]

        while upper_freq < length - 1 and y_ndarray[upper_freq] > peak_val_half:
            upper_freq += 1
        if y_ndarray[upper_freq] != peak_val_half and upper_freq != length - 1:
            upper_value = x[upper_freq] - d * (
                peak_val_half - y_ndarray[upper_freq]
            ) / (
                y_ndarray[upper_freq - 1] - y_ndarray[upper_freq]
            )  # linear interpolation
        else:
            upper_value = x[upper_freq]

        if lower_freq == 0 and upper_freq == length - 1:
            return (False, None, None, None, None, None)

        # judge whether estimation value is used.
        if lower_freq == 0:
            is_estimated = True
            upper_value = x[upper_freq]
            lower_value = x[peak_idx] - (x[upper_freq] - x[peak_idx])
            hwp = np.sum(y_ndarray[peak_idx:upper_freq]) * d * 2
        elif upper_freq == length - 1:
            is_estimated = True
            lower_value = x[lower_freq]
            upper_value = x[peak_idx] + (x[peak_idx] - x[lower_freq])
            hwp = np.sum(y_ndarray[lower_freq:peak_idx]) * d * 2
        else:
            # not estimated
            hwp = np.sum(y_ndarray[lower_freq:upper_freq]) * d

        if upper_value is None and lower_value is None:
            fwhm = float("nan")
            hwp = float("nan")
            is_estimated = 0  # False
        elif is_estimated:
            fwhm = upper_value - lower_value
            is_estimated = 1  # True
        else:
            fwhm = upper_value - lower_value
            is_estimated = 0  # False

        return (is_estimated, lower_freq, upper_freq, hwp, fwhm)

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
        # TODO ↓のnpersegはconfigのとは別？
        nperseg = (
            self.config["sampling_rate"].value
            * self.config["segment_duration_sec"].value
        )
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
    data = [np.tile(y[np.newaxis, :], (3, 1))]
    print(analysis.run(data))
