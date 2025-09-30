import dataclasses
from typing import Type, Union

from PIL import Image


@dataclasses.dataclass
class AnalysisResult:
    """
    解析結果のデータを格納するクラス
    解析結果の数値データと画像データを，それぞれの項目名をキーとするdictに格納する
    """

    analysis_method_class: type
    numerical_result: dict[str, Union[int, float]]
    image_result: dict[str, Image.Image]
    filename1: Union[Type[None], Type[str]]
    filename2: Union[Type[None], Type[str]]
