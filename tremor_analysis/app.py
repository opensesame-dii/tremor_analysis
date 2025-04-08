import csv
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
from tremor_analysis.data_models.config_parameter import ConfigParameter
from tremor_analysis.ui.text_field_with_type import TextFieldWithType
from tremor_analysis.utils.yaml_file_handler import YamlFileHandler

CONFIG_FILE_PATH = Path.home() / ".tremor_analysis_config.yaml"


class MainApp:
    CONFIG_DEFAULT_VALUE: list[ConfigParameter] = [
        ConfigParameter(name="Row start", value=1, type=int),
        ConfigParameter(name="Column start", value=1, type=int),
        ConfigParameter(name="Encoding", value="utf-8", type=str),
    ]
    OUTPUT_FILE_EXTENSION = ".tremor.csv"
    ACCEPTABLE_FILE_EXTENSION = ".csv"

    def __init__(self) -> None:
        self.analysis_methods: list[AnalysisMethodBase] = [
            # SpectrogramAnalysis(),
            DummyAnalysis(),  # ここで解析手法のクラスをインスタンス化
            DummyAnalysisCapableTwoData(),
            # 他の解析手法もここに追加
        ]
        self.yaml_file_handler = YamlFileHandler(
            CONFIG_FILE_PATH,
            {
                "_general_": {default.name: default.value}
                for default in self.CONFIG_DEFAULT_VALUE
            }
            | {
                method.__class__.__name__: {entry.name: entry.value}
                for method in self.analysis_methods
                for entry in method.config
            },
        )
        self.apply_config_on_each_method()
        self.target_dir = ft.Text(value="Not Selected")
        self.log_content = ft.Text()
        self.file_num = 0
        self.pairs_num = 0

        self.general_setting_fields: dict[str, TextFieldWithType] = {}

    def run(self):
        results_1file: list[AnalysisResult] = []
        results_2files: list[AnalysisResult] = []
        file_list = self.scan()
        data1 = np.zeros((10, 10))  # 仮
        data2 = np.zeros((20, 20))
        data = [data1, data2]

        for file_pair in file_list:
            # TODO: ファイル読み込み
            if len(file_pair) == 1:
                # TODO: dataとして読み込み data = [data1]
                pass
            elif len(file_pair) == 2:
                # TODO: dataとして読み込み data = [data1, data2]
                pass
            else:
                raise NotImplementedError
        if self.target_dir:
            self.output_file = os.path.join(self.target_dir.value, "result.tremor.csv")
            with open(self.output_file, "w") as file:
                writer = csv.writer(file)
                for key, value in result.numerical_result.items():
                    writer.writerows([[key, value]])
            self.output_image_file = os.path.join(self.target_dir.value, "image.png")
            for key, image in result.image_result.items():
                image.save(self.output_image_file)
            for method in self.analysis_methods:
                if method.ACCEPTABLE_DATA_COUNT == 1:
                    for i, file in enumerate(file_pair):
                        result = method.run(data)
                        result.filename1 = file_pair[0]
                        results_1file.append(result)
                elif method.ACCEPTABLE_DATA_COUNT == 2 and len(file_pair) == 2:
                    # 左右の手のデータペアを受け入れる解析
                    result = method.run(data)
                    result.filename1 = file_pair[0]
                    result.filename2 = file_pair[1]
                    results_2files.append(result)
                elif method.ACCEPTABLE_DATA_COUNT == 2 and len(file_pair) == 1:
                    pass
                else:
                    raise NotImplementedError
        self.append_result_file(
            results_1file=results_1file,
            results_2files=results_2files,
        )

    def append_result_file(
        self,
        results_1file: list[AnalysisResult],  # ファイル名：結果
        results_2files: list[AnalysisResult],
    ) -> None:

        #  単一ファイルの結果出力
        output_1file = os.path.join(
            self.target_dir.value, "result_1file" + self.OUTPUT_FILE_EXTENSION
        )
        #  一通りの結果の列名をmethod_result.numerical_resultから取得してヘッダー作成

        header = []
        header += [
            f"{results_1file[0].analysis_method_class.__qualname__}_{key}"
            for key in results_1file[0].numerical_result.keys()
        ]
        #  出力先ファイルの存在確認,なかったらheader書き込み
        if not os.path.isfile(output_1file):
            with open(output_1file, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["filename"] + header)
        with open(output_1file, "a", newline="") as file:
            writer = csv.writer(file)
            # method_result.numerical_resultのキーに対して総当たりで， f"{method_result.analysis_method_class.__qualname__}_{key}" がheaderの要素と一致するものを検索
            # それの値を書き込み
            for filename in list(result.filename1 for result in results_1file):
                # headerの要素に対するループ
                for method_result in results_1file:
                    #  クラス名_key: valueの新しいresultリストを作成
                    result_with_class = {
                        f"{method_result.analysis_method_class.__qualname__}_{key}": value
                        for key, value in method_result.numerical_result.items()
                    }
                    result_row = [
                        result_with_class[header_key] for header_key in header
                    ]
                writer.writerow([filename] + result_row)

        output_2files = os.path.join(
            self.target_dir.value, "result_2file" + self.OUTPUT_FILE_EXTENSION
        )

        if len(results_2files) != 0:
            # 一通りの結果の列名をmethod_result.numerical_resultから取得してヘッダー作成
            header = []
            header += [
                f"{results_2files[0].analysis_method_class.__qualname__}_{key}"
                for key in results_2files[0].numerical_result.keys()
            ]
            # 出力先ファイルの存在確認,なかったらheader書き込み
            if not os.path.isfile(output_2files):
                with open(output_2files, "w", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow(["filename1", "filename2"] + header)
            with open(output_2files, "a", newline="") as file:
                writer = csv.writer(file)

                for results in results_2files:
                    #  クラス名_key: valueの新しいresultリストを作成
                    result_with_class = {
                        f"{results.analysis_method_class.__qualname__}_{key}": value
                        for key, value in results.numerical_result.items()
                    }
                    result_row = [
                        result_with_class[header_key] for header_key in header
                    ]
                    writer.writerow([results.filename1, results.filename2] + result_row)
            pass

    def on_run_click(self, e: ControlEvent):
        """Buttonのon_clickでは, 引数にControlEventが渡されるが，run()では不要のため, この関数でwrapしている

        Args:
            e (ControlEvent): click event
        """
        self.run()

    def read_config_file(self, e: ControlEvent):
        with open(CONFIG_FILE_PATH) as file:
            self.config = yaml.safe_load(file)
        print(self.config)

    def write_config_file(self, e: ControlEvent):
        self.config["key1"] = "change"
        self.config["add_key"] = "add"
        with open(CONFIG_FILE_PATH, "w") as file:
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
                    if f.endswith(self.ACCEPTABLE_FILE_EXTENSION)
                    and not f.endswith(self.OUTPUT_FILE_EXTENSION)
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

    def on_apply_click(self, _: ft.ControlEvent) -> None:
        self.apply()

    # apply settings
    def apply(self) -> None:
        yaml_file_content_tmp: dict[str, Any] = {}
        yaml_file_content_tmp["_general_"] = {
            key: general_config.value
            for key, general_config in self.general_setting_fields.items()
        }
        for method in self.analysis_methods:
            yaml_file_content_tmp[method.__class__.__name__] = {}
            for config, ui_component in zip(
                method.config, method.configure_ui_components.values()
            ):
                config.value = ui_component.value
                yaml_file_content_tmp[method.__class__.__name__][
                    config.name
                ] = ui_component.value  # TODO: このへん型のキャストがうまくいってない
        if yaml_file_content_tmp != self.yaml_file_handler.content:
            self.yaml_file_handler.content = yaml_file_content_tmp
            self.yaml_file_handler.export_yaml()
        self.apply_config_on_each_method()

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
        apply_button = ft.OutlinedButton(
            text="Apply&Save Settings",
            on_click=self.on_apply_click,
        )
        self.general_setting_fields = {
            config_key: TextFieldWithType(
                dtype=list(
                    filter(lambda x: x.name == config_key, self.CONFIG_DEFAULT_VALUE)
                )[0].type,
                default_value=config_value,
            )
            for config_key, config_value in self.yaml_file_handler.content[
                "_general_"
            ].items()
        }
        settings = ft.Container(
            content=ft.Column(
                [
                    ft.Text("General Settings"),
                ]
                + [
                    ft.Row(
                        [
                            ft.Text(general_config.name),
                            self.general_setting_fields[general_config.name].widget,
                        ]
                    )
                    for general_config in self.CONFIG_DEFAULT_VALUE
                ]
                + [method.configure_ui() for method in self.analysis_methods]
                + [
                    apply_button,
                ],
                scroll=ft.ScrollMode.ALWAYS,
            ),
            padding=25,
            height=self.page.window_height * 0.7,
        )
        log_outputs = ft.Container(
            content=(
                ft.Column(
                    [
                        ft.Text("Log Outputs"),
                        ft.Container(
                            content=ft.Column(
                                [self.log_content],
                                height=self.page.window_height * 0.7,
                                width=400,
                                scroll=ft.ScrollMode.ALWAYS,
                            ),
                            border=ft.border.all(1, "black"),
                            padding=10,
                        ),
                    ],
                )
            ),
        )

        self.page.add(
            select_folder_button,
            ft.Row(
                [
                    ft.Container(
                        content=(
                            ft.Column(
                                [
                                    settings,
                                    scan_button,
                                    run_button,
                                    open_result_button,
                                ]
                            )
                        ),
                    ),
                    log_outputs,
                ]
            ),
        )
        return

    def apply_config_on_each_method(self):
        for method in self.analysis_methods:
            config = self.yaml_file_handler.content[method.__class__.__name__]
            method.update_config(config)

    def main(self, page: ft.Page):

        self.page = page

        # page setting
        self.page.title = "tremor_analysis"

        self.build_ui()
        self.page.update()
        page.update()


class SpectrogramAnalysis:
    def __init__(self):
        self.data = 3

    def run(
        self,
    ) -> dict[str, Any]:
        self.val = 1 + self.data
        self.answer = {"answer": self.val}

    def import_config(self):
        with open(CONFIG_FILE_PATH) as file:
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
