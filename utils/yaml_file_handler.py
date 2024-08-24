from typing import Any


class YamlFileHandler:


    """
    yamlファイルの読み書きを行う
    Args:
        file_path(str):yamファイルのパス
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.content: dict[str, Any] = {}
        if (yamlファイルがない場合):
            self.export_yaml()
        self.content = self.import_yaml()
        # self.content の値は，dictになるようにアプリケーション側で制御

    def import_yaml(self):
        """
        yamlファイルを読み込んで `self.content` に格納する
        """

        with open(self.file_path, "r") as file:
            self.content = load(file)  # なんらかの方法でファイルを読み込む

    def export_yaml(self):
        """
        `self.content` をyamlファイルに書き込む
        """

        with open(self.file_path, "w") as file:
            dump(self.content, file)  # なんらかの方法でファイルに出力する