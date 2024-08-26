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
        self.file_path = file_path
        self.content: dict[str, Any] = {}
        if not os.path.isfile(self.file_path):
            self.export_yaml()
        self.content = self.import_yaml()
        # self.content の値は，dictになるようにアプリケーション側で制御

    def import_yaml(self):
        """
        yamlファイルを読み込んで `self.content` に格納する
        """
        with open(self.file_path, "r") as file:
            self.content = yaml.safe_load(file)
            print("imported self.content:", self.content)  # 確認用

    def export_yaml(self):
        """
        `self.content` をyamlファイルに書き込む
        """

        with open(self.file_path, "w") as file:
            yaml.safe_dump(self.content, file)


if __name__ == "__main__":
    handler = YamlFileHandler("config.yaml")
