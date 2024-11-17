from base import AnalysisMethodBase, AnalysisResult
from PIL import Image


class DummyAnalysis(AnalysisMethodBase):
    def run(self, data) -> AnalysisResult:
        return AnalysisResult(
            numerical_result={"value1": 1, "value2": 2},
            image_result={"image1": Image.new("RGB", (1, 1))},
        )