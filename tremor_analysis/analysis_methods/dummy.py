from typing import Optional

from PIL import Image

from tremor_analysis.analysis_methods.base import AnalysisMethodBase
from tremor_analysis.data_models.analysis_result import AnalysisResult
from tremor_analysis.data_models.config_parameter import ConfigParameter


class DummyAnalysis(AnalysisMethodBase):
    ACCEPTABLE_DATA_COUNT = 1
    config = [
        ConfigParameter(name="sampling_rate (Hz, float)", value=200, type=float),
        ConfigParameter(name="nperseg (n, int)", value=512, type=int),
    ]

    def __init__(
        self,
        config: Optional[list[ConfigParameter]] = None,
    ):
        super(DummyAnalysis, self).__init__(config)

    def run(self, data) -> AnalysisResult:
        return AnalysisResult(
            analysis_method_class=DummyAnalysis,
            numerical_result={"value1": 1, "value2": 2},
            image_result={"image1": Image.new("RGB", (1, 1))},
            filename1=None,  # ファイル名を取得する
            filename2=None,
        )


class DummyAnalysisCapableTwoData(AnalysisMethodBase):
    ACCEPTABLE_DATA_COUNT = 2
    config = [
        ConfigParameter(name="min_frequency (Hz, int)", value=2, type=int),
        ConfigParameter(name="max_frequency (Hz, int)", value=20, type=int),
    ]

    def __init__(
        self,
        config: Optional[list[ConfigParameter]] = None,
    ):
        super(DummyAnalysisCapableTwoData, self).__init__(config)

    def run(self, data) -> AnalysisResult:
        return AnalysisResult(
            numerical_result={"value1": 1, "value2": 2},
            image_result={"image1": Image.new("RGB", (1, 1))},
            analysis_method_class=type(self),
            filename1=None,
            filename2=None,
        )
