from typing import Any
import yaml
import os


class YamlFileHandler:
    """
    yamlファイルの読み書きを行う
    Args:
        file_path(str):yamlファイルのパス
        content(dict[str, Any]): 読み込む項目と初期値　MainAppから渡される
    """

    def __init__(self, file_path: str, content: dict[str, Any]):
        self.file_path = file_path
        self.content: dict[str, Any] = content
        if not os.path.isfile(self.file_path):  # yamlファイルが無かったら新規作成
            self.export_yaml()
        self.content = self.import_yaml()
        self.export_yaml()

    def import_yaml(self):
        """
        yamlファイルを読み込んで `self.content` に格納する
        読み込む項目について、項目がyamlファイルに既に存在する場合、指定された値を読み取る
        項目が存在しない場合、初期値を格納する
        """
        with open(self.file_path, "r") as file:
            current_file_content: dict[str, Any] = yaml.safe_load(file)
            for key in current_file_content.keys():
                if key in self.content:
                    self.content[key] = current_file_content[key]
        return (self.content)

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
    file_path = "configa.yaml"  # 仮
    content = {"key1": 1, "key3": 2}  # 仮
    YamlFileHandler(file_path, content)
