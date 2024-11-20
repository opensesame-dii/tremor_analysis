import dataclasses
from typing import Union

from PIL import Image


@dataclasses.dataclass
class AnalysisResult:
    """
    解析結果のデータを格納するクラス
    解析結果の数値データと画像データを，それぞれの項目名をキーとするdictに格納する
    """

    numerical_result: dict[str, Union[int, float]]
    image_result: dict[str, Image.Image]
