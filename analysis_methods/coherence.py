from typing import Any, Optional

import flet as ft
import numpy as np
from scipy.signal import detrend, spectrogram, get_window
# from analysis_methods.base import AnalysisMethodBase
from base import AnalysisMethodBase


class CoherenceAnalysis(AnalysisMethodBase):
    """
    Args:

    Params

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
        super(CoherenceAnalysis, self).__init__(content)

    def run(self, data: np.ndarray) -> dict[str, Any]:
        """
        解析を実行する

        Args:

        """
