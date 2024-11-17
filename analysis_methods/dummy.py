from flet_runtime import Control
from analysis_methods.base import AnalysisMethodBase, AnalysisResult
from PIL import Image
from typing import Any, Optional


class DummyAnalysis(AnalysisMethodBase):
    def __init__(
        self,
        config: Optional[dict[str, Any]] = {
            "sampling_rate": 200,  # デフォルト値を書いておき，初回起動時のconfig作成に利用する
            "nperseg": 512,
            "min_frequency": 2,
            "max_frequency": 20,
        },
    ):
        super(DummyAnalysis, self).__init__(config)

    def run(self, data) -> AnalysisResult:
        return AnalysisResult(
            numerical_result={"value1": 1, "value2": 2},
            image_result={"image1": Image.new("RGB", (1, 1))},
        )

    def configure_ui(self) -> Control:
        print("configure_ui")
