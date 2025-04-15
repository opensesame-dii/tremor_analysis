import os
from typing import Any

import yaml
from dictknife import deepmerge


class YamlFileHandler:
    """
    yamlファイルの読み書きを行う
    Args:
        file_path (str): yamlファイルのパス
        content (dict[str, Any]): 読み込む項目と初期値。MainAppから渡される
            {解析クラス名 (str):
                {項目名 (str): 初期値 (int or float)}
            }
            のようにネストした辞書型になる
            全体の設定項目の場合、解析クラス名は"_general_"
    """

    def __init__(self, file_path: str, content: dict[str, Any]):
        self.file_path = file_path
        self.content: dict[str, Any] = content  # デフォルト値
        if not os.path.isfile(self.file_path):  # yamlファイルが無かったら新規作成
            self.export_yaml()
        self.import_yaml()  # 過去の設定を反映
        self.export_yaml()

    def import_yaml(self):
        """
        yamlファイルを読み込んで `self.content` に格納する
        読み込む項目について、項目がyamlファイルに既に存在する場合、指定された値を読み取る
        項目が存在しない場合、初期値を格納する
        """
        with open(self.file_path, "r") as file:
            current_file_content: dict[str, Any] = yaml.safe_load(file)
            self.content = deepmerge(self.content, current_file_content)

    def export_yaml(self):
        """
        `self.content` をyamlファイルに書き込む
        'self.content'のうち新しい情報をyamlファイルに書き込む
        """
        if not os.path.isfile(self.file_path):  # yamlファイルが無かったら新規作成
            with open(self.file_path, "w") as file:
                yaml.safe_dump(self.content, file)

        with open(self.file_path, "r") as file:
            current_file_content: dict[str, Any] = yaml.safe_load(file)
        for key, value in self.content.items():
            current_file_content[key] = value

        with open(self.file_path, "w") as file:
            yaml.safe_dump(current_file_content, file)


if __name__ == "__main__":
    file_path = "configa.yaml"
    content = {"key1": 1, "key3": 2}
    yaml_file_handler = YamlFileHandler(file_path, content)
    yaml_file_handler.content["key3"] = 3
    yaml_file_handler.export_yaml()
    with open(file_path, "r") as file:
        for line in file.readlines():
            print(line)
    yaml_file_handler = YamlFileHandler(file_path, content)
    print(yaml_file_handler.content)
    os.remove(file_path)
