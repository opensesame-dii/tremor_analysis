import csv
import itertools
import os
import platform
import subprocess
from pathlib import Path
from typing import Any

import flet as ft
import numpy as np
import yaml
from flet import ControlEvent

from tremor_analysis.analysis_methods.base import AnalysisMethodBase, AnalysisResult
from tremor_analysis.analysis_methods.dummy import (
    DummyAnalysis,
    DummyAnalysisCapableTwoData,
)
from tremor_analysis.utils.path import remove_extension


class MainApp:
    OUTPUT_FILE_EXTENSION = ".tremor.csv"
    ACCEPTABLE_FILE_EXTENSION = ".csv"

    def __init__(self) -> None:
        self.analysis_methods: list[AnalysisMethodBase] = [
            # SpectrogramAnalysis(),
            DummyAnalysis(),  # ここで解析手法のクラスをインスタンス化
            DummyAnalysisCapableTwoData(),
            # 他の解析手法もここに追加
        ]
        self.target_dir = ft.Text(value="Not Selected")
        self.log_content = ft.Text()
        self.file_num = 0
        self.pairs_num = 0

    def run(self):
        results_1file: dict[str, list[AnalysisResult]] = {}
        results_2files: list[AnalysisResult] = []
        file_list = self.scan()
        data1 = np.zeros((10, 10))  # 仮
        data2 = np.zeros((20, 20))
        data = [data1, data2]

        for file_pair in file_list:
            for file in file_pair:
                results_1file[file] = []
            # TODO: ファイル読み込み
            if len(file_pair) == 1:
                # TODO: dataとして読み込み data = [data1]
                pass
            elif len(file_pair) == 2:
                # TODO: dataとして読み込み data = [data1, data2]
                pass
            else:
                raise NotImplementedError

            for method in self.analysis_methods:
                if method.ACCEPTABLE_DATA_COUNT == 1:
                    for i, file in enumerate(file_pair):
                        result = method.run([data[i]])
                        results_1file[file].append(result)
                elif method.ACCEPTABLE_DATA_COUNT == 2 and len(file_pair) == 2:
                    # 左右の手のデータペアを受け入れる解析
                    result = method.run(data)
                    results_2files.append(result)
                else:
                    raise NotImplementedError
            self.append_result_file(
                results_1file=results_1file,
                results_2files=results_2files,
            )

    def append_result_file(
            self,
            results_1file: dict[str, list[AnalysisResult]],
            results_2files: list[AnalysisResult],
    ) -> None:
        filenames = list(results_1file.keys())  # ファイル名を入手
        # TODO: 単一ファイルの結果出力
        # TODO: 出力先ファイルの存在確認
        if ("result_1file" + self.OUTPUT_FILE_EXTENSION):
            pass
        # TODO: なかったら一通りの結果の列名をmethod_result.numerical_resultから取得してヘッダー作成
        for filename in filenames:
            for method_result in results_1file[filename]:
                method_result.numerical_result

        # TODO: ペアファイルの結果出漁
        if len(results_2files) != 0:
            # TODO: 出力先ファイルの存在確認
            # TODO: なかったら一通りの結果の列名をmethod_result.numerical_resultから取得してヘッダー作成
            # ファイル名は，filenamesを参照して取得
            pass

    def on_run_click(self, e: ControlEvent):
        """Buttonのon_clickでは, 引数にControlEventが渡されるが，run()では不要のため, この関数でwrapしている

        Args:
            e (ControlEvent): click event
        """
        self.run()

    def read_config_file(self, e: ControlEvent):
        with open("config.yaml") as file:
            self.config = yaml.safe_load(file)
        print(self.config)

    def write_config_file(self, e: ControlEvent):
        self.config["key1"] = "change"
        self.config["add_key"] = "add"
        with open("config.yaml", "w") as file:
            yaml.dump(self.config, file)
        print(self.config)

    # select folder
    def on_folder_picked(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.target_dir.value = e.path
            self.page.update()

    def show_pick_folder(self, _: ft.ControlEvent):
        self.folder_picker.get_directory_path()

    def on_scan_click(self, _: ft.ControlEvent):
        self.scan()

    # scan directory
    def scan(self) -> list[list[str]]:
        if self.target_dir.value != "Not Selected":
            file_list = []
            self.file_num = 0
            self.pairs_num = 0

            # 最大3階層まで再帰的にディレクトリを探索
            def recursive_search(directory, depth):
                if depth > 3:
                    return
                csv_files = [
                    f
                    for f in os.listdir(directory)
                    if f.endswith(self.ACCEPTABLE_FILE_EXTENSION) and not f.endswith(self.OUTPUT_FILE_EXTENSION)
                ]
                self.file_num += len(csv_files)
                if len(csv_files) == 2:
                    file_list.append(
                        tuple(os.path.join(directory, file) for file in csv_files)
                    )
                    self.pairs_num += 1

                elif len(csv_files) == 1:
                    file_list.append((os.path.join(directory, csv_files[0]),))
                else:
                    for item in os.listdir(directory):
                        path = os.path.join(directory, item)
                        if os.path.isdir(path):
                            recursive_search(path, depth + 1)

            recursive_search(self.target_dir.value, 0)

            # log_outputsの中身更新
            self.log_content.value = f"{self.file_num}files\n{self.pairs_num}pairs\nanalysis files\n{file_list}"

        else:  # Not Selected なら
            self.log_content.value = "No folder is selected"

        self.page.update()
        return file_list

    def on_open_result_click(self, _: ft.ControlEvent):
        self.open_result()

    # open result directory
    def open_result(self):
        if platform.system() == "Windows":  # Windows
            subprocess.Popen(["explorer", self.target_dir.value], shell=True)
        elif platform.system() == "Darwin":  # Mac
            subprocess.Popen(["open", self.target_dir.value])
        else:  # Linux
            subprocess.Popen(["xdg-open", self.target_dir.value])
        return

    def build_ui(self):
        self.folder_picker = ft.FilePicker(on_result=self.on_folder_picked)
        self.page.overlay.append(self.folder_picker)
        select_folder_button = ft.Row(
            [
                ft.OutlinedButton(text="Select Folder", on_click=self.show_pick_folder),
                self.target_dir,
            ]
        )
        scan_button = ft.OutlinedButton(text="Scan", on_click=self.on_scan_click)
        run_button = ft.OutlinedButton(text="Run", on_click=self.on_run_click)
        open_result_button = ft.OutlinedButton(
            text="Open Result", on_click=self.on_open_result_click
        )
        apply_button = ft.OutlinedButton(text="Apply&Save Settings", on_click="")
        settings = ft.Container(
            content=ft.Column(
                [
                    ft.Text("General Settings"),
                    ft.Row([ft.Text("Row start"), ft.TextField(height=40, width=50)]),
                    ft.Row(
                        [ft.Text("Column start"), ft.TextField(height=40, width=50)]
                    ),
                    ft.Row([ft.Text("Sensors num"), ft.TextField(height=40, width=50)]),
                    ft.Row([ft.Text("Encoding"), ft.TextField(height=40, width=100)]),
                ]
                + [method.configure_ui() for method in self.analysis_methods]
                + [
                    apply_button,
                ]
            ),
            padding=25,
        )
        log_outputs = ft.Container(
            content=(
                ft.Column(
                    [
                        ft.Text("Log Outputs"),
                        ft.Container(
                            content=self.log_content,
                            border=ft.border.all(1, "black"),
                            height=400,
                            width=300,
                        ),
                    ],
                    scroll=ft.ScrollMode.ALWAYS,
                )
            ),
            width="",
            height="",
        )

        self.page.add(
            select_folder_button,
            ft.Row(
                [
                    ft.Container(
                        content=(
                            ft.Column(
                                [settings, scan_button, run_button, open_result_button]
                            )
                        ),
                        margin=10,
                        width=300,
                    ),
                    log_outputs,
                ]
            ),
        )
        return

    def main(self, page: ft.Page):

        self.page = page

        # page setting
        self.page.title = "tremor_analysis"
        self.page.window_width = 700  # 幅
        self.page.window_height = ""  # 高さ
        self.page.window_top = ""  # 位置(TOP)
        self.page.window_left = ""  # 位置(LEFT)
        self.page.window_always_on_top = True  # ウィンドウを最前面に固定

        self.build_ui()
        self.page.update()
        page.update()


class SpectrogramAnalysis:
    def __init__(self):
        self.data = 3
        # self.frame_range = None

    def run(
        self,
    ) -> dict[str, Any]:
        self.val = 1 + self.data
        self.answer = {"answer": self.val}

    def import_config(self):
        with open("config.yaml") as file:
            self.config = yaml.safe_load(file)
        self.max = self.config["SpectrogramAnalysis"]["max"]
        self.min = self.config["SpectrogramAnalysis"]["min"]

    def export_config(self):
        return self.config["SpectrogramAnalysis"]

    def build_result_ui(self):
        self.text_area = ft.Text("設定項目")
        self.val_area = ft.TextField(hint_text="int")
        x = ft.Container(ft.Row(self.text_area, self.val_area))
        return x

        # Main_appでのrunでこれも呼ぶ？？

    def update_ui(self):
        # 横並びで一塊にして配置したい　https://qiita.com/donraq/items/1ac45ddfe0a803a94e27
        # ここでつくる=>Main_appにUI関係のmake_picみたいなやつを作って並べる
        print("test")


def main():
    app = MainApp()
    ft.app(target=app.main)


if __name__ == "__main__":
    main()
