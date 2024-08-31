from typing import Any
import yaml
import os


class YamlFileHandler:
    """
    yamlファイルの読み書きを行う
    Args:
        file_path(str):yamlファイルのパス
    """

    def __init__(self, file_path: str):
        content: dict[str, Any] = {}  # MainAppから受け取るように要変更
        self.file_path = file_path
        self.content: dict[str, Any] = {}
        self.content: dict[str, Any] = content
        if not os.path.isfile(self.file_path):  # yamlファイルが無かったら新規作成
            self.export_yaml()
        self.content = self.import_yaml()
        # self.content の値は，dictになるようにアプリケーション側で制御

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
            print("imported self.content:", self.content)  # 確認用

    def export_yaml(self):
        """
        `self.content` をyamlファイルに書き込む
        """
        with open(self.file_path, "w") as file:
            yaml.safe_dump(self.content, file)
            print("exported self.content:", self.content)  # 確認用


if __name__ == "__main__":
    YamlFileHandler("config.yaml")
